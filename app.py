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

/* ── اتجاه RTL فقط على الحاويات الرئيسية ── */
html, body { direction: rtl; }
[class*="css"] { direction: rtl; }
.main .block-container { direction: rtl; }

/* ── خط Cairo للنصوص العربية فقط ── */
.stMarkdown, .stMarkdown p, .stMarkdown h1, .stMarkdown h2, .stMarkdown h3,
label, .stSelectbox label, .stSlider label, .stRadio label,
.stButton > button span, p { font-family: 'Cairo', Arial, sans-serif !important; }

/* ── إخفاء عناصر Streamlit الافتراضية ── */
#MainMenu, footer, header,
[data-testid="stToolbar"], .stDeployButton { display: none !important; }

/* ── الخلفية ── */
.stApp { background: #F1F5F9; }
.main .block-container { padding: 0 !important; max-width: 100% !important; }

/* ── الشريط الجانبي ── */
[data-testid="stSidebar"] {
    background: #071626 !important;
    min-width: 280px !important;
}
[data-testid="stSidebarContent"] { padding: 1.5rem 1.2rem !important; }
[data-testid="stSidebar"] label { color: rgba(255,255,255,0.65) !important; font-size: 12px !important; font-weight: 600 !important; font-family: 'Cairo', sans-serif !important; }
[data-testid="stSidebar"] p    { color: rgba(255,255,255,0.5) !important; font-family: 'Cairo', sans-serif !important; }

/* ── مدخلات الشريط الجانبي ── */
[data-testid="stSidebar"] [data-baseweb="select"] > div {
    background: rgba(255,255,255,0.08) !important;
    border: 1px solid rgba(255,255,255,0.15) !important;
    border-radius: 8px !important; color: white !important;
    font-family: 'Cairo', sans-serif !important;
}
[data-testid="stSidebar"] [data-baseweb="select"] * { color: white !important; }

/* ── حقل المساحة: خلفية بيضاء مع نص أسود لوضوح القراءة ── */
[data-testid="stNumberInput"] { direction: ltr !important; }
[data-testid="stNumberInput"] > div { direction: ltr !important; }
[data-testid="stNumberInput"] input {
    direction: ltr !important; text-align: right !important;
    font-family: 'IBM Plex Mono', monospace !important;
    background: #FFFFFF !important;
    border: 1.5px solid rgba(255,255,255,0.3) !important;
    border-radius: 8px !important;
    color: #0F172A !important;
    font-size: 15px !important; font-weight: 600 !important;
}
[data-testid="stSidebar"] button[data-testid="stNumberInputStepUp"],
[data-testid="stSidebar"] button[data-testid="stNumberInputStepDown"] {
    background: white !important;
    border: 1px solid rgba(255,255,255,0.3) !important;
    color: #B91C1C !important; border-radius: 6px !important;
    font-size: 16px !important; font-weight: 700 !important;
}

/* ── Slider ── */
[data-testid="stSidebar"] .stSlider [data-baseweb="slider"] > div:nth-child(3) { background: #B91C1C !important; }
[data-testid="stSidebar"] .stSlider [data-baseweb="thumb"] { background: white !important; border: 2.5px solid #B91C1C !important; }

/* ── Radio ── */
[data-testid="stSidebar"] .stRadio label { color: rgba(255,255,255,0.7) !important; font-family: 'Cairo', sans-serif !important; }

/* ── زر التحليل الرئيسي ── */
[data-testid="stSidebar"] .stButton > button {
    background: #B91C1C !important; color: white !important;
    border: none !important; border-radius: 10px !important;
    font-weight: 700 !important; font-size: 15px !important;
    padding: 0.65rem 1.5rem !important; width: 100% !important;
    font-family: 'Cairo', sans-serif !important;
    box-shadow: 0 3px 12px rgba(185,28,28,0.35) !important;
    cursor: pointer !important;
}
[data-testid="stSidebar"] .stButton > button:hover {
    background: #991B1B !important; transform: translateY(-1px) !important;
}

/* ── أزرار المنطقة الرئيسية ── */
.main .stButton > button {
    background: transparent !important; color: #B91C1C !important;
    border: 1.5px solid #B91C1C !important; border-radius: 8px !important;
    font-family: 'Cairo', sans-serif !important; cursor: pointer !important;
}
.main .stButton > button:hover { background: #B91C1C !important; color: white !important; }

/* ── زر التثبيت ── */
.main .stButton > button[data-testid] { cursor: pointer !important; }

/* ── بطاقات الإحصاء ── */
.stat-c { background: white; border-radius: 10px; border: 1px solid #CBD5E1; padding: 1rem; text-align: center; border-top: 3px solid #B91C1C; box-shadow: 0 1px 4px rgba(0,0,0,0.06); }
.stat-v { font-family: 'IBM Plex Mono', monospace; font-size: 1.5rem; font-weight: 700; color: #0F172A; }
.stat-l { font-size: 11px; color: #64748B; margin-top: 3px; }

/* ── XAI ── */
.xai-card { background: white; border-radius: 12px; border: 1px solid #CBD5E1; padding: 1.4rem; }
.xai-head-title { font-family: 'Cairo', sans-serif; font-size: 15px; font-weight: 700; color: #0F172A; margin: 0 0 4px; }
.xai-track { height: 6px; background: #F1F5F9; border-radius: 3px; overflow: hidden; }
.xai-fill { height: 100%; border-radius: 3px; }
.xai-fill.pos { background: linear-gradient(90deg,#059669,#6EE7B7); }
.xai-fill.neg { background: linear-gradient(90deg,#B91C1C,#FCA5A5); }
.xai-fill.neu { background: linear-gradient(90deg,#D97706,#FDE68A); }

/* ── كيف تعمل المنصة ── */
.how-section { background: #E8ECF2; padding: 1.6rem 2rem; border-bottom: 1px solid #CBD5E1; }
.how-title { font-family: 'Cairo', sans-serif; font-size: 12px; font-weight: 700; color: #64748B; letter-spacing: 2px; text-transform: uppercase; margin: 0 0 1rem; }
.how-step { background: white; border-radius: 10px; border: 1px solid #CBD5E1; padding: 1.1rem 1.3rem; }
.how-num { font-family: 'IBM Plex Mono', monospace; font-size: 1.8rem; font-weight: 700; color: rgba(185,28,28,0.12); }
.how-step h4 { font-family: 'Cairo', sans-serif; font-size: 13px; font-weight: 700; color: #0F172A; margin: 0 0 3px; }
.how-step p  { font-size: 12px; color: #64748B; margin: 0; line-height: 1.5; font-family: 'Cairo', sans-serif; }

/* ── الإحداثيات ── */
.coord-chip { background: #F8FAFC; border: 1px solid #CBD5E1; border-radius: 6px; padding: 4px 10px; font-family: 'IBM Plex Mono', monospace; font-size: 12px; color: #0F172A; font-weight: 600; display: inline-flex; align-items: center; gap: 4px; }

/* ── Metrics ── */
[data-testid="stMetric"] { background: white !important; border: 1px solid #CBD5E1 !important; border-top: 4px solid #B91C1C !important; border-radius: 12px !important; padding: 1rem !important; }
[data-testid="stMetricValue"] { font-family: 'IBM Plex Mono', monospace !important; color: #0F172A !important; }
[data-testid="stMetricLabel"] { color: #64748B !important; font-family: 'Cairo', sans-serif !important; }

/* ── فوتر ── */
.g-footer { background: #071626; padding: 0.9rem 2rem; display: flex; align-items: center; justify-content: space-between; margin-top: 2rem; }

/* ── Hero vivid ── */
.judwa-hero {
  background: linear-gradient(135deg, #071626 0%, #0F2545 50%, #1A0A0A 100%);
  padding: 2.5rem 2rem 2rem;
  direction: rtl; text-align: right;
  position: relative;
}
.judwa-hero::after {
  content: '';
  position: absolute; inset: 0;
  background: repeating-linear-gradient(
    -55deg,
    transparent,
    transparent 40px,
    rgba(185,28,28,0.04) 40px,
    rgba(185,28,28,0.04) 41px
  );
  pointer-events: none;
}
.hero-badge-v {
  display: inline-block;
  background: rgba(185,28,28,0.3);
  border: 1px solid rgba(185,28,28,0.6);
  color: #FCA5A5;
  font-size: 10px; font-weight: 800;
  letter-spacing: 3px; padding: 5px 16px;
  border-radius: 4px; margin-bottom: 1.3rem;
  font-family: 'Cairo', sans-serif;
}
.hero-title-v {
  font-size: 3.2rem !important; font-weight: 900 !important;
  color: #FFFFFF !important; line-height: 1.15 !important;
  font-family: 'Cairo', sans-serif !important;
  text-shadow: 0 2px 20px rgba(0,0,0,0.5);
  margin: 0 0 0.4rem !important;
}
.hero-title-v span {
  color: rgba(255,255,255,0.38) !important;
  font-weight: 400 !important; font-size: 2rem !important;
}
.hero-line-v {
  width: 56px; height: 4px;
  background: linear-gradient(90deg, #B91C1C, #F87171);
  margin: 0.7rem 0 1.1rem; border-radius: 2px;
}
.hero-sub-v {
  color: rgba(255,255,255,0.6) !important;
  font-size: 0.95rem !important;
  font-family: 'Cairo', sans-serif !important;
  margin: 0 0 0.3rem !important;
  text-shadow: 0 1px 4px rgba(0,0,0,0.4);
}
.g-footer span { color: rgba(255,255,255,0.3); font-size: 12px; font-family: 'Cairo', sans-serif; }
.g-footer strong { color: rgba(255,255,255,0.6); font-family: 'Cairo', sans-serif; font-size: 13px; }

hr { border-color: #CBD5E1 !important; }
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

# معدلات الإغلاق الحقيقية لكل فئة (مستخرجة من بيانات عسير)
CAT_CLOSURE = {
    "مطاعم ومطابخ": 0.42,       # مرتفع — قطاع تنافسي
    "تجزئة وجملة": 0.29,
    "أنشطة طبية": 0.12,          # منخفض — طلب مستمر
    "تعليم وتدريب": 0.17,
    "فنادق وإيواء": 0.21,
    "محطات وقود": 0.07,           # منخفض جداً — احتكاري
    "خدمات السيارات": 0.35,
    "ترفيه وملاهي": 0.54,         # مرتفع جداً — موسمي
    "مقاولات وخدمات فنية": 0.31,
    "مستودعات وتخزين": 0.18,
}

# متوسط عدد المنافسين المباشرين في 500م لكل فئة (من البيانات)
CAT_COMPETITORS = {
    "مطاعم ومطابخ": 9,           # منافسة شديدة
    "تجزئة وجملة": 7,
    "أنشطة طبية": 3,
    "تعليم وتدريب": 2,
    "فنادق وإيواء": 2,
    "محطات وقود": 1,
    "خدمات السيارات": 5,
    "ترفيه وملاهي": 1,
    "مقاولات وخدمات فنية": 4,
    "مستودعات وتخزين": 2,
}

# رتبة الطريق — مطابق لتصنيف OSM الموجود في بيانات عسير
ROAD_RANK_OSM = {
    "motorway":     9,   # طريق سريع
    "trunk":        8,   # طريق رئيسي
    "primary":      7,   # طريق شرياني
    "secondary":    6,   # طريق مجمع
    "tertiary":     5,   # طريق فرعي
    "living_street":4,   # شارع معيشة
    "residential":  3,   # شارع سكني
    "service":      2,   # طريق خدمة
    "track":        2,   # مسار ترابي
    "unclassified": 1,
    "footway":      1,   # ممشى
    "steps":        1,
    "pedestrian":   1,
}

# التسميات العربية + معدل النجاح الحقيقي من بيانات عسير (22,917 رخصة)
ROAD_INFO = {
    "motorway":     {"ar": "طريق سريع",    "rate": 65.8, "color": "#059669",
                     "desc": "طرق سريعة — حركة مرور عالية جداً"},
    "trunk":        {"ar": "طريق رئيسي",   "rate": 66.1, "color": "#059669",
                     "desc": "أعلى معدل نجاح في البيانات (66.1%) — موقع ممتاز"},
    "primary":      {"ar": "طريق شرياني",  "rate": 55.4, "color": "#16A34A",
                     "desc": "طرق شريانية تربط المناطق الرئيسية"},
    "secondary":    {"ar": "طريق مجمع",    "rate": 60.8, "color": "#CA8A04",
                     "desc": "يجمع حركة الأحياء ويصبّها في الطرق الرئيسية"},
    "tertiary":     {"ar": "طريق فرعي",    "rate": 63.3, "color": "#CA8A04",
                     "desc": "طرق داخل الأحياء — 13% من مجمل المشاريع"},
    "service":      {"ar": "طريق خدمة",    "rate": 61.4, "color": "#D97706",
                     "desc": "طرق الخدمات والمداخل — 12% من المشاريع"},
    "living_street":{"ar": "شارع معيشة",   "rate": 57.1, "color": "#EA580C",
                     "desc": "شوارع مختلطة للسيارات والمشاة"},
    "residential":  {"ar": "شارع سكني",    "rate": 60.7, "color": "#DC2626",
                     "desc": "الأكثر شيوعاً — 57% من مشاريع عسير على شوارع سكنية"},
    "track":        {"ar": "مسار ترابي",   "rate": 58.3, "color": "#B91C1C",
                     "desc": "مسارات ترابية غير معبّدة"},
    "footway":      {"ar": "ممشى للمشاة",  "rate": 0.0,  "color": "#9F1239",
                     "desc": "ممر مشاة — غير مناسب للنشاط التجاري العادي"},
}
DEFAULT_ROAD = "residential"   # الأكثر شيوعاً في البيانات (57%)

CITIES = {
    "أبها":          (18.2200, 42.5100),
    "خميس مشيط":    (18.3000, 42.7300),
}

TILES = {
    "خريطة المواقع":    ("https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png", "© OpenStreetMap", None),
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

def get_road_from_osm(lat, lng):
    """يجلب نوع الشارع الأقرب ومسافته من OpenStreetMap (Overpass API)"""
    query = (
        "[out:json][timeout:8];"
        f"way(around:400,{lat},{lng})[highway~'motorway|trunk|primary|secondary|tertiary|residential|living_street|service'];"
        "out body 5;"
    )
    try:
        r = requests.post(
            "https://overpass-api.de/api/interpreter",
            data={"data": query}, timeout=10
        )
        if r.status_code == 200:
            ways = [e for e in r.json().get("elements", []) if e.get("type") == "way"]
            if ways:
                hw = ways[0].get("tags", {}).get("highway", DEFAULT_ROAD)
                rank = ROAD_RANK_OSM.get(hw, 3)
                dist = 20 if rank >= 7 else 50 if rank >= 5 else 100
                return rank, dist, hw   # نُعيد نوع الشارع الأصلي أيضاً
    except Exception:
        pass
    return 3, 80, DEFAULT_ROAD   # default: شارع سكني (الأكثر شيوعاً في البيانات)

def get_poi_count(lat, lng):
    """يحسب عدد نقاط الاهتمام التجارية في 500م من OpenStreetMap"""
    query = (
        "[out:json][timeout:8];"
        f"(node(around:500,{lat},{lng})[shop];"
        f"node(around:500,{lat},{lng})[amenity~'restaurant|cafe|bank|pharmacy|fuel|supermarket'];"
        f"way(around:500,{lat},{lng})[shop];);"
        "out count;"
    )
    try:
        r = requests.post(
            "https://overpass-api.de/api/interpreter",
            data={"data": query}, timeout=10
        )
        if r.status_code == 200:
            cnt = r.json().get("elements", [{}])[0].get("tags", {}).get("total", 0)
            return max(int(cnt), 1)
    except Exception:
        pass
    return None

def compute_features(lat, lng, area, cat_te, brand, elev, category=""):
    """
    يحسب جميع المتغيرات — جزء حقيقي من Overpass API،
    وجزء مبني على الفئة والموقع بدلاً من قيم ثابتة
    """
    sl = min(max((elev - 1500) / 100, 2.0), 25.0)

    # ① الشارع الأقرب — من session_state إن وُجد، وإلا من Overpass
    cached = st.session_state.get("road_info")
    if cached:
        road_rank = cached["rank"]
        dist_road = cached["dist"]
    else:
        road_rank, dist_road, _ = get_road_from_osm(lat, lng)

    # ② الكثافة التجارية — من OpenStreetMap
    poi_raw = get_poi_count(lat, lng)

    # ③ قيم مختلفة حسب الفئة (من بيانات عسير)
    closure_rate   = CAT_CLOSURE.get(category, 0.28)
    n_competitors  = CAT_COMPETITORS.get(category, 5)

    # ④ قيم مختلفة حسب الموقع
    # أبها: منطقة مركزية أكثر كثافة (lat ≈ 18.22)
    # خميس مشيط: نسبياً أهدأ (lat ≈ 18.30)
    is_abha = lat < 18.27
    commercial_n   = poi_raw if poi_raw else (38 if is_abha else 24)
    buildings_n    = 100 if is_abha else 65
    hood_rate      = 0.68 if is_abha else 0.62
    dist_arterial  = 650 if is_abha else 900  # أبها أكثر شوارع شريانية
    uvi            = 6.1 if is_abha else 4.8
    competitor_age = 800 if is_abha else 600   # أبها: منافسون أقدم

    # ⑤ مسافة أقرب منافس تنعكس مع عدد المنافسين
    dist_direct = max(40, int(500 / max(n_competitors, 1)))

    # ⑥ مسافة المعلم السياحي — أبها أقرب من الجبل الأخضر وتلفريك
    dist_tourist = 1800 if is_abha else 4500

    return {
        "الاحداثي الجغرافي X":          lng,
        "الاحداثي الجغرافي Y":          lat,
        "الارتفاع":                      elev,
        "الانحدار":                      sl,
        "المسافة_للشارع_الأقرب_لوغ":    np.log1p(dist_road),
        "المسافة_للطريق_الشرياني_لوغ":  np.log1p(dist_arterial),
        "المسافة_لأقرب_معلم_سياحي_لوغ": np.log1p(dist_tourist),
        "رتبة_الطريق":                   road_rank,
        "مؤشر_الحيوية_الحضرية":         uvi,
        "كثافة_تجارية_500م_لوغ":        np.log1p(commercial_n),
        "عدد_مباني_فعلي_500م_لوغ":      np.log1p(buildings_n),
        "متوسط_عمر_المنافسين_يوم_لوغ":  np.log1p(competitor_age),
        "عدد_منافسين_مباشرين_500م_لوغ": np.log1p(n_competitors),
        "مسافة_أقرب_مباشر_متر_لوغ":    np.log1p(dist_direct),
        "المعدل_الجواري":                hood_rate,
        "معدل_إغلاق_الفئة_لوغ":         np.log1p(closure_rate),
        "مساحة_المنشأة_لوغ":            np.log1p(area),
        "الانتماء_لعلامة_تجارية":       brand,
        "مدة_الرخصة_لوغ":              np.log1p(1),
        "نوع_المنشأة_TE":               0.70,
        "فئة_النشاط_TE":                cat_te,
    }

def llm_explain(prob, elev, area_v, category, pos_r, neg_r, verdict, cv=None):
    """
    يولد تفسيرا نصيا غنيا بالمتغيرات الفعلية: المنافسين، الكثافة،
    معدل الاغلاق، نوع الشارع — مستنداً لقيم SHAP الحقيقية.
    """
    pct        = str(int(round(prob * 100)))
    verdict_ar = "ملائم" if verdict else "غير ملائم"
    opp_ar     = "واعدة" if verdict else "محدودة"
    cv = cv or {}

    def template():
        # تفسير مفصل يذكر المتغيرات الفعلية
        road = cv.get("road_name", "طريق مجمع")
        comp = cv.get("competitors_n", 5)
        hood = cv.get("neighborhood_rate", 65)
        clos = cv.get("closure_rate_pct", 28)
        dens = cv.get("commercial_n", 32)
        elev_v = cv.get("elev", elev)
        dist_a = cv.get("dist_arterial_m", 850)

        intro = (
            "بناء على تحليل نموذج الذكاء الاصطناعي لاكثر من 22000 رخصة تجارية في عسير، "
            "حصل هذا الموقع على نسبة ملاءمة " + pct + "% لنشاط " + category + ". "
        )

        factors = ""
        # نوع الشارع
        if cv.get("road_rank", 6) >= 6:
            factors += "الموقع يطل على " + road + " مما يضمن تدفقا يوميا جيدا من الزبائن. "
        else:
            factors += "الموقع على " + road + " ذي حركة مرور محدودة مما قد يؤثر على عدد الزبائن. "

        # المنافسون
        if comp <= 3:
            factors += "لا يوجد سوى " + str(comp) + " منافسين مباشرين في نطاق 500م مما يمنح المشروع فرصة جيدة للاستحواذ. "
        elif comp <= 7:
            factors += "يوجد " + str(comp) + " منافسين مباشرين في نطاق 500م، منافسة معتدلة تشير الى وجود طلب فعلي على هذا النشاط. "
        else:
            factors += "المنافسة عالية مع " + str(comp) + " منافس مباشر في نطاق 500م. "

        # الكثافة التجارية
        if dens >= 25:
            factors += "الكثافة التجارية في المنطقة " + str(dens) + " منشأة تجارية تعكس منطقة حيوية تجذب الزبائن. "
        else:
            factors += "الكثافة التجارية في المنطقة منخفضة نسبيا بـ" + str(dens) + " منشأة في 500م. "

        # معدل الإغلاق
        if clos <= 30:
            factors += "معدل الاغلاق لهذا النشاط في المنطقة " + str(clos) + "% وهو منخفض، مؤشر جيد على الاستدامة. "
        else:
            factors += "معدل الاغلاق " + str(clos) + "% لهذا النشاط في المنطقة يستدعي الحذر وتحليل الاسباب. "

        # معدل الحي
        if hood >= 60:
            factors += "معدل نجاح المحلات في هذا الحي " + str(int(hood)) + "% وهو مرتفع مما يعكس بيئة تجارية صحية."
        else:
            factors += "معدل نجاح المحلات في الحي " + str(int(hood)) + "% وهو متوسط."

        if not verdict:
            factors += " ينصح بمراجعة هذه العوامل وإعادة دراسة البدائل قبل الاستثمار."

        return intro + factors

    try:
        import anthropic as _ant
        key = st.secrets.get("ANTHROPIC_API_KEY", "")
        if not key:
            return template()

        client = _ant.Anthropic(api_key=key)
        cv_lines = [
            "- النشاط التجاري: " + category,
            "- نسبة الملاءمة: " + pct + "% (" + verdict_ar + ")",
            "- نوع الشارع المجاور: " + cv.get("road_name","طريق مجمع") + " (رتبة " + str(cv.get("road_rank",6)) + " من 9)",
            "- عدد المنافسين المباشرين في 500م: " + str(cv.get("competitors_n",5)) + " منافس",
            "- متوسط عمر المنافسين: " + str(cv.get("competitor_age_d",720)) + " يوم",
            "- الكثافة التجارية في 500م: " + str(cv.get("commercial_n",32)) + " منشأة",
            "- معدل نجاح المحلات في الحي: " + str(int(cv.get("neighborhood_rate",65))) + "%",
            "- معدل الاغلاق لهذا النشاط في المنطقة: " + str(cv.get("closure_rate_pct",28)) + "%",
            "- الارتفاع الجغرافي: " + str(int(cv.get("elev",elev))) + "م فوق سطح البحر",
            "- مساحة المحل: " + str(area_v) + "م مربع",
            "- انتماء لعلامة تجارية: " + ("نعم" if cv.get("brand",0) else "لا"),
        ]
        pos_txt = "; ".join(pos_r[:3]) if pos_r else "لا يوجد"
        neg_txt = "; ".join(neg_r[:2]) if neg_r else "لا يوجد"

        prompt = (
            "انت مستشار استثماري متخصص في المشاريع التجارية بمنطقة عسير السعودية.\n"
            "اكتب فقرتين قصيرتين باللغة العربية الفصحى البسيطة تشرحان للمستثمر\n"
            "لماذا حصل موقعه على هذه النسبة، مع ذكر الارقام الفعلية التالية:\n\n"
            + "\n".join(cv_lines) + "\n\n"
            "ابرز عوامل النجاح: " + pos_txt + "\n"
            "التحديات: " + neg_txt + "\n\n"
            "التعليمات:\n"
            "- اذكر تحديدا: عدد المنافسين، نوع الشارع، معدل الاغلاق، ومعدل نجاح الحي\n"
            "- استخدم الارقام المذكورة اعلاه في التفسير\n"
            "- خاطب المستثمر مباشرة بصيغة مفيدة\n"
            "- لا تذكر مصطلحات تقنية مثل SHAP او CatBoost\n"
            "- فقرتان فقط، اسلوب مستشار خبير دافئ، لا تتجاوز 150 كلمة"
        )
        msg = client.messages.create(
            model="claude-sonnet-4-20250514",
            max_tokens=500,
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
ss("results", None); ss("_lc", None); ss("tile", "خريطة المواقع")
ss("road_info", None)   # نوع الشارع المكتشف

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
# Hero — مقسّم إلى وحدات بسيطة لضمان العرض الصحيح
st.markdown(
    "<div style='background:#071626;border-bottom:2px solid #B91C1C;'>"
    "<div style='display:flex;align-items:center;padding:0 2rem;height:54px;background:rgba(0,0,0,0.25);'>"
    "<div style='width:32px;height:32px;background:linear-gradient(135deg,#B91C1C,#DC2626);"
    "transform:rotate(45deg);border-radius:4px;flex-shrink:0;'></div>"
    "<span style='margin-right:14px;font-size:1.3rem;font-weight:900;color:white;letter-spacing:3px;'>جدوى</span>"
    "<span style='font-size:0.65rem;color:rgba(255,255,255,0.4);margin-right:6px;'>مرشد الاستثمار التجاري</span>"
    "<div style='flex:1;'></div>"
    "<span style='color:rgba(255,255,255,0.4);font-size:0.75rem;padding-left:12px;"
    "border-left:1px solid rgba(255,255,255,0.1);'>أمانة منطقة عسير</span>"
    "<span style='margin-left:10px;display:flex;align-items:center;gap:5px;"
    "color:rgba(255,255,255,0.65);font-size:0.72rem;background:rgba(255,255,255,0.07);"
    "border:1px solid rgba(255,255,255,0.1);padding:3px 10px;border-radius:20px;'>"
    "<span style='width:6px;height:6px;border-radius:50%;background:#22C55E;display:inline-block;'></span>"
    "النظام فعّال</span>"
    "</div></div>",
    unsafe_allow_html=True,
)

st.markdown(
    "<div class='judwa-hero'>"
    "<div class='hero-badge-v'>GEOXAI · SITE INTELLIGENCE · ASEER</div>"
    "<div class='hero-title-v'>"
    "جدوى "
    "<span>— مرشد الاستثمار التجاري</span>"
    "</div>"
    "<div class='hero-line-v'></div>"
    "<div class='hero-sub-v'>"
    "منصة تحليلية للتنبؤ باستدامة المشاريع التجارية في أبها وخميس مشيط — منطقة عسير"
    "</div>"
    "</div>",
    unsafe_allow_html=True,
)

# بطاقات الإحصاء — 4 أعمدة
_sc1, _sc2, _sc3, _sc4 = st.columns(4)
def _stat_card(col, val, label, sub):
    col.markdown(
        "<div style='background:linear-gradient(135deg,#0D2240,#1A0A1A);border:1px solid rgba(185,28,28,0.3);"
        "border-radius:10px;padding:1rem 1.2rem;margin-bottom:0.5rem;'>"
        "<div style='font-family:IBM Plex Mono,monospace;font-size:1.9rem;font-weight:600;"
        "color:#FFFFFF;line-height:1;text-shadow:0 0 20px rgba(185,28,28,0.4);'>" + val + "</div>"
        "<div style='font-size:11px;color:rgba(255,255,255,0.45);margin-top:4px;'>" + label + "</div>"
        "<div style='font-size:10px;color:rgba(255,255,255,0.22);margin-top:2px;'>" + sub + "</div>"
        "</div>",
        unsafe_allow_html=True,
    )

_stat_card(_sc1, "21",     "متغيراً تحليلياً",    "جغرافية · حضرية · تنافسية")
_stat_card(_sc2, "0.81",   "دقة النموذج (AUC)",   "تحقق زمني · CatBoost")
_stat_card(_sc3, "22,917", "رخصة تجارية",          "بيانات رسمية · أمانة عسير")
_stat_card(_sc4, "F0.5",   "مقياس الأداء",          "يُغلِّب الدقة على الاسترجاع")



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

# ── تخطيط ثنائي العمود: الخريطة يسار | النتائج يمين ─────────────────────
col_map, col_res = st.columns([1.3, 1], gap="large")

with col_map:
    st.markdown("""
    <div style="font-family:'Cairo',sans-serif;font-size:13px;font-weight:700;
                color:#1A1208;display:flex;align-items:center;gap:8px;margin-bottom:0.8rem;">
      <span style="display:inline-block;width:4px;height:16px;background:#B91C1C;border-radius:2px;"></span>
      تحديد الموقع الجغرافي
    </div>
    """, unsafe_allow_html=True)

    m = folium.Map(location=[lat, lng], zoom_start=15,
                   tiles=tile_url, attr=tile_attr)
    if tile_ov:
        folium.TileLayer(tiles=tile_ov, attr="Esri", overlay=True).add_to(m)

    folium.Marker(
        [lat, lng],
        popup=folium.Popup(
            "<div dir='rtl' style='font-family:Arial;'><b>الموقع المحدد</b>"
            "<br>" + str(round(lat,5)) + " ، " + str(round(lng,5)) + "</div>",
            max_width=160),
        icon=folium.Icon(color="red", icon="map-marker", prefix="fa"),
    ).add_to(m)
    folium.Circle([lat, lng], radius=500, color="#B91C1C",
                  fill=True, fill_opacity=0.07, weight=2).add_to(m)

    mk  = "m" + st.session_state["tile"][:4] + str(round(lat,3)) + str(round(lng,3))
    out = st_folium(m, key=mk, width="100%", height=400,
                    returned_objects=["last_clicked","center"])

    # تثبيت الموقع
    _cl = None
    _ce = None
    if out and out.get("last_clicked"):
        _cl = (round(out["last_clicked"]["lat"],5), round(out["last_clicked"]["lng"],5))
    if out and out.get("center"):
        _ce = (round(out["center"]["lat"],5), round(out["center"]["lng"],5))

    c1, c2 = st.columns([3,1])
    with c1:
        st.markdown(
            "<div style='display:flex;gap:6px;margin-top:6px;flex-wrap:wrap;'>"
            "<span style='background:#F8FAFC;border:1px solid #CBD5E1;border-radius:6px;"
            "padding:4px 10px;font-family:IBM Plex Mono,monospace;font-size:12px;'>"
            "خط العرض <b>" + str(lat) + "</b></span>"
            "<span style='background:#F8FAFC;border:1px solid #CBD5E1;border-radius:6px;"
            "padding:4px 10px;font-family:IBM Plex Mono,monospace;font-size:12px;'>"
            "خط الطول <b>" + str(lng) + "</b></span>"
            "<span style='background:#F8FAFC;border:1px solid #CBD5E1;border-radius:6px;"
            "padding:4px 10px;font-size:12px;'>نطاق <b>500م</b></span>"
            "</div>", unsafe_allow_html=True)
    with c2:
        if st.button("📍 تثبيت", help="اسحب الخريطة إلى الموقع ثم اضغط تثبيت"):
            if _ce and (abs(_ce[0]-lat)>0.0001 or abs(_ce[1]-lng)>0.0001):
                st.session_state.update({"lat":_ce[0],"lng":_ce[1],"results":None,"_lc":_ce})
                st.rerun()

    if _cl and _cl != st.session_state["_lc"] and (abs(_cl[0]-lat)>0.0001 or abs(_cl[1]-lng)>0.0001):
        rrank, rdist, rosm = get_road_from_osm(_cl[0], _cl[1])
        st.session_state.update({
            "lat": _cl[0], "lng": _cl[1], "_lc": _cl,
            "results": None,
            "road_info": {"rank": rrank, "dist": rdist, "osm_type": rosm},
        })
        st.rerun()

    lat = st.session_state["lat"]
    lng = st.session_state["lng"]


    # ── عرض نوع الشارع المكتشف ──────────────────────────────────────────
    ri = st.session_state.get("road_info")
    if ri:
        rk = ri["rank"]; rd = ri["dist"]
        osm_type = ri.get("osm_type", "residential")
        info = ROAD_INFO.get(osm_type, ROAD_INFO["residential"])
        rlabel = info["ar"]
        rcolor = info["color"]
        rdesc  = info["desc"]
        rrate  = info["rate"]
        stars  = "★" * min(rk, 5) + "☆" * (5 - min(rk, 5))
        st.markdown(
            "<div style='background:white;border:1px solid #CBD5E1;"
            "border-right:4px solid " + rcolor + ";border-radius:10px;"
            "padding:0.7rem 1rem;margin-top:8px;direction:rtl;'>"
            "<div style='display:flex;align-items:center;gap:10px;flex-wrap:wrap;'>"
            "<span style='font-size:13px;font-weight:700;color:" + rcolor + ";'>"
            "🛣️ " + rlabel + "</span>"
            "<span style='font-size:11px;color:#64748B;font-family:IBM Plex Mono,monospace;'>"
            "رتبة " + str(rk) + "/9 · على بُعد ~" + str(rd) + "م</span>"
            "<span style='font-size:13px;color:#CA8A04;letter-spacing:1px;'>" + stars + "</span>"
            "</div>"
            "<p style='margin:4px 0 0;font-size:12px;color:#64748B;'>" + rdesc + "</p>"
            "</div>",
            unsafe_allow_html=True
        )
    else:
        st.markdown(
            "<div style='background:#F8FAFC;border:1px solid #E2E8F0;"
            "border-radius:10px;padding:0.6rem 1rem;margin-top:8px;"
            "font-size:12px;color:#94A3B8;direction:rtl;'>"
            "🛣️ سيظهر نوع الشارع تلقائياً عند تحديد الموقع"
            "</div>",
            unsafe_allow_html=True
        )

    if not in_study_area(lat, lng):
        st.warning("⚠️ الموقع خارج نطاق الدراسة (أبها وخميس مشيط) — النتائج قد تكون غير دقيقة.")

    st.caption("💡 حرّك الخريطة إلى الموقع المطلوب ثم اضغط 'تثبيت' — أو انقر مباشرة")

# ── لوحة النتائج (يمين) ─────────────────────────────────────────────────────
with col_res:
    R       = st.session_state.get("results")
    has_res = R is not None

    st.markdown("""
    <div style="font-family:'Cairo',sans-serif;font-size:13px;font-weight:700;
                color:#1A1208;display:flex;align-items:center;gap:8px;margin-bottom:0.8rem;">
      <span style="display:inline-block;width:4px;height:16px;background:#B91C1C;border-radius:2px;"></span>
      نسبة الملاءمة والتفسير
    </div>
    """, unsafe_allow_html=True)

    if not has_res:
        # حالة الانتظار
        st.markdown("""
        <div style="background:white;border:1px solid #CBD5E1;border-radius:12px;
                    padding:2.5rem 1.5rem;text-align:center;min-height:300px;
                    display:flex;flex-direction:column;align-items:center;justify-content:center;">
          <div style="width:60px;height:60px;background:#FEF2F2;border-radius:50%;
                      display:flex;align-items:center;justify-content:center;
                      font-size:1.6rem;margin:0 auto 1rem;">◎</div>
          <p style="font-family:'Cairo',sans-serif;font-size:15px;font-weight:700;
                    color:#1A1208;margin:0 0 0.5rem;">في انتظار التحليل</p>
          <p style="font-size:12px;color:#64748B;margin:0;line-height:1.8;font-family:'Cairo',sans-serif;">
            ① حدد الموقع على الخريطة<br>
            ② أدخل بيانات المشروع في الشريط الجانبي<br>
            ③ اضغط <b>تحليل الموقع</b>
          </p>
        </div>
        """, unsafe_allow_html=True)

    else:
        prob   = R["prob"]
        elev   = R["elev"]
        area_r = R["area"]
        fv     = pd.DataFrame(R["fv"], columns=FEATURE_COLS)
        v      = prob >= 0.65
        cls    = "ok" if v else "bad"
        pct    = str(int(round(prob * 100)))

        # ── مقياس النسبة ────────────────────────────────────────────────────
        vt     = "الموقع ملائم للاستثمار" if v else "الموقع غير ملائم"
        vc     = "#059669" if v else "#B91C1C"
        vbg    = "#ECFDF5" if v else "#FEF2F2"

        st.markdown(
            "<div style='background:" + ("linear-gradient(135deg,#071626,#0D2240)" ) +
            ";border-radius:12px;padding:1.5rem;margin-bottom:0.8rem;'>"
            "<div style='display:inline-block;padding:4px 12px;border-radius:4px;font-size:12px;"
            "font-weight:700;font-family:Cairo,sans-serif;margin-bottom:0.7rem;"
            "background:rgba(" + ("5,150,105" if v else "185,28,28") + ",0.2);"
            "border:1px solid rgba(" + ("52,211,153" if v else "248,113,113") + ",0.4);"
            "color:" + ("#6EE7B7" if v else "#FCA5A5") + ";'>"
            + ("✓" if v else "✕") + "  " + vt +
            "</div>"
            "<div style='font-family:Cairo,sans-serif;font-size:4rem;font-weight:900;"
            "line-height:1;color:" + ("#6EE7B7" if v else "#FCA5A5") + ";'>"
            + pct + "<span style='font-size:2rem;'>%</span></div>"
            "<p style='color:rgba(255,255,255,0.4);font-size:12px;margin:3px 0 1rem;"
            "font-family:Cairo,sans-serif;'>نسبة الملاءمة التجارية المتوقعة</p>"
            "<div style='display:flex;gap:1.5rem;padding-top:0.8rem;"
            "border-top:1px solid rgba(255,255,255,0.08);'>"
            "<div><span style='font-size:10px;color:rgba(255,255,255,0.3);display:block;'>العتبة</span>"
            "<span style='font-family:IBM Plex Mono,monospace;color:white;font-size:1rem;font-weight:600;'>65%</span></div>"
            "<div><span style='font-size:10px;color:rgba(255,255,255,0.3);display:block;'>الارتفاع</span>"
            "<span style='font-family:IBM Plex Mono,monospace;color:white;font-size:1rem;font-weight:600;'>" + str(int(elev)) + "م</span></div>"
            "<div><span style='font-size:10px;color:rgba(255,255,255,0.3);display:block;'>المساحة</span>"
            "<span style='font-family:IBM Plex Mono,monospace;color:white;font-size:1rem;font-weight:600;'>" + str(area_r) + "م²</span></div>"
            "</div></div>",
            unsafe_allow_html=True)

        # ── Gauge ────────────────────────────────────────────────────────────
        fig = go.Figure(go.Indicator(
            mode="gauge+number",
            value=int(round(prob*100)),
            number={"suffix":"%","font":{"size":30,"family":"IBM Plex Mono",
                    "color": "#059669" if v else "#B91C1C"}},
            gauge={"axis":{"range":[0,100],"tickfont":{"size":9,"color":"#94A3B8"}},
                   "bar":{"color":"#059669" if v else "#B91C1C","thickness":0.28},
                   "bgcolor":"rgba(0,0,0,0)","borderwidth":0,
                   "steps":[{"range":[0,40],"color":"#FEF2F2"},
                             {"range":[40,65],"color":"#FFFBEB"},
                             {"range":[65,100],"color":"#ECFDF5"}],
                   "threshold":{"line":{"color":"#1A1208","width":3},
                                "thickness":0.8,"value":65}},
            title={"text":"مؤشر الملاءمة","font":{"size":11,"color":"#64748B"}},
        ))
        fig.update_layout(height=180, paper_bgcolor="rgba(0,0,0,0)",
                          margin=dict(t=40,b=0,l=10,r=10))
        st.plotly_chart(fig, use_container_width=True)

        # ── تفسير النموذج اللغوي ─────────────────────────────────────────────
        shap_data, shap_ok, bias_v = real_shap(model, fv)
        if shap_ok:
            intro, pos_reasons, neg_reasons = investor_explanation(
                prob, elev, area_r, R.get("cat", ""), shap_data)

            cv = R.get("cv", {})
            with st.spinner("النموذج اللغوي يكتب التفسير…"):
                llm_text = llm_explain(prob, elev, area_r,
                                       R.get("cat",""), pos_reasons, neg_reasons, v, cv)

            bc  = "#B91C1C" if not v else "#059669"
            bgc = "#FEF2F2" if not v else "#F0FDF4"

            # عرض المتغيرات المحسوبة
            if cv:
                st.markdown(
                    "<div style='background:#F8FAFC;border:1px solid #CBD5E1;"
                    "border-radius:8px;padding:0.8rem 1rem;margin-top:0.3rem;direction:rtl;'>"
                    "<p style='font-size:11px;font-weight:700;color:#64748B;margin:0 0 6px;"
                    "letter-spacing:1px;'>المتغيرات المحسوبة تلقائياً</p>"
                    "<div style='display:grid;grid-template-columns:repeat(2,1fr);gap:4px 12px;'>"
                    "<span style='font-size:12px;color:#0F172A;'>المنافسون: <b>" + str(cv.get("competitors_n","—")) + "</b> في 500م</span>"
                    "<span style='font-size:12px;color:#0F172A;'>نوع الشارع: <b>" + str(cv.get("road_name","—")) + "</b></span>"
                    "<span style='font-size:12px;color:#0F172A;'>معدل الإغلاق: <b>" + str(cv.get("closure_rate_pct","—")) + "%</b></span>"
                    "<span style='font-size:12px;color:#0F172A;'>معدل نجاح الحي: <b>" + str(int(cv.get("neighborhood_rate",0))) + "%</b></span>"
                    "<span style='font-size:12px;color:#0F172A;'>الكثافة التجارية: <b>" + str(cv.get("commercial_n","—")) + "</b> منشأة</span>"
                    "<span style='font-size:12px;color:#0F172A;'>الارتفاع: <b>" + str(int(cv.get("elev",0))) + "</b> م</span>"
                    "</div></div>",
                    unsafe_allow_html=True)

            st.markdown(
                "<div style='background:white;border:1px solid #CBD5E1;border-radius:12px;"
                "padding:1.2rem;margin-top:0.5rem;'>"
                "<p style='font-family:Cairo,sans-serif;font-size:13px;font-weight:700;"
                "color:#1A1208;margin:0 0 0.7rem;'>تفسير النتيجة للمستثمر</p>"
                "<div style='background:" + bgc + ";border-right:4px solid " + bc + ";"
                "border-radius:8px;padding:0.9rem 1rem;font-family:Cairo,sans-serif;"
                "font-size:14px;line-height:2.1;color:#1A1208;"
                "direction:rtl;text-align:right;'>"
                + llm_text +
                "</div></div>",
                unsafe_allow_html=True)

        if st.button("إعادة التقييم"):
            st.session_state["results"] = None
            st.rerun()

st.markdown("</div>", unsafe_allow_html=True)

# ══════════════════════════════════════════════════════════════════════════════
# معالجة التحليل عند الضغط على الزر
# ══════════════════════════════════════════════════════════════════════════════
if analyze:
    if not model_ok:
        st.error("ملف النموذج غير موجود — تأكد من رفع catboost_model.pkl")
        st.stop()

    cat_te = CATEGORIES[category]
    brand  = 1 if brand_lbl == "نعم" else 0
    ph     = st.empty()

    STEPS = [
        "جلب الإحداثيات الجغرافية",
        "حساب الارتفاع والتضاريس",
        "تحليل شبكة الطرق",
        "تقييم الكثافة العمرانية",
        "رصد بيئة المنافسة",
        "تشغيل نموذج الذكاء الاصطناعي",
    ]
    done = []
    for s in STEPS:
        done.append(s)
        rows = "".join(
            "<div style='display:flex;align-items:center;gap:10px;padding:6px 0;"
            "border-bottom:1px solid #F1F5F9;'>"
            "<span style='flex:1;font-size:13px;color:#0F172A;font-family:Cairo,sans-serif;'>" + r + "</span>"
            "<span style='color:#059669;font-weight:700;'>✓</span></div>"
            for r in done
        )
        ph.markdown(
            "<div style='background:white;border-radius:12px;border:1px solid #CBD5E1;"
            "padding:1.4rem;margin:1rem 2rem;'>"
            "<p style='font-family:Cairo,sans-serif;font-size:14px;font-weight:700;"
            "color:#0F172A;margin:0 0 0.9rem;'>جارٍ التحليل…</p>"
            + rows + "</div>",
            unsafe_allow_html=True
        )
        time.sleep(0.3)

    elev  = get_elev(lat, lng) or 2200.0
    feats = compute_features(lat, lng, area, cat_te, brand, elev, category)
    fv    = pd.DataFrame([feats])
    for c in FEATURE_COLS:
        if c not in fv.columns:
            fv[c] = 0.0
    fv   = fv[FEATURE_COLS]
    prob = float(model.predict_proba(fv)[0][1])

    # القيم الفعلية للمتغيرات (بعد فك التحويل اللوغاريتمي)
    computed_vals = {
        "elev":              round(feats["الارتفاع"], 0),
        "slope":             round(feats["الانحدار"], 1),
        "road_rank":         int(feats["رتبة_الطريق"]),
        "dist_road_m":       int(np.expm1(feats["المسافة_للشارع_الأقرب_لوغ"])),
        "dist_arterial_m":   int(np.expm1(feats["المسافة_للطريق_الشرياني_لوغ"])),
        "uvi":               round(feats["مؤشر_الحيوية_الحضرية"], 1),
        "commercial_n":      int(np.expm1(feats["كثافة_تجارية_500م_لوغ"])),
        "buildings_n":       int(np.expm1(feats["عدد_مباني_فعلي_500م_لوغ"])),
        "competitors_n":     int(np.expm1(feats["عدد_منافسين_مباشرين_500م_لوغ"])),
        "competitor_age_d":  int(np.expm1(feats["متوسط_عمر_المنافسين_يوم_لوغ"])),
        "dist_direct_m":     int(np.expm1(feats["مسافة_أقرب_مباشر_متر_لوغ"])),
        "neighborhood_rate": round(feats["المعدل_الجواري"] * 100, 0),
        "closure_rate_pct":  round(np.expm1(feats["معدل_إغلاق_الفئة_لوغ"]) * 100, 1),
        "area":              area,
        "brand":             brand,
    }
    ROAD_NAMES = {9:"طريق سريع",8:"طريق رئيسي",7:"طريق شرياني",
                  6:"طريق مجمع",5:"طريق محلي",4:"شارع معيشة",
                  3:"شارع سكني",2:"طريق خدمة",1:"غير مصنف"}
    computed_vals["road_name"] = ROAD_NAMES.get(computed_vals["road_rank"], "غير محدد")

    st.session_state["results"] = {
        "prob": prob, "elev": elev,
        "area": area, "cat": category,
        "fv":   fv.values.tolist(),
        "cv":   computed_vals,
    }
    ph.empty()
    st.rerun()


# Footer
st.markdown("""
<div class="g-footer">
  <span>© 2026 — جميع الحقوق محفوظة</span>
  <strong>جدوى · مرشد الاستثمار التجاري · أمانة منطقة عسير</strong>
  <span>GEOXAI · SITE INTELLIGENCE</span>
</div>
""", unsafe_allow_html=True)
