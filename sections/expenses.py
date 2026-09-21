"""
pages_expenses.py — إدارة المصروفات التشغيلية والأصول مع دعم التعديل، الحذف، والإتلاف (PostgreSQL/Supabase).
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


def render(conn):
    ui.section_header("📦", "المصروفات والأصول", "إدارة المصروفات التشغيلية وجرد وحالة الأصول والألعاب")

    tab1, tab2 = st.tabs(["💰 المصروفات التشغيلية", "🧸 الأصول والتجهيزات"])

    # ------------------------------------------------------------------
    # TAB 1: OPERATIONAL EXPENSES
    # ------------------------------------------------------------------
    with tab1:
        col_form, col_list = st.columns([1, 1.8])

        with col_form:
            st.markdown("##### ➕ تسجيل مصروف جديد")
            with st.form("add_expense_form", clear_on_submit=True):
                exp_date = st.date_input("تاريخ المصروف", value=date.today())
                category = st.selectbox("بند المصروف", EXPENSE_CATEGORIES)
                amount = st.number_input("المبلغ (شيكل)", min_value=0.0, step=10.0, format="%.2f")
                payee = st.text_input("المستلم / المورد (اختياري)")
                method = st.selectbox("طريقة الدفع", ["كاش", "تحويل بنكي", "شيك"])
                notes = st.text_area("ملاحظات / رقم الفاتورة", height=70)

                submit = st.form_submit_button("حفظ المصروف", type="primary", use_container_width=True)

                if submit:
                    if amount <= 0:
                        st.error("⚠️ يرجى إدخال مبلغ أكبر من صفر.")
                    else:
                        with conn.cursor() as cur:
                            cur.execute("""
                                INSERT INTO expenses (expense_date, category, amount, payment_method, payee, notes)
                                VALUES (%s, %s, %s, %s, %s, %s)
                            """, (exp_date, category, amount, method, payee, notes))
                        st.success("✅ تم تسجيل المصروف بنجاح!")
                        st.rerun()

        with col_list:
            st.markdown("##### 📋 سجل المصروفات التشغيلية")
            df_exp = ui.df(
                conn, 
                """
                SELECT 
                    expense_id AS "الرقم", 
                    expense_date AS "التاريخ", 
                    category AS "البند", 
                    amount AS "المبلغ", 
                    payment_method AS "الطريقة", 
                    payee AS "المورد", 
                    notes AS "ملاحظات" 
                FROM expenses 
                ORDER BY expense_date DESC
                """
            )

            if df_exp.empty:
                ui.empty_state("لا توجد مصروفات مسجلة حتى الآن.")
            else:
                st.dataframe(df_exp, use_container_width=True, hide_index=True)

                # ------------------------------------------------------
                # إدارة المصروفات (تعديل / حذف)
                # ------------------------------------------------------
                st.markdown("---")
                st.markdown("##### ⚙️ إدارة أو حذف مصروف مسجل")
                exp_ids = df_exp["الرقم"].tolist()
                selected_exp_id = st.selectbox("اختر رقم المصروف للتعديل أو الحذف:", exp_ids, key="sb_exp")

                if selected_exp_id:
                    exp_row = df_exp[df_exp["الرقم"] == selected_exp_id].iloc[0]

                    with st.expander(f"✏️ تعديل / حذف المصروف رقم #{selected_exp_id}", expanded=True):
                        c_edit, c_del = st.columns([2, 1])

                        with c_edit:
                            with st.form(f"edit_exp_{selected_exp_id}"):
                                try:
                                    curr_date = datetime.strptime(str(exp_row["التاريخ"]), "%Y-%m-%d").date()
                                except Exception:
                                    curr_date = date.today()

                                edit_date = st.date_input("التاريخ", value=curr_date)
                                edit_cat = st.selectbox("البند", EXPENSE_CATEGORIES, index=EXPENSE_CATEGORIES.index(exp_row["البند"]) if exp_row["البند"] in EXPENSE_CATEGORIES else 0)
                                edit_amt = st.number_input("المبلغ", value=float(exp_row["المبلغ"]), step=10.0, format="%.2f")
                                edit_payee = st.text_input("المورد", value=exp_row["المورد"] or "")
                                edit_notes = st.text_area("ملاحظات", value=exp_row["ملاحظات"] or "", height=60)

                                if st.form_submit_button("تحديث البيانات", type="primary", use_container_width=True):
                                    with conn.cursor() as cur:
                                        cur.execute("""
                                            UPDATE expenses 
                                            SET expense_date = %s, category = %s, amount = %s, payee = %s, notes = %s
                                            WHERE expense_id = %s
                                        """, (edit_date, edit_cat, edit_amt, edit_payee, edit_notes, selected_exp_id))
                                    st.success("✅ تم تحديث بيانات المصروف!")
                                    st.rerun()

                        with c_del:
                            st.warning("⚠️ منطقة الخطر")
                            st.write("حذف هذا المصروف سينعكس فوراً على التقارير واللوحة الرئيسية.")
                            if st.button("🗑️ حذف المصروف النهائي", key=f"del_exp_{selected_exp_id}", use_container_width=True):
                                with conn.cursor() as cur:
                                    cur.execute("DELETE FROM expenses WHERE expense_id = %s", (selected_exp_id,))
                                st.success("🗑️ تم حذف المصروف بنجاح!")
                                st.rerun()

    # ------------------------------------------------------------------
    # TAB 2: CAPITAL ASSETS & TOYS (WITH DISPOSAL & EDIT FUNCTIONALITY)
    # ------------------------------------------------------------------
    with tab2:
        col_form, col_list = st.columns([1, 1.8])

        with col_form:
            st.markdown("##### ➕ إضافة أصل / ألعاب جديدة")
            with st.form("add_asset_form", clear_on_submit=True):
                p_date = st.date_input("تاريخ الشراء", value=date.today())
                item_name = st.text_input("اسم الأصل / اللعبة", placeholder="مثال: مجمع ألعاب بلاستيكي خارجي")
                category = st.selectbox("فئة الأصل", ASSET_CATEGORIES)
                qty = st.number_input("الكمية", min_value=1, value=1, step=1)
                unit_cost = st.number_input("سعر القطعة (شيكل)", min_value=0.0, step=10.0, format="%.2f")
                status = st.selectbox("الحالة الأولية", ASSET_CONDITIONS)
                notes = st.text_area("ملاحظات / المورد", height=70)

                submit_asset = st.form_submit_button("تسجيل الأصل", type="primary", use_container_width=True)

                if submit_asset:
                    if not item_name.strip():
                        st.error("⚠️ يرجى إدخال اسم الأصل أو اللعبة.")
                    elif unit_cost <= 0:
                        st.error("⚠️ يرجى إدخال تكلفة التجهيزات.")
                    else:
                        total_cost = qty * unit_cost
                        with conn.cursor() as cur:
                            cur.execute("""
                                INSERT INTO assets (purchase_date, item_name, category, quantity, unit_cost, total_cost, condition_status, notes)
                                VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
                            """, (p_date, item_name, category, qty, unit_cost, total_cost, status, notes))
                        st.success("✅ تم تسجيل الأصل بنجاح!")
                        st.rerun()

        with col_list:
            st.markdown("##### 🧸 جرد الأصول والألعاب")
            df_assets = ui.df(
                conn, 
                """
                SELECT 
                    asset_id AS "الرقم", 
                    purchase_date AS "تاريخ الشراء", 
                    item_name AS "الاسم", 
                    category AS "الفئة", 
                    quantity AS "الكمية", 
                    unit_cost AS "سعر القطعة", 
                    total_cost AS "الإجمالي", 
                    condition_status AS "الحالة",
                    notes AS "ملاحظات"
                FROM assets 
                ORDER BY purchase_date DESC
                """
            )

            if df_assets.empty:
                ui.empty_state("لا توجد أصول أو ألعاب مسجلة حتى الآن.")
            else:
                st.dataframe(df_assets, use_container_width=True, hide_index=True)

                # ------------------------------------------------------
                # إدارة وتحديد حالة الأصل (تعديل / إتلاف / حذف)
                # ------------------------------------------------------
                st.markdown("---")
                st.markdown("##### ⚙️ إدارة الأصل، تغيير الحالة، أو الإتلاف")
                asset_ids = df_assets["الرقم"].tolist()
                selected_asset_id = st.selectbox("اختر رقم الأصل/اللعبة للتحكم:", asset_ids, key="sb_ast")

                if selected_asset_id:
                    ast_row = df_assets[df_assets["الرقم"] == selected_asset_id].iloc[0]

                    with st.expander(f"⚙️ إدارة الأصل: {ast_row['الاسم']} (رقم #{selected_asset_id})", expanded=True):
                        c_ast_edit, c_ast_actions = st.columns([1.8, 1])

                        # Edit asset general details
                        with c_ast_edit:
                            with st.form(f"edit_ast_{selected_asset_id}"):
                                edit_ast_name = st.text_input("اسم الأصل", value=ast_row["الاسم"])
                                edit_ast_cat = st.selectbox("الفئة", ASSET_CATEGORIES, index=ASSET_CATEGORIES.index(ast_row["الفئة"]) if ast_row["الفئة"] in ASSET_CATEGORIES else 0)
                                edit_ast_qty = st.number_input("الكمية", min_value=1, value=int(ast_row["الكمية"]))
                                edit_ast_ucost = st.number_input("سعر القطعة", value=float(ast_row["سعر القطعة"]), format="%.2f")
                                edit_ast_status = st.selectbox("الحالة التشغيلية", ASSET_CONDITIONS, index=ASSET_CONDITIONS.index(ast_row["الحالة"]) if ast_row["الحالة"] in ASSET_CONDITIONS else 0)
                                edit_ast_notes = st.text_area("سبب التعديل / ملاحظات الصيانة", value=ast_row["ملاحظات"] or "", height=60)

                                if st.form_submit_button("تحديث بيانات الأصل", type="primary", use_container_width=True):
                                    new_total = edit_ast_qty * edit_ast_ucost
                                    with conn.cursor() as cur:
                                        cur.execute("""
                                            UPDATE assets
                                            SET item_name = %s, category = %s, quantity = %s, unit_cost = %s, 
                                                total_cost = %s, condition_status = %s, notes = %s
                                            WHERE asset_id = %s
                                        """, (edit_ast_name, edit_ast_cat, edit_ast_qty, edit_ast_ucost, new_total, edit_ast_status, edit_ast_notes, selected_asset_id))
                                    st.success("✅ تم تحديث بيانات الأصل بنجاح!")
                                    st.rerun()

                        # Fast Quick Actions (Mark as Scrapped / Destroyed OR Delete)
                        with c_ast_actions:
                            st.markdown("##### 🚨 إجراءات سريعة")
                            
                            # Fast Scrap Action
                            if ast_row["الحالة"] != "تالفة/مستهلكة":
                                if st.button("🔥 تسجيل كأصل مكسور/مُتلف", key=f"scrap_{selected_asset_id}", use_container_width=True):
                                    with conn.cursor() as cur:
                                        cur.execute("""
                                            UPDATE assets 
                                            SET condition_status = 'تالفة/مستهلكة' 
                                            WHERE asset_id = %s
                                        """, (selected_asset_id,))
                                    st.warning("⚠️ تم تعديل حالة الأصل إلى (تالفة/مستهلكة).")
                                    st.rerun()
                            else:
                                st.info("ℹ️ هذا الأصل مكسور/مُتلف حالياً.")

                            st.write("---")

                            # Permanent Delete Action
                            if st.button("🗑️ حذف الأصل نهائياً", key=f"del_ast_{selected_asset_id}", use_container_width=True):
                                with conn.cursor() as cur:
                                    cur.execute("DELETE FROM assets WHERE asset_id = %s", (selected_asset_id,))
                                st.success("🗑️ تم حذف الأصل من السجلات بنجاح!")
                                st.rerun()