"""
جدوى — نظام تقييم ملاءمة المواقع التجارية
من عسير · أبها وخميس مشيط
"""

import streamlit as st
import pandas as pd
import numpy as np
import joblib
import folium
from streamlit_folium import st_folium
import plotly.graph_objects as go
import requests

# ─────────────────────────────────────────────────────────────────────────────
# إعداد الصفحة
# ─────────────────────────────────────────────────────────────────────────────
st.set_page_config(
    page_title="جدوى · من عسير",
    page_icon="◆",
    layout="wide",
    initial_sidebar_state="expanded",
)

# ─────────────────────────────────────────────────────────────────────────────
# CSS — هوية عسير الكاملة
# ─────────────────────────────────────────────────────────────────────────────
st.markdown("""
<style>

/* ══ 1. خلفية نمط الماس ═══════════════════════════════════════════════════ */
.stApp {
    background-color: #0D1B2A;
    background-image: url("data:image/svg+xml,%3Csvg xmlns='http://www.w3.org/2000/svg' width='80' height='80'%3E%3Crect width='80' height='80' fill='%230D1B2A'/%3E%3Cpolygon points='40,3 77,40 40,77 3,40' fill='none' stroke='%23C41230' stroke-width='0.8' opacity='0.22'/%3E%3Cpolygon points='40,18 62,40 40,62 18,40' fill='none' stroke='%23F5821F' stroke-width='0.6' opacity='0.14'/%3E%3Ccircle cx='40' cy='40' r='1.5' fill='%23F5821F' opacity='0.18'/%3E%3C/svg%3E");
    background-repeat: repeat;
}

/* طبقة زجاجية على المحتوى الرئيسي */
.main .block-container {
    background: rgba(10, 20, 35, 0.55);
    backdrop-filter: blur(2px);
    border-radius: 16px;
    padding: 1.5rem 2rem 2rem;
    border: 1px solid rgba(196, 18, 48, 0.15);
}

/* ══ 2. الشريط الجانبي ═══════════════════════════════════════════════════ */
[data-testid="stSidebar"] {
    background: linear-gradient(180deg, #0A1220 0%, #0D1B2A 50%, #0A1220 100%) !important;
    border-right: 3px solid #C41230 !important;
}
[data-testid="stSidebar"] label,
[data-testid="stSidebar"] p,
[data-testid="stSidebar"] span { color: #D8DCE8 !important; }
[data-testid="stSidebar"] h2 {
    color: #F5821F !important;
    font-size: 1.0rem !important;
    border-bottom: 1px solid rgba(196,18,48,0.3);
    padding-bottom: 4px;
    margin-top: 1rem !important;
}

/* ══ 3. التابات ══════════════════════════════════════════════════════════ */
.stTabs [data-baseweb="tab-list"] {
    background: rgba(13,27,42,0.85);
    border-radius: 12px; padding: 5px; gap: 4px;
    border: 1px solid rgba(196,18,48,0.3);
}
.stTabs [data-baseweb="tab"] {
    color: #9BAABF !important;
    border-radius: 9px !important;
    font-size: 14px; padding: 0.5rem 1rem;
}
.stTabs [aria-selected="true"] {
    background: #C41230 !important;
    color: white !important; font-weight: 600 !important;
}

/* ══ 4. بطاقات المقاييس ══════════════════════════════════════════════════ */
[data-testid="stMetric"] {
    background: rgba(27,58,107,0.35) !important;
    border: 1px solid rgba(245,130,31,0.25) !important;
    border-left: 4px solid #F5821F !important;
    border-radius: 12px !important;
    padding: 0.8rem !important;
    backdrop-filter: blur(6px);
}
[data-testid="stMetricValue"] { color: #FFFFFF !important; font-size: 1.5rem !important; }
[data-testid="stMetricLabel"] { color: #F5C07A !important; font-size: 0.82rem !important; }

/* ══ 5. الأزرار ══════════════════════════════════════════════════════════ */
.stButton > button {
    background: linear-gradient(135deg, #C41230, #9B0E25) !important;
    color: white !important; border: none !important;
    border-radius: 10px !important; font-weight: 700 !important;
    font-size: 14px !important; padding: 0.55rem 1.4rem !important;
    transition: all 0.25s ease; letter-spacing: 0.5px;
}
.stButton > button:hover {
    background: linear-gradient(135deg, #F5821F, #D4691A) !important;
    transform: translateY(-2px);
    box-shadow: 0 4px 15px rgba(245,130,31,0.4) !important;
}

/* ══ 6. حقول الإدخال ════════════════════════════════════════════════════ */
.stSelectbox div[data-baseweb="select"] > div,
.stNumberInput input, .stTextInput input {
    background: rgba(15,30,55,0.75) !important;
    border: 1px solid rgba(196,18,48,0.35) !important;
    border-radius: 8px !important; color: white !important;
}

/* ══ 7. الإشعارات ════════════════════════════════════════════════════════ */
[data-testid="stSuccessMessage"] {
    background: rgba(40,167,69,0.12) !important;
    border: 1px solid rgba(40,167,69,0.5) !important;
    color: #90EE90 !important; border-radius: 10px !important;
}
[data-testid="stErrorMessage"] {
    background: rgba(220,53,69,0.12) !important;
    border: 1px solid rgba(220,53,69,0.5) !important;
    color: #FFB3B3 !important; border-radius: 10px !important;
}
[data-testid="stInfoMessage"], [data-testid="stWarningMessage"] {
    background: rgba(27,58,107,0.3) !important;
    border: 1px solid rgba(245,130,31,0.4) !important;
    color: #F5C07A !important; border-radius: 10px !important;
}

/* ══ 8. الاتجاه RTL والنصوص ══════════════════════════════════════════════ */
html, body, [class*="css"] { direction: rtl; }
[data-testid="stSidebar"] { direction: rtl; }
.stMarkdown p { color: #CDD2DF; line-height: 1.7; }
h1, h2, h3 { color: white !important; }
hr { border-color: rgba(196,18,48,0.3) !important; margin: 1rem 0 !important; }

/* ══ 9. بطاقات الحكم ════════════════════════════════════════════════════ */
.verdict-box {
    border-radius: 14px; padding: 1.2rem 1.5rem; margin: 0.6rem 0;
    text-align: center; font-size: 18px; font-weight: 700;
}
.verdict-success {
    background: rgba(40,167,69,0.15); border: 2px solid rgba(40,167,69,0.6);
    color: #90EE90; box-shadow: 0 0 20px rgba(40,167,69,0.12);
}
.verdict-fail {
    background: rgba(220,53,69,0.15); border: 2px solid rgba(220,53,69,0.6);
    color: #FFB3B3; box-shadow: 0 0 20px rgba(220,53,69,0.12);
}

/* ══ 10. الشارات ════════════════════════════════════════════════════════ */
.info-badge {
    background: rgba(27,58,107,0.55); border: 1px solid rgba(245,130,31,0.35);
    border-radius: 8px; padding: 0.35rem 0.75rem; font-size: 13px; color: #F5C07A;
    display: inline-block; margin: 3px; backdrop-filter: blur(4px);
}

</style>
""", unsafe_allow_html=True)


