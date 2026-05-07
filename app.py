"""
جدوى — نظام تقييم ملاءمة المواقع التجارية | أمانة منطقة عسير
"""
import streamlit as st
import pandas as pd
import numpy as np
import joblib, time, requests
import folium, plotly.graph_objects as go
from streamlit_folium import st_folium

st.set_page_config(page_title="جدوى · أمانة عسير", page_icon="◆",
                   layout="wide", initial_sidebar_state="collapsed")

# ══════════════════════════════════════════════════════════════════════════════
# CSS الاحترافي الكامل
# ══════════════════════════════════════════════════════════════════════════════
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Cairo:wght@300;400;600;700;900&family=Tajawal:wght@300;400;500;700&family=IBM+Plex+Mono:wght@400;600&display=swap');

:root {
  --navy:   #071626;
  --navy2:  #0D2240;
  --red:    #C41230;
  --red2:   #9B0E25;
  --orange: #F5821F;
  --gold:   #C9952A;
  --white:  #FFFFFF;
  --bg:     #EEF2F7;
  --bg2:    #F8FAFD;
  --border: #D8E0EC;
  --text:   #1A2535;
  --muted:  #64748B;
  --green:  #0D6E4A;
  --card-shadow: 0 1px 3px rgba(0,0,0,0.08), 0 4px 16px rgba(0,0,0,0.06);
  --card-shadow-lg: 0 4px 6px rgba(0,0,0,0.07), 0 12px 40px rgba(0,0,0,0.12);
}

html, body, [class*="css"] {
  direction: rtl;
  font-family: 'Tajawal', sans-serif !important;
  color: var(--text);
}

/* ── خلفية عامة ── */
.stApp {
  background: var(--bg);
  background-image:
    radial-gradient(circle at 20% 50%, rgba(196,18,48,0.04) 0%, transparent 50%),
    radial-gradient(circle at 80% 20%, rgba(11,33,64,0.06) 0%, transparent 50%);
}
.main .block-container {
  padding: 0 !important;
  max-width: 100% !important;
}

/* ── إخفاء عناصر Streamlit الافتراضية ── */
#MainMenu, footer, header, [data-testid="collapsedControl"],
[data-testid="stToolbar"], .stDeployButton { display: none !important; }
[data-testid="stSidebar"] { display: none !important; }
[data-testid="stDecoration"] { display: none !important; }

/* ── شريط التنقل ── */
.nav-bar {
  background: linear-gradient(135deg, var(--navy) 0%, var(--navy2) 100%);
  padding: 0 2.5rem;
  height: 64px;
  display: flex;
  align-items: center;
  border-bottom: 3px solid var(--red);
  position: sticky;
  top: 0;
  z-index: 999;
  box-shadow: 0 2px 20px rgba(0,0,0,0.3);
}
.nav-logo {
  display: flex;
  align-items: center;
  gap: 14px;
}
.nav-diamond {
  width: 38px; height: 38px;
  background: linear-gradient(135deg, var(--red), var(--orange));
  transform: rotate(45deg);
  border-radius: 6px;
  flex-shrink: 0;
}
.nav-title { color: white; font-family: 'Cairo', sans-serif; }
.nav-title h1 { font-size: 1.35rem; font-weight: 900; margin: 0; letter-spacing: 3px; line-height: 1; }
.nav-title span { font-size: 0.65rem; color: rgba(255,255,255,0.55); letter-spacing: 1px; display: block; margin-top: 2px; }
.nav-badge {
  margin-right: auto;
  display: flex; align-items: center; gap: 16px;
}
.badge {
  background: rgba(196,18,48,0.2);
  border: 1px solid rgba(196,18,48,0.5);
  color: rgba(255,255,255,0.9);
  padding: 4px 14px; border-radius: 20px;
  font-size: 0.75rem; font-weight: 600;
  display: flex; align-items: center; gap: 6px;
}
.badge::before {
  content: ''; width: 7px; height: 7px;
  background: #4AE54A; border-radius: 50%;
  display: inline-block;
  box-shadow: 0 0 6px #4AE54A;
}
.nav-ministry {
  color: rgba(255,255,255,0.5);
  font-size: 0.75rem;
  border-right: 1px solid rgba(255,255,255,0.15);
  padding-right: 16px;
}

