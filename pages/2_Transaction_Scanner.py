import streamlit as st
import numpy as np
import joblib
import shap
import time
import sys, os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from src.styles import apply_global_styles, render_nav, render_footer

st.set_page_config(page_title='Transaction Scanner', page_icon='🔎', layout='wide', initial_sidebar_state='collapsed')
apply_global_styles()
render_nav("Scanner")

@st.cache_resource
def load_model():
    return joblib.load('models/best_model.pkl'), joblib.load('models/scaler.pkl'), joblib.load('models/feature_names.pkl')

model, scaler, feature_names = load_model()

st.markdown("""
<div style="margin-bottom: 20px;">
    <h1 style="font-size: 2rem; font-weight: 800; color: #c4d0ff; margin: 0;">🔎 Transaction Scanner</h1>
    <p style="color: #6b7c93; margin-top: 5px;">Real-time fraud assessment with explainable AI</p>
</div>
""", unsafe_allow_html=True)

# Input sections
c1, c2, c3 = st.columns(3)

with c1:
    st.markdown('<div class="section-header">💳 Transaction</div>', unsafe_allow_html=True)
    amt = st.number_input('Amount ($)', min_value=0.0, max_value=50000.0, value=500.0, step=10.0)
    category = st.selectbox('Category', [
        'shopping_net', 'shopping_pos', 'grocery_pos', 'grocery_net',
        'food_dining', 'entertainment', 'gas_transport', 'misc_net',
        'misc_pos', 'home', 'health_fitness', 'travel',
        'kids_pets', 'personal_care'
    ], format_func=lambda x: x.replace('_', ' ').title())
    distance = st.slider('Distance to Merchant', 0.0, 10.0, 0.5, 0.1)

with c2:
    st.markdown('<div class="section-header">🕐 Timing</div>', unsafe_allow_html=True)
    hour = st.slider('Hour of Day', 0, 23, 14)
    day_of_week = st.selectbox('Day', list(range(7)),
        format_func=lambda x: ['Monday','Tuesday','Wednesday','Thursday','Friday','Saturday','Sunday'][x])
    month = st.selectbox('Month', list(range(1, 13)),
        format_func=lambda x: ['Jan','Feb','Mar','Apr','May','Jun','Jul','Aug','Sep','Oct','Nov','Dec'][x-1])

with c3:
    st.markdown('<div class="section-header">👤 Customer</div>', unsafe_allow_html=True)
    age = st.number_input('Age', min_value=18, max_value=100, value=45)
    gender = st.selectbox('Gender', ['Male', 'Female'])
    city_pop = st.number_input('City Population', min_value=100, max_value=5000000, value=50000, step=1000)

st.markdown("---")

