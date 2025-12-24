"""
🧠 ADHD Task Dashboard - نسخه 2.0
شامل:
- Dashboard با ماتریس آیزنهاور
- مدیریت Tasks
- Habits Tracker (جدید)
- Sync Notion Structure (جدید)
- Analytics با نمودارهای جدید
"""

import os
import json
import logging
from datetime import datetime
from functools import wraps

from flask import (
    Flask, render_template, request, jsonify, 
    redirect, url_for, flash
)
from dotenv import load_dotenv
from werkzeug.utils import secure_filename

from config import get_config, Config
from utils.notion_api import NotionAPI
from utils.sheets_api import create_sheets_api

# بارگذاری متغیرهای محیطی
load_dotenv()

# تنظیم logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# ایجاد اپلیکیشن Flask
app = Flask(__name__)
app.config.from_object(get_config())
app.secret_key = Config.SECRET_KEY

# تنظیم آپلود فایل
UPLOAD_FOLDER = os.path.join(os.path.dirname(__file__), 'uploads')
ALLOWED_EXTENSIONS = {'md', 'txt'}
os.makedirs(UPLOAD_FOLDER, exist_ok=True)
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
app.config['MAX_CONTENT_LENGTH'] = 1 * 1024 * 1024  # 1MB

# آبجکت‌های API
notion_api = None
sheets_api = None


def init_apis():
    """اولیه‌سازی API ها"""
    global notion_api, sheets_api
    
    if Config.is_notion_configured():
        notion_api = NotionAPI(Config.NOTION_API_KEY)
        logger.info("Notion API آماده است")
    else:
        logger.warning("Notion API تنظیم نشده")
    
    if Config.is_sheets_configured():
        sheets_api = create_sheets_api(Config.GOOGLE_SHEETS_CREDENTIALS)
        if sheets_api:
            logger.info("Google Sheets API آماده است")
    else:
        logger.warning("Google Sheets API تنظیم نشده")


def api_required(f):
    """دکوراتور برای بررسی اتصال به Notion API"""
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if not notion_api:
            return jsonify({"error": "Notion API تنظیم نشده"}), 503
        return f(*args, **kwargs)
    return decorated_function


def allowed_file(filename):
    """بررسی پسوند فایل"""
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS


# ============================================
# صفحات اصلی
# ============================================

@app.route('/')
def dashboard():
    """صفحه اصلی داشبورد"""
    tasks = []
    stats = {}
    habit_stats = {}
    sheets_summary = {}
    
    if notion_api and Config.NOTION_TASKS_DB_ID:
        tasks = notion_api.fetch_tasks(Config.NOTION_TASKS_DB_ID)
        stats = notion_api.get_task_stats(Config.NOTION_TASKS_DB_ID)
    
    if notion_api and Config.NOTION_HABITS_DB_ID:
        habit_stats = notion_api.get_habit_stats(Config.NOTION_HABITS_DB_ID)
    
    if sheets_api and Config.DAILY_LOG_SHEET_ID:
        sheets_summary = sheets_api.get_analytics_summary(
            Config.DAILY_LOG_SHEET_ID,
            Config.DAILY_LOG_SHEET_NAME
        )
    
    # گروه‌بندی Tasks بر اساس کوادرانت
    quadrants = {1: [], 2: [], 3: [], 4: []}
    for task in tasks:
        q = task.get("quadrant", 4)
        if len(quadrants[q]) < 5:
            quadrants[q].append(task)
    
    # Quick Wins
    quick_wins = [t for t in tasks if t.get("quick_win") and "Done" not in t.get("status", "")][:3]
    
    # Low Energy Tasks
    low_energy = [t for t in tasks if "Low" in t.get("energy", "") and "Done" not in t.get("status", "")][:3]
    
    # High Focus Tasks
    high_focus = [t for t in tasks if "High" in t.get("energy", "") and "Done" not in t.get("status", "")][:3]
    
    # Urgent reminders
    reminders = [t for t in tasks if "Urgent" in t.get("urgency", "") or "🚨" in t.get("urgency", "")][:5]
    
    return render_template(
        'dashboard.html',
        user_name=Config.USER_NAME,
        today=datetime.now().strftime("%Y/%m/%d"),
        today_weekday=get_persian_weekday(),
        stats=stats,
        habit_stats=habit_stats,
        sheets_summary=sheets_summary,
        reminders=reminders,
        quadrants=quadrants,
        quick_wins=quick_wins,
        low_energy=low_energy,
        high_focus=high_focus,
        notion_configured=Config.is_notion_configured(),
        sheets_configured=Config.is_sheets_configured()
    )


