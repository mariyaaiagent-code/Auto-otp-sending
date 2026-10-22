# -*- coding: utf-8 -*-
"""Selenium Bot - يعمل مع Facebook Identify"""

import time
from concurrent.futures import ThreadPoolExecutor, as_completed
from datetime import datetime

from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from webdriver_manager.chrome import ChromeDriverManager

from config import *
from file_reader import load_numbers, save_result
from logger import logger, log_start, log_finish
from report_generator import generate_html_report
from user_agents import get_random_ua


# ============ الإعدادات ============
FACEBOOK_URL = "https://www.facebook.com/login/identify/?locale=en_US"
MAX_WINDOWS = 3
PAGE_TIMEOUT = 40


def safe_click(driver, el, name=""):
    """نقر آمن"""
    try:
        driver.execute_script("arguments[0].scrollIntoView({block: 'center'});", el)
        time.sleep(0.3)
        try:
            el.click()
        except:
            driver.execute_script("arguments[0].click();", el)
        return True
    except Exception:
        return False


def create_driver(headless=False):
    """إنشاء WebDriver - نسخة محسّنة"""
    options = Options()
    if headless:
        options.add_argument("--headless=new")

    # تحسينات الأداء
    options.add_argument("--disable-gpu")
    options.add_argument("--no-sandbox")
    options.add_argument("--disable-dev-shm-usage")
    options.add_argument("--disable-software-rasterizer")
    options.add_argument("--disable-extensions")

    # إخفاء الأتمتة
    options.add_argument("--disable-blink-features=AutomationControlled")
    options.add_experimental_option("excludeSwitches", ["enable-automation"])
    options.add_experimental_option('useAutomationExtension', False)

    # إعدادات إضافية
    options.add_argument("--disable-notifications")
    options.add_argument("--disable-infobars")
    options.add_argument("--mute-audio")
    options.add_argument("--window-size=500,700")
    options.add_argument(f"user-agent={get_random_ua()}")

    driver = webdriver.Chrome(
        service=Service(ChromeDriverManager().install()),
        options=options
    )
    driver.set_page_load_timeout(PAGE_TIMEOUT)
    return driver


def process_number(number, headless=False):
    """
    معالجة رقم واحد عبر Facebook Identify

    Returns: (bool, str, str) - (نجح, رسالة, حالة)
    """
    driver = None

    try:
        # 1: فتح المتصفح
        driver = create_driver(headless=headless)

        # 2: فتح الصفحة
        driver.get(FACEBOOK_URL)
        time.sleep(2)

        # 3: إدخال الرقم
        try:
            phone_input = WebDriverWait(driver, 15).until(
                EC.presence_of_element_located((By.XPATH, "//input[@type='text']"))
            )
            phone_input.clear()
            phone_input.send_keys(number)
            time.sleep(1)
        except Exception as e:
            return False, f"لم نجد حقل الإدخال: {str(e)[:40]}", "failed"

        # 4: Continue الأول
        try:
            el = WebDriverWait(driver, 10).until(
                EC.presence_of_element_located((By.XPATH,
                    "//div[@role='button' and .//span[text()='Continue']]"))
            )
            safe_click(driver, el, "Continue #1")
            time.sleep(5)
        except Exception as e:
            return False, f"لم نجد زر Continue: {str(e)[:40]}", "failed"

        # 5: فحص الصفحة الحالية
        current_url = driver.current_url

        if "login/identify" in current_url:
            return False, "لم ننتقل لصفحة الخيارات", "failed"

        if "login" in current_url and "recover" not in current_url:
            return False, "الصفحة تطلب كلمة المرور", "failed"

        # 6: البحث عن صفحة OTP أو خيارات SMS
        time.sleep(3)

        body_text = driver.find_element(By.TAG_NAME, "body").text

        # الحالة 1: صفحة الخيارات
        if "Choose a way to log in" in body_text or "Get code via SMS" in body_text:
            print(f"     → صفحة الخيارات")

            sms_clicked = False
            all_radios = driver.find_elements(By.XPATH, "//input[@type='radio']")

            for radio in all_radios:
                try:
                    radio_id = radio.get_attribute("id") or ""
                    if radio_id:
                        try:
                            label = driver.find_element(By.XPATH, f"//label[@for='{radio_id}']")
                            if number in label.text:
                                safe_click(driver, label, "SMS option")
                                sms_clicked = True
                                break
                        except:
                            pass

                    parent = radio.find_element(By.XPATH, "./..")
                    if number in parent.text:
                        safe_click(driver, radio, "SMS option (radio)")
                        sms_clicked = True
                        break
                except:
                    continue

            if not sms_clicked:
                return False, "لم نجد خيار SMS", "failed"

            time.sleep(1)

            # النقر على Continue الأزرق
            spans = driver.find_elements(By.XPATH, "//span[text()='Continue']")
            continue_clicked = False

            for span in spans:
                try:
                    parent = span.find_element(By.XPATH, "./ancestor::*[@role='button'][1]")
                    if parent.text.strip() == "Continue":
                        safe_click(driver, parent, "Continue الأزرق")
                        continue_clicked = True
                        break
                except:
                    continue

            if not continue_clicked:
                return False, "لم نجد Continue الأزرق", "failed"

            time.sleep(5)

        # الحالة 2: صفحة OTP مباشرة
        elif "Enter the code" in body_text or "6-digit" in body_text or "We sent" in body_text:
            print(f"     → صفحة OTP مباشرة")
            return True, "OTP مُرسَل مباشرة", "success"

        # الحالة 3: Captcha
        elif "not a robot" in body_text.lower() or "captcha" in body_text.lower():
            print(f"     → Captcha")
            return True, "OTP مُرسَل - Captcha ظهرت", "success"

        # الحالة 4: صفحة غير معروفة
        else:
            return False, "صفحة غير معروفة", "failed"

        # 7: التحقق النهائي
        time.sleep(3)
        body_text = driver.find_element(By.TAG_NAME, "body").text

        if any(kw in body_text for kw in ["Enter the code", "We sent", "6-digit", "Confirmation code"]):
            return True, "OTP مُرسَل - حقل الكود ظهر", "success"

        if any(kw in body_text.lower() for kw in ["not a robot", "captcha", "security check"]):
            return True, "OTP مُرسَل - Captcha ظهرت", "success"

        return True, "OTP مُرسَل (غير مؤكد)", "success"

    except Exception as e:
        error_msg = str(e)[:80]

        if "timeout" in error_msg.lower():
            return False, "Timeout من Chrome", "error"

        return False, f"خطأ: {error_msg}", "error"

    finally:
        if driver:
            try:
                driver.quit()
            except:
                pass


