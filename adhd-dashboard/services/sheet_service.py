"""
📊 Smart Google Sheet Service v3.1
ساخت و مدیریت خودکار Google Sheets
بر اساس ساختار setup_existing.py که تست شده و کار می‌کنه

Features:
- Auto-create spreadsheet با تمام Tab ها
- Batch Update برای سرعت بیشتر
- Conditional Formatting
- Data Validation
- Formulas
"""

import logging
from datetime import datetime
from typing import Optional, Dict, Callable
from pathlib import Path

try:
    import gspread
    from google.oauth2.service_account import Credentials
    GSPREAD_AVAILABLE = True
except ImportError:
    GSPREAD_AVAILABLE = False

logger = logging.getLogger(__name__)

# ============================================
# Constants
# ============================================

SCOPES = [
    'https://www.googleapis.com/auth/spreadsheets',
    'https://www.googleapis.com/auth/drive'
]

# رنگ‌ها (فرمت Google Sheets API)
COLORS = {
    'RED': {'red': 0.917, 'green': 0.262, 'blue': 0.207},
    'YELLOW': {'red': 0.984, 'green': 0.737, 'blue': 0.015},
    'GREEN': {'red': 0.203, 'green': 0.658, 'blue': 0.325},
    'ORANGE': {'red': 1.0, 'green': 0.647, 'blue': 0.0},
    'BLUE': {'red': 0.29, 'green': 0.564, 'blue': 0.886},
    'PURPLE': {'red': 0.612, 'green': 0.153, 'blue': 0.69},
    'WHITE': {'red': 1, 'green': 1, 'blue': 1},
    'LIGHT_GREEN': {'red': 0.8, 'green': 1, 'blue': 0.8},
    'LIGHT_YELLOW': {'red': 1, 'green': 1, 'blue': 0.8},
    'DARK_RED': {'red': 0.8, 'green': 0, 'blue': 0},
    'LIGHT_ORANGE': {'red': 1, 'green': 0.647, 'blue': 0, 'alpha': 0.3},
    'LIGHT_GREEN_ALPHA': {'red': 0.2, 'green': 0.66, 'blue': 0.33, 'alpha': 0.3},
    'LIGHT_RED': {'red': 1, 'green': 0.8, 'blue': 0.8},
}

# دسته‌بندی‌های Task
TASK_CATEGORIES = {
    'general': [
        'تماس‌ها', 'لیست خرید', 'کارهای خرد شخصی', 
        'کارهای شخصی', 'کارهای هنگامه'
    ],
    'workflow': [
        'پیگیری‌ها', 'جلسه/بازدید', 'پیش‌فاکتور', 
        'تایید پرداخت', 'دریافت تجهیزات', 'انجام پروژه', 
        'تحویل پروژه', 'رضایت‌نامه', 'گارانتی'
    ],
    'other': [
        'آموزش', 'پروژه عقب‌مانده', 'تعمیرات', 'ایده درآمدزایی'
    ]
}

# همه دسته‌بندی‌ها
ALL_CATEGORIES = (
    TASK_CATEGORIES['general'] + 
    TASK_CATEGORIES['workflow'] + 
    TASK_CATEGORIES['other']
)


# ============================================
# Batch Update Helpers
# ============================================

def batch_set_validation(sheet_id: int, requests: list, start_row: int, 
                         end_row: int, col_index: int, values: list):
    """اضافه کردن درخواست Validation به لیست"""
    requests.append({
        "setDataValidation": {
            "range": {
                "sheetId": sheet_id,
                "startRowIndex": start_row,
                "endRowIndex": end_row,
                "startColumnIndex": col_index,
                "endColumnIndex": col_index + 1
            },
            "rule": {
                "condition": {
                    "type": "ONE_OF_LIST",
                    "values": [{"userEnteredValue": v} for v in values]
                },
                "showCustomUi": True,
                "strict": False
            }
        }
    })


def batch_add_conditional_format(sheet_id: int, requests: list, col_index: int,
                                  condition_type: str, condition_values: list, 
                                  bg_color: dict):
    """اضافه کردن درخواست فرمت شرطی"""
    requests.append({
        "addConditionalFormatRule": {
            "rule": {
                "ranges": [{
                    "sheetId": sheet_id,
                    "startRowIndex": 1,
                    "startColumnIndex": col_index,
                    "endColumnIndex": col_index + 1
                }],
                "booleanRule": {
                    "condition": {
                        "type": condition_type,
                        "values": [{"userEnteredValue": str(v)} for v in condition_values]
                    },
                    "format": {"backgroundColor": bg_color}
                }
            },
            "index": 0
        }
    })


