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
    html, body {{
        height: 100%;
        margin: 0;
        padding: 0;
        background: #FAF9F5;
        direction: rtl;
        text-align: right;
    }}
    .page-container {{
        max-width: 720px;
        margin: 0 auto;
        padding: 10px;
        display: flex;
        flex-direction: column;
        min-height: 100vh;
    }}
    .letterhead {{
        display: flex; 
        align-items: center; 
        justify-content: center; 
        gap: 12px;
        margin-bottom: 8px;
    }}
    .letterhead img {{ 
        width: 46px; 
        height: 46px; 
        border-radius: 50%; 
        flex-shrink: 0; 
    }}
    .letterhead-text {{ text-align: center; }}
    .letterhead-text .lh-ar {{ font-size: 15px; font-weight: 800; color: var(--primary-dark); }}
    .letterhead-text .lh-en {{ font-size: 11px; color: #7C8A7E; }}
    
    .voucher-box {{
        background: #FFFDF6;
        border: 2px dashed var(--gold);
        border-radius: 12px;
        padding: 14px 20px;
        font-size: 12px;
        line-height: 1.5;
        flex: 1;
        display: flex;
        flex-direction: column;
        justify-content: space-between;
    }}
    .voucher-header {{
        display: flex;
        justify-content: space-between;
        align-items: center;
        border-bottom: 1px dashed var(--gold);
        padding-bottom: 6px;
        margin-bottom: 10px;
    }}
    .voucher-header h3 {{
        margin: 0;
        color: var(--primary-dark);
        font-size: 16px;
    }}
    .copy-badge {{
        background: var(--primary-dark);
        color: #FFFDF6;
        font-size: 11px;
        font-weight: 700;
        padding: 2px 10px;
        border-radius: 6px;
    }}
    .voucher-grid {{
        display: grid;
        grid-template-columns: 1fr 1fr;
        gap: 6px 16px;
        margin-bottom: 8px;
    }}
    .voucher-row {{
        display: flex; 
        justify-content: flex-start; 
        align-items: center;
        gap: 8px;
        border-bottom: 1px dotted #e5e0c8; 
        padding: 4px 0;
        text-align: right;
    }}
    .voucher-row.full-width {{
        grid-column: span 2;
    }}
    .voucher-row span {{ 
        color: #7C8A7E; 
        white-space: nowrap; 
    }}
    .voucher-row b {{ 
        color: #1F2A22; 
        text-align: right;
    }}
    .details-table {{
        width: 100%;
        border-collapse: collapse;
        margin: 6px 0;
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
        font-size: 13px;
        font-weight: 800;
        color: #15803D;
    }}
    .signatures {{
        display: flex;
        justify-content: space-between;
        align-items: flex-end;
        margin-top: 10px;
        padding-top: 8px;
        border-top: 1px dashed #d0c8b0;
        text-align: center;
        font-size: 11px;
    }}
    .sig-block {{
        width: 42%;
    }}
    .sig-title {{
        font-size: 12px;
        font-weight: 700;
        color: var(--primary-dark);
        margin-bottom: 20px;
    }}
    .sig-line {{
        border-bottom: 1px dotted #7C8A7E;
        width: 100%;
    }}
    .cut-line {{
        display: flex;
        align-items: center;
        text-align: center;
        margin: 8px 0;
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
        max-width: 720px;
        margin: 0 auto 10px auto;
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
        html, body {{ 
            background: #fff; 
            padding: 0; 
            margin: 0;
            height: 100%;
        }}
        .page-container {{ 
            max-width: 100%; 
            height: 100vh;
            padding: 0;
            box-sizing: border-box;
            justify-content: space-between;
        }}
        .voucher-box {{
            height: 48%;
            flex: none;
            border-style: dashed;
        }}
        .cut-line {{
            margin: 4px 0;
            height: 2%;
        }}
        @page {{
            size: A4 portrait;
            margin: 8mm;
        }}
    }}
</style>
</head>
<body>
    <button class="print-btn" onclick="window.print()">🖨️ طباعة النسختين (A4)</button>
    <div class="page-container">

        <!-- ==================== COPY 1: SCHOOL ==================== -->
        <div class="voucher-box">
            <div>
                <div class="letterhead">
                    {logo_img_tag}
                    <div class="letterhead-text">
                        <div class="lh-ar">روضة أحلام الطفولة</div>
                        <div class="lh-en">Childhood Dreams Kindergarten</div>
                    </div>
                </div>

                <div class="voucher-header">
                    <h3>🧾 قسيمة استلام راتب شهر: {salary_month}</h3>
                    <span class="copy-badge">نسخة الروضة</span>
                </div>

                <div class="voucher-grid">
                    <div class="voucher-row"><span>رقم القسيمة:</span><b>#{payment_id}</b></div>
                    <div class="voucher-row"><span>تاريخ الصرف:</span><b>{payment_date}</b></div>
                    <div class="voucher-row full-width"><span>اسم المعلم/ة:</span><b>{teacher_name}</b></div>
                    <div class="voucher-row full-width"><span>رقم الهوية:</span><b>{national_id}</b></div>
                </div>

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
            </div>

            <div class="signatures">
                <div class="sig-block">
                    <div class="sig-title">توقيع المعلم/ة المستلم/ة</div>
                    <div class="sig-line"></div>
                </div>
                <div class="sig-block">
                    <div class="sig-title">توقيع ودمغ الإدارة</div>
                    <div class="sig-line"></div>
                </div>
            </div>
        </div>

        <!-- ==================== CUT LINE ==================== -->
        <div class="cut-line">✂️ خط القص</div>

        <!-- ==================== COPY 2: TEACHER ==================== -->
        <div class="voucher-box">
            <div>
                <div class="letterhead">
                    {logo_img_tag}
                    <div class="letterhead-text">
                        <div class="lh-ar">روضة أحلام الطفولة</div>
                        <div class="lh-en">Childhood Dreams Kindergarten</div>
                    </div>
                </div>

                <div class="voucher-header">
                    <h3>🧾 قسيمة استلام راتب شهر: {salary_month}</h3>
                    <span class="copy-badge">نسخة المعلم/ة</span>
                </div>

                <div class="voucher-grid">
                    <div class="voucher-row"><span>رقم القسيمة:</span><b>#{payment_id}</b></div>
                    <div class="voucher-row"><span>تاريخ الصرف:</span><b>{payment_date}</b></div>
                    <div class="voucher-row full-width"><span>اسم المعلم/ة:</span><b>{teacher_name}</b></div>
                    <div class="voucher-row full-width"><span>رقم الهوية:</span><b>{national_id}</b></div>
                </div>

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
            </div>

            <div class="signatures">
                <div class="sig-block">
                    <div class="sig-title">توقيع المعلم/ة المستلم/ة</div>
                    <div class="sig-line"></div>
                </div>
                <div class="sig-block">
                    <div class="sig-title">توقيع ودمغ الإدارة</div>
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
    
    components.html(html, height=1050, scrolling=True)