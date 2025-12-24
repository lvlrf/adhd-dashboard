# 📚 راهنمای کامل: ADHD System v2.1 - تمام Prompts

**تاریخ:** 24 دسامبر 2024  
**نسخه:** 2.1 Complete Package

---

## 📦 فایل‌های این بسته:

### 1️⃣ **Create_Sheet_Prompt_v2.md** (31KB)
🎯 **کاربرد:** ساخت خودکار Google Sheet با ساختار واقعی

**چی داره:**
- ✅ Auto-detect تمام Tab ها (بدون نیاز به .env)
- ✅ ساخت Sheet با 3 Tab کامل
- ✅ Tab 1: Daily Log (17 ستون)
- ✅ Tab 2: Brain Dump Archive (12 ستون)
- ✅ Tab 3: Analytics
- ✅ Conditional Formatting
- ✅ Data Validation (Dropdowns)
- ✅ Formulas
- ✅ امکان اضافه کردن Tab جدید از Dashboard

**کجا استفاده کنم:**
→ این رو به چت Dashboard قبلی بفرست (همون جایی که Dashboard رو ساختی)

---

### 2️⃣ **Dashboard_Mega_Update_v2.1.md** (34KB) ⭐ **جامع‌ترین!**
🎯 **کاربرد:** بروزرسانی کامل Dashboard با تمام Features درخواستی

**چی داره:**
✅ **مدیریت Task ها:**
   - تخصیص به "امروز" با تیک زدن
   - Drag & Drop برای تغییر تاریخ
   - ویرایش inline

✅ **دسته‌بندی سفارشی:**
   - تماس‌ها
   - لیست خرید
   - کارهای خرد شخصی / شخصی
   - کارهای هنگامه
   - روند پروژه (11 مرحله)
   - امکان اضافه کردن دسته جدید

✅ **سیستم تگ:**
   - تگ پروژه (📁)
   - تگ شخص/مشتری (👤)
   - تگ وابستگی (🔗)

✅ **فیلترها:**
   - فیلتر هفته (جاری، بعد، این ماه)
   - فیلتر ددلاین (عقب‌افتاده، امروز، فردا، این هفته)
   - فیلتر دسته‌بندی
   - تارگت هفته

✅ **View های متنوع:**
   - List View
   - Ribbon View (ریبونی)
   - Kanban View (Trello-like)
   - همه Responsive

✅ **Recurring Tasks:**
   - روزانه / هفتگی / ماهانه / سفارشی
   - انتخاب روزهای هفته
   - تاریخ پایان

✅ **Notifications:**
   - Telegram Bot
   - Google Calendar Sync
   - یادآوری قبل از ددلاین

✅ **Responsive Design:**
   - Mobile First
   - Tablet
   - Desktop

**کجا استفاده کنم:**
→ این رو هم به چت Dashboard قبلی بفرست

---

### 3️⃣ **Sync_System_Prompt.md** (23KB)
🎯 **کاربرد:** همگام‌سازی دو طرفه بین Notion ↔ Sheet ↔ Dashboard

**چی داره:**
- ✅ Notion → Dashboard (هر 5 دقیقه)
- ✅ Dashboard → Notion (لحظه‌ای)
- ✅ Dashboard → Sheet (هر ساعت)
- ✅ Scheduler خودکار (Cron Jobs)
- ✅ Conflict Resolution
- ✅ Error Handling & Retry
- ✅ Rate Limiting
- ✅ Sync Status UI

**معماری:**
```
Notion (Source of Truth)
   ↓ Sync (5 min)
Dashboard (Main Interface)
   ↓ Backup (1 hour)
Google Sheet (Analytics)
```

**کجا استفاده کنم:**
→ بعد از اینکه Dashboard بروز شد، این رو هم بفرست

---

## 🚀 نحوه استفاده (گام به گام):

### مرحله 1: ساخت Google Sheet ✅
```
1. برو به چت Dashboard قبلی
2. کپی کن تمام محتوای "Create_Sheet_Prompt_v2.md"
3. پیست کن و بفرست
4. صبر کن تا کد اضافه بشه
5. نصب کن dependencies:
   npm install googleapis
6. Start کن Dashboard:
   npm run dev
7. برو Settings → Create Google Sheet
8. Sheet ID رو کپی کن و در .env ذخیره کن
```

### مرحله 2: بروزرسانی Dashboard ✅
```
1. همون چت Dashboard
2. کپی کن "Dashboard_Mega_Update_v2.1.md"
3. پیست کن و بفرست
4. نصب کن dependencies:
   npm install react-dnd react-dnd-html5-backend
   npm install node-telegram-bot-api
   npm install node-cron
   npm install dayjs
5. Restart Dashboard
6. چک کن Features جدید
```

### مرحله 3: همگام‌سازی ✅
```
1. همون چت Dashboard
2. کپی کن "Sync_System_Prompt.md"
3. پیست کن و بفرست
4. نصب کن dependencies:
   npm install @notionhq/client
   npm install p-limit
5. تنظیم کن Environment Variables:
   NOTION_API_KEY=...
   NOTION_TASKS_DB_ID=...
   TELEGRAM_BOT_TOKEN=...
6. Restart Dashboard
7. چک کن Sync Status در Settings
```