def run():
    """نقطة الدخول - من main.py"""
    show_logo()

    print(f"{GREEN}[●]{WHITE} تحميل الأرقام...")
    numbers = load_numbers("Number_List.txt")

    if not numbers:
        print(f"{RED}❌ لا توجد أرقام!")
        return

    print(f"{GREEN}[●]{WHITE} عدد الأرقام: {len(numbers)}")

    # الوضع
    try:
        mode = input(f"{GREEN}[●]{WHITE} الوضع (1=مرئي, 2=مخفي) [افتراضي: 1]: ").strip() or "1"
        headless = (mode == "2")
    except:
        headless = False

    # عدد النوافذ
    print(f"{YELLOW}⚠️  تحذير: 3 نوافذ قد تسبب timeouts{RESET}")
    try:
        windows = int(input(f"{GREEN}[●]{WHITE} عدد النوافذ [افتراضي: 2, أقصى: 3]: ").strip() or "2")
        windows = min(windows, 3)
        windows = max(windows, 1)
    except:
        windows = 2

    print(f"\n{GREEN}{LINE}")
    print(f"  🚀 بدء المعالجة...")
    print(f"  🪟 النوافذ: {windows}")
    print(f"  👁️  الوضع: {'مخفي' if headless else 'مرئي'}")
    print(f"  ⏱️  Timeout: {PAGE_TIMEOUT} ثانية")
    print(f"{LINE}{RESET}\n")

    log_start(len(numbers), 0)
    logger.info(f"🪟 عدد النوافذ: {windows}")
    logger.info(f"👁️  الوضع: {'headless' if headless else 'visible'}")

    success = 0
    failed = 0
    errors = 0
    results = []
    start_time = time.time()

    with ThreadPoolExecutor(max_workers=windows) as executor:
        futures = {}

        for number in numbers:
            future = executor.submit(process_number, number, headless)
            futures[future] = number

        for future in as_completed(futures):
            number = futures[future]
            current_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

            try:
                ok, msg, status = future.result()

                if status == "success":
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
                elif status == "failed":
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
                else:
                    errors += 1
                    print(f"{RED}⚠️  {number} — {msg}{RESET}")
                    logger.error(f"⚠️  خطأ: {number} — {msg}")
                    results.append({
                        "number": number,
                        "status": "error",
                        "message": msg,
                        "time": current_time,
                    })

            except Exception as e:
                errors += 1
                print(f"{RED}⚠️  {number} — استثناء: {e}{RESET}")
                logger.error(f"⚠️  {number} — {e}")
                results.append({
                    "number": number,
                    "status": "error",
                    "message": str(e)[:60],
                    "time": current_time,
                })

    duration = time.time() - start_time
    log_finish(success, failed, errors)

    print(f"\n{GREEN}{LINE}")
    print(f"  📊 النتائج:")
    print(f"  ✅ نجح: {success}")
    print(f"  ❌ فشل: {failed}")
    print(f"  ⚠️  أخطاء: {errors}")
    print(f"  ⏱️  المدة: {duration:.1f} ثانية")
    print(f"{LINE}{RESET}")

    try:
        report_file = generate_html_report(results, duration)
        print(f"{CYAN}  📄 التقرير: {report_file}{RESET}")
        logger.info(f"📄 التقرير: {report_file}")
    except Exception as e:
        logger.error(f"فشل التقرير: {e}")

    print(f"{CYAN}  📁 السجلات: logs/{RESET}")
