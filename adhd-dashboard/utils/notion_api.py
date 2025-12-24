"""
ماژول ارتباط با Notion API - نسخه 2.0
شامل:
- CRUD برای Tasks, Projects, Resources, Daily Logs, Habits
- Sync Structure (ساخت/بروزرسانی Database ها از فایل MD)
- آمار و گزارش
"""

import re
import logging
from typing import Optional, List, Dict, Any
from datetime import datetime, timedelta
from notion_client import Client
from notion_client.errors import APIResponseError

logger = logging.getLogger(__name__)


class NotionAPI:
    """کلاس مدیریت ارتباط با Notion"""
    
    def __init__(self, api_key: str):
        """سازنده کلاس"""
        self.client = Client(auth=api_key)
        self.api_version = "2022-06-28"
        
        # تعریف ساختار Database ها
        self._define_schemas()
    
    def _define_schemas(self):
        """تعریف schema های پیش‌فرض برای هر Database"""
        
        # مقادیر Status برای Tasks
        self.task_status_options = [
            {"name": "📥 Inbox", "color": "default"},
            {"name": "▶️ Next Action", "color": "blue"},
            {"name": "🔄 In Progress", "color": "yellow"},
            {"name": "⏳ Waiting", "color": "orange"},
            {"name": "✅ Done", "color": "green"},
            {"name": "💭 Someday/Maybe", "color": "gray"}
        ]
        
        # مقادیر Context
        self.context_options = [
            {"name": "📞 تماس", "color": "red"},
            {"name": "💬 پیام", "color": "pink"},
            {"name": "🛒 خرید", "color": "purple"},
            {"name": "💻 پشت سیستم", "color": "blue"},
            {"name": "🚗 بیرون خانه", "color": "green"},
            {"name": "🏢 دفتر", "color": "yellow"},
            {"name": "🏠 خانه", "color": "orange"},
            {"name": "📧 ایمیل", "color": "brown"}
        ]
        
        # مقادیر Energy Level
        self.energy_options = [
            {"name": "🔥 High Focus", "color": "red"},
            {"name": "⚡ Medium", "color": "yellow"},
            {"name": "🪶 Low Focus", "color": "blue"}
        ]
        
        # مقادیر Importance
        self.importance_options = [
            {"name": "🔴 High", "color": "red"},
            {"name": "🟡 Medium", "color": "yellow"},
            {"name": "🟢 Low", "color": "green"}
        ]
        
        # مقادیر Urgency
        self.urgency_options = [
            {"name": "🚨 Urgent", "color": "red"},
            {"name": "⏰ Soon", "color": "orange"},
            {"name": "📅 Normal", "color": "blue"},
            {"name": "🐢 Low", "color": "gray"}
        ]
        
        # مقادیر Estimated Time
        self.time_options = [
            {"name": "⚡ < 5 min", "color": "green"},
            {"name": "🕐 15 min", "color": "blue"},
            {"name": "🕑 30 min", "color": "yellow"},
            {"name": "🕓 1 hour", "color": "orange"},
            {"name": "🕕 2+ hours", "color": "red"}
        ]
        
        # مقادیر Habit Type
        self.habit_type_options = [
            {"name": "🟢 عادت خوب", "color": "green"},
            {"name": "🔴 عادت بد", "color": "red"}
        ]
        
        # مقادیر Habit Category
        self.habit_category_options = [
            {"name": "🏃 سلامت/ورزش", "color": "green"},
            {"name": "🧠 ذهنی/یادگیری", "color": "blue"},
            {"name": "💼 کاری", "color": "yellow"},
            {"name": "😴 خواب", "color": "purple"},
            {"name": "🍽️ تغذیه", "color": "orange"},
            {"name": "📱 دیجیتال", "color": "pink"},
            {"name": "🧘 روحی/ذهن‌آگاهی", "color": "brown"}
        ]
        
        # مقادیر Habit Status
        self.habit_status_options = [
            {"name": "🎯 Active", "color": "blue"},
            {"name": "⏸️ Paused", "color": "yellow"},
            {"name": "✅ Achieved", "color": "green"},
            {"name": "❌ Abandoned", "color": "red"}
        ]
        
        # مقادیر Habit Frequency
        self.habit_frequency_options = [
            {"name": "روزانه", "color": "red"},
            {"name": "3 بار در هفته", "color": "orange"},
            {"name": "هفتگی", "color": "yellow"},
            {"name": "ماهانه", "color": "blue"}
        ]
        
        # مقادیر Project Status
        self.project_status_options = [
            {"name": "🟢 Active", "color": "green"},
            {"name": "⏸️ On Hold", "color": "yellow"},
            {"name": "💭 Someday/Maybe", "color": "gray"},
            {"name": "✅ Completed", "color": "blue"},
            {"name": "❌ Cancelled", "color": "red"}
        ]
        
        # مقادیر Area
        self.area_options = [
            {"name": "💼 کاری", "color": "blue"},
            {"name": "💰 مالی", "color": "green"},
            {"name": "🎓 یادگیری", "color": "purple"},
            {"name": "🏠 شخصی", "color": "orange"},
            {"name": "🏥 سلامت", "color": "red"}
        ]
        
        # مقادیر Resource Type
        self.resource_type_options = [
            {"name": "📖 کتاب", "color": "brown"},
            {"name": "🎥 ویدیو/دوره", "color": "red"},
            {"name": "📝 مقاله", "color": "blue"},
            {"name": "💡 ایده", "color": "yellow"},
            {"name": "🔗 لینک", "color": "gray"}
        ]
        
        # مقادیر Resource Status
        self.resource_status_options = [
            {"name": "📥 To Consume", "color": "default"},
            {"name": "📖 In Progress", "color": "yellow"},
            {"name": "✅ Done", "color": "green"},
            {"name": "🗄️ Reference", "color": "blue"}
        ]
        
        # Mood/Energy Scores (1-10)
        self.score_options = [{"name": str(i), "color": "default"} for i in range(1, 11)]

    # ============================================
    # Sync Structure - ساخت/بروزرسانی Database ها
    # ============================================
    
    def parse_structure_md(self, md_content: str) -> List[Dict]:
        """
        پارس کردن فایل MD ساختار Notion
        
        Args:
            md_content: محتوای فایل Markdown
            
        Returns:
            لیست Database ها با Properties
        """
        databases = []
        
        # پیدا کردن بخش‌های Database
        # الگو: ### Database X: NAME یا ### Database X: EMOJI NAME
        db_pattern = r'### Database \d+: (?:[\U0001F300-\U0001F9FF]\s*)?(.+?)(?:\n|$)'
        
        # پیدا کردن جداول Properties
        # هر جدول شامل | **Property** | Type | Options | Description |
        table_pattern = r'\| \*\*(.+?)\*\* \| (.+?) \| (.+?) \| (.+?) \|'
        
        # تقسیم بر اساس Database ها
        sections = re.split(r'### Database \d+:', md_content)
        
        for i, section in enumerate(sections[1:], 1):  # Skip first empty section
            lines = section.strip().split('\n')
            if not lines:
                continue
            
            # نام Database
            db_name = lines[0].strip()
            # حذف emoji از اول اگه بود
            db_name = re.sub(r'^[\U0001F300-\U0001F9FF]\s*', '', db_name).strip()
            
            # پیدا کردن Properties از جدول
            properties = []
            for line in lines:
                match = re.match(table_pattern, line)
                if match:
                    prop_name = match.group(1).strip()
                    prop_type = match.group(2).strip()
                    prop_options = match.group(3).strip()
                    prop_desc = match.group(4).strip()
                    
                    # Skip header row
                    if prop_name == "Property Name":
                        continue
                    
                    properties.append({
                        "name": prop_name,
                        "type": self._map_property_type(prop_type),
                        "options": self._parse_options(prop_options),
                        "description": prop_desc
                    })
            
            if properties:
                databases.append({
                    "name": db_name,
                    "properties": properties
                })
        
        logger.info(f"پارس شد: {len(databases)} دیتابیس")
        return databases
    
    def _map_property_type(self, md_type: str) -> str:
        """تبدیل نوع Property از MD به Notion API"""
        mapping = {
            'Title': 'title',
            'Text': 'rich_text',
            'Select': 'select',
            'Multi-select': 'multi_select',
            'Date': 'date',
            'Number': 'number',
            'Checkbox': 'checkbox',
            'Relation': 'relation',
            'Rollup': 'rollup',
            'Formula': 'formula',
            'URL': 'url'
        }
        return mapping.get(md_type, 'rich_text')
    
    def _parse_options(self, options_str: str) -> List[Dict]:
        """پارس کردن Options از متن"""
        if options_str == '-' or not options_str:
            return []
        
        # الگوهای مختلف: "• Option 1<br>• Option 2" یا "Option1, Option2"
        options = []
        
        # حذف <br> و تقسیم
        parts = re.split(r'<br>|,', options_str)
        
        for part in parts:
            # حذف bullet و whitespace
            opt = re.sub(r'^[•\-\*]\s*', '', part.strip())
            if opt and opt != '-':
                # استخراج رنگ اگه بود (مثلا "Option (red)")
                color_match = re.match(r'(.+?)\s*\((\w+)\)$', opt)
                if color_match:
                    options.append({
                        "name": color_match.group(1).strip(),
                        "color": color_match.group(2)
                    })
                else:
                    options.append({"name": opt, "color": "default"})
        
        return options
    
    def sync_structure(self, parent_page_id: str, md_content: str = None) -> Dict:
        """
        Sync کردن ساختار Notion از فایل MD
        
        Args:
            parent_page_id: شناسه صفحه Parent
            md_content: محتوای فایل MD (اختیاری - اگه نباشه از default استفاده میشه)
            
        Returns:
            نتیجه شامل created, updated, errors
        """
        result = {
            "created": [],
            "updated": [],
            "errors": [],
            "db_ids": {}
        }
        
        # اگه MD نداریم، از ساختار پیش‌فرض استفاده کن
        databases = self._get_default_databases() if not md_content else self.parse_structure_md(md_content)
        
        for db in databases:
            try:
                db_name = db["name"]
                
                # چک کن آیا Database وجود داره
                existing = self._find_database_by_name(parent_page_id, db_name)
                
                if existing:
                    # بروزرسانی Properties
                    updated = self._update_database_properties(existing["id"], db["properties"])
                    if updated:
                        result["updated"].append(db_name)
                        result["db_ids"][self._db_name_to_key(db_name)] = existing["id"]
                else:
                    # ایجاد Database جدید
                    new_db = self._create_database(parent_page_id, db_name, db["properties"])
                    if new_db:
                        result["created"].append(db_name)
                        result["db_ids"][self._db_name_to_key(db_name)] = new_db["id"]
                        
            except Exception as e:
                logger.error(f"خطا در پردازش {db['name']}: {e}")
                result["errors"].append(f"{db['name']}: {str(e)}")
        
        return result
    
    def _db_name_to_key(self, name: str) -> str:
        """تبدیل نام Database به key"""
        mapping = {
            "Tasks": "tasks",
            "Projects": "projects",
            "Resources": "resources",
            "Daily Logs": "daily_logs",
            "Habits": "habits"
        }
        # حذف emoji و پیدا کردن
        clean_name = re.sub(r'[\U0001F300-\U0001F9FF]\s*', '', name).strip()
        for k, v in mapping.items():
            if k.lower() in clean_name.lower():
                return v
        return clean_name.lower().replace(' ', '_')
    
    def _find_database_by_name(self, parent_page_id: str, name: str) -> Optional[Dict]:
        """پیدا کردن Database با نام در صفحه Parent"""
        try:
            # جستجو در children صفحه
            response = self.client.blocks.children.list(block_id=parent_page_id)
            
            for block in response.get("results", []):
                if block["type"] == "child_database":
                    db_title = block.get("child_database", {}).get("title", "")
                    if name.lower() in db_title.lower():
                        return {"id": block["id"], "title": db_title}
            
            return None
        except Exception as e:
            logger.error(f"خطا در جستجوی Database: {e}")
            return None
    
    def _create_database(self, parent_page_id: str, name: str, properties: List[Dict]) -> Optional[Dict]:
        """ایجاد Database جدید"""
        try:
            notion_props = self._convert_to_notion_properties(properties, name)
            
            response = self.client.databases.create(
                parent={"type": "page_id", "page_id": parent_page_id},
                title=[{"type": "text", "text": {"content": name}}],
                properties=notion_props
            )
            
            logger.info(f"Database ایجاد شد: {name}")
            return response
            
        except APIResponseError as e:
            logger.error(f"خطای API در ایجاد Database {name}: {e}")
            return None
    
    def _update_database_properties(self, db_id: str, properties: List[Dict]) -> bool:
        """بروزرسانی Properties یک Database"""
        try:
            # فعلاً فقط لاگ میکنیم - بروزرسانی Properties پیچیده‌تره
            logger.info(f"Database موجود: {db_id}")
            return True
        except Exception as e:
            logger.error(f"خطا در بروزرسانی: {e}")
            return False
    
    def _convert_to_notion_properties(self, properties: List[Dict], db_name: str) -> Dict:
        """تبدیل Properties به فرمت Notion API"""
        notion_props = {}
        
        for prop in properties:
            name = prop["name"]
            ptype = prop["type"]
            options = prop.get("options", [])
            
            if ptype == "title":
                notion_props[name] = {"title": {}}
            
            elif ptype == "rich_text":
                notion_props[name] = {"rich_text": {}}
            
            elif ptype == "select":
                # استفاده از options پیش‌فرض اگه موجود بود
                opts = self._get_default_options(name, db_name) or options
                notion_props[name] = {"select": {"options": opts}}
            
            elif ptype == "multi_select":
                opts = self._get_default_options(name, db_name) or options
                notion_props[name] = {"multi_select": {"options": opts}}
            
            elif ptype == "number":
                notion_props[name] = {"number": {"format": "number"}}
            
            elif ptype == "checkbox":
                notion_props[name] = {"checkbox": {}}
            
            elif ptype == "date":
                notion_props[name] = {"date": {}}
            
            elif ptype == "url":
                notion_props[name] = {"url": {}}
            
            # Relation, Rollup, Formula نیاز به پیاده‌سازی جداگانه دارن
        
        return notion_props
    
    def _get_default_options(self, prop_name: str, db_name: str) -> List[Dict]:
        """دریافت Options پیش‌فرض برای Property"""
        defaults = {
            "Status": self.task_status_options if "Task" in db_name else 
                      self.habit_status_options if "Habit" in db_name else
                      self.project_status_options,
            "Context": self.context_options,
            "Energy Level": self.energy_options,
            "Importance": self.importance_options,
            "Urgency": self.urgency_options,
            "Estimated Time": self.time_options,
            "Type": self.habit_type_options if "Habit" in db_name else self.resource_type_options,
            "Category": self.habit_category_options,
            "Frequency": self.habit_frequency_options,
            "Area": self.area_options,
            "Mood Score": self.score_options,
            "Energy Score": self.score_options
        }
        return defaults.get(prop_name, [])
    
    def _get_default_databases(self) -> List[Dict]:
        """ساختار پیش‌فرض Database ها"""
        return [
            {
                "name": "📋 Tasks",
                "properties": [
                    {"name": "Name", "type": "title"},
                    {"name": "Status", "type": "select"},
                    {"name": "Context", "type": "multi_select"},
                    {"name": "Energy Level", "type": "select"},
                    {"name": "Importance", "type": "select"},
                    {"name": "Urgency", "type": "select"},
                    {"name": "Estimated Time", "type": "select"},
                    {"name": "Due Date", "type": "date"},
                    {"name": "Scheduled For", "type": "date"},
                    {"name": "Quick Win", "type": "checkbox"},
                    {"name": "Completed Date", "type": "date"},
                    {"name": "Notes", "type": "rich_text"}
                ]
            },
            {
                "name": "📁 Projects",
                "properties": [
                    {"name": "Name", "type": "title"},
                    {"name": "Status", "type": "select"},
                    {"name": "Area", "type": "select"},
                    {"name": "Start Date", "type": "date"},
                    {"name": "Target Date", "type": "date"},
                    {"name": "Vision/Why", "type": "rich_text"},
                    {"name": "Archived", "type": "checkbox"}
                ]
            },
            {
                "name": "📚 Resources",
                "properties": [
                    {"name": "Name", "type": "title"},
                    {"name": "Type", "type": "select"},
                    {"name": "Status", "type": "select"},
                    {"name": "Area", "type": "select"},
                    {"name": "URL", "type": "url"},
                    {"name": "Notes", "type": "rich_text"}
                ]
            },
            {
                "name": "📊 Daily Logs",
                "properties": [
                    {"name": "Date", "type": "title"},
                    {"name": "Mood Score", "type": "select"},
                    {"name": "Energy Score", "type": "select"},
                    {"name": "Top Win", "type": "rich_text"},
                    {"name": "Main Obstacle", "type": "rich_text"},
                    {"name": "Techniques Used", "type": "multi_select"},
                    {"name": "Sleep Hours", "type": "number"},
                    {"name": "Tasks Done", "type": "number"},
                    {"name": "Reflection", "type": "rich_text"}
                ]
            },
            {
                "name": "🎯 Habits",
                "properties": [
                    {"name": "Habit Name", "type": "title"},
                    {"name": "Type", "type": "select"},
                    {"name": "Category", "type": "select"},
                    {"name": "Status", "type": "select"},
                    {"name": "Frequency", "type": "select"},
                    {"name": "Start Date", "type": "date"},
                    {"name": "Counter", "type": "number"},
                    {"name": "Last Mentioned", "type": "date"},
                    {"name": "Streak", "type": "number"},
                    {"name": "Best Streak", "type": "number"},
                    {"name": "Related Trigger", "type": "rich_text"},
                    {"name": "Replacement", "type": "rich_text"},
                    {"name": "Why Important", "type": "rich_text"},
                    {"name": "Notes", "type": "rich_text"}
                ]
            }
        ]

    # ============================================
    # Tasks CRUD
    # ============================================
    
    def _parse_task(self, page: dict) -> dict:
        """تبدیل داده Notion به فرمت برنامه"""
        props = page.get("properties", {})
        
        # استخراج عنوان
        title = ""
        if "Name" in props and props["Name"].get("title"):
            title = props["Name"]["title"][0]["plain_text"] if props["Name"]["title"] else ""
        
        # استخراج Status
        status = ""
        if "Status" in props and props["Status"].get("select"):
            status = props["Status"]["select"].get("name", "")
        
        # استخراج Context (multi-select)
        context = []
        if "Context" in props and props["Context"].get("multi_select"):
            context = [item["name"] for item in props["Context"]["multi_select"]]
        
        # استخراج Energy Level
        energy = ""
        if "Energy Level" in props and props["Energy Level"].get("select"):
            energy = props["Energy Level"]["select"].get("name", "")
        
        # استخراج Importance
        importance = ""
        if "Importance" in props and props["Importance"].get("select"):
            importance = props["Importance"]["select"].get("name", "")
        
        # استخراج Urgency
        urgency = ""
        if "Urgency" in props and props["Urgency"].get("select"):
            urgency = props["Urgency"]["select"].get("name", "")
        
        # استخراج Estimated Time
        time_est = ""
        if "Estimated Time" in props and props["Estimated Time"].get("select"):
            time_est = props["Estimated Time"]["select"].get("name", "")
        
        # استخراج Due Date
        due_date = None
        if "Due Date" in props and props["Due Date"].get("date"):
            due_date = props["Due Date"]["date"].get("start")
        
        # استخراج Quick Win
        quick_win = False
        if "Quick Win" in props:
            quick_win = props["Quick Win"].get("checkbox", False)
        
        # استخراج Notes
        notes = ""
        if "Notes" in props and props["Notes"].get("rich_text"):
            notes = props["Notes"]["rich_text"][0]["plain_text"] if props["Notes"]["rich_text"] else ""
        
        # محاسبه Quadrant
        quadrant = self._calculate_quadrant(importance, urgency)
        
        return {
            "id": page["id"],
            "title": title,
            "status": status,
            "context": context,
            "energy": energy,
            "importance": importance,
            "urgency": urgency,
            "time": time_est,
            "due_date": due_date,
            "quick_win": quick_win,
            "notes": notes,
            "quadrant": quadrant,
            "url": page.get("url", ""),
            "created_time": page.get("created_time"),
            "last_edited_time": page.get("last_edited_time")
        }
    
    def _calculate_quadrant(self, importance: str, urgency: str) -> int:
        """محاسبه کوادرانت ماتریس آیزنهاور"""
        is_important = "High" in importance or "🔴" in importance
        is_urgent = "Urgent" in urgency or "🚨" in urgency or "Soon" in urgency or "⏰" in urgency
        
        if is_important and is_urgent:
            return 1  # بحران
        elif is_important and not is_urgent:
            return 2  # ذکاوت
        elif not is_important and is_urgent:
            return 3  # حواس‌پرتی
        else:
            return 4  # اتلاف
    
    def fetch_tasks(self, database_id: str, include_done: bool = False) -> List[Dict]:
        """دریافت Task ها از Notion"""
        try:
            query_params = {"database_id": database_id}
            
            if not include_done:
                query_params["filter"] = {
                    "and": [
                        {"property": "Status", "select": {"does_not_equal": "✅ Done"}},
                        {"property": "Status", "select": {"does_not_equal": "Done"}}
                    ]
                }
            
            query_params["sorts"] = [
                {"property": "Urgency", "direction": "ascending"},
                {"property": "Importance", "direction": "ascending"}
            ]
            
            response = self.client.databases.query(**query_params)
            
            tasks = [self._parse_task(page) for page in response.get("results", [])]
            logger.info(f"دریافت {len(tasks)} تسک")
            return tasks
            
        except Exception as e:
            logger.error(f"خطا در دریافت Tasks: {e}")
            return []
    
    def create_task(self, database_id: str, task_data: dict) -> Optional[Dict]:
        """ایجاد Task جدید"""
        try:
            properties = {
                "Name": {"title": [{"text": {"content": task_data.get("title", "")}}]}
            }
            
            if task_data.get("status"):
                properties["Status"] = {"select": {"name": task_data["status"]}}
            
            if task_data.get("context"):
                contexts = task_data["context"] if isinstance(task_data["context"], list) else [task_data["context"]]
                properties["Context"] = {"multi_select": [{"name": c} for c in contexts]}
            
            if task_data.get("energy"):
                properties["Energy Level"] = {"select": {"name": task_data["energy"]}}
            
            if task_data.get("importance"):
                properties["Importance"] = {"select": {"name": task_data["importance"]}}
            
            if task_data.get("urgency"):
                properties["Urgency"] = {"select": {"name": task_data["urgency"]}}
            
            if task_data.get("time"):
                properties["Estimated Time"] = {"select": {"name": task_data["time"]}}
            
            if task_data.get("due_date"):
                properties["Due Date"] = {"date": {"start": task_data["due_date"]}}
            
            if task_data.get("quick_win") is not None:
                properties["Quick Win"] = {"checkbox": task_data["quick_win"]}
            
            if task_data.get("notes"):
                properties["Notes"] = {"rich_text": [{"text": {"content": task_data["notes"]}}]}
            
            response = self.client.pages.create(
                parent={"database_id": database_id},
                properties=properties
            )
            
            logger.info(f"Task ایجاد شد: {task_data.get('title')}")
            return self._parse_task(response)
            
        except Exception as e:
            logger.error(f"خطا در ایجاد Task: {e}")
            return None
    
    def update_task(self, page_id: str, task_data: dict) -> Optional[Dict]:
        """بروزرسانی Task"""
        try:
            properties = {}
            
            if "title" in task_data:
                properties["Name"] = {"title": [{"text": {"content": task_data["title"]}}]}
            
            if "status" in task_data:
                properties["Status"] = {"select": {"name": task_data["status"]}}
            
            if "context" in task_data:
                contexts = task_data["context"] if isinstance(task_data["context"], list) else [task_data["context"]]
                properties["Context"] = {"multi_select": [{"name": c} for c in contexts]}
            
            if "energy" in task_data:
                properties["Energy Level"] = {"select": {"name": task_data["energy"]}}
            
            if "importance" in task_data:
                properties["Importance"] = {"select": {"name": task_data["importance"]}}
            
            if "urgency" in task_data:
                properties["Urgency"] = {"select": {"name": task_data["urgency"]}}
            
            if "time" in task_data:
                properties["Estimated Time"] = {"select": {"name": task_data["time"]}}
            
            if "due_date" in task_data:
                properties["Due Date"] = {"date": {"start": task_data["due_date"]} if task_data["due_date"] else None}
            
            if "quick_win" in task_data:
                properties["Quick Win"] = {"checkbox": task_data["quick_win"]}
            
            if "notes" in task_data:
                properties["Notes"] = {"rich_text": [{"text": {"content": task_data["notes"]}}]}
            
            response = self.client.pages.update(page_id=page_id, properties=properties)
            
            logger.info(f"Task بروزرسانی شد: {page_id}")
            return self._parse_task(response)
            
        except Exception as e:
            logger.error(f"خطا در بروزرسانی Task: {e}")
            return None
    
    def delete_task(self, page_id: str) -> bool:
        """آرشیو Task"""
        try:
            self.client.pages.update(page_id=page_id, archived=True)
            logger.info(f"Task آرشیو شد: {page_id}")
            return True
        except Exception as e:
            logger.error(f"خطا در آرشیو Task: {e}")
            return False
    
    def mark_done(self, page_id: str) -> Optional[Dict]:
        """تغییر وضعیت به Done"""
        return self.update_task(page_id, {"status": "✅ Done"})

    # ============================================
    # Habits CRUD
    # ============================================
    
    def _parse_habit(self, page: dict) -> dict:
        """تبدیل داده Notion به فرمت Habit"""
        props = page.get("properties", {})
        
        # نام
        name = ""
        if "Habit Name" in props and props["Habit Name"].get("title"):
            name = props["Habit Name"]["title"][0]["plain_text"] if props["Habit Name"]["title"] else ""
        
        # Type
        habit_type = ""
        if "Type" in props and props["Type"].get("select"):
            habit_type = props["Type"]["select"].get("name", "")
        
        # Category
        category = ""
        if "Category" in props and props["Category"].get("select"):
            category = props["Category"]["select"].get("name", "")
        
        # Status
        status = ""
        if "Status" in props and props["Status"].get("select"):
            status = props["Status"]["select"].get("name", "")
        
        # Frequency
        frequency = ""
        if "Frequency" in props and props["Frequency"].get("select"):
            frequency = props["Frequency"]["select"].get("name", "")
        
        # Start Date
        start_date = None
        if "Start Date" in props and props["Start Date"].get("date"):
            start_date = props["Start Date"]["date"].get("start")
        
        # Counter
        counter = 0
        if "Counter" in props and props["Counter"].get("number") is not None:
            counter = props["Counter"]["number"]
        
        # Last Mentioned
        last_mentioned = None
        if "Last Mentioned" in props and props["Last Mentioned"].get("date"):
            last_mentioned = props["Last Mentioned"]["date"].get("start")
        
        # Streak
        streak = 0
        if "Streak" in props and props["Streak"].get("number") is not None:
            streak = props["Streak"]["number"]
        
        # Best Streak
        best_streak = 0
        if "Best Streak" in props and props["Best Streak"].get("number") is not None:
            best_streak = props["Best Streak"]["number"]
        
        # Trigger
        trigger = ""
        if "Related Trigger" in props and props["Related Trigger"].get("rich_text"):
            trigger = props["Related Trigger"]["rich_text"][0]["plain_text"] if props["Related Trigger"]["rich_text"] else ""
        
        # Replacement
        replacement = ""
        if "Replacement" in props and props["Replacement"].get("rich_text"):
            replacement = props["Replacement"]["rich_text"][0]["plain_text"] if props["Replacement"]["rich_text"] else ""
        
        # Why Important
        why = ""
        if "Why Important" in props and props["Why Important"].get("rich_text"):
            why = props["Why Important"]["rich_text"][0]["plain_text"] if props["Why Important"]["rich_text"] else ""
        
        return {
            "id": page["id"],
            "name": name,
            "type": habit_type,
            "category": category,
            "status": status,
            "frequency": frequency,
            "start_date": start_date,
            "counter": counter,
            "last_mentioned": last_mentioned,
            "streak": streak,
            "best_streak": best_streak,
            "trigger": trigger,
            "replacement": replacement,
            "why": why,
            "is_good": "خوب" in habit_type or "🟢" in habit_type,
            "url": page.get("url", "")
        }
    
    def fetch_habits(self, database_id: str, filter_type: str = "all") -> List[Dict]:
        """دریافت Habits از Notion"""
        try:
            query_params = {"database_id": database_id}
            
            # فیلتر بر اساس نوع
            if filter_type == "good":
                query_params["filter"] = {
                    "property": "Type",
                    "select": {"equals": "🟢 عادت خوب"}
                }
            elif filter_type == "bad":
                query_params["filter"] = {
                    "property": "Type",
                    "select": {"equals": "🔴 عادت بد"}
                }
            elif filter_type == "active":
                query_params["filter"] = {
                    "property": "Status",
                    "select": {"equals": "🎯 Active"}
                }
            
            query_params["sorts"] = [
                {"property": "Streak", "direction": "descending"}
            ]
            
            response = self.client.databases.query(**query_params)
            
            habits = [self._parse_habit(page) for page in response.get("results", [])]
            logger.info(f"دریافت {len(habits)} عادت")
            return habits
            
        except Exception as e:
            logger.error(f"خطا در دریافت Habits: {e}")
            return []
    
    def create_habit(self, database_id: str, habit_data: dict) -> Optional[Dict]:
        """ایجاد Habit جدید"""
        try:
            properties = {
                "Habit Name": {"title": [{"text": {"content": habit_data.get("name", "")}}]}
            }
            
            if habit_data.get("type"):
                properties["Type"] = {"select": {"name": habit_data["type"]}}
            
            if habit_data.get("category"):
                properties["Category"] = {"select": {"name": habit_data["category"]}}
            
            if habit_data.get("status"):
                properties["Status"] = {"select": {"name": habit_data["status"]}}
            else:
                properties["Status"] = {"select": {"name": "🎯 Active"}}
            
            if habit_data.get("frequency"):
                properties["Frequency"] = {"select": {"name": habit_data["frequency"]}}
            
            if habit_data.get("start_date"):
                properties["Start Date"] = {"date": {"start": habit_data["start_date"]}}
            else:
                properties["Start Date"] = {"date": {"start": datetime.now().strftime("%Y-%m-%d")}}
            
            properties["Counter"] = {"number": habit_data.get("counter", 0)}
            properties["Streak"] = {"number": habit_data.get("streak", 0)}
            properties["Best Streak"] = {"number": habit_data.get("best_streak", 0)}
            
            if habit_data.get("trigger"):
                properties["Related Trigger"] = {"rich_text": [{"text": {"content": habit_data["trigger"]}}]}
            
            if habit_data.get("replacement"):
                properties["Replacement"] = {"rich_text": [{"text": {"content": habit_data["replacement"]}}]}
            
            if habit_data.get("why"):
                properties["Why Important"] = {"rich_text": [{"text": {"content": habit_data["why"]}}]}
            
            response = self.client.pages.create(
                parent={"database_id": database_id},
                properties=properties
            )
            
            logger.info(f"Habit ایجاد شد: {habit_data.get('name')}")
            return self._parse_habit(response)
            
        except Exception as e:
            logger.error(f"خطا در ایجاد Habit: {e}")
            return None
    
    def increment_habit(self, database_id: str, habit_id: str) -> Optional[Dict]:
        """افزایش Counter و بروزرسانی Streak"""
        try:
            # دریافت اطلاعات فعلی
            page = self.client.pages.retrieve(page_id=habit_id)
            habit = self._parse_habit(page)
            
            today = datetime.now().strftime("%Y-%m-%d")
            yesterday = (datetime.now() - timedelta(days=1)).strftime("%Y-%m-%d")
            
            new_counter = habit["counter"] + 1
            new_streak = habit["streak"]
            
            # محاسبه Streak
            last_mentioned = habit["last_mentioned"]
            if last_mentioned == yesterday:
                new_streak = habit["streak"] + 1
            elif last_mentioned != today:
                new_streak = 1  # Reset streak
            
            new_best = max(new_streak, habit["best_streak"])
            
            # بروزرسانی
            properties = {
                "Counter": {"number": new_counter},
                "Streak": {"number": new_streak},
                "Best Streak": {"number": new_best},
                "Last Mentioned": {"date": {"start": today}}
            }
            
            response = self.client.pages.update(page_id=habit_id, properties=properties)
            
            logger.info(f"Habit بروزرسانی شد: {habit['name']} (Counter: {new_counter}, Streak: {new_streak})")
            return self._parse_habit(response)
            
        except Exception as e:
            logger.error(f"خطا در افزایش Habit: {e}")
            return None
    
    def update_habit(self, habit_id: str, habit_data: dict) -> Optional[Dict]:
        """بروزرسانی Habit"""
        try:
            properties = {}
            
            if "name" in habit_data:
                properties["Habit Name"] = {"title": [{"text": {"content": habit_data["name"]}}]}
            
            if "type" in habit_data:
                properties["Type"] = {"select": {"name": habit_data["type"]}}
            
            if "category" in habit_data:
                properties["Category"] = {"select": {"name": habit_data["category"]}}
            
            if "status" in habit_data:
                properties["Status"] = {"select": {"name": habit_data["status"]}}
            
            if "frequency" in habit_data:
                properties["Frequency"] = {"select": {"name": habit_data["frequency"]}}
            
            if "trigger" in habit_data:
                properties["Related Trigger"] = {"rich_text": [{"text": {"content": habit_data["trigger"]}}]}
            
            if "replacement" in habit_data:
                properties["Replacement"] = {"rich_text": [{"text": {"content": habit_data["replacement"]}}]}
            
            if "why" in habit_data:
                properties["Why Important"] = {"rich_text": [{"text": {"content": habit_data["why"]}}]}
            
            response = self.client.pages.update(page_id=habit_id, properties=properties)
            
            return self._parse_habit(response)
            
        except Exception as e:
            logger.error(f"خطا در بروزرسانی Habit: {e}")
            return None

    # ============================================
    # Statistics
    # ============================================
    
    def get_task_stats(self, database_id: str) -> dict:
        """دریافت آمار Task ها"""
        try:
            all_tasks = self.fetch_tasks(database_id, include_done=True)
            today = datetime.now().date().isoformat()
            
            stats = {
                "total": len(all_tasks),
                "done": 0,
                "pending": 0,
                "urgent": 0,
                "done_today": 0,
                "by_quadrant": {1: 0, 2: 0, 3: 0, 4: 0},
                "by_energy": {"high": 0, "medium": 0, "low": 0},
                "by_context": {},
                "quick_wins_pending": 0
            }
            
            for task in all_tasks:
                if "Done" in task["status"] or "✅" in task["status"]:
                    stats["done"] += 1
                    if task.get("last_edited_time", "").startswith(today):
                        stats["done_today"] += 1
                else:
                    stats["pending"] += 1
                
                if "Urgent" in task.get("urgency", "") or "🚨" in task.get("urgency", ""):
                    stats["urgent"] += 1
                
                q = task.get("quadrant", 4)
                stats["by_quadrant"][q] += 1
                
                energy = task.get("energy", "")
                if "High" in energy or "🔥" in energy:
                    stats["by_energy"]["high"] += 1
                elif "Medium" in energy or "⚡" in energy:
                    stats["by_energy"]["medium"] += 1
                elif "Low" in energy or "🪶" in energy:
                    stats["by_energy"]["low"] += 1
                
                for ctx in task.get("context", []):
                    stats["by_context"][ctx] = stats["by_context"].get(ctx, 0) + 1
                
                if task.get("quick_win") and "Done" not in task.get("status", ""):
                    stats["quick_wins_pending"] += 1
            
            return stats
            
        except Exception as e:
            logger.error(f"خطا در دریافت آمار: {e}")
            return {}
    
    def get_habit_stats(self, database_id: str) -> dict:
        """دریافت آمار Habits"""
        try:
            all_habits = self.fetch_habits(database_id)
            
            stats = {
                "total": len(all_habits),
                "active": 0,
                "achieved": 0,
                "good_count": 0,
                "bad_count": 0,
                "longest_streak": 0,
                "total_counter": 0,
                "by_category": {}
            }
            
            for habit in all_habits:
                if "Active" in habit.get("status", "") or "🎯" in habit.get("status", ""):
                    stats["active"] += 1
                elif "Achieved" in habit.get("status", "") or "✅" in habit.get("status", ""):
                    stats["achieved"] += 1
                
                if habit.get("is_good"):
                    stats["good_count"] += 1
                else:
                    stats["bad_count"] += 1
                
                stats["longest_streak"] = max(stats["longest_streak"], habit.get("best_streak", 0))
                stats["total_counter"] += habit.get("counter", 0)
                
                cat = habit.get("category", "Other")
                stats["by_category"][cat] = stats["by_category"].get(cat, 0) + 1
            
            return stats
            
        except Exception as e:
            logger.error(f"خطا در دریافت آمار Habits: {e}")
            return {}
    
    def import_tasks_from_json(self, database_id: str, tasks_json: List[Dict]) -> dict:
        """Import کردن Task ها از JSON"""
        result = {"success": 0, "failed": 0, "errors": []}
        
        for task in tasks_json:
            created = self.create_task(database_id, task)
            if created:
                result["success"] += 1
            else:
                result["failed"] += 1
                result["errors"].append(f"خطا در ایجاد: {task.get('title', 'بدون عنوان')}")
        
        return result
