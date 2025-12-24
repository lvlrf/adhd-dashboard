"""
🗄️ Database Service v3.0
مدیریت SQLite Database برای ذخیره‌سازی محلی
"""

import os
import json
import sqlite3
import logging
from datetime import datetime, date
from pathlib import Path
from typing import Optional, List, Dict, Any
from contextlib import contextmanager

logger = logging.getLogger(__name__)


class DatabaseService:
    """سرویس مدیریت SQLite Database"""
    
    def __init__(self, db_path: str = './database/local.db'):
        """
        سازنده
        
        Args:
            db_path: مسیر فایل دیتابیس
        """
        self.db_path = Path(db_path)
        self.db_path.parent.mkdir(parents=True, exist_ok=True)
        self._init_db()
    
    def _init_db(self):
        """اولیه‌سازی دیتابیس"""
        schema_path = Path(__file__).parent.parent / 'database' / 'schema.sql'
        
        if schema_path.exists():
            with open(schema_path, 'r', encoding='utf-8') as f:
                schema = f.read()
            
            with self.get_connection() as conn:
                conn.executescript(schema)
                conn.commit()
            
            logger.info(f"Database initialized: {self.db_path}")
        else:
            logger.warning(f"Schema file not found: {schema_path}")
    
    @contextmanager
    def get_connection(self):
        """Context manager برای اتصال به دیتابیس"""
        conn = sqlite3.connect(str(self.db_path))
        conn.row_factory = sqlite3.Row
        try:
            yield conn
        finally:
            conn.close()
    
    # ============================================
    # Tasks CRUD
    # ============================================
    
    def create_task(self, task_data: Dict) -> Optional[int]:
        """ایجاد Task جدید"""
        sql = """
            INSERT INTO tasks (
                title, status, category, tags, energy_level, 
                importance, urgency, scheduled_for, due_date, 
                estimated_time, quick_win, notes, notion_id
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """
        
        try:
            with self.get_connection() as conn:
                cursor = conn.execute(sql, (
                    task_data.get('title', ''),
                    task_data.get('status', 'Inbox'),
                    task_data.get('category'),
                    json.dumps(task_data.get('tags', {}), ensure_ascii=False),
                    task_data.get('energy_level', 'Medium'),
                    task_data.get('importance', 'Medium'),
                    task_data.get('urgency', 'Normal'),
                    task_data.get('scheduled_for'),
                    task_data.get('due_date'),
                    task_data.get('estimated_time', 15),
                    1 if task_data.get('quick_win') else 0,
                    task_data.get('notes', ''),
                    task_data.get('notion_id')
                ))
                conn.commit()
                return cursor.lastrowid
        except Exception as e:
            logger.error(f"Error creating task: {e}")
            return None
    
    def get_tasks(
        self, 
        status: str = None, 
        category: str = None,
        include_done: bool = False
    ) -> List[Dict]:
        """دریافت لیست Task ها"""
        sql = "SELECT * FROM tasks WHERE 1=1"
        params = []
        
        if not include_done:
            sql += " AND status != 'Done'"
        
        if status:
            sql += " AND status = ?"
            params.append(status)
        
        if category:
            sql += " AND category = ?"
            params.append(category)
        
        sql += " ORDER BY urgency ASC, importance ASC, created_at DESC"
        
        try:
            with self.get_connection() as conn:
                cursor = conn.execute(sql, params)
                rows = cursor.fetchall()
                return [self._row_to_dict(row) for row in rows]
        except Exception as e:
            logger.error(f"Error fetching tasks: {e}")
            return []
    
    def get_task(self, task_id: int) -> Optional[Dict]:
        """دریافت یک Task"""
        try:
            with self.get_connection() as conn:
                cursor = conn.execute(
                    "SELECT * FROM tasks WHERE id = ?", 
                    (task_id,)
                )
                row = cursor.fetchone()
                return self._row_to_dict(row) if row else None
        except Exception as e:
            logger.error(f"Error fetching task: {e}")
            return None
    
    def update_task(self, task_id: int, task_data: Dict) -> bool:
        """بروزرسانی Task"""
        fields = []
        values = []
        
        field_mapping = {
            'title': 'title',
            'status': 'status',
            'category': 'category',
            'energy_level': 'energy_level',
            'importance': 'importance',
            'urgency': 'urgency',
            'scheduled_for': 'scheduled_for',
            'due_date': 'due_date',
            'estimated_time': 'estimated_time',
            'notes': 'notes'
        }
        
        for key, col in field_mapping.items():
            if key in task_data:
                fields.append(f"{col} = ?")
                values.append(task_data[key])
        
        if 'tags' in task_data:
            fields.append("tags = ?")
            values.append(json.dumps(task_data['tags'], ensure_ascii=False))
        
        if 'quick_win' in task_data:
            fields.append("quick_win = ?")
            values.append(1 if task_data['quick_win'] else 0)
        
        if not fields:
            return False
        
        values.append(task_id)
        sql = f"UPDATE tasks SET {', '.join(fields)} WHERE id = ?"
        
        try:
            with self.get_connection() as conn:
                conn.execute(sql, values)
                conn.commit()
                return True
        except Exception as e:
            logger.error(f"Error updating task: {e}")
            return False
    
    def complete_task(self, task_id: int) -> bool:
        """تکمیل Task"""
        try:
            with self.get_connection() as conn:
                conn.execute(
                    "UPDATE tasks SET status = 'Done', completed_at = ? WHERE id = ?",
                    (datetime.now().isoformat(), task_id)
                )
                conn.commit()
                return True
        except Exception as e:
            logger.error(f"Error completing task: {e}")
            return False
    
    def delete_task(self, task_id: int) -> bool:
        """حذف Task"""
        try:
            with self.get_connection() as conn:
                conn.execute("DELETE FROM tasks WHERE id = ?", (task_id,))
                conn.commit()
                return True
        except Exception as e:
            logger.error(f"Error deleting task: {e}")
            return False
    
    def get_task_stats(self) -> Dict:
        """دریافت آمار Task ها"""
        try:
            with self.get_connection() as conn:
                stats = {
                    'total': 0,
                    'done': 0,
                    'pending': 0,
                    'urgent': 0,
                    'by_status': {},
                    'by_category': {}
                }
                
                # Total
                cursor = conn.execute("SELECT COUNT(*) FROM tasks")
                stats['total'] = cursor.fetchone()[0]
                
                # Done
                cursor = conn.execute("SELECT COUNT(*) FROM tasks WHERE status = 'Done'")
                stats['done'] = cursor.fetchone()[0]
                
                # Pending
                stats['pending'] = stats['total'] - stats['done']
                
                # Urgent
                cursor = conn.execute("SELECT COUNT(*) FROM tasks WHERE urgency = 'Urgent' AND status != 'Done'")
                stats['urgent'] = cursor.fetchone()[0]
                
                # By Status
                cursor = conn.execute("SELECT status, COUNT(*) as cnt FROM tasks GROUP BY status")
                for row in cursor.fetchall():
                    stats['by_status'][row['status']] = row['cnt']
                
                # By Category
                cursor = conn.execute("SELECT category, COUNT(*) as cnt FROM tasks WHERE category IS NOT NULL GROUP BY category")
                for row in cursor.fetchall():
                    if row['category']:
                        stats['by_category'][row['category']] = row['cnt']
                
                return stats
        except Exception as e:
            logger.error(f"Error getting task stats: {e}")
            return {}
    
    # ============================================
    # Habits CRUD
    # ============================================
    
    def create_habit(self, habit_data: Dict) -> Optional[int]:
        """ایجاد Habit جدید"""
        sql = """
            INSERT INTO habits (
                name, type, category, status, frequency,
                start_date, trigger_text, replacement, why_important
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
        """
        
        try:
            with self.get_connection() as conn:
                cursor = conn.execute(sql, (
                    habit_data.get('name', ''),
                    habit_data.get('type', 'good'),
                    habit_data.get('category'),
                    habit_data.get('status', 'active'),
                    habit_data.get('frequency', 'daily'),
                    habit_data.get('start_date', date.today().isoformat()),
                    habit_data.get('trigger_text', ''),
                    habit_data.get('replacement', ''),
                    habit_data.get('why_important', '')
                ))
                conn.commit()
                return cursor.lastrowid
        except Exception as e:
            logger.error(f"Error creating habit: {e}")
            return None
    
    def get_habits(self, habit_type: str = None, status: str = None) -> List[Dict]:
        """دریافت لیست Habit ها"""
        sql = "SELECT * FROM habits WHERE 1=1"
        params = []
        
        if habit_type:
            sql += " AND type = ?"
            params.append(habit_type)
        
        if status:
            sql += " AND status = ?"
            params.append(status)
        
        sql += " ORDER BY streak DESC, counter DESC"
        
        try:
            with self.get_connection() as conn:
                cursor = conn.execute(sql, params)
                rows = cursor.fetchall()
                return [self._row_to_dict(row) for row in rows]
        except Exception as e:
            logger.error(f"Error fetching habits: {e}")
            return []
    
    def increment_habit(self, habit_id: int) -> Optional[Dict]:
        """افزایش Counter و بروزرسانی Streak"""
        try:
            with self.get_connection() as conn:
                # دریافت اطلاعات فعلی
                cursor = conn.execute("SELECT * FROM habits WHERE id = ?", (habit_id,))
                habit = cursor.fetchone()
                
                if not habit:
                    return None
                
                today = date.today().isoformat()
                yesterday = (date.today() - timedelta(days=1)).isoformat() if hasattr(date, 'today') else None
                
                # محاسبه Streak جدید
                last_logged = habit['last_logged']
                new_streak = habit['streak']
                
                if last_logged == yesterday:
                    new_streak = habit['streak'] + 1
                elif last_logged != today:
                    new_streak = 1
                
                new_best = max(new_streak, habit['best_streak'])
                new_counter = habit['counter'] + 1
                
                # بروزرسانی
                conn.execute("""
                    UPDATE habits SET 
                        counter = ?, streak = ?, best_streak = ?, last_logged = ?
                    WHERE id = ?
                """, (new_counter, new_streak, new_best, today, habit_id))
                conn.commit()
                
                # برگرداندن نتیجه
                cursor = conn.execute("SELECT * FROM habits WHERE id = ?", (habit_id,))
                return self._row_to_dict(cursor.fetchone())
                
        except Exception as e:
            logger.error(f"Error incrementing habit: {e}")
            return None
    
    def get_habit_stats(self) -> Dict:
        """دریافت آمار Habit ها"""
        try:
            with self.get_connection() as conn:
                stats = {
                    'total': 0,
                    'good_count': 0,
                    'bad_count': 0,
                    'active': 0,
                    'achieved': 0,
                    'longest_streak': 0,
                    'total_counter': 0
                }
                
                cursor = conn.execute("SELECT COUNT(*) FROM habits")
                stats['total'] = cursor.fetchone()[0]
                
                cursor = conn.execute("SELECT COUNT(*) FROM habits WHERE type = 'good'")
                stats['good_count'] = cursor.fetchone()[0]
                
                cursor = conn.execute("SELECT COUNT(*) FROM habits WHERE type = 'bad'")
                stats['bad_count'] = cursor.fetchone()[0]
                
                cursor = conn.execute("SELECT COUNT(*) FROM habits WHERE status = 'active'")
                stats['active'] = cursor.fetchone()[0]
                
                cursor = conn.execute("SELECT COUNT(*) FROM habits WHERE status = 'achieved'")
                stats['achieved'] = cursor.fetchone()[0]
                
                cursor = conn.execute("SELECT MAX(best_streak) FROM habits")
                stats['longest_streak'] = cursor.fetchone()[0] or 0
                
                cursor = conn.execute("SELECT SUM(counter) FROM habits")
                stats['total_counter'] = cursor.fetchone()[0] or 0
                
                return stats
        except Exception as e:
            logger.error(f"Error getting habit stats: {e}")
            return {}
    
    # ============================================
    # Daily Logs CRUD
    # ============================================
    
    def create_daily_log(self, log_data: Dict) -> Optional[int]:
        """ایجاد لاگ روزانه"""
        sql = """
            INSERT OR REPLACE INTO daily_logs (
                log_date, mood, energy, top_win, main_obstacle,
                techniques_suggested, techniques_used, bad_habits, good_habits,
                desires, reflection, daily_report, sleep_hours, tasks_done
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """
        
        try:
            with self.get_connection() as conn:
                cursor = conn.execute(sql, (
                    log_data.get('log_date', date.today().isoformat()),
                    log_data.get('mood', 5),
                    log_data.get('energy', 5),
                    log_data.get('top_win', ''),
                    log_data.get('main_obstacle', ''),
                    log_data.get('techniques_suggested', ''),
                    log_data.get('techniques_used', ''),
                    log_data.get('bad_habits', ''),
                    log_data.get('good_habits', ''),
                    log_data.get('desires', ''),
                    log_data.get('reflection', ''),
                    log_data.get('daily_report', ''),
                    log_data.get('sleep_hours'),
                    log_data.get('tasks_done', 0)
                ))
                conn.commit()
                return cursor.lastrowid
        except Exception as e:
            logger.error(f"Error creating daily log: {e}")
            return None
    
    def get_daily_logs(self, days: int = 30) -> List[Dict]:
        """دریافت لاگ‌های روزانه"""
        try:
            with self.get_connection() as conn:
                cursor = conn.execute("""
                    SELECT * FROM daily_logs 
                    ORDER BY log_date DESC 
                    LIMIT ?
                """, (days,))
                rows = cursor.fetchall()
                return [self._row_to_dict(row) for row in rows]
        except Exception as e:
            logger.error(f"Error fetching daily logs: {e}")
            return []
    
    def get_today_log(self) -> Optional[Dict]:
        """دریافت لاگ امروز"""
        try:
            with self.get_connection() as conn:
                cursor = conn.execute(
                    "SELECT * FROM daily_logs WHERE log_date = ?",
                    (date.today().isoformat(),)
                )
                row = cursor.fetchone()
                return self._row_to_dict(row) if row else None
        except Exception as e:
            logger.error(f"Error fetching today's log: {e}")
            return None
    
    # ============================================
    # Settings
    # ============================================
    
    def get_setting(self, key: str, default: str = None) -> Optional[str]:
        """دریافت تنظیم"""
        try:
            with self.get_connection() as conn:
                cursor = conn.execute(
                    "SELECT value FROM settings WHERE key = ?",
                    (key,)
                )
                row = cursor.fetchone()
                return row['value'] if row else default
        except Exception as e:
            logger.error(f"Error getting setting: {e}")
            return default
    
    def set_setting(self, key: str, value: str) -> bool:
        """ذخیره تنظیم"""
        try:
            with self.get_connection() as conn:
                conn.execute("""
                    INSERT OR REPLACE INTO settings (key, value, updated_at)
                    VALUES (?, ?, ?)
                """, (key, value, datetime.now().isoformat()))
                conn.commit()
                return True
        except Exception as e:
            logger.error(f"Error setting setting: {e}")
            return False
    
    def get_all_settings(self) -> Dict:
        """دریافت همه تنظیمات"""
        try:
            with self.get_connection() as conn:
                cursor = conn.execute("SELECT key, value FROM settings")
                return {row['key']: row['value'] for row in cursor.fetchall()}
        except Exception as e:
            logger.error(f"Error getting all settings: {e}")
            return {}
    
    # ============================================
    # Helpers
    # ============================================
    
    def _row_to_dict(self, row) -> Dict:
        """تبدیل Row به Dictionary"""
        if row is None:
            return {}
        
        d = dict(row)
        
        # Parse JSON fields
        if 'tags' in d and d['tags']:
            try:
                d['tags'] = json.loads(d['tags'])
            except:
                d['tags'] = {}
        
        return d


# Import timedelta
from datetime import timedelta


# ============================================
# Factory
# ============================================

def create_database_service(db_path: str = './database/local.db') -> DatabaseService:
    """Factory function"""
    return DatabaseService(db_path)