---

## 📊 Environment Variables مورد نیاز:

```env
# -------------------------
# Google Sheets
# -------------------------
GOOGLE_SHEETS_CREDENTIALS=./credentials.json

# -------------------------
# Notion API
# -------------------------
NOTION_API_KEY=secret_xxxxx
NOTION_TASKS_DB_ID=xxxxx
NOTION_PROJECTS_DB_ID=xxxxx
NOTION_HABITS_DB_ID=xxxxx
NOTION_DAILY_LOGS_DB_ID=xxxxx

# -------------------------
# Telegram Bot
# -------------------------
TELEGRAM_BOT_TOKEN=123456:ABC-xxxxx

# -------------------------
# Google Calendar (optional)
# -------------------------
GOOGLE_CALENDAR_CREDENTIALS=./calendar-credentials.json

# -------------------------
# App
# -------------------------
APP_URL=http://localhost:3000
```

---

## 🗄️ Database Schema Updates:

```sql
-- Tasks
ALTER TABLE tasks ADD COLUMN category VARCHAR(100);
ALTER TABLE tasks ADD COLUMN tags JSON;
ALTER TABLE tasks ADD COLUMN is_recurring BOOLEAN DEFAULT FALSE;
ALTER TABLE tasks ADD COLUMN recurring_type ENUM('daily', 'weekly', 'monthly', 'custom');
ALTER TABLE tasks ADD COLUMN recurring_days JSON;
ALTER TABLE tasks ADD COLUMN last_created_at DATETIME;
ALTER TABLE tasks ADD COLUMN notion_id VARCHAR(100) UNIQUE;
ALTER TABLE tasks ADD COLUMN last_synced DATETIME;
ALTER TABLE tasks ADD COLUMN notion_url TEXT;

-- Custom Categories
CREATE TABLE custom_categories (
  id INT PRIMARY KEY AUTO_INCREMENT,
  user_id INT,
  name VARCHAR(100),
  icon VARCHAR(10),
  created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Telegram
CREATE TABLE telegram_activations (
  id INT PRIMARY KEY AUTO_INCREMENT,
  chat_id BIGINT,
  code VARCHAR(20),
  expires_at DATETIME,
  activated BOOLEAN DEFAULT FALSE
);

-- Sync Log
CREATE TABLE sync_log (
  id INT PRIMARY KEY AUTO_INCREMENT,
  sync_type ENUM('notion_to_db', 'db_to_notion', 'db_to_sheet'),
  status ENUM('success', 'failed'),
  records_synced INT DEFAULT 0,
  error_message TEXT,
  started_at DATETIME,
  completed_at DATETIME,
  duration_seconds INT
);
```

---

## 🎯 اولویت‌بندی پیاده‌سازی:

### Priority 1 (حیاتی - همین الان):
1. ✅ Create Google Sheet
2. ✅ دسته‌بندی‌های سفارشی
3. ✅ سیستم تگ
4. ✅ View Switcher (List/Ribbon/Kanban)

### Priority 2 (مهم - این هفته):
5. ✅ فیلترها
6. ✅ تخصیص به امروز
7. ✅ Drag & Drop
8. ✅ Sync System

### Priority 3 (خوب به داشتن - بعداً):
9. ✅ Recurring Tasks
10. ✅ Telegram Notifications
11. ✅ Google Calendar Sync

---

## 🐛 Troubleshooting:

### مشکل 1: Google Sheets API Error
```
خطا: "The caller does not have permission"
راه حل:
1. چک کن credentials.json موجود هست
2. چک کن Google Sheets API فعال هست
3. Sheet رو با service account email Share کن
```

### مشکل 2: Notion Sync نمی‌کنه
```
خطا: "Could not find database"
راه حل:
1. چک کن NOTION_API_KEY درسته
2. چک کن Database ID ها درسته
3. چک کن Integration به Database دسترسی داره
```

### مشکل 3: Telegram Bot پاسخ نمیده
```
خطا: "Bot token invalid"
راه حل:
1. از BotFather توکن جدید بگیر
2. چک کن TELEGRAM_BOT_TOKEN در .env درسته
3. Restart کن Dashboard
```

---

## 📞 پشتیبانی:

اگه مشکلی داری:
1. اول فایل‌های راهنما رو بخون
2. Console Logs رو چک کن
3. Error Message رو کامل بفرست

---

## 🎁 Bonus Features:

### در این بسته:
- ✅ 8 Components جدید React
- ✅ 5 Services Backend
- ✅ 3 Schedulers (Cron Jobs)
- ✅ 2 External API Integrations (Telegram + Google)
- ✅ 1 سیستم کامل Sync
- ✅ Responsive Design
- ✅ RTL Support
- ✅ Error Handling
- ✅ Rate Limiting

---

## 📈 آمار این بسته:

```
خطوط کد تقریبی: 3000+
فایل‌های Prompt: 3
حجم کل: 88KB
زمان پیاده‌سازی تخمینی: 8-12 ساعت
```

---

**موفق باشی! این قدرتمندترین سیستم ADHD هست که ساختیم!** 🚀💪

**سوال داری؟ بپرس!** 💙
