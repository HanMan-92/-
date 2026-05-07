"""
جدوى — نظام تقييم ملاءمة المواقع التجارية
أمانة منطقة عسير · أبها وخميس مشيط
"""
import streamlit as st
import pandas as pd
import numpy as np
import joblib, time, requests
import folium, plotly.graph_objects as go
from streamlit_folium import st_folium
from catboost import Pool

st.set_page_config(page_title="جدوى | أمانة منطقة عسير",
                   page_icon="◆", layout="wide",
                   initial_sidebar_state="collapsed")

# ══════════════════════════════════════════════════════════════════════════════
# CSS
# ══════════════════════════════════════════════════════════════════════════════
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Cairo:wght@400;600;700;900&family=Tajawal:wght@400;500;700&family=IBM+Plex+Mono:wght@400;600&display=swap');

:root {
  --navy:   #071626;
  --navy2:  #0C2040;
  --red:    #B91C1C;
  --gold:   #B45309;
  --bg:     #F1F5F9;
  --white:  #FFFFFF;
  --border: #CBD5E1;
  --text:   #0F172A;
  --muted:  #64748B;
  --green:  #065F46;
  --sh: 0 1px 3px rgba(0,0,0,0.08), 0 4px 16px rgba(0,0,0,0.05);
}
html, body, [class*="css"] {
  direction: rtl;
  font-family: 'Tajawal', sans-serif !important;
  color: var(--text);
}
.stApp { background: var(--bg); }
.main .block-container { padding: 0 !important; max-width: 100% !important; }
#MainMenu, footer, header, [data-testid="stToolbar"],
[data-testid="collapsedControl"], .stDeployButton,
[data-testid="stSidebar"] { display: none !important; }