@app.route('/tasks')
def tasks_page():
    """صفحه لیست Tasks"""
    tasks = []
    
    if notion_api and Config.NOTION_TASKS_DB_ID:
        tasks = notion_api.fetch_tasks(Config.NOTION_TASKS_DB_ID)
    
    # فیلترها
    status_filter = request.args.get('status', '')
    context_filter = request.args.get('context', '')
    energy_filter = request.args.get('energy', '')
    search_query = request.args.get('q', '')
    
    filtered_tasks = tasks
    
    if status_filter:
        filtered_tasks = [t for t in filtered_tasks if status_filter in t.get("status", "")]
    
    if context_filter:
        filtered_tasks = [t for t in filtered_tasks if context_filter in str(t.get("context", []))]
    
    if energy_filter:
        filtered_tasks = [t for t in filtered_tasks if energy_filter in t.get("energy", "")]
    
    if search_query:
        search_lower = search_query.lower()
        filtered_tasks = [t for t in filtered_tasks 
                         if search_lower in t.get("title", "").lower() 
                         or search_lower in t.get("notes", "").lower()]
    
    # Pagination
    page = request.args.get('page', 1, type=int)
    per_page = Config.ITEMS_PER_PAGE
    total = len(filtered_tasks)
    start = (page - 1) * per_page
    paginated_tasks = filtered_tasks[start:start + per_page]
    
    return render_template(
        'tasks.html',
        tasks=paginated_tasks,
        total_tasks=total,
        page=page,
        per_page=per_page,
        total_pages=(total + per_page - 1) // per_page,
        filters={'status': status_filter, 'context': context_filter, 'energy': energy_filter, 'q': search_query},
        status_values=notion_api.task_status_options if notion_api else [],
        context_values=notion_api.context_options if notion_api else [],
        energy_values=notion_api.energy_options if notion_api else [],
        importance_values=notion_api.importance_options if notion_api else [],
        urgency_values=notion_api.urgency_options if notion_api else [],
        time_values=notion_api.time_options if notion_api else [],
        notion_configured=Config.is_notion_configured()
    )


@app.route('/habits')
def habits_page():
    """صفحه Habits Tracker"""
    habits = []
    stats = {}
    
    filter_type = request.args.get('filter', 'all')
    
    if notion_api and Config.NOTION_HABITS_DB_ID:
        habits = notion_api.fetch_habits(Config.NOTION_HABITS_DB_ID, filter_type)
        stats = notion_api.get_habit_stats(Config.NOTION_HABITS_DB_ID)
    
    return render_template(
        'habits.html',
        habits=habits,
        stats=stats,
        filter_type=filter_type,
        habit_type_options=notion_api.habit_type_options if notion_api else [],
        habit_category_options=notion_api.habit_category_options if notion_api else [],
        habit_status_options=notion_api.habit_status_options if notion_api else [],
        habit_frequency_options=notion_api.habit_frequency_options if notion_api else [],
        notion_configured=Config.is_notion_configured(),
        habits_db_configured=bool(Config.NOTION_HABITS_DB_ID)
    )


@app.route('/import')
def import_page():
    """صفحه Import از Gem"""
    return render_template(
        'import.html',
        notion_configured=Config.is_notion_configured()
    )


