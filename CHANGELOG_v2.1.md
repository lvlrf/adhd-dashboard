# 📝 تغییرات نسخه 2.1 - Habits Tracking & Advanced Features

**تاریخ:** 23 دسامبر 2024

---

## 🎉 ویژگی‌های جدید عمده:

### 1️⃣ **سیستم ردیابی عادت‌ها (Habits Tracking System)** ✨

#### Database جدید در Notion:
- **Database: Habits** با 14 Property
- ردیابی عادت‌های خوب 🟢 (می‌خوام داشته باشم)
- ردیابی عادت‌های بد 🔴 (می‌خوام ترک کنم)
- Counter خودکار از Daily Coach
- Streak Tracking (چند روز پشت سر هم)
- Trigger Identification
- Replacement suggestions

#### 4 View جدید:
- Active Habits Tracker (Table)
- Bad Habits to Break (Board)
- Habits Timeline (Timeline)
- Achieved Habits (Gallery)

---

### 2️⃣ **Pattern Detection پیشرفته در Daily Coach** 🔍

5 نوع الگو شناسایی می‌شود:

#### الف) الگوی زمانی (Temporal Pattern)
```
مثال: "3 روز پشت سر هم می‌گی خستگی داری"
```

#### ب) الگوی محرک-واکنش (Trigger-Response)
```
مثال: "وقتی پروژه بلندمدت می‌بینی → احساس استرس → فرار به یوتیوب"
```

#### ج) الگوی چرخه‌ای (Cyclical Pattern)
```
مثال: "انگیزه بالا → کار زیاد → Burnout → انگیزه صفر"
```

#### د) الگوی اجتنابی (Avoidance Pattern)
```
مثال: "Task هایی که Estimated Time بالا دارن → همیشه Skip"
```

#### ه) الگوی علت-معلول (Causal Pattern)
```
مثال: "خواب کم → انرژی پایین → اهمال‌کاری"
```

**خروجی:**
- فرضیه علمی
- تحلیل داده‌محور
- پیشنهاد مداخله (Intervention)

---

### 3️⃣ **Technique Reminder & Checker** 🎯

Daily Coach حالا چک می‌کنه:
- ✅ کدوم تکنیک‌ها استفاده شده
- ❌ کدوم تکنیک‌ها فراموش شده
- 🔔 یادآوری عادت‌های خوب Skip شده
- 🔔 یادآوری Weekly Review

**بخش جدید در خروجی:**
```
═══════════════════════════════════════════════════════
🎯 بررسی تکنیک‌ها و یادآوری‌ها
═══════════════════════════════════════════════════════

✅ تکنیک‌های امروز: Pomodoro (2 بار)
❌ فراموش شده: دیروز گفتم 'دور کردن محرک'
🔔 یادآوری: Weekly Review جمعه عصره!
```

---

### 4️⃣ **گزارش روزانه کامل (Daily Report)** 📊

**ستون جدید در Google Sheet:**
- تمام متن مکالمه روزانه ذخیره می‌شه
- قابل جستجو
- مثل دفترچه خاطرات
- برای تحلیل الگوها در آینده

**کاربرد:**
```
بعد از چند ماه می‌تونی:
- الگوهای فکری رو ببینی
- تکرار نگرانی‌ها رو شناسایی کنی
- پیشرفت رو مشاهده کنی
```

---

### 5️⃣ **پیشنهاد خرد کردن کار (با تایید کاربر)** 🔨

**تغییر در Brain Dump:**
- قبلا: Gem خودش کار رو خُرد می‌کرد
- حالا: فقط پیشنهاد می‌ده و منتظر تایید می‌مونه
- کاربر می‌تونه ویرایش کنه
- استفاده از "Stupidly Small Tasks"

**مثال:**
```
Gem: پیشنهاد من:
1. [Task] باز کردن Notion (🪶 Low - ⚡<5min)
2. [Task] انتخاب قالب سایت (⚡ Medium - 🕑30min)
...

تایید می‌کنی؟

من: Task 3 رو به 2 تا تقسیم کن

Gem: باشه، اصلاح شد! تایید نهایی؟
```

---

### 6️⃣ **Deduplication هوشمند** 🧹

**مشکل قبلی:**
```
روز 1: "می‌خوام کتاب بخونم" → عادت جدید
روز 2: "می‌خوام مطالعه کنم" → عادت جدید (تکراری!)
روز 3: "می‌خوام کتاب‌خوانی داشته باشم" → عادت جدید (تکراری!)
```

**حالا:**
```
روز 1: "می‌خوام کتاب بخونم" → عادت جدید ✅
روز 2: "می‌خوام مطالعه کنم" → دیدم دوباره 'مطالعه' رو ذکر کردی (2 بار)
روز 3: "می‌خوام کتاب‌خوانی داشته باشم" → دیدم دوباره 'مطالعه' رو ذکر کردی (3 بار)
```

---

## 📊 تغییرات فایل‌ها:

### ✅ Mega_Prompt_Daily_Coach.md (41KB)
**اضافه شده:**
- مرحله 1.5: Habits & Desires Tracking
- مرحله 2.5: Pattern Detection (پیشرفته)
- مرحله 3.5: Technique Reminder & Checker
- CSV Output بروز شده (12 ستون، قبلا 7 ستون بود)
- Daily Report (Full Text)

