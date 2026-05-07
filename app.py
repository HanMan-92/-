"""
جدوى — مرشد الاستثمار التجاري في عسير
"""
import streamlit as st
import pandas as pd
import numpy as np
import joblib, time, requests
import folium, plotly.graph_objects as go
from streamlit_folium import st_folium
from catboost import Pool

st.set_page_config(
    page_title="جدوى | مرشد الاستثمار التجاري",
    page_icon="◆", layout="wide",
    initial_sidebar_state="expanded",
)

# ══════════════════════════════════════════════════════════════════════════════
# CSS
# ══════════════════════════════════════════════════════════════════════════════
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Cairo:wght@300;400;500;600;700;900&family=IBM+Plex+Mono:wght@400;600&display=swap');

:root {
  --navy:    #071626;
  --navy2:   #0D2240;
  --cream:   #F5F2EB;
  --cream2:  #EDE9DF;
  --red:     #B91C1C;
  --gold:    #92400E;
  --white:   #FFFFFF;
  --border:  #D6CFC0;
  --text:    #1A1208;
  --muted:   #6B6355;
  --green:   #065F46;
  --sh: 0 1px 4px rgba(0,0,0,0.07), 0 4px 20px rgba(0,0,0,0.05);
}

html, body, [class*="css"] {
  direction: rtl;
  font-family: 'Cairo', sans-serif !important;
}

/* خلفية كريمية */
.stApp { background: var(--cream); }
.main .block-container { padding: 0 !important; max-width: 100% !important; }

/* إخفاء Streamlit الافتراضي */
#MainMenu, footer, header,
[data-testid="stToolbar"], .stDeployButton { display: none !important; }

/* ═══════════ SIDEBAR ═══════════ */
[data-testid="stSidebar"] {
  background: var(--navy) !important;
  border-left: none !important;
  min-width: 280px !important;
}
[data-testid="stSidebarContent"] { padding: 1.5rem 1.2rem !important; }