@app.route('/analytics')
def analytics_page():
    """صفحه آمار و نمودارها"""
    mood_data = {}
    summary = {}
    task_stats = {}
    habit_stats = {}
    bad_habits_freq = []
    good_habits_streak = []
    techniques_usage = []
    
    if sheets_api and Config.DAILY_LOG_SHEET_ID:
        mood_data = sheets_api.get_mood_trend(
            Config.DAILY_LOG_SHEET_ID,
            Config.DAILY_LOG_SHEET_NAME,
            days=14
        )
        summary = sheets_api.get_analytics_summary(
            Config.DAILY_LOG_SHEET_ID,
            Config.DAILY_LOG_SHEET_NAME,
            days=30
        )
        bad_habits_freq = sheets_api.get_bad_habits_frequency(
            Config.DAILY_LOG_SHEET_ID,
            Config.DAILY_LOG_SHEET_NAME
        )
        good_habits_streak = sheets_api.get_good_habits_streak(
            Config.DAILY_LOG_SHEET_ID,
            Config.DAILY_LOG_SHEET_NAME
        )
        techniques_usage = sheets_api.get_techniques_usage(
            Config.DAILY_LOG_SHEET_ID,
            Config.DAILY_LOG_SHEET_NAME
        )
    
    if notion_api and Config.NOTION_TASKS_DB_ID:
        task_stats = notion_api.get_task_stats(Config.NOTION_TASKS_DB_ID)
    
    if notion_api and Config.NOTION_HABITS_DB_ID:
        habit_stats = notion_api.get_habit_stats(Config.NOTION_HABITS_DB_ID)
    
    return render_template(
        'analytics.html',
        mood_data=json.dumps(mood_data),
        summary=summary,
        task_stats=task_stats,
        habit_stats=habit_stats,
        bad_habits_freq=json.dumps(bad_habits_freq),
        good_habits_streak=json.dumps(good_habits_streak),
        techniques_usage=json.dumps(techniques_usage),
        notion_configured=Config.is_notion_configured(),
        sheets_configured=Config.is_sheets_configured()
    )


@app.route('/settings')
def settings_page():
    """صفحه تنظیمات"""
    return render_template(
        'settings.html',
        config={
            'notion_configured': Config.is_notion_configured(),
            'sheets_configured': Config.is_sheets_configured(),
            'telegram_configured': Config.is_telegram_configured(),
            'can_sync': Config.can_sync_structure(),
            'user_name': Config.USER_NAME,
            'parent_page_id': Config.NOTION_PARENT_PAGE_ID[:8] + '...' if Config.NOTION_PARENT_PAGE_ID else '',
            'tasks_db': Config.NOTION_TASKS_DB_ID[:8] + '...' if Config.NOTION_TASKS_DB_ID else '',
            'habits_db': Config.NOTION_HABITS_DB_ID[:8] + '...' if Config.NOTION_HABITS_DB_ID else '',
            'daily_log_sheet': Config.DAILY_LOG_SHEET_ID[:8] + '...' if Config.DAILY_LOG_SHEET_ID else ''
        }
    )


# ============================================
# API Routes - Tasks
# ============================================

@app.route('/api/tasks', methods=['GET'])
@api_required
def api_get_tasks():
    """دریافت لیست Tasks"""
    if not Config.NOTION_TASKS_DB_ID:
        return jsonify({"error": "Tasks Database تنظیم نشده"}), 400
    
    tasks = notion_api.fetch_tasks(Config.NOTION_TASKS_DB_ID)
    return jsonify({"tasks": tasks, "count": len(tasks)})


@app.route('/api/tasks', methods=['POST'])
@api_required
def api_create_task():
    """ایجاد Task جدید"""
    if not Config.NOTION_TASKS_DB_ID:
        return jsonify({"error": "Tasks Database تنظیم نشده"}), 400
    
    data = request.get_json()
    if not data or not data.get('title'):
        return jsonify({"error": "عنوان الزامی است"}), 400
    
    task = notion_api.create_task(Config.NOTION_TASKS_DB_ID, data)
    
    if task:
        return jsonify({"success": True, "task": task}), 201
    return jsonify({"error": "خطا در ایجاد"}), 500


@app.route('/api/tasks/<task_id>', methods=['PATCH'])
@api_required
def api_update_task(task_id):
    """بروزرسانی Task"""
    data = request.get_json()
    if not data:
        return jsonify({"error": "داده‌ای ارسال نشده"}), 400
    
    task = notion_api.update_task(task_id, data)
    
    if task:
        return jsonify({"success": True, "task": task})
    return jsonify({"error": "خطا در بروزرسانی"}), 500


@app.route('/api/tasks/<task_id>', methods=['DELETE'])
@api_required
def api_delete_task(task_id):
    """حذف Task"""
    success = notion_api.delete_task(task_id)
    
    if success:
        return jsonify({"success": True})
    return jsonify({"error": "خطا در حذف"}), 500


@app.route('/api/tasks/<task_id>/done', methods=['POST'])
@api_required
def api_mark_done(task_id):
    """تغییر وضعیت به Done"""
    task = notion_api.mark_done(task_id)
    
    if task:
        return jsonify({"success": True, "task": task})
    return jsonify({"error": "خطا"}), 500


