# 🎨 MEGA PROMPT: Dashboard Builder (برای Claude Opus)

> این متن را در یک چت جداگانه با Claude Opus بفرست تا Dashboard را برایت بسازد.

---

## ROLE & MISSION

تو یک **Full-Stack Developer** حرفه‌ای هستی که متخصص ساخت وب‌اپلیکیشن‌های مدرن و کاربرپسند هستی.

ماموریت تو: **ساخت یک Dashboard مدیریت وظایف برای افراد ADHD**

---

## PROJECT CONTEXT

من یک سیستم مدیریت وظایف برای افراد ADHD دارم که شامل:
- **Notion Database**: Tasks, Projects, Resources
- **Google Sheets**: Daily logs و Brain dump archive
- **Gemini Gems**: دو بات برای Brain Dump و Daily Coaching

حالا نیاز دارم یک **Web Dashboard** که:
1. به Notion API وصل بشه
2. Task ها رو Import/Export کنه
3. نمایش visual از Task ها بر اساس Eisenhower Matrix
4. سازگار با موبایل و لپ‌تاپ
5. زبان فارسی با فونت Vazir
6. طراحی مینیمال و مدرن

---

## TECH STACK REQUIREMENTS

### Backend:
- **Python 3.10+**
- **Flask** (lightweight و ساده)
- **SQLite** (برای cache و لاگ‌های local)
- **Notion API Client** (notion-client)
- **Google Sheets API** (gspread یا google-api-python-client)
- **python-dotenv** (برای environment variables)

### Frontend:
- **HTML5 + CSS3 + Vanilla JavaScript**
- **NO React/Vue/Angular** - باید ساده باشه
- **Tailwind CSS** (از CDN) - برای styling سریع
- **Chart.js** (از CDN) - برای نمودارها
- **Font: Vazir** (از CDN)

### Deployment:
- سرور Ubuntu
- Gunicorn + Nginx
- باید راهنمای نصب کامل بدی

---

## FUNCTIONAL REQUIREMENTS

### صفحات اصلی:

#### 1. صفحه Home (Dashboard)
```
┌─────────────────────────────────────────────────────────┐
│  🧠 داشبورد من                        [تاریخ امروز]     │
│  [نام کاربر]                                            │
└─────────────────────────────────────────────────────────┘

┌───────────────────────────┬─────────────────────────────┐
│  📊 آمار امروز             │  🔔 یادآوری‌ها              │
│  • ✅ انجام شده: 3         │  • تماس با علی (فوری)     │
│  • ⏳ در انتظار: 5         │  • ارسال فاکتور (امروز)   │
│  • 🔥 فوری: 2              │                            │
└───────────────────────────┴─────────────────────────────┘

┌─────────────────────────────────────────────────────────┐
│  🔥 ماتریس آیزنهاور                                     │
│                                                         │
│  ┌──────────────┬──────────────┐                       │
│  │ Q1: بحران    │ Q2: ذکاوت    │                       │
│  │ [Task 1]    │ [Task 3]    │                       │
│  │ [Task 2]    │ [Task 4]    │                       │
│  ├──────────────┼──────────────┤                       │
│  │ Q3: حواس‌پرتی│ Q4: اتلاف    │                       │
│  │ [Task 5]    │ [Task 6]    │                       │
│  └──────────────┴──────────────┘                       │
└─────────────────────────────────────────────────────────┘

┌─────────────────────────────────────────────────────────┐
│  ⚡ دسترسی سریع                                         │
│  [🔥 High Focus Tasks]  [🪶 Low Energy Tasks]          │
└─────────────────────────────────────────────────────────┘
```

#### 2. صفحه Tasks
- لیست همه Task ها
- فیلتر بر اساس: Status, Context, Energy, Importance, Urgency
- جستجو
- مرتب‌سازی
- اضافه/ویرایش/حذف Task

#### 3. صفحه Import from Gem
- فیلد Textarea برای paste کردن JSON از Gem
- دکمه "Import to Notion"
- نمایش preview قبل از Import
- نمایش پیام Success/Error

#### 4. صفحه Analytics
- نمودار Mood Trend (از Google Sheets)
- نمودار Tasks Done per Day
- توزیع Context ها (Pie Chart)
- توزیع Energy Level ها

#### 5. صفحه Settings
- Notion API Key
- Notion Database IDs
- Google Sheets API credentials
- تنظیمات یادآوری (Telegram Bot Token)

---

## UI/UX GUIDELINES (ADHD-Optimized)