# ─────────────────────────────────────────────────────────────────────────────
# رأسية البطل — "جدوى من عسير" + أفق عمراني
# ─────────────────────────────────────────────────────────────────────────────
st.markdown("<h1 style='text-align:center;color:white;font-size:3.8rem;font-weight:900;letter-spacing:8px;margin:0.5rem 0 0;padding-top:1rem;'>جدوى</h1>", unsafe_allow_html=True)
st.markdown("<p style='text-align:center;color:#F5821F;font-size:1rem;letter-spacing:5px;font-weight:500;margin:0.2rem 0;'>من عسير</p>", unsafe_allow_html=True)
st.markdown("<p style='text-align:center;color:rgba(255,255,255,0.6);font-size:0.85rem;margin:0 0 0.5rem;'>نظام ذكي لتقييم ملاءمة المواقع التجارية · أبها وخميس مشيط</p>", unsafe_allow_html=True)
st.markdown("<hr style='border-color:rgba(196,18,48,0.4);margin:0.8rem 0 1.5rem;'>", unsafe_allow_html=True)


# ─────────────────────────────────────────────────────────────────────────────
# تحميل النموذج
# ─────────────────────────────────────────────────────────────────────────────
# الترتيب الثابت للأعمدة — مطابق لما دُرِّب عليه النموذج
@st.cache_resource
def load_model():
    try:
        model = joblib.load("catboost_model.pkl")
        # نأخذ أسماء الأعمدة مباشرة من النموذج
        feature_cols = list(model.feature_names_)
        return model, feature_cols, True
    except Exception:
        return None, None, False