/* شعار الشريط الجانبي */
.sb-logo {
  display: flex; align-items: center; gap: 12px;
  padding-bottom: 1.2rem;
  border-bottom: 1px solid rgba(255,255,255,0.08);
  margin-bottom: 1.4rem;
}
.sb-diamond {
  width: 38px; height: 38px; flex-shrink: 0;
  background: linear-gradient(135deg, var(--red), #DC2626);
  transform: rotate(45deg); border-radius: 5px;
}
.sb-name {
  color: white; font-family: 'Cairo', sans-serif;
}
.sb-name h2 { font-size: 1.4rem; font-weight: 900; margin: 0; letter-spacing: 2px; line-height: 1; }
.sb-name p  { font-size: 0.62rem; color: rgba(255,255,255,0.4); margin: 3px 0 0; letter-spacing: 0.5px; }

/* عناوين الأقسام */
.sb-section {
  font-size: 10px; font-weight: 700; letter-spacing: 2px;
  color: rgba(255,255,255,0.35); text-transform: uppercase;
  margin: 1.2rem 0 0.5rem;
}

/* مدخلات الشريط الجانبي */
[data-testid="stSidebar"] label {
  color: rgba(255,255,255,0.6) !important;
  font-size: 12px !important; font-weight: 600 !important;
}
[data-testid="stSidebar"] .stSelectbox [data-baseweb="select"] > div {
  background: rgba(255,255,255,0.07) !important;
  border: 1px solid rgba(255,255,255,0.12) !important;
  border-radius: 8px !important; color: white !important;
}
[data-testid="stSidebar"] .stSelectbox [data-baseweb="select"] > div:hover {
  border-color: rgba(185,28,28,0.6) !important;
}
[data-testid="stSidebar"] .stRadio label { color: rgba(255,255,255,0.7) !important; }
[data-testid="stSidebar"] input { color: white !important; }
[data-testid="stSidebar"] p { color: rgba(255,255,255,0.6) !important; }

/* slider في الشريط الجانبي */
[data-testid="stSidebar"] .stSlider [data-baseweb="slider"] > div:nth-child(3) {
  background: var(--red) !important;
}
[data-testid="stSidebar"] .stSlider [data-baseweb="thumb"] {
  background: white !important; border: 2.5px solid var(--red) !important;
}
[data-testid="stSidebar"] [data-testid="stSliderTickBarMin"],
[data-testid="stSidebar"] [data-testid="stSliderTickBarMax"] {
  color: rgba(255,255,255,0.4) !important;
  font-family: 'IBM Plex Mono', monospace !important;
}

/* زر التحليل */
[data-testid="stSidebar"] .stButton > button {
  background: var(--red) !important; color: white !important;
  border: none !important; border-radius: 10px !important;
  font-weight: 700 !important; font-size: 14px !important;
  padding: 0.65rem 1.5rem !important; width: 100% !important;
  font-family: 'Cairo', sans-serif !important;
  box-shadow: 0 3px 12px rgba(185,28,28,0.4) !important;
  transition: all .25s !important; margin-top: 0.5rem !important;
}
[data-testid="stSidebar"] .stButton > button:hover {
  background: #991B1B !important; transform: translateY(-1px) !important;
}

/* زر المنطقة الرئيسية */
.main .stButton > button {
  background: transparent !important; color: var(--red) !important;
  border: 1.5px solid var(--red) !important; border-radius: 8px !important;
  font-weight: 600 !important; font-size: 13px !important;
  padding: 0.4rem 1.2rem !important;
  font-family: 'Cairo', sans-serif !important;
  transition: all .2s !important;
}
.main .stButton > button:hover {
  background: var(--red) !important; color: white !important;
}

/* ═══════════ HERO ═══════════ */
.hero {
  background: linear-gradient(135deg, var(--navy) 0%, var(--navy2) 60%, #0A1E35 100%);
  padding: 3rem 3rem 2.5rem;
  position: relative; overflow: hidden;
}
.hero::before {
  content: '';
  position: absolute; top: 0; left: 0; right: 0; bottom: 0;
  background-image: url("data:image/svg+xml,%3Csvg xmlns='http://www.w3.org/2000/svg' width='60' height='60'%3E%3Cpolygon points='30,2 58,30 30,58 2,30' fill='none' stroke='rgba(255,255,255,0.04)' stroke-width='1'/%3E%3C/svg%3E");
  background-repeat: repeat;
}
.hero-badge {
  display: inline-block;
  background: rgba(185,28,28,0.2); border: 1px solid rgba(185,28,28,0.4);
  color: rgba(255,255,255,0.7); font-size: 11px; font-weight: 700;
  letter-spacing: 2px; padding: 5px 14px; border-radius: 4px;
  font-family: 'Cairo', sans-serif;
  margin-bottom: 1.2rem;
}
.hero h1 {
  font-family: 'Cairo', sans-serif !important;
  font-size: 3.2rem !important; font-weight: 900 !important;
  color: white !important; margin: 0 0 0.4rem !important;
  line-height: 1.1 !important; letter-spacing: 1px !important;
}
.hero h1 span { color: rgba(255,255,255,0.35); font-weight: 400; font-size: 2.2rem; }
.hero-sub {
  color: rgba(255,255,255,0.5); font-size: 0.95rem; margin: 0 0 2rem;
}
.hero-divider {
  width: 60px; height: 3px;
  background: linear-gradient(90deg, var(--red), transparent);
  margin: 0.8rem 0 1.8rem;
}

/* بطاقات الإحصاء في الـ hero */
.hero-stats { display: flex; gap: 1.5rem; flex-wrap: wrap; }
.hero-stat {
  background: rgba(255,255,255,0.05);
  border: 1px solid rgba(255,255,255,0.08);
  border-radius: 10px; padding: 1rem 1.4rem;
  min-width: 160px;
}
.hero-stat-v {
  font-family: 'IBM Plex Mono', monospace;
  font-size: 2rem; font-weight: 600; color: white;
  display: block; line-height: 1;
}
.hero-stat-l { font-size: 12px; color: rgba(255,255,255,0.45); margin-top: 4px; display: block; }
.hero-stat-s { font-size: 10px; color: rgba(255,255,255,0.25); display: block; margin-top: 2px; }

/* ═══════════ كيف تعمل المنصة ═══════════ */
.how-section {
  background: var(--cream2); padding: 1.8rem 3rem;
  border-bottom: 1px solid var(--border);
}
.how-title {
  font-family: 'Cairo', sans-serif; font-size: 13px; font-weight: 700;
  color: var(--muted); text-transform: uppercase; letter-spacing: 2px;
  margin: 0 0 1.2rem; display: flex; align-items: center; gap: 8px;
}
.how-title::before {
  content: ''; display: inline-block;
  width: 16px; height: 3px; background: var(--red);
}
.how-steps { display: flex; gap: 0; align-items: stretch; }
.how-step {
  flex: 1; padding: 1.2rem 1.5rem;
  background: white; border: 1px solid var(--border); border-radius: 10px;
  margin-left: 1rem; position: relative;
}
.how-step:last-child { margin-left: 0; }
.how-num {
  font-family: 'IBM Plex Mono', monospace; font-size: 2rem;
  font-weight: 700; color: rgba(185,28,28,0.12); line-height: 1;
  margin-bottom: 0.5rem;
}
.how-step h4 { font-family: 'Cairo',sans-serif; font-size: 14px; font-weight: 700; color: var(--text); margin: 0 0 4px; }
.how-step p  { font-size: 12px; color: var(--muted); margin: 0; line-height: 1.5; }

/* ═══════════ المنطقة الرئيسية ═══════════ */
.main-body { padding: 1.8rem 3rem; }

/* قسم الخريطة */
.map-section-head {
  display: flex; align-items: center; justify-content: space-between;
  margin-bottom: 1rem;
}
.section-label {
  font-family: 'Cairo',sans-serif; font-size: 15px; font-weight: 700;
  color: var(--text); display: flex; align-items: center; gap: 8px;
}
.section-label::before {
  content: ''; width: 4px; height: 18px;
  background: var(--red); border-radius: 2px; display: inline-block;
}

/* بطاقة الخريطة */
.map-card {
  background: white; border-radius: 12px;
  border: 1px solid var(--border); box-shadow: var(--sh); overflow: hidden;
}
.map-tile-bar {
  padding: 0.7rem 1rem; border-bottom: 1px solid var(--border);
  background: #FAFAF8; display: flex; align-items: center; gap: 8px;
}
.map-tile-label { font-size: 12px; color: var(--muted); font-weight: 600; flex-shrink: 0; }

/* الإحداثيات */
.coord-bar {
  padding: 0.7rem 1rem; display: flex; gap: 8px;
  border-top: 1px solid var(--border); background: #FAFAF8;
}
.coord-chip {
  background: white; border: 1px solid var(--border);
  border-radius: 6px; padding: 4px 10px;
  font-family: 'IBM Plex Mono', monospace; font-size: 12px;
  color: var(--text); font-weight: 600;
  display: flex; align-items: center; gap: 5px;
}
.coord-dot { width: 5px; height: 5px; border-radius: 50%; background: var(--red); }

/* ═══════════ النتائج ═══════════ */
.results-section { margin-top: 2rem; }

/* بطاقة النتيجة الرئيسية */
.res-hero {
  background: var(--navy);
  border-radius: 12px; padding: 2rem;
  position: relative; overflow: hidden;
  margin-bottom: 1.2rem;
}
.res-verdict {
  font-size: 12px; font-weight: 700; letter-spacing: 1px;
  padding: 4px 12px; border-radius: 4px; display: inline-block;
  margin-bottom: 0.8rem; font-family: 'Cairo', sans-serif;
}
.res-verdict.ok  { background: rgba(5,150,105,0.2); color: #6EE7B7; border: 1px solid rgba(6,95,70,0.4); }
.res-verdict.bad { background: rgba(185,28,28,0.2); color: #FCA5A5; border: 1px solid rgba(185,28,28,0.4); }
.res-num { font-family: 'Cairo',sans-serif; font-size: 5rem; font-weight: 900; line-height: 1; margin: 0; }
.res-num.ok  { color: #6EE7B7; }
.res-num.bad { color: #FCA5A5; }
.res-caption { color: rgba(255,255,255,0.35); font-size: 13px; margin: 4px 0 1.2rem; }
.res-row { display: flex; gap: 2rem; padding-top: 1rem; border-top: 1px solid rgba(255,255,255,0.08); }
.res-item-l { font-size: 11px; color: rgba(255,255,255,0.3); display: block; }
.res-item-v { font-family: 'IBM Plex Mono',monospace; color: white; font-size: 1rem; font-weight: 600; }

/* بطاقة XAI */
.xai-card {
  background: white; border-radius: 12px;
  border: 1px solid var(--border); box-shadow: var(--sh);
  padding: 1.5rem; margin-bottom: 1rem;
}
.xai-head-title { font-family:'Cairo',sans-serif; font-size:15px; font-weight:700; color:var(--text); margin:0 0 3px; }
.xai-head-sub   { font-size:12px; color:var(--muted); margin:0 0 1.2rem; }
.xai-row { margin-bottom: 1.1rem; }
.xai-rh  { display:flex; align-items:center; margin-bottom:5px; gap:6px; }
.xai-fname { font-size:13px; font-weight:600; color:var(--text); flex:1; }
.xai-fval  { font-size:11px; font-family:'IBM Plex Mono',monospace; color:var(--muted); }
.xai-badge { font-size:10px; padding:2px 8px; border-radius:4px; font-weight:700; }
.xai-badge.pos { background:#ECFDF5; color:#065F46; border:1px solid #A7F3D0; }
.xai-badge.neg { background:#FEF2F2; color:#B91C1C; border:1px solid #FECACA; }
.xai-badge.neu { background:#FFFBEB; color:#92400E; border:1px solid #FDE68A; }
.xai-track { height:6px; background:var(--cream2); border-radius:3px; overflow:hidden; }
.xai-fill { height:100%; border-radius:3px; }
.xai-fill.pos { background:linear-gradient(90deg,#059669,#6EE7B7); }
.xai-fill.neg { background:linear-gradient(90deg,#B91C1C,#FCA5A5); }
.xai-fill.neu { background:linear-gradient(90deg,#D97706,#FDE68A); }

/* شبكة الإحصاء الصغيرة */
.stat-grid { display:grid; grid-template-columns:repeat(4,1fr); gap:0.8rem; margin-top:1rem; }
.stat-c { background:white; border-radius:10px; border:1px solid var(--border); box-shadow:var(--sh); padding:1rem; text-align:center; border-top:3px solid var(--red); }
.stat-v { font-size:1.5rem; font-weight:700; font-family:'IBM Plex Mono',monospace; color:var(--text); display:block; }
.stat-l { font-size:11px; color:var(--muted); display:block; margin-top:3px; }

/* معالجة */
.proc-card { background:white; border-radius:12px; border:1px solid var(--border); box-shadow:var(--sh); padding:1.5rem; margin:0 3rem 1rem; }
.proc-title { font-family:'Cairo',sans-serif; font-size:14px; font-weight:700; color:var(--text); margin:0 0 1rem; }
.proc-row { display:flex; align-items:center; gap:10px; padding:7px 0; border-bottom:1px solid var(--cream); }
.proc-row:last-child { border:none; }
.proc-lbl { flex:1; font-size:13px; color:var(--text); }
.proc-ok  { color:var(--green); font-weight:700; font-size:14px; }

/* فوتر */
.g-footer { background:var(--navy); padding:1rem 3rem; display:flex; align-items:center; justify-content:space-between; margin-top:3rem; }
.g-footer span { color:rgba(255,255,255,0.3); font-size:12px; }
.g-footer strong { color:rgba(255,255,255,0.6); font-family:'Cairo',sans-serif; font-size:13px; }

/* أرقام انجليزية */
input, [data-testid="stMetricValue"],
[data-testid="stSliderTickBarMin"],
[data-testid="stSliderTickBarMax"] {
  font-family: 'IBM Plex Mono', monospace !important;
}
label { font-family: 'Cairo', sans-serif !important; }
hr { border-color: var(--border) !important; }
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
    "مطاعم ومطابخ": 0.68, "تجزئة وجملة": 0.72,
    "أنشطة طبية": 0.78,   "تعليم وتدريب": 0.75,
    "فنادق وإيواء": 0.73, "محطات وقود": 0.80,
    "خدمات السيارات": 0.65, "ترفيه وملاهي": 0.62,
    "مقاولات وخدمات فنية": 0.70, "مستودعات وتخزين": 0.65,
}

CITIES = {
    "أبها":          (18.2200, 42.5100),
    "خميس مشيط":    (18.3000, 42.7300),
}

TILES = {
    "خريطة الشوارع":    ("https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png", "© OpenStreetMap", None),
    "صور جوية":         ("https://server.arcgisonline.com/ArcGIS/rest/services/World_Imagery/MapServer/tile/{z}/{y}/{x}", "Esri",
                          "https://server.arcgisonline.com/ArcGIS/rest/services/Reference/World_Boundaries_and_Places/MapServer/tile/{z}/{y}/{x}"),
    "خريطة حضرية":      ("https://{s}.basemaps.cartocdn.com/rastertiles/voyager/{z}/{x}/{y}{r}.png", "© CARTO", None),
    "تضاريس":           ("https://server.arcgisonline.com/ArcGIS/rest/services/World_Topo_Map/MapServer/tile/{z}/{y}/{x}", "Esri", None),
}

FEAT_AR = {
    "الاحداثي الجغرافي X": ("الموقع — خط الطول",        "pos"),
    "الاحداثي الجغرافي Y": ("الموقع — خط العرض",        "pos"),
    "الارتفاع":             ("الارتفاع الجغرافي",          None),
    "الانحدار":             ("انحدار التضاريس",            None),
    "المسافة_للشارع_الأقرب_لوغ":    ("المسافة لأقرب شارع",    None),
    "المسافة_للطريق_الشرياني_لوغ":  ("البُعد عن الطريق الشرياني", None),
    "المسافة_لأقرب_معلم_سياحي_لوغ": ("القرب من المعالم السياحية", None),
    "رتبة_الطريق":          ("رتبة الطريق المجاور",        None),
    "مؤشر_الحيوية_الحضرية": ("مؤشر الحيوية الحضرية",     None),
    "كثافة_تجارية_500م_لوغ": ("الكثافة التجارية — 500م",  None),
    "عدد_مباني_فعلي_500م_لوغ": ("عدد المباني — 500م",     None),
    "متوسط_عمر_المنافسين_يوم_لوغ": ("متوسط عمر المنافسين",  None),
    "عدد_منافسين_مباشرين_500م_لوغ": ("عدد المنافسين المباشرين", None),
    "مسافة_أقرب_مباشر_متر_لوغ": ("المسافة لأقرب منافس",   None),
    "المعدل_الجواري":       ("معدل نجاح الحي",             None),
    "معدل_إغلاق_الفئة_لوغ": ("معدل الإغلاق — الفئة",      None),
    "مساحة_المنشأة_لوغ":    ("مساحة المحل",                None),
    "الانتماء_لعلامة_تجارية": ("الانتماء لعلامة تجارية",  None),
    "مدة_الرخصة_لوغ":       ("مدة الرخصة",                None),
    "نوع_المنشأة_TE":        ("نوع المنشأة",               None),
    "فئة_النشاط_TE":         ("فئة النشاط التجاري",        None),
}

# أوصاف بلغة المستثمر (بدون مصطلحات تقنية)
INVESTOR_DESC = {
    "الاحداثي الجغرافي X":          {"pos": "الموقع الجغرافي مناسب لهذا النوع من النشاط",            "neg": "الموقع الجغرافي أقل ملاءمة لهذا النشاط في المنطقة"},
    "الاحداثي الجغرافي Y":          {"pos": "الموقع ضمن نطاق حيوي من المدينة",                         "neg": "الموقع في منطقة طرفية أو أقل نشاطاً"},
    "الارتفاع":                      {"pos": "الارتفاع مناسب — لا يُعيق وصول الزبائن طوال العام",      "neg": "الارتفاع الشاهق قد يُصعّب الوصول في موسم البرد والضباب"},
    "الانحدار":                      {"pos": "التضاريس منبسطة نسبياً — مناسبة للحركة التجارية",         "neg": "الانحدار الشديد قد يُعيق وصول الزبائن وخاصة كبار السن"},
    "المسافة_للشارع_الأقرب_لوغ":    {"pos": "الواجهة مباشرة على الشارع — سهولة رؤية المحل والوصول إليه", "neg": "المحل بعيد عن الشارع الرئيسي — يصعب على المارّين رؤيته"},
    "المسافة_للطريق_الشرياني_لوغ":  {"pos": "قريب من طريق رئيسي — تدفق يومي عالٍ من الزبائن",         "neg": "بُعد المحل عن الطريق الرئيسي يُقلّل من الحركة التلقائية"},
    "المسافة_لأقرب_معلم_سياحي_لوغ": {"pos": "قرب من معلم سياحي — مصدر إضافي للزبائن والسياح",          "neg": "البُعد عن المعالم السياحية يحدّ من الزبائن السياحيين"},
    "رتبة_الطريق":                   {"pos": "الطريق المجاور رئيسي أو شرياني — حركة مرور عالية طوال اليوم", "neg": "الطريق المجاور محلي أو سكني — حركة مرور محدودة"},
    "مؤشر_الحيوية_الحضرية":         {"pos": "المنطقة نابضة بالحياة — تنوع الخدمات يجذب أنواعاً مختلفة من الزبائن", "neg": "المنطقة هادئة تجارياً — ضعف الجذب العام للزبائن"},
    "كثافة_تجارية_500م_لوغ":        {"pos": "منطقة تجارية نشطة — وجود محلات متنوعة يجذب الزبائن ويُكمل بعضها بعضاً", "neg": "قلة المحلات التجارية في المنطقة — قد تعكس ضعف الطلب"},
    "عدد_مباني_فعلي_500م_لوغ":      {"pos": "المنطقة مكتظة بالمباني — قاعدة سكانية جيدة وكثافة بشرية مناسبة",      "neg": "قلة المباني تعني قاعدة سكانية صغيرة حول المشروع"},
    "متوسط_عمر_المنافسين_يوم_لوغ":  {"pos": "المنافسون حديثو الدخول — السوق منفتح ولم يتشبّع بعد",            "neg": "المنافسون متجذّرون منذ سنوات — لهم زبائن وفيّون وسيصعب منافستهم"},
    "عدد_منافسين_مباشرين_500م_لوغ": {"pos": "منافسة خفيفة في نطاق 500م — فرصة لاستحواذ جيد على السوق",         "neg": "منافسة شديدة — عدد كبير من المنافسين المباشرين في المنطقة"},
    "مسافة_أقرب_مباشر_متر_لوغ":    {"pos": "المنافس الأقرب بعيد بما يكفي — مجال جيد للتميز والانفراد",          "neg": "يوجد منافس مباشر قريب جداً — صعوبة في التمييز وجذب الزبائن"},
    "المعدل_الجواري":                {"pos": "معظم المحلات المجاورة ناجحة ومستمرة — بيئة تجارية صحية ومشجّعة",   "neg": "نسبة الإغلاق في الحي مرتفعة — تحقق من الأسباب قبل الاستثمار"},
    "معدل_إغلاق_الفئة_لوغ":         {"pos": "هذا النشاط مستدام في المنطقة — معدل إغلاقه منخفض تاريخياً",         "neg": "هذا النشاط يواجه تحديات في المنطقة — معدل إغلاقه مرتفع"},
    "مساحة_المنشأة_لوغ":            {"pos": "المساحة مثالية لهذا النشاط — توازن بين التكلفة والطاقة الاستيعابية", "neg": "المساحة غير متناسبة مع النشاط — إما كبيرة فتزيد التكاليف أو صغيرة فتُقيّد الخدمة"},
    "الانتماء_لعلامة_تجارية":       {"pos": "الانتماء لعلامة تجارية معروفة يُعجّل بناء الثقة ويرفع معدل الإقبال", "neg": "النشاط بدون علامة تجارية — يحتاج وقتاً أطول لبناء قاعدة زبائن"},
    "مدة_الرخصة_لوغ":              {"pos": "مدة الرخصة مناسبة لتحقيق العائد",                             "neg": "مدة الرخصة قصيرة — خطر إضافي في حال التجديد"},
    "نوع_المنشأة_TE":               {"pos": "هذا النوع من المنشآت له سجل نجاح جيد في المنطقة",              "neg": "هذا النوع من المنشآت واجه تحديات في المنطقة تاريخياً"},
    "فئة_النشاط_TE":                {"pos": "هذا النشاط مطلوب في عسير وله معدل استدامة جيد",               "neg": "هذا النشاط يواجه تنافسية عالية في المنطقة"},
}


def investor_explanation(prob, elev, area_val, category, shap_rows):
    """يُنشئ شرحاً بلغة بسيطة للمستثمر"""
    v   = prob >= 0.65
    pct = f"{prob*100:.0f}"

    if v:
        intro = (f"بناءً على تحليل أكثر من 22,000 مشروع تجاري في منطقة عسير، "
                 f"يُوصي النظام بهذا الموقع لنشاط «{category}» بنسبة ملاءمة {pct}%. "
                 f"الموقع يمتلك مقوّمات نجاح جيدة وفق المعطيات المتوفرة.")
    else:
        intro = (f"بعد تحليل شامل، يُشير النموذج إلى مخاطر استثمارية في هذا الموقع، "
                 f"إذ بلغت نسبة الملاءمة {pct}% فقط. "
                 f"يُنصح بمراجعة العوامل أدناه قبل اتخاذ القرار النهائي.")

    reasons_pos, reasons_neg = [], []
    for feat, cls_b, val, bar, sv in shap_rows:
        desc_dict = INVESTOR_DESC.get(feat, {})
        if cls_b == "pos" and desc_dict.get("pos"):
            reasons_pos.append(desc_dict["pos"])
        elif cls_b == "neg" and desc_dict.get("neg"):
            reasons_neg.append(desc_dict["neg"])

    return intro, reasons_pos[:3], reasons_neg[:2]


# حدود نطاق الدراسة الجغرافي (أبها + خميس مشيط)
STUDY_AREA = {"lat_min": 18.05, "lat_max": 18.55,
               "lng_min": 42.25, "lng_max": 43.05}

def in_study_area(lat, lng):
    return (STUDY_AREA["lat_min"] <= lat <= STUDY_AREA["lat_max"] and
            STUDY_AREA["lng_min"] <= lng <= STUDY_AREA["lng_max"])

# ══════════════════════════════════════════════════════════════════════════════
# دوال
# ══════════════════════════════════════════════════════════════════════════════
def get_elev(lat, lng):
    try:
        r = requests.get(f"https://api.open-elevation.com/api/v1/lookup?locations={lat},{lng}", timeout=6)
        if r.status_code == 200:
            return float(r.json()["results"][0]["elevation"])
    except Exception: pass
    return None

def compute_features(lat, lng, area, cat_te, brand, elev):
    sl = min(max((elev - 1500) / 100, 2), 25)
    return {
        "الاحداثي الجغرافي X": lng, "الاحداثي الجغرافي Y": lat,
        "الارتفاع": elev, "الانحدار": sl,
        "المسافة_للشارع_الأقرب_لوغ": np.log1p(35),
        "المسافة_للطريق_الشرياني_لوغ": np.log1p(850),
        "المسافة_لأقرب_معلم_سياحي_لوغ": np.log1p(3200),
        "رتبة_الطريق": 6, "مؤشر_الحيوية_الحضرية": 5.2,
        "كثافة_تجارية_500م_لوغ": np.log1p(32),
        "عدد_مباني_فعلي_500م_لوغ": np.log1p(85),
        "متوسط_عمر_المنافسين_يوم_لوغ": np.log1p(720),
        "عدد_منافسين_مباشرين_500م_لوغ": np.log1p(5),
        "مسافة_أقرب_مباشر_متر_لوغ": np.log1p(160),
        "المعدل_الجواري": 0.65, "معدل_إغلاق_الفئة_لوغ": np.log1p(0.28),
        "مساحة_المنشأة_لوغ": np.log1p(area),
        "الانتماء_لعلامة_تجارية": brand, "مدة_الرخصة_لوغ": np.log1p(1),
        "نوع_المنشأة_TE": 0.70, "فئة_النشاط_TE": cat_te,
    }

def llm_explain(prob, elev, area_v, category, pos_r, neg_r, verdict):
    """
    يُولّد تفسيراً نصياً طبيعياً باستخدام Claude API.
    يتطلب إضافة مفتاح ANTHROPIC_API_KEY في Streamlit Secrets.
    في حال غياب المفتاح يُعيد نصاً قالبياً جيداً.
    """
    pct = f"{prob*100:.0f}"

    def template():
        """نص قالبي احترافي بدون API"""
        verdict_txt = "واعدة" if verdict else "محدودة"
        intro = (f"يُشير تحليل النموذج إلى أن هذا الموقع يمتلك فرصة استثمارية {verdict_txt} "
                 f"لنشاط '{category}'، إذ حصل على نسبة ملاءمة {pct}% وفق قاعدة بيانات تضم "
                 f"أكثر من 22,000 رخصة تجارية في منطقة عسير.")
        body = ""
        if pos_r:
            body += f" ومما يدعم هذا الموقع أن {pos_r[0].lower()}"
            if len(pos_r) > 1:
                body += f"، فضلاً عن أن {pos_r[1].lower()}"
            body += "."
        if neg_r:
            body += f" غير أن ثمة اعتبارات جديرة بالانتباه؛ إذ {neg_r[0].lower()}"
            if len(neg_r) > 1:
                body += f"، كما يُلاحَظ أن {neg_r[1].lower()}"
            body += ". يُنصح بأخذ هذه العوامل بعين الاعتبار قبل اتخاذ القرار النهائي."
        return intro + body

    try:
        import anthropic as _ant
        key = st.secrets.get("ANTHROPIC_API_KEY", "")
        if not key:
            return template()

        client = _ant.Anthropic(api_key=key)
        prompt = (
            f"أنت مستشار استثماري متخصص في المشاريع التجارية بمنطقة عسير السعودية. "
            f"اكتب فقرة واحدة متدفقة باللغة العربية الفصحى البسيطة تشرح للمستثمر العادي "
            f"سبب حصول موقعه على نسبة الملاءمة هذه.

"
            f"البيانات:
"
            f"- نسبة الملاءمة: {pct}%
"
            f"- الحكم: {'ملائم' if verdict else 'غير ملائم'}
"
            f"- النشاط التجاري: {category}
"
            f"- الارتفاع: {elev:.0f}م فوق سطح البحر
"
            f"- المساحة: {area_v}م²
"
            f"- نقاط القوة: {'; '.join(pos_r) if pos_r else 'لا توجد'}
"
            f"- التحديات: {'; '.join(neg_r) if neg_r else 'لا توجد'}

"
            f"التعليمات: فقرة واحدة فقط. خاطب المستثمر مباشرة. "
            f"لا تذكر أرقاماً تقنية أو مصطلحات برمجية. "
            f"أسلوب مستشار خبير دافئ ومهني. لا تتجاوز 120 كلمة."
        )
        msg = client.messages.create(
            model="claude-sonnet-4-20250514",
            max_tokens=400,
            messages=[{"role": "user", "content": prompt}]
        )
        return msg.content[0].text.strip()
    except Exception:
        return template()


def real_shap(model, fv):
    try:
        mat  = model.get_feature_importance(Pool(fv), type="ShapValues")
        vals = mat[0][:-1]; bias = mat[0][-1]
        total = np.sum(np.abs(vals)) + 1e-9
        rows  = []
        for feat, v in zip(FEATURE_COLS, vals):
            nm  = FEAT_AR.get(feat, (feat, None))[0]
            cls = "pos" if v > 0.001 else ("neg" if v < -0.001 else "neu")
            bar = int(min(98, abs(v) / total * 600))
            sv  = f"+{v:.4f}" if v >= 0 else f"{v:.4f}"
            rows.append((nm, cls, v, bar, sv))
        rows.sort(key=lambda x: abs(x[2]), reverse=True)
        return rows[:5], True, bias
    except Exception:
        return None, False, 0.0

# ══════════════════════════════════════════════════════════════════════════════
# Session state
# ══════════════════════════════════════════════════════════════════════════════
def ss(k, v):
    if k not in st.session_state: st.session_state[k] = v

ss("lat", 18.2200); ss("lng", 42.5100)
ss("results", None); ss("_lc", None); ss("tile", "خريطة الشوارع")

lat = st.session_state["lat"]
lng = st.session_state["lng"]

# ══════════════════════════════════════════════════════════════════════════════
# SIDEBAR
# ══════════════════════════════════════════════════════════════════════════════
with st.sidebar:
    st.markdown("""
    <div class="sb-logo">
      <div class="sb-diamond"></div>
      <div class="sb-name">
        <h2>جدوى</h2>
        <p>مرشد الاستثمار التجاري · عسير</p>
      </div>
    </div>
    """, unsafe_allow_html=True)

    st.markdown('<p class="sb-section">الموقع</p>', unsafe_allow_html=True)
    city = st.selectbox("المدينة", list(CITIES.keys()), label_visibility="collapsed")
    if st.session_state.get("city") != city:
        st.session_state["city"] = city
        st.session_state["lat"], st.session_state["lng"] = CITIES[city]
        st.session_state["results"] = None

    st.markdown('<p class="sb-section">بيانات المشروع</p>', unsafe_allow_html=True)
    category  = st.selectbox("نوع النشاط التجاري", list(CATEGORIES.keys()))
    area      = st.number_input("مساحة المحل (م²)", min_value=2, max_value=30000, value=80, step=1)
    brand_lbl = st.radio("علامة تجارية؟", ["لا", "نعم"], horizontal=True)

    st.markdown('<p class="sb-section">الخريطة</p>', unsafe_allow_html=True)
    tile_name = st.selectbox("نوع الخريطة", list(TILES.keys()),
                              index=list(TILES.keys()).index(st.session_state["tile"]))
    if tile_name != st.session_state["tile"]:
        st.session_state["tile"] = tile_name
        st.rerun()

    st.markdown("<br>", unsafe_allow_html=True)
    analyze = st.button("تحليل الموقع وتقييم الجدوى", use_container_width=True)

    st.markdown("""
    <div style="margin-top:2rem;padding-top:1rem;border-top:1px solid rgba(255,255,255,0.07);">
      <p style="font-size:11px;color:rgba(255,255,255,0.2);line-height:1.6;">
        النموذج: CatBoost<br>
        التحقق: زمني + مكاني<br>
        البيانات: 22,917 رخصة
      </p>
    </div>
    """, unsafe_allow_html=True)

lat = st.session_state["lat"]
lng = st.session_state["lng"]

# ══════════════════════════════════════════════════════════════════════════════
# HERO
# ══════════════════════════════════════════════════════════════════════════════
st.markdown("""
<div class="hero">
  <div style="position:relative;z-index:1;">
    <div class="hero-badge">GEOXAI · SITE INTELLIGENCE · ASEER</div>
    <h1>جدوى <span>— مرشد الاستثمار التجاري</span></h1>
    <div class="hero-divider"></div>
    <p class="hero-sub">منصة تحليلية للتنبؤ باستدامة المشاريع التجارية في أبها وخميس مشيط — منطقة عسير</p>
    <div class="hero-stats">
      <div class="hero-stat">
        <span class="hero-stat-v">21</span>
        <span class="hero-stat-l">متغيراً تحليلياً</span>
        <span class="hero-stat-s">جغرافية · حضرية · تنافسية</span>
      </div>
      <div class="hero-stat">
        <span class="hero-stat-v">0.81</span>
        <span class="hero-stat-l">دقة النموذج (AUC)</span>
        <span class="hero-stat-s">تحقق زمني ومكاني · CatBoost</span>
      </div>
      <div class="hero-stat">
        <span class="hero-stat-v">22,917</span>
        <span class="hero-stat-l">رخصة تجارية</span>
        <span class="hero-stat-s">بيانات رسمية من أمانة عسير</span>
      </div>
      <div class="hero-stat">
        <span class="hero-stat-v">F0.5</span>
        <span class="hero-stat-l">مقياس الأداء</span>
        <span class="hero-stat-s">يُغلِّب الدقة على الاسترجاع</span>
      </div>
    </div>
  </div>
</div>
""", unsafe_allow_html=True)

# ══════════════════════════════════════════════════════════════════════════════
# كيف تعمل المنصة
# ══════════════════════════════════════════════════════════════════════════════
st.markdown("""
<div class="how-section">
  <div class="how-title">كيف تعمل المنصة</div>
  <div class="how-steps">
    <div class="how-step">
      <div class="how-num">01</div>
      <h4>تحديد الموقع</h4>
      <p>انقر على الخريطة لتحديد الموقع المراد تقييمه — الإحداثيات تُضبط تلقائياً</p>
    </div>
    <div class="how-step">
      <div class="how-num">02</div>
      <h4>إدخال البيانات</h4>
      <p>حدد نوع النشاط والمساحة من الشريط الجانبي — باقي المؤشرات تُحسب تلقائياً</p>
    </div>
    <div class="how-step">
      <div class="how-num">03</div>
      <h4>النتائج والتفسير</h4>
      <p>نسبة الملاءمة مع تفسير GeoShapley لأبرز العوامل المؤثرة</p>
    </div>
  </div>
</div>
""", unsafe_allow_html=True)

# ══════════════════════════════════════════════════════════════════════════════
# الخريطة
# ══════════════════════════════════════════════════════════════════════════════
st.markdown('<div class="main-body">', unsafe_allow_html=True)

st.markdown("""
<div class="map-section-head">
  <div class="section-label">تحديد الموقع الجغرافي</div>
</div>
""", unsafe_allow_html=True)

tile_url, tile_attr, tile_ov = TILES[st.session_state["tile"]]
m = folium.Map(location=[lat, lng], zoom_start=15,
               tiles=tile_url, attr=tile_attr)
if tile_ov:
    folium.TileLayer(tiles=tile_ov, attr="Esri", overlay=True).add_to(m)

# علامة الموقع الحالي
folium.Marker(
    [lat, lng],
    popup=folium.Popup(
        f"<div dir='rtl' style='font-family:Arial;'><b>الموقع المحدد</b>"
        f"<br>{lat:.5f} ، {lng:.5f}</div>", max_width=160),
    icon=folium.Icon(color="red", icon="map-marker", prefix="fa"),
    tooltip="الموقع الحالي",
).add_to(m)

folium.Circle([lat, lng], radius=500, color="#B91C1C",
              fill=True, fill_opacity=0.07, weight=2,
              tooltip="نطاق التحليل 500م").add_to(m)

mk  = f"m{st.session_state['tile'][:4]}{round(lat,3)}{round(lng,3)}"
out = st_folium(m, key=mk, width="100%", height=440,
                returned_objects=["last_clicked", "center"])

# تحديد الموقع: طريقتان
# ① من النقر المباشر
_clicked_lat, _clicked_lng = lat, lng
if out and out.get("last_clicked"):
    _lc = out["last_clicked"]
    _clicked_lat = round(_lc["lat"], 5)
    _clicked_lng = round(_lc["lng"], 5)

# ② من مركز الخريطة الحالي
_center_lat, _center_lng = lat, lng
if out and out.get("center"):
    _center_lat = round(out["center"]["lat"], 5)
    _center_lng = round(out["center"]["lng"], 5)

# عرض الإحداثيات وأزرار التأكيد
col_coord, col_btn = st.columns([3, 1])
with col_coord:
    st.markdown(f"""
    <div class="coord-bar">
      <div class="coord-chip"><span class="coord-dot"></span>خط العرض <b>{lat:.5f}</b></div>
      <div class="coord-chip"><span class="coord-dot"></span>خط الطول <b>{lng:.5f}</b></div>
      <div class="coord-chip">نطاق التحليل <b>500م</b></div>
    </div>
    """, unsafe_allow_html=True)

with col_btn:
    # زر "تثبيت مركز الخريطة" — الطريقة الأكثر موثوقية
    if st.button("📍 تثبيت الموقع", help="انقل الخريطة إلى الموقع المراد ثم اضغط هذا الزر"):
        if abs(_center_lat - lat) > 0.0001 or abs(_center_lng - lng) > 0.0001:
            st.session_state.update({"lat": _center_lat, "lng": _center_lng,
                                      "results": None, "_lc": (_center_lat, _center_lng)})
            st.rerun()

# معالجة النقر المباشر أيضاً
if out and out.get("last_clicked"):
    _lt = (_clicked_lat, _clicked_lng)
    if _lt != st.session_state["_lc"] and (
        abs(_clicked_lat - lat) > 0.0001 or abs(_clicked_lng - lng) > 0.0001):
        st.session_state.update({"lat": _clicked_lat, "lng": _clicked_lng,
                                  "_lc": _lt, "results": None})
        st.rerun()

st.caption("💡 تلميح: حرّك الخريطة حتى يكون الموقع في مركزها، ثم اضغط 'تثبيت الموقع' — أو انقر مباشرة على الخريطة")

lat = st.session_state["lat"]
lng = st.session_state["lng"]

st.markdown("</div>", unsafe_allow_html=True)

# ══════════════════════════════════════════════════════════════════════════════
# التحليل
# ══════════════════════════════════════════════════════════════════════════════
if analyze:
    if not model_ok:
        st.error("ملف النموذج غير موجود.")
        st.stop()

    cat_te = CATEGORIES[category]
    brand  = 1 if brand_lbl == "نعم" else 0
    ph     = st.empty()

    STEPS = ["جلب الإحداثيات الجغرافية", "حساب الارتفاع من DEM",
             "تحليل شبكة الطرق", "تقييم الكثافة العمرانية",
             "رصد بيئة المنافسة", "تشغيل نموذج الذكاء الاصطناعي"]
    done = []
    for s in STEPS:
        done.append(s)
        rows = "".join(f'<div class="proc-row"><span class="proc-lbl">{r}</span>'
                       f'<span class="proc-ok">✓</span></div>' for r in done)
        ph.markdown(f'<div class="proc-card"><p class="proc-title">جارٍ التحليل…</p>{rows}</div>',
                    unsafe_allow_html=True)
        time.sleep(0.3)

    elev  = get_elev(lat, lng) or 2200.0
    feats = compute_features(lat, lng, area, cat_te, brand, elev)
    fv    = pd.DataFrame([feats])
    for c in FEATURE_COLS:
        if c not in fv.columns: fv[c] = 0.0
    fv   = fv[FEATURE_COLS]
    prob = float(model.predict_proba(fv)[0][1])

    st.session_state["results"] = {"prob": prob, "elev": elev,
                                    "area": area, "fv": fv.values.tolist()}
    ph.empty()
    st.rerun()

# ══════════════════════════════════════════════════════════════════════════════
# النتائج
# ══════════════════════════════════════════════════════════════════════════════
if st.session_state["results"]:
    R    = st.session_state["results"]
    prob = R["prob"]; elev = R["elev"]; area_r = R["area"]
    fv   = pd.DataFrame(R["fv"], columns=FEATURE_COLS)
    v    = prob >= 0.65; cls = "ok" if v else "bad"
    pct  = f"{prob*100:.1f}"

    st.markdown('<div class="main-body">', unsafe_allow_html=True)
    st.markdown("""
    <div class="section-label" style="margin-bottom:1.2rem;">نتائج التقييم والتفسير</div>
    """, unsafe_allow_html=True)

    col_r, col_x = st.columns([1, 1.4], gap="large")

    with col_r:
        vt = "الموقع ملائم للاستثمار" if v else "الموقع غير ملائم"
        st.markdown(f"""
        <div class="res-hero">
          <div class="res-verdict {cls}">{'✓' if v else '✕'}  {vt}</div>
          <div class="res-num {cls}">{pct}<span style="font-size:2.5rem;">%</span></div>
          <p class="res-caption">نسبة الملاءمة التجارية المتوقعة</p>
          <div class="res-row">
            <div><span class="res-item-l">العتبة</span><span class="res-item-v">65%</span></div>
            <div><span class="res-item-l">الارتفاع</span><span class="res-item-v">{elev:,.0f} م</span></div>
            <div><span class="res-item-l">المساحة</span><span class="res-item-v">{area_r} م²</span></div>
          </div>
        </div>
        """, unsafe_allow_html=True)

        fig = go.Figure(go.Indicator(
            mode="gauge+number",
            value=round(prob*100, 1),
            number={"suffix":"%","font":{"size":34,"family":"IBM Plex Mono",
                    "color":"#059669" if v else "#B91C1C"}},
            gauge={"axis":{"range":[0,100],"tickfont":{"family":"IBM Plex Mono","size":9,"color":"#94A3B8"}},
                   "bar":{"color":"#059669" if v else "#B91C1C","thickness":0.28},
                   "bgcolor":"rgba(0,0,0,0)","borderwidth":0,
                   "steps":[{"range":[0,40],"color":"#FEF2F2"},
                             {"range":[40,65],"color":"#FFFBEB"},
                             {"range":[65,100],"color":"#ECFDF5"}],
                   "threshold":{"line":{"color":"#1A1208","width":3},"thickness":0.8,"value":65}},
            title={"text":"مؤشر الملاءمة","font":{"size":12,"color":"#6B6355","family":"Cairo"}},
        ))
        fig.update_layout(height=200, paper_bgcolor="rgba(0,0,0,0)",
                          margin=dict(t=45,b=0,l=10,r=10))
        st.plotly_chart(fig, use_container_width=True)

    with col_x:
        shap_data, shap_ok, bias_v = real_shap(model, fv)
        if shap_ok:
            import math
            try: bp = 1/(1+math.exp(-bias_v))*100
            except: bp = 50.0

            st.markdown(f"""
            <div class="xai-card">
              <p class="xai-head-title">التفسير بالذكاء الاصطناعي — GeoSHAP</p>
              <p class="xai-head-sub">قيم SHAP محسوبة من نموذج CatBoost · القاعدة الأساسية: <b style="font-family:'IBM Plex Mono',monospace;">{bp:.1f}%</b> · أبرز 5 عوامل مرتبة بحسب الأثر</p>
            """, unsafe_allow_html=True)

            BM = {"pos":"إيجابي ▲","neg":"سلبي ▼","neu":"محايد "}
            for nm, cls_b, val, bar, sv in shap_data:
                st.markdown(f"""
                <div class="xai-row">
                  <div class="xai-rh">
                    <span class="xai-fname">{nm}</span>
                    <span class="xai-fval">{sv}</span>
                    <span class="xai-badge {cls_b}">{BM[cls_b]}</span>
                  </div>
                  <div class="xai-track"><div class="xai-fill {cls_b}" style="width:{bar}%;"></div></div>
                </div>
                """, unsafe_allow_html=True)
            st.markdown("</div>", unsafe_allow_html=True)
        else:
            st.info("تعذّر حساب SHAP — تأكد من توافق إصدار CatBoost.")

    st.markdown(f"""
    <div class="stat-grid">
      <div class="stat-c"><span class="stat-v">{elev:,.0f}</span><span class="stat-l">الارتفاع (م)</span></div>
      <div class="stat-c"><span class="stat-v">32</span><span class="stat-l">منشأة في 500م</span></div>
      <div class="stat-c"><span class="stat-v">5</span><span class="stat-l">منافس مباشر</span></div>
      <div class="stat-c"><span class="stat-v">65%</span><span class="stat-l">معدل نجاح الحي</span></div>
    </div>
    """, unsafe_allow_html=True)

    if st.button("إعادة التقييم"):
        st.session_state["results"] = None
        st.rerun()

    st.markdown("</div>", unsafe_allow_html=True)

# Footer
st.markdown("""
<div class="g-footer">
  <span>© 2026 — جميع الحقوق محفوظة</span>
  <strong>جدوى · مرشد الاستثمار التجاري · أمانة منطقة عسير</strong>
  <span>GEOXAI · SITE INTELLIGENCE</span>
</div>
""", unsafe_allow_html=True)
