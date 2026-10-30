"""
receipt.py — printable cash receipt with a real "طباعة" button and an
official letterhead (logo + kindergarten name) at the top.

Renders two copies on the same page (School Copy & Payer Copy) separated by a cut line.
"""

import streamlit.components.v1 as components

import ui

RECEIPT_TEMPLATE = """
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
    
    .receipt-box {{
        background: #FFFDF6;
        border: 2px dashed var(--gold);
        border-radius: 12px;
        padding: 14px 20px;
        font-size: 13px;
        line-height: 1.5;
        flex: 1;
        display: flex;
        flex-direction: column;
        justify-content: space-between;
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
    
    .receipt-header {{
        display: flex;
        justify-content: space-between;
        align-items: center;
        border-bottom: 1px dashed var(--gold);
        padding-bottom: 6px;
        margin-bottom: 10px;
    }}
    .receipt-header h3 {{
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
    .receipt-grid {{
        display: grid;
        grid-template-columns: 1fr 1fr;
        gap: 6px 16px;
    }}
    .receipt-row {{
        display: flex; 
        justify-content: flex-start; 
        align-items: center;
        gap: 8px;
        border-bottom: 1px dotted #e5e0c8; 
        padding: 4px 0;
        text-align: right;
    }}
    .receipt-row.full-width {{
        grid-column: span 2;
    }}
    .receipt-row span {{ 
        color: #7C8A7E; 
        white-space: nowrap; 
    }}
    .receipt-row b {{ 
        color: #1F2A22; 
        text-align: right;
    }}
    .receipt-row.balance {{ 
        border-bottom: none; 
        margin-top: 4px; 
        padding-top: 6px; 
        border-top: 1px solid #e5e0c8; 
    }}
    .receipt-row.balance b {{ color: #B4790C; font-size: 14px; }}
    
    .signatures-section {{
        display: flex;
        justify-content: space-between;
        align-items: flex-end;
        margin-top: 15px;
        padding-top: 10px;
        border-top: 1px dashed #d0c8b0;
    }}
    .sig-box {{
        text-align: center;
        width: 42%;
    }}
    .sig-title {{
        font-size: 12px;
        font-weight: 700;
        color: var(--primary-dark);
        margin-bottom: 25px;
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
        .receipt-box {{
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
        <div class="receipt-box">
            <div>
                <div class="letterhead">
                    {logo_img_tag}
                    <div class="letterhead-text">
                        <div class="lh-ar">روضة أحلام الطفولة</div>
                        <div class="lh-en">Childhood Dreams Kindergarten</div>
                    </div>
                </div>
                <div class="receipt-header">
                    <h3>🧾 وصل استلام نقدية</h3>
                    <span class="copy-badge">نسخة الروضة</span>
                </div>
                <div class="receipt-grid">
                    <div class="receipt-row"><span>رقم الوصل:</span><b>#{receipt_id}</b></div>
                    <div class="receipt-row"><span>التاريخ:</span><b>{date}</b></div>
                    <div class="receipt-row full-width"><span>اسم الطالب:</span><b>{student_name}</b></div>
                    <div class="receipt-row full-width"><span>وصلنا من السيد/ة:</span><b>{payer}</b></div>
                    <div class="receipt-row"><span>مبلغ وقدره:</span><b>{amount} شيكل</b></div>
                    <div class="receipt-row"><span>طريقة الدفع:</span><b>كاش 💵</b></div>
                    <div class="receipt-row full-width"><span>مقابل:</span><b>{reason}</b></div>
                    <div class="receipt-row full-width balance"><span>المبلغ المتبقي لهذه السنة:</span><b>{remaining} شيكل</b></div>
                </div>
            </div>

            <div class="signatures-section">
                <div class="sig-box">
                    <div class="sig-title">توقيع المستلم / مديرة الروضة</div>
                    <div class="sig-line"></div>
                </div>
                <div class="sig-box">
                    <div class="sig-title">توقيع دافع المبلغ</div>
                    <div class="sig-line"></div>
                </div>
            </div>
        </div>

        <!-- ==================== CUT LINE ==================== -->
        <div class="cut-line">✂️ خط القص</div>

        <!-- ==================== COPY 2: PAYER ==================== -->
        <div class="receipt-box">
            <div>
                <div class="letterhead">
                    {logo_img_tag}
                    <div class="letterhead-text">
                        <div class="lh-ar">روضة أحلام الطفولة</div>
                        <div class="lh-en">Childhood Dreams Kindergarten</div>
                    </div>
                </div>
                <div class="receipt-header">
                    <h3>🧾 وصل استلام نقدية</h3>
                    <span class="copy-badge">نسخة ولي الأمر</span>
                </div>
                <div class="receipt-grid">
                    <div class="receipt-row"><span>رقم الوصل:</span><b>#{receipt_id}</b></div>
                    <div class="receipt-row"><span>التاريخ:</span><b>{date}</b></div>
                    <div class="receipt-row full-width"><span>اسم الطالب:</span><b>{student_name}</b></div>
                    <div class="receipt-row full-width"><span>وصلنا من السيد/ة:</span><b>{payer}</b></div>
                    <div class="receipt-row"><span>مبلغ وقدره:</span><b>{amount} شيكل</b></div>
                    <div class="receipt-row"><span>طريقة الدفع:</span><b>كاش 💵</b></div>
                    <div class="receipt-row full-width"><span>مقابل:</span><b>{reason}</b></div>
                    <div class="receipt-row full-width balance"><span>المبلغ المتبقي لهذه السنة:</span><b>{remaining} شيكل</b></div>
                </div>
            </div>

            <div class="signatures-section">
                <div class="sig-box">
                    <div class="sig-title">توقيع المستلم / مديرة الروضة</div>
                    <div class="sig-line"></div>
                </div>
                <div class="sig-box">
                    <div class="sig-title">توقيع دافع المبلغ</div>
                    <div class="sig-line"></div>
                </div>
            </div>
        </div>

    </div>
</body>
</html>
"""


def render_receipt(receipt_id, date, student_name, payer, amount, reason, remaining, reason_other=""):
    reason_full = f"{reason} ({reason_other})" if reason_other else reason

    logo_b64 = ui._logo_base64()
    logo_img_tag = f'<img src="data:image/png;base64,{logo_b64}" />' if logo_b64 else ""

    html = RECEIPT_TEMPLATE.format(
        logo_img_tag=logo_img_tag,
        receipt_id=receipt_id,
        date=date,
        student_name=student_name,
        payer=payer,
        amount=amount,
        reason=reason_full,
        remaining=remaining,
    )
    components.html(html, height=1050, scrolling=True)