model, FEATURE_COLS, model_loaded = load_model()
original_cols = FEATURE_COLS if FEATURE_COLS else []


# ─────────────────────────────────────────────────────────────────────────────
# القواميس
# ─────────────────────────────────────────────────────────────────────────────
ROAD_RANK = {
    "طريق سريع (motorway)":       9,
    "طريق رئيسي (trunk)":         8,
    "طريق شرياني (primary)":      7,
    "طريق مجمع (secondary)":      6,
    "طريق محلي (tertiary)":       5,
    "شارع معيشة (living_street)":  4,
    "طريق سكني (residential)":    3,
    "طريق خدمة (service)":        2,
    "غير مصنف":                   1,
}

CATEGORY_TE = {
    "الصراف الآلي":                 0.85,
    "محطات الوقود":                 0.80,
    "الأنشطة الطبية":               0.78,
    "الأنشطة التعليمية":            0.75,
    "الفنادق والإيواء":             0.73,
    "تجارة التجزئة والجملة":        0.72,
    "المطابخ والمطاعم":             0.68,
    "قصور الأفراح":                 0.70,
    "المقاولات والخدمات الفنية":    0.70,
    "دور العرض والاستراحات":        0.65,
    "خدمات السيارات":               0.65,
    "المستودعات":                   0.65,
    "مدن الملاهي والترفيه":         0.62,
    "الورش المهنية":                0.60,
    "محلات التشليح":                0.55,
}

FACILITY_TYPE_TE = {
    "شركة":         0.76,
    "عيادة":        0.78,
    "مدرسة / معهد": 0.75,
    "فندق / شقق":   0.73,
    "محل تجاري":   0.70,
    "مطعم":        0.68,
    "مؤسسة فردية": 0.65,
    "مستودع":      0.62,
    "ورشة":        0.60,
}


# ─────────────────────────────────────────────────────────────────────────────
# دوال مساعدة
# ─────────────────────────────────────────────────────────────────────────────
def get_elevation(lat, lng):
    try:
        r = requests.get(
            f"https://api.open-elevation.com/api/v1/lookup?locations={lat},{lng}",
            timeout=6)
        if r.status_code == 200:
            return r.json()["results"][0]["elevation"]
    except Exception:
        pass
    return None


def build_feature_vector(inp):
    features = {
        "الاحداثي الجغرافي X":          inp["lng"],
        "الاحداثي الجغرافي Y":          inp["lat"],
        "الارتفاع":                      inp["elevation"],
        "الانحدار":                      inp["slope"],
        "المسافة_للشارع_الأقرب_لوغ":    np.log1p(inp["dist_road"]),
        "المسافة_للطريق_الشرياني_لوغ":  np.log1p(inp["dist_arterial"]),
        "المسافة_لأقرب_معلم_سياحي_لوغ": np.log1p(inp["dist_tourist"]),
        "رتبة_الطريق":                   inp["road_rank"],
        "مؤشر_الحيوية_الحضرية":         inp["uvi"],
        "كثافة_تجارية_500م_لوغ":        np.log1p(inp["commercial_density"]),
        "عدد_مباني_فعلي_500م_لوغ":      np.log1p(inp["buildings_count"]),
        "متوسط_عمر_المنافسين_يوم_لوغ":  np.log1p(max(inp["competitor_age"], 0)),
        "عدد_منافسين_مباشرين_500م_لوغ": np.log1p(inp["direct_competitors"]),
        "مسافة_أقرب_مباشر_متر_لوغ":    np.log1p(inp["dist_direct"]),
        "المعدل_الجواري":                inp["neighborhood_rate"],
        "معدل_إغلاق_الفئة_لوغ":         np.log1p(inp["closure_rate"]),
        "مساحة_المنشأة_لوغ":            np.log1p(inp["area"]),
        "الانتماء_لعلامة_تجارية":       inp["has_brand"],
        "مدة_الرخصة_لوغ":              np.log1p(inp["license_years"]),
        "نوع_المنشأة_TE":               inp["facility_te"],
        "فئة_النشاط_TE":                inp["category_te"],
    }
    return pd.DataFrame([features])


