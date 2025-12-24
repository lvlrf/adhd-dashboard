-- ============================================
-- 🧠 ADHD Dashboard v3.0 - Database Schema
-- SQLite Database for local caching & offline
-- ============================================

-- جدول تسک‌ها
CREATE TABLE IF NOT EXISTS tasks (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    title TEXT NOT NULL,
    status TEXT DEFAULT 'Inbox',
    -- Values: Inbox, Next Action, In Progress, Waiting, Done, Someday/Maybe
    
    -- دسته‌بندی‌های خاص کاربر
    category TEXT,
    -- Values:
    -- 'تماس‌ها', 'لیست خرید', 'کارهای خرد شخصی', 'کارهای شخصی', 
    -- 'کارهای هنگامه', 'پیگیری‌ها', 'جلسه/بازدید', 'پیش‌فاکتور', 
    -- 'تایید پرداخت', 'دریافت تجهیزات', 'انجام پروژه', 'تحویل پروژه', 
    -- 'رضایت‌نامه', 'آموزش', 'پروژه عقب‌مانده', 'تعمیرات', 'ایده درآمدزایی'
    
    -- تگ‌ها به صورت JSON
    tags TEXT DEFAULT '{}',
    -- Format: {"person": ["Ali"], "project": ["Site A"], "general": ["Urgent"]}
    
    -- سطح انرژی مورد نیاز
    energy_level TEXT DEFAULT 'Medium',
    -- Values: High, Medium, Low
    
    -- اهمیت
    importance TEXT DEFAULT 'Medium',
    -- Values: High, Medium, Low
    
    -- فوریت
    urgency TEXT DEFAULT 'Normal',
    -- Values: Urgent, Soon, Normal, Low
    
    -- زمان‌بندی
    scheduled_for DATE,
    due_date DATE,
    completed_at DATETIME,
    
    -- زمان تخمینی (دقیقه)
    estimated_time INTEGER DEFAULT 15,
    
    -- Quick Win؟
    quick_win BOOLEAN DEFAULT 0,
    
    -- یادداشت
    notes TEXT,
    
    -- شناسه‌های خارجی
    notion_id TEXT UNIQUE,
    google_event_id TEXT,
    
    -- زمان‌های ایجاد و بروزرسانی
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    updated_at DATETIME DEFAULT CURRENT_TIMESTAMP
);

-- جدول پروژه‌ها
CREATE TABLE IF NOT EXISTS projects (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT NOT NULL,
    status TEXT DEFAULT 'Active',
    -- Values: Active, On Hold, Completed, Cancelled
    
    area TEXT,
    -- Values: کاری, مالی, یادگیری, شخصی, سلامت
    
    start_date DATE,
    target_date DATE,
    
    vision TEXT,
    archived BOOLEAN DEFAULT 0,
    
    notion_id TEXT UNIQUE,
    
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    updated_at DATETIME DEFAULT CURRENT_TIMESTAMP
);

-- جدول عادت‌ها
CREATE TABLE IF NOT EXISTS habits (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT NOT NULL,
    
    type TEXT DEFAULT 'good',
    -- Values: good, bad
    
    category TEXT,
    -- Values: سلامت/ورزش, ذهنی/یادگیری, کاری, خواب, تغذیه, دیجیتال, روحی
    
    status TEXT DEFAULT 'active',
    -- Values: active, paused, achieved, abandoned
    
    frequency TEXT DEFAULT 'daily',
    -- Values: daily, 3x_week, weekly, monthly
    
    start_date DATE DEFAULT CURRENT_DATE,
    
    counter INTEGER DEFAULT 0,
    streak INTEGER DEFAULT 0,
    best_streak INTEGER DEFAULT 0,
    last_logged DATE,
    
    trigger_text TEXT,
    replacement TEXT,
    why_important TEXT,
    
    notion_id TEXT UNIQUE,
    
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    updated_at DATETIME DEFAULT CURRENT_TIMESTAMP
);

-- جدول لاگ روزانه
CREATE TABLE IF NOT EXISTS daily_logs (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    log_date DATE UNIQUE NOT NULL,
    
    mood INTEGER CHECK(mood >= 1 AND mood <= 10),
    energy INTEGER CHECK(energy >= 1 AND energy <= 10),
    
    top_win TEXT,
    main_obstacle TEXT,
    
    techniques_suggested TEXT,
    techniques_used TEXT,
    
    bad_habits TEXT,
    good_habits TEXT,
    desires TEXT,
    
    reflection TEXT,
    daily_report TEXT,
    
    sleep_hours REAL,
    tasks_done INTEGER DEFAULT 0,
    
    synced_to_sheets BOOLEAN DEFAULT 0,
    
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP
);

-- جدول تنظیمات
CREATE TABLE IF NOT EXISTS settings (
    key TEXT PRIMARY KEY,
    value TEXT,
    updated_at DATETIME DEFAULT CURRENT_TIMESTAMP
);

-- جدول Sync Log
CREATE TABLE IF NOT EXISTS sync_logs (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    service TEXT NOT NULL,
    -- Values: notion, sheets
    
    action TEXT NOT NULL,
    -- Values: push, pull, create, update, delete
    
    entity_type TEXT,
    entity_id TEXT,
    
    status TEXT DEFAULT 'pending',
    -- Values: pending, success, failed
    
    error_message TEXT,
    
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP
);

-- ایندکس‌ها برای سرعت بیشتر
CREATE INDEX IF NOT EXISTS idx_tasks_status ON tasks(status);
CREATE INDEX IF NOT EXISTS idx_tasks_category ON tasks(category);
CREATE INDEX IF NOT EXISTS idx_tasks_due_date ON tasks(due_date);
CREATE INDEX IF NOT EXISTS idx_tasks_notion_id ON tasks(notion_id);

CREATE INDEX IF NOT EXISTS idx_habits_type ON habits(type);
CREATE INDEX IF NOT EXISTS idx_habits_status ON habits(status);

CREATE INDEX IF NOT EXISTS idx_daily_logs_date ON daily_logs(log_date);

-- داده‌های اولیه تنظیمات
INSERT OR IGNORE INTO settings (key, value) VALUES 
    ('user_name', 'کاربر'),
    ('theme', 'dark'),
    ('notion_connected', 'false'),
    ('sheets_connected', 'false'),
    ('sheets_id', ''),
    ('notion_parent_page', ''),
    ('last_sync', '');

-- Trigger برای بروزرسانی خودکار updated_at
CREATE TRIGGER IF NOT EXISTS update_tasks_timestamp 
AFTER UPDATE ON tasks
BEGIN
    UPDATE tasks SET updated_at = CURRENT_TIMESTAMP WHERE id = NEW.id;
END;

CREATE TRIGGER IF NOT EXISTS update_habits_timestamp 
AFTER UPDATE ON habits
BEGIN
    UPDATE habits SET updated_at = CURRENT_TIMESTAMP WHERE id = NEW.id;
END;

CREATE TRIGGER IF NOT EXISTS update_projects_timestamp 
AFTER UPDATE ON projects
BEGIN
    UPDATE projects SET updated_at = CURRENT_TIMESTAMP WHERE id = NEW.id;
END;
