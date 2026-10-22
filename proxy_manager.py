# -*- coding: utf-8 -*-
"""إدارة البروكسي"""
import os


def parse_proxy(proxy_str):
    """
    تحويل صيغة البروكسي إلى dict
    المدعوم:
    - ip:port
    - ip:port:user:pass
    - http://user:pass@ip:port
    """
    if not proxy_str or not proxy_str.strip():
        return None

    proxy_str = proxy_str.strip()

    if "://" in proxy_str:
        return {"http": proxy_str, "https": proxy_str}

    parts = proxy_str.split(":")

    if len(parts) == 2:
        url = f"http://{parts[0]}:{parts[1]}"
        return {"http": url, "https": url}

    if len(parts) == 4:
        url = f"http://{parts[2]}:{parts[3]}@{parts[0]}:{parts[1]}"
        return {"http": url, "https": url}

    return None


def load_proxies_from_file(filename="proxies.txt"):
    """قراءة البروكسيات من ملف"""
    proxies = []

    if not os.path.exists(filename):
        return proxies

    with open(filename, "r", encoding="utf-8") as f:
        for line in f:
            line = line.strip()
            if line and not line.startswith("#"):
                parsed = parse_proxy(line)
                if parsed:
                    proxies.append(parsed)

    return proxies


def test_proxy(proxy_dict, timeout=5):
    """اختبار صلاحية البروكسي"""
    import requests
    try:
        r = requests.get(
            "http://httpbin.org/ip",
            proxies=proxy_dict,
            timeout=timeout
        )
        return r.status_code == 200
    except:
        return False
