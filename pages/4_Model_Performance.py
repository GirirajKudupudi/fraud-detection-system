import streamlit as st
import pandas as pd
import numpy as np
import plotly.graph_objects as go
import joblib
from sklearn.metrics import roc_curve, precision_recall_curve, confusion_matrix
import sys, os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from src.styles import apply_global_styles, render_nav, render_footer

st.set_page_config(page_title='Model Performance', page_icon='📈', layout='wide', initial_sidebar_state='collapsed')
apply_global_styles()
render_nav("Performance")

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
    <h1 style="font-size: 2rem; font-weight: 800; color: #c4d0ff; margin: 0;">📈 Model Performance</h1>
    <p style="color: #6b7c93; margin-top: 5px;">Detailed analysis of the XGBoost fraud detection model</p>
</div>
""", unsafe_allow_html=True)

# KPIs
c1, c2, c3, c4 = st.columns(4)
c1.metric('Model', 'XGBoost')
c2.metric('ROC-AUC', '0.9988')
c3.metric('Fraud Recall', '93%')
c4.metric('PR-AUC', '0.9456')

st.markdown("---")

# Curves
cl, cr = st.columns(2)

with cl:
    st.markdown('<div class="section-header">ROC Curve</div>', unsafe_allow_html=True)
    fpr, tpr, _ = roc_curve(y_true, y_probs)
    fig_roc = go.Figure()
    fig_roc.add_trace(go.Scatter(x=fpr, y=tpr, name='XGBoost (AUC=0.9988)',
        line=dict(color='#667eea', width=3), fill='tozeroy', fillcolor='rgba(102,126,234,0.05)'))
    fig_roc.add_trace(go.Scatter(x=[0,1], y=[0,1], name='Random Baseline',
        line=dict(color='#4a5568', width=1, dash='dash')))
    fig_roc.update_layout(plot_bgcolor=PLOT_BG, paper_bgcolor=PLOT_BG,
        font=dict(color=FONT_COLOR), height=420,
        xaxis=dict(title='False Positive Rate', gridcolor=GRID_COLOR),
        yaxis=dict(title='True Positive Rate', gridcolor=GRID_COLOR),
        legend=dict(bgcolor='rgba(0,0,0,0)', font=dict(color='#8899aa')))
    st.plotly_chart(fig_roc, use_container_width=True)

with cr:
    st.markdown('<div class="section-header">Precision-Recall Curve</div>', unsafe_allow_html=True)
    prec, rec, _ = precision_recall_curve(y_true, y_probs)
    fig_pr = go.Figure()
    fig_pr.add_trace(go.Scatter(x=rec, y=prec, name='XGBoost (PR-AUC=0.9456)',
        line=dict(color='#f5576c', width=3), fill='tozeroy', fillcolor='rgba(245,87,108,0.05)'))
    fig_pr.update_layout(plot_bgcolor=PLOT_BG, paper_bgcolor=PLOT_BG,
        font=dict(color=FONT_COLOR), height=420,
        xaxis=dict(title='Recall', gridcolor=GRID_COLOR),
        yaxis=dict(title='Precision', gridcolor=GRID_COLOR),
        legend=dict(bgcolor='rgba(0,0,0,0)', font=dict(color='#8899aa')))
    st.plotly_chart(fig_pr, use_container_width=True)

# Confusion Matrix
st.markdown("---")
st.markdown('<div class="section-header">Confusion Matrix</div>', unsafe_allow_html=True)

y_pred = (y_probs >= 0.5).astype(int)
cm = confusion_matrix(y_true, y_pred)

cl2, cr2 = st.columns([1, 1])

with cl2:
    fig_cm = go.Figure(data=go.Heatmap(
        z=cm, x=['Predicted Legit', 'Predicted Fraud'],
        y=['Actual Legit', 'Actual Fraud'],
        text=[[f"TN<br>{cm[0][0]:,}", f"FP<br>{cm[0][1]:,}"],
              [f"FN<br>{cm[1][0]:,}", f"TP<br>{cm[1][1]:,}"]],
        texttemplate="%{text}", textfont=dict(size=16, color='white'),
        colorscale=[[0, '#141b2d'], [0.5, '#2d3a5e'], [1, '#667eea']],
        showscale=False
    ))
    fig_cm.update_layout(plot_bgcolor=PLOT_BG, paper_bgcolor=PLOT_BG,
        font=dict(color=FONT_COLOR), height=400,
        xaxis=dict(side='bottom'), yaxis=dict(autorange='reversed'))
    st.plotly_chart(fig_cm, use_container_width=True)

with cr2:
    st.markdown("""
    #### Reading the Matrix
    
    | Cell | Meaning |
    |------|---------|
    | **TN** | Legit correctly approved ✅ |
    | **FP** | Legit wrongly flagged ⚠️ |
    | **FN** | Fraud missed ❌ |
    | **TP** | Fraud caught 🎯 |
    
    **Goal:** Maximize TP and TN, minimize FP and FN.
    """)

# Model Comparison
st.markdown("---")
st.markdown('<div class="section-header">Model Comparison</div>', unsafe_allow_html=True)

comp = pd.DataFrame({
    'Model': ['Logistic Regression', 'Random Forest', 'XGBoost'],
    'ROC-AUC': [0.9698, 0.9973, 0.9988],
    'PR-AUC': [0.2558, 0.8878, 0.9456],
    'Recall': [0.93, 0.93, 0.93],
    'Precision': [0.07, 0.42, 0.69]
})

fig_comp = go.Figure()
fig_comp.add_trace(go.Bar(name='ROC-AUC', x=comp['Model'], y=comp['ROC-AUC'],
    marker_color='#667eea', text=comp['ROC-AUC'], texttemplate='%{text:.4f}',
    textposition='outside', textfont=dict(color='#c4d0ff')))
fig_comp.add_trace(go.Bar(name='PR-AUC', x=comp['Model'], y=comp['PR-AUC'],
    marker_color='#f5576c', text=comp['PR-AUC'], texttemplate='%{text:.4f}',
    textposition='outside', textfont=dict(color='#f5576c')))
fig_comp.update_layout(plot_bgcolor=PLOT_BG, paper_bgcolor=PLOT_BG,
    font=dict(color=FONT_COLOR), height=420, barmode='group',
    yaxis=dict(range=[0, 1.15], gridcolor=GRID_COLOR),
    xaxis=dict(gridcolor=GRID_COLOR),
    legend=dict(bgcolor='rgba(0,0,0,0)', font=dict(color='#8899aa')))
st.plotly_chart(fig_comp, use_container_width=True)

st.markdown("""
> **Why XGBoost won:** All three models achieve 93% recall, but XGBoost has dramatically 
> better precision (69% vs 7% for Logistic Regression). This means **10x fewer false alarms** 
> in production, translating to massive cost savings.
""")

# Technical Details
st.markdown("---")
st.markdown('<div class="section-header">Technical Details</div>', unsafe_allow_html=True)

st.markdown("""
| Parameter | Value |
|-----------|-------|
| **Algorithm** | XGBoost (Gradient Boosted Trees) |
| **Training Data** | 1,037,340 transactions |
| **Test Data** | 259,335 transactions |
| **Features** | 30 engineered features |
| **Class Balance** | scale_pos_weight (auto-calculated) |
| **Hyperparameters** | n_estimators=300, max_depth=8, lr=0.1 |
| **Explainability** | SHAP (TreeExplainer) |
| **Training Time** | ~2 minutes |
""")

render_footer()