if st.button('🛡️ SCAN TRANSACTION', type='primary', use_container_width=True):
    # Scanning animation
    ph = st.empty()
    for msg in ['🔄 Analyzing transaction patterns...', '🧠 Running XGBoost fraud detection...', '📊 Computing SHAP explanations...']:
        ph.markdown(f'<div class="scan-anim">{msg}</div>', unsafe_allow_html=True)
        time.sleep(0.4)
    ph.empty()

    is_weekend = 1 if day_of_week >= 5 else 0
    is_night = 1 if hour in [0,1,2,3,4,5,22,23] else 0

    cat_f = {f'cat_{c}': 0 for c in [
        'entertainment','food_dining','gas_transport','grocery_net','grocery_pos',
        'health_fitness','home','kids_pets','misc_net','misc_pos',
        'personal_care','shopping_net','shopping_pos','travel']}
    cat_f[f'cat_{category}'] = 1

    inp = np.array([[amt, hour, day_of_week, month, is_weekend, is_night,
                      np.log1p(amt), 1 if amt > 800 else 0, 1 if amt % 50 == 0 else 0,
                      distance, 1 if distance > 3 else 0, age,
                      1 if gender == 'Male' else 0, city_pop,
                      np.log1p(city_pop), 1 if city_pop < 5000 else 0,
                      *cat_f.values()]])

    scaled = scaler.transform(inp)
    prob = float(model.predict_proba(scaled)[0][1])

    # Config
    if prob > 0.85:
        risk, action, border, bg, glow, pcolor, emoji, aicon = \
            "CRITICAL","BLOCK","#dc3545","rgba(220,53,69,0.06)","rgba(220,53,69,0.35)","#ff4757","🔴","🚫"
    elif prob > 0.6:
        risk, action, border, bg, glow, pcolor, emoji, aicon = \
            "HIGH","BLOCK","#fd7e14","rgba(253,126,20,0.06)","rgba(253,126,20,0.35)","#ff9f43","🟠","🚫"
    elif prob > 0.3:
        risk, action, border, bg, glow, pcolor, emoji, aicon = \
            "MEDIUM","REVIEW","#ffc107","rgba(255,193,7,0.06)","rgba(255,193,7,0.35)","#feca57","🟡","👁️"
    else:
        risk, action, border, bg, glow, pcolor, emoji, aicon = \
            "LOW","APPROVE","#28a745","rgba(40,167,69,0.06)","rgba(40,167,69,0.35)","#2ecc71","🟢","✅"

    # Result
    st.markdown(f"""
    <div class="result-box" style="background: {bg}; border: 2px solid {border}; box-shadow: 0 0 40px {glow};">
        <div style="display: flex; justify-content: space-around; align-items: center; flex-wrap: wrap;">
            <div><div class="result-val" style="color: {pcolor};">{prob:.1%}</div>
                 <div class="result-sub" style="color: {border};">Fraud Probability</div></div>
            <div><div style="font-size: 3.5rem; line-height: 1;">{emoji}</div>
                 <div style="font-weight: 800; font-size: 1.2rem; color: {border}; text-align:center; margin-top: 5px;">{risk}</div></div>
            <div><div style="font-size: 2.8rem; line-height: 1;">{aicon}</div>
                 <div style="font-weight: 800; font-size: 1.3rem; color: {border}; text-align:center; margin-top: 5px;">{action}</div></div>
        </div>
    </div>
    """, unsafe_allow_html=True)

    # SHAP
    exp = shap.TreeExplainer(model)
    sv = exp.shap_values(scaled)
    sd = dict(zip(feature_names, sv[0]))
    top = sorted(sd.items(), key=lambda x: abs(x[1]), reverse=True)[:8]
    ups = [(n, v) for n, v in top if v > 0]
    downs = [(n, v) for n, v in top if v < 0]

    st.markdown('<div class="section-header" style="margin-top: 25px;">🧠 AI Explanation</div>', unsafe_allow_html=True)

    cr, cs = st.columns(2)
    with cr:
        st.markdown("##### ⚠️ Risk Factors")
        if not ups:
            st.markdown('<div class="reason-down" style="text-align:center;">No significant risk factors</div>', unsafe_allow_html=True)
        for n, v in ups:
            clean = n.replace('cat_', '').replace('_', ' ').title()
            pct = min(int(abs(v) / 6 * 100), 100)
            st.markdown(f"""
            <div class="reason-up">
                <div style="display:flex; justify-content:space-between; align-items:center;">
                    <span style="font-weight:700; color:#ff6b6b; font-size:0.95rem;">⬆ {clean}</span>
                    <span style="color:#ff6b6b; font-weight:700; font-size:0.85rem; 
                          background:rgba(231,76,60,0.15); padding:3px 10px; border-radius:8px;">
                        +{abs(v):.3f}</span>
                </div>
                <div style="background:rgba(231,76,60,0.1); border-radius:5px; height:8px; margin-top:10px; overflow:hidden;">
                    <div style="background:linear-gradient(90deg,#e74c3c,#ff6b6b); height:8px; 
                         width:{pct}%; border-radius:5px; animation: barGrow 1s ease-out;"></div>
                </div>
            </div>""", unsafe_allow_html=True)

    with cs:
        st.markdown("##### ✅ Safety Factors")
        if not downs:
            st.markdown('<div class="reason-up" style="text-align:center;">No safety factors detected</div>', unsafe_allow_html=True)
        for n, v in downs:
            clean = n.replace('cat_', '').replace('_', ' ').title()
            pct = min(int(abs(v) / 6 * 100), 100)
            st.markdown(f"""
            <div class="reason-down">
                <div style="display:flex; justify-content:space-between; align-items:center;">
                    <span style="font-weight:700; color:#2ecc71; font-size:0.95rem;">⬇ {clean}</span>
                    <span style="color:#2ecc71; font-weight:700; font-size:0.85rem;
                          background:rgba(46,204,113,0.15); padding:3px 10px; border-radius:8px;">
                        -{abs(v):.3f}</span>
                </div>
                <div style="background:rgba(46,204,113,0.1); border-radius:5px; height:8px; margin-top:10px; overflow:hidden;">
                    <div style="background:linear-gradient(90deg,#2ecc71,#55efc4); height:8px; 
                         width:{pct}%; border-radius:5px; animation: barGrow 1s ease-out;"></div>
                </div>
            </div>""", unsafe_allow_html=True)

    st.markdown("""
    <style>@keyframes barGrow { from { width: 0; } }</style>
    """, unsafe_allow_html=True)

render_footer()