### 🧠 اصول کلیدی طراحی برای ADHD:

#### 1. مینیمال و بدون شلوغی (Minimal & Clutter-Free)
```
❌ بد: 20 کارت، 10 بخش، 5 منو همزمان
✅ خوب: 3-5 بخش اصلی، فضای خالی زیاد

قوانین:
• هر صفحه فقط 1 هدف اصلی دارد
• حداکثر 3 اکشن اصلی در یک صفحه
• استفاده هوشمندانه از Whitespace (فضای خالی)
• Hide کردن جزئیات غیرضروری با Toggle/Collapse
```

#### 2. کاهش بار شناختی (Reduce Cognitive Load)
```
❌ بد: نمایش همه 50 تا Task در یک لیست
✅ خوب: نمایش فقط 3 Task امروز

قوانین:
• فقط اطلاعات ضروری نشان داده شود
• گروه‌بندی منطقی (Chunking)
• Pagination برای لیست‌های بلند (10 آیتم در صفحه)
• تمرکز روی سوال: "الان چیکار کنم؟"
```

#### 3. بازخورد بصری فوری (Instant Visual Feedback)
```
مثال‌های اجرایی:
• Task Done شد → ✓ انیمیشن سبز + صدای کوچک
• Progress Bar برای پروژه‌ها (% تکمیل)
• Confetti animation برای Complete کردن Project!
• Loading spinners برای هر اقدام
```

#### 4. ساده‌سازی تصمیم‌گیری (Simplify Decisions)
```
❌ بد: "کدوم کار رو انجام بدم؟" (20 گزینه)
✅ خوب: "الان 3 کار داری، کدوم؟"

قوانین:
• محدود کردن گزینه‌ها (Choice Paradox)
• پیشنهاد هوشمند روی Dashboard:
  "با توجه به انرژیت، این کار رو پیشنهاد میدم"
• Default values برای همه فیلدها
```

#### 5. Gamification ساده
```
عناصر مجاز:
• Streak Counter: "5 روز پشت سر هم!"
• Progress Circles نمایش %
• Badges برای Milestones (اختیاری)

⚠️ توجه: Gamification بیش از حد → حواس‌پرتی!
```

---

### رنگ‌بندی:

```css
/* Primary Colors */
--primary: #4A90E2;        /* آبی روشن */
--primary-dark: #357ABD;   /* آبی تیره */
--secondary: #50C878;      /* سبز یشمی */

/* Status Colors */
--urgent: #E74C3C;         /* قرمز - فوری */
--important: #F39C12;      /* نارنجی - مهم */
--normal: #3498DB;         /* آبی - عادی */
--low: #95A5A6;            /* خاکستری - کم */

/* Quadrant Colors */
--q1: #E74C3C;             /* Q1: بحران - قرمز */
--q2: #2ECC71;             /* Q2: ذکاوت - سبز */
--q3: #F39C12;             /* Q3: حواس‌پرتی - نارنجی */
--q4: #95A5A6;             /* Q4: اتلاف - خاکستری */

/* Energy Colors */
--high-energy: #E74C3C;    /* قرمز */
--medium-energy: #F39C12;  /* نارنجی */
--low-energy: #3498DB;     /* آبی */

/* Background */
--bg-primary: #FFFFFF;     /* سفید */
--bg-secondary: #F5F7FA;   /* خاکستری خیلی روشن */
--bg-dark: #2C3E50;        /* تیره */

/* Text */
--text-primary: #2C3E50;   /* تیره */
--text-secondary: #7F8C8D; /* خاکستری */
--text-light: #FFFFFF;     /* سفید */
```

### فونت:

```css
@import url('https://cdn.jsdelivr.net/gh/rastikerdar/vazir-font@v30.1.0/dist/font-face.css');

body {
    font-family: Vazir, -apple-system, BlinkMacSystemFont, 'Segoe UI', sans-serif;
    direction: rtl; /* راست به چپ */
}
```

### طراحی مینیمال:

- **کارت‌ها**: با shadow ملایم، border-radius: 12px
- **دکمه‌ها**: با hover effect، transition smooth
- **فاصله‌گذاری**: استفاده از margin/padding consistent
- **Icons**: استفاده از Emoji یا Lucide Icons

### Responsive:

- موبایل (< 768px): تک ستونی
- تبلت (768-1024px): دو ستونی
- دسکتاپ (> 1024px): سه ستونی

---

## API INTEGRATION SPECS

### Notion API:

