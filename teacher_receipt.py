"""
teacher_receipt.py — Printable Teacher Salary Slip Voucher
Renders a print-ready salary voucher for teachers.
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
        padding: 15px;
        background: #FAF9F5;
    }}
    .page-container {{
        max-width: 580px;
        margin: 0 auto;
    }}
    .letterhead {{
        display: flex; 
        align-items: center; 
        justify-content: center; 
        gap: 12px;
        margin-bottom: 8px;
    }}
    .letterhead img {{ 
        width: 48px; 
        height: 48px; 
        border-radius: 50%; 
        flex-shrink: 0; 
    }}
    .letterhead-text {{ text-align: center; }}
    .letterhead-text .lh-ar {{ font-size: 16px; font-weight: 800; color: var(--primary-dark); }}
    .letterhead-text .lh-en {{ font-size: 11px; color: #7C8A7E; }}
    
    .voucher-box {{
        background: #FFFDF6;
        border: 2px solid var(--primary-dark);
        border-radius: 12px;
        padding: 18px 22px;
        font-size: 13px;
        line-height: 1.6;
        box-shadow: 0 4px 6px rgba(0,0,0,0.02);
    }}
    .voucher-header {{
        display: flex;
        justify-content: space-between;
        align-items: center;
        border-bottom: 2px dashed var(--gold);
        padding-bottom: 8px;
        margin-bottom: 12px;
    }}
    .voucher-header h3 {{
        margin: 0;
        color: var(--primary-dark);
        font-size: 17px;
    }}
    .badge {{
        background: var(--primary-dark);
        color: #FFFDF6;
        font-size: 11px;
        font-weight: 700;
        padding: 3px 10px;
        border-radius: 6px;
    }}
    .details-table {{
        width: 100%;
        border-collapse: collapse;
        margin: 12px 0;
    }}
    .details-table td, .details-table th {{
        padding: 8px;
        border: 1px solid #e5e0c8;
    }}
    .details-table th {{
        background: #F4EFE0;
        color: var(--primary-dark);
        font-weight: 700;
    }}
    .amount-highlight {{
        font-size: 16px;
        font-weight: 800;
        color: #15803D;
    }}
    .signatures {{
        display: flex;
        justify-content: space-between;
        margin-top: 30px;
        padding-top: 15px;
        border-top: 1px solid #e5e0c8;
        text-align: center;
    }}
    .sig-block {{
        width: 45%;
    }}
    .sig-line {{
        margin-top: 35px;
        border-bottom: 1px dashed #7C8A7E;
    }}
    .print-btn {{
        display: block;
        width: 100%;
        max-width: 580px;
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
            size: A5 landscape;
            margin: 8mm;
        }}
    }}
</style>
</head>
<body>
    <div class="page-container">
        <button class="print-btn" onclick="window.print()">🖨️ طباعة قسيمة الراتب (A5 / A4)</button>

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
                <span class="badge">رقم القسيمة #{payment_id}</span>
            </div>

            <table class="details-table">
                <tr>
                    <td><b>اسم المعلم/ة:</b> {teacher_name}</td>
                    <td><b>رقم الهوية:</b> {national_id}</td>
                </tr>
                <tr>
                    <td><b>تاريخ الصرف:</b> {payment_date}</td>
                    <td><b>طريقة الدفع:</b> نقداً (كاش) 💵</td>
                </tr>
            </table>

            <table class="details-table">
                <thead>
                    <tr>
                        <th>الراتب الأساسي</th>
                        <th>المكافآت / الإضافات</th>
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
    notes_html = f'<p style="font-size:11px; color:#666;"><b>ملاحظات:</b> {notes}</p>' if notes else ''
    
    logo_b64 = ui._logo_base64()
    logo_img_tag = f'<img src="data:image/png;base64,{logo_b64}" />' if logo_b64 else ""

    html = TEACHER_SLIP_TEMPLATE.format(
        logo_img_tag=logo_img_tag,
        payment_id=payment_id,
        teacher_name=teacher_name,
        national_id=national_id,
        payment_date=payment_date,
        salary_month=salary_month,
        base_salary=ui.format_money(base_salary) if hasattr(ui, 'format_money') else f"{base_salary:,.2f}",
        bonus=f"{bonus:,.2f}",
        deductions=f"{deductions:,.2f}",
        net_amount=f"{net_amount:,.2f}",
        notes_html=notes_html,
    )
    
    components.html(html, height=520, scrolling=True)