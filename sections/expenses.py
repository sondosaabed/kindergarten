"""
expenses.py — Module for managing operational expenses and capital assets/toys.
"""

import streamlit as st
import pandas as pd
from datetime import date
import ui

EXPENSE_CATEGORIES = ["قرطاسية ومطبوعات", "ضيافة وتنظيف", "صيانة وإصلاحات", "كهرباء ومياه واشتراكات", "فعاليات وأنشطة", "مصروفات أخرى"]
ASSET_CATEGORIES = ["ألعاب وتجهيزات أطفال", "أثاث ومفروشات", "أجهزة إلكترونية وتقنية", "معدات تحسين الروضة"]
ASSET_CONDITIONS = ["ممتازة", "جيدة", "تحتاج صيانة", "تالفة/مستهلكة"]


def render(conn):
    ui.section_header("📦", "المصروفات والأصول", "إدارة المصروفات التشغيلية وشراء الألعاب والتجهيزات")

    tab1, tab2, tab3 = st.tabs(["💰 المصروفات التشغيلية", "🧸 الأصول والألعاب", "📊 الملخص والتقارير"])

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
                method = st.selectbox("طريقة الدفع", ["نقداً", "تحويل بنكي", "شيك"])
                notes = st.text_area("ملاحظات / رقم الفاتورة", height=70)

                submit = st.form_submit_button("حفظ المصروف", type="primary", use_container_width=True)

                if submit:
                    if amount <= 0:
                        st.error("⚠️ يرجى إدخال مبلغ أكبر من صفر.")
                    else:
                        cur = conn.cursor()
                        cur.execute("""
                            INSERT INTO expenses (expense_date, category, amount, payment_method, payee, notes)
                            VALUES (?, ?, ?, ?, ?, ?)
                        """, (str(exp_date), category, amount, method, payee, notes))
                        conn.commit()
                        cur.close()
                        st.success("✅ تم تسجيل المصروف بنجاح!")
                        st.rerun()

        with col_list:
            st.markdown("##### 📋 سجل المصروفات التشغيلية")
            df_exp = ui.df(conn, "SELECT id, expense_date AS 'التاريخ', category AS 'البند', amount AS 'المبلغ', payment_method AS 'الطريقة', payee AS 'المورد', notes AS 'ملاحظات' FROM expenses ORDER BY expense_date DESC")

            if df_exp.empty:
                ui.empty_state("لا توجد مصروفات مسجلة حتى الآن.")
            else:
                st.dataframe(df_exp, use_container_width=True, hide_index=True)

    # ------------------------------------------------------------------
    # TAB 2: CAPITAL ASSETS & TOYS
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
                status = st.selectbox("الحالة", ASSET_CONDITIONS)
                notes = st.text_area("ملاحظات / المورد", height=70)

                submit_asset = st.form_submit_button("تسجيل الأصل", type="primary", use_container_width=True)

                if submit_asset:
                    if not item_name.strip():
                        st.error("⚠️ يرجى إدخال اسم الأصل أو اللعبة.")
                    elif unit_cost <= 0:
                        st.error("⚠️ يرجى إدخال تكلفة التجهيزات.")
                    else:
                        total_cost = qty * unit_cost
                        cur = conn.cursor()
                        cur.execute("""
                            INSERT INTO assets (purchase_date, item_name, category, quantity, unit_cost, total_cost, condition_status, notes)
                            VALUES (?, ?, ?, ?, ?, ?, ?, ?)
                        """, (str(p_date), item_name, category, qty, unit_cost, total_cost, status, notes))
                        conn.commit()
                        cur.close()
                        st.success("✅ تم تسجيل الأصل بنجاح!")
                        st.rerun()

        with col_list:
            st.markdown("##### 🧸 جرد الأصول والألعاب")
            df_assets = ui.df(conn, "SELECT id, purchase_date AS 'تاريخ الشراء', item_name AS 'الاسم', category AS 'الفئة', quantity AS 'الكمية', unit_cost AS 'سعر القطعة', total_cost AS 'الإجمالي', condition_status AS 'الحالة' FROM assets ORDER BY purchase_date DESC")

            if df_assets.empty:
                ui.empty_state("لا توجد أصول أو ألعاب مسجلة حتى الآن.")
            else:
                st.dataframe(df_assets, use_container_width=True, hide_index=True)

    # ------------------------------------------------------------------
    # TAB 3: FINANCIAL SUMMARY
    # ------------------------------------------------------------------
    with tab3:
        total_exp = ui.df(conn, "SELECT SUM(amount) AS val FROM expenses").iloc[0]['val'] or 0.0
        total_assets = ui.df(conn, "SELECT SUM(total_cost) AS val FROM assets").iloc[0]['val'] or 0.0

        c1, c2, c3 = st.columns(3)
        ui.kpi(c1, "💸", "إجمالي المصروفات التشغيلية", f"{total_exp:,.2f} ₪")
        ui.kpi(c2, "🧩", "إجمالي الاستثمار في الأصول الألعاب", f"{total_assets:,.2f} ₪")
        ui.kpi(c3, "📊", "المجموع الكلي للإنفاق", f"{(total_exp + total_assets):,.2f} ₪")