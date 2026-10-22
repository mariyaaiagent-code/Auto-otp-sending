# -*- coding: utf-8 -*-
"""استخراج الرموز من HTML"""
import re
import time

LSD_PATTERNS = [
    re.compile(r'"LSD",\s*\[\s*\],\s*\{\s*"token":\s*"([^"]+)"'),
    re.compile(r'"lsd":\s*"([^"]+)"'),
    re.compile(r'name="lsd"\s+value="([^"]+)"'),
]

REV_PATTERN = re.compile(r'"server_revision":\s*(\d+)')
HSI_PATTERN = re.compile(r'"hsi":\s*"(\d+)"')
SPIN_B_PATTERN = re.compile(r'"__spin_b":\s*"([^"]+)"')
SPIN_T_PATTERN = re.compile(r'"__spin_t":\s*(\d+)')
HS_PATTERN = re.compile(r'"__hs":\s*"([^"]+)"')
COMET_REQ_PATTERN = re.compile(r'"comet_env":\s*(\d+)')


def extract_tokens(html, session_cookies=None):
    """استخراج الرموز من HTML"""
    tokens = {
        'lsd': '',
        'rev': '',
        'hsi': '',
        'hs': '',
        'spin_b': 'trunk',
        'spin_t': str(int(time.time())),
        'comet_req': '72',
        'jazoest': '',
    }

    for p in LSD_PATTERNS:
        m = p.search(html)
        if m:
            tokens['lsd'] = m.group(1)
            break

    m = REV_PATTERN.search(html)
    if m:
        tokens['rev'] = m.group(1)

    m = HSI_PATTERN.search(html)
    if m:
        tokens['hsi'] = m.group(1)

    m = HS_PATTERN.search(html)
    if m:
        tokens['hs'] = m.group(1)

    m = SPIN_B_PATTERN.search(html)
    if m:
        tokens['spin_b'] = m.group(1)

    m = SPIN_T_PATTERN.search(html)
    if m:
        tokens['spin_t'] = m.group(1)

    m = COMET_REQ_PATTERN.search(html)
    if m:
        tokens['comet_req'] = m.group(1)

    if session_cookies:
        try:
            cookie_str = ''.join(session_cookies.get_dict().values())
            tokens['jazoest'] = "2" + str(sum(ord(c) for c in cookie_str))
        except:
            pass

    return tokens
