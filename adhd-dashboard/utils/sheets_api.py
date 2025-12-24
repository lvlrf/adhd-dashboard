"""
ماژول ارتباط با Google Sheets API - نسخه 2.0
شامل 12 ستون:
- قدیمی: Date, Mood, Energy, Top Win, Main Obstacle, Techniques Suggested, Reflection
- جدید: Techniques Used, Bad Habits, Good Habits, Desires, Daily Report
"""

import logging
from typing import Optional, List, Dict
from datetime import datetime, timedelta
from pathlib import Path
from collections import Counter

import gspread
from google.oauth2.service_account import Credentials

logger = logging.getLogger(__name__)

# محدوده دسترسی‌های مورد نیاز
SCOPES = [
    'https://www.googleapis.com/auth/spreadsheets',
    'https://www.googleapis.com/auth/drive.readonly'
]

# ستون‌های Sheet (نسخه 2.0)
COLUMNS = {
    'DATE': 0,                  # A
    'MOOD': 1,                  # B
    'ENERGY': 2,                # C
    'TOP_WIN': 3,               # D
    'MAIN_OBSTACLE': 4,         # E
    'TECHNIQUES_SUGGESTED': 5,  # F
    'REFLECTION': 6,            # G
    'TECHNIQUES_USED': 7,       # H (جدید)
    'BAD_HABITS': 8,            # I (جدید)
    'GOOD_HABITS': 9,           # J (جدید)
    'DESIRES': 10,              # K (جدید)
    'DAILY_REPORT': 11          # L (جدید)
}


