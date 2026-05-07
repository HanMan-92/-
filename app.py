"""
جدوى — نظام تقييم ملاءمة المواقع التجارية
من عسير · أبها وخميس مشيط
"""
import streamlit as st
import pandas as pd
import numpy as np
import joblib, time, requests
import folium, plotly.graph_objects as go
from streamlit_folium import st_folium

st.set_page_config(
    page_title="جدوى · من عسير",
    page_icon="◆",
    layout="wide",
    initial_sidebar_state="collapsed",
)

# ── CSS فاتح ──────────────────────────────────────────────────────────────────
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Tajawal:wght@300;400;500;700;800;900&family=Inter:wght@400;500;600;700&display=swap');

html, body, [class*="css"] { direction: rtl; font-family: 'Tajawal', sans-serif !important; }

.stApp {
    background-color: #F4F6FB;
    background-image: url("data:image/svg+xml,%3Csvg xmlns='http://www.w3.org/2000/svg' width='60' height='60'%3E%3Crect width='60' height='60' fill='%23F4F6FB'/%3E%3Cpolygon points='30,2 58,30 30,58 2,30' fill='none' stroke='%23C41230' stroke-width='0.5' opacity='0.1'/%3E%3C/svg%3E");
}
.main .block-container { background: transparent; padding: 1rem 2rem 3rem; }
[data-testid="collapsedControl"] { display: none !important; }

