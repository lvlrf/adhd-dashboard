#!/usr/bin/env python3
"""
Setup Existing Sheet - v3.1
بروزرسانی Google Sheet موجود با ساختار کامل

استفاده:
    python setup_existing.py

پیش‌نیاز:
    - فایل credentials.json
    - SHEET_ID در .env یا اینجا
"""

import sys
import os
from pathlib import Path

try:
    import gspread
    from google.oauth2.service_account import Credentials
except ImportError:
    print("pip install gspread google-auth --break-system-packages")
    sys.exit(1)

# تنظیمات
SHEET_ID = ''  # از .env میخونه
CREDENTIALS_FILE = './credentials.json'
SCOPES = ['https://www.googleapis.com/auth/spreadsheets', 'https://www.googleapis.com/auth/drive']

# بارگذاری .env
try:
    from dotenv import load_dotenv
    load_dotenv()
    SHEET_ID = os.getenv('DAILY_LOG_SHEET_ID', '')
except:
    pass

if not SHEET_ID:
    print("SHEET_ID not set! Set DAILY_LOG_SHEET_ID in .env")
    sys.exit(1)

# رنگ‌ها
COLORS = {
    'RED': {'red': 0.917, 'green': 0.262, 'blue': 0.207},
    'YELLOW': {'red': 0.984, 'green': 0.737, 'blue': 0.015},
    'GREEN': {'red': 0.203, 'green': 0.658, 'blue': 0.325},
    'ORANGE': {'red': 1.0, 'green': 0.647, 'blue': 0.0},
    'BLUE': {'red': 0.29, 'green': 0.564, 'blue': 0.886},
    'WHITE': {'red': 1, 'green': 1, 'blue': 1},
}

def get_client():
    creds = Credentials.from_service_account_file(CREDENTIALS_FILE, scopes=SCOPES)
    return gspread.authorize(creds)

def batch_set_validation(sid, reqs, sr, er, col, vals):
    reqs.append({"setDataValidation": {"range": {"sheetId": sid, "startRowIndex": sr, "endRowIndex": er, "startColumnIndex": col, "endColumnIndex": col+1}, "rule": {"condition": {"type": "ONE_OF_LIST", "values": [{"userEnteredValue": v} for v in vals]}, "showCustomUi": True, "strict": False}}})

def batch_cond_format(sid, reqs, col, ctype, cvals, bg):
    reqs.append({"addConditionalFormatRule": {"rule": {"ranges": [{"sheetId": sid, "startRowIndex": 1, "startColumnIndex": col, "endColumnIndex": col+1}], "booleanRule": {"condition": {"type": ctype, "values": [{"userEnteredValue": str(v)} for v in cvals]}, "format": {"backgroundColor": bg}}}, "index": 0}})

def batch_not_empty(sid, reqs, col, bg):
    reqs.append({"addConditionalFormatRule": {"rule": {"ranges": [{"sheetId": sid, "startRowIndex": 1, "startColumnIndex": col, "endColumnIndex": col+1}], "booleanRule": {"condition": {"type": "NOT_BLANK"}, "format": {"backgroundColor": bg}}}, "index": 0}})

def setup_daily_log(sp):
    print("Setting up Daily Log...")
    try: sh = sp.worksheet("Daily Log")
    except: sh = sp.add_worksheet("Daily Log", 1000, 20)
    sh.clear()
    sh.update('A1:L1', [['Date', 'Mood', 'Energy', 'Top Win', 'Main Obstacle', 'Techniques Suggested', 'Reflection', 'Techniques Used', 'Bad Habits', 'Good Habits', 'Desires', 'Daily Report']])
    sh.update('M1:Q1', [['Avg Mood', 'Avg Energy', 'Techs', 'Bad', 'Good']])
    sh.update('M2:Q2', [['=AVERAGE(B2:B)', '=AVERAGE(C2:C)', '=COUNTA(H2:H)', '=COUNTA(I2:I)', '=COUNTA(J2:J)']], value_input_option='USER_ENTERED')
    reqs = []
    sid = sh.id
    reqs.append({"repeatCell": {"range": {"sheetId": sid, "startRowIndex": 0, "endRowIndex": 1}, "cell": {"userEnteredFormat": {"backgroundColor": COLORS['BLUE'], "textFormat": {"foregroundColor": COLORS['WHITE'], "bold": True}, "horizontalAlignment": "CENTER"}}, "fields": "userEnteredFormat"}})
    reqs.append({"updateSheetProperties": {"properties": {"sheetId": sid, "gridProperties": {"frozenRowCount": 1, "frozenColumnCount": 1}}, "fields": "gridProperties.frozenRowCount,gridProperties.frozenColumnCount"}})
    for c in [1,2]:
        batch_cond_format(sid, reqs, c, "NUMBER_BETWEEN", ["1","3"], COLORS['RED'])
        batch_cond_format(sid, reqs, c, "NUMBER_BETWEEN", ["4","6"], COLORS['YELLOW'])
        batch_cond_format(sid, reqs, c, "NUMBER_BETWEEN", ["7","10"], COLORS['GREEN'])
    batch_not_empty(sid, reqs, 8, {'red':1,'green':0.65,'blue':0,'alpha':0.3})
    batch_not_empty(sid, reqs, 9, {'red':0.2,'green':0.66,'blue':0.33,'alpha':0.3})
    sp.batch_update({'requests': reqs})
    try: sh.set_basic_filter('A1:L1000')
    except: pass
    print("Daily Log OK")

