# نظام إدارة الروضة

## 🗂️ هيكلة المشروع (وحدات مستقلة)
```
app.py              → نقطة التشغيل فقط (إعداد الصفحة + تسجيل الدخول + التوجيه بين الشاشات)
sidebar.py           → القائمة الجانبية (الشعار، الإحصائيات السريعة، أزرار التنقل)
auth.py               → شاشة تسجيل الدخول
ui.py                  → عناصر مشتركة (بطاقات، عناوين الأقسام، الشعار...)
receipt.py            → وصل الدفع القابل للطباعة بضغطة واحدة
style.py               → التنسيق العام (الألوان، الاستجابة للجوال)
db.py / helpers.py     → قاعدة البيانات والمنطق المشترك (لا تُعدَّل عادة)

sections/
    dashboard.py        → لوحة التحكم
    students.py          → الطلاب
    parents.py            → أولياء الأمور
    teachers.py            → المعلمون
    classes.py              → الصفوف
    academic_years.py        → السنوات الدراسية
    registration.py           → التسجيل
    payments.py                → الدفعات المالية
    reports.py                  → التقارير
```

د
## التشغيل
1. Python 3.9+
2. ```
   pip install -r requirements.txt
   ```
3. تأكد من وجود كل الملفات والمجلدات التالية بجانب بعضها: `app.py`, `db.py`, `helpers.py`, `style.py`, `auth.py`, `ui.py`, `sidebar.py`, `receipt.py`, مجلد `sections/`, `school_data.db`, مجلد `assets/` (فيه `logo.png`)، ومجلد `.streamlit` (فيه `secrets.toml`)
4. ```
   streamlit run app.py
   ```

- **الترتيب المقترح عند أول استخدام:** المعلمون ← الصفوف ← السنة الدراسية ← أولياء الأمور ← الطلاب ← التسجيل ← الدفعات المالية.
- حالة التسجيل (مسجل جديد / منتظم) تتحدث تلقائياً بمجرد تسجيل دفعة "رسوم تسجيل".
- زر تحميل Excel متاح في شاشة التقارير.


<img width="1287" height="895" alt="image" src="https://github.com/user-attachments/assets/75c9a208-c805-48d4-9de8-1a1c8b434a82" />



<img width="1910" height="930" alt="image" src="https://github.com/user-attachments/assets/ac06a2f2-b60c-4e62-a93d-4bc50670cfeb" />



<img width="1912" height="922" alt="image" src="https://github.com/user-attachments/assets/b68391db-4ab4-4861-8fc0-efdbdc23055e" />


<img width="1905" height="841" alt="image" src="https://github.com/user-attachments/assets/6f9e0039-d379-441b-a070-e0c17efa9a31" />