def batch_add_not_empty_format(sheet_id: int, requests: list, col_index: int, 
                                bg_color: dict):
    """فرمت برای سلول‌های غیرخالی"""
    requests.append({
        "addConditionalFormatRule": {
            "rule": {
                "ranges": [{
                    "sheetId": sheet_id,
                    "startRowIndex": 1,
                    "startColumnIndex": col_index,
                    "endColumnIndex": col_index + 1
                }],
                "booleanRule": {
                    "condition": {"type": "NOT_BLANK"},
                    "format": {"backgroundColor": bg_color}
                }
            },
            "index": 0
        }
    })


def batch_header_style(sheet_id: int, requests: list, bg_color: dict):
    """استایل Header"""
    requests.append({
        "repeatCell": {
            "range": {"sheetId": sheet_id, "startRowIndex": 0, "endRowIndex": 1},
            "cell": {
                "userEnteredFormat": {
                    "backgroundColor": bg_color,
                    "textFormat": {
                        "foregroundColor": COLORS['WHITE'],
                        "bold": True
                    },
                    "horizontalAlignment": "CENTER"
                }
            },
            "fields": "userEnteredFormat(backgroundColor,textFormat,horizontalAlignment)"
        }
    })


def batch_freeze(sheet_id: int, requests: list, rows: int = 1, cols: int = 1):
    """Freeze ردیف و ستون"""
    requests.append({
        "updateSheetProperties": {
            "properties": {
                "sheetId": sheet_id,
                "gridProperties": {
                    "frozenRowCount": rows,
                    "frozenColumnCount": cols
                }
            },
            "fields": "gridProperties.frozenRowCount,gridProperties.frozenColumnCount"
        }
    })


# ============================================
# Sheet Service Class
# ============================================

