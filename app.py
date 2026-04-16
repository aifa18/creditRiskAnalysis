import streamlit as st
import numpy as np
import skfuzzy as fuzz
from skfuzzy import control as ctrl
import joblib
import pandas as pd
import plotly.graph_objects as go
import plotly.express as px
from datetime import datetime
import random

# =========================
# PAGE CONFIG
# =========================
st.set_page_config(
    page_title="CreditGuard | Bank Credit Analysis",
    page_icon="🏦",
    layout="wide",
    initial_sidebar_state="expanded"
)

# =========================
# INISIALISASI DATABASE SEMENTARA (SESSION STATE)
# =========================
if "history_data" not in st.session_state:
    st.session_state.history_data = []

# =========================
# GLOBAL CSS
# =========================
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Plus+Jakarta+Sans:wght@300;400;500;600;700;800&family=Space+Mono:wght@400;700&display=swap');

html, body, [class*="css"] {
    font-family: 'Plus Jakarta Sans', sans-serif;
}

/* Hide default Streamlit chrome */
#MainMenu {visibility: hidden;}
footer {visibility: hidden;}
.stDeployButton {display: none;}

/* Background */
.main .block-container {
    background: #F0F4F8;
    padding-top: 1.5rem;
    max-width: 1400px;
}

/* ---- Sidebar ---- */
[data-testid="stSidebar"] {
    background: linear-gradient(180deg, #0A1628 0%, #0D2345 100%);
    border-right: 1px solid rgba(255,255,255,0.06);
}
[data-testid="stSidebar"] * {
    color: #C8D6E5 !important;
}
[data-testid="stSidebar"] .stRadio label {
    color: #C8D6E5 !important;
    font-size: 0.9rem;
}

/* Sidebar logo area */
.sidebar-logo {
    text-align: center;
    padding: 20px 10px 28px;
    border-bottom: 1px solid rgba(255,255,255,0.08);
    margin-bottom: 20px;
}
.sidebar-logo h1 {
    font-family: 'Space Mono', monospace;
    font-size: 1.4rem;
    color: #4EAEFF !important;
    margin: 8px 0 2px;
    letter-spacing: -0.5px;
}
.sidebar-logo p {
    font-size: 0.7rem;
    color: rgba(200,214,229,0.5) !important;
    text-transform: uppercase;
    letter-spacing: 2px;
}

/* Sidebar nav section */
.nav-section {
    padding: 8px 12px 4px;
    font-size: 0.65rem;
    text-transform: uppercase;
    letter-spacing: 2px;
    color: rgba(200,214,229,0.4) !important;
}

/* ---- Cards ---- */
.metric-card {
    background: white;
    border-radius: 16px;
    padding: 22px 24px;
    box-shadow: 0 1px 3px rgba(0,0,0,0.06), 0 4px 16px rgba(0,0,0,0.04);
    border: 1px solid rgba(0,0,0,0.04);
    transition: transform 0.2s ease, box-shadow 0.2s ease;
}
.metric-card:hover {
    transform: translateY(-2px);
    box-shadow: 0 4px 20px rgba(0,0,0,0.10);
}

.metric-label {
    font-size: 0.72rem;
    text-transform: uppercase;
    letter-spacing: 1.5px;
    color: #8899AA;
    margin-bottom: 6px;
    font-weight: 600;
}
.metric-value {
    font-size: 2rem;
    font-weight: 800;
    color: #0A1628;
    line-height: 1;
    margin-bottom: 4px;
}
.metric-sub {
    font-size: 0.78rem;
    color: #8899AA;
}

/* ---- Page header ---- */
.page-header {
    background: linear-gradient(135deg, #0A1628 0%, #0D3060 100%);
    border-radius: 20px;
    padding: 32px 36px;
    margin-bottom: 24px;
    position: relative;
    overflow: hidden;
}
.page-header::before {
    content: '';
    position: absolute;
    top: -60px; right: -60px;
    width: 220px; height: 220px;
    background: radial-gradient(circle, rgba(78,174,255,0.15) 0%, transparent 70%);
    border-radius: 50%;
}
.page-header::after {
    content: '';
    position: absolute;
    bottom: -40px; left: 30%;
    width: 160px; height: 160px;
    background: radial-gradient(circle, rgba(100,220,180,0.10) 0%, transparent 70%);
    border-radius: 50%;
}
.page-header h1 {
    color: white;
    font-size: 1.9rem;
    font-weight: 800;
    margin: 0 0 6px;
}
.page-header p {
    color: rgba(200,214,229,0.7);
    font-size: 0.9rem;
    margin: 0;
}

/* ---- Section titles ---- */
.section-title {
    font-size: 1rem;
    font-weight: 700;
    color: #0A1628;
    margin-bottom: 16px;
    display: flex;
    align-items: center;
    gap: 8px;
}
.section-title::after {
    content: '';
    flex: 1;
    height: 1px;
    background: rgba(0,0,0,0.07);
    margin-left: 8px;
}

/* ---- Result verdict card ---- */
.verdict-approved {
    background: linear-gradient(135deg, #0D7E5B 0%, #12A678 100%);
    border-radius: 16px;
    padding: 28px 32px;
    color: white;
    text-align: center;
}
.verdict-rejected {
    background: linear-gradient(135deg, #B91C1C 0%, #DC2626 100%);
    border-radius: 16px;
    padding: 28px 32px;
    color: white;
    text-align: center;
}
.verdict-review {
    background: linear-gradient(135deg, #92400E 0%, #D97706 100%);
    border-radius: 16px;
    padding: 28px 32px;
    color: white;
    text-align: center;
}
.verdict-title {
    font-size: 1rem;
    opacity: 0.85;
    margin-bottom: 6px;
    text-transform: uppercase;
    letter-spacing: 1.5px;
    font-weight: 600;
}
.verdict-status {
    font-size: 2rem;
    font-weight: 800;
    margin-bottom: 6px;
}
.verdict-sub {
    font-size: 0.82rem;
    opacity: 0.75;
}

/* ---- Method result card ---- */
.method-card {
    background: white;
    border-radius: 14px;
    padding: 20px 22px;
    box-shadow: 0 1px 3px rgba(0,0,0,0.05);
    border: 1px solid rgba(0,0,0,0.05);
    height: 100%;
}
.method-badge {
    display: inline-block;
    font-size: 0.65rem;
    font-weight: 700;
    text-transform: uppercase;
    letter-spacing: 1.5px;
    padding: 4px 10px;
    border-radius: 20px;
    margin-bottom: 12px;
}
.badge-fuzzy { background: #EEF2FF; color: #4338CA; }
.badge-ga    { background: #ECFDF5; color: #059669; }
.badge-ann   { background: #FFF7ED; color: #C2410C; }

.method-name {
    font-size: 1rem;
    font-weight: 700;
    color: #0A1628;
    margin-bottom: 12px;
}
.method-score {
    font-family: 'Space Mono', monospace;
    font-size: 2.2rem;
    font-weight: 700;
    margin: 8px 0;
    line-height: 1;
}
.score-approved { color: #059669; }
.score-rejected { color: #DC2626; }
.score-review   { color: #D97706; }

.method-label {
    font-size: 0.78rem;
    font-weight: 600;
    padding: 4px 12px;
    border-radius: 20px;
    display: inline-block;
    margin: 6px 0;
}
.label-approved { background: #D1FAE5; color: #065F46; }
.label-rejected { background: #FEE2E2; color: #991B1B; }
.label-review   { background: #FEF3C7; color: #92400E; }

.method-note {
    font-size: 0.75rem;
    color: #8899AA;
    margin-top: 10px;
    line-height: 1.5;
    border-top: 1px solid #F0F4F8;
    padding-top: 10px;
}

/* ---- Form container ---- */
.form-container {
    background: white;
    border-radius: 16px;
    padding: 28px 30px;
    box-shadow: 0 1px 3px rgba(0,0,0,0.05);
    border: 1px solid rgba(0,0,0,0.05);
}

/* ---- Applicant info badge ---- */
.applicant-badge {
    background: #F0F4F8;
    border-radius: 12px;
    padding: 14px 18px;
    display: flex;
    align-items: center;
    gap: 12px;
    margin-bottom: 20px;
}
.applicant-avatar {
    width: 42px; height: 42px;
    background: linear-gradient(135deg, #4EAEFF, #0D3060);
    border-radius: 50%;
    display: flex;
    align-items: center;
    justify-content: center;
    font-size: 1.2rem;
    color: white;
    font-weight: 700;
    flex-shrink: 0;
}
.applicant-name {
    font-weight: 700;
    color: #0A1628;
    font-size: 1rem;
}
.applicant-meta {
    font-size: 0.78rem;
    color: #8899AA;
}

/* ---- Risk indicator ---- */
.risk-bar-container {
    background: #F0F4F8;
    border-radius: 8px;
    height: 8px;
    overflow: hidden;
    margin: 6px 0;
}
.risk-bar {
    height: 100%;
    border-radius: 8px;
    transition: width 0.5s ease;
}

/* Streamlit widget overrides */
.stNumberInput input, .stTextInput input, .stSelectbox select {
    border-radius: 10px !important;
    border: 1.5px solid #DDE3EE !important;
    font-family: 'Plus Jakarta Sans', sans-serif !important;
}
.stSlider .thumb { background: #4EAEFF !important; }
div[data-testid="stForm"] {
    border: none !important;
    padding: 0 !important;
}

/* Tabs */
.stTabs [data-baseweb="tab-list"] {
    background: #F0F4F8;
    border-radius: 12px;
    padding: 4px;
    gap: 4px;
}
.stTabs [data-baseweb="tab"] {
    border-radius: 9px;
    font-weight: 600;
    font-size: 0.85rem;
}
.stTabs [aria-selected="true"] {
    background: white !important;
    color: #0A1628 !important;
    box-shadow: 0 1px 4px rgba(0,0,0,0.10) !important;
}

/* Divider */
hr { border-color: rgba(0,0,0,0.06) !important; }

/* Home Steps */
.step-box {
    background: white;
    border-radius: 12px;
    padding: 20px;
    border: 1px solid rgba(0,0,0,0.05);
    height: 100%;
    box-shadow: 0 1px 3px rgba(0,0,0,0.03);
}
.step-number {
    width: 32px;
    height: 32px;
    background: linear-gradient(135deg, #4EAEFF, #0D3060);
    color: white;
    border-radius: 50%;
    display: flex;
    align-items: center;
    justify-content: center;
    font-weight: bold;
    margin-bottom: 12px;
}
</style>
""", unsafe_allow_html=True)


# =========================
# PARAMETER GA HASIL OPTIMASI
# =========================
best_ga = [
    30932, 34758, 51285, 73989,
    0.18, 0.271, 0.351, 0.444,
    2, 6, 6, 7
]

# =========================
# FUZZY MANUAL
# =========================
def fuzzy_manual(pendapatan, rasio_hutang, lama_kerja):
    income = ctrl.Antecedent(np.arange(0, 200001, 1000), 'pendapatan')
    debt_ratio = ctrl.Antecedent(np.arange(0, 1.01, 0.01), 'rasio_hutang')
    emp_length = ctrl.Antecedent(np.arange(0, 51, 1), 'lama_kerja')
    kelayakan = ctrl.Consequent(np.arange(0, 101, 1), 'kelayakan')

    income['rendah'] = fuzz.trapmf(income.universe, [0, 0, 30000, 40000])
    income['sedang'] = fuzz.trapmf(income.universe, [30000, 40000, 75000, 85000])
    income['tinggi'] = fuzz.trapmf(income.universe, [75000, 85000, 200000, 200000])

    debt_ratio['aman'] = fuzz.trapmf(debt_ratio.universe, [0, 0, 0.15, 0.20])
    debt_ratio['waspada'] = fuzz.trapmf(debt_ratio.universe, [0.15, 0.20, 0.25, 0.30])
    debt_ratio['bahaya'] = fuzz.trapmf(debt_ratio.universe, [0.25, 0.30, 1.0, 1.0])

    emp_length['baru'] = fuzz.trapmf(emp_length.universe, [0, 0, 2, 3])
    emp_length['menengah'] = fuzz.trapmf(emp_length.universe, [2, 3, 7, 8])
    emp_length['lama'] = fuzz.trapmf(emp_length.universe, [7, 8, 50, 50])

    kelayakan['ditolak'] = fuzz.trapmf(kelayakan.universe, [0, 0, 40, 50])
    kelayakan['dipertimbangkan'] = fuzz.trapmf(kelayakan.universe, [40, 50, 65, 75])
    kelayakan['diterima'] = fuzz.trapmf(kelayakan.universe, [65, 75, 100, 100])

    rules = [
        ctrl.Rule(income['tinggi'] & debt_ratio['aman'] & emp_length['lama'], kelayakan['diterima']),
        ctrl.Rule(income['tinggi'] & debt_ratio['aman'] & emp_length['baru'], kelayakan['diterima']),
        ctrl.Rule(income['sedang'] & debt_ratio['aman'] & emp_length['lama'], kelayakan['diterima']),
        ctrl.Rule(income['tinggi'] & debt_ratio['waspada'] & emp_length['lama'], kelayakan['diterima']),
        ctrl.Rule(income['rendah'] & debt_ratio['bahaya'] & emp_length['baru'], kelayakan['ditolak']),
        ctrl.Rule(income['sedang'] & debt_ratio['bahaya'] & emp_length['baru'], kelayakan['ditolak']),
        ctrl.Rule(income['rendah'] & debt_ratio['waspada'] & emp_length['menengah'], kelayakan['ditolak']),
        ctrl.Rule(income['rendah'] & debt_ratio['bahaya'] & emp_length['lama'], kelayakan['ditolak']),
        ctrl.Rule(income['sedang'] & debt_ratio['aman'] & emp_length['baru'], kelayakan['dipertimbangkan']),
        ctrl.Rule(income['tinggi'] & debt_ratio['bahaya'] & emp_length['menengah'], kelayakan['dipertimbangkan']),
        ctrl.Rule(income['rendah'] & debt_ratio['aman'] & emp_length['lama'], kelayakan['dipertimbangkan']),
        ctrl.Rule(income['sedang'] & debt_ratio['waspada'] & emp_length['menengah'], kelayakan['dipertimbangkan'])
    ]
    sim = ctrl.ControlSystemSimulation(ctrl.ControlSystem(rules))
    sim.input['pendapatan'] = pendapatan
    sim.input['rasio_hutang'] = rasio_hutang
    sim.input['lama_kerja'] = lama_kerja
    try:
        sim.compute()
        return sim.output['kelayakan']
    except:
        return 0


# =========================
# FUZZY + GA
# =========================
def fuzzy_ga(pendapatan, rasio_hutang, lama_kerja, kromosom):
    x_inc = np.sort(kromosom[0:4])
    x_deb = np.sort(kromosom[4:8])
    x_emp = np.sort(kromosom[8:12])

    income = ctrl.Antecedent(np.arange(0, 200001, 1000), 'pendapatan')
    debt_ratio = ctrl.Antecedent(np.arange(0, 1.01, 0.01), 'rasio_hutang')
    emp_length = ctrl.Antecedent(np.arange(0, 51, 1), 'lama_kerja')
    kelayakan = ctrl.Consequent(np.arange(0, 101, 1), 'kelayakan')

    income['rendah'] = fuzz.trapmf(income.universe, [0, 0, x_inc[0], x_inc[1]])
    income['sedang'] = fuzz.trapmf(income.universe, [x_inc[0], x_inc[1], x_inc[2], x_inc[3]])
    income['tinggi'] = fuzz.trapmf(income.universe, [x_inc[2], x_inc[3], 200000, 200000])

    debt_ratio['aman'] = fuzz.trapmf(debt_ratio.universe, [0, 0, x_deb[0], x_deb[1]])
    debt_ratio['waspada'] = fuzz.trapmf(debt_ratio.universe, [x_deb[0], x_deb[1], x_deb[2], x_deb[3]])
    debt_ratio['bahaya'] = fuzz.trapmf(debt_ratio.universe, [x_deb[2], x_deb[3], 1.0, 1.0])

    emp_length['baru'] = fuzz.trapmf(emp_length.universe, [0, 0, x_emp[0], x_emp[1]])
    emp_length['menengah'] = fuzz.trapmf(emp_length.universe, [x_emp[0], x_emp[1], x_emp[2], x_emp[3]])
    emp_length['lama'] = fuzz.trapmf(emp_length.universe, [x_emp[2], x_emp[3], 50, 50])

    kelayakan['ditolak'] = fuzz.trapmf(kelayakan.universe, [0, 0, 40, 50])
    kelayakan['dipertimbangkan'] = fuzz.trapmf(kelayakan.universe, [40, 50, 65, 75])
    kelayakan['diterima'] = fuzz.trapmf(kelayakan.universe, [65, 75, 100, 100])

    rules = [
        ctrl.Rule(income['tinggi'] & debt_ratio['aman'] & emp_length['lama'], kelayakan['diterima']),
        ctrl.Rule(income['tinggi'] & debt_ratio['aman'] & emp_length['baru'], kelayakan['diterima']),
        ctrl.Rule(income['sedang'] & debt_ratio['aman'] & emp_length['lama'], kelayakan['diterima']),
        ctrl.Rule(income['tinggi'] & debt_ratio['waspada'] & emp_length['lama'], kelayakan['diterima']),
        ctrl.Rule(income['rendah'] & debt_ratio['bahaya'] & emp_length['baru'], kelayakan['ditolak']),
        ctrl.Rule(income['sedang'] & debt_ratio['bahaya'] & emp_length['baru'], kelayakan['ditolak']),
        ctrl.Rule(income['rendah'] & debt_ratio['waspada'] & emp_length['menengah'], kelayakan['ditolak']),
        ctrl.Rule(income['rendah'] & debt_ratio['bahaya'] & emp_length['lama'], kelayakan['ditolak']),
        ctrl.Rule(income['sedang'] & debt_ratio['aman'] & emp_length['baru'], kelayakan['dipertimbangkan']),
        ctrl.Rule(income['tinggi'] & debt_ratio['bahaya'] & emp_length['menengah'], kelayakan['dipertimbangkan']),
        ctrl.Rule(income['rendah'] & debt_ratio['aman'] & emp_length['lama'], kelayakan['dipertimbangkan']),
        ctrl.Rule(income['sedang'] & debt_ratio['waspada'] & emp_length['menengah'], kelayakan['dipertimbangkan'])
    ]

    sim = ctrl.ControlSystemSimulation(ctrl.ControlSystem(rules))
    sim.input['pendapatan'] = pendapatan
    sim.input['rasio_hutang'] = rasio_hutang
    sim.input['lama_kerja'] = lama_kerja
    try:
        sim.compute()
        return sim.output['kelayakan']
    except:
        return 0


# =========================
# LOAD MODEL ANN
# =========================
@st.cache_resource
def load_models():
    model = joblib.load("ann_model.pkl")
    scaler = joblib.load("scaler.pkl")
    return model, scaler

try:
    ann_model, scaler = load_models()
    ANN_AVAILABLE = True
except:
    ANN_AVAILABLE = False

def prediksi_ann(pendapatan, rasio_hutang, lama_kerja):
    if not ANN_AVAILABLE:
        return None
    data = np.array([[pendapatan, rasio_hutang, lama_kerja]])
    data_scaled = scaler.transform(data)
    return ann_model.predict(data_scaled)[0]


# =========================
# HELPER: interpret score & alasan
# =========================
def interpret_fuzzy(score):
    if score >= 65:
        return "APPROVED", "approved"
    elif score >= 40:
        return "UNDER REVIEW", "review"
    else:
        return "REJECTED", "rejected"

def interpret_ann(val):
    if val == 0:
        return "APPROVED", "approved"
    else:
        return "REJECTED", "rejected"

def penjelasan_fuzzy(score, status, pendapatan, rasio_hutang, lama_kerja):
    if status == "APPROVED":
        return (
            f"Berdasarkan evaluasi berbasis rule, profil nasabah menunjukkan kondisi yang cukup solid. "
            f"Pendapatan dan stabilitas kerja mendukung kemampuan pembayaran, serta rasio kewajiban masih dalam batas aman. "
            f"Skor {score:.1f} mencerminkan kelayakan kredit yang baik untuk diproses lebih lanjut."
        )
    elif status == "UNDER REVIEW":
        return (
            f"Hasil analisis menunjukkan profil nasabah berada pada area pertimbangan. "
            f"Terdapat kombinasi faktor yang belum sepenuhnya kuat, seperti keseimbangan antara pendapatan dan rasio kewajiban. "
            f"Dengan skor {score:.1f}, disarankan dilakukan peninjauan tambahan sebelum keputusan akhir."
        )
    else:
        return (
            f"Berdasarkan aturan evaluasi, profil nasabah mengindikasikan tingkat risiko yang relatif tinggi. "
            f"Faktor seperti pendapatan, rasio hutang, atau stabilitas kerja belum cukup mendukung kemampuan pembayaran. "
            f"Skor {score:.1f} menunjukkan pengajuan kredit belum layak untuk disetujui."
        )

def penjelasan_ga(score, status, pendapatan, rasio_hutang, lama_kerja):
    if status == "APPROVED":
        return (
            f"Dengan parameter yang telah dioptimasi, hasil evaluasi menunjukkan profil nasabah berada pada kondisi yang menguntungkan. "
            f"Penyesuaian batas penilaian menghasilkan skor {score:.1f}, yang mengindikasikan kemampuan finansial cukup stabil "
            f"dan risiko kredit relatif rendah."
        )
    elif status == "UNDER REVIEW":
        return (
            f"Hasil optimasi menunjukkan profil nasabah masih berada di area abu-abu. "
            f"Beberapa indikator keuangan belum sepenuhnya konsisten untuk mendukung keputusan langsung. "
            f"Skor {score:.1f} menunjukkan perlunya validasi tambahan sebelum persetujuan."
        )
    else:
        return (
            f"Berdasarkan hasil evaluasi yang telah dioptimasi, profil nasabah menunjukkan kecenderungan risiko yang lebih tinggi. "
            f"Nilai {score:.1f} mengindikasikan bahwa struktur keuangan saat ini belum cukup kuat "
            f"untuk memenuhi kriteria kelayakan kredit."
        )
    
def penjelasan_ann(status):
    if status == "APPROVED":
        return (
            "Model pembelajaran dari data historis menunjukkan pola nasabah serupa memiliki performa pembayaran yang baik. "
            "Hal ini mengindikasikan risiko kredit relatif rendah berdasarkan pengalaman data sebelumnya."
        )
    else:
        return (
            "Berdasarkan pola dari data historis, profil nasabah memiliki kemiripan dengan kasus yang berisiko. "
            "Model mengindikasikan potensi ketidaklancaran pembayaran sehingga pengajuan tidak direkomendasikan."
        )

def risk_color(status):
    return {"approved": "#059669", "rejected": "#DC2626", "review": "#D97706"}.get(status, "#8899AA")

def score_color_class(status):
    return {"approved": "score-approved", "rejected": "score-rejected", "review": "score-review"}.get(status, "")

def label_class(status):
    return {"approved": "label-approved", "rejected": "label-rejected", "review": "label-review"}.get(status, "")

def verdict_class(status):
    return {"approved": "verdict-approved", "rejected": "verdict-rejected", "review": "verdict-review"}.get(status, "verdict-review")

def overall_verdict(s1, s2, ann_val):
    statuses = [s1, s2]
    if ann_val is not None:
        ann_s, _ = interpret_ann(ann_val)
        statuses.append(ann_s)
    approved = statuses.count("APPROVED")
    rejected = statuses.count("REJECTED")
    if approved > rejected:
        return "APPROVED", "approved", f"{approved}/{len(statuses)} methods recommend approval"
    elif rejected > approved:
        return "REJECTED", "rejected", f"{rejected}/{len(statuses)} methods recommend rejection"
    else:
        return "UNDER REVIEW", "review", "Methods disagree — manual review recommended"

def risk_profile(pendapatan, rasio_hutang, lama_kerja):
    score = 0
    if pendapatan > 75000: score += 35
    elif pendapatan > 40000: score += 20
    else: score += 5
    if rasio_hutang < 0.20: score += 35
    elif rasio_hutang < 0.30: score += 18
    else: score += 3
    if lama_kerja > 7: score += 30
    elif lama_kerja > 3: score += 18
    else: score += 5
    if score >= 70: return "Low Risk", score, "#059669"
    elif score >= 40: return "Medium Risk", score, "#D97706"
    else: return "High Risk", score, "#DC2626"

def format_currency(val):
    return f"${val:,.0f}"

def format_pct(val):
    return f"{val*100:.1f}%"


# =========================
# SIDEBAR
# =========================
with st.sidebar:
    st.markdown("""
    <div class="sidebar-logo">
        <div style="font-size:2.2rem">🏦</div>
        <h1>CreditGuard</h1>
        <p>Credit Risk Analysis</p>
    </div>
    """, unsafe_allow_html=True)

    st.markdown('<div class="nav-section">Navigasi Utama</div>', unsafe_allow_html=True)
    menu = st.radio(
        "",
        ["🏠  Home & About", "🔍  Applicant Analysis", "📊  Dashboard & History"],
        label_visibility="collapsed"
    )

    st.markdown("---")
    st.markdown("""
    <div style="padding: 12px; background: rgba(78,174,255,0.08); border-radius: 10px; border: 1px solid rgba(78,174,255,0.15);">
        <div style="font-size:0.7rem; color: rgba(200,214,229,0.6); text-transform:uppercase; letter-spacing:1.5px; margin-bottom:6px;">System Status</div>
        <div style="display:flex; align-items:center; gap:6px; margin-bottom:4px;">
            <div style="width:7px;height:7px;border-radius:50%;background:#34D399;"></div>
            <span style="font-size:0.8rem;">Fuzzy Manual — Active</span>
        </div>
        <div style="display:flex; align-items:center; gap:6px; margin-bottom:4px;">
            <div style="width:7px;height:7px;border-radius:50%;background:#34D399;"></div>
            <span style="font-size:0.8rem;">Fuzzy + GA — Active</span>
        </div>
        <div style="display:flex; align-items:center; gap:6px;">
            <div style="width:7px;height:7px;border-radius:50%;background:{}; "></div>
            <span style="font-size:0.8rem;">ANN Model — {}</span>
        </div>
    </div>
    """.format("#34D399" if ANN_AVAILABLE else "#F87171", "Active" if ANN_AVAILABLE else "No model file"), unsafe_allow_html=True)

    st.markdown("---")
    st.markdown("""
    <div style="font-size:0.72rem; color:rgba(200,214,229,0.4); text-align:center; line-height:1.6;">
        Soft Computing UTS 2025/2026<br>
        Teknik Informatika — UNPAD
    </div>
    """, unsafe_allow_html=True)

# ============================================================
# PAGE: HOME & ABOUT 
# ============================================================
if "🏠" in menu:
    st.markdown("""
    <div class="page-header">
        <h1>🏠 Selamat Datang di CreditGuard</h1>
        <p>Sistem Cerdas Evaluasi Kelayakan Kartu Kredit berbasis AI (Artificial Intelligence)</p>
    </div>
    """, unsafe_allow_html=True)

    # --- Bagian 1: Tentang Sistem ---
    st.markdown('<div class="section-title">🧩 Tentang Sistem</div>', unsafe_allow_html=True)
    st.markdown("""
    **CreditGuard** adalah sistem analisis kelayakan kredit yang dirancang untuk membantu institusi keuangan dalam mengevaluasi risiko calon nasabah secara lebih objektif dan terstruktur.

    Sistem ini menggabungkan beberapa pendekatan kecerdasan buatan untuk menghasilkan keputusan yang lebih akurat dan dapat dipertanggungjawabkan.

    | Metode Analisis | Pendekatan AI | Deskripsi Singkat |
    |--------|------|-------------|
    | **Fuzzy Manual (FIS)** | *Rule-based* | Menggunakan 12 aturan dasar buatan manusia dan fungsi keanggotaan trapesium statis. |
    | **Fuzzy + GA** | *Evolutionary* | Menggunakan Algoritma Genetika untuk menggeser & mengoptimasi titik kurva batas secara otomatis agar lebih presisi. |
    | **Neural Network (ANN)** | *Data-driven* | Menggunakan Machine Learning (Multilayer Perceptron) yang dilatih menggunakan riwayat data asli ribuan nasabah. |

    **Fitur Input Utama (Variabel Keuangan Nasabah):**
    - Pendapatan Tahunan (USD)
    - Rasio Hutang terhadap Pendapatan
    - Lama Masa Kerja (tahun)
    """)
    
    st.write("---")

    # --- Bagian 2: Cara Penggunaan ---
    st.markdown('<div class="section-title">💡 Cara Penggunaan Aplikasi</div>', unsafe_allow_html=True)
    st.write("")

    col1, col2, col3 = st.columns(3)
    with col1:
        st.markdown("""
        <div class="step-box">
            <div class="step-number">1</div>
            <h4>Input Data Nasabah</h4>
            <p style="font-size: 0.9rem; color: #8899AA;">Masuk ke menu <b>🔍 Applicant Analysis</b> di sidebar. Isi profil keuangan nasabah yang ingin dievaluasi.</p>
        </div>
        """, unsafe_allow_html=True)
    
    with col2:
        st.markdown("""
        <div class="step-box">
            <div class="step-number">2</div>
            <h4>Eksekusi Analisis</h4>
            <p style="font-size: 0.9rem; color: #8899AA;">Klik tombol <b>⚡ Run Credit Analysis</b>. Ketiga "otak" sistem (Fuzzy, GA, ANN) akan langsung bekerja memproses data tersebut.</p>
        </div>
        """, unsafe_allow_html=True)

    with col3:
        st.markdown("""
        <div class="step-box">
            <div class="step-number">3</div>
            <h4>Bandingkan Hasil</h4>
            <p style="font-size: 0.9rem; color: #8899AA;">Gulir ke bawah untuk melihat perbandingan prediksi. Cek juga menu <b>📊 Dashboard & History</b> untuk pantauan riwayat aplikasi.</p>
        </div>
        """, unsafe_allow_html=True)
    
    st.write("")
    st.info("👈 **Sudah paham alurnya?** Silakan pilih menu **Applicant Analysis** di panel kiri untuk mulai melakukan simulasi kelayakan kredit!")

# ============================================================
# PAGE: APPLICANT ANALYSIS
# ============================================================
elif "🔍" in menu:

    st.markdown("""
    <div class="page-header">
        <h1>🔍 Applicant Credit Analysis</h1>
        <p>Masukkan data nasabah di bawah ini untuk melihat evaluasi kelayakan dari ketiga metode AI.</p>
    </div>
    """, unsafe_allow_html=True)

# ---- INPUT FORM ----
    with st.container():
        st.markdown('<div class="section-title">👤 Informasi Pribadi Nasabah</div>', unsafe_allow_html=True)

        col1, col2, col3 = st.columns(3)
        with col1:
            nama = st.text_input("Nama Lengkap", placeholder="Contoh: Budi Santoso")
        with col2:
            umur = st.number_input("Usia (Tahun)", min_value=18, max_value=75, value=30)
        with col3:
            pekerjaan = st.selectbox("Jenis Pekerjaan", [
                "Sektor Swasta", "PNS / Pegawai Pemerintahan",
                "Wiraswasta / Pengusaha", "Freelancer", "Lainnya"
            ])

        st.markdown("---")
        st.markdown('<div class="section-title">📋 Profil Keuangan</div>', unsafe_allow_html=True)

        colA, colB, colC = st.columns(3)
        with colA:
            st.markdown("**Pendapatan Tahunan (USD)**")
            pendapatan = st.number_input(
                "Annual Income", min_value=0, max_value=200000,
                value=55000, step=1000, label_visibility="collapsed"
            )
            st.caption(f"Estimasi: {format_currency(pendapatan/12)} / bulan")

        with colB:
            st.markdown("**Rasio Hutang (Debt-to-Income)**")
            rasio_hutang = st.slider(
                "Debt Ratio", min_value=0.0, max_value=1.0,
                value=0.22, step=0.01, label_visibility="collapsed"
            )
            risk_lbl = "🟢 Aman" if rasio_hutang < 0.20 else ("🟡 Waspada" if rasio_hutang < 0.30 else "🔴 Bahaya")
            st.caption(f"{format_pct(rasio_hutang)} — {risk_lbl}")

        with colC:
            st.markdown("**Lama Masa Kerja (Tahun)**")
            lama_kerja = st.number_input(
                "Years", min_value=0, max_value=50,
                value=5, label_visibility="collapsed"
            )
            exp_lbl = "🔴 Karyawan Baru" if lama_kerja < 2 else ("🟡 Menengah" if lama_kerja < 7 else "🟢 Berpengalaman")
            st.caption(f"{lama_kerja} tahun — {exp_lbl}")

        st.markdown("</div>", unsafe_allow_html=True)

    st.write("")

    # ---- ANALYZE BUTTON ----
    btn_col = st.columns([1, 2, 1])
    with btn_col[1]:
        analyze = st.button("⚡ Run Credit Analysis", use_container_width=True, type="primary")

    st.write("")

    # ---- RESULTS ----
    if analyze:
        if not nama.strip():
            st.warning("Mohon isi nama nasabah terlebih dahulu sebelum menjalankan analisis.")
        else:
            with st.spinner("Sistem sedang memproses data menggunakan tiga kecerdasan buatan..."):
                hasil_fuzzy = fuzzy_manual(pendapatan, rasio_hutang, lama_kerja)
                hasil_ga = fuzzy_ga(pendapatan, rasio_hutang, lama_kerja, best_ga)
                hasil_ann = prediksi_ann(pendapatan, rasio_hutang, lama_kerja)

            fz_status, fz_s = interpret_fuzzy(hasil_fuzzy)
            ga_status, ga_s = interpret_fuzzy(hasil_ga)
            ann_label = None
            ann_s = None
            if hasil_ann is not None:
                ann_label, ann_s = interpret_ann(hasil_ann)

            ov_status, ov_s, ov_reason = overall_verdict(fz_status, ga_status, hasil_ann)
            risk_label, risk_score, risk_col = risk_profile(pendapatan, rasio_hutang, lama_kerja)
            
            # Memanggil fungsi penjelasan_kelayakan
            alasan_fuzzy = penjelasan_fuzzy(hasil_fuzzy, fz_status, pendapatan, rasio_hutang, lama_kerja)
            alasan_ga = penjelasan_ga(hasil_ga, ga_status, pendapatan, rasio_hutang, lama_kerja)

            if hasil_ann is not None:
                alasan_ann = penjelasan_ann(ann_label)

            record_id = f"APP-{1000 + len(st.session_state.history_data) + 1}"
            st.session_state.history_data.append({
                "ID": record_id,
                "Name": nama,
                "Income": pendapatan,
                "Debt Ratio": rasio_hutang,
                "Emp. Years": lama_kerja,
                "Fuzzy Score": round(hasil_fuzzy, 1),
                "Status": ov_status,
                "Date": datetime.now().strftime("%Y-%m-%d %H:%M")
            })

            # Applicant badge
            initials = "".join([w[0].upper() for w in nama.strip().split()[:2]])
            st.markdown(f"""
            <div class="applicant-badge">
                <div class="applicant-avatar">{initials}</div>
                <div>
                    <div class="applicant-name">{nama}</div>
                    <div class="applicant-meta">Usia {umur} · {pekerjaan} · Dianalisis pada {datetime.now().strftime("%d %B %Y, %H:%M")}</div>
                </div>
            </div>
            """, unsafe_allow_html=True)

            # Overall verdict + risk
            col_verdict, col_risk = st.columns([3, 1])

            with col_verdict:
                st.markdown(f"""
                <div class="{verdict_class(ov_s)}">
                    <div class="verdict-title">Rekomendasi Keputusan Akhir</div>
                    <div class="verdict-status">{'✅' if ov_s=='approved' else ('⛔' if ov_s=='rejected' else '⚠️')} {ov_status}</div>
                    <div class="verdict-sub">{ov_reason}</div>
                </div>
                """, unsafe_allow_html=True)

            with col_risk:
                st.markdown(f"""
                <div class="metric-card" style="height:100%; display:flex; flex-direction:column; justify-content:center;">
                    <div class="metric-label">Profil Risiko Dasar</div>
                    <div class="metric-value" style="color:{risk_col}; font-size:1.5rem;">{risk_label}</div>
                    <div class="risk-bar-container" style="margin-top:10px;">
                        <div class="risk-bar" style="width:{risk_score}%; background:{risk_col};"></div>
                    </div>
                    <div class="metric-sub" style="margin-top:4px;">Skor Komposit: {risk_score}/100</div>
                </div>
                """, unsafe_allow_html=True)

            st.write("")

            # Three method cards
            st.markdown('<div class="section-title">📊 Rincian Hasil dari Masing-Masing Metode</div>', unsafe_allow_html=True)
            mc1, mc2, mc3 = st.columns(3)

            with mc1:
                st.markdown(f"""
                <div class="method-card">
                    <div class="method-badge badge-fuzzy">Fuzzy Logic</div>
                    <div class="method-name">Manual FIS</div>
                    <div class="method-score {score_color_class(fz_s)}">{hasil_fuzzy:.1f}<span style="font-size:1rem;opacity:0.5">/100</span></div>
                    <div class="method-label {label_class(fz_s)}">{'✅ ' if fz_s=='approved' else ('⛔ ' if fz_s=='rejected' else '⚠️ ')}{fz_status}</div>
                    <div class="method-note">📌 Analisis Input: {alasan_fuzzy}</div>
                </div>
                """, unsafe_allow_html=True)

            with mc2:
                st.markdown(f"""
                <div class="method-card">
                    <div class="method-badge badge-ga">Fuzzy + GA</div>
                    <div class="method-name">Genetic Algorithm Tuning</div>
                    <div class="method-score {score_color_class(ga_s)}">{hasil_ga:.1f}<span style="font-size:1rem;opacity:0.5">/100</span></div>
                    <div class="method-label {label_class(ga_s)}">{'✅ ' if ga_s=='approved' else ('⛔ ' if ga_s=='rejected' else '⚠️ ')}{ga_status}</div>
                    <div class="method-note">📌 Analisis Input: {alasan_ga}</div>
                </div>
                """, unsafe_allow_html=True)

            with mc3:
                if ann_label:
                    st.markdown(f"""
                    <div class="method-card">
                        <div class="method-badge badge-ann">Neural Network</div>
                        <div class="method-name">ANN Classifier</div>
                        <div class="method-score {score_color_class(ann_s)}" style="font-size:1.5rem; margin-top:16px;">{'Binary ML'}</div>
                        <div class="method-label {label_class(ann_s)}">{'✅ ' if ann_s=='approved' else '⛔ '}{ann_label}</div>
                        <div class="method-note">📌 Analisis Input: {alasan_ann}</div>
                    </div>
                    """, unsafe_allow_html=True)
                else:
                    st.markdown("""
                    <div class="method-card" style="opacity:0.5;">
                        <div class="method-badge badge-ann">Neural Network</div>
                        <div class="method-name">ANN Classifier</div>
                        <div style="color:#8899AA; font-size:0.85rem; margin-top:16px;">⚠️ Model file not found.<br>Pastikan file <code>ann_model.pkl</code> ada di folder aplikasi.</div>
                    </div>
                    """, unsafe_allow_html=True)

            st.write("")

            # Key factors breakdown
            st.markdown('<div class="section-title">🔎 Breakdown Variabel Penentu</div>', unsafe_allow_html=True)
            f1, f2, f3 = st.columns(3)

            income_score = 35 if pendapatan > 75000 else (20 if pendapatan > 40000 else 5)
            dr_score = 35 if rasio_hutang < 0.20 else (18 if rasio_hutang < 0.30 else 3)
            emp_score = 30 if lama_kerja > 7 else (18 if lama_kerja > 3 else 5)

            for col, label, val, score, max_s, icon in [
                (f1, "Pendapatan", format_currency(pendapatan), income_score, 35, "💰"),
                (f2, "Rasio Hutang", format_pct(rasio_hutang), dr_score, 35, "📉"),
                (f3, "Masa Kerja", f"{lama_kerja} thn", emp_score, 30, "🧑‍💼"),
            ]:
                bar_w = int(score / max_s * 100)
                bar_c = "#059669" if bar_w >= 70 else ("#D97706" if bar_w >= 40 else "#DC2626")
                with col:
                    st.markdown(f"""
                    <div class="metric-card">
                        <div class="metric-label">{icon} {label}</div>
                        <div class="metric-value" style="font-size:1.5rem;">{val}</div>
                        <div class="risk-bar-container" style="margin-top:10px;">
                            <div class="risk-bar" style="width:{bar_w}%; background:{bar_c};"></div>
                        </div>
                        <div class="metric-sub" style="margin-top:4px;">Kekuatan Skor: {score}/{max_s}</div>
                    </div>
                    """, unsafe_allow_html=True)

            # Fuzzy score radar chart
            st.write("")
            st.markdown('<div class="section-title">📈 Visualisasi Skor Evaluasi</div>', unsafe_allow_html=True)

            chart_col1, chart_col2 = st.columns(2)
            with chart_col1:
                # Gauge for Fuzzy Manual
                fig_gauge = go.Figure(go.Indicator(
                    mode="gauge+number",
                    value=hasil_fuzzy,
                    domain={'x': [0, 1], 'y': [0, 1]},
                    title={'text': "Skor Fuzzy Manual", 'font': {'size': 14, 'family': 'Plus Jakarta Sans'}},
                    number={'font': {'size': 32, 'family': 'Space Mono'}},
                    gauge={
                        'axis': {'range': [0, 100], 'tickwidth': 1},
                        'bar': {'color': risk_color(fz_s)},
                        'steps': [
                            {'range': [0, 40], 'color': '#FEE2E2'},
                            {'range': [40, 65], 'color': '#FEF3C7'},
                            {'range': [65, 100], 'color': '#D1FAE5'}
                        ],
                        'threshold': {'line': {'color': '#0A1628', 'width': 2}, 'value': hasil_fuzzy}
                    }
                ))
                fig_gauge.update_layout(
                    height=240, margin=dict(l=20, r=20, t=50, b=10),
                    paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0,0,0,0)',
                    font={'family': 'Plus Jakarta Sans'}
                )
                st.plotly_chart(fig_gauge, use_container_width=True)

            with chart_col2:
                # Gauge for GA
                fig_gauge2 = go.Figure(go.Indicator(
                    mode="gauge+number",
                    value=hasil_ga,
                    domain={'x': [0, 1], 'y': [0, 1]},
                    title={'text': "Skor Fuzzy + Algoritma Genetika", 'font': {'size': 14, 'family': 'Plus Jakarta Sans'}},
                    number={'font': {'size': 32, 'family': 'Space Mono'}},
                    gauge={
                        'axis': {'range': [0, 100], 'tickwidth': 1},
                        'bar': {'color': risk_color(ga_s)},
                        'steps': [
                            {'range': [0, 40], 'color': '#FEE2E2'},
                            {'range': [40, 65], 'color': '#FEF3C7'},
                            {'range': [65, 100], 'color': '#D1FAE5'}
                        ],
                        'threshold': {'line': {'color': '#0A1628', 'width': 2}, 'value': hasil_ga}
                    }
                ))
                fig_gauge2.update_layout(
                    height=240, margin=dict(l=20, r=20, t=50, b=10),
                    paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0,0,0,0)',
                    font={'family': 'Plus Jakarta Sans'}
                )
                st.plotly_chart(fig_gauge2, use_container_width=True)


# ============================================================
# PAGE: DASHBOARD & HISTORY
# ============================================================
elif "📊" in menu:

    st.markdown("""
    <div class="page-header">
        <h1>📊 Dashboard & Riwayat Aplikasi</h1>
        <p>Pantauan visual dari seluruh nasabah yang telah dievaluasi dalam sesi aplikasi ini.</p>
    </div>
    """, unsafe_allow_html=True)

    if len(st.session_state.history_data) == 0:
        st.info("💡 Belum ada data nasabah. Silakan lakukan evaluasi terlebih dahulu di menu **Applicant Analysis**.")
    else:
        df = pd.DataFrame(st.session_state.history_data)

        # ---- SUMMARY METRICS ----
        total = len(df)
        approved = (df["Status"] == "APPROVED").sum()
        rejected = (df["Status"] == "REJECTED").sum()
        review   = (df["Status"] == "UNDER REVIEW").sum()
        avg_income = df["Income"].mean()

        m1, m2, m3, m4 = st.columns(4)
        for col, label, val, sub in [
            (m1, "Total Evaluasi", total, "Data sesi saat ini"),
            (m2, "✅ Layak (Approved)", approved, f"Tingkat persetujuan: {approved/total*100:.0f}%"),
            (m3, "⛔ Ditolak (Rejected)", rejected, f"Tingkat penolakan: {rejected/total*100:.0f}%"),
            (m4, "💰 Rata-rata Gaji", format_currency(avg_income), "Dari total nasabah"),
        ]:
            with col:
                st.markdown(f"""
                <div class="metric-card">
                    <div class="metric-label">{label}</div>
                    <div class="metric-value">{val}</div>
                    <div class="metric-sub">{sub}</div>
                </div>
                """, unsafe_allow_html=True)

        st.write("")

        # ---- CHARTS ----
        ch1, ch2 = st.columns(2)

        with ch1:
            st.markdown('<div class="section-title">Distribusi Keputusan Akhir</div>', unsafe_allow_html=True)
            fig_pie = go.Figure(go.Pie(
                labels=["Approved", "Rejected", "Under Review"],
                values=[approved, rejected, review],
                hole=0.55,
                marker_colors=["#059669", "#DC2626", "#D97706"],
                textinfo='label+percent',
                textfont=dict(family='Plus Jakarta Sans', size=12)
            ))
            fig_pie.update_layout(
                showlegend=False, height=260,
                margin=dict(l=10, r=10, t=10, b=10),
                paper_bgcolor='rgba(0,0,0,0)'
            )
            st.plotly_chart(fig_pie, use_container_width=True)

        with ch2:
            st.markdown('<div class="section-title">Sebaran Pendapatan vs Skor Kelayakan</div>', unsafe_allow_html=True)
            colors_map = {"APPROVED": "#059669", "REJECTED": "#DC2626", "UNDER REVIEW": "#D97706"}
            fig_scatter = px.scatter(
                df, x="Income", y="Fuzzy Score",
                color="Status",
                color_discrete_map=colors_map,
                hover_data=["Name", "Debt Ratio", "Emp. Years"],
                size_max=12
            )
            fig_scatter.update_layout(
                height=260, margin=dict(l=10, r=10, t=10, b=10),
                paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0,0,0,0)',
                legend=dict(orientation="h", yanchor="bottom", y=1.02),
                font=dict(family='Plus Jakarta Sans')
            )
            fig_scatter.update_traces(marker=dict(size=9, opacity=0.8))
            st.plotly_chart(fig_scatter, use_container_width=True)

        st.write("")

        # ---- HISTORY TABLE ----
        st.markdown('<div class="section-title">📋 Riwayat Detail Nasabah</div>', unsafe_allow_html=True)

        # Filter
        filter_col1, filter_col2 = st.columns([2, 1])
        with filter_col1:
            search = st.text_input("🔍 Cari berdasarkan Nama atau ID Nasabah", placeholder="Ketik untuk mencari...")
        with filter_col2:
            status_filter = st.selectbox("Saring berdasarkan Status", ["Semua", "APPROVED", "REJECTED", "UNDER REVIEW"])

        filtered_df = df.copy()

        if search:
            filtered_df = filtered_df[
                filtered_df["Name"].str.contains(search, case=False) |
                filtered_df["ID"].str.contains(search, case=False)
            ]

        if status_filter != "Semua":
            filtered_df = filtered_df[filtered_df["Status"] == status_filter]

        # Format data
        display_df = filtered_df.copy()
        display_df["Income"] = display_df["Income"].apply(format_currency)
        display_df["Debt Ratio"] = display_df["Debt Ratio"].apply(format_pct)

        # Tambahin visual biar menarik
        display_df["Status"] = display_df["Status"].replace({
            "APPROVED": " APPROVED",
            "REJECTED": " REJECTED",
            "UNDER REVIEW": " UNDER REVIEW"
        })

        # Tampilkan tabel
        st.dataframe(display_df, use_container_width=True, height=380)

        st.caption(f"Menampilkan {len(filtered_df)} dari {total} nasabah yang dievaluasi pada sesi saat ini.")