@app.route('/api/import', methods=['POST'])
@api_required
def api_import_tasks():
    """Import Tasks از JSON"""
    if not Config.NOTION_TASKS_DB_ID:
        return jsonify({"error": "Tasks Database تنظیم نشده"}), 400
    
    data = request.get_json()
    if not data or not data.get('tasks'):
        return jsonify({"error": "لیست خالی است"}), 400
    
    result = notion_api.import_tasks_from_json(Config.NOTION_TASKS_DB_ID, data['tasks'])
    
    return jsonify({
        "success": True,
        "imported": result["success"],
        "failed": result["failed"],
        "errors": result["errors"]
    })


@app.route('/api/stats')
@api_required
def api_get_stats():
    """دریافت آمار"""
    if not Config.NOTION_TASKS_DB_ID:
        return jsonify({"error": "Tasks Database تنظیم نشده"}), 400
    
    stats = notion_api.get_task_stats(Config.NOTION_TASKS_DB_ID)
    return jsonify(stats)


# ============================================
# API Routes - Habits
# ============================================

@app.route('/api/habits', methods=['GET'])
@api_required
def api_get_habits():
    """دریافت لیست Habits"""
    if not Config.NOTION_HABITS_DB_ID:
        return jsonify({"error": "Habits Database تنظیم نشده"}), 400
    
    filter_type = request.args.get('filter', 'all')
    habits = notion_api.fetch_habits(Config.NOTION_HABITS_DB_ID, filter_type)
    return jsonify({"habits": habits, "count": len(habits)})


@app.route('/api/habits', methods=['POST'])
@api_required
def api_create_habit():
    """ایجاد Habit جدید"""
    if not Config.NOTION_HABITS_DB_ID:
        return jsonify({"error": "Habits Database تنظیم نشده"}), 400
    
    data = request.get_json()
    if not data or not data.get('name'):
        return jsonify({"error": "نام عادت الزامی است"}), 400
    
    habit = notion_api.create_habit(Config.NOTION_HABITS_DB_ID, data)
    
    if habit:
        return jsonify({"success": True, "habit": habit}), 201
    return jsonify({"error": "خطا در ایجاد"}), 500


@app.route('/api/habits/<habit_id>', methods=['PATCH'])
@api_required
def api_update_habit(habit_id):
    """بروزرسانی Habit"""
    data = request.get_json()
    if not data:
        return jsonify({"error": "داده‌ای ارسال نشده"}), 400
    
    habit = notion_api.update_habit(habit_id, data)
    
    if habit:
        return jsonify({"success": True, "habit": habit})
    return jsonify({"error": "خطا در بروزرسانی"}), 500


@app.route('/api/habits/<habit_id>/increment', methods=['POST'])
@api_required
def api_increment_habit(habit_id):
    """افزایش Counter عادت"""
    if not Config.NOTION_HABITS_DB_ID:
        return jsonify({"error": "Habits Database تنظیم نشده"}), 400
    
    habit = notion_api.increment_habit(Config.NOTION_HABITS_DB_ID, habit_id)
    
    if habit:
        return jsonify({"success": True, "habit": habit})
    return jsonify({"error": "خطا"}), 500


@app.route('/api/habits/stats')
@api_required
def api_habit_stats():
    """دریافت آمار Habits"""
    if not Config.NOTION_HABITS_DB_ID:
        return jsonify({"error": "Habits Database تنظیم نشده"}), 400
    
    stats = notion_api.get_habit_stats(Config.NOTION_HABITS_DB_ID)
    return jsonify(stats)


# ============================================
# API Routes - Sync Notion Structure
# ============================================

@app.route('/api/sync-notion', methods=['POST'])
@api_required
def api_sync_notion():
    """Sync کردن ساختار Notion از فایل MD"""
    if not Config.can_sync_structure():
        return jsonify({
            "error": "برای Sync باید Parent Page ID تنظیم شده باشه"
        }), 400
    
    md_content = None
    
    # چک کن آیا فایل آپلود شده
    if 'file' in request.files:
        file = request.files['file']
        if file and allowed_file(file.filename):
            md_content = file.read().decode('utf-8')
    
    # یا از body بخون
    elif request.is_json:
        data = request.get_json()
        md_content = data.get('md_content')
    
    try:
        result = notion_api.sync_structure(
            Config.NOTION_PARENT_PAGE_ID,
            md_content
        )
        
        # ذخیره Database IDs جدید
        for db_name, db_id in result.get("db_ids", {}).items():
            Config.update_db_id(db_name, db_id)
        
        return jsonify({
            "success": True,
            "created": result["created"],
            "updated": result["updated"],
            "errors": result["errors"],
            "db_ids": result["db_ids"]
        })
        
    except Exception as e:
        logger.error(f"خطا در Sync: {e}")
        return jsonify({"error": str(e)}), 500