class SheetService:
    """سرویس مدیریت Google Sheets"""
    
    def __init__(self, credentials_path: str = './credentials.json'):
        self.credentials_path = Path(credentials_path)
        self.client = None
        self.spreadsheet = None
        self._connected = False
    
    def connect(self) -> bool:
        """اتصال به Google API"""
        if not GSPREAD_AVAILABLE:
            logger.error("gspread not installed")
            return False
        
        if not self.credentials_path.exists():
            logger.error(f"Credentials not found: {self.credentials_path}")
            return False
        
        try:
            creds = Credentials.from_service_account_file(
                str(self.credentials_path),
                scopes=SCOPES
            )
            self.client = gspread.authorize(creds)
            self._connected = True
            logger.info("Connected to Google Sheets API")
            return True
        except Exception as e:
            logger.error(f"Connection failed: {e}")
            return False
    
    @property
    def is_connected(self) -> bool:
        return self._connected and self.client is not None
    
    def create_spreadsheet(self, title: str = None):
        """ساخت Spreadsheet جدید"""
        if not self.is_connected:
            if not self.connect():
                return None
        
        if not title:
            today = datetime.now().strftime("%Y-%m-%d")
            title = f"🧠 ADHD Dashboard - {today}"
        
        try:
            self.spreadsheet = self.client.create(title)
            return self.spreadsheet
        except Exception as e:
            logger.error(f"Error creating spreadsheet: {e}")
            return None
    
    def open_by_id(self, spreadsheet_id: str) -> bool:
        """باز کردن Spreadsheet با ID"""
        if not self.is_connected:
            if not self.connect():
                return False
        
        try:
            self.spreadsheet = self.client.open_by_key(spreadsheet_id)
            return True
        except Exception as e:
            logger.error(f"Could not open spreadsheet: {e}")
            return False
    
    # ============================================
    # Setup Daily Log Tab
    # ============================================
    
    def setup_daily_log(self, on_progress: Callable = None):
        """تنظیم تب Daily Log"""
        if not self.spreadsheet:
            return False
        
        if on_progress:
            on_progress("تنظیم Daily Log...", 20)
        
        try:
            try:
                sheet = self.spreadsheet.worksheet("Daily Log")
            except:
                sheet = self.spreadsheet.add_worksheet("Daily Log", 1000, 20)
            
            sheet.clear()
            
            # Headers
            headers = [
                'تاریخ', 'Mood', 'Energy', 'Top Win', 'Main Obstacle',
                'Techniques Suggested', 'Reflection', 'Techniques Used',
                'Bad Habits', 'Good Habits', 'Desires', 'Daily Report'
            ]
            sheet.update(range_name='A1:L1', values=[headers])
            
            # Meta Headers
            meta_headers = ['Avg Mood', 'Avg Energy', 'Techs Used', 'Bad Count', 'Good Count']
            sheet.update(range_name='M1:Q1', values=[meta_headers])
            
            # Formulas
            formulas = [['=AVERAGE(B2:B)', '=AVERAGE(C2:C)', '=COUNTA(H2:H)', 
                         '=COUNTA(I2:I)', '=COUNTA(J2:J)']]
            sheet.update(range_name='M2:Q2', values=formulas, value_input_option='USER_ENTERED')
            
            # Batch Requests
            requests = []
            sid = sheet.id
            
            batch_header_style(sid, requests, COLORS['BLUE'])
            batch_freeze(sid, requests, rows=1, cols=1)
            
            # Conditional Formatting
            for col in [1, 2]:
                batch_add_conditional_format(sid, requests, col, "NUMBER_BETWEEN", ["1", "3"], COLORS['RED'])
                batch_add_conditional_format(sid, requests, col, "NUMBER_BETWEEN", ["4", "6"], COLORS['YELLOW'])
                batch_add_conditional_format(sid, requests, col, "NUMBER_BETWEEN", ["7", "10"], COLORS['GREEN'])
            
            batch_add_not_empty_format(sid, requests, 8, COLORS['LIGHT_ORANGE'])
            batch_add_not_empty_format(sid, requests, 9, COLORS['LIGHT_GREEN_ALPHA'])
            
            self.spreadsheet.batch_update({'requests': requests})
            
            try:
                sheet.set_basic_filter('A1:L1000')
            except:
                pass
            
            return True
            
        except Exception as e:
            logger.error(f"Error setting up Daily Log: {e}")
            return False
    
    # ============================================
    # Setup Brain Dump Archive Tab
    # ============================================
    
    def setup_brain_dump(self, on_progress: Callable = None):
        """تنظیم تب Brain Dump Archive"""
        if not self.spreadsheet:
            return False
        
        if on_progress:
            on_progress("تنظیم Brain Dump Archive...", 40)
        
        try:
            try:
                sheet = self.spreadsheet.worksheet("Brain Dump Archive")
            except:
                sheet = self.spreadsheet.add_worksheet("Brain Dump Archive", 1000, 15)
            
            sheet.clear()
            
            headers = [
                'تاریخ', 'نام', 'نوع', 'وضعیت', 'زمینه', 'انرژی',
                'اهمیت', 'فوریت', 'زمان تخمینی', 'ددلاین', 'Quick Win', 
                'دسته‌بندی', 'یادداشت'
            ]
            sheet.update(range_name='A1:M1', values=[headers])
            
            requests = []
            sid = sheet.id
            
            batch_header_style(sid, requests, COLORS['BLUE'])
            batch_freeze(sid, requests, rows=1, cols=2)
            
            # Validations
            batch_set_validation(sid, requests, 1, 1000, 2, ['Task', 'Project', 'Resource', 'Idea'])
            batch_set_validation(sid, requests, 1, 1000, 3, 
                ['Inbox', 'Next Action', 'In Progress', 'Waiting', 'Done', 'Someday/Maybe'])
            batch_set_validation(sid, requests, 1, 1000, 4,
                ['📞تماس', '💬پیام', '🛒خرید', '💻سیستم', '🚗بیرون', '🏢دفتر', '🏠خانه'])
            batch_set_validation(sid, requests, 1, 1000, 5,
                ['🔥High Focus', '⚡Medium', '🪶Low Focus'])
            batch_set_validation(sid, requests, 1, 1000, 6, ['🔴High', '🟡Medium', '🟢Low'])
            batch_set_validation(sid, requests, 1, 1000, 7, ['🚨Urgent', '⏰Soon', '📅Normal', '🐢Low'])
            batch_set_validation(sid, requests, 1, 1000, 8, ['⚡<5min', '🕐15min', '🕑30min', '🕓1h', '🕕2h+'])
            batch_set_validation(sid, requests, 1, 1000, 10, ['Yes', 'No'])
            batch_set_validation(sid, requests, 1, 1000, 11, ALL_CATEGORIES)
            
            # Conditional Formatting
            batch_add_conditional_format(sid, requests, 6, "TEXT_EQ", ["🔴High"], COLORS['RED'])
            batch_add_conditional_format(sid, requests, 6, "TEXT_EQ", ["🟡Medium"], COLORS['YELLOW'])
            batch_add_conditional_format(sid, requests, 6, "TEXT_EQ", ["🟢Low"], COLORS['GREEN'])
            batch_add_conditional_format(sid, requests, 7, "TEXT_EQ", ["🚨Urgent"], COLORS['DARK_RED'])
            batch_add_conditional_format(sid, requests, 7, "TEXT_EQ", ["⏰Soon"], COLORS['ORANGE'])
            batch_add_conditional_format(sid, requests, 10, "TEXT_EQ", ["Yes"], COLORS['LIGHT_GREEN'])
            
            self.spreadsheet.batch_update({'requests': requests})
            return True
            
        except Exception as e:
            logger.error(f"Error setting up Brain Dump: {e}")
            return False
    
    # ============================================
    # Setup Habits Tab
    # ============================================
    
    def setup_habits(self, on_progress: Callable = None):
        """تنظیم تب Habits"""
        if not self.spreadsheet:
            return False
        
        if on_progress:
            on_progress("تنظیم Habits...", 60)
        
        try:
            try:
                sheet = self.spreadsheet.worksheet("Habits")
            except:
                sheet = self.spreadsheet.add_worksheet("Habits", 100, 15)
            
            sheet.clear()
            
            headers = [
                'نام عادت', 'نوع', 'دسته‌بندی', 'وضعیت', 'تکرار',
                'Counter', 'Streak', 'Best Streak', 'آخرین ثبت',
                'Trigger', 'جایگزین', 'چرا مهمه؟'
            ]
            sheet.update(range_name='A1:L1', values=[headers])
            
            sample_data = [
                ['ورزش صبحگاهی', '🟢خوب', 'سلامت/ورزش', 'Active', 'روزانه',
                 '0', '0', '0', '', 'بعد بیدار شدن', '-', 'انرژی بیشتر'],
                ['چک کردن گوشی', '🔴بد', 'دیجیتال', 'Active', 'روزانه',
                 '0', '0', '0', '', 'استرس', 'یادداشت', 'هدر رفتن وقت']
            ]
            sheet.update(range_name='A2:L3', values=sample_data)
            
            requests = []
            sid = sheet.id
            
            batch_header_style(sid, requests, COLORS['GREEN'])
            batch_freeze(sid, requests, rows=1, cols=1)
            
            batch_set_validation(sid, requests, 1, 100, 1, ['🟢خوب', '🔴بد'])
            batch_set_validation(sid, requests, 1, 100, 2,
                ['سلامت/ورزش', 'ذهنی/یادگیری', 'کاری', 'خواب', 'تغذیه', 'دیجیتال', 'روحی'])
            batch_set_validation(sid, requests, 1, 100, 3, ['Active', 'Paused', 'Achieved', 'Abandoned'])
            batch_set_validation(sid, requests, 1, 100, 4, ['روزانه', '3x هفته', 'هفتگی', 'ماهانه'])
            
            batch_add_conditional_format(sid, requests, 1, "TEXT_CONTAINS", ["🟢"], COLORS['LIGHT_GREEN'])
            batch_add_conditional_format(sid, requests, 1, "TEXT_CONTAINS", ["🔴"], COLORS['LIGHT_RED'])
            
            self.spreadsheet.batch_update({'requests': requests})
            return True
            
        except Exception as e:
            logger.error(f"Error setting up Habits: {e}")
            return False
    
    # ============================================
    # Setup Analytics Tab
    # ============================================
    
    def setup_analytics(self, on_progress: Callable = None):
        """تنظیم تب Analytics"""
        if not self.spreadsheet:
            return False
        
        if on_progress:
            on_progress("تنظیم Analytics...", 80)
        
        try:
            try:
                sheet = self.spreadsheet.worksheet("Analytics")
            except:
                sheet = self.spreadsheet.add_worksheet("Analytics", 100, 10)
            
            sheet.clear()
            
            content = [
                ['📊 Analytics Dashboard'],
                [''],
                ['متریک', 'مقدار'],
                ['میانگین Mood', "='Daily Log'!M2"],
                ['میانگین Energy', "='Daily Log'!N2"],
                ['تکنیک‌ها', "='Daily Log'!O2"],
                [''],
                ['تسک‌های Inbox', '=COUNTIF(\'Brain Dump Archive\'!D:D,"Inbox")'],
                ['تسک‌های Next', '=COUNTIF(\'Brain Dump Archive\'!D:D,"Next Action")'],
                ['تسک‌های Done', '=COUNTIF(\'Brain Dump Archive\'!D:D,"Done")'],
                [''],
                ['عادت خوب', '=COUNTIF(Habits!B:B,"🟢خوب")'],
                ['عادت بد', '=COUNTIF(Habits!B:B,"🔴بد")'],
            ]
            
            sheet.update(range_name='A1:B13', values=content, value_input_option='USER_ENTERED')
            sheet.format('A1', {'textFormat': {'fontSize': 16, 'bold': True}})
            sheet.format('A3:B3', {
                'backgroundColor': COLORS['PURPLE'],
                'textFormat': {'foregroundColor': COLORS['WHITE'], 'bold': True}
            })
            
            return True
            
        except Exception as e:
            logger.error(f"Error setting up Analytics: {e}")
            return False
    
    # ============================================
    # Main Methods
    # ============================================
    
    def create_and_setup_sheet(self, title: str = None,
                                on_progress: Callable = None) -> Dict:
        """ساخت Spreadsheet کامل"""
        
        def progress(msg: str, pct: int):
            if on_progress:
                on_progress(msg, pct)
            logger.info(f"[{pct}%] {msg}")
        
        try:
            progress("اتصال...", 5)
            if not self.is_connected and not self.connect():
                raise Exception("Cannot connect to Google API")
            
            progress("ساخت Spreadsheet...", 10)
            if not self.create_spreadsheet(title):
                raise Exception("Cannot create spreadsheet")
            
            self.setup_daily_log(on_progress)
            self.setup_brain_dump(on_progress)
            self.setup_habits(on_progress)
            self.setup_analytics(on_progress)
            
            progress("پاکسازی...", 90)
            try:
                self.spreadsheet.del_worksheet(self.spreadsheet.worksheet("Sheet1"))
            except:
                pass
            
            progress("دسترسی...", 95)
            self.spreadsheet.share(None, perm_type='anyone', role='reader')
            
            progress("✅ تمام!", 100)
            
            return {
                'success': True,
                'spreadsheet_id': self.spreadsheet.id,
                'spreadsheet_url': self.spreadsheet.url,
                'title': self.spreadsheet.title
            }
            
        except Exception as e:
            logger.error(f"Error: {e}")
            return {'success': False, 'error': str(e)}
    
    def setup_existing_sheet(self, spreadsheet_id: str,
                              on_progress: Callable = None) -> Dict:
        """بروزرسانی Sheet موجود"""
        
        def progress(msg: str, pct: int):
            if on_progress:
                on_progress(msg, pct)
        
        try:
            progress("اتصال...", 5)
            if not self.open_by_id(spreadsheet_id):
                raise Exception("Cannot open spreadsheet")
            
            progress(f"متصل: {self.spreadsheet.title}", 10)
            
            self.setup_daily_log(on_progress)
            self.setup_brain_dump(on_progress)
            self.setup_habits(on_progress)
            self.setup_analytics(on_progress)
            
            progress("✅ تمام!", 100)
            
            return {
                'success': True,
                'spreadsheet_id': self.spreadsheet.id,
                'spreadsheet_url': self.spreadsheet.url
            }
            
        except Exception as e:
            return {'success': False, 'error': str(e)}


# ============================================
# Factory
# ============================================

def create_sheet_service(credentials_path: str = './credentials.json'):
    """Factory function"""
    if not GSPREAD_AVAILABLE:
        return None
    return SheetService(credentials_path)
