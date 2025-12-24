# 🧠 ADHD Task Dashboard v2.0

داشبورد مدیریت کارها و عادت‌ها، بهینه‌شده برای ذهن‌های ADHD

![Python](https://img.shields.io/badge/Python-3.10+-blue)
![Flask](https://img.shields.io/badge/Flask-3.0-green)
![Notion](https://img.shields.io/badge/Notion-API-black)

## ✨ امکانات نسخه 2.0

### 🔥 قابلیت‌های اصلی
- **ماتریس آیزنهاور** - دسته‌بندی کارها (بحران، رشد، مزاحمت، اتلاف)
- **Habits Tracker** 🆕 - ردیابی عادت‌های خوب و بد با Streak
- **Sync Notion Structure** 🆕 - ساخت خودکار Database ها از فایل MD
- **Import از Gem** - ورود Task ها از JSON
- **5 Database Notion** - Tasks, Projects, Resources, Daily Logs, Habits

### 📊 نمودارهای جدید
- Bad Habits Frequency (Bar Chart)
- Good Habits Streak (Line Chart)
- Techniques Usage (Pie Chart)
- Mood & Energy Trend

### 📈 Google Sheets (12 ستون)
- Date, Mood, Energy, Top Win, Main Obstacle
- Techniques Suggested, Reflection
- **Techniques Used** 🆕
- **Bad Habits** 🆕
- **Good Habits** 🆕
- **Desires** 🆕
- **Daily Report** 🆕

---

## 🚀 نصب سریع

```bash
# 1. کلون پروژه
git clone https://github.com/your-username/adhd-dashboard.git
cd adhd-dashboard

# 2. نصب پکیج‌ها
pip install -r requirements.txt --break-system-packages

# 3. تنظیم محیط
cp .env.example .env
nano .env  # مقادیر رو پر کن

# 4. اجرا
python app.py
```

برنامه روی http://localhost:5000 اجرا میشه.

---

## ⚙️ تنظیمات

### 1. Notion API

#### ساخت Integration
1. برو به [notion.so/my-integrations](https://www.notion.so/my-integrations)
2. **New integration** → نام: `ADHD Dashboard`
3. توکن رو کپی کن (شروع با `secret_`)

#### تنظیم Parent Page
1. یک صفحه خالی در Notion بساز (مثلا "🧠 ADHD System")
2. صفحه رو Share کن با Integration
3. از URL، شناسه Page رو بردار

```
https://www.notion.so/My-Page-abc123def456...
                       ↑↑↑↑↑↑↑↑↑↑↑↑↑↑↑↑
                       این قسمت = NOTION_PARENT_PAGE_ID
```

#### Sync Structure
بعد از تنظیم، از Settings دکمه **Sync Notion Structure** رو بزن تا 5 Database خودکار ساخته بشن.

---

### 2. Google Sheets API

#### ساخت Service Account
1. [console.cloud.google.com](https://console.cloud.google.com) → New Project
2. APIs & Services → Enable: **Google Sheets API**
3. Credentials → Service Account → Create Key (JSON)
4. فایل رو بذار کنار پروژه: `credentials.json`

#### اتصال Sheet
1. Sheet رو با `client_email` از credentials.json شیر کن
2. شناسه Sheet رو از URL بردار

---

## 📁 ساختار پروژه

```
adhd-dashboard/
├── app.py              # اپلیکیشن Flask
├── config.py           # تنظیمات
├── requirements.txt    # پکیج‌ها
├── .env.example        # نمونه محیط
│
├── templates/
│   ├── base.html       # قالب پایه
│   ├── dashboard.html  # صفحه اصلی
│   ├── tasks.html      # لیست کارها
│   ├── habits.html     # 🆕 عادت‌ها
│   ├── import.html     # ورود داده
│   ├── analytics.html  # آمار
│   └── settings.html   # تنظیمات + Sync
│
├── static/
│   ├── css/main.css
│   └── js/
│       ├── main.js
│       ├── charts.js
│       └── import.js
│
└── utils/
    ├── notion_api.py   # API نوشن + Sync
    └── sheets_api.py   # API شیت (12 ستون)
```

---

## 🔧 API Endpoints

### Tasks
| Method | Endpoint | توضیح |
|--------|----------|-------|
| GET | `/api/tasks` | لیست کارها |
| POST | `/api/tasks` | ایجاد کار |
| PATCH | `/api/tasks/<id>` | بروزرسانی |
| DELETE | `/api/tasks/<id>` | حذف |
| POST | `/api/tasks/<id>/done` | علامت Done |

### Habits 🆕
| Method | Endpoint | توضیح |
|--------|----------|-------|
| GET | `/api/habits` | لیست عادت‌ها |
| POST | `/api/habits` | ایجاد عادت |
| PATCH | `/api/habits/<id>` | بروزرسانی |
| POST | `/api/habits/<id>/increment` | افزایش Counter |

### Sync 🆕
| Method | Endpoint | توضیح |
|--------|----------|-------|
| POST | `/api/sync-notion` | ساخت Database ها |

### Analytics
| Method | Endpoint | توضیح |
|--------|----------|-------|
| GET | `/api/mood-data` | داده Mood/Energy |
| GET | `/api/analytics/bad-habits` | فراوانی عادت بد |
| GET | `/api/analytics/good-habits` | روند عادت خوب |
| GET | `/api/analytics/techniques` | استفاده تکنیک‌ها |

---

## 🖥️ استقرار Production

### با Gunicorn + Nginx

```bash
# نصب
pip install gunicorn

# اجرا
gunicorn --bind 0.0.0.0:5000 app:app
```

### Systemd Service

```ini
# /etc/systemd/system/adhd-dashboard.service
[Unit]
Description=ADHD Dashboard
After=network.target

[Service]
User=www-data
WorkingDirectory=/var/www/adhd-dashboard
ExecStart=/var/www/adhd-dashboard/venv/bin/gunicorn --bind unix:app.sock app:app

[Install]
WantedBy=multi-user.target
```

### Nginx Config

```nginx
server {
    listen 80;
    server_name your-domain.com;

    location / {
        proxy_pass http://unix:/var/www/adhd-dashboard/app.sock;
        include proxy_params;
    }

    location /static {
        alias /var/www/adhd-dashboard/static;
    }
}
```

---

## 🎯 ساختار Notion

### Database ها
1. **📋 Tasks** - کارها با Eisenhower Matrix
2. **📁 Projects** - پروژه‌ها
3. **📚 Resources** - منابع و لینک‌ها
4. **📊 Daily Logs** - لاگ روزانه
5. **🎯 Habits** 🆕 - عادت‌ها

### فیلدهای Tasks
- Name, Status, Context, Energy Level
- Importance, Urgency, Estimated Time
- Due Date, Quick Win, Notes

### فیلدهای Habits 🆕
- Habit Name, Type (خوب/بد), Category
- Status, Frequency, Start Date
- Counter, Streak, Best Streak
- Trigger, Replacement, Why Important

---

## 🐛 عیب‌یابی

### Notion متصل نمیشه
- توکن با `secret_` شروع میشه؟
- Integration به Page وصله؟
- Parent Page ID درسته؟

### Sync کار نمیکنه
- Parent Page ID تنظیم شده؟
- Integration دسترسی داره؟

### Sheet خطا میده
- `credentials.json` کنار app.py هست؟
- Sheet با email سرویس اکانت شیر شده؟

---

## 📝 لایسنس

MIT License

---

## 💜 ساخته شده با عشق

برای همه ذهن‌های ADHD که مدیریت کارها براشون چالشه.

**نسخه 2.0** - با پشتیبانی از Habits و Sync Structure