class SheetsAPI:
    """کلاس مدیریت ارتباط با Google Sheets"""
    
    def __init__(self, credentials_path: str):
        """سازنده کلاس"""
        self.credentials_path = Path(credentials_path)
        self.client = None
        self._connect()
    
    def _connect(self) -> bool:
        """اتصال به Google Sheets API"""
        try:
            if not self.credentials_path.exists():
                logger.error(f"فایل credentials یافت نشد: {self.credentials_path}")
                return False
            
            creds = Credentials.from_service_account_file(
                str(self.credentials_path),
                scopes=SCOPES
            )
            self.client = gspread.authorize(creds)
            logger.info("اتصال به Google Sheets برقرار شد")
            return True
            
        except Exception as e:
            logger.error(f"خطا در اتصال به Google Sheets: {e}")
            return False
    
    def is_connected(self) -> bool:
        """بررسی وضعیت اتصال"""
        return self.client is not None
    
    def get_sheet(self, sheet_id: str, sheet_name: str = "Sheet1"):
        """دریافت یک Sheet خاص"""
        try:
            spreadsheet = self.client.open_by_key(sheet_id)
            worksheet = spreadsheet.worksheet(sheet_name)
            return worksheet
        except Exception as e:
            logger.error(f"خطا در دریافت Sheet: {e}")
            return None
    
    # ============================================
    # Read Operations
    # ============================================
    
    def read_daily_logs(self, sheet_id: str, sheet_name: str = "Sheet1", 
                        days: int = 30) -> List[Dict]:
        """
        خواندن Daily Log ها با 12 ستون
        """
        try:
            worksheet = self.get_sheet(sheet_id, sheet_name)
            if not worksheet:
                return []
            
            all_values = worksheet.get_all_values()
            
            # Skip header row
            if len(all_values) > 0 and all_values[0][0].lower() == 'date':
                all_values = all_values[1:]
            
            logs = []
            cutoff_date = datetime.now() - timedelta(days=days)
            
            for row in all_values:
                try:
                    if len(row) < 1 or not row[0]:
                        continue
                    
                    date_str = row[0]
                    date_obj = self._parse_date(date_str)
                    
                    if not date_obj or date_obj < cutoff_date:
                        continue
                    
                    log = {
                        "date": date_obj.strftime("%Y-%m-%d"),
                        "mood": self._safe_int(row[COLUMNS['MOOD']] if len(row) > COLUMNS['MOOD'] else 5),
                        "energy": self._safe_int(row[COLUMNS['ENERGY']] if len(row) > COLUMNS['ENERGY'] else 5),
                        "top_win": row[COLUMNS['TOP_WIN']] if len(row) > COLUMNS['TOP_WIN'] else "",
                        "main_obstacle": row[COLUMNS['MAIN_OBSTACLE']] if len(row) > COLUMNS['MAIN_OBSTACLE'] else "",
                        "techniques_suggested": row[COLUMNS['TECHNIQUES_SUGGESTED']] if len(row) > COLUMNS['TECHNIQUES_SUGGESTED'] else "",
                        "reflection": row[COLUMNS['REFLECTION']] if len(row) > COLUMNS['REFLECTION'] else "",
                        # ستون‌های جدید
                        "techniques_used": row[COLUMNS['TECHNIQUES_USED']] if len(row) > COLUMNS['TECHNIQUES_USED'] else "",
                        "bad_habits": row[COLUMNS['BAD_HABITS']] if len(row) > COLUMNS['BAD_HABITS'] else "",
                        "good_habits": row[COLUMNS['GOOD_HABITS']] if len(row) > COLUMNS['GOOD_HABITS'] else "",
                        "desires": row[COLUMNS['DESIRES']] if len(row) > COLUMNS['DESIRES'] else "",
                        "daily_report": row[COLUMNS['DAILY_REPORT']] if len(row) > COLUMNS['DAILY_REPORT'] else ""
                    }
                    logs.append(log)
                    
                except Exception as e:
                    logger.warning(f"خطا در پردازش ردیف: {e}")
                    continue
            
            logs.sort(key=lambda x: x["date"])
            logger.info(f"خواندن {len(logs)} لاگ روزانه")
            return logs
            
        except Exception as e:
            logger.error(f"خطا در خواندن Daily Logs: {e}")
            return []
    
    def _parse_date(self, date_str: str) -> Optional[datetime]:
        """پارس تاریخ با فرمت‌های مختلف"""
        formats = ["%Y-%m-%d", "%Y/%m/%d", "%d/%m/%Y", "%m/%d/%Y", "%d-%m-%Y"]
        for fmt in formats:
            try:
                return datetime.strptime(date_str, fmt)
            except ValueError:
                continue
        return None
    
    def _safe_int(self, value, default: int = 5) -> int:
        """تبدیل امن به int"""
        try:
            return int(value)
        except (ValueError, TypeError):
            return default
    
    # ============================================
    # Write Operations
    # ============================================
    
    def append_daily_log(self, sheet_id: str, sheet_name: str, data: Dict) -> bool:
        """
        اضافه کردن لاگ روزانه جدید با 12 ستون
        """
        try:
            worksheet = self.get_sheet(sheet_id, sheet_name)
            if not worksheet:
                return False
            
            today = data.get('date', datetime.now().strftime("%Y-%m-%d"))
            
            row = [
                today,
                data.get('mood', 5),
                data.get('energy', 5),
                data.get('top_win', ''),
                data.get('main_obstacle', ''),
                data.get('techniques_suggested', ''),
                data.get('reflection', ''),
                data.get('techniques_used', ''),
                data.get('bad_habits', ''),
                data.get('good_habits', ''),
                data.get('desires', ''),
                data.get('daily_report', '')
            ]
            
            worksheet.append_row(row)
            logger.info(f"لاگ روزانه اضافه شد: {today}")
            return True
            
        except Exception as e:
            logger.error(f"خطا در اضافه کردن لاگ: {e}")
            return False
    
    # ============================================
    # Analytics
    # ============================================
    
    def get_mood_trend(self, sheet_id: str, sheet_name: str = "Sheet1",
                       days: int = 14) -> Dict:
        """دریافت روند Mood و Energy برای نمودار"""
        logs = self.read_daily_logs(sheet_id, sheet_name, days)
        
        return {
            "labels": [log["date"] for log in logs],
            "mood": [log["mood"] for log in logs],
            "energy": [log["energy"] for log in logs]
        }
    
    def get_analytics_summary(self, sheet_id: str, sheet_name: str = "Sheet1",
                              days: int = 30) -> Dict:
        """دریافت خلاصه آماری"""
        logs = self.read_daily_logs(sheet_id, sheet_name, days)
        
        if not logs:
            return {
                "avg_mood": 0,
                "avg_energy": 0,
                "days_tracked": 0,
                "trend": "neutral"
            }
        
        moods = [log["mood"] for log in logs]
        energies = [log["energy"] for log in logs]
        
        avg_mood = sum(moods) / len(moods)
        avg_energy = sum(energies) / len(energies)
        
        # تعیین روند
        mid = len(moods) // 2
        if mid > 0:
            first_half = sum(moods[:mid]) / mid
            second_half = sum(moods[mid:]) / (len(moods) - mid)
            
            if second_half > first_half + 0.5:
                trend = "improving"
            elif second_half < first_half - 0.5:
                trend = "declining"
            else:
                trend = "stable"
        else:
            trend = "neutral"
        
        return {
            "avg_mood": round(avg_mood, 1),
            "avg_energy": round(avg_energy, 1),
            "days_tracked": len(logs),
            "trend": trend
        }
    
    def get_bad_habits_frequency(self, sheet_id: str, sheet_name: str = "Sheet1",
                                  days: int = 30) -> List[Dict]:
        """
        دریافت فراوانی عادت‌های بد (برای نمودار Bar)
        """
        logs = self.read_daily_logs(sheet_id, sheet_name, days)
        
        frequency = Counter()
        
        for log in logs:
            bad_habits = log.get("bad_habits", "")
            if bad_habits and bad_habits != '-':
                habits = [h.strip() for h in bad_habits.split(',')]
                frequency.update(habits)
        
        return [{"name": name, "count": count} 
                for name, count in frequency.most_common(10)]
    
    def get_good_habits_streak(self, sheet_id: str, sheet_name: str = "Sheet1",
                                days: int = 30) -> List[Dict]:
        """
        دریافت روند عادت‌های خوب (برای نمودار Line)
        """
        logs = self.read_daily_logs(sheet_id, sheet_name, days)
        
        data = []
        for log in logs:
            good_habits = log.get("good_habits", "")
            count = len([h for h in good_habits.split(',') if h.strip() and h != '-']) if good_habits else 0
            data.append({
                "date": log["date"],
                "count": count
            })
        
        return data
    
    def get_techniques_usage(self, sheet_id: str, sheet_name: str = "Sheet1",
                              days: int = 30) -> List[Dict]:
        """
        دریافت استفاده از تکنیک‌ها (برای نمودار Pie)
        """
        logs = self.read_daily_logs(sheet_id, sheet_name, days)
        
        usage = Counter()
        
        for log in logs:
            techniques = log.get("techniques_used", "")
            if techniques and techniques != '-':
                techs = [t.strip() for t in techniques.split(',')]
                usage.update(techs)
        
        return [{"name": name, "value": value} 
                for name, value in usage.most_common()]
    
    def get_desires_analysis(self, sheet_id: str, sheet_name: str = "Sheet1",
                              days: int = 30) -> List[Dict]:
        """
        تحلیل خواسته‌ها و آرزوها
        """
        logs = self.read_daily_logs(sheet_id, sheet_name, days)
        
        desires = Counter()
        
        for log in logs:
            desire = log.get("desires", "")
            if desire and desire != '-':
                items = [d.strip() for d in desire.split(',')]
                desires.update(items)
        
        return [{"desire": name, "frequency": count} 
                for name, count in desires.most_common(10)]
    
    # ============================================
    # Import from CSV (خروجی Gem)
    # ============================================
    
    def parse_csv_from_gem(self, csv_text: str) -> List[Dict]:
        """
        پارس CSV از خروجی Gem
        فرمت: Date|Mood|Energy|Top Win|Main Obstacle|Techniques Suggested|Reflection|Techniques Used|Bad Habits|Good Habits|Desires|"Daily Report"
        """
        lines = csv_text.strip().split('\n')
        data = []
        
        for line in lines:
            if not line.strip():
                continue
            
            # Handle quoted Daily Report
            # الگو: ... |"Daily Report content"
            match = re.match(
                r'^([^|]+)\|([^|]*)\|([^|]*)\|([^|]*)\|([^|]*)\|([^|]*)\|([^|]*)\|([^|]*)\|([^|]*)\|([^|]*)\|([^|]*)\|"?(.+?)"?$',
                line
            )
            
            if match:
                data.append({
                    "date": match.group(1).strip(),
                    "mood": self._safe_int(match.group(2).strip()),
                    "energy": self._safe_int(match.group(3).strip()),
                    "top_win": match.group(4).strip(),
                    "main_obstacle": match.group(5).strip(),
                    "techniques_suggested": match.group(6).strip(),
                    "reflection": match.group(7).strip(),
                    "techniques_used": match.group(8).strip(),
                    "bad_habits": match.group(9).strip(),
                    "good_habits": match.group(10).strip(),
                    "desires": match.group(11).strip(),
                    "daily_report": match.group(12).strip()
                })
            else:
                # فرمت ساده‌تر با | جداکننده
                parts = line.split('|')
                if len(parts) >= 7:
                    data.append({
                        "date": parts[0].strip() if len(parts) > 0 else "",
                        "mood": self._safe_int(parts[1].strip() if len(parts) > 1 else "5"),
                        "energy": self._safe_int(parts[2].strip() if len(parts) > 2 else "5"),
                        "top_win": parts[3].strip() if len(parts) > 3 else "",
                        "main_obstacle": parts[4].strip() if len(parts) > 4 else "",
                        "techniques_suggested": parts[5].strip() if len(parts) > 5 else "",
                        "reflection": parts[6].strip() if len(parts) > 6 else "",
                        "techniques_used": parts[7].strip() if len(parts) > 7 else "",
                        "bad_habits": parts[8].strip() if len(parts) > 8 else "",
                        "good_habits": parts[9].strip() if len(parts) > 9 else "",
                        "desires": parts[10].strip() if len(parts) > 10 else "",
                        "daily_report": parts[11].strip().strip('"') if len(parts) > 11 else ""
                    })
        
        return data
    
    def bulk_import(self, sheet_id: str, sheet_name: str, data: List[Dict]) -> Dict:
        """Import چندین ردیف به Sheet"""
        result = {"success": 0, "failed": 0, "errors": []}
        
        for item in data:
            if self.append_daily_log(sheet_id, sheet_name, item):
                result["success"] += 1
            else:
                result["failed"] += 1
                result["errors"].append(f"خطا در ذخیره: {item.get('date', 'unknown')}")
        
        return result


# ============================================
# Import re for CSV parsing
# ============================================
import re


def create_sheets_api(credentials_path: str) -> Optional[SheetsAPI]:
    """Factory function برای ایجاد SheetsAPI"""
    try:
        api = SheetsAPI(credentials_path)
        if api.is_connected():
            return api
        return None
    except Exception as e:
        logger.error(f"خطا در ایجاد SheetsAPI: {e}")
        return None
