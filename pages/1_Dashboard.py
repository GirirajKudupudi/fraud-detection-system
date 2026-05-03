import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import sys, os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from src.styles import apply_global_styles, render_nav, render_footer

st.set_page_config(page_title='Dashboard', page_icon='📊', layout='wide', initial_sidebar_state='collapsed')
apply_global_styles()
render_nav("Dashboard")

PLOT_BG = "rgba(0,0,0,0)"
PAPER_BG = "rgba(0,0,0,0)"
GRID_COLOR = "rgba(255,255,255,0.05)"
FONT_COLOR = "#8899aa"
PLOT_LAYOUT = dict(
    plot_bgcolor=PLOT_BG, paper_bgcolor=PAPER_BG,
    font=dict(color=FONT_COLOR, size=12),
    xaxis=dict(gridcolor=GRID_COLOR, zerolinecolor=GRID_COLOR),
    yaxis=dict(gridcolor=GRID_COLOR, zerolinecolor=GRID_COLOR),
    margin=dict(l=20, r=20, t=40, b=20),
    coloraxis_showscale=False
)

@st.cache_data
def load_data():
    return pd.read_csv('data/processed/fraud_features.csv')

df = load_data()

st.markdown("""
<div style="margin-bottom: 20px;">
    <h1 style="font-size: 2rem; font-weight: 800; color: #c4d0ff; margin: 0;">📊 Fraud Analytics Dashboard</h1>
    <p style="color: #6b7c93; margin-top: 5px;">Real-time monitoring of transaction patterns and fraud signals</p>
</div>
""", unsafe_allow_html=True)

# KPIs
total = len(df)
fraud_count = int(df['is_fraud'].sum())
fraud_rate = df['is_fraud'].mean() * 100
avg_fraud_amt = df[df['is_fraud'] == 1]['amt'].mean()
avg_legit_amt = df[df['is_fraud'] == 0]['amt'].mean()

c1, c2, c3, c4, c5 = st.columns(5)
c1.metric('Total Transactions', f"{total:,}")
c2.metric('Fraudulent', f"{fraud_count:,}", delta=f"{fraud_rate:.2f}%", delta_color="inverse")
c3.metric('Legitimate', f"{total - fraud_count:,}")
c4.metric('Avg Fraud Amount', f"${avg_fraud_amt:,.0f}")
c5.metric('Avg Legit Amount', f"${avg_legit_amt:,.0f}")

st.markdown("---")

# Row 1
col_l, col_r = st.columns(2)

with col_l:
    st.markdown('<div class="section-header">Fraud Pattern by Hour</div>', unsafe_allow_html=True)
    hourly = df.groupby('hour').agg(fraud_rate=('is_fraud', 'mean')).reset_index()
    hourly['fraud_rate'] = hourly['fraud_rate'] * 100
    fig = px.bar(hourly, x='hour', y='fraud_rate', color='fraud_rate',
                 color_continuous_scale='YlOrRd',
                 labels={'hour': 'Hour', 'fraud_rate': 'Fraud Rate (%)'})
    fig.update_layout(plot_bgcolor=PLOT_BG, paper_bgcolor=PLOT_BG, font=dict(color=FONT_COLOR, size=12),
                      yaxis=dict(gridcolor=GRID_COLOR), margin=dict(l=20, r=20, t=40, b=20),
                      coloraxis_showscale=False, height=400,
                      xaxis=dict(tickmode='linear', gridcolor=GRID_COLOR, zerolinecolor=GRID_COLOR))

