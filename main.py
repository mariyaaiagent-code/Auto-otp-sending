# -*- coding: utf-8 -*-
"""Meta OTP Sender - نقطة الدخول"""

import sys
import time
from datetime import datetime
from concurrent.futures import ThreadPoolExecutor, as_completed

from config import *
from file_reader import load_numbers, save_result
from proxy_manager import load_proxies_from_file
from api_bot import process_number
from logger import logger, log_start, log_finish
from report_generator import generate_html_report


def choose_mode():
    """اختيار الوضع: API أو Selenium"""
    show_logo()
    print(f" {GREEN}[{RED}01{GREEN}] API Bot         {EKL} سريع، بدون متصفح")
    print(f" {GREEN}[{RED}02{GREEN}] Selenium Bot    {EKL} متصفح حقيقي (يعمل)")
    print(f" {GREEN}[{RED}03{GREEN}] خروج")
    print(f"{LINE}")

    choice = input(f"{GREEN} [{RED}●{GREEN}] اختر الوضع {EKL} ").strip()

    if choice in ["1", "01"]:
        return "api"
    elif choice in ["2", "02"]:
        return "selenium"
    elif choice in ["3", "03"]:
        print(f"\n{GREEN} [{RED}●{GREEN}] إلى اللقاء!")
        time.sleep(1)
        sys.exit(0)
    else:
        print(f"\n{RED} اختيار غير صحيح! جرب مرة أخرى...")
        time.sleep(1.5)
        return choose_mode()


def run_api_mode():
    """الوضع القديم - API"""
    show_logo()

    print(f"{GREEN}[●]{WHITE} تحميل الأرقام...")
    numbers = load_numbers("Number_List.txt")

    if not numbers:
        print(f"{RED}❌ لا توجد أرقام!")
        print(f"{WHITE}أضف أرقاماً في ملف Number_List.txt")
        logger.warning("لا توجد أرقام في Number_List.txt")
        return

    print(f"{GREEN}[●]{WHITE} عدد الأرقام: {len(numbers)}")

    proxies = load_proxies_from_file("proxies.txt")
    print(f"{GREEN}[●]{WHITE} عدد البروكسيات: {len(proxies)}")

    # عدد الخيوط
    try:
        threads = int(input(f"{GREEN}[●]{WHITE} عدد الخيوط (افتراضي 5): ").strip() or "5")
    except:
        threads = 5

    # عدد مرات إعادة OTP
    try:
        resend = int(input(f"{GREEN}[●]{WHITE} مرات إعادة OTP (افتراضي 1): ").strip() or "1")
    except:
        resend = 1

    print(f"\n{GREEN}{LINE}")
    print(f"  بدء المعالجة...")
    print(f"{LINE}{RESET}\n")

    log_start(len(numbers), len(proxies))
    logger.info(f"⚙️  عدد الخيوط: {threads}")
    logger.info(f"⚙️  مرات إعادة OTP: {resend}")

    success = 0
    failed = 0
    errors = 0
    results = []
    start_time = time.time()

    with ThreadPoolExecutor(max_workers=threads) as executor:
        futures = {}

        for i, number in enumerate(numbers):
            proxy = proxies[i % len(proxies)] if proxies else None
            future = executor.submit(process_number, number, proxy, resend)
            futures[future] = number

        for future in as_completed(futures):
            number = futures[future]
            current_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

            try:
                ok, msg = future.result()

                if ok:
                    success += 1
                    print(f"{GREEN}✅ {number} — {msg}{RESET}")
                    save_result(number, "Success_Numbers.txt")
                    logger.info(f"✅ نجح: {number} — {msg}")
                    results.append({
                        "number": number,
                        "status": "success",
                        "message": msg,
                        "time": current_time,
                    })
                else:
                    failed += 1
                    print(f"{RED}❌ {number} — {msg}{RESET}")
                    save_result(number, "Failed_Numbers.txt")
                    logger.warning(f"❌ فشل: {number} — {msg}")
                    results.append({
                        "number": number,
                        "status": "failed",
                        "message": msg,
                        "time": current_time,
                    })

            except Exception as e:
                errors += 1
                print(f"{RED}⚠️  {number} — خطأ: {e}{RESET}")
                logger.error(f"⚠️  خطأ: {number} — {e}")
                results.append({
                    "number": number,
                    "status": "error",
                    "message": str(e)[:80],
                    "time": current_time,
                })

    duration = time.time() - start_time
    log_finish(success, failed, errors)

    # النتائج
    print(f"\n{GREEN}{LINE}")
    print(f"  📊 النتائج:")
    print(f"  ✅ نجح: {success}")
    print(f"  ❌ فشل: {failed}")
    print(f"  ⚠️  أخطاء: {errors}")
    print(f"  ⏱️  المدة: {duration:.1f} ثانية")
    print(f"{LINE}{RESET}")

    # تقرير HTML
    try:
        report_file = generate_html_report(results, duration)
        print(f"{CYAN}  📄 التقرير: {report_file}{RESET}")
        logger.info(f"📄 تم إنشاء التقرير: {report_file}")
    except Exception as e:
        print(f"{RED}  ⚠️  فشل إنشاء التقرير: {e}{RESET}")
        logger.error(f"فشل إنشاء التقرير: {e}")

    print(f"{CYAN}  📁 السجلات: logs/{RESET}")


def run_selenium_mode():
    """الوضع الجديد - Selenium"""
    from selenium_bot import run as selenium_run
    selenium_run()


def main():
    """الدالة الرئيسية"""
    mode = choose_mode()

    if mode == "api":
        run_api_mode()
    elif mode == "selenium":
        run_selenium_mode()


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print(f"\n{YELLOW}⏹️  تم الإيقاف{RESET}")
        logger.info("⏹️  تم إيقاف الأداة يدوياً")
    except Exception as e:
        print(f"\n{RED}❌ خطأ غير متوقع: {e}{RESET}")
        logger.exception(f"❌ خطأ غير متوقع: {e}")
