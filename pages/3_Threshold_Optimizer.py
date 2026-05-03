import streamlit as st
import pandas as pd
import numpy as np
import plotly.graph_objects as go
import joblib
import sys, os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from src.styles import apply_global_styles, render_nav, render_footer

st.set_page_config(page_title='Threshold Optimizer', page_icon='⚙️', layout='wide', initial_sidebar_state='collapsed')
apply_global_styles()
render_nav("Optimizer")

PLOT_BG = "rgba(0,0,0,0)"
GRID_COLOR = "rgba(255,255,255,0.05)"
FONT_COLOR = "#8899aa"

@st.cache_resource
def load_model():
    return joblib.load('models/best_model.pkl'), joblib.load('models/scaler.pkl')

@st.cache_data
def load_and_predict():
    df = pd.read_csv('data/processed/fraud_features.csv')
    sample = df.sample(n=min(50000, len(df)), random_state=42)
    y_true = sample['is_fraud']
    X = sample.drop(columns=['is_fraud'])
    bool_cols = X.select_dtypes(include=['bool']).columns
    X[bool_cols] = X[bool_cols].astype(int)
    model, scaler = load_model()
    X_scaled = scaler.transform(X)
    y_probs = model.predict_proba(X_scaled)[:, 1]
    return y_true.values, y_probs

y_true, y_probs = load_and_predict()

st.markdown("""
<div style="margin-bottom: 20px;">
    <h1 style="font-size: 2rem; font-weight: 800; color: #c4d0ff; margin: 0;">⚙️ Threshold Optimizer</h1>
    <p style="color: #6b7c93; margin-top: 5px;">Balance between catching fraud and minimizing false alarms</p>
</div>
""", unsafe_allow_html=True)

threshold = st.slider('Decision Threshold', min_value=0.05, max_value=0.95, value=0.50, step=0.05,
    help='Lower = catch more fraud but more false alarms. Higher = fewer false alarms but miss more fraud.')

y_pred = (y_probs >= threshold).astype(int)
tp = int(((y_pred == 1) & (y_true == 1)).sum())
fp = int(((y_pred == 1) & (y_true == 0)).sum())
fn = int(((y_pred == 0) & (y_true == 1)).sum())
tn = int(((y_pred == 0) & (y_true == 0)).sum())
recall = tp / (tp + fn) if (tp + fn) > 0 else 0
precision = tp / (tp + fp) if (tp + fp) > 0 else 0

st.markdown("---")
st.markdown('<div class="section-header">Detection Metrics</div>', unsafe_allow_html=True)

c1, c2, c3, c4 = st.columns(4)
c1.metric('🎯 Fraud Caught', f"{recall:.1%}")
c2.metric('✅ Precision', f"{precision:.1%}")
c3.metric('🚨 False Alarms', f"{fp:,}")
c4.metric('❌ Missed Fraud', f"{fn:,}")

st.markdown("---")
st.markdown('<div class="section-header">Business Impact</div>', unsafe_allow_html=True)

avg_loss = 750.0
review_cost = 5.0
saved = tp * avg_loss
missed = fn * avg_loss
reviews = fp * review_cost
net = saved - missed - reviews

b1, b2, b3, b4 = st.columns(4)
b1.metric('💰 Fraud Prevented', f"${saved:,.0f}")
b2.metric('💸 Fraud Missed', f"${missed:,.0f}")
b3.metric('📋 Review Costs', f"${reviews:,.0f}")
b4.metric('📈 Net Savings', f"${net:,.0f}", delta=f"${net:,.0f}", delta_color="normal")

st.markdown("---")
st.markdown('<div class="section-header">Precision vs Recall Curve</div>', unsafe_allow_html=True)

thresholds = np.arange(0.05, 0.96, 0.05)
metrics = []
for t in thresholds:
    yp = (y_probs >= t).astype(int)
    tp_t = ((yp == 1) & (y_true == 1)).sum()
    fp_t = ((yp == 1) & (y_true == 0)).sum()
    fn_t = ((yp == 0) & (y_true == 1)).sum()
    rec = tp_t / (tp_t + fn_t) if (tp_t + fn_t) > 0 else 0
    prec = tp_t / (tp_t + fp_t) if (tp_t + fp_t) > 0 else 0
    metrics.append({'Threshold': round(t, 2), 'Recall': rec, 'Precision': prec})

m_df = pd.DataFrame(metrics)

fig = go.Figure()
fig.add_trace(go.Scatter(x=m_df['Threshold'], y=m_df['Recall'],
    name='Recall (Fraud Caught)', line=dict(color='#ff6b6b', width=3),
    fill='tozeroy', fillcolor='rgba(255,107,107,0.05)'))
fig.add_trace(go.Scatter(x=m_df['Threshold'], y=m_df['Precision'],
    name='Precision', line=dict(color='#2ecc71', width=3),
    fill='tozeroy', fillcolor='rgba(46,204,113,0.05)'))
fig.add_vline(x=threshold, line_dash="dash", line_color="#667eea",
              annotation_text=f"Current: {threshold}", annotation_font=dict(color="#667eea"))
fig.update_layout(
    plot_bgcolor=PLOT_BG, paper_bgcolor=PLOT_BG,
    font=dict(color=FONT_COLOR), height=450,
    xaxis=dict(title='Threshold', gridcolor=GRID_COLOR),
    yaxis=dict(title='Score', gridcolor=GRID_COLOR, range=[0, 1.05]),
    legend=dict(bgcolor='rgba(0,0,0,0)', font=dict(color='#8899aa'),
                yanchor="bottom", y=0.02, xanchor="right", x=0.98)
)
st.plotly_chart(fig, use_container_width=True)

st.markdown("""
> **💡 How to use:** Banks prioritize catching fraud (**high recall**, lower threshold). 
> E-commerce platforms prioritize customer experience (**high precision**, higher threshold). 
> Drag the slider to find the optimal balance for your use case.
""")

render_footer()