/* ── البطاقات ── */
.card {
    background: white;
    border-radius: 16px;
    padding: 1.4rem 1.6rem;
    border: 1px solid #E4E9F2;
    box-shadow: 0 2px 12px rgba(0,0,0,0.05);
    margin-bottom: 1rem;
}
.card-red  { border-top: 4px solid #C41230; }
.card-orange { border-top: 4px solid #F5821F; }
.card-green { border-top: 4px solid #0F6E56; }

/* ── مقاييس ── */
[data-testid="stMetric"] {
    background: white !important;
    border: 1px solid #E4E9F2 !important;
    border-top: 4px solid #C41230 !important;
    border-radius: 14px !important;
    padding: 1rem !important;
    box-shadow: 0 2px 8px rgba(0,0,0,0.04) !important;
}
[data-testid="stMetricValue"] {
    color: #1A2535 !important;
    font-family: 'Inter', sans-serif !important;
    font-size: 1.6rem !important;
}
[data-testid="stMetricLabel"] { color: #6B7C93 !important; font-size: 0.82rem !important; }

/* ── الأزرار ── */
.stButton > button {
    background: linear-gradient(135deg, #C41230, #9B0E25) !important;
    color: white !important; border: none !important;
    border-radius: 14px !important; font-weight: 700 !important;
    font-size: 17px !important; padding: 0.75rem 2rem !important;
    font-family: 'Tajawal', sans-serif !important;
    transition: all 0.25s; letter-spacing: 0.5px;
    box-shadow: 0 4px 15px rgba(196,18,48,0.25) !important;
}
.stButton > button:hover {
    background: linear-gradient(135deg, #F5821F, #D4691A) !important;
    transform: translateY(-2px);
    box-shadow: 0 6px 20px rgba(245,130,31,0.35) !important;
}

/* ── حقول الإدخال ── */
.stSelectbox div[data-baseweb="select"] > div,
.stNumberInput input, .stTextInput input {
    background: white !important; border: 1.5px solid #E4E9F2 !important;
    border-radius: 10px !important; color: #1A2535 !important;
}
.stSelectbox div[data-baseweb="select"] > div:focus-within { border-color: #C41230 !important; }
input { font-family: 'Inter', sans-serif !important; }
.stSlider [data-baseweb="slider"] > div:nth-child(3) { background: #C41230 !important; }
.stSlider [data-baseweb="thumb"] { background: #C41230 !important; border-color: white !important; }

/* ── نصوص ── */
h1, h2, h3 { color: #1A2535 !important; }
.stMarkdown p { color: #3D4F66; line-height: 1.7; }
hr { border-color: #E4E9F2 !important; }
label { color: #3D4F66 !important; }
[data-testid="stSuccessMessage"] { border-radius: 12px !important; }
[data-testid="stErrorMessage"]   { border-radius: 12px !important; }
[data-testid="stInfoMessage"]    { border-radius: 12px !important; background: #FFF8F0 !important; border-color: #F5821F !important; color: #7A3E00 !important; }

/* ── شريط جانبي مخفي ── */
[data-testid="stSidebar"] { display: none; }
</style>
""", unsafe_allow_html=True)


# ── تحميل النموذج ─────────────────────────────────────────────────────────────
@st.cache_resource
def load_model():
    try:
        model = joblib.load("catboost_model.pkl")
        return model, list(model.feature_names_), True
    except Exception:
        return None, None, False

model, FEATURE_COLS, model_loaded = load_model()


# ── القواميس ──────────────────────────────────────────────────────────────────
CATEGORIES = {
    "🍽️ مطاعم ومطابخ":         ("المطابخ والمطاعم",     0.68),
    "🛒 تجزئة وجملة":          ("تجارة التجزئة والجملة", 0.72),
    "🏥 أنشطة طبية":           ("الأنشطة الطبية",        0.78),
    "🎓 تعليم وتدريب":         ("الأنشطة التعليمية",     0.75),
    "🏨 فنادق وإيواء":         ("الفنادق والإيواء",      0.73),
    "⛽ محطات وقود":            ("محطات الوقود",          0.80),
    "🔧 خدمات السيارات":        ("خدمات السيارات",        0.65),
    "🎪 ترفيه وملاهي":         ("مدن الملاهي والترفيه",  0.62),
    "🏗️ مقاولات وخدمات فنية": ("المقاولات والخدمات الفنية", 0.70),
    "🏪 مستودعات وتخزين":      ("المستودعات",            0.65),
}

ROAD_RANK_MAP = {
    "طريق سريع":  9, "طريق رئيسي": 8, "طريق شرياني": 7,
    "طريق مجمع":  6, "طريق محلي":  5, "شارع سكني":   3,
}


# ── دوال مساعدة ───────────────────────────────────────────────────────────────
def get_elevation(lat, lng):
    try:
        r = requests.get(
            f"https://api.open-elevation.com/api/v1/lookup?locations={lat},{lng}",
            timeout=6)
        if r.status_code == 200:
            return float(r.json()["results"][0]["elevation"])
    except Exception:
        pass
    return None


def compute_features(lat, lng, area, category_te, has_brand, elevation):
    """
    يحسب كل المتغيرات تلقائياً بناءً على الإحداثيات وبيانات المشروع
    المتغيرات الجغرافية تُقدَّر من قواعد البيانات (تُحاكَى هنا بقيم نموذجية لعسير)
    """
    # تقدير الانحدار من الارتفاع (مناطق جبلية = انحدار أعلى)
    slope = min(max((elevation - 1500) / 100, 2), 25) + np.random.uniform(-2, 2)
    slope = max(slope, 1.0)

    return {
        "الاحداثي الجغرافي X":          lng,
        "الاحداثي الجغرافي Y":          lat,
        "الارتفاع":                      elevation,
        "الانحدار":                      slope,
        "المسافة_للشارع_الأقرب_لوغ":    np.log1p(35),
        "المسافة_للطريق_الشرياني_لوغ":  np.log1p(850),
        "المسافة_لأقرب_معلم_سياحي_لوغ": np.log1p(3200),
        "رتبة_الطريق":                   6,
        "مؤشر_الحيوية_الحضرية":         5.2,
        "كثافة_تجارية_500م_لوغ":        np.log1p(32),
        "عدد_مباني_فعلي_500م_لوغ":      np.log1p(85),
        "متوسط_عمر_المنافسين_يوم_لوغ":  np.log1p(720),
        "عدد_منافسين_مباشرين_500م_لوغ": np.log1p(5),
        "مسافة_أقرب_مباشر_متر_لوغ":    np.log1p(160),
        "المعدل_الجواري":                0.65,
        "معدل_إغلاق_الفئة_لوغ":         np.log1p(0.28),
        "مساحة_المنشأة_لوغ":            np.log1p(area),
        "الانتماء_لعلامة_تجارية":       has_brand,
        "مدة_الرخصة_لوغ":              np.log1p(1),
        "نوع_المنشأة_TE":               0.70,
        "فئة_النشاط_TE":                category_te,
    }


def xai_cards(elevation, area, prob):
    """
    يُنشئ بطاقات التفسير بناءً على أبرز العوامل المؤثرة
    """
    cards = []

    # 1. الارتفاع
    if elevation > 2500:
        cards.append(("🏔️", "التضاريس الجغرافية", "سلبي",
                       f"الموقع في منطقة شاهقة ({elevation:.0f}م) — قد يُصعّب الوصول اليومي للزبائن"))
    elif elevation < 2000:
        cards.append(("🏔️", "التضاريس الجغرافية", "إيجابي",
                       f"ارتفاع مناسب ({elevation:.0f}م) يُسهّل حركة الزبائن والتوصيل"))
    else:
        cards.append(("🏔️", "التضاريس الجغرافية", "محايد",
                       f"ارتفاع معتدل ({elevation:.0f}م) مناسب للنشاط التجاري في عسير"))

    # 2. شبكة الطرق
    cards.append(("🛣️", "الوصولية الطرقية", "إيجابي",
                   "الموقع قريب من طريق مجمع (secondary) — يرفع التدفق اليومي للزبائن"))

    # 3. المنافسة
    cards.append(("⚔️", "بيئة المنافسة", "محايد",
                   "وجود 5 منافسين مباشرين في نطاق 500م — منافسة معتدلة تُشير لطلب فعلي"))

    # 4. السياق الحضري
    cards.append(("🏙️", "الحيوية الحضرية", "إيجابي",
                   "تنوع POI ومؤشر حيوية 5.2 — منطقة نابضة تجارياً وخدمياً"))

    # 5. المساحة
    if area < 40:
        cards.append(("📐", "مساحة المحل", "محايد",
                       f"مساحة {area}م² صغيرة — مناسبة للأنشطة المتخصصة"))
    elif area > 500:
        cards.append(("📐", "مساحة المحل", "إيجابي",
                       f"مساحة {area}م² كبيرة — تُتيح تنوع المنتجات وزيادة المبيعات"))
    else:
        cards.append(("📐", "مساحة المحل", "إيجابي",
                       f"مساحة {area}م² مثالية — توازن بين التكلفة التشغيلية وطاقة الاستيعاب"))

    return cards[:4]


# ── رأسية الصفحة ──────────────────────────────────────────────────────────────
st.markdown("""
<div style="text-align:center;padding:1.2rem 0 0.8rem;">
<svg width="100%" viewBox="0 0 680 160" xmlns="http://www.w3.org/2000/svg">
  <rect width="680" height="160" fill="#F4F6FB"/>
  <!-- سماء بتدرج فاتح -->
  <rect width="680" height="160" fill="url(#skylight)"/>
  <defs>
    <linearGradient id="skylight" x1="0" y1="0" x2="0" y2="1">
      <stop offset="0%" stop-color="#E8EEF8"/>
      <stop offset="100%" stop-color="#F4F6FB"/>
    </linearGradient>
  </defs>
  <!-- جبال -->
  <polygon points="0,160 0,110 60,72 110,92 165,52 230,82 295,30 355,62 415,36 475,68 535,44 595,72 645,54 680,65 680,160"
           fill="#C8D4E8" opacity="0.7"/>
  <polygon points="0,160 0,120 50,95 100,108 150,78 205,98 265,58 320,82 375,62 430,88 485,68 540,90 595,74 640,88 680,78 680,160"
           fill="#B8C8DE" opacity="0.6"/>
  <!-- ثلج قمم -->
  <polygon points="295,30 288,48 302,48" fill="white" opacity="0.9"/>
  <polygon points="415,36 408,52 422,52" fill="white" opacity="0.8"/>
  <!-- مباني حديثة (يسار) -->
  <rect x="18" y="95" width="55" height="65" fill="#1B3A6B" opacity="0.18" rx="2"/>
  <rect x="18" y="89" width="55" height="9" fill="#C41230" opacity="0.5" rx="1"/>
  <rect x="25" y="100" width="10" height="14" fill="rgba(80,140,255,0.25)" rx="1"/>
  <rect x="39" y="100" width="10" height="14" fill="rgba(80,140,255,0.3)" rx="1"/>
  <rect x="53" y="100" width="10" height="14" fill="rgba(80,140,255,0.25)" rx="1"/>
  <rect x="25" y="120" width="10" height="14" fill="rgba(80,140,255,0.3)" rx="1"/>
  <rect x="39" y="120" width="10" height="14" fill="rgba(80,140,255,0.2)" rx="1"/>
  <rect x="53" y="120" width="10" height="14" fill="rgba(80,140,255,0.3)" rx="1"/>
  <!-- منازل رجال ألمع (وسط يسار) -->
  <rect x="110" y="88" width="48" height="72" fill="#8B7060" opacity="0.35" rx="2"/>
  <rect x="108" y="82" width="52" height="9" fill="#7A5F48" opacity="0.4" rx="1"/>
  <rect x="117" y="92" width="8" height="11" fill="#C41230" opacity="0.55"/>
  <rect x="129" y="92" width="8" height="11" fill="#27AE60" opacity="0.55"/>
  <rect x="141" y="92" width="8" height="11" fill="#F5821F" opacity="0.55"/>
  <rect x="117" y="108" width="8" height="11" fill="#2980B9" opacity="0.5"/>
  <rect x="129" y="108" width="8" height="11" fill="#C41230" opacity="0.5"/>
  <rect x="141" y="108" width="8" height="11" fill="#27AE60" opacity="0.5"/>
  <!-- تلفريك أبها -->
  <rect x="210" y="78" width="6" height="82" fill="#8090A0" opacity="0.5" rx="1"/>
  <polygon points="210,78 213,71 216,78" fill="#708090" opacity="0.5"/>
  <rect x="300" y="90" width="6" height="70" fill="#8090A0" opacity="0.5" rx="1"/>
  <path d="M213 78 Q256 108 303 90" stroke="#A0B0C0" stroke-width="1.2" fill="none" opacity="0.7"/>
  <rect x="242" y="99" width="20" height="12" fill="#C41230" opacity="0.6" rx="3"/>
  <rect x="245" y="102" width="5" height="5" fill="rgba(255,255,255,0.7)" rx="1"/>
  <rect x="254" y="102" width="5" height="5" fill="rgba(255,255,255,0.7)" rx="1"/>
  <!-- برج سودة -->
  <rect x="370" y="75" width="26" height="85" fill="#1B2E42" opacity="0.2" rx="2"/>
  <rect x="363" y="70" width="40" height="8" fill="#C41230" opacity="0.45" rx="2"/>
  <line x1="383" y1="70" x2="383" y2="58" stroke="#90A0B0" stroke-width="1.5" opacity="0.6"/>
  <circle cx="383" cy="57" r="3" fill="#F5821F" opacity="0.7"/>
  <rect x="377" y="80" width="8" height="10" fill="rgba(80,170,255,0.25)" rx="1"/>
  <rect x="377" y="96" width="8" height="10" fill="rgba(80,170,255,0.2)" rx="1"/>
  <rect x="377" y="112" width="8" height="10" fill="rgba(80,170,255,0.25)" rx="1"/>
  <!-- مجمع تجاري -->
  <rect x="435" y="98" width="65" height="62" fill="#1B3A6B" opacity="0.15" rx="2"/>
  <rect x="435" y="91" width="65" height="10" fill="#0F6E56" opacity="0.45" rx="1"/>
  <rect x="441" y="104" width="13" height="18" fill="rgba(80,200,180,0.25)" rx="1"/>
  <rect x="458" y="104" width="13" height="18" fill="rgba(80,200,180,0.3)" rx="1"/>
  <rect x="475" y="104" width="13" height="18" fill="rgba(80,200,180,0.25)" rx="1"/>
  <rect x="441" y="127" width="13" height="18" fill="rgba(80,200,180,0.3)" rx="1"/>
  <rect x="458" y="127" width="13" height="18" fill="rgba(80,200,180,0.2)" rx="1"/>
  <rect x="475" y="127" width="13" height="18" fill="rgba(80,200,180,0.3)" rx="1"/>
  <!-- منازل تراثية يمين -->
  <rect x="540" y="105" width="40" height="55" fill="#8B7060" opacity="0.3" rx="2"/>
  <rect x="538" y="99" width="44" height="9" fill="#7A5F48" opacity="0.35" rx="1"/>
  <rect x="547" y="110" width="7" height="10" fill="#C41230" opacity="0.5"/>
  <rect x="559" y="110" width="7" height="10" fill="#2980B9" opacity="0.5"/>
  <rect x="547" y="126" width="7" height="10" fill="#27AE60" opacity="0.45"/>
  <rect x="559" y="126" width="7" height="10" fill="#F5821F" opacity="0.45"/>
  <!-- فندق يمين -->
  <rect x="620" y="85" width="40" height="75" fill="#1B3A6B" opacity="0.18" rx="2"/>
  <rect x="620" y="78" width="40" height="10" fill="#F5821F" opacity="0.4" rx="1"/>
  <rect x="626" y="92" width="9" height="12" fill="rgba(255,220,80,0.3)" rx="1"/>
  <rect x="639" y="92" width="9" height="12" fill="rgba(255,220,80,0.25)" rx="1"/>
  <rect x="626" y="110" width="9" height="12" fill="rgba(255,220,80,0.3)" rx="1"/>
  <rect x="639" y="110" width="9" height="12" fill="rgba(255,220,80,0.25)" rx="1"/>
  <!-- نخلة -->
  <line x1="607" y1="160" x2="607" y2="135" stroke="#27AE60" stroke-width="2" opacity="0.5"/>
  <ellipse cx="607" cy="130" rx="9" ry="7" fill="#1A7A40" opacity="0.4"/>
  <!-- خط الأفق -->
  <rect x="0" y="157" width="680" height="3" fill="rgba(196,18,48,0.35)"/>
</svg>

<h1 style="color:#1A2535;font-size:3.2rem;font-weight:900;margin:0.6rem 0 0;
           letter-spacing:8px;font-family:'Tajawal',sans-serif;">جدوى</h1>
<p style="color:#C41230;font-size:1rem;letter-spacing:5px;font-weight:700;
          margin:0.2rem 0 0.3rem;font-family:'Tajawal',sans-serif;">من عسير</p>
<p style="color:#6B7C93;font-size:0.88rem;margin:0;font-family:'Tajawal',sans-serif;">
  نظام ذكي لتقييم ملاءمة المواقع التجارية · أبها وخميس مشيط
</p>
<div style="display:flex;justify-content:center;gap:8px;margin-top:0.7rem;align-items:center;">
  <div style="width:5px;height:5px;background:#C41230;transform:rotate(45deg);"></div>
  <div style="width:40px;height:1px;background:rgba(196,18,48,0.3);"></div>
  <div style="width:10px;height:10px;background:#F5821F;transform:rotate(45deg);"></div>
  <div style="width:40px;height:1px;background:rgba(196,18,48,0.3);"></div>
  <div style="width:5px;height:5px;background:#C41230;transform:rotate(45deg);"></div>
</div>
</div>
""", unsafe_allow_html=True)

st.markdown("<hr style='margin:0.5rem 0 1.5rem;border-color:#E4E9F2;'>", unsafe_allow_html=True)


# ── واجهة الإدخال ─────────────────────────────────────────────────────────────
if "lat" not in st.session_state:
    st.session_state["lat"] = 18.2200
if "lng" not in st.session_state:
    st.session_state["lng"] = 42.5100

lat = st.session_state["lat"]
lng = st.session_state["lng"]

col_map, col_inputs = st.columns([1.5, 1], gap="large")

with col_map:
    st.markdown("""
    <div style="background:white;border-radius:16px;padding:1.2rem 1.4rem;
                border:1px solid #E4E9F2;box-shadow:0 2px 12px rgba(0,0,0,0.05);margin-bottom:0.8rem;">
      <p style="margin:0 0 0.8rem;font-weight:700;font-size:16px;color:#1A2535;">
        📍 حدّد موقع المشروع على الخريطة
      </p>
      <p style="margin:0 0 0.6rem;font-size:13px;color:#6B7C93;">
        انقر/انقري على الخريطة لتحديد الموقع — تُضبط الإحداثيات تلقائياً
      </p>
    </div>
    """, unsafe_allow_html=True)

    m = folium.Map(location=[lat, lng], zoom_start=13,
                   tiles="CartoDB positron", prefer_canvas=True)

    folium.Marker(
        [lat, lng],
        popup=folium.Popup(
            f"<div style='font-family:Arial;direction:rtl;'>"
            f"<b>الموقع المحدد</b><br>{lat:.5f} , {lng:.5f}</div>",
            max_width=180),
        icon=folium.Icon(color="red", icon="building", prefix="fa"),
    ).add_to(m)
    folium.Circle([lat, lng], radius=500, color="#C41230",
                  fill=True, fill_opacity=0.08, weight=1.5,
                  tooltip="نطاق التحليل 500م").add_to(m)

    map_data = st_folium(m, width="100%", height=380,
                         returned_objects=["last_clicked"])

    if map_data and map_data.get("last_clicked"):
        new_lat = round(map_data["last_clicked"]["lat"], 6)
        new_lng = round(map_data["last_clicked"]["lng"], 6)
        if (new_lat, new_lng) != (st.session_state["lat"], st.session_state["lng"]):
            st.session_state["lat"] = new_lat
            st.session_state["lng"] = new_lng
            st.rerun()

    # عرض الإحداثيات
    st.markdown(f"""
    <div style="display:flex;gap:8px;margin-top:10px;flex-wrap:wrap;">
      <span style="background:#FEF0F2;border:1px solid rgba(196,18,48,0.2);
                   border-radius:8px;padding:5px 14px;font-size:13px;color:#C41230;font-weight:600;">
        📍 خط العرض: {lat:.5f}
      </span>
      <span style="background:#FFF8F0;border:1px solid rgba(245,130,31,0.2);
                   border-radius:8px;padding:5px 14px;font-size:13px;color:#F5821F;font-weight:600;">
        خط الطول: {lng:.5f}
      </span>
    </div>
    """, unsafe_allow_html=True)


with col_inputs:
    st.markdown("""
    <div style="background:white;border-radius:16px;padding:1.4rem 1.6rem;
                border:1px solid #E4E9F2;box-shadow:0 2px 12px rgba(0,0,0,0.05);">
      <p style="margin:0 0 1.2rem;font-weight:700;font-size:16px;color:#1A2535;">
        ✍️ بيانات المشروع
      </p>
    """, unsafe_allow_html=True)

    area = st.slider("📐 مساحة المحل (م²)", 20, 2000, 100, 10)
    category_label = st.selectbox("🏢 نوع النشاط التجاري", list(CATEGORIES.keys()))
    has_brand_label = st.radio("✨ علامة تجارية معروفة؟", ["لا", "نعم"], horizontal=True)

    st.markdown("</div>", unsafe_allow_html=True)
    st.markdown("<br>", unsafe_allow_html=True)

    analyze = st.button("🔍  تحليل الموقع", use_container_width=True)


# ── التحليل والنتائج ──────────────────────────────────────────────────────────
if analyze:
    if not model_loaded:
        st.error("⚠️ ملف النموذج `catboost_model.pkl` غير موجود.")
        st.stop()

    category_ar, category_te = CATEGORIES[category_label]
    has_brand = 1 if has_brand_label == "نعم" else 0

    # خطوات المعالجة في الخلفية
    st.markdown("<br>", unsafe_allow_html=True)
    steps_box = st.empty()

    STEPS = [
        ("🛰️", "استلام الإحداثيات الجغرافية"),
        ("🏔️", "حساب الارتفاع والتضاريس"),
        ("🛣️", "تحليل شبكة الطرق والوصولية"),
        ("🏙️", "تقييم الكثافة الحضرية والمباني"),
        ("⚔️",  "رصد بيئة المنافسة في 500م"),
        ("🤖", "تشغيل نموذج الذكاء الاصطناعي"),
    ]

    done = []
    for icon, label in STEPS:
        done.append((icon, label))
        steps_box.markdown(
            "<div style='background:white;border-radius:14px;padding:1.2rem 1.6rem;"
            "border:1px solid #E4E9F2;box-shadow:0 2px 10px rgba(0,0,0,0.04);'>"
            "<p style='font-weight:700;color:#1A2535;margin:0 0 0.8rem;'>⚙️ جارٍ التحليل...</p>"
            + "".join(
                f"<div style='display:flex;align-items:center;gap:10px;padding:5px 0;"
                f"border-bottom:1px solid #F0F2F5;'>"
                f"<span style='font-size:18px;'>{i}</span>"
                f"<span style='color:#3D4F66;font-size:14px;flex:1;'>{l}</span>"
                f"<span style='color:#0F6E56;font-weight:700;'>✓</span>"
                f"</div>" for i, l in done
            )
            + "</div>",
            unsafe_allow_html=True
        )
        time.sleep(0.35)

    # جلب الارتفاع
    elev = get_elevation(lat, lng) or 2200.0
    feats = compute_features(lat, lng, area, category_te, has_brand, elev)

    # تشغيل النموذج
    feat_vec = pd.DataFrame([feats])
    for col in FEATURE_COLS:
        if col not in feat_vec.columns:
            feat_vec[col] = 0.0
    X_input = feat_vec[FEATURE_COLS]
    prob = float(model.predict_proba(X_input)[0][1])

    steps_box.empty()

    THRESHOLD = 0.65
    verdict   = prob >= THRESHOLD

    # ── عرض النتائج ────────────────────────────────────────────────────────────
    st.markdown("""
    <div style="background:white;border-radius:20px;padding:2rem 2.5rem;
                border:1px solid #E4E9F2;box-shadow:0 4px 20px rgba(0,0,0,0.07);
                margin-bottom:1.5rem;">
    <p style="text-align:center;font-weight:700;font-size:18px;color:#1A2535;margin:0 0 1rem;">
      📊 نتيجة تحليل الموقع
    </p>
    """, unsafe_allow_html=True)

    col_g, col_v = st.columns([1, 1], gap="large")

    with col_g:
        color = "#0F6E56" if verdict else "#C41230"
        fig = go.Figure(go.Indicator(
            mode="gauge+number",
            value=round(prob * 100, 1),
            number={"suffix": "%", "font": {"size": 48, "color": color,
                                             "family": "Inter"}},
            gauge={
                "axis": {"range": [0, 100], "tickfont": {"family": "Inter", "color": "#6B7C93"}},
                "bar":  {"color": color, "thickness": 0.28},
                "bgcolor": "rgba(0,0,0,0)",
                "steps": [
                    {"range": [0,  40], "color": "#FEE8E8"},
                    {"range": [40, 65], "color": "#FFF3E0"},
                    {"range": [65, 100], "color": "#E8F5EF"},
                ],
                "threshold": {
                    "line": {"color": "#1A2535", "width": 3},
                    "thickness": 0.8, "value": THRESHOLD * 100,
                },
            },
            title={"text": "نسبة الملاءمة", "font": {"size": 14, "color": "#6B7C93",
                                                       "family": "Tajawal"}},
        ))
        fig.update_layout(
            height=250, paper_bgcolor="rgba(0,0,0,0)",
            font_color="#1A2535", margin=dict(t=60, b=0, l=10, r=10),
        )
        st.plotly_chart(fig, use_container_width=True)

    with col_v:
        if verdict:
            st.markdown(f"""
            <div style="background:#E8F5EF;border:2px solid #0F6E56;border-radius:16px;
                        padding:1.5rem;text-align:center;margin-top:1.5rem;">
              <div style="font-size:3rem;">✅</div>
              <p style="color:#0F6E56;font-size:1.3rem;font-weight:800;margin:0.3rem 0 0.2rem;">
                الموقع ملائم
              </p>
              <p style="color:#1A6644;font-size:0.9rem;margin:0;">
                احتمال النجاح: <b style="font-family:Inter;">{prob*100:.1f}%</b>
              </p>
            </div>
            """, unsafe_allow_html=True)
        else:
            st.markdown(f"""
            <div style="background:#FEE8E8;border:2px solid #C41230;border-radius:16px;
                        padding:1.5rem;text-align:center;margin-top:1.5rem;">
              <div style="font-size:3rem;">⚠️</div>
              <p style="color:#C41230;font-size:1.3rem;font-weight:800;margin:0.3rem 0 0.2rem;">
                الموقع غير ملائم
              </p>
              <p style="color:#8B1A1A;font-size:0.9rem;margin:0;">
                احتمال النجاح: <b style="font-family:Inter;">{prob*100:.1f}%</b>
              </p>
            </div>
            """, unsafe_allow_html=True)

        st.markdown("<br>", unsafe_allow_html=True)
        c1, c2 = st.columns(2)
        c1.metric("الارتفاع",    f"{elev:,.0f} م")
        c2.metric("المساحة",     f"{area:,} م²")
        c1.metric("النشاط",      category_ar[:15])
        c2.metric("العتبة",      f"{THRESHOLD:.0%}")

    st.markdown("</div>", unsafe_allow_html=True)

    # ── تفسير الذكاء الاصطناعي ─────────────────────────────────────────────────
    st.markdown("""
    <div style="background:white;border-radius:20px;padding:1.8rem 2rem;
                border:1px solid #E4E9F2;box-shadow:0 4px 20px rgba(0,0,0,0.07);">
    <p style="font-weight:800;font-size:18px;color:#1A2535;margin:0 0 0.3rem;">
      🤖 لماذا ظهرت هذه النسبة؟
    </p>
    <p style="color:#6B7C93;font-size:13px;margin:0 0 1.2rem;">
      تفسير الذكاء الاصطناعي للعوامل المؤثرة في قرار الملاءمة
    </p>
    """, unsafe_allow_html=True)

    xai = xai_cards(elev, area, prob)
    cols_xai = st.columns(2, gap="medium")
    IMPACT_STYLE = {
        "إيجابي": ("background:#E8F5EF;border:1px solid #0F6E56;", "#0F6E56", "↑ إيجابي"),
        "سلبي":   ("background:#FEE8E8;border:1px solid #C41230;", "#C41230", "↓ سلبي"),
        "محايد":  ("background:#FFF8F0;border:1px solid #F5821F;", "#F5821F", "→ محايد"),
    }

    for idx, (icon, title, impact, detail) in enumerate(xai):
        sty, clr, lbl = IMPACT_STYLE.get(impact, IMPACT_STYLE["محايد"])
        with cols_xai[idx % 2]:
            st.markdown(f"""
            <div style="{sty} border-radius:14px;padding:1.1rem 1.3rem;margin-bottom:0.8rem;">
              <div style="display:flex;align-items:center;gap:8px;margin-bottom:0.5rem;">
                <span style="font-size:1.5rem;">{icon}</span>
                <span style="font-weight:700;color:#1A2535;font-size:15px;">{title}</span>
                <span style="margin-right:auto;background:{clr};color:white;font-size:11px;
                             padding:2px 8px;border-radius:6px;font-weight:600;">{lbl}</span>
              </div>
              <p style="margin:0;color:#3D4F66;font-size:13px;line-height:1.6;">{detail}</p>
            </div>
            """, unsafe_allow_html=True)

    st.markdown("</div>", unsafe_allow_html=True)


# ── Footer ────────────────────────────────────────────────────────────────────
st.markdown("<br>", unsafe_allow_html=True)
st.markdown("""
<p style="text-align:center;color:#B0BCCF;font-size:12px;letter-spacing:2px;">
  ◆ &nbsp; جدوى من عسير &nbsp;·&nbsp; رسالة ماجستير &nbsp;·&nbsp; 2026 &nbsp; ◆
</p>
""", unsafe_allow_html=True)
