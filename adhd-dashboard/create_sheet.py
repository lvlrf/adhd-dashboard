#!/usr/bin/env python3
"""
📊 ADHD Dashboard - Google Sheet Creator v3.0
ساخت خودکار Google Sheet با ساختار کامل

استفاده:
    python create_sheet.py

پیش‌نیاز:
    1. فایل credentials.json کنار این فایل باشه
    2. pip install -r requirements.txt --break-system-packages
"""

import os
import sys
from pathlib import Path

# اضافه کردن مسیر پروژه
sys.path.insert(0, str(Path(__file__).parent))

try:
    from services.sheet_service import create_sheet_service
except ImportError:
    print("❌ خطا در import سرویس‌ها")
    print("مطمئن شو که از داخل پوشه پروژه اجرا می‌کنی")
    sys.exit(1)


# ============================================
# رنگ‌ها برای Terminal
# ============================================

class Colors:
    GREEN = '\033[92m'
    YELLOW = '\033[93m'
    RED = '\033[91m'
    BLUE = '\033[94m'
    CYAN = '\033[96m'
    RESET = '\033[0m'
    BOLD = '\033[1m'


def print_progress(message: str, percent: int):
    """نمایش progress"""
    progress = int(percent / 5)
    bar = '█' * progress + '░' * (20 - progress)
    print(f"{Colors.CYAN}[{bar}] {percent:3d}%{Colors.RESET} {message}")


def print_success(message: str):
    print(f"{Colors.GREEN}✅ {message}{Colors.RESET}")


def print_error(message: str):
    print(f"{Colors.RED}❌ {message}{Colors.RESET}")


def print_info(message: str):
    print(f"{Colors.BLUE}ℹ️  {message}{Colors.RESET}")


# ============================================
# Main
# ============================================

def main():
    print()
    print(f"{Colors.BOLD}{'='*50}{Colors.RESET}")
    print(f"{Colors.BOLD}📊 ADHD Dashboard - Sheet Creator v3.0{Colors.RESET}")
    print(f"{Colors.BOLD}{'='*50}{Colors.RESET}")
    print()
    
    # بررسی credentials
    creds_path = Path('./credentials.json')
    if not creds_path.exists():
        print_error("فایل credentials.json پیدا نشد!")
        print_info("این فایل رو از Google Cloud Console دانلود کن:")
        print("   1. برو به https://console.cloud.google.com")
        print("   2. APIs & Services → Credentials")
        print("   3. Service Account → Keys → Add Key → JSON")
        print("   4. فایل رو بذار کنار این اسکریپت")
        sys.exit(1)
    
    print_info("credentials.json پیدا شد")
    
    # ساخت سرویس
    service = create_sheet_service('./credentials.json')
    
    if not service:
        print_error("خطا در ایجاد Sheet Service")
        sys.exit(1)
    
    print_info("اتصال به Google API...")
    
    if not service.connect():
        print_error("خطا در اتصال به Google API")
        print_info("مطمئن شو که:")
        print("   1. Google Sheets API فعاله")
        print("   2. Google Drive API فعاله")
        sys.exit(1)
    
    print_success("اتصال برقرار شد")
    print()
    
    # ساخت Sheet
    try:
        result = service.create_and_setup_sheet(
            on_progress=print_progress
        )
        
        if result['success']:
            print()
            print(f"{Colors.BOLD}{'='*50}{Colors.RESET}")
            print(f"{Colors.GREEN}{Colors.BOLD}✅ Sheet با موفقیت ساخته شد!{Colors.RESET}")
            print(f"{Colors.BOLD}{'='*50}{Colors.RESET}")
            print()
            print(f"📋 {Colors.BOLD}Sheet ID:{Colors.RESET}")
            print(f"   {Colors.CYAN}{result['spreadsheet_id']}{Colors.RESET}")
            print()
            print(f"🔗 {Colors.BOLD}لینک Sheet:{Colors.RESET}")
            print(f"   {Colors.CYAN}{result['spreadsheet_url']}{Colors.RESET}")
            print()
            print(f"📝 {Colors.BOLD}Tab ها:{Colors.RESET}")
            print(f"   • Daily Log (12 ستون + Formulas + Conditional Formatting)")
            print(f"   • Tasks Archive (10 ستون + Data Validation)")
            print(f"   • Habits (11 ستون + Dropdowns)")
            print(f"   • Projects (8 ستون)")
            print(f"   • Analytics (خلاصه آمار با Formulas)")
            print()
            print(f"{Colors.YELLOW}⚠️  این Sheet ID رو در .env ذخیره کن:{Colors.RESET}")
            print(f"   DAILY_LOG_SHEET_ID={result['spreadsheet_id']}")
            print()
            
            # بروزرسانی .env
            update_env_file(result['spreadsheet_id'])
            
        else:
            print_error("خطا در ساخت Sheet")
            
    except Exception as e:
        print_error(f"خطا: {e}")
        sys.exit(1)


def update_env_file(sheet_id: str):
    """بروزرسانی فایل .env"""
    env_path = Path('.env')
    
    if not env_path.exists():
        example_path = Path('.env.example')
        if example_path.exists():
            env_path.write_text(example_path.read_text())
    
    if env_path.exists():
        content = env_path.read_text()
        
        if 'DAILY_LOG_SHEET_ID=' in content:
            lines = content.split('\n')
            new_lines = []
            for line in lines:
                if line.startswith('DAILY_LOG_SHEET_ID='):
                    new_lines.append(f'DAILY_LOG_SHEET_ID={sheet_id}')
                else:
                    new_lines.append(line)
            env_path.write_text('\n'.join(new_lines))
            print_success(".env بروزرسانی شد")
        else:
            with open(env_path, 'a') as f:
                f.write(f'\nDAILY_LOG_SHEET_ID={sheet_id}\n')
            print_success("Sheet ID به .env اضافه شد")


if __name__ == '__main__':
    main()