def gauge_chart(prob, threshold=0.65):
    color = "#27AE60" if prob >= threshold else "#E74C3C"
    fig = go.Figure(go.Indicator(
        mode="gauge+number",
        value=round(prob * 100, 1),
        number={"suffix": "%", "font": {"size": 42, "color": color}},
        gauge={
            "axis": {"range": [0, 100], "tickwidth": 1,
                     "tickcolor": "#555", "tickfont": {"color": "#aaa"}},
            "bar":  {"color": color, "thickness": 0.28},
            "bgcolor": "rgba(0,0,0,0)",
            "bordercolor": "rgba(255,255,255,0.1)",
            "steps": [
                {"range": [0,  40], "color": "rgba(220,53,69,0.18)"},
                {"range": [40, 65], "color": "rgba(255,193,7,0.15)"},
                {"range": [65, 100], "color": "rgba(40,167,69,0.18)"},
            ],
            "threshold": {
                "line": {"color": "rgba(255,255,255,0.6)", "width": 3},
                "thickness": 0.8, "value": threshold * 100,
            },
        },
        title={"text": "احتمال الملاءمة", "font": {"size": 15, "color": "#CDD2DF"}},
    ))
    fig.update_layout(
        height=260,
        paper_bgcolor="rgba(0,0,0,0)",
        plot_bgcolor="rgba(0,0,0,0)",
        font_color="#CDD2DF",
        margin=dict(t=70, b=10, l=20, r=20),
    )
    return fig


def importance_chart(model, cols):
    imp = pd.Series(model.feature_importances_, index=cols).sort_values().tail(15)
    colors = ["#C41230" if v >= imp.quantile(0.75)
              else "#F5821F" if v >= imp.quantile(0.4)
              else "#1B3A6B" for v in imp.values]
    fig = go.Figure(go.Bar(
        x=imp.values, y=imp.index.tolist(), orientation="h",
        marker_color=colors,
        text=[f"{v:.1f}" for v in imp.values],
        textposition="outside",
        textfont=dict(color="#CDD2DF", size=11),
    ))
    fig.update_layout(
        height=500,
        paper_bgcolor="rgba(0,0,0,0)",
        plot_bgcolor="rgba(0,0,0,0)",
        font_color="#CDD2DF",
        margin=dict(t=20, b=20, l=240, r=70),
        xaxis=dict(title="الأهمية النسبية (%)",
                   showgrid=True, gridcolor="rgba(255,255,255,0.07)", color="#888"),
        yaxis=dict(tickfont=dict(size=12, color="#CDD2DF")),
    )
    return fig