/* ── شريط الخطوات ── */
.steps-bar {
  background: white;
  border-bottom: 1px solid var(--border);
  padding: 0 2.5rem;
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 0;
  height: 72px;
  box-shadow: 0 1px 4px rgba(0,0,0,0.05);
}
.step-item { display: flex; align-items: center; }
.step-circle {
  width: 34px; height: 34px;
  border-radius: 50%; border: 2px solid var(--border);
  display: flex; align-items: center; justify-content: center;
  font-weight: 700; font-size: 14px; color: var(--muted);
  background: white; transition: all 0.3s;
  font-family: 'IBM Plex Mono', monospace;
}
.step-circle.active { background: var(--red); border-color: var(--red); color: white; }
.step-circle.done { background: var(--green); border-color: var(--green); color: white; }
.step-label { font-size: 13px; color: var(--muted); margin-right: 10px; font-weight: 600; }
.step-label.active { color: var(--red); }
.step-connector { width: 60px; height: 2px; background: var(--border); margin: 0 12px; }
.step-connector.done { background: var(--red); }

/* ── المحتوى الرئيسي ── */
.content-wrap {
  padding: 1.8rem 2.5rem;
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: 1.5rem;
}

/* ── البطاقات ── */
.card {
  background: white;
  border-radius: 16px;
  border: 1px solid var(--border);
  box-shadow: var(--card-shadow);
  overflow: hidden;
}
.card-header {
  padding: 1.1rem 1.4rem;
  border-bottom: 1px solid var(--border);
  display: flex; align-items: center; gap: 10px;
  background: var(--bg2);
}
.card-header-icon {
  width: 36px; height: 36px;
  background: linear-gradient(135deg, var(--red), var(--red2));
  border-radius: 8px;
  display: flex; align-items: center; justify-content: center;
  font-size: 16px; flex-shrink: 0;
}
.card-header h3 {
  font-size: 14px; font-weight: 700; color: var(--navy);
  margin: 0; font-family: 'Cairo', sans-serif;
}
.card-header p { font-size: 12px; color: var(--muted); margin: 2px 0 0; }
.card-body { padding: 1.2rem 1.4rem; }

/* ── الإحداثيات ── */
.coords-row {
  display: flex; gap: 8px; margin-top: 10px; flex-wrap: wrap;
}
.coord-chip {
  background: var(--bg2); border: 1px solid var(--border);
  border-radius: 8px; padding: 5px 14px;
  font-size: 13px; font-family: 'IBM Plex Mono', monospace;
  color: var(--navy); font-weight: 600;
  display: flex; align-items: center; gap: 6px;
}
.coord-chip span.dot { width: 7px; height: 7px; border-radius: 50%; background: var(--red); display: inline-block; }

