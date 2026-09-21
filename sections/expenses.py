"""
pages_expenses.py — Operational Expenses & Capital Assets Management (PostgreSQL/Supabase).
Supports full Paid/Debt status calculations, edit/delete actions, and asset scrapping.
"""

import streamlit as st
from datetime import datetime, date
import ui

EXPENSE_CATEGORIES = [
    "قرطاسية ومطبوعات", 
    "ضيافة وتنظيف", 
    "صيانة وإصلاحات", 
    "كهرباء ومياه واشتراكات", 
    "فعاليات وأنشطة", 
    "مصروفات أخرى"
]

ASSET_CATEGORIES = [
    "ألعاب وتجهيزات أطفال", 
    "أثاث ومفروشات", 
    "أجهزة إلكترونية وتقنية", 
    "معدات تحسين الروضة"
]

ASSET_CONDITIONS = ["ممتازة", "جيدة", "تحتاج صيانة", "تالفة/مستهلكة"]
PAYMENT_STATUSES = ["مدفوع بالكامل", "آجل / دين (غير مدفوع)", "مدفوع جزئياً"]


def render(conn):
    ui.section_header("📦", "المصروفات والأصول", "إدارة المصروفات التشغيلية والديون وجرد حالة الأصول")

    main_tab1, main_tab2 = st.tabs(["💰 المصروفات والديون التشغيلية", "🧸 الأصول والتجهيزات"])

    # ==================================================================
    # MAIN TAB 1: OPERATIONAL EXPENSES & DEBT MANAGEMENT
    # ==================================================================
    with main_tab1:
        sub_tab1, sub_tab2 = st.tabs(["📋 السجل والتسجيل", "⚙️ إدارة المصروفات والديون"])

        # --------------------------------------------------------------
        # SUB TAB 1: View Log & Add Expense
        # --------------------------------------------------------------
        with sub_tab1:
            col_list, col_form = st.columns([1.8, 1])

            with col_form:
                # --------------------------------------------------------------
                # داخل نموذج إضافة مصروف جديد (Add Expense Form)
                # --------------------------------------------------------------
                st.markdown("##### ➕ تسجيل مصروف جديد")
                with st.form("add_expense_form", clear_on_submit=True):
                    exp_date = st.date_input("تاريخ المصروف", value=date.today())
                    category = st.selectbox("بند المصروف", EXPENSE_CATEGORIES)
                    amount = st.number_input("إجمالي قيمة الفاتورة/المصروف (شيكل)", min_value=0.0, step=10.0, format="%.2f")
                    
                    pay_status = st.selectbox("حالة الدفع", PAYMENT_STATUSES)
                    
                    # تحكم ديناميكي بالمبلغ المدفوع بناءً على الحالة
                    if pay_status == "مدفوع بالكامل":
                        amount_paid = amount
                    elif pay_status == "آجل / دين (غير مدفوع)":
                        amount_paid = 0.0
                    else:  # مدفوع جزئياً
                        amount_paid = st.number_input(
                            "المبلغ المدفوع فعلياً (شيكل)", 
                            min_value=0.0, 
                            max_value=float(amount) if amount > 0 else 0.0, 
                            value=float(amount)/2 if amount > 0 else 0.0,
                            step=10.0, 
                            format="%.2f"
                        )

                    payee = st.text_input("المستلم / المورد (اختياري)")
                    method = st.selectbox("طريقة الدفع", ["كاش", "تحويل بنكي", "شيك"])
                    notes = st.text_area("ملاحظات / رقم الفاتورة", height=70)

                    if st.form_submit_button("حفظ المصروف", type="primary", use_container_width=True):
                        if amount <= 0:
                            st.error("⚠️ يرجى إدخال مبلغ أكبر من صفر.")
                        else:
                            # ضمان حتمي لتطابق القيمة قبل الحفظ في قاعدة البيانات
                            final_paid = amount if pay_status == "مدفوع بالكامل" else (0.0 if pay_status == "آجل / دين (غير مدفوع)" else amount_paid)
                            
                            with conn.cursor() as cur:
                                cur.execute("""
                                    INSERT INTO expenses (expense_date, category, amount, amount_paid, payment_status, payment_method, payee, notes)
                                    VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
                                """, (exp_date, category, amount, final_paid, pay_status, method, payee, notes))
                            st.success("✅ تم تسجيل المصروف بنجاح!")
                            st.rerun()

            with col_list:
                st.markdown("##### 📋 سجل المصروفات والالتزامات")
                df_exp = ui.df(conn, """
                    SELECT 
                        expense_id AS "الرقم", 
                        expense_date AS "التاريخ", 
                        category AS "البند", 
                        amount AS "الإجمالي", 
                        amount_paid AS "المدفوع",
                        (amount - amount_paid) AS "المتبقي (دين)",
                        payment_status AS "حالة الدفع",
                        payee AS "المورد", 
                        notes AS "ملاحظات" 
                    FROM expenses 
                    ORDER BY expense_date DESC
                """)
                if df_exp.empty:
                    ui.empty_state("لا توجد مصروفات مسجلة حتى الآن.")
                else:
                    st.dataframe(df_exp, use_container_width=True, hide_index=True)

        # --------------------------------------------------------------
        # SUB TAB 2: Edit & Settle Debts
        # --------------------------------------------------------------
        with sub_tab2:
            df_exp_manage = ui.df(conn, "SELECT * FROM expenses ORDER BY expense_date DESC")
            if df_exp_manage.empty:
                ui.empty_state("لا توجد مصروفات للتعديل أو الحذف.")
            else:
                exp_options = {
                    row["expense_id"]: f"#{row['expense_id']} - {row['category']} (المتبقي: {float(row['amount']) - float(row['amount_paid'])} ₪) - {row['payment_status']}" 
                    for _, row in df_exp_manage.iterrows()
                }
                selected_id = st.selectbox("اختر المصروف لتعديله، تسديد الدين، أو الحذف:", options=list(exp_options.keys()), format_func=lambda x: exp_options[x])

                exp_data = df_exp_manage[df_exp_manage["expense_id"] == selected_id].iloc[0]
                remaining_debt = float(exp_data["amount"]) - float(exp_data["amount_paid"])

                col_edit, col_del = st.columns([2, 1])
                with col_edit:
                    st.markdown("##### ✏️ تعديل البيانات وحالة السداد")
                    with st.form(f"edit_exp_{selected_id}"):
                        try:
                            curr_date = datetime.strptime(str(exp_data["expense_date"]), "%Y-%m-%d").date()
                        except Exception:
                            curr_date = date.today()

                        e_date = st.date_input("التاريخ", value=curr_date)
                        e_cat = st.selectbox("البند", EXPENSE_CATEGORIES, index=EXPENSE_CATEGORIES.index(exp_data["category"]) if exp_data["category"] in EXPENSE_CATEGORIES else 0)
                        e_amt = st.number_input("إجمالي الفاتورة", value=float(exp_data["amount"]), step=10.0, format="%.2f")
                        
                        curr_status_idx = PAYMENT_STATUSES.index(exp_data["payment_status"]) if exp_data["payment_status"] in PAYMENT_STATUSES else 0
                        e_status = st.selectbox("حالة الدفع", PAYMENT_STATUSES, index=curr_status_idx)
                        
                        e_paid = st.number_input("المبلغ المدفوع فعلياً", value=float(exp_data["amount_paid"]), min_value=0.0, max_value=float(e_amt), step=10.0, format="%.2f")
                        
                        e_payee = st.text_input("المورد", value=exp_data["payee"] or "")
                        e_notes = st.text_area("ملاحظات", value=exp_data["notes"] or "", height=70)

                        if st.form_submit_button("تحديث المصروف", type="primary", use_container_width=True):
                            # Auto fix paid amount if marked as fully paid
                            final_paid = e_amt if e_status == "مدفوع بالكامل" else e_paid
                            with conn.cursor() as cur:
                                cur.execute("""
                                    UPDATE expenses 
                                    SET expense_date = %s, category = %s, amount = %s, amount_paid = %s, 
                                        payment_status = %s, payee = %s, notes = %s
                                    WHERE expense_id = %s
                                """, (e_date, e_cat, e_amt, final_paid, e_status, e_payee, e_notes, selected_id))
                            st.success("✅ تم تحديث بيانات المصروف والدفع بنجاح!")
                            st.rerun()

                with col_del:
                    st.markdown("##### 🚨 إجراءات الديون والحذف")
                    with st.container(border=True):
                        if remaining_debt > 0:
                            st.info(f"💡 المتبقي كدين لهذا المصروف: **{remaining_debt:,.2f} ₪**")
                            if st.button("💸 تسديد الدين بالكامل الآن", key=f"settle_{selected_id}", use_container_width=True):
                                with conn.cursor() as cur:
                                    cur.execute("""
                                        UPDATE expenses 
                                        SET amount_paid = amount, payment_status = 'مدفوع بالكامل'
                                        WHERE expense_id = %s
                                    """, (selected_id,))
                                st.success("✅ تم تسديد الدين وتحديث حالة المصروف إلى (مدفوع بالكامل)!")
                                st.rerun()
                            st.write("---")

                        st.warning("حذف المصروف سينعكس فوراً على الحسابات واللوحة الرئيسية.")
                        if st.button("🗑️ حذف المصروف نهائياً", key=f"del_exp_{selected_id}", use_container_width=True):
                            with conn.cursor() as cur:
                                cur.execute("DELETE FROM expenses WHERE expense_id = %s", (selected_id,))
                            st.success("🗑️ تم الحذف بنجاح!")
                            st.rerun()

    # ==================================================================
    # MAIN TAB 2: CAPITAL ASSETS & TOYS
    # ==================================================================
    with main_tab2:
        sub_ast1, sub_ast2 = st.tabs(["🧸 جرد الأصول والإضافة", "⚙️ إدارة وتعديل الأصول والفرق"])

        # --------------------------------------------------------------
        # SUB TAB 1: View Assets & Add New
        # --------------------------------------------------------------
        with sub_ast1:
            col_ast_list, col_ast_form = st.columns([1.8, 1])

            with col_ast_form:
                st.markdown("##### ➕ إضافة أصل / ألعاب جديدة")
                with st.form("add_asset_form", clear_on_submit=True):
                    p_date = st.date_input("تاريخ الشراء", value=date.today())
                    item_name = st.text_input("اسم الأصل / اللعبة", placeholder="مثال: مجمع ألعاب بلاستيكي")
                    category = st.selectbox("فئة الأصل", ASSET_CATEGORIES)
                    qty = st.number_input("الكمية", min_value=1, value=1, step=1)
                    unit_cost = st.number_input("سعر القطعة (شيكل)", min_value=0.0, step=10.0, format="%.2f")
                    status = st.selectbox("الحالة", ASSET_CONDITIONS)
                    notes = st.text_area("ملاحظات / المورد", height=70)

                    if st.form_submit_button("تسجيل الأصل", type="primary", use_container_width=True):
                        if not item_name.strip() or unit_cost <= 0:
                            st.error("⚠️ يرجى التأكد من إدخال اسم الأصل والتكلفة.")
                        else:
                            total_cost = qty * unit_cost
                            with conn.cursor() as cur:
                                cur.execute("""
                                    INSERT INTO assets (purchase_date, item_name, category, quantity, unit_cost, total_cost, condition_status, notes)
                                    VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
                                """, (p_date, item_name, category, qty, unit_cost, total_cost, status, notes))
                            st.success("✅ تم تسجيل الأصل بنجاح!")
                            st.rerun()

            with col_ast_list:
                st.markdown("##### 🧸 جدول جرد الأصول والألعاب")
                df_ast = ui.df(conn, """
                    SELECT 
                        asset_id AS "الرقم", 
                        purchase_date AS "تاريخ الشراء", 
                        item_name AS "الاسم", 
                        category AS "الفئة", 
                        quantity AS "الكمية", 
                        unit_cost AS "سعر القطعة", 
                        total_cost AS "الإجمالي", 
                        condition_status AS "الحالة"
                    FROM assets 
                    ORDER BY purchase_date DESC
                """)
                if df_ast.empty:
                    ui.empty_state("لا توجد أصول أو ألعاب مسجلة حتى الآن.")
                else:
                    st.dataframe(df_ast, use_container_width=True, hide_index=True)

        # --------------------------------------------------------------
        # SUB TAB 2: Edit & Scrap Asset
        # --------------------------------------------------------------
        with sub_ast2:
            df_ast_manage = ui.df(conn, "SELECT * FROM assets ORDER BY purchase_date DESC")
            if df_ast_manage.empty:
                ui.empty_state("لا توجد أصول لإدارتها.")
            else:
                ast_options = {row["asset_id"]: f"#{row['asset_id']} - {row['item_name']} ({row['condition_status']})" for _, row in df_ast_manage.iterrows()}
                selected_ast_id = st.selectbox("اختر الأصل/اللعبة لإدارة الحالة أو التعديل:", options=list(ast_options.keys()), format_func=lambda x: ast_options[x])

                ast_data = df_ast_manage[df_ast_manage["asset_id"] == selected_ast_id].iloc[0]

                col_ast_edit, col_ast_act = st.columns([2, 1])
                with col_ast_edit:
                    st.markdown("##### ✏️ تعديل بيانات الأصل")
                    with st.form(f"edit_ast_{selected_ast_id}"):
                        e_name = st.text_input("اسم الأصل", value=ast_data["item_name"])
                        e_cat = st.selectbox("الفئة", ASSET_CATEGORIES, index=ASSET_CATEGORIES.index(ast_data["category"]) if ast_data["category"] in ASSET_CATEGORIES else 0)
                        e_qty = st.number_input("الكمية", min_value=1, value=int(ast_data["quantity"]))
                        e_ucost = st.number_input("سعر القطعة", value=float(ast_data["unit_cost"]), format="%.2f")
                        e_status = st.selectbox("الحالة", ASSET_CONDITIONS, index=ASSET_CONDITIONS.index(ast_data["condition_status"]) if ast_data["condition_status"] in ASSET_CONDITIONS else 0)
                        e_notes = st.text_area("ملاحظات", value=ast_data["notes"] or "", height=70)

                        if st.form_submit_button("تحديث الأصل", type="primary", use_container_width=True):
                            new_total = e_qty * e_ucost
                            with conn.cursor() as cur:
                                cur.execute("""
                                    UPDATE assets 
                                    SET item_name = %s, category = %s, quantity = %s, unit_cost = %s, 
                                        total_cost = %s, condition_status = %s, notes = %s 
                                    WHERE asset_id = %s
                                """, (e_name, e_cat, e_qty, e_ucost, new_total, e_status, e_notes, selected_ast_id))
                            st.success("✅ تم تحديث بيانات الأصل بنجاح!")
                            st.rerun()

                with col_ast_act:
                    st.markdown("##### 🚨 إتاحة والإتلاف")
                    with st.container(border=True):
                        if ast_data["condition_status"] != "تالفة/مستهلكة":
                            if st.button("🔥 تسجيل كـ (تالفة/مستهلكة)", key=f"scrap_{selected_ast_id}", use_container_width=True):
                                with conn.cursor() as cur:
                                    cur.execute("UPDATE assets SET condition_status = 'تالفة/مستهلكة' WHERE asset_id = %s", (selected_ast_id,))
                                st.warning("⚠️ تم تغيير الحالة إلى تالفة/مستهلكة.")
                                st.rerun()
                        else:
                            st.info("ℹ️ الأصل مسجل كـ تالف حالياً.")

                        st.write("---")
                        if st.button("🗑️ حذف الأصل نهائياً", key=f"del_ast_{selected_ast_id}", use_container_width=True):
                            with conn.cursor() as cur:
                                cur.execute("DELETE FROM assets WHERE asset_id = %s", (selected_ast_id,))
                            st.success("🗑️ تم الحذف بنجاح!")
                            st.rerun()