# ─────────────────────────────────────────────────────────────────────────────
# Sidebar
# ─────────────────────────────────────────────────────────────────────────────
with st.sidebar:
    st.markdown("## ⚙️ بيانات المشروع")

    st.markdown("## 📍 الموقع الجغرافي")
    lat = st.number_input("خط العرض (Y)", value=18.2200, format="%.6f", step=0.0001)
    lng = st.number_input("خط الطول (X)", value=42.5100, format="%.6f", step=0.0001)
    if st.button("🛰️ جلب الارتفاع تلقائياً"):
        with st.spinner("جارٍ الجلب..."):
            elev = get_elevation(lat, lng)
        if elev is not None:
            st.session_state["elevation"] = float(elev)
            st.success(f"الارتفاع: {elev:.0f} م")
        else:
            st.warning("تعذّر الجلب — أدخل يدوياً")
    elevation = st.number_input("الارتفاع (م)", 0, 5000,
                                value=int(st.session_state.get("elevation", 2200)), step=10)
    slope = st.slider("الانحدار (درجة)", 0.0, 60.0, 8.0, 0.5)

    st.divider()
    st.markdown("## 🏗️ المنشأة")
    area          = st.number_input("مساحة المحل (م²)", 10, 30000, 80, step=5)
    has_brand     = st.radio("علامة تجارية؟", ["نعم ✅", "لا ❌"], horizontal=True)
    license_years = st.slider("مدة الرخصة (سنوات)", 1, 5, 1)

    st.divider()
    st.markdown("## 🛣️ شبكة الطرق")
    road_label    = st.selectbox("نوع الطريق الأقرب", list(ROAD_RANK.keys()), index=2)
    dist_road     = st.number_input("المسافة لأقرب شارع (م)", 0, 2000, 25, step=5)
    dist_arterial = st.number_input("المسافة للطريق الشرياني (م)", 0, 15000, 800, step=50)
    dist_tourist  = st.number_input("المسافة لأقرب معلم سياحي (م)", 0, 25000, 3000, step=100)

    st.divider()
    st.markdown("## 🏙️ السياق الحضري")
    uvi                = st.slider("مؤشر الحيوية الحضرية (UVI)", 0.0, 25.0, 5.0, 0.1)
    commercial_density = st.number_input("المنشآت التجارية في 500م", 0, 400, 30)
    buildings_count    = st.number_input("عدد المباني في 500م", 0, 600, 80, step=5)

    st.divider()
    st.markdown("## ⚔️ المنافسة")
    direct_competitors = st.number_input("المنافسون المباشرون في 500م", 0, 80, 5)
    dist_direct        = st.number_input("المسافة لأقرب منافس مباشر (م)", 0, 500, 150, step=10)
    competitor_age     = st.number_input("متوسط عمر المنافسين (يوم)", 0, 7300, 0, step=30)

    st.divider()
    st.markdown("## 📊 البيانات المكانية")
    neighborhood_rate = st.slider("معدل نجاح الحي", 0.0, 1.0, 0.65, 0.01)
    closure_rate      = st.slider("معدل إغلاق المنطقة", 0.0, 1.0, 0.30, 0.01)

    st.divider()
    st.markdown("## 🏢 القطاع")
    category_label      = st.selectbox("فئة النشاط الرئيسية", list(CATEGORY_TE.keys()))
    facility_type_label = st.selectbox("نوع المنشأة", list(FACILITY_TYPE_TE.keys()))


# ─────────────────────────────────────────────────────────────────────────────
# Main
# ─────────────────────────────────────────────────────────────────────────────
if not model_loaded:
    st.error("⚠️ ملف النموذج غير موجود: `catboost_model.pkl`")
    st.stop()

inputs = dict(
    lat=lat, lng=lng, elevation=elevation, slope=slope,
    dist_road=dist_road, dist_arterial=dist_arterial, dist_tourist=dist_tourist,
    road_rank=ROAD_RANK[road_label], uvi=uvi,
    commercial_density=commercial_density, buildings_count=buildings_count,
    direct_competitors=direct_competitors, dist_direct=dist_direct,
    competitor_age=competitor_age,
    neighborhood_rate=neighborhood_rate, closure_rate=closure_rate,
    area=area,
    has_brand=1 if "نعم" in has_brand else 0,
    license_years=license_years,
    facility_te=FACILITY_TYPE_TE[facility_type_label],
    category_te=CATEGORY_TE[category_label],
)

feat_vec  = build_feature_vector(inputs)
# نضيف أي عمود ناقص بقيمة 0
for col in FEATURE_COLS:
    if col not in feat_vec.columns:
        feat_vec[col] = 0.0
X_input   = feat_vec[FEATURE_COLS]
prob      = float(model.predict_proba(X_input)[0][1])
THRESHOLD = 0.65

tab_pred, tab_map, tab_imp, tab_about = st.tabs([
    "🎯  التنبؤ", "🗺️  الخريطة", "📊  أهمية المتغيرات", "ℹ️  عن المشروع"
])


