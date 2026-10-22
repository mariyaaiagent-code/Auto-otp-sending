# -*- coding: utf-8 -*-
"""قراءة الأرقام"""
import os
import re


def clean_number(number):
    """تنظيف رقم الهاتف"""
    if not number:
        return None
    cleaned = re.sub(r'[\s\-\(\)\.]', '', str(number).strip())
    if re.match(r'^\+?\d{7,15}$', cleaned):
        return cleaned
    return None


def load_numbers(filename="Number_List.txt"):
    """قراءة الأرقام من ملف"""
    if not os.path.exists(filename):
        print(f"⚠️  الملف {filename} غير موجود")
        return []

    numbers = []
    with open(filename, "r", encoding="utf-8") as f:
        for line in f:
            cleaned = clean_number(line)
            if cleaned:
                numbers.append(cleaned)

    return list(dict.fromkeys(numbers))


def save_result(number, filename):
    """حفظ النتيجة"""
    with open(filename, "a", encoding="utf-8") as f:
        f.write(f"{number}\n")
