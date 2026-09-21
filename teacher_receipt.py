"""
teacher_receipt.py — Printable Teacher Salary Slip Voucher
Renders two copies on the same page (School Copy & Teacher Copy) separated by a cut line.
"""

import streamlit.components.v1 as components
import ui

TEACHER_SLIP_TEMPLATE = """
<!DOCTYPE html>
<html lang="ar" dir="rtl">
<head>
<meta charset="utf-8">
<style>
    @import url('https://fonts.googleapis.com/css2?family=Cairo:wght@400;600;700;800&display=swap');

    :root {{
        --primary-dark:#163D22;
        --gold:#D7A431;
    }}
    * {{ 
        box-sizing: border-box; 
        font-family: 'Cairo', 'Segoe UI', Tahoma, sans-serif;
    }}
    body {{
        direction: rtl;
        text-align: right;
        margin: 0;
        padding: 10px;
        background: #FAF9F5;
    }}
    .page-container {{
        max-width: 520px;
        margin: 0 auto;
    }}
    .letterhead {{
        display: flex; 
        align-items: center; 
        justify-content: center; 
        gap: 10px;
        margin-bottom: 6px;
    }}
    .letterhead img {{ 
        width: 42px; 
        height: 42px; 
        border-radius: 50%; 
        flex-shrink: 0; 
    }}
    .letterhead-text {{ text-align: center; }}
    .letterhead-text .lh-ar {{ font-size: 14px; font-weight: 800; color: var(--primary-dark); }}
    .letterhead-text .lh-en {{ font-size: 10px; color: #7C8A7E; }}
    
    .voucher-box {{
        background: #FFFDF6;
        border: 2px dashed var(--gold);
        border-radius: 12px;
        padding: 12px 16px;
        font-size: 12px;
        line-height: 1.5;
        position: relative;
    }}
    .voucher-header {{
        display: flex;
        justify-content: space-between;
        align-items: center;
        border-bottom: 1px dashed var(--gold);
        padding-bottom: 6px;
        margin-bottom: 8px;
    }}
    .voucher-header h3 {{
        margin: 0;
        color: var(--primary-dark);
        font-size: 15px;
    }}
    .copy-badge {{
        background: var(--primary-dark);
        color: #FFFDF6;
        font-size: 11px;
        font-weight: 700;
        padding: 2px 8px;
        border-radius: 6px;
    }}
    .details-table {{
        width: 100%;
        border-collapse: collapse;
        margin: 8px 0;
    }}
    .details-table td, .details-table th {{
        padding: 5px;
        border: 1px solid #e5e0c8;
        font-size: 12px;
    }}
    .details-table th {{
        background: #F4EFE0;
        color: var(--primary-dark);
        font-weight: 700;
    }}
    .amount-highlight {{
        font-size: 14px;
        font-weight: 800;
        color: #15803D;
    }}
    .signatures {{
        display: flex;
        justify-content: space-between;
        margin-top: 15px;
        padding-top: 8px;
        border-top: 1px solid #e5e0c8;
        text-align: center;
        font-size: 11px;
    }}
    .sig-block {{
        width: 45%;
    }}
    .sig-line {{
        margin-top: 20px;
        border-bottom: 1px dashed #7C8A7E;
    }}
    .cut-line {{
        display: flex;
        align-items: center;
        text-align: center;
        margin: 12px 0;
        color: #A3AD9E;
        font-size: 11px;
    }}
    .cut-line::before, .cut-line::after {{
        content: '';
        flex: 1;
        border-bottom: 1px dashed #A3AD9E;
    }}
    .cut-line::before {{ margin-left: .5em; }}
    .cut-line::after {{ margin-right: .5em; }}

    .print-btn {{
        display: block;
        width: 100%;
        max-width: 520px;
        margin: 14px auto 0 auto;
        background: var(--primary-dark);
        color: #fff;
        border: none;
        border-radius: 10px;
        padding: 10px 0;
        font-size: 14px;
        font-weight: 700;
        cursor: pointer;
    }}
    .print-btn:hover {{ opacity: .9; }}

    @media print {{
        .print-btn {{ display: none; }}
        body {{ background: #fff; padding: 0; }}
        .page-container {{ max-width: 100%; }}
        @page {{
            size: A4 portrait;
            margin: 8mm;
        }}
    }}
</style>
</head>
<body>
    <div class="page-container">
        <button class="print-btn" onclick="window.print()">🖨️ طباعة النسختين (A4)</button>

        <!-- ==================== COPY 1: SCHOOL ==================== -->
        <div class="voucher-box">
            <div class="letterhead">
                {logo_img_tag}
                <div class="letterhead-text">
                    <div class="lh-ar">روضة مؤسسة شباب البيرة</div>
                    <div class="lh-en">Al-Bireh Youth Foundation Kindergarten</div>
                </div>
            </div>

            <div class="voucher-header">
                <h3>🧾 قسيمة استلام راتب شهر: {salary_month}</h3>
                <span class="copy-badge">نسخة الروضة</span>
            </div>

            <table class="details-table">
                <tr>
                    <td><b>رقم القسيمة:</b> #{payment_id}</td>
                    <td><b>تاريخ الصرف:</b> {payment_date}</td>
                </tr>
                <tr>
                    <td><b>اسم المعلم/ة:</b> {teacher_name}</td>
                    <td><b>رقم الهوية:</b> {national_id}</td>
                </tr>
            </table>

            <table class="details-table">
                <thead>
                    <tr>
                        <th>الراتب الأساسي</th>
                        <th>المكافآت</th>
                        <th>الخصومات</th>
                        <th>صافي الراتب المستلم</th>
                    </tr>
                </thead>
                <tbody>
                    <tr style="text-align: center;">
                        <td>{base_salary} شيكل</td>
                        <td>+{bonus} شيكل</td>
                        <td>-{deductions} شيكل</td>
                        <td class="amount-highlight">{net_amount} شيكل</td>
                    </tr>
                </tbody>
            </table>

            {notes_html}

            <div class="signatures">
                <div class="sig-block">
                    <b>توقيع المعلم/ة المستلم/ة</b>
                    <div class="sig-line"></div>
                </div>
                <div class="sig-block">
                    <b>توقيع ودمغ الإدارة</b>
                    <div class="sig-line"></div>
                </div>
            </div>
        </div>

        <!-- ==================== CUT LINE ==================== -->
        <div class="cut-line">✂️ خط القص</div>

        <!-- ==================== COPY 2: TEACHER ==================== -->
        <div class="voucher-box">
            <div class="letterhead">
                {logo_img_tag}
                <div class="letterhead-text">
                    <div class="lh-ar">روضة مؤسسة شباب البيرة</div>
                    <div class="lh-en">Al-Bireh Youth Foundation Kindergarten</div>
                </div>
            </div>

            <div class="voucher-header">
                <h3>🧾 قسيمة استلام راتب شهر: {salary_month}</h3>
                <span class="copy-badge">نسخة المعلم/ة</span>
            </div>

            <table class="details-table">
                <tr>
                    <td><b>رقم القسيمة:</b> #{payment_id}</td>
                    <td><b>تاريخ الصرف:</b> {payment_date}</td>
                </tr>
                <tr>
                    <td><b>اسم المعلم/ة:</b> {teacher_name}</td>
                    <td><b>رقم الهوية:</b> {national_id}</td>
                </tr>
            </table>

            <table class="details-table">
                <thead>
                    <tr>
                        <th>الراتب الأساسي</th>
                        <th>المكافآت</th>
                        <th>الخصومات</th>
                        <th>صافي الراتب المستلم</th>
                    </tr>
                </thead>
                <tbody>
                    <tr style="text-align: center;">
                        <td>{base_salary} شيكل</td>
                        <td>+{bonus} شيكل</td>
                        <td>-{deductions} شيكل</td>
                        <td class="amount-highlight">{net_amount} شيكل</td>
                    </tr>
                </tbody>
            </table>

            {notes_html}

            <div class="signatures">
                <div class="sig-block">
                    <b>توقيع المعلم/ة المستلم/ة</b>
                    <div class="sig-line"></div>
                </div>
                <div class="sig-block">
                    <b>توقيع ودمغ الإدارة</b>
                    <div class="sig-line"></div>
                </div>
            </div>
        </div>
    </div>
</body>
</html>
"""


def render_salary_slip(payment_id, teacher_name, national_id, payment_date, salary_month, base_salary, bonus, deductions, net_amount, notes=""):
    notes_html = f'<p style="font-size:11px; color:#666; margin: 4px 0 0 0;"><b>ملاحظات:</b> {notes}</p>' if notes else ''
    
    logo_b64 = ui._logo_base64()
    logo_img_tag = f'<img src="data:image/png;base64,{logo_b64}" />' if logo_b64 else ""

    html = TEACHER_SLIP_TEMPLATE.format(
        logo_img_tag=logo_img_tag,
        payment_id=payment_id,
        teacher_name=teacher_name,
        national_id=national_id,
        payment_date=payment_date,
        salary_month=salary_month,
        base_salary=f"{float(base_salary):,.2f}",
        bonus=f"{float(bonus):,.2f}",
        deductions=f"{float(deductions):,.2f}",
        net_amount=f"{float(net_amount):,.2f}",
        notes_html=notes_html,
    )
    
    # Height set to 880px to accommodate both vouchers and cut line inside Streamlit's iframe
    components.html(html, height=880, scrolling=True)