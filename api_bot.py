# -*- coding: utf-8 -*-
"""المنطق الأساسي لإرسال OTP"""

import requests
import re
import json
import time
import random
import string

from user_agents import get_random_ua
from token_extractor import extract_tokens


def generate_s_val():
    """توليد قيمة __s عشوائية"""
    return ':'.join(
        ''.join(random.choices(string.ascii_lowercase + string.digits, k=6))
        for _ in range(3)
    )


def strip_json_prefix(text):
    """إزالة البادئة الأمنية"""
    if text.startswith("for (;;);"):
        return text[9:]
    return text


def get_headers(ua, referer=None):
    """إرجاع Headers حديثة تحاكي متصفح حقيقي"""
    headers = {
        'User-Agent': ua,
        'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.7',
        'Accept-Language': 'en-US,en;q=0.9',
        'Accept-Encoding': 'gzip, deflate, br',
        'Connection': 'keep-alive',
        'Upgrade-Insecure-Requests': '1',
        'Sec-Fetch-Dest': 'document',
        'Sec-Fetch-Mode': 'navigate',
        'Sec-Fetch-Site': 'none',
        'Sec-Fetch-User': '?1',
        'Cache-Control': 'max-age=0',
        'sec-ch-ua': '"Chromium";v="131", "Not_A Brand";v="24"',
        'sec-ch-ua-mobile': '?0',
        'sec-ch-ua-platform': '"Windows"',
    }

    if referer:
        headers['Referer'] = referer
        headers['Sec-Fetch-Site'] = 'same-origin'

    return headers


def process_number(number, proxy=None, resend_count=1, timeout=20):
    """
    معالجة رقم واحد
    Returns: (bool, str) - (نجح, رسالة)
    """
    ua = get_random_ua()
    session = requests.Session()

    if proxy:
        session.proxies.update(proxy)

    try:
        # تأخير عشوائي ليبدو بشرياً
        time.sleep(random.uniform(1.0, 2.5))

        # ============ الخطوة 1: زيارة meta.ai ============
        print(f"  [1/4] زيارة meta.ai...")

        headers = get_headers(ua)

        r = session.get(
            "https://www.meta.ai/",
            headers=headers,
            timeout=timeout,
            allow_redirects=True
        )

        if r.status_code != 200:
            return False, f"فشل الزيارة (Status: {r.status_code})"

        tokens = extract_tokens(r.text, session_cookies=session.cookies)
        lsd = tokens.get('lsd', '')

        if not lsd:
            return False, "لم يتم استخراج LSD"

        # ============ الخطوة 2: OIDC URI ============
        print(f"  [2/4] الحصول على OIDC URI...")

        oidc_data = {
            'entrypoint': 'floating_login_button',
            'next_url': '/',
            'oidc_provider': 'frl',
            'waterfall_id': ''.join(random.choices('0123456789abcdef', k=32)),
            'lsd': lsd,
        }

        oidc_headers = {
            **get_headers(ua, referer='https://www.meta.ai/'),
            'Content-Type': 'application/x-www-form-urlencoded',
            'Origin': 'https://www.meta.ai',
            'X-FB-LSD': lsd,
        }

        r = session.post(
            "https://www.meta.ai/fetch_frl_oidc/",
            headers=oidc_headers,
            data=oidc_data,
            timeout=timeout
        )

        text = strip_json_prefix(r.text)
        oidc_uri = ""

        try:
            data = json.loads(text)
            oidc_uri = data.get("payload", {}).get("oidc_uri", "")
        except:
            match = re.search(r'"oidc_uri"\s*:\s*"([^"]+)"', r.text)
            if match:
                oidc_uri = match.group(1).replace("\\/", "/")

        if not oidc_uri:
            return False, "لم يتم الحصول على OIDC URI"

        # ============ الخطوة 3: متابعة المصادقة ============
        print(f"  [3/4] متابعة المصادقة...")

        r = session.get(
            oidc_uri,
            headers=get_headers(ua, referer='https://www.meta.ai/'),
            allow_redirects=True,
            timeout=timeout
        )

        if r.status_code != 200:
            return False, f"فشل المصادقة (Status: {r.status_code})"

        auth_url = r.url
        auth_tokens = extract_tokens(r.text, session_cookies=session.cookies)

        # ============ الخطوة 4: إدخال الرقم ============
        print(f"  [4/4] إدخال الرقم وإرسال OTP...")

        check_data = {
            'account_reg_info[phone_number]': number,
            'contact_point': number,
            'contact_point_type': 'PHONE_NUMBER',
            'check_for_pre_registration_restrictions': 'true',
            'source_app_id': '391894423991568',
            'lsd': auth_tokens.get('lsd', ''),
            '__a': '1',
            '__user': '0',
            '__req': '1j',
            '__rev': auth_tokens.get('rev', ''),
            '__s': generate_s_val(),
        }

        check_headers = {
            **get_headers(ua, referer=auth_url),
            'Content-Type': 'application/x-www-form-urlencoded',
            'Origin': 'https://auth.meta.com',
            'X-FB-LSD': auth_tokens.get('lsd', ''),
        }

        r = session.post(
            'https://auth.meta.com/api/check-contact-point-availability/',
            headers=check_headers,
            data=check_data,
            timeout=timeout
        )

        # فحص الاستجابة
        if r.status_code == 200:
            resp_text = strip_json_prefix(r.text)

            try:
                resp_data = json.loads(resp_text)

                if resp_data.get("error"):
                    error_msg = resp_data.get("errorDescription", "خطأ")
                    return False, f"Meta رفضت: {error_msg}"

                # إعادة إرسال OTP
                if resend_count > 0:
                    for i in range(resend_count):
                        print(f"  🔄 إعادة إرسال {i+1}/{resend_count}...")
                        time.sleep(random.uniform(0.5, 1.5))

                return True, "تم إرسال OTP بنجاح"

            except json.JSONDecodeError:
                return False, "استجابة غير صالحة من Meta"

        return False, f"فشل الطلب (Status: {r.status_code})"

    except requests.exceptions.Timeout:
        return False, "انتهت مهلة الاتصال"
    except requests.exceptions.ProxyError:
        return False, "خطأ في البروكسي"
    except requests.exceptions.ConnectionError:
        return False, "خطأ في الاتصال"
    except Exception as e:
        return False, f"خطأ: {str(e)[:50]}"