def setup_brain_dump(sp):
    print("Setting up Brain Dump Archive...")
    try: sh = sp.worksheet("Brain Dump Archive")
    except: sh = sp.add_worksheet("Brain Dump Archive", 1000, 15)
    sh.clear()
    sh.update('A1:M1', [['Date', 'Name', 'Type', 'Status', 'Context', 'Energy', 'Importance', 'Urgency', 'Time', 'Deadline', 'QuickWin', 'Category', 'Notes']])
    reqs = []
    sid = sh.id
    reqs.append({"repeatCell": {"range": {"sheetId": sid, "startRowIndex": 0, "endRowIndex": 1}, "cell": {"userEnteredFormat": {"backgroundColor": COLORS['BLUE'], "textFormat": {"foregroundColor": COLORS['WHITE'], "bold": True}, "horizontalAlignment": "CENTER"}}, "fields": "userEnteredFormat"}})
    reqs.append({"updateSheetProperties": {"properties": {"sheetId": sid, "gridProperties": {"frozenRowCount": 1, "frozenColumnCount": 2}}, "fields": "gridProperties.frozenRowCount,gridProperties.frozenColumnCount"}})
    batch_set_validation(sid, reqs, 1, 1000, 2, ['Task','Project','Resource','Idea'])
    batch_set_validation(sid, reqs, 1, 1000, 3, ['Inbox','Next Action','In Progress','Waiting','Done','Someday/Maybe'])
    batch_set_validation(sid, reqs, 1, 1000, 4, ['Call','Message','Shop','System','Out','Office','Home'])
    batch_set_validation(sid, reqs, 1, 1000, 5, ['High Focus','Medium','Low Focus'])
    batch_set_validation(sid, reqs, 1, 1000, 6, ['High','Medium','Low'])
    batch_set_validation(sid, reqs, 1, 1000, 7, ['Urgent','Soon','Normal','Low'])
    batch_set_validation(sid, reqs, 1, 1000, 8, ['<5min','15min','30min','1h','2h+'])
    batch_set_validation(sid, reqs, 1, 1000, 10, ['Yes','No'])
    cats = ['Calls','Shopping','Personal Tasks','Follow-ups','Meeting','Pre-Invoice','Payment Confirm','Equipment','Project Work','Delivery','Satisfaction','Warranty','Training','Backlog','Repairs','Ideas']
    batch_set_validation(sid, reqs, 1, 1000, 11, cats)
    batch_cond_format(sid, reqs, 6, "TEXT_EQ", ["High"], COLORS['RED'])
    batch_cond_format(sid, reqs, 6, "TEXT_EQ", ["Medium"], COLORS['YELLOW'])
    batch_cond_format(sid, reqs, 6, "TEXT_EQ", ["Low"], COLORS['GREEN'])
    batch_cond_format(sid, reqs, 7, "TEXT_EQ", ["Urgent"], {'red':0.8,'green':0,'blue':0})
    batch_cond_format(sid, reqs, 7, "TEXT_EQ", ["Soon"], COLORS['ORANGE'])
    batch_cond_format(sid, reqs, 10, "TEXT_EQ", ["Yes"], {'red':0.8,'green':1,'blue':0.8})
    sp.batch_update({'requests': reqs})
    print("Brain Dump Archive OK")

def setup_habits(sp):
    print("Setting up Habits...")
    try: sh = sp.worksheet("Habits")
    except: sh = sp.add_worksheet("Habits", 100, 15)
    sh.clear()
    sh.update('A1:L1', [['Habit Name','Type','Category','Status','Frequency','Counter','Streak','Best Streak','Last Log','Trigger','Replacement','Why']])
    reqs = []
    sid = sh.id
    reqs.append({"repeatCell": {"range": {"sheetId": sid, "startRowIndex": 0, "endRowIndex": 1}, "cell": {"userEnteredFormat": {"backgroundColor": COLORS['GREEN'], "textFormat": {"foregroundColor": COLORS['WHITE'], "bold": True}, "horizontalAlignment": "CENTER"}}, "fields": "userEnteredFormat"}})
    reqs.append({"updateSheetProperties": {"properties": {"sheetId": sid, "gridProperties": {"frozenRowCount": 1, "frozenColumnCount": 1}}, "fields": "gridProperties.frozenRowCount,gridProperties.frozenColumnCount"}})
    batch_set_validation(sid, reqs, 1, 100, 1, ['Good','Bad'])
    batch_set_validation(sid, reqs, 1, 100, 2, ['Health','Mental','Work','Sleep','Food','Digital','Spiritual'])
    batch_set_validation(sid, reqs, 1, 100, 3, ['Active','Paused','Achieved','Abandoned'])
    batch_set_validation(sid, reqs, 1, 100, 4, ['Daily','3x Week','Weekly','Monthly'])
    sp.batch_update({'requests': reqs})
    print("Habits OK")

def setup_analytics(sp):
    print("Setting up Analytics...")
    try: sh = sp.worksheet("Analytics")
    except: sh = sp.add_worksheet("Analytics", 100, 10)
    sh.clear()
    sh.update('A1', [['Analytics Dashboard']])
    sh.format('A1', {'textFormat': {'fontSize': 14, 'bold': True}})
    print("Analytics OK")

def cleanup(sp):
    allowed = ["Daily Log", "Brain Dump Archive", "Habits", "Analytics"]
    for ws in sp.worksheets():
        if ws.title not in allowed:
            try: sp.del_worksheet(ws)
            except: pass

def main():
    print(f"\nSetup Existing Sheet: {SHEET_ID[:10]}...\n")
    client = get_client()
    try:
        sp = client.open_by_key(SHEET_ID)
        print(f"Connected: {sp.title}")
    except Exception as e:
        print(f"Error: {e}")
        return
    setup_daily_log(sp)
    setup_brain_dump(sp)
    setup_habits(sp)
    setup_analytics(sp)
    cleanup(sp)
    print(f"\nDone! URL: {sp.url}")

if __name__ == '__main__':
    main()
