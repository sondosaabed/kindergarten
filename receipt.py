"""
receipt.py — printable cash receipt with a real "طباعة" button.

Streamlit runs inside the browser tab, so a plain button can't print just
one part of the page. The trick: render the receipt inside its own
<iframe> (via components.html) with a print button that calls
window.print() *from inside that iframe*. Most modern browsers then print
only the iframe's own content, which gives a clean one-click receipt
print instead of asking the manager to use Ctrl/Cmd+P on the whole app.
"""

import streamlit.components.v1 as components


RECEIPT_TEMPLATE = """
<!DOCTYPE html>
<html lang="ar" dir="rtl">
<head>
<meta charset="utf-8">
<style>
    :root {{
        --primary-dark:#163D22;
        --gold:#D7A431;
    }}
    * {{ box-sizing: border-box; }}
    body {{
        font-family: 'Segoe UI', Tahoma, sans-serif;
        direction: rtl;
        text-align: right;
        margin: 0;
        padding: 14px;
        background: #FAF9F5;
    }}
    .receipt-box{{
        background: #FFFDF6;
        border: 2px dashed var(--gold);
        border-radius: 14px;
        padding: 20px 22px;
        font-size: 15px;
        line-height: 1.9;
        max-width: 460px;
        margin: 0 auto;
    }}
    .receipt-box h3{{
        margin: 0 0 10px 0;
        color: var(--primary-dark);
        font-size: 17px;
        text-align: center;
    }}
    .receipt-row{{
        display:flex; justify-content:space-between; gap: 10px;
        border-bottom:1px dotted #e5e0c8; padding:5px 0;
    }}
    .receipt-row span{{ color:#7C8A7E; }}
    .receipt-row b{{ color:#1F2A22; }}
    .print-btn{{
        display:block;
        width: 100%;
        max-width: 460px;
        margin: 14px auto 0 auto;
        background: var(--primary-dark);
        color: #fff;
        border: none;
        border-radius: 10px;
        padding: 12px 0;
        font-size: 15px;
        font-weight: 700;
        cursor: pointer;
        font-family: inherit;
    }}
    .print-btn:hover {{ opacity: .9; }}
    @media print {{
        .print-btn {{ display: none; }}
        body {{ background: #fff; padding: 0; }}
    }}
</style>
</head>
<body>
    <div class="receipt-box">
        <h3>🧾 وصل استلام نقدية — روضة مؤسسة شباب البيرة</h3>
        <div class="receipt-row"><span>رقم الوصل</span><b>#{receipt_id}</b></div>
        <div class="receipt-row"><span>التاريخ</span><b>{date}</b></div>
        <div class="receipt-row"><span>اسم الطالب</span><b>{student_name}</b></div>
        <div class="receipt-row"><span>وصلنا من السيد/ة</span><b>{payer}</b></div>
        <div class="receipt-row"><span>مبلغ وقدره</span><b>{amount} شيكل/دينار</b></div>
        <div class="receipt-row"><span>مقابل</span><b>{reason}</b></div>
        <div class="receipt-row"><span>طريقة الدفع</span><b>كاش 💵</b></div>
    </div>
    <button class="print-btn" onclick="window.print()">🖨️ طباعة الوصل</button>
</body>
</html>
"""


def render_receipt(receipt_id, date, student_name, payer, amount, reason, reason_other=""):
    reason_full = f"{reason} ({reason_other})" if reason_other else reason
    html = RECEIPT_TEMPLATE.format(
        receipt_id=receipt_id,
        date=date,
        student_name=student_name,
        payer=payer,
        amount=amount,
        reason=reason_full,
    )
    components.html(html, height=430, scrolling=True)
