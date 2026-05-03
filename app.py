import streamlit as st
from src.styles import apply_global_styles, render_nav, render_footer

st.set_page_config(page_title='Fraud Detection System', page_icon='🛡️', layout='wide',initial_sidebar_state='expanded' )

apply_global_styles()
render_nav("Home")

# ---- Hero ----
st.markdown("""
<div style="text-align:center; padding: 40px 0 10px;">
    <div style="font-size: 4rem; margin-bottom: 10px; animation: popIn 0.6s ease-out;">🛡️</div>
    <h1 style="font-size: 2.8rem; font-weight: 900;
        background: linear-gradient(135deg, #667eea 0%, #a78bfa 40%, #f093fb 100%);
        -webkit-background-clip: text; -webkit-text-fill-color: transparent;
        margin: 0; animation: fadeIn 0.8s ease-out;">
        Fraud Detection System
    </h1>
    <p style="color: #6b7c93; font-size: 1.1rem; margin-top: 10px; animation: fadeIn 1s ease-out;">
        AI-Powered Real-Time Transaction Monitoring & Investigation Platform
    </p>
</div>
""", unsafe_allow_html=True)

# ---- Stats Row ----
st.markdown("")
c1, c2, c3, c4 = st.columns(4)

stats = [
    ("1.3M+", "Transactions Analyzed", "linear-gradient(135deg, #667eea, #764ba2)"),
    ("99.88%", "ROC-AUC Score", "linear-gradient(135deg, #f093fb, #f5576c)"),
    ("93%", "Fraud Detection Rate", "linear-gradient(135deg, #4facfe, #00f2fe)"),
    ("30", "Engineered Features", "linear-gradient(135deg, #43e97b, #38f9d7)")
]

for col, (num, label, bg) in zip([c1,c2,c3,c4], stats):
    with col:
        st.markdown(f"""
        <div class="glow-card" style="background: {bg};">
            <div class="glow-number">{num}</div>
            <div class="glow-label">{label}</div>
        </div>
        """, unsafe_allow_html=True)

# ---- Capabilities ----
st.markdown("---")
st.markdown('<div class="section-header">System Capabilities</div>', unsafe_allow_html=True)

c1, c2, c3 = st.columns(3)
cards = [
    ("📊 Analytics Dashboard", "Monitor fraud patterns across time, categories, and geography with interactive visualizations.", "#667eea"),
    ("🔎 Transaction Scanner", "Submit any transaction for instant AI-powered fraud probability, risk level, and explainable reasons.", "#f5576c"),
    ("⚙️ Threshold Optimizer", "Fine-tune fraud-vs-false-alarm tradeoff with real-time business impact in dollars.", "#43e97b"),
]
for col, (title, desc, color) in zip([c1,c2,c3], cards):
    with col:
        st.markdown(f"""
        <div class="info-card" style="border-left-color: {color};">
            <h4>{title}</h4>
            <p>{desc}</p>
        </div>
        """, unsafe_allow_html=True)

# ---- Pipeline ----
st.markdown("---")
st.markdown('<div class="section-header">Pipeline Architecture</div>', unsafe_allow_html=True)

c1, c2, c3, c4 = st.columns(4)
steps = [
    ("01", "Ingest", "Transaction data with amount, time, location, category, and customer details", "#667eea"),
    ("02", "Engineer", "30 features: time patterns, amount anomalies, distance metrics, risk signals", "#a78bfa"),
    ("03", "Score", "XGBoost assigns fraud probability with risk classification", "#4facfe"),
    ("04", "Explain", "SHAP provides top reasons WHY each transaction was flagged", "#43e97b"),
]
for col, (num, title, desc, color) in zip([c1,c2,c3,c4], steps):
    with col:
        st.markdown(f"""
        <div class="step-box" style="border-top-color: {color};">
            <div class="step-num" style="color: {color};">{num}</div>
            <h4>{title}</h4>
            <p>{desc}</p>
        </div>
        """, unsafe_allow_html=True)

# ---- Tech Stack ----
st.markdown("---")
st.markdown('<div class="section-header">Tech Stack</div>', unsafe_allow_html=True)

techs = ['Python', 'XGBoost', 'Scikit-learn', 'SHAP', 'FastAPI', 'Streamlit', 'Pandas', 'Plotly', 'Docker']
badges = "".join([f'<span class="badge">{t}</span>' for t in techs])
st.markdown(badges, unsafe_allow_html=True)

# ---- Navigate ----
st.markdown("---")
st.markdown('<div class="section-header">Explore the System</div>', unsafe_allow_html=True)

c1, c2, c3, c4 = st.columns(4)
with c1: st.markdown("**📊 Dashboard** — Use sidebar to navigate")
with c2: st.markdown("**🔎 Scanner** — Use sidebar to navigate")
with c3: st.markdown("**⚙️ Optimizer** — Use sidebar to navigate")
with c4: st.markdown("**📈 Performance** — Use sidebar to navigate")

render_footer()