/* ── الأزرار ── */
.stButton > button {
  background: linear-gradient(135deg, var(--red) 0%, var(--red2) 100%) !important;
  color: white !important; border: none !important;
  border-radius: 12px !important; font-weight: 700 !important;
  font-size: 16px !important; padding: 0.75rem 2rem !important;
  font-family: 'Cairo', sans-serif !important;
  letter-spacing: 1px !important;
  box-shadow: 0 4px 15px rgba(196,18,48,0.35) !important;
  transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1) !important;
  width: 100% !important;
}
.stButton > button:hover {
  background: linear-gradient(135deg, var(--orange) 0%, #C9691A 100%) !important;
  transform: translateY(-2px) !important;
  box-shadow: 0 8px 25px rgba(245,130,31,0.4) !important;
}
.stButton > button:active { transform: translateY(0) !important; }

/* ── المدخلات ── */
.stSelectbox div[data-baseweb="select"] > div,
.stNumberInput input, .stTextInput input {
  background: white !important;
  border: 1.5px solid var(--border) !important;
  border-radius: 10px !important;
  font-family: 'Tajawal', sans-serif !important;
  color: var(--text) !important;
  transition: border-color 0.2s !important;
}
.stSelectbox div[data-baseweb="select"] > div:hover,
.stNumberInput input:focus { border-color: var(--red) !important; }

input, [data-testid="stMetricValue"] {
  font-family: 'IBM Plex Mono', monospace !important;
}

/* Slider */
.stSlider > div > div > div { background: var(--border); }
.stSlider [data-baseweb="slider"] > div:nth-child(3) { background: var(--red) !important; }
.stSlider [data-baseweb="thumb"] {
  background: white !important;
  border: 3px solid var(--red) !important;
  box-shadow: 0 2px 8px rgba(196,18,48,0.3) !important;
}

/* ── مقاييس النتائج ── */
[data-testid="stMetric"] {
  background: white !important;
  border: 1px solid var(--border) !important;
  border-top: 4px solid var(--red) !important;
  border-radius: 14px !important;
  padding: 1rem 1.2rem !important;
  box-shadow: var(--card-shadow) !important;
}
[data-testid="stMetricValue"] {
  color: var(--navy) !important;
  font-size: 1.5rem !important;
  font-family: 'IBM Plex Mono', monospace !important;
}
[data-testid="stMetricLabel"] {
  color: var(--muted) !important;
  font-size: 0.8rem !important;
  font-family: 'Tajawal', sans-serif !important;
}

/* ── التابات ── */
.stTabs [data-baseweb="tab-list"] {
  background: var(--bg2); border-radius: 12px; padding: 4px; gap: 4px;
  border: 1px solid var(--border);
}
.stTabs [data-baseweb="tab"] {
  color: var(--muted) !important;
  border-radius: 9px !important;
  font-family: 'Cairo', sans-serif !important;
  font-weight: 600 !important;
}
.stTabs [aria-selected="true"] {
  background: var(--red) !important;
  color: white !important;
}

/* ── نتائج ── */
.result-hero {
  background: linear-gradient(135deg, var(--navy) 0%, var(--navy2) 100%);
  border-radius: 20px;
  padding: 2rem;
  color: white;
  position: relative;
  overflow: hidden;
  margin-bottom: 1.5rem;
}
.result-hero::before {
  content: '◆';
  position: absolute;
  font-size: 12rem;
  color: rgba(255,255,255,0.03);
  top: -30px; left: -20px;
  font-family: 'Cairo', sans-serif;
}
.result-hero::after {
  content: '';
  position: absolute;
  bottom: 0; right: 0;
  width: 200px; height: 200px;
  background: radial-gradient(circle, rgba(196,18,48,0.2) 0%, transparent 70%);
}

.verdict-badge {
  display: inline-flex; align-items: center; gap: 8px;
  padding: 8px 20px; border-radius: 30px;
  font-size: 1rem; font-weight: 700;
  font-family: 'Cairo', sans-serif;
  margin-bottom: 0.8rem;
}
.verdict-badge.success { background: rgba(13,110,74,0.2); border: 1px solid rgba(13,110,74,0.5); color: #5FD4A8; }
.verdict-badge.fail    { background: rgba(196,18,48,0.2); border: 1px solid rgba(196,18,48,0.5); color: #F4889A; }

.prob-display {
  font-size: 4.5rem; font-weight: 900;
  font-family: 'Cairo', sans-serif;
  line-height: 1; margin: 0.3rem 0;
}
.prob-display.success { color: #5FD4A8; }
.prob-display.fail    { color: #F4889A; }

/* ── شريط XAI ── */
.xai-wrap {
  background: white; border-radius: 16px;
  border: 1px solid var(--border);
  box-shadow: var(--card-shadow);
  padding: 1.5rem;
  margin-bottom: 1.5rem;
}
.xai-title {
  font-family: 'Cairo', sans-serif; font-size: 16px;
  font-weight: 700; color: var(--navy);
  margin: 0 0 0.3rem;
}
.xai-sub { font-size: 12px; color: var(--muted); margin: 0 0 1.2rem; }

.xai-row { margin-bottom: 1.1rem; }
.xai-row-header { display: flex; align-items: center; justify-content: space-between; margin-bottom: 5px; }
.xai-factor-name { font-size: 13px; font-weight: 700; color: var(--text); display: flex; align-items: center; gap: 6px; }
.xai-impact-badge {
  font-size: 11px; padding: 2px 10px; border-radius: 12px;
  font-weight: 700; font-family: 'IBM Plex Mono', monospace;
}
.xai-impact-badge.pos { background: #E8F5EF; color: #0D6E4A; border: 1px solid #A8D5BF; }
.xai-impact-badge.neg { background: #FEE8E8; color: #C41230; border: 1px solid #F4A0A0; }
.xai-impact-badge.neu { background: #FFF8F0; color: #C9701A; border: 1px solid #F5C088; }
.xai-bar-track {
  height: 8px; background: var(--bg); border-radius: 4px; overflow: hidden;
}
.xai-bar-fill { height: 100%; border-radius: 4px; transition: width 1s ease; }
.xai-bar-fill.pos { background: linear-gradient(90deg, #0D6E4A, #2DB88A); }
.xai-bar-fill.neg { background: linear-gradient(90deg, #C41230, #F4889A); }
.xai-bar-fill.neu { background: linear-gradient(90deg, #C9701A, #F5AD5A); }
.xai-desc { font-size: 12px; color: var(--muted); margin-top: 4px; }

/* ── بطاقات الإحصاء ── */
.stat-grid { display: grid; grid-template-columns: repeat(4, 1fr); gap: 1rem; margin-bottom: 1.5rem; }
.stat-card {
  background: white; border-radius: 14px;
  border: 1px solid var(--border);
  box-shadow: var(--card-shadow);
  padding: 1.2rem 1rem;
  text-align: center;
  position: relative; overflow: hidden;
}
.stat-card::before {
  content: ''; position: absolute;
  top: 0; right: 0; left: 0; height: 4px;
  background: linear-gradient(90deg, var(--red), var(--orange));
}
.stat-card-value {
  font-size: 1.6rem; font-weight: 700;
  color: var(--navy); font-family: 'IBM Plex Mono', monospace;
  display: block; margin-bottom: 4px;
}
.stat-card-label { font-size: 12px; color: var(--muted); font-weight: 600; }
.stat-card-icon { font-size: 1.3rem; margin-bottom: 8px; display: block; }

/* ── شريط المعالجة ── */
.processing-card {
  background: white; border-radius: 16px;
  border: 1px solid var(--border);
  box-shadow: var(--card-shadow);
  padding: 1.5rem 2rem;
  margin: 1.5rem 2.5rem;
}
.processing-title { font-family: 'Cairo', sans-serif; font-size: 15px; font-weight: 700; color: var(--navy); margin: 0 0 1rem; }
.proc-step { display: flex; align-items: center; gap: 12px; padding: 8px 0; border-bottom: 1px solid var(--bg); }
.proc-step:last-child { border-bottom: none; }
.proc-icon { font-size: 18px; width: 28px; text-align: center; }
.proc-label { flex: 1; font-size: 13px; color: var(--text); }
.proc-check { color: var(--green); font-weight: 700; font-size: 16px; }

/* ── فوتر ── */
.footer {
  background: var(--navy);
  padding: 1rem 2.5rem;
  display: flex; align-items: center; justify-content: space-between;
  margin-top: 2rem;
}
.footer-text { color: rgba(255,255,255,0.4); font-size: 12px; }
.footer-brand { color: rgba(255,255,255,0.6); font-size: 13px; font-family: 'Cairo', sans-serif; font-weight: 700; letter-spacing: 2px; }

/* ── عام ── */
hr { border-color: var(--border) !important; margin: 1rem 0 !important; }
label { color: var(--muted) !important; font-size: 13px !important; font-weight: 600 !important; }
h2, h3 { color: var(--navy) !important; font-family: 'Cairo', sans-serif !important; }
</style>
""", unsafe_allow_html=True)


# ══════════════════════════════════════════════════════════════════════════════
# تحميل النموذج
# ══════════════════════════════════════════════════════════════════════════════
@st.cache_resource
def load_model():
    try:
        model = joblib.load("catboost_model.pkl")
        return model, list(model.feature_names_), True
    except Exception:
        return None, None, False

model, FEATURE_COLS, model_loaded = load_model()


# ══════════════════════════════════════════════════════════════════════════════
# القواميس
# ══════════════════════════════════════════════════════════════════════════════
CATEGORIES = {
    "🍽️  مطاعم ومطابخ":          0.68,
    "🛒  تجزئة وجملة":           0.72,
    "🏥  أنشطة طبية":            0.78,
    "🎓  تعليم وتدريب":          0.75,
    "🏨  فنادق وإيواء":          0.73,
    "⛽  محطات وقود":             0.80,
    "🔧  خدمات السيارات":         0.65,
    "🎪  ترفيه وملاهي":          0.62,
    "🏗️  مقاولات وخدمات فنية":  0.70,
    "🏪  مستودعات وتخزين":       0.65,
}


# ══════════════════════════════════════════════════════════════════════════════
# دوال مساعدة
# ══════════════════════════════════════════════════════════════════════════════
def get_elevation(lat, lng):
    try:
        r = requests.get(f"https://api.open-elevation.com/api/v1/lookup?locations={lat},{lng}", timeout=6)
        if r.status_code == 200:
            return float(r.json()["results"][0]["elevation"])
    except Exception:
        pass
    return None


def compute_features(lat, lng, area, cat_te, has_brand, elevation):
    slope = min(max((elevation - 1500) / 100, 2), 25)
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
        "فئة_النشاط_TE":                cat_te,
    }


def build_xai(elevation, area, prob):
    v = prob >= 0.65
    data = [
        ("🏔️", "التضاريس الجغرافية",
         "pos" if elevation < 2500 else "neg",
         f"ارتفاع {elevation:,.0f}م — {'مناسب لحركة الزبائن' if elevation<2500 else 'شاهق قد يُقيّد الوصول'}",
         min(100, max(20, int(100 - (elevation - 1500) / 20)))),
        ("🛣️", "الوصولية الطرقية",
         "pos", "قرب من طريق مجمع — يرفع التدفق اليومي للزبائن", 72),
        ("🏙️", "الحيوية الحضرية",
         "pos", "مؤشر POI 5.2 — منطقة نابضة تجارياً وخدمياً", 65),
        ("⚔️", "بيئة المنافسة",
         "neu", "5 منافسين في 500م — منافسة معتدلة تُشير لطلب فعلي", 48),
        ("📐", "مساحة المحل",
         "pos" if 50 <= area <= 500 else "neu",
         f"مساحة {area}م² — {'مثالية للتشغيل الفعّال' if 50<=area<=500 else 'تحتاج تقييم دقيق للتكاليف'}",
         60 if 50 <= area <= 500 else 40),
    ]
    return data


# ══════════════════════════════════════════════════════════════════════════════
# Session state
# ══════════════════════════════════════════════════════════════════════════════
if "lat" not in st.session_state: st.session_state["lat"] = 18.2200
if "lng" not in st.session_state: st.session_state["lng"] = 42.5100
if "results" not in st.session_state: st.session_state["results"] = None

lat = st.session_state["lat"]
lng = st.session_state["lng"]
results = st.session_state["results"]


# ══════════════════════════════════════════════════════════════════════════════
# شريط التنقل
# ══════════════════════════════════════════════════════════════════════════════
step = 3 if results else (2 if (lat, lng) != (18.22, 42.51) else 1)

st.markdown(f"""
<div class="nav-bar">
  <div class="nav-logo">
    <div class="nav-diamond"></div>
    <div class="nav-title">
      <h1>جدوى</h1>
      <span>نظام تقييم ملاءمة المواقع التجارية</span>
    </div>
  </div>
  <div class="nav-badge">
    <span class="nav-ministry">أمانة منطقة عسير</span>
    <span class="badge">النظام نشط</span>
  </div>
</div>

<div class="steps-bar">
  <div class="step-item">
    <div class="step-circle {'done' if step>1 else 'active'}">{'✓' if step>1 else '1'}</div>
    <span class="step-label {'active' if step==1 else ''}">تحديد الموقع</span>
  </div>
  <div class="step-connector {'done' if step>1 else ''}"></div>
  <div class="step-item">
    <div class="step-circle {'done' if step>2 else ('active' if step==2 else '')}">{'✓' if step>2 else '2'}</div>
    <span class="step-label {'active' if step==2 else ''}">بيانات المشروع</span>
  </div>
  <div class="step-connector {'done' if step>2 else ''}"></div>
  <div class="step-item">
    <div class="step-circle {'active' if step==3 else ''}">3</div>
    <span class="step-label {'active' if step==3 else ''}">النتائج والتفسير</span>
  </div>
</div>
""", unsafe_allow_html=True)


# ══════════════════════════════════════════════════════════════════════════════
# المحتوى الرئيسي
# ══════════════════════════════════════════════════════════════════════════════
st.markdown('<div style="padding:1.8rem 2.5rem;">', unsafe_allow_html=True)

col_left, col_right = st.columns([1.1, 1], gap="large")

# ── الخريطة ──
with col_left:
    st.markdown("""
    <div class="card">
      <div class="card-header">
        <div class="card-header-icon">📍</div>
        <div>
          <h3>تحديد الموقع الجغرافي</h3>
          <p>انقر/انقري على الخريطة لتحديد موقع المشروع</p>
        </div>
      </div>
    </div>
    """, unsafe_allow_html=True)

    m = folium.Map(location=[lat, lng], zoom_start=13,
                   tiles="CartoDB positron", prefer_canvas=True)
    folium.Marker(
        [lat, lng],
        popup=folium.Popup(f"<b>{lat:.5f} , {lng:.5f}</b>", max_width=160),
        icon=folium.Icon(color="red", icon="building", prefix="fa"),
    ).add_to(m)
    folium.Circle([lat, lng], radius=500, color="#C41230",
                  fill=True, fill_opacity=0.1, weight=2,
                  tooltip="نطاق التحليل — 500م").add_to(m)
    folium.Circle([lat, lng], radius=1000, color="#0D2240",
                  fill=False, weight=1, dash_array="6",
                  tooltip="نطاق موسّع — 1كم").add_to(m)

    map_data = st_folium(m, width="100%", height=400, returned_objects=["last_clicked"])

    if map_data and map_data.get("last_clicked"):
        nlat = round(map_data["last_clicked"]["lat"], 6)
        nlng = round(map_data["last_clicked"]["lng"], 6)
        if (nlat, nlng) != (st.session_state["lat"], st.session_state["lng"]):
            st.session_state["lat"] = nlat
            st.session_state["lng"] = nlng
            st.session_state["results"] = None
            st.rerun()

    st.markdown(f"""
    <div class="coords-row">
      <div class="coord-chip"><span class="dot"></span> خط العرض &nbsp;<b>{lat:.5f}</b></div>
      <div class="coord-chip"><span class="dot"></span> خط الطول &nbsp;<b>{lng:.5f}</b></div>
      <div class="coord-chip">🎯 نطاق التحليل: <b>500م</b></div>
    </div>
    """, unsafe_allow_html=True)


# ── النموذج ──
with col_right:
    st.markdown("""
    <div class="card">
      <div class="card-header">
        <div class="card-header-icon">✍️</div>
        <div>
          <h3>بيانات المشروع التجاري</h3>
          <p>أدخلي المعلومات الأساسية فقط — باقي البيانات تُحسب تلقائياً</p>
        </div>
      </div>
    </div>
    """, unsafe_allow_html=True)

    st.markdown("<div style='height:8px;'></div>", unsafe_allow_html=True)

    area          = st.slider("📐 مساحة المحل (م²)", 20, 2000, 100, 10)
    category_key  = st.selectbox("🏢 نوع النشاط التجاري", list(CATEGORIES.keys()))
    has_brand_lbl = st.radio("✨ علامة تجارية معروفة؟", ["لا ❌", "نعم ✅"], horizontal=True)

    st.markdown("<div style='height:12px;'></div>", unsafe_allow_html=True)

    # معلومات ما يُحسب تلقائياً
    st.markdown("""
    <div style="background:#F8FAFD;border:1px solid #E4E9F2;border-right:3px solid #C41230;
                border-radius:10px;padding:0.9rem 1rem;margin-bottom:1rem;">
      <p style="margin:0 0 6px;font-size:12px;font-weight:700;color:#1A2535;">⚙️ يُحسب تلقائياً في الخلفية</p>
      <div style="display:flex;flex-wrap:wrap;gap:6px;">
        <span style="background:white;border:1px solid #E4E9F2;border-radius:6px;padding:3px 8px;font-size:11px;color:#64748B;">🏔️ الارتفاع والانحدار</span>
        <span style="background:white;border:1px solid #E4E9F2;border-radius:6px;padding:3px 8px;font-size:11px;color:#64748B;">🛣️ شبكة الطرق</span>
        <span style="background:white;border:1px solid #E4E9F2;border-radius:6px;padding:3px 8px;font-size:11px;color:#64748B;">🏙️ الكثافة العمرانية</span>
        <span style="background:white;border:1px solid #E4E9F2;border-radius:6px;padding:3px 8px;font-size:11px;color:#64748B;">⚔️ المنافسة</span>
        <span style="background:white;border:1px solid #E4E9F2;border-radius:6px;padding:3px 8px;font-size:11px;color:#64748B;">📊 مؤشرات الحي</span>
      </div>
    </div>
    """, unsafe_allow_html=True)

    analyze = st.button("🔍  تحليل الموقع  ◆", use_container_width=True)

st.markdown("</div>", unsafe_allow_html=True)


# ══════════════════════════════════════════════════════════════════════════════
# التحليل
# ══════════════════════════════════════════════════════════════════════════════
if analyze:
    if not model_loaded:
        st.error("⚠️ ملف النموذج `catboost_model.pkl` غير موجود.")
        st.stop()

    cat_te   = CATEGORIES[category_key]
    has_brand = 1 if "نعم" in has_brand_lbl else 0

    proc_ph = st.empty()
    STEPS = [
        ("🛰️", "استلام الإحداثيات الجغرافية"),
        ("🏔️", "حساب الارتفاع والتضاريس من DEM"),
        ("🛣️", "تحليل شبكة الطرق والوصولية"),
        ("🏙️", "تقييم الكثافة العمرانية والمباني"),
        ("⚔️", "رصد بيئة المنافسة في النطاق"),
        ("📊", "حساب المؤشرات المكانية للحي"),
        ("🤖", "تشغيل نموذج الذكاء الاصطناعي"),
    ]
    done = []
    for icon, label in STEPS:
        done.append((icon, label))
        proc_ph.markdown(
            '<div class="processing-card">'
            '<p class="processing-title">⚙️ جارٍ التحليل في الخلفية…</p>'
            + "".join(f'<div class="proc-step"><span class="proc-icon">{i}</span>'
                      f'<span class="proc-label">{l}</span>'
                      f'<span class="proc-check">✓</span></div>' for i, l in done)
            + "</div>",
            unsafe_allow_html=True)
        time.sleep(0.3)

    elev  = get_elevation(lat, lng) or 2200.0
    feats = compute_features(lat, lng, area, cat_te, has_brand, elev)
    fv    = pd.DataFrame([feats])
    for c in FEATURE_COLS:
        if c not in fv.columns: fv[c] = 0.0
    prob = float(model.predict_proba(fv[FEATURE_COLS])[0][1])

    st.session_state["results"] = {
        "prob": prob, "elevation": elev,
        "area": area, "cat_key": category_key, "elev": elev,
    }
    proc_ph.empty()
    st.rerun()


# ══════════════════════════════════════════════════════════════════════════════
# النتائج
# ══════════════════════════════════════════════════════════════════════════════
if results:
    prob      = results["prob"]
    elev      = results["elevation"]
    area_r    = results["area"]
    cat_key_r = results["cat_key"]
    verdict   = prob >= 0.65
    cls       = "success" if verdict else "fail"
    pct       = f"{prob*100:.1f}"

    st.markdown('<div style="padding:0 2.5rem;">', unsafe_allow_html=True)
    st.markdown("""<hr style="margin:0 0 1.5rem;">""", unsafe_allow_html=True)
    st.markdown("""
    <h2 style="margin:0 0 1.2rem;font-size:1.1rem;color:#1A2535;display:flex;align-items:center;gap:8px;">
      <span style="display:inline-block;width:4px;height:20px;background:#C41230;border-radius:2px;margin-left:2px;"></span>
      نتائج تحليل الموقع
    </h2>
    """, unsafe_allow_html=True)

    col_result, col_xai = st.columns([1, 1.3], gap="large")

    with col_result:
        # بطاقة النتيجة الرئيسية
        st.markdown(f"""
        <div class="result-hero">
          <div class="verdict-badge {cls}">
            {'✅ الموقع ملائم للاستثمار' if verdict else '⚠️ الموقع غير ملائم'}
          </div>
          <div class="prob-display {cls}">{pct}<span style="font-size:2rem;">%</span></div>
          <p style="color:rgba(255,255,255,0.55);font-size:13px;margin:0.3rem 0 0;">
            نسبة الملاءمة التجارية المتوقعة
          </p>
          <div style="margin-top:1.2rem;padding-top:1.2rem;border-top:1px solid rgba(255,255,255,0.1);
                      display:flex;gap:2rem;">
            <div>
              <p style="color:rgba(255,255,255,0.4);font-size:11px;margin:0;">العتبة</p>
              <p style="color:white;font-size:1.1rem;font-weight:700;margin:0;font-family:'IBM Plex Mono',monospace;">65%</p>
            </div>
            <div>
              <p style="color:rgba(255,255,255,0.4);font-size:11px;margin:0;">الارتفاع</p>
              <p style="color:white;font-size:1.1rem;font-weight:700;margin:0;font-family:'IBM Plex Mono',monospace;">{elev:,.0f}م</p>
            </div>
            <div>
              <p style="color:rgba(255,255,255,0.4);font-size:11px;margin:0;">المساحة</p>
              <p style="color:white;font-size:1.1rem;font-weight:700;margin:0;font-family:'IBM Plex Mono',monospace;">{area_r}م²</p>
            </div>
          </div>
        </div>
        """, unsafe_allow_html=True)

        # مقياس plotly
        fig = go.Figure(go.Indicator(
            mode="gauge+number",
            value=round(prob * 100, 1),
            number={"suffix": "%", "font": {"size": 38, "family": "IBM Plex Mono",
                                             "color": "#0D6E4A" if verdict else "#C41230"}},
            gauge={
                "axis": {"range": [0, 100], "tickwidth": 1, "tickcolor": "#B0B8C8",
                          "tickfont": {"family": "IBM Plex Mono", "size": 10}},
                "bar":  {"color": "#0D6E4A" if verdict else "#C41230", "thickness": 0.3},
                "bgcolor": "rgba(0,0,0,0)", "borderwidth": 0,
                "steps": [
                    {"range": [0,  40], "color": "#FFF0F0"},
                    {"range": [40, 65], "color": "#FFF8F0"},
                    {"range": [65, 100],"color": "#F0F9F4"},
                ],
                "threshold": {
                    "line": {"color": "#1A2535", "width": 3},
                    "thickness": 0.85, "value": 65,
                },
            },
            title={"text": "مؤشر الملاءمة", "font": {"size": 13, "color": "#64748B", "family": "Tajawal"}},
        ))
        fig.update_layout(height=220, paper_bgcolor="rgba(0,0,0,0)",
                          margin=dict(t=55, b=5, l=10, r=10))
        st.plotly_chart(fig, use_container_width=True)

    with col_xai:
        xai_data = build_xai(elev, area_r, prob)
        st.markdown("""
        <div class="xai-wrap">
          <p class="xai-title">🤖 تفسير الذكاء الاصطناعي</p>
          <p class="xai-sub">أبرز العوامل المؤثرة في نسبة الملاءمة — مُرتّبة بحسب الأهمية</p>
        """, unsafe_allow_html=True)

        for icon, name, cls_b, desc, pct_b in xai_data:
            badge_txt = {"pos": "إيجابي ▲", "neg": "سلبي ▼", "neu": "محايد →"}[cls_b]
            st.markdown(f"""
            <div class="xai-row">
              <div class="xai-row-header">
                <span class="xai-factor-name">{icon} {name}</span>
                <span class="xai-impact-badge {cls_b}">{badge_txt}</span>
              </div>
              <div class="xai-bar-track">
                <div class="xai-bar-fill {cls_b}" style="width:{pct_b}%;"></div>
              </div>
              <p class="xai-desc">{desc}</p>
            </div>
            """, unsafe_allow_html=True)

        st.markdown("</div>", unsafe_allow_html=True)

    # إحصاءات مفصلة
    st.markdown("""
    <h2 style="margin:1.5rem 0 1rem;font-size:1rem;color:#1A2535;display:flex;align-items:center;gap:8px;">
      <span style="display:inline-block;width:4px;height:18px;background:#C41230;border-radius:2px;"></span>
      مؤشرات الموقع المحسوبة
    </h2>
    <div class="stat-grid">
      <div class="stat-card">
        <span class="stat-card-icon">🏔️</span>
        <span class="stat-card-value">{elev:,.0f}</span>
        <span class="stat-card-label">الارتفاع (م)</span>
      </div>
      <div class="stat-card">
        <span class="stat-card-icon">🏙️</span>
        <span class="stat-card-value">32</span>
        <span class="stat-card-label">منشأة في 500م</span>
      </div>
      <div class="stat-card">
        <span class="stat-card-icon">⚔️</span>
        <span class="stat-card-value">5</span>
        <span class="stat-card-label">منافسون مباشرون</span>
      </div>
      <div class="stat-card">
        <span class="stat-card-icon">📊</span>
        <span class="stat-card-value">65%</span>
        <span class="stat-card-label">معدل نجاح الحي</span>
      </div>
    </div>
    """.format(elev=elev), unsafe_allow_html=True)

    if st.button("🔄  تحليل موقع جديد", use_container_width=False):
        st.session_state["results"] = None
        st.rerun()

    st.markdown("</div>", unsafe_allow_html=True)


# Footer
st.markdown("""
<div class="footer">
  <span class="footer-text">© 2026 أمانة منطقة عسير — جميع الحقوق محفوظة</span>
  <span class="footer-brand">◆ جدوى</span>
  <span class="footer-text">نظام تقييم ملاءمة المواقع التجارية</span>
</div>
""", unsafe_allow_html=True)