with col_r:
    st.markdown('<div class="section-header">Fraud Rate by Category</div>', unsafe_allow_html=True)
    cat_cols = [c for c in df.columns if c.startswith('cat_')]
    cat_data = []
    for col in cat_cols:
        name = col.replace('cat_', '').replace('_', ' ').title()
        subset = df[df[col] == 1]
        if len(subset) > 100:
            cat_data.append({'Category': name, 'Fraud Rate %': subset['is_fraud'].mean() * 100})
    cat_df = pd.DataFrame(cat_data).sort_values('Fraud Rate %', ascending=True)
    fig2 = px.bar(cat_df, x='Fraud Rate %', y='Category', orientation='h',
                  color='Fraud Rate %', color_continuous_scale='YlOrRd')
    fig2.update_layout(**PLOT_LAYOUT, height=400)
    st.plotly_chart(fig2, use_container_width=True)

# Row 2
col_l2, col_r2 = st.columns(2)

with col_l2:
    st.markdown('<div class="section-header">Amount Distribution: Fraud vs Legit</div>', unsafe_allow_html=True)
    fig3 = go.Figure()
    fig3.add_trace(go.Histogram(x=df[df['is_fraud']==0]['amt'].clip(upper=2000),
                                 name='Legitimate', opacity=0.7, marker_color='#2ecc71', nbinsx=50))
    fig3.add_trace(go.Histogram(x=df[df['is_fraud']==1]['amt'].clip(upper=2000),
                                 name='Fraudulent', opacity=0.8, marker_color='#e74c3c', nbinsx=50))
    fig3.update_layout(**PLOT_LAYOUT, height=400, barmode='overlay',
                        xaxis_title='Amount ($)', yaxis_title='Count',
                        legend=dict(bgcolor='rgba(0,0,0,0)', font=dict(color='#8899aa')))
    st.plotly_chart(fig3, use_container_width=True)

with col_r2:
    st.markdown('<div class="section-header">Feature Importance (SHAP)</div>', unsafe_allow_html=True)
    try:
        imp = pd.read_csv('data/processed/feature_importance.csv')
        top12 = imp.head(12).sort_values('importance', ascending=True)
        top12['feature'] = top12['feature'].str.replace('cat_', '').str.replace('_', ' ').str.title()
        fig4 = px.bar(top12, x='importance', y='feature', orientation='h',
                      color='importance', color_continuous_scale='Viridis')
        fig4.update_layout(**PLOT_LAYOUT, height=400)
        st.plotly_chart(fig4, use_container_width=True)
    except:
        st.info("Run explainability module to generate feature importance.")

# Row 3
col_l3, col_r3 = st.columns(2)

with col_l3:
    st.markdown('<div class="section-header">Fraud by Day of Week</div>', unsafe_allow_html=True)
    days = ['Mon', 'Tue', 'Wed', 'Thu', 'Fri', 'Sat', 'Sun']
    daily = df.groupby('day_of_week')['is_fraud'].mean().reset_index()
    daily['day'] = daily['day_of_week'].map(lambda x: days[x])
    daily['rate'] = daily['is_fraud'] * 100
    fig5 = px.bar(daily, x='day', y='rate', color='rate', color_continuous_scale='YlOrRd',
                  labels={'day': 'Day', 'rate': 'Fraud Rate (%)'})
    fig5.update_layout(**PLOT_LAYOUT, height=370)
    st.plotly_chart(fig5, use_container_width=True)

with col_r3:
    st.markdown('<div class="section-header">Night vs Day Fraud</div>', unsafe_allow_html=True)
    nd = df.groupby('is_night')['is_fraud'].mean().reset_index()
    nd['label'] = nd['is_night'].map({0: 'Daytime (6AM-10PM)', 1: 'Nighttime (10PM-6AM)'})
    nd['rate'] = nd['is_fraud'] * 100
    fig6 = px.bar(nd, x='label', y='rate', color='rate', color_continuous_scale='YlOrRd',
                  text='rate', labels={'label': '', 'rate': 'Fraud Rate (%)'})
    fig6.update_traces(texttemplate='%{text:.2f}%', textposition='outside',
                        textfont=dict(color='#e0e6ed'))
    fig6.update_layout(**PLOT_LAYOUT, height=370)
    st.plotly_chart(fig6, use_container_width=True)

render_footer()