# ── التنبؤ ────────────────────────────────────────────────────────────────────
with tab_pred:
    col_gauge, col_detail = st.columns([1, 1.45], gap="large")

    with col_gauge:
        st.plotly_chart(gauge_chart(prob, THRESHOLD), use_container_width=True)
        verdict = prob >= THRESHOLD
        if verdict:
            st.markdown("""
            <div class='verdict-box verdict-success'>
                ✅ الموقع <strong>ملائم</strong><br>
                <small style='font-weight:400;'>النموذج يوصي بهذا الموقع</small>
            </div>""", unsafe_allow_html=True)
        else:
            st.markdown("""
            <div class='verdict-box verdict-fail'>
                ❌ الموقع <strong>غير ملائم</strong><br>
                <small style='font-weight:400;'>النموذج لا يوصي بهذا الموقع</small>
            </div>""", unsafe_allow_html=True)
        st.caption(f"العتبة: {THRESHOLD:.0%}  ·  الاحتمال: {prob:.1%}")

    with col_detail:
        st.subheader("ملخص المدخلات")
        c1, c2, c3 = st.columns(3)
        c1.metric("الاحتمال",     f"{prob*100:.1f}%")
        c2.metric("الارتفاع",     f"{elevation:,} م")
        c3.metric("رتبة الطريق",  f"{ROAD_RANK[road_label]}/9")
        c4, c5, c6 = st.columns(3)
        c4.metric("المنافسون",    f"{direct_competitors}")
        c5.metric("مؤشر الحيوية",f"{uvi:.1f}")
        c6.metric("معدل الحي",    f"{neighborhood_rate*100:.0f}%")
        st.divider()
        st.markdown(f"""
**القطاع:** {category_label}  
**نوع المنشأة:** {facility_type_label}  
**المساحة:** {area:,} م²  ·  **مدة الرخصة:** {license_years} سنة  
**علامة تجارية:** {"نعم" if inputs["has_brand"] else "لا"}
        """)
        st.divider()
        st.caption("🔍 تحليل العوامل الحرجة:")
        if elevation > 2800:
            st.markdown('<span class="info-badge">⚠️ ارتفاع شاهق > 2800م</span>', unsafe_allow_html=True)
        if dist_arterial > 5000:
            st.markdown('<span class="info-badge">⚠️ بُعد عن الشريان > 5كم</span>', unsafe_allow_html=True)
        if direct_competitors > 10:
            st.markdown('<span class="info-badge">⚠️ منافسة مرتفعة جداً</span>', unsafe_allow_html=True)
        if closure_rate > 0.5:
            st.markdown('<span class="info-badge">⚠️ معدل إغلاق مرتفع في المنطقة</span>', unsafe_allow_html=True)
        if neighborhood_rate > 0.75:
            st.markdown('<span class="info-badge">✅ حي ذو معدل نجاح مرتفع</span>', unsafe_allow_html=True)
        if ROAD_RANK[road_label] >= 7:
            st.markdown('<span class="info-badge">✅ على طريق شرياني رئيسي</span>', unsafe_allow_html=True)
        if inputs["has_brand"]:
            st.markdown('<span class="info-badge">✅ علامة تجارية معروفة</span>', unsafe_allow_html=True)
        if buildings_count > 150:
            st.markdown('<span class="info-badge">✅ كثافة عمرانية مرتفعة</span>', unsafe_allow_html=True)