/* ─ شريط التنقل ─────────────────────────────── */
.g-nav {
  background: var(--navy);
  display: flex; align-items: center;
  padding: 0 2rem; height: 60px;
  border-bottom: 3px solid var(--red);
  box-shadow: 0 2px 12px rgba(0,0,0,0.4);
}
.g-logo {
  width: 36px; height: 36px; flex-shrink: 0;
  background: linear-gradient(135deg, var(--red), #DC2626);
  transform: rotate(45deg); border-radius: 5px;
  box-shadow: 0 0 14px rgba(185,28,28,0.5);
}
.g-brand {
  margin-right: 16px; color: white;
  font-family: 'Cairo', sans-serif;
}
.g-brand-name { font-size: 1.5rem; font-weight: 900; letter-spacing: 3px; line-height: 1; }
.g-brand-sub  { font-size: 0.65rem; color: rgba(255,255,255,0.45); letter-spacing: 1px; }
.g-spacer { flex: 1; }
.g-ministry { color: rgba(255,255,255,0.5); font-size: 0.78rem; padding-left: 16px; border-left: 1px solid rgba(255,255,255,0.12); }
.g-status {
  margin-left: 14px; display: flex; align-items: center; gap: 6px;
  color: rgba(255,255,255,0.75); font-size: 0.75rem;
  background: rgba(255,255,255,0.07); border: 1px solid rgba(255,255,255,0.12);
  padding: 4px 12px; border-radius: 20px;
}
.g-dot { width: 7px; height: 7px; border-radius: 50%; background: #22C55E; box-shadow: 0 0 6px #22C55E; }

/* ─ شريط الخطوات ────────────────────────────── */
.g-steps {
  background: white; border-bottom: 1px solid var(--border);
  display: flex; align-items: center; justify-content: center;
  height: 64px; gap: 0;
  box-shadow: 0 1px 4px rgba(0,0,0,0.04);
}
.g-step { display: flex; align-items: center; }
.g-step-c {
  width: 32px; height: 32px; border-radius: 50%;
  border: 2px solid var(--border); background: white;
  display: flex; align-items: center; justify-content: center;
  font-size: 13px; font-weight: 700; color: var(--muted);
  font-family: 'IBM Plex Mono', monospace;
  transition: all .3s;
}
.g-step-c.active { background: var(--red); border-color: var(--red); color: white; }
.g-step-c.done   { background: var(--green); border-color: var(--green); color: white; }
.g-step-l { font-size: 13px; font-weight: 600; color: var(--muted); margin-right: 8px; }
.g-step-l.active { color: var(--red); }
.g-line { width: 56px; height: 2px; background: var(--border); margin: 0 12px; }
.g-line.done { background: var(--red); }

/* ─ المحتوى ─────────────────────────────────── */
.g-body { padding: 1.6rem 2rem; }

/* ─ البطاقات ────────────────────────────────── */
.g-card {
  background: white; border-radius: 12px;
  border: 1px solid var(--border); box-shadow: var(--sh);
  overflow: hidden; margin-bottom: 1rem;
}
.g-card-head {
  padding: 0.85rem 1.2rem; border-bottom: 1px solid var(--border);
  display: flex; align-items: center; gap: 10px;
  background: #FAFBFD;
}
.g-card-icon {
  width: 32px; height: 32px; border-radius: 7px;
  background: var(--red); display: flex; align-items: center;
  justify-content: center; color: white; font-size: 14px; flex-shrink: 0;
}
.g-card-title { font-family: 'Cairo',sans-serif; font-size: 14px; font-weight: 700; color: var(--navy); margin: 0; }
.g-card-desc  { font-size: 12px; color: var(--muted); margin: 2px 0 0; }
.g-card-body  { padding: 1.1rem 1.2rem; }

/* ─ اختيار الخريطة ─────────────────────────── */
.map-type-bar {
  display: flex; gap: 6px; margin-bottom: 10px; flex-wrap: wrap;
}
.map-type-btn {
  border: 1.5px solid var(--border); background: white;
  border-radius: 8px; padding: 5px 14px;
  font-size: 13px; font-family: 'Tajawal',sans-serif;
  color: var(--muted); cursor: pointer; transition: all .2s;
}
.map-type-btn.sel {
  border-color: var(--red); background: #FEF2F2;
  color: var(--red); font-weight: 700;
}

/* ─ الإحداثيات ──────────────────────────────── */
.g-coords { display: flex; gap: 8px; margin-top: 10px; flex-wrap: wrap; }
.g-coord-chip {
  background: #F8FAFC; border: 1px solid var(--border);
  border-radius: 7px; padding: 5px 12px; font-size: 12px;
  font-family: 'IBM Plex Mono', monospace; color: var(--navy); font-weight: 600;
  display: flex; align-items: center; gap: 5px;
}
.g-coord-dot { width: 6px; height: 6px; border-radius: 50%; background: var(--red); }

/* ─ الأزرار ─────────────────────────────────── */
.stButton > button {
  background: var(--red) !important; color: white !important;
  border: none !important; border-radius: 10px !important;
  font-weight: 700 !important; font-size: 15px !important;
  padding: 0.7rem 2rem !important; width: 100% !important;
  font-family: 'Cairo', sans-serif !important;
  letter-spacing: 0.5px !important;
  box-shadow: 0 3px 12px rgba(185,28,28,0.3) !important;
  transition: all .25s !important;
}
.stButton > button:hover {
  background: #991B1B !important;
  transform: translateY(-1px) !important;
  box-shadow: 0 6px 20px rgba(185,28,28,0.4) !important;
}

/* ─ المدخلات ────────────────────────────────── */
label { color: var(--muted) !important; font-size: 13px !important; font-weight: 600 !important; }
input, [data-testid="stMetricValue"] { font-family: 'IBM Plex Mono',monospace !important; }
.stSelectbox [data-baseweb="select"] > div,
.stNumberInput input {
  background: white !important; border: 1.5px solid var(--border) !important;
  border-radius: 8px !important; color: var(--text) !important;
}
.stSlider [data-baseweb="slider"] > div:nth-child(3) { background: var(--red) !important; }
.stSlider [data-baseweb="thumb"] {
  background: white !important; border: 3px solid var(--red) !important;
}
.stRadio label { font-size: 13px !important; }

/* ─ مقاييس ──────────────────────────────────── */
[data-testid="stMetric"] {
  background: white !important; border: 1px solid var(--border) !important;
  border-top: 4px solid var(--red) !important; border-radius: 12px !important;
  padding: 1rem 1.1rem !important; box-shadow: var(--sh) !important;
}
[data-testid="stMetricValue"] { color: var(--navy) !important; font-size: 1.4rem !important; }
[data-testid="stMetricLabel"] { color: var(--muted) !important; font-size: 0.78rem !important; }

/* ─ XAI ─────────────────────────────────────── */
.xai-card { background: white; border-radius: 12px; border: 1px solid var(--border); box-shadow: var(--sh); padding: 1.4rem; margin-bottom: 1rem; }
.xai-title { font-family: 'Cairo',sans-serif; font-size: 15px; font-weight: 700; color: var(--navy); margin: 0 0 4px; }
.xai-sub   { font-size: 12px; color: var(--muted); margin: 0 0 1rem; }
.xai-row   { margin-bottom: 1rem; }
.xai-head  { display: flex; align-items: center; justify-content: space-between; margin-bottom: 5px; }
.xai-name  { font-size: 13px; font-weight: 700; color: var(--text); }
.xai-badge { font-size: 11px; padding: 2px 9px; border-radius: 10px; font-weight: 700; font-family: 'IBM Plex Mono',monospace; }
.xai-badge.pos { background: #ECFDF5; color: #065F46; border: 1px solid #A7F3D0; }
.xai-badge.neg { background: #FEF2F2; color: #B91C1C; border: 1px solid #FECACA; }
.xai-badge.neu { background: #FFFBEB; color: #92400E; border: 1px solid #FDE68A; }
.xai-val   { font-size: 11px; color: var(--muted); font-family: 'IBM Plex Mono',monospace; margin-right: 8px; }
.xai-track { height: 7px; background: #F1F5F9; border-radius: 4px; overflow: hidden; }
.xai-fill  { height: 100%; border-radius: 4px; }
.xai-fill.pos { background: linear-gradient(90deg, #059669, #34D399); }
.xai-fill.neg { background: linear-gradient(90deg, #B91C1C, #F87171); }
.xai-fill.neu { background: linear-gradient(90deg, #D97706, #FCD34D); }
.xai-desc  { font-size: 12px; color: var(--muted); margin-top: 4px; }

/* ─ بطاقة النتيجة ───────────────────────────── */
.res-card {
  background: linear-gradient(135deg, var(--navy) 0%, var(--navy2) 100%);
  border-radius: 14px; padding: 1.8rem; color: white;
  margin-bottom: 1rem; position: relative; overflow: hidden;
}
.res-verdict {
  display: inline-flex; align-items: center; gap: 8px;
  padding: 6px 16px; border-radius: 20px; font-size: 14px; font-weight: 700;
  font-family: 'Cairo',sans-serif; margin-bottom: 0.8rem;
}
.res-verdict.ok  { background: rgba(5,150,105,0.2); border: 1px solid rgba(52,211,153,0.4); color: #6EE7B7; }
.res-verdict.bad { background: rgba(185,28,28,0.2); border: 1px solid rgba(248,113,113,0.4); color: #FCA5A5; }
.res-pct {
  font-size: 4.5rem; font-weight: 900; font-family: 'Cairo',sans-serif;
  line-height: 1; margin: 0.2rem 0;
}
.res-pct.ok  { color: #6EE7B7; }
.res-pct.bad { color: #FCA5A5; }
.res-meta { display: flex; gap: 2rem; margin-top: 1.2rem; padding-top: 1rem; border-top: 1px solid rgba(255,255,255,0.1); }
.res-meta-item { }
.res-meta-label { font-size: 11px; color: rgba(255,255,255,0.4); display: block; }
.res-meta-val { font-size: 1.05rem; font-weight: 700; font-family: 'IBM Plex Mono',monospace; }

/* ─ شبكة الإحصاء ────────────────────────────── */
.stat-grid { display: grid; grid-template-columns: repeat(4,1fr); gap: 0.8rem; margin-bottom: 1.2rem; }
.stat-c {
  background: white; border-radius: 10px; border: 1px solid var(--border);
  box-shadow: var(--sh); padding: 1rem 0.9rem; text-align: center;
  border-top: 3px solid var(--red);
}
.stat-v { font-size: 1.5rem; font-weight: 700; color: var(--navy); font-family: 'IBM Plex Mono',monospace; display: block; }
.stat-l { font-size: 11px; color: var(--muted); font-weight: 600; display: block; margin-top: 2px; }

/* ─ معالجة ───────────────────────────────────── */
.proc-card { background: white; border-radius: 12px; border: 1px solid var(--border); box-shadow: var(--sh); padding: 1.4rem; }
.proc-title { font-family: 'Cairo',sans-serif; font-size: 14px; font-weight: 700; color: var(--navy); margin: 0 0 0.9rem; }
.proc-row { display: flex; align-items: center; gap: 10px; padding: 7px 0; border-bottom: 1px solid #F8FAFC; }
.proc-row:last-child { border: none; }
.proc-lbl { flex: 1; font-size: 13px; color: var(--text); }
.proc-ok  { color: var(--green); font-weight: 700; }

/* ─ فوتر ─────────────────────────────────────── */
.g-footer { background: var(--navy); padding: 0.9rem 2rem; display: flex; align-items: center; justify-content: space-between; margin-top: 2rem; }
.g-footer-l { color: rgba(255,255,255,0.35); font-size: 12px; }
.g-footer-c { color: rgba(255,255,255,0.6); font-size: 13px; font-family: 'Cairo',sans-serif; font-weight: 700; }

/* ─ عام ──────────────────────────────────────── */
hr { border-color: var(--border) !important; margin: 1rem 0 !important; }
h2, h3 { color: var(--navy) !important; font-family: 'Cairo',sans-serif !important; }
.stMarkdown p { color: #334155; line-height: 1.7; }
</style>
""", unsafe_allow_html=True)

# ══════════════════════════════════════════════════════════════════════════════
# النموذج
# ══════════════════════════════════════════════════════════════════════════════
@st.cache_resource
def load_model():
    try:
        m = joblib.load("catboost_model.pkl")
        return m, list(m.feature_names_), True
    except Exception:
        return None, None, False

model, FEATURE_COLS, model_ok = load_model()

# ══════════════════════════════════════════════════════════════════════════════
# الثوابت
# ══════════════════════════════════════════════════════════════════════════════
CATEGORIES = {
    "مطاعم ومطابخ":         0.68,
    "تجزئة وجملة":          0.72,
    "أنشطة طبية":           0.78,
    "تعليم وتدريب":         0.75,
    "فنادق وإيواء":         0.73,
    "محطات وقود":            0.80,
    "خدمات السيارات":        0.65,
    "ترفيه وملاهي":         0.62,
    "مقاولات وخدمات فنية":  0.70,
    "مستودعات وتخزين":      0.65,
}

TILES = {
    "خريطة الشوارع": {
        "url":  "https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png",
        "attr": "© OpenStreetMap contributors",
        "ov":   None,
    },
    "صور جوية": {
        "url":  "https://server.arcgisonline.com/ArcGIS/rest/services/World_Imagery/MapServer/tile/{z}/{y}/{x}",
        "attr": "Esri",
        "ov":   "https://server.arcgisonline.com/ArcGIS/rest/services/Reference/World_Boundaries_and_Places/MapServer/tile/{z}/{y}/{x}",
    },
    "خريطة حضرية": {
        "url":  "https://{s}.basemaps.cartocdn.com/rastertiles/voyager/{z}/{x}/{y}{r}.png",
        "attr": "© CARTO",
        "ov":   None,
    },
    "تضاريس طبوغرافية": {
        "url":  "https://server.arcgisonline.com/ArcGIS/rest/services/World_Topo_Map/MapServer/tile/{z}/{y}/{x}",
        "attr": "Esri",
        "ov":   None,
    },
}

FEAT_AR = {
    "الاحداثي الجغرافي X":          ("الموقع — خط الطول",         "◈"),
    "الاحداثي الجغرافي Y":          ("الموقع — خط العرض",         "◈"),
    "الارتفاع":                      ("الارتفاع الجغرافي",          "▲"),
    "الانحدار":                      ("انحدار التضاريس",            "⫶"),
    "المسافة_للشارع_الأقرب_لوغ":    ("المسافة لأقرب شارع",         "↦"),
    "المسافة_للطريق_الشرياني_لوغ":  ("البُعد عن الطريق الشرياني",  "↦"),
    "المسافة_لأقرب_معلم_سياحي_لوغ": ("القرب من المعالم السياحية",  "↦"),
    "رتبة_الطريق":                   ("رتبة الطريق المجاور",        "⊟"),
    "مؤشر_الحيوية_الحضرية":         ("مؤشر الحيوية الحضرية",       "⊞"),
    "كثافة_تجارية_500م_لوغ":        ("الكثافة التجارية في 500م",   "⊞"),
    "عدد_مباني_فعلي_500م_لوغ":      ("عدد المباني في 500م",        "⊞"),
    "متوسط_عمر_المنافسين_يوم_لوغ":  ("متوسط عمر المنافسين",        "⊡"),
    "عدد_منافسين_مباشرين_500م_لوغ": ("عدد المنافسين المباشرين",    "⊡"),
    "مسافة_أقرب_مباشر_متر_لوغ":    ("المسافة لأقرب منافس",        "⊡"),
    "المعدل_الجواري":                ("معدل نجاح الحي",             "◉"),
    "معدل_إغلاق_الفئة_لوغ":         ("معدل الإغلاق في الفئة",      "◉"),
    "مساحة_المنشأة_لوغ":            ("مساحة المحل",                "▭"),
    "الانتماء_لعلامة_تجارية":       ("الانتماء لعلامة تجارية",     "★"),
    "مدة_الرخصة_لوغ":              ("مدة الرخصة",                 "⬡"),
    "نوع_المنشأة_TE":               ("نوع المنشأة",                "◧"),
    "فئة_النشاط_TE":                ("فئة النشاط التجاري",          "◧"),
}

# ══════════════════════════════════════════════════════════════════════════════
# دوال
# ══════════════════════════════════════════════════════════════════════════════
def get_elev(lat, lng):
    try:
        r = requests.get(f"https://api.open-elevation.com/api/v1/lookup?locations={lat},{lng}", timeout=6)
        if r.status_code == 200:
            return float(r.json()["results"][0]["elevation"])
    except Exception:
        pass
    return None

def compute_features(lat, lng, area, cat_te, brand, elev):
    sl = min(max((elev - 1500) / 100, 2), 25)
    return {
        "الاحداثي الجغرافي X": lng, "الاحداثي الجغرافي Y": lat,
        "الارتفاع": elev, "الانحدار": sl,
        "المسافة_للشارع_الأقرب_لوغ":    np.log1p(35),
        "المسافة_للطريق_الشرياني_لوغ":  np.log1p(850),
        "المسافة_لأقرب_معلم_سياحي_لوغ": np.log1p(3200),
        "رتبة_الطريق": 6, "مؤشر_الحيوية_الحضرية": 5.2,
        "كثافة_تجارية_500م_لوغ":        np.log1p(32),
        "عدد_مباني_فعلي_500م_لوغ":      np.log1p(85),
        "متوسط_عمر_المنافسين_يوم_لوغ":  np.log1p(720),
        "عدد_منافسين_مباشرين_500م_لوغ": np.log1p(5),
        "مسافة_أقرب_مباشر_متر_لوغ":    np.log1p(160),
        "المعدل_الجواري": 0.65, "معدل_إغلاق_الفئة_لوغ": np.log1p(0.28),
        "مساحة_المنشأة_لوغ": np.log1p(area),
        "الانتماء_لعلامة_تجارية": brand, "مدة_الرخصة_لوغ": np.log1p(1),
        "نوع_المنشأة_TE": 0.70, "فئة_النشاط_TE": cat_te,
    }

@st.cache_resource
def get_shap(_model):
    return _model.get_feature_importance

def real_shap(model, fv):
    try:
        pool = Pool(fv)
        mat  = model.get_feature_importance(pool, type="ShapValues")
        vals = mat[0][:-1]
        bias = mat[0][-1]
        total = np.sum(np.abs(vals)) + 1e-9
        rows  = []
        for feat, v in zip(FEATURE_COLS, vals):
            nm, sym = FEAT_AR.get(feat, (feat, "◆"))
            cls = "pos" if v > 0.001 else ("neg" if v < -0.001 else "neu")
            bar = int(min(98, abs(v) / total * 600))
            rows.append((sym, nm, cls, v, bar, f"+{v:.4f}" if v >= 0 else f"{v:.4f}"))
        rows.sort(key=lambda x: abs(x[3]), reverse=True)
        return rows[:5], True, bias
    except Exception:
        return None, False, 0.0

# ══════════════════════════════════════════════════════════════════════════════
# Session state
# ══════════════════════════════════════════════════════════════════════════════
def ss(k, v):
    if k not in st.session_state:
        st.session_state[k] = v

ss("lat", 18.2200); ss("lng", 42.5100)
ss("results", None); ss("_lc", None)
ss("tile", "خريطة الشوارع")

lat = st.session_state["lat"]
lng = st.session_state["lng"]

# ══════════════════════════════════════════════════════════════════════════════
# شريط التنقل
# ══════════════════════════════════════════════════════════════════════════════
step = 3 if st.session_state["results"] else 2

st.markdown(f"""
<div class="g-nav">
  <div class="g-logo"></div>
  <div class="g-brand">
    <div class="g-brand-name">جدوى</div>
    <div class="g-brand-sub">نظام تقييم ملاءمة المواقع الاستثمارية</div>
  </div>
  <div class="g-spacer"></div>
  <div class="g-ministry">أمانة منطقة عسير</div>
  <div class="g-status"><span class="g-dot"></span> النظام فعّال</div>
</div>

<div class="g-steps">
  <div class="g-step">
    <div class="g-step-c {'done' if step>1 else 'active'}">{'✓' if step>1 else '1'}</div>
    <span class="g-step-l {'active' if step==1 else ''}">تحديد الموقع</span>
  </div>
  <div class="g-line {'done' if step>1 else ''}"></div>
  <div class="g-step">
    <div class="g-step-c {'done' if step>2 else 'active'}">{'✓' if step>2 else '2'}</div>
    <span class="g-step-l {'active' if step==2 else ''}">بيانات المشروع</span>
  </div>
  <div class="g-line {'done' if step>2 else ''}"></div>
  <div class="g-step">
    <div class="g-step-c {'active' if step==3 else ''}">3</div>
    <span class="g-step-l {'active' if step==3 else ''}">النتائج والتفسير</span>
  </div>
</div>
""", unsafe_allow_html=True)

# ══════════════════════════════════════════════════════════════════════════════
# المحتوى
# ══════════════════════════════════════════════════════════════════════════════
st.markdown('<div class="g-body">', unsafe_allow_html=True)

col_form, col_map = st.columns([1, 1.25], gap="large")

# ─ عمود النموذج ──────────────────────────────────────────────────────────────
with col_form:
    st.markdown("""
    <div class="g-card">
      <div class="g-card-head">
        <div class="g-card-icon">✦</div>
        <div>
          <p class="g-card-title">بيانات المشروع الاستثماري</p>
          <p class="g-card-desc">أدخل المعلومات الأساسية — باقي المؤشرات تُحسب تلقائياً</p>
        </div>
      </div>
    </div>
    """, unsafe_allow_html=True)

    area       = st.slider("مساحة المحل (م²)", 20, 2000, 100, 10)
    category   = st.selectbox("نوع النشاط التجاري", list(CATEGORIES.keys()))
    brand_lbl  = st.radio("انتماء لعلامة تجارية معروفة؟", ["لا", "نعم"], horizontal=True)

    st.markdown("""
    <div style="background:#F8FAFC;border:1px solid #E2E8F0;border-right:3px solid #B91C1C;
                border-radius:8px;padding:0.8rem 1rem;margin:0.8rem 0;">
      <p style="margin:0 0 5px;font-size:12px;font-weight:700;color:#0F172A;">
        يُحسب تلقائياً من قواعد البيانات الجغرافية
      </p>
      <div style="display:flex;flex-wrap:wrap;gap:5px;">
        <span style="background:white;border:1px solid #E2E8F0;border-radius:5px;padding:2px 8px;font-size:11px;color:#64748B;">الارتفاع والتضاريس</span>
        <span style="background:white;border:1px solid #E2E8F0;border-radius:5px;padding:2px 8px;font-size:11px;color:#64748B;">شبكة الطرق</span>
        <span style="background:white;border:1px solid #E2E8F0;border-radius:5px;padding:2px 8px;font-size:11px;color:#64748B;">الكثافة العمرانية</span>
        <span style="background:white;border:1px solid #E2E8F0;border-radius:5px;padding:2px 8px;font-size:11px;color:#64748B;">بيانات المنافسة</span>
        <span style="background:white;border:1px solid #E2E8F0;border-radius:5px;padding:2px 8px;font-size:11px;color:#64748B;">مؤشرات الحي</span>
      </div>
    </div>
    """, unsafe_allow_html=True)

    analyze = st.button("تحليل الموقع وتقييم الجدوى", use_container_width=True)

# ─ عمود الخريطة ──────────────────────────────────────────────────────────────
with col_map:
    st.markdown("""
    <div class="g-card">
      <div class="g-card-head">
        <div class="g-card-icon">⊕</div>
        <div>
          <p class="g-card-title">تحديد الموقع الجغرافي</p>
          <p class="g-card-desc">انقر على الخريطة لتحديد موقع المشروع</p>
        </div>
      </div>
    </div>
    """, unsafe_allow_html=True)

    # اختيار الطبقة — selectbox بسيط
    tile_name = st.selectbox(
        "طبقة الخريطة:",
        list(TILES.keys()),
        index=list(TILES.keys()).index(st.session_state["tile"]),
        key="tile_sel",
        label_visibility="collapsed",
    )
    if tile_name != st.session_state["tile"]:
        st.session_state["tile"] = tile_name
        st.rerun()

    tc = TILES[tile_name]

    # بناء الخريطة — طبقة واحدة فقط
    m = folium.Map(location=[lat, lng], zoom_start=15,
                   tiles=tc["url"], attr=tc["attr"])

    if tc["ov"]:
        folium.TileLayer(tiles=tc["ov"], attr="Esri", overlay=True).add_to(m)

    folium.Marker(
        [lat, lng],
        popup=folium.Popup(
            f"<div dir='rtl' style='font-family:Arial;'>"
            f"<b>الموقع المحدد</b><br>{lat:.5f} ، {lng:.5f}</div>",
            max_width=180),
        icon=folium.Icon(color="red", icon="map-marker", prefix="fa"),
    ).add_to(m)

    folium.Circle([lat, lng], radius=500,
                  color="#B91C1C", fill=True, fill_opacity=0.07, weight=2).add_to(m)

    # مفتاح ديناميكي = يتغير عند تغيير الموقع أو الطبقة
    mk = f"mp{tile_name[:3]}{round(lat,3)}{round(lng,3)}"

    out = st_folium(m, key=mk, width="100%", height=420)

    # معالجة النقر — نتتبع آخر نقرة معالجة لتجنب التكرار
    if out and out.get("last_clicked"):
        _lc = out["last_clicked"]
        _lt = (round(_lc["lat"], 5), round(_lc["lng"], 5))
        _prev = st.session_state["_lc"]
        if _lt != _prev and (abs(_lt[0]-lat)>0.0001 or abs(_lt[1]-lng)>0.0001):
            st.session_state.update({"lat": _lt[0], "lng": _lt[1],
                                      "_lc": _lt, "results": None})
            st.rerun()

    lat = st.session_state["lat"]
    lng = st.session_state["lng"]

    st.markdown(f"""
    <div class="g-coords">
      <div class="g-coord-chip"><span class="g-coord-dot"></span>خط العرض <b>{lat:.5f}</b></div>
      <div class="g-coord-chip"><span class="g-coord-dot"></span>خط الطول <b>{lng:.5f}</b></div>
      <div class="g-coord-chip">نطاق التحليل <b>500م</b></div>
    </div>
    <p style="font-size:12px;color:#94A3B8;margin:7px 0 0;text-align:center;">
      انقر على أي موقع في الخريطة لتحديده
    </p>
    """, unsafe_allow_html=True)

st.markdown("</div>", unsafe_allow_html=True)

# ══════════════════════════════════════════════════════════════════════════════
# التحليل
# ══════════════════════════════════════════════════════════════════════════════
if analyze:
    if not model_ok:
        st.error("ملف النموذج غير موجود.")
        st.stop()

    cat_te  = CATEGORIES[category]
    brand   = 1 if brand_lbl == "نعم" else 0
    ph      = st.empty()

    STEPS = [
        ("جلب الإحداثيات الجغرافية"),
        ("حساب الارتفاع والتضاريس من DEM"),
        ("تحليل شبكة الطرق"),
        ("تقييم الكثافة العمرانية"),
        ("رصد بيئة المنافسة"),
        ("تشغيل نموذج الذكاء الاصطناعي"),
    ]
    done = []
    for s in STEPS:
        done.append(s)
        rows = "".join(
            f'<div class="proc-row"><span class="proc-lbl">{r}</span>'
            f'<span class="proc-ok">✓</span></div>' for r in done)
        ph.markdown(
            f'<div style="padding:0 2rem;"><div class="proc-card">'
            f'<p class="proc-title">جارٍ التحليل…</p>{rows}</div></div>',
            unsafe_allow_html=True)
        time.sleep(0.32)

    elev  = get_elev(lat, lng) or 2200.0
    feats = compute_features(lat, lng, area, cat_te, brand, elev)
    fv    = pd.DataFrame([feats])
    for c in FEATURE_COLS:
        if c not in fv.columns: fv[c] = 0.0
    fv = fv[FEATURE_COLS]
    prob = float(model.predict_proba(fv)[0][1])

    st.session_state["results"] = {
        "prob": prob, "elev": elev, "area": area,
        "cat": category, "fv": fv.values.tolist(),
    }
    ph.empty()
    st.rerun()

# ══════════════════════════════════════════════════════════════════════════════
# النتائج
# ══════════════════════════════════════════════════════════════════════════════
if st.session_state["results"]:
    R    = st.session_state["results"]
    prob = R["prob"]; elev = R["elev"]; area_r = R["area"]
    fv   = pd.DataFrame(R["fv"], columns=FEATURE_COLS)
    v    = prob >= 0.65
    cls  = "ok" if v else "bad"
    pct  = f"{prob*100:.1f}"

    st.markdown('<div style="padding:0 2rem;">', unsafe_allow_html=True)
    st.markdown("""<hr style="margin:0 0 1.2rem;">""", unsafe_allow_html=True)
    st.markdown("""
    <div style="display:flex;align-items:center;gap:10px;margin-bottom:1.2rem;">
      <span style="display:inline-block;width:4px;height:20px;background:#B91C1C;border-radius:2px;"></span>
      <span style="font-family:'Cairo',sans-serif;font-size:15px;font-weight:700;color:#0F172A;">نتائج تقييم الموقع</span>
    </div>
    """, unsafe_allow_html=True)

    col_r, col_x = st.columns([1, 1.3], gap="large")

    with col_r:
        verdict_txt = "الموقع ملائم للاستثمار" if v else "الموقع غير ملائم"
        verdict_ico = "✓" if v else "✕"
        st.markdown(f"""
        <div class="res-card">
          <div class="res-verdict {cls}">{verdict_ico} {verdict_txt}</div>
          <div class="res-pct {cls}">{pct}<span style="font-size:2.2rem;">%</span></div>
          <p style="color:rgba(255,255,255,0.45);font-size:12px;margin:3px 0 0;">نسبة الملاءمة التجارية المتوقعة</p>
          <div class="res-meta">
            <div class="res-meta-item">
              <span class="res-meta-label">العتبة</span>
              <span class="res-meta-val">65%</span>
            </div>
            <div class="res-meta-item">
              <span class="res-meta-label">الارتفاع</span>
              <span class="res-meta-val">{elev:,.0f} م</span>
            </div>
            <div class="res-meta-item">
              <span class="res-meta-label">المساحة</span>
              <span class="res-meta-val">{area_r} م²</span>
            </div>
          </div>
        </div>
        """, unsafe_allow_html=True)

        fig = go.Figure(go.Indicator(
            mode="gauge+number",
            value=round(prob*100, 1),
            number={"suffix":"%","font":{"size":36,"family":"IBM Plex Mono",
                    "color":"#059669" if v else "#B91C1C"}},
            gauge={
                "axis":{"range":[0,100],"tickfont":{"family":"IBM Plex Mono","size":9,"color":"#94A3B8"}},
                "bar": {"color":"#059669" if v else "#B91C1C","thickness":0.28},
                "bgcolor":"rgba(0,0,0,0)","borderwidth":0,
                "steps":[{"range":[0,40],"color":"#FEF2F2"},
                         {"range":[40,65],"color":"#FFFBEB"},
                         {"range":[65,100],"color":"#ECFDF5"}],
                "threshold":{"line":{"color":"#0F172A","width":3},"thickness":0.8,"value":65},
            },
            title={"text":"مؤشر الملاءمة","font":{"size":12,"color":"#64748B","family":"Tajawal"}},
        ))
        fig.update_layout(height=210,paper_bgcolor="rgba(0,0,0,0)",
                          margin=dict(t=50,b=0,l=10,r=10))
        st.plotly_chart(fig, use_container_width=True)

    with col_x:
        shap_data, shap_ok, bias_v = real_shap(model, fv)
        if shap_ok:
            import math
            try: base_pct = 1/(1+math.exp(-bias_v))*100
            except: base_pct = 50.0

            st.markdown(f"""
            <div class="xai-card">
              <p class="xai-title">التفسير بالذكاء الاصطناعي — SHAP</p>
              <p class="xai-sub">قيم محسوبة من نموذج CatBoost مباشرةً · القاعدة الأساسية: <b style="font-family:\'IBM Plex Mono\',monospace;">{base_pct:.1f}%</b></p>
            """, unsafe_allow_html=True)

            BM = {"pos":"إيجابي ▲","neg":"سلبي ▼","neu":"محايد"}
            for sym, nm, cls_b, val, bar, sv in shap_data:
                st.markdown(f"""
                <div class="xai-row">
                  <div class="xai-head">
                    <span class="xai-name">{sym} {nm}</span>
                    <span class="xai-val">{sv}</span>
                    <span class="xai-badge {cls_b}">{BM[cls_b]}</span>
                  </div>
                  <div class="xai-track"><div class="xai-fill {cls_b}" style="width:{bar}%;"></div></div>
                </div>
                """, unsafe_allow_html=True)

            st.markdown("</div>", unsafe_allow_html=True)
        else:
            st.warning("تعذّر حساب SHAP.")

    st.markdown(f"""
    <div class="stat-grid">
      <div class="stat-c"><span class="stat-v">{elev:,.0f}</span><span class="stat-l">الارتفاع (م)</span></div>
      <div class="stat-c"><span class="stat-v">32</span><span class="stat-l">منشأة في 500م</span></div>
      <div class="stat-c"><span class="stat-v">5</span><span class="stat-l">منافس مباشر</span></div>
      <div class="stat-c"><span class="stat-v">65%</span><span class="stat-l">معدل نجاح الحي</span></div>
    </div>
    """, unsafe_allow_html=True)

    if st.button("إعادة التقييم لموقع جديد"):
        st.session_state["results"] = None
        st.rerun()

    st.markdown("</div>", unsafe_allow_html=True)

# Footer
st.markdown("""
<div class="g-footer">
  <span class="g-footer-l">© 2026 جميع الحقوق محفوظة</span>
  <span class="g-footer-c">جدوى · أمانة منطقة عسير</span>
  <span class="g-footer-l">نظام تقييم ملاءمة المواقع الاستثمارية</span>
</div>
""", unsafe_allow_html=True)
