# -*- coding: utf-8 -*-
"""User-Agents حديثة"""
import random

MODERN_UAS = [
    # Chrome على Windows
    'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/131.0.0.0 Safari/537.36',
    # Safari على iPhone
    'Mozilla/5.0 (iPhone; CPU iPhone OS 18_1 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/18.1 Mobile/15E148 Safari/604.1',
    # Chrome على Android
    'Mozilla/5.0 (Linux; Android 14; SM-S921B) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/131.0.0.0 Mobile Safari/537.36',
]


def get_random_ua():
    """إرجاع User-Agent عشوائي حديث"""
    return random.choice(MODERN_UAS)