**ستون‌های جدید CSV:**
8. Techniques Used (استفاده شده)
9. Bad Habits (عادت‌های بد)
10. Good Habits (عادت‌های خوب)
11. Desires (خواسته‌ها)
12. Daily Report (گزارش کامل)

---

### ✅ Mega_Prompt_Brain_Dump.md (19KB)
**اضافه شده:**
- سیستم پیشنهاد + تایید کاربر
- Stupidly Small Tasks در مثال‌ها
- تاکید بر "تو ذهنیت بهتری داری"

---

### ✅ ADHD_Notion_Structure.md (24KB)
**اضافه شده:**
- Database 5: Habits (با 14 Property)
- 4 View جدید برای Habits
- بخش Habits در Dashboard Layout
- توضیحات کامل Integration با Daily Coach

---

### ✅ Google_Sheet_Template_Guide.md (10KB)
**اضافه شده:**
- 5 ستون جدید در Tab 1: Daily Log
  - Techniques Used
  - Bad Habits
  - Good Habits
  - Desires
  - Daily Report
- 3 Chart جدید:
  - Bad Habits Frequency
  - Good Habits Streak
  - Techniques Usage
- Conditional Formatting جدید
- Formula های اضافی

---

## 🔢 آمار تغییرات:

```
فایل                       | سایز قبل | سایز حالا | افزایش
---------------------------|----------|-----------|--------
Mega_Prompt_Daily_Coach    | 26KB     | 41KB      | +58%
Mega_Prompt_Brain_Dump     | 17KB     | 19KB      | +12%
ADHD_Notion_Structure      | 20KB     | 24KB      | +20%
Google_Sheet_Template      | 7.9KB    | 10KB      | +27%
---------------------------|----------|-----------|--------
جمع                        | 71KB     | 94KB      | +32%
```

**خطوط کد اضافه شده:** ~1200+ خط

---

## 🎯 تغییر در تجربه کاربر:

### قبل از این نسخه:
```
Daily Coach:
- فقط تحلیل روز
- پیشنهاد تکنیک
- CSV ساده (7 ستون)

Brain Dump:
- خودکار خُرد می‌کرد
- کنترل کامل با Gem

Notion:
- فقط Tasks & Projects
- بدون ردیابی عادت
```

### بعد از این نسخه:
```
Daily Coach:
- تحلیل روز ✓
- پیشنهاد تکنیک ✓
- ردیابی عادت‌ها ✨
- شناسایی الگوها ✨
- چک کردن تکنیک‌ها ✨
- یادآوری‌های هوشمند ✨
- CSV پیشرفته (12 ستون) ✨
- گزارش کامل روزانه ✨

Brain Dump:
- پیشنهاد خُرد کردن ✨
- منتظر تایید کاربر ✨
- امکان ویرایش ✨

Notion:
- Tasks & Projects ✓
- Database Habits ✨
- 4 View جدید ✨
- Trigger Tracking ✨
- Streak Counter ✨
```

---

## 🚀 قدم بعدی:

### برای استفاده فوری:

#### 1. بروز کردن Gem #2 (Daily Coach):
```
1. برو Google AI Studio
2. پیدا کن Gem #2
3. Edit کن System Instructions
4. کپی کن محتوای Mega_Prompt_Daily_Coach.md جدید
5. Save
```

#### 2. بروز کردن Gem #1 (Brain Dump):
```
1. برو Google AI Studio
2. پیدا کن Gem #1
3. Edit کن System Instructions
4. کپی کن محتوای Mega_Prompt_Brain_Dump.md جدید
5. Save
```

#### 3. اضافه کردن Database Habits در Notion:
```
1. باز کن Notion Workspace
2. ایجاد Database جدید: "Habits"
3. اضافه کن Properties طبق راهنمای ADHD_Notion_Structure.md
4. ساخت 4 View جدید
```

#### 4. بروز کردن Google Sheet:
```
1. باز کن Sheet فعلی
2. اضافه کن 5 ستون جدید به Tab 1
3. اضافه کن Chart های جدید به Tab 3
```

---

## 💡 نکات مهم:

### ✅ سازگاری با نسخه قبل:
- تمام فایل‌های قبلی کار می‌کنن
- فقط ویژگی‌های جدید اضافه شده
- هیچ چیزی حذف نشده

### ⚠️ توصیه‌ها:
1. **اول Gem ها رو بروز کن** - این مهم‌ترینه
2. **بعد Notion رو** - Database Habits اضافه کن
3. **آخر Sheet رو** - ستون‌های جدید اضافه کن
4. **تدریجی پیش برو** - همه چیز یکجا نه!

### 🎁 Bonus:
- حالا می‌تونی الگوهای عمیق رو ببینی
- می‌تونی پیشرفت عادت‌ها رو Track کنی
- می‌تونی بعد چند ماه Daily Report ها رو بخونی
- می‌تونی Trigger ها رو شناسایی کنی

---

## 📞 پشتیبانی:

اگه سوالی داری یا مشکلی پیش اومد:
- بخون INDEX.md (راهنمای کلی)
- بخون MASTER_GUIDE.md (راهنمای جامع)
- یا بیا اینجا بپرس!

---

**موفق باشی!** 🚀💙