**Environment Variables:**
```
NOTION_API_KEY=secret_xxxxxxxxxxxxx
NOTION_TASKS_DB_ID=xxxxxxxxxxxxxxxxxxxxxxxx
NOTION_PROJECTS_DB_ID=xxxxxxxxxxxxxxxxxxxxxxxx
NOTION_RESOURCES_DB_ID=xxxxxxxxxxxxxxxxxxxxxxxx
```

**Operations:**
1. **Fetch Tasks** - GET all tasks from Notion
2. **Create Task** - POST new task
3. **Update Task** - PATCH existing task
4. **Delete Task** - Archive task

**Mapping:**
```python
notion_to_app = {
    "Name": "title",
    "Status": "status",
    "Context": "context",
    "Energy Level": "energy",
    "Importance": "importance",
    "Urgency": "urgency",
    "Estimated Time": "time",
    "Due Date": "due_date",
    "Quick Win": "quick_win",
    "Notes": "notes"
}
```

### Google Sheets API:

**Environment Variables:**
```
GOOGLE_SHEETS_CREDENTIALS=./credentials.json
DAILY_LOG_SHEET_ID=xxxxxxxxxxxxxxxxxxxxxxxxxx
BRAIN_DUMP_SHEET_ID=xxxxxxxxxxxxxxxxxxxxxxxxxx
```

**Operations:**
1. **Read Daily Log** - برای نمودار Mood/Energy
2. **Read Brain Dump Archive** - برای آمار
3. **Append Row** - اضافه کردن لاگ جدید (در آینده)

---

## FILE STRUCTURE

```
adhd-dashboard/
├── app.py                    # Flask main app
├── config.py                 # Configuration
├── requirements.txt          # Python dependencies
├── .env                      # Environment variables (NOT in git)
├── .env.example              # نمونه env (for documentation)
├── README.md                 # راهنمای نصب و استفاده
├── static/
│   ├── css/
│   │   └── main.css          # Custom styles
│   ├── js/
│   │   ├── main.js           # Main JavaScript
│   │   ├── eisenhower.js     # ماتریس آیزنهاور
│   │   ├── charts.js         # نمودارها
│   │   └── import.js         # Import از Gem
│   └── assets/
│       └── logo.png
├── templates/
│   ├── base.html             # Base template
│   ├── dashboard.html        # صفحه اصلی
│   ├── tasks.html            # لیست Task ها
│   ├── import.html           # Import از Gem
│   ├── analytics.html        # آمار و نمودار
│   └── settings.html         # تنظیمات
├── utils/
│   ├── __init__.py
│   ├── notion_api.py         # Notion integration
│   ├── sheets_api.py         # Google Sheets integration
│   └── telegram_bot.py       # Telegram bot (فاز بعد)
└── database/
    └── local.db              # SQLite for caching
```

---

## PRIORITY FEATURES (مرحله اول)

### Must Have (الان):
1. ✅ Dashboard با ماتریس آیزنهاور
2. ✅ لیست Tasks با فیلتر
3. ✅ Import JSON از Gem به Notion
4. ✅ اتصال به Notion API
5. ✅ UI فارسی با فونت Vazir
6. ✅ Responsive design

### Nice to Have (فاز دوم):
- 🔄 اتصال به Google Sheets برای Analytics
- 🔄 Telegram Bot یادآوری
- 🔄 Export به PDF
- 🔄 Dark Mode
- 🔄 PWA (Progressive Web App)

---

## SECURITY CONSIDERATIONS

1. **API Keys**: همیشه در .env، never hardcode
2. **CORS**: فقط از origin های مشخص
3. **Rate Limiting**: محدودیت درخواست
4. **Input Validation**: چک کردن JSON ورودی
5. **SQL Injection**: استفاده از parameterized queries

---

## DEPLOYMENT GUIDE REQUIREMENTS

باید یک `README.md` کامل بدی که شامل:

### بخش 1: نصب روی Ubuntu Server
```bash
# Update system
sudo apt update && sudo apt upgrade -y

# Install Python & pip
sudo apt install python3.10 python3-pip -y

# Install Nginx
sudo apt install nginx -y

# Clone repo
git clone ...

# Setup virtual environment
python3 -m venv venv
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt

# Setup .env
cp .env.example .env
nano .env  # Edit with your keys

# Run migrations (if any)
python app.py init-db

# Test locally
python app.py

# Setup Gunicorn
pip install gunicorn

# Setup systemd service
sudo nano /etc/systemd/system/adhd-dashboard.service

# Setup Nginx config
sudo nano /etc/nginx/sites-available/adhd-dashboard

# Enable and start
sudo systemctl enable adhd-dashboard
sudo systemctl start adhd-dashboard
sudo systemctl reload nginx
```

