# GeoXAI — نظام تقييم ملاءمة المواقع التجارية
### أبها وخميس مشيط · منطقة عسير

نموذج تعلم آلي قابل للتفسير يُقيّم ملاءمة مواقع المشاريع التجارية
في البيئة الجبلية لمنطقة عسير باستخدام CatBoost + GeoShapley.

---

## 🗂️ هيكل الملفات

```
geoxai-app/
├── app.py                    ← الواجهة الرئيسية
├── requirements.txt          ← المكتبات المطلوبة
├── README.md                 ← هذا الملف
├── .streamlit/
│   └── config.toml          ← إعدادات التصميم
│
├── catboost_model.pkl        ← ⬅ أضيفيها من Colab
├── original_cols.pkl         ← ⬅ أضيفيها من Colab
└── fill_stats.pkl            ← ⬅ أضيفيها من Colab
```

---

## 🚀 خطوات النشر الكاملة

### الخطوة 1 — تصدير ملفات النموذج من Colab

في نهاية الكود الأصلي، أضيفي هذه الخلية في Colab وشغّليها:

```python
from google.colab import files

# تنزيل الملفات الثلاثة
files.download('catboost_model.pkl')
files.download('original_cols.pkl')
files.download('fill_stats.pkl')
```

ستتنزّل الملفات الثلاثة إلى جهازك تلقائياً.

---

### الخطوة 2 — إنشاء مستودع GitHub

1. افتحي [github.com](https://github.com) وسجّلي الدخول
2. اضغطي **New** (أو زر +) لإنشاء مستودع جديد
3. اسم المستودع: `geoxai-app` (أو أي اسم تريدينه)
4. اجعليه **Public** (مطلوب للنشر المجاني)
5. اضغطي **Create repository**

---

### الخطوة 3 — رفع الملفات على GitHub

#### الطريقة الأسهل (عبر المتصفح):

1. في صفحة المستودع اضغطي **Add file → Upload files**
2. ارفعي هذه الملفات دفعة واحدة:
   - `app.py`
   - `requirements.txt`
   - `catboost_model.pkl`
   - `original_cols.pkl`
   - `fill_stats.pkl`
3. لإضافة مجلد `.streamlit` مع `config.toml`:
   - اضغطي **Add file → Create new file**
   - في اسم الملف اكتبي: `.streamlit/config.toml`
   - انسخي محتوى ملف `config.toml` في المربع
   - اضغطي **Commit new file**

---

### الخطوة 4 — النشر على Streamlit Cloud (مجاني)

1. افتحي [share.streamlit.io](https://share.streamlit.io)
2. اضغطي **Sign in with GitHub** وسجّلي الدخول
3. اضغطي **New app**
4. اختاري:
   - **Repository**: `اسم_المستخدم/geoxai-app`
   - **Branch**: `main`
   - **Main file path**: `app.py`
5. اضغطي **Deploy**

⏳ انتظري 2–3 دقائق للنشر الأول.

✅ ستحصلين على رابط مثل:
```
https://geoxai-app-XXXX.streamlit.app
```

---

## 🔄 تحديث التطبيق لاحقاً

في أي وقت تحدّثين `app.py` وترفعينه على GitHub،
يتحدث Streamlit Cloud تلقائياً خلال ثوانٍ.

---

## ⚙️ تشغيل محلي (اختياري)

```bash
# تثبيت المكتبات
pip install -r requirements.txt

# تشغيل التطبيق
streamlit run app.py
```

---

## 🎯 مميزات الواجهة

| الميزة | الوصف |
|--------|--------|
| 🗺️ خريطة تفاعلية | عرض الموقع مع دائرة 500م |
| 🛰️ جلب الارتفاع | تلقائي عبر Open-Elevation API |
| 🎯 مقياس الاحتمال | Gauge chart ملوّن |
| 📊 أهمية المتغيرات | مخطط شريطي من CatBoost |
| 🔍 تحليل المخاطر | تنبيهات ذكية للعوامل الحرجة |
| 🌙 وضع مظلم | مدعوم تلقائياً |
| 📱 متجاوب | يعمل على الجوال والحاسب |

---

## ⚠️ ملاحظة مهمة — Target Encoding

القيم الافتراضية لـ `CATEGORY_TE` و`FACILITY_TYPE_TE` في `app.py` تقديرية.
لتحديثها بالقيم الحقيقية من نموذجك:

في Colab، بعد تشغيل القسم 12.2، أضيفي:

```python
import json

# تصدير قيم TE الحقيقية
category_te = agg_full['te'].to_dict()
facility_te = agg_full_type['te'].to_dict()

print(json.dumps(category_te, ensure_ascii=False, indent=2))
print(json.dumps(facility_te, ensure_ascii=False, indent=2))
```

ثم انسخي القيم وحدّثي القواميس `CATEGORY_TE` و`FACILITY_TYPE_TE` في `app.py`.

---

## 📚 المراجع
- Li, Z. (2024). GeoShapley
- Starakiewicz & Wojcik (2025)
- Khan et al. (2025)
- اللائحة التنفيذية لنظام إجراءات التراخيص البلدية
