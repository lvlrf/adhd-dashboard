"""
تنظیمات اصلی برنامه - نسخه 2.0
شامل پشتیبانی از 5 Database و Sync Structure
"""

import os
from pathlib import Path
from dotenv import load_dotenv

# بارگذاری متغیرهای محیطی
load_dotenv()

# مسیر پایه پروژه
BASE_DIR = Path(__file__).resolve().parent


class Config:
    """تنظیمات پایه"""
    
    # Flask
    SECRET_KEY = os.getenv('FLASK_SECRET_KEY', 'dev-secret-key-change-in-production')
    FLASK_ENV = os.getenv('FLASK_ENV', 'development')
    FLASK_PORT = int(os.getenv('FLASK_PORT', 5000))
    DEBUG = os.getenv('DEBUG', 'True').lower() == 'true'
    
    # Notion API
    NOTION_API_KEY = os.getenv('NOTION_API_KEY', '')
    NOTION_PARENT_PAGE_ID = os.getenv('NOTION_PARENT_PAGE_ID', '')
    
    # Database IDs (می‌تونن خالی باشن و بعد از Sync پر بشن)
    NOTION_TASKS_DB_ID = os.getenv('NOTION_TASKS_DB_ID', '')
    NOTION_PROJECTS_DB_ID = os.getenv('NOTION_PROJECTS_DB_ID', '')
    NOTION_RESOURCES_DB_ID = os.getenv('NOTION_RESOURCES_DB_ID', '')
    NOTION_DAILY_LOGS_DB_ID = os.getenv('NOTION_DAILY_LOGS_DB_ID', '')
    NOTION_HABITS_DB_ID = os.getenv('NOTION_HABITS_DB_ID', '')
    
    # Google Sheets
    GOOGLE_SHEETS_CREDENTIALS = os.getenv('GOOGLE_SHEETS_CREDENTIALS', './credentials.json')
    DAILY_LOG_SHEET_ID = os.getenv('DAILY_LOG_SHEET_ID', '')
    DAILY_LOG_SHEET_NAME = os.getenv('DAILY_LOG_SHEET_NAME', 'Sheet1')
    
    # Telegram (اختیاری)
    TELEGRAM_BOT_TOKEN = os.getenv('TELEGRAM_BOT_TOKEN', '')
    TELEGRAM_CHAT_ID = os.getenv('TELEGRAM_CHAT_ID', '')
    
    # Database
    DATABASE_PATH = os.getenv('DATABASE_PATH', './database/local.db')
    
    # App Settings
    USER_NAME = os.getenv('USER_NAME', 'کاربر')
    ITEMS_PER_PAGE = int(os.getenv('ITEMS_PER_PAGE', 10))
    
    # ستون‌های Google Sheet (نسخه 2.0 با 12 ستون)
    SHEET_COLUMNS = [
        'Date',              # A
        'Mood',              # B
        'Energy',            # C
        'Top Win',           # D
        'Main Obstacle',     # E
        'Techniques Suggested',  # F
        'Reflection',        # G
        'Techniques Used',   # H (جدید)
        'Bad Habits',        # I (جدید)
        'Good Habits',       # J (جدید)
        'Desires',           # K (جدید)
        'Daily Report'       # L (جدید)
    ]
    
    @classmethod
    def is_notion_configured(cls) -> bool:
        """بررسی اینکه آیا Notion API تنظیم شده"""
        return bool(cls.NOTION_API_KEY)
    
    @classmethod
    def is_notion_fully_configured(cls) -> bool:
        """بررسی اینکه آیا همه Database ها تنظیم شدن"""
        return bool(
            cls.NOTION_API_KEY and 
            cls.NOTION_TASKS_DB_ID and
            cls.NOTION_HABITS_DB_ID
        )
    
    @classmethod
    def can_sync_structure(cls) -> bool:
        """بررسی امکان Sync کردن ساختار"""
        return bool(cls.NOTION_API_KEY and cls.NOTION_PARENT_PAGE_ID)
    
    @classmethod
    def is_sheets_configured(cls) -> bool:
        """بررسی اینکه آیا Google Sheets تنظیم شده"""
        creds_path = Path(cls.GOOGLE_SHEETS_CREDENTIALS)
        return creds_path.exists() and bool(cls.DAILY_LOG_SHEET_ID)
    
    @classmethod
    def is_telegram_configured(cls) -> bool:
        """بررسی اینکه آیا Telegram تنظیم شده"""
        return bool(cls.TELEGRAM_BOT_TOKEN and cls.TELEGRAM_CHAT_ID)
    
    @classmethod
    def get_db_ids(cls) -> dict:
        """دریافت همه Database IDs"""
        return {
            'tasks': cls.NOTION_TASKS_DB_ID,
            'projects': cls.NOTION_PROJECTS_DB_ID,
            'resources': cls.NOTION_RESOURCES_DB_ID,
            'daily_logs': cls.NOTION_DAILY_LOGS_DB_ID,
            'habits': cls.NOTION_HABITS_DB_ID
        }
    
    @classmethod
    def update_db_id(cls, db_name: str, db_id: str):
        """بروزرسانی Database ID (در runtime)"""
        mapping = {
            'tasks': 'NOTION_TASKS_DB_ID',
            'projects': 'NOTION_PROJECTS_DB_ID',
            'resources': 'NOTION_RESOURCES_DB_ID',
            'daily_logs': 'NOTION_DAILY_LOGS_DB_ID',
            'habits': 'NOTION_HABITS_DB_ID'
        }
        if db_name in mapping:
            setattr(cls, mapping[db_name], db_id)
            # همچنین در env ذخیره کن
            os.environ[mapping[db_name]] = db_id


class DevelopmentConfig(Config):
    """تنظیمات توسعه"""
    DEBUG = True
    FLASK_ENV = 'development'


class ProductionConfig(Config):
    """تنظیمات تولید"""
    DEBUG = False
    FLASK_ENV = 'production'


# انتخاب تنظیمات بر اساس محیط
config_by_name = {
    'development': DevelopmentConfig,
    'production': ProductionConfig,
    'default': DevelopmentConfig
}


def get_config():
    """دریافت تنظیمات فعلی"""
    env = os.getenv('FLASK_ENV', 'development')
    return config_by_name.get(env, DevelopmentConfig)