### بخش 2: دریافت Notion API Key
```
1. برو به https://www.notion.so/my-integrations
2. Create new integration
3. نام: ADHD Dashboard
4. Copy Internal Integration Token
5. برو به Notion Database
6. کلیک روی ... (سه نقطه)
7. Connections → Add connection → انتخاب integration
8. کپی کردن Database ID از URL
```

### بخش 3: تنظیم Google Sheets API
```
1. برو به https://console.cloud.google.com
2. Create new project
3. Enable Google Sheets API
4. Create Service Account
5. Download JSON credentials
6. Share Sheet با email Service Account
7. کپی Sheet ID از URL
```

---

## OUTPUT EXPECTATIONS

من از تو می‌خوام:

### فایل 1: app.py (Backend اصلی)
```python
from flask import Flask, render_template, request, jsonify
# ... کد کامل
```

### فایل 2: templates/base.html
```html
<!DOCTYPE html>
<html lang="fa" dir="rtl">
<!-- ... کد کامل -->
```

### فایل 3: templates/dashboard.html
```html
{% extends "base.html" %}
{% block content %}
<!-- ... کد کامل -->
```

### فایل 4: static/css/main.css
```css
/* Reset & Base */
/* ... کد کامل */
```

### فایل 5: static/js/eisenhower.js
```javascript
// ماتریس آیزنهاور
// ... کد کامل
```

### فایل 6: utils/notion_api.py
```python
from notion_client import Client
# ... کد کامل
```

### فایل 7: requirements.txt
```
Flask==3.0.0
notion-client==2.2.1
python-dotenv==1.0.0
# ... بقیه
```

### فایل 8: README.md (راهنمای کامل فارسی)

### فایل 9: .env.example
```
NOTION_API_KEY=your_key_here
# ...
```

---

## CODING STANDARDS

1. **Python**: PEP 8 compliance
2. **Comments**: به فارسی برای فایل‌های مهم
3. **Error Handling**: try-except برای همه API calls
4. **Logging**: استفاده از logging module
5. **Type Hints**: استفاده کن (Python 3.10+)

مثال:
```python
def fetch_tasks(database_id: str) -> list[dict]:
    """
    دریافت تمام Task ها از Notion
    
    Args:
        database_id: شناسه دیتابیس Notion
        
    Returns:
        لیست Task ها به صورت dict
    """
    try:
        # کد
        pass
    except Exception as e:
        logging.error(f"خطا در دریافت Task ها: {e}")
        return []
```

---

## SAMPLE DATA FOR TESTING

در فایل `sample_data.json` چند نمونه Task بذار:

```json
{
  "tasks": [
    {
      "name": "تماس با مشتری برای پیگیری",
      "status": "Next Action",
      "context": ["📞 تماس"],
      "energy": "⚡ Medium",
      "importance": "🔴 High",
      "urgency": "🚨 Urgent",
      "time": "🕐 15 min",
      "quick_win": false
    },
    {
      "name": "خرید نان و شیر",
      "status": "Next Action",
      "context": ["🛒 خرید"],
      "energy": "🪶 Low Focus",
      "importance": "🟡 Medium",
      "urgency": "⏰ Soon",
      "time": "⚡ < 5 min",
      "quick_win": true
    }
  ]
}
```

---

## QUESTIONS FOR YOU (قبل از شروع)

1. آیا می‌خوای من **همین الان** همه فایل‌ها رو بسازم؟
2. یا می‌خوای **قدم به قدم** هر فایل رو توضیح بدم و تو تایید کنی؟
3. آیا نیاز به Docker support داری؟
4. آیا قرار است چند کاربر داشته باشد یا فقط تک کاربر؟

---

## READY TO BUILD

این مگاپرامپت آماده است. کافیه این متن رو به Claude Opus بفرستی و بگی:

```
"سلام! این مگاپرامپت رو خوندی؟
من نیاز دارم یک Dashboard مطابق این مشخصات بسازی.

جواب سوالات:
1. بله، همین الان همه فایل‌ها رو بساز
2. تک کاربره (فقط برای من)
3. Docker نیاز نیست (مستقیم روی Ubuntu)
4. [هر توضیح اضافه دیگری که داری...]

شروع کن!"
```

بعد Opus شروع می‌کنه به ساخت کامل پروژه.
