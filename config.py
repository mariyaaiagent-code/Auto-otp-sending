# -*- coding: utf-8 -*-
"""إعدادات الألوان والواجهة"""

WHITE = "\033[1;97m"
GREEN = "\033[1;92m"
RED = "\033[1;91m"
CYAN = "\033[1;96m"
YELLOW = "\033[1;93m"
RESET = "\033[0m"

EKL = f"{CYAN}:{WHITE}"
LINE = f"{CYAN}•{'━'*47}•"


def clear_screen():
    import os
    os.system("clear" if os.name != "nt" else "cls")


def show_logo():
    clear_screen()
    print(f"""{GREEN}
╔══════════════════════════════════════════╗
║       META OTP SENDER v1.0               ║
║       تعليمي - للاستخدام الشخصي          ║
╚══════════════════════════════════════════╝
{LINE}""")
