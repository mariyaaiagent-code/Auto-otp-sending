# -*- coding: utf-8 -*-
"""مولّد تقارير HTML"""
import os
from datetime import datetime


def generate_html_report(results, duration_seconds=0):
    """
    توليد تقرير HTML

    Args:
        results: قائمة من dicts
            {
                "number": "+201234567890",
                "status": "success" | "failed" | "error",
                "message": "تم إرسال OTP",
                "time": "2026-10-16 14:30:05"
            }
        duration_seconds: مدة التشغيل بالثواني

    Returns:
        مسار ملف HTML
    """
    today = datetime.now().strftime("%Y-%m-%d")
    filename = f"report_{today}.html"

    # إحصائيات
    total = len(results)
    success = sum(1 for r in results if r["status"] == "success")
    failed = sum(1 for r in results if r["status"] == "failed")
    errors = sum(1 for r in results if r["status"] == "error")

    success_rate = (success / total * 100) if total > 0 else 0
    duration_min = duration_seconds / 60

    # بناء الجداول
    rows_html = ""
    for r in results:
        if r["status"] == "success":
            badge = '<span class="badge success">✅ نجح</span>'
            row_class = "row-success"
        elif r["status"] == "failed":
            badge = '<span class="badge failed">❌ فشل</span>'
            row_class = "row-failed"
        else:
            badge = '<span class="badge error">⚠️ خطأ</span>'
            row_class = "row-error"

        rows_html += f"""
        <tr class="{row_class}">
            <td>{r['number']}</td>
            <td>{badge}</td>
            <td>{r.get('message', '')}</td>
            <td>{r.get('time', '')}</td>
        </tr>
        """

    html = f"""<!DOCTYPE html>
<html lang="ar" dir="rtl">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>تقرير Meta OTP - {today}</title>
    <style>
        * {{
            box-sizing: border-box;
            margin: 0;
            padding: 0;
        }}
        body {{
            font-family: 'Segoe UI', Tahoma, Arial, sans-serif;
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            min-height: 100vh;
            padding: 20px;
            direction: rtl;
        }}
        .container {{
            max-width: 1200px;
            margin: 0 auto;
            background: white;
            border-radius: 15px;
            box-shadow: 0 20px 60px rgba(0,0,0,0.3);
            overflow: hidden;
        }}
        .header {{
            background: linear-gradient(135deg, #1e3c72 0%, #2a5298 100%);
            color: white;
            padding: 30px;
            text-align: center;
        }}
        .header h1 {{
            font-size: 2em;
            margin-bottom: 10px;
        }}
        .header p {{
            opacity: 0.9;
            font-size: 1.1em;
        }}
        .stats {{
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
            gap: 15px;
            padding: 30px;
            background: #f8f9fa;
        }}
        .stat-card {{
            background: white;
            padding: 20px;
            border-radius: 10px;
            text-align: center;
            box-shadow: 0 2px 10px rgba(0,0,0,0.1);
            border-right: 5px solid;
        }}
        .stat-card.total {{ border-color: #3498db; }}
        .stat-card.success {{ border-color: #27ae60; }}
        .stat-card.failed {{ border-color: #e74c3c; }}
        .stat-card.errors {{ border-color: #f39c12; }}
        .stat-card.duration {{ border-color: #9b59b6; }}
        .stat-number {{
            font-size: 2.5em;
            font-weight: bold;
            margin: 10px 0;
        }}
        .stat-card.total .stat-number {{ color: #3498db; }}
        .stat-card.success .stat-number {{ color: #27ae60; }}
        .stat-card.failed .stat-number {{ color: #e74c3c; }}
        .stat-card.errors .stat-number {{ color: #f39c12; }}
        .stat-card.duration .stat-number {{ color: #9b59b6; font-size: 1.8em; }}
        .stat-label {{
            color: #7f8c8d;
            font-size: 0.95em;
        }}
        .progress-section {{
            padding: 20px 30px;
            background: white;
        }}
        .progress-bar {{
            height: 30px;
            background: #ecf0f1;
            border-radius: 15px;
            overflow: hidden;
            display: flex;
        }}
        .progress-success {{
            background: linear-gradient(90deg, #27ae60, #2ecc71);
            color: white;
            display: flex;
            align-items: center;
            justify-content: center;
            font-weight: bold;
        }}
        .progress-failed {{
            background: linear-gradient(90deg, #e74c3c, #c0392b);
            color: white;
            display: flex;
            align-items: center;
            justify-content: center;
            font-weight: bold;
        }}
        .progress-errors {{
            background: linear-gradient(90deg, #f39c12, #e67e22);
            color: white;
            display: flex;
            align-items: center;
            justify-content: center;
            font-weight: bold;
        }}
        .table-section {{
            padding: 0 30px 30px 30px;
        }}
        .table-section h2 {{
            margin-bottom: 15px;
            color: #2c3e50;
        }}
        table {{
            width: 100%;
            border-collapse: collapse;
            background: white;
            border-radius: 10px;
            overflow: hidden;
            box-shadow: 0 2px 10px rgba(0,0,0,0.1);
        }}
        th {{
            background: #34495e;
            color: white;
            padding: 15px;
            text-align: right;
            font-weight: 600;
        }}
        td {{
            padding: 12px 15px;
            border-bottom: 1px solid #ecf0f1;
            text-align: right;
        }}
        tr:last-child td {{
            border-bottom: none;
        }}
        tr:hover {{
            background: #f8f9fa;
        }}
        .badge {{
            display: inline-block;
            padding: 5px 12px;
            border-radius: 20px;
            font-weight: bold;
            font-size: 0.9em;
        }}
        .badge.success {{
            background: #d4edda;
            color: #155724;
        }}
        .badge.failed {{
            background: #f8d7da;
            color: #721c24;
        }}
        .badge.error {{
            background: #fff3cd;
            color: #856404;
        }}
        .row-success {{ background: #f0fff4; }}
        .row-failed {{ background: #fff5f5; }}
        .row-error {{ background: #fffbf0; }}
        .footer {{
            background: #2c3e50;
            color: white;
            padding: 20px;
            text-align: center;
            font-size: 0.9em;
        }}
        @media (max-width: 768px) {{
            .header h1 {{ font-size: 1.5em; }}
            .stats {{ padding: 15px; gap: 10px; }}
            .stat-number {{ font-size: 1.8em; }}
            th, td {{ padding: 8px; font-size: 0.9em; }}
            .table-section {{ padding: 0 15px 15px 15px; }}
        }}
    </style>
</head>
<body>
    <div class="container">
        <div class="header">
            <h1>📊 تقرير Meta OTP Sender</h1>
            <p>📅 {today}</p>
        </div>

        <div class="stats">
            <div class="stat-card total">
                <div class="stat-label">📋 الإجمالي</div>
                <div class="stat-number">{total}</div>
            </div>
            <div class="stat-card success">
                <div class="stat-label">✅ نجح</div>
                <div class="stat-number">{success}</div>
            </div>
            <div class="stat-card failed">
                <div class="stat-label">❌ فشل</div>
                <div class="stat-number">{failed}</div>
            </div>
            <div class="stat-card errors">
                <div class="stat-label">⚠️ أخطاء</div>
                <div class="stat-number">{errors}</div>
            </div>
            <div class="stat-card duration">
                <div class="stat-label">⏱️ المدة</div>
                <div class="stat-number">{duration_min:.1f} د</div>
            </div>
        </div>

        <div class="progress-section">
            <h2 style="margin-bottom: 10px; color: #2c3e50;">معدل النجاح: {success_rate:.1f}%</h2>
            <div class="progress-bar">
                <div class="progress-success" style="width: {(success/total*100) if total else 0}%">{success}</div>
                <div class="progress-failed" style="width: {(failed/total*100) if total else 0}%">{failed}</div>
                <div class="progress-errors" style="width: {(errors/total*100) if total else 0}%">{errors}</div>
            </div>
        </div>

        <div class="table-section">
            <h2>📋 تفاصيل العمليات</h2>
            <table>
                <thead>
                    <tr>
                        <th>📱 الرقم</th>
                        <th>الحالة</th>
                        <th>الرسالة</th>
                        <th>🕐 الوقت</th>
                    </tr>
                </thead>
                <tbody>
                    {rows_html if rows_html else '<tr><td colspan="4" style="text-align: center; padding: 30px;">لا توجد بيانات</td></tr>'}
                </tbody>
            </table>
        </div>

        <div class="footer">
            <p>🤖 تم إنشاء التقرير بواسطة Meta OTP Sender</p>
            <p>© 2026</p>
        </div>
    </div>
</body>
</html>
"""

    with open(filename, "w", encoding="utf-8") as f:
        f.write(html)

    return filename