# ── الخريطة ───────────────────────────────────────────────────────────────────
with tab_map:
    verdict_color = "green" if prob >= THRESHOLD else "red"
    m = folium.Map(location=[lat, lng], zoom_start=15, tiles="CartoDB dark_matter")
    folium.Marker(
        [lat, lng],
        popup=folium.Popup(
            f"""<div dir='rtl' style='font-family:Arial;min-width:180px;'>
                <b style='color:#C41230;font-size:15px;'>جدوى</b><br>
                <b>احتمال النجاح: {prob*100:.1f}%</b><br>
                <span style='color:{"green" if verdict_color=="green" else "red"};'>
                {"✅ ملائم" if verdict_color=="green" else "❌ غير ملائم"}
                </span><br><hr style='margin:4px 0;'>
                الفئة: {category_label}<br>
                {lat:.5f} · {lng:.5f}
            </div>""", max_width=230,
        ),
        icon=folium.Icon(color=verdict_color, icon="building", prefix="fa"),
    ).add_to(m)
    folium.Circle([lat, lng], radius=500,
                  color="#F5821F", fill=True, fill_opacity=0.08, weight=1.5,
                  tooltip="نطاق التحليل المكاني (500م)").add_to(m)
    folium.TileLayer(
        tiles="https://mt1.google.com/vt/lyrs=y&x={x}&y={y}&z={z}",
        attr="Google Hybrid", name="صور جوية",
    ).add_to(m)
    folium.LayerControl(position="topright").add_to(m)
    map_data = st_folium(m, width="100%", height=520, returned_objects=["last_clicked"])
    if map_data and map_data.get("last_clicked"):
        c = map_data["last_clicked"]
        st.info(f"📌 نقرتِ على: خط العرض = {c['lat']:.5f}  |  خط الطول = {c['lng']:.5f}  \nحدّثي القيم في الشريط الجانبي.")


# ── أهمية المتغيرات ───────────────────────────────────────────────────────────
with tab_imp:
    col_imp, col_note = st.columns([2, 1])
    with col_imp:
        st.subheader("أهمية المتغيرات في نموذج CatBoost")
        st.plotly_chart(importance_chart(model, original_cols), use_container_width=True)
    with col_note:
        st.subheader("دليل القراءة")
        st.markdown("""
🔴 **عالي التأثير** — أكثر تأثيراً في قرار النموذج  
🟠 **متوسط التأثير** — مساهمة ملحوظة  
🔵 **منخفض التأثير** — أثر محدود

---
**مجموعات المتغيرات:**
- 📍 الموقع والتضاريس
- 🛣️ شبكة الطرق والوصولية
- 🏙️ السياق الحضري والمباني
- ⚔️ ديناميكيات المنافسة
- 📊 المؤشرات المكانية
- 🏗️ خصائص المنشأة
        """)


# ── عن المشروع ────────────────────────────────────────────────────────────────
with tab_about:
    cola, colb = st.columns(2)
    with cola:
        st.subheader("📖 عن جدوى")
        st.markdown("""
**جدوى** نموذج تعلم آلي قابل للتفسير يُقيّم ملاءمة المواقع التجارية
في البيئة الجبلية لمنطقة عسير (أبها وخميس مشيط).

| العنصر | القيمة |
|--------|--------|
| الخوارزمية | CatBoost |
| مقياس الهدف | F0.5 |
| عتبة التصنيف | 65% |
| عدد المتغيرات | 21 متغير |
| التحقق المتقاطع | StratifiedGroupKFold مكاني |
| التفسيرية | GeoShapley |

**مصادر البيانات:**  
رخص بلدية عسير · تقييمات Google · Overture Maps ·
نماذج DEM · نقاط اهتمام POI · بيانات المباني
        """)
    with colb:
        st.subheader("📚 المراجع")
        st.markdown("""
- Starakiewicz & Wojcik (2025)
- Khan et al. (2025)
- Kapoor & Narayanan (2023)
- Anselin (1995) — Moran's I
- Li (2024) — GeoShapley
- Rey, Arribas-Bel & Wolf (2023)

**المرجع التشريعي:**  
اللائحة التنفيذية لنظام إجراءات التراخيص البلدية،
القرار 1/4500665986

---
⚠️ قيم Target Encoding تقديرية.
حدّثيها من `agg_full['te']` في الكود الأصلي.
        """)


# Footer
st.markdown("---")
st.markdown("""
<div style='text-align:center;padding:0.5rem;'>
    <span style='color:rgba(255,255,255,0.2);font-size:13px;letter-spacing:2px;'>
        ◆ &nbsp; جدوى من عسير &nbsp;·&nbsp; رسالة ماجستير &nbsp;·&nbsp; 2026 &nbsp; ◆
    </span>
</div>
""", unsafe_allow_html=True)