# ============================================
# API Routes - Google Sheets
# ============================================

@app.route('/api/mood-data')
def api_mood_data():
    """دریافت داده‌های Mood"""
    if not sheets_api or not Config.DAILY_LOG_SHEET_ID:
        return jsonify({"error": "Google Sheets تنظیم نشده"}), 503
    
    days = request.args.get('days', 14, type=int)
    data = sheets_api.get_mood_trend(
        Config.DAILY_LOG_SHEET_ID,
        Config.DAILY_LOG_SHEET_NAME,
        days
    )
    return jsonify(data)


@app.route('/api/log-mood', methods=['POST'])
def api_log_mood():
    """ثبت لاگ روزانه"""
    if not sheets_api or not Config.DAILY_LOG_SHEET_ID:
        return jsonify({"error": "Google Sheets تنظیم نشده"}), 503
    
    data = request.get_json()
    
    success = sheets_api.append_daily_log(
        Config.DAILY_LOG_SHEET_ID,
        Config.DAILY_LOG_SHEET_NAME,
        data
    )
    
    if success:
        return jsonify({"success": True})
    return jsonify({"error": "خطا در ثبت"}), 500


@app.route('/api/analytics/bad-habits')
def api_bad_habits():
    """دریافت فراوانی عادت‌های بد"""
    if not sheets_api or not Config.DAILY_LOG_SHEET_ID:
        return jsonify({"error": "Google Sheets تنظیم نشده"}), 503
    
    data = sheets_api.get_bad_habits_frequency(
        Config.DAILY_LOG_SHEET_ID,
        Config.DAILY_LOG_SHEET_NAME
    )
    return jsonify(data)


@app.route('/api/analytics/good-habits')
def api_good_habits():
    """دریافت روند عادت‌های خوب"""
    if not sheets_api or not Config.DAILY_LOG_SHEET_ID:
        return jsonify({"error": "Google Sheets تنظیم نشده"}), 503
    
    data = sheets_api.get_good_habits_streak(
        Config.DAILY_LOG_SHEET_ID,
        Config.DAILY_LOG_SHEET_NAME
    )
    return jsonify(data)


@app.route('/api/analytics/techniques')
def api_techniques():
    """دریافت استفاده از تکنیک‌ها"""
    if not sheets_api or not Config.DAILY_LOG_SHEET_ID:
        return jsonify({"error": "Google Sheets تنظیم نشده"}), 503
    
    data = sheets_api.get_techniques_usage(
        Config.DAILY_LOG_SHEET_ID,
        Config.DAILY_LOG_SHEET_NAME
    )
    return jsonify(data)


# ============================================
# Helper Functions
# ============================================

def get_persian_weekday() -> str:
    """دریافت نام روز هفته به فارسی"""
    days = {
        0: "دوشنبه",
        1: "سه‌شنبه",
        2: "چهارشنبه",
        3: "پنج‌شنبه",
        4: "جمعه",
        5: "شنبه",
        6: "یک‌شنبه"
    }
    return days.get(datetime.now().weekday(), "")


@app.context_processor
def utility_processor():
    """توابع کمکی برای Templates"""
    return {
        'now': datetime.now,
        'get_persian_weekday': get_persian_weekday
    }


@app.errorhandler(404)
def not_found_error(error):
    return render_template('base.html', error="صفحه یافت نشد"), 404


@app.errorhandler(500)
def internal_error(error):
    return render_template('base.html', error="خطای داخلی سرور"), 500


# ============================================
# اجرای برنامه
# ============================================

if __name__ == '__main__':
    init_apis()
    
    port = Config.FLASK_PORT
    debug = Config.DEBUG
    
    logger.info(f"🧠 ADHD Dashboard v2.0 شروع شد")
    logger.info(f"📍 آدرس: http://localhost:{port}")
    
    app.run(host='0.0.0.0', port=port, debug=debug)
