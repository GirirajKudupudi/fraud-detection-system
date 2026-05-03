import streamlit as st

def apply_global_styles():
    """Apply consistent dark theme and styling across all pages."""
    st.markdown("""
    <style>
        /* ============ GLOBAL DARK THEME ============ */
        .stApp {
            background: #0a0e17;
            color: #e0e6ed;
        }
        [data-testid="stSidebar"] {
            background: #141b2d;
            border-right: 2px solid rgba(102,126,234,0.2);
            min-width: 250px;
        }
        [data-testid="stSidebar"] .stRadio label,
        [data-testid="stSidebar"] span,
        [data-testid="stSidebar"] a {
            color: #c4d0ff !important;
            font-size: 1rem !important;
        }
        [data-testid="stSidebarNav"] a {
            color: #c4d0ff !important;
            padding: 8px 15px !important;
            border-radius: 8px !important;
            margin: 2px 5px !important;
        }
        [data-testid="stSidebarNav"] a:hover {
            background: rgba(102,126,234,0.15) !important;
        }
        [data-testid="stSidebarNav"] a[aria-selected="true"] {
            background: rgba(102,126,234,0.2) !important;
            border-left: 3px solid #667eea !important;
        }
        [data-testid="stHeader"] {
            background: transparent;
        }
        
        /* ============ TOP NAVIGATION BAR ============ */
        .top-nav {
            display: flex;
            justify-content: center;
            gap: 8px;
            padding: 12px 0;
            margin-bottom: 20px;
            border-bottom: 1px solid rgba(255,255,255,0.06);
            animation: fadeIn 0.6s ease-out;
        }
        .nav-item {
            padding: 10px 22px;
            border-radius: 10px;
            font-size: 0.88rem;
            font-weight: 600;
            color: #8899aa;
            background: rgba(255,255,255,0.03);
            border: 1px solid rgba(255,255,255,0.06);
            text-decoration: none;
            transition: all 0.3s ease;
            cursor: pointer;
            letter-spacing: 0.3px;
        }
        .nav-item:hover {
            background: rgba(102,126,234,0.15);
            color: #a8b8ff;
            border-color: rgba(102,126,234,0.3);
            transform: translateY(-2px);
        }
        .nav-active {
            background: linear-gradient(135deg, rgba(102,126,234,0.2), rgba(118,75,162,0.2));
            color: #c4d0ff;
            border-color: rgba(102,126,234,0.4);
            box-shadow: 0 4px 15px rgba(102,126,234,0.15);
        }
        
        /* ============ METRIC CARDS ============ */
        [data-testid="stMetric"] {
            background: linear-gradient(135deg, #141b2d 0%, #1a2235 100%);
            border: 1px solid rgba(255,255,255,0.04);
            border-radius: 14px;
            padding: 18px 20px;
            box-shadow: 0 4px 20px rgba(0,0,0,0.3);
            transition: transform 0.3s, box-shadow 0.3s;
        }
        [data-testid="stMetric"]:hover {
            transform: translateY(-3px);
            box-shadow: 0 8px 30px rgba(0,0,0,0.4);
        }
        [data-testid="stMetricLabel"] {
            color: #7a8ba5 !important;
            font-size: 0.82rem !important;
            letter-spacing: 0.5px;
        }
        [data-testid="stMetricValue"] {
            color: #e8ecf1 !important;
            font-weight: 800 !important;
        }
        
        /* ============ PLOTLY CHARTS ============ */
        .js-plotly-plot .plotly .main-svg {
            background: transparent !important;
        }
        
        /* ============ BUTTONS ============ */
        .stButton > button[kind="primary"] {
            background: linear-gradient(135deg, #667eea, #764ba2);
            border: none;
            border-radius: 12px;
            padding: 12px 24px;
            font-weight: 700;
            letter-spacing: 0.5px;
            transition: all 0.3s;
            box-shadow: 0 4px 15px rgba(102,126,234,0.3);
        }
        .stButton > button[kind="primary"]:hover {
            transform: translateY(-2px);
            box-shadow: 0 8px 25px rgba(102,126,234,0.5);
        }
        
        /* ============ SELECT BOXES / INPUTS ============ */
        .stSelectbox > div > div,
        .stNumberInput > div > div > input,
        .stTextInput > div > div > input {
            background: #141b2d !important;
            border-color: rgba(255,255,255,0.08) !important;
            color: #e0e6ed !important;
            border-radius: 10px !important;
        }
        
        /* ============ DIVIDERS ============ */
        hr {
            border-color: rgba(255,255,255,0.06) !important;
        }
        
        /* ============ SECTION HEADERS ============ */
        .section-header {
            font-size: 1.4rem;
            font-weight: 700;
            color: #c4d0ff;
            margin-bottom: 15px;
            padding-bottom: 8px;
            border-bottom: 2px solid rgba(102,126,234,0.2);
            letter-spacing: 0.3px;
        }
        
        /* ============ STAT CARDS (Custom) ============ */
        .glow-card {
            border-radius: 16px;
            padding: 28px 20px;
            text-align: center;
            margin: 8px 0;
            animation: popIn 0.6s ease-out;
            transition: transform 0.3s, box-shadow 0.3s;
            border: 1px solid rgba(255,255,255,0.05);
        }
        .glow-card:hover {
            transform: translateY(-5px);
            box-shadow: 0 12px 35px rgba(0,0,0,0.5);
        }
        .glow-number {
            font-size: 2.6rem;
            font-weight: 900;
            color: white;
            text-shadow: 0 2px 12px rgba(0,0,0,0.3);
        }
        .glow-label {
            font-size: 0.85rem;
            color: rgba(255,255,255,0.8);
            margin-top: 8px;
            font-weight: 500;
            letter-spacing: 0.5px;
            text-transform: uppercase;
        }
        
        /* ============ FEATURE / INFO CARDS ============ */
        .info-card {
            background: #141b2d;
            border-radius: 14px;
            padding: 22px;
            border-left: 4px solid #667eea;
            margin: 10px 0;
            animation: slideUp 0.7s ease-out;
            transition: transform 0.3s, border-color 0.3s;
        }
        .info-card:hover {
            transform: translateX(5px);
            border-left-color: #a78bfa;
        }
        .info-card h4 { color: #e0e6ed; margin: 0 0 8px 0; }
        .info-card p { color: #7a8ba5; font-size: 0.9rem; line-height: 1.6; margin: 0; }
        
        /* ============ TECH BADGES ============ */
        .badge {
            display: inline-block;
            background: rgba(102,126,234,0.1);
            color: #98aaff;
            padding: 6px 16px;
            border-radius: 20px;
            margin: 4px;
            font-size: 0.82rem;
            font-weight: 600;
            border: 1px solid rgba(102,126,234,0.2);
            transition: all 0.3s;
        }
        .badge:hover {
            background: rgba(102,126,234,0.25);
            transform: scale(1.05);
        }
        
        /* ============ RESULT CARDS (Scanner) ============ */
        .result-box {
            border-radius: 20px;
            padding: 35px;
            margin: 25px 0;
            animation: resultPop 0.8s ease-out;
            backdrop-filter: blur(10px);
        }
        .result-val {
            font-size: 3rem;
            font-weight: 900;
            text-align: center;
        }
        .result-sub {
            font-size: 0.9rem;
            text-align: center;
            margin-top: 5px;
            opacity: 0.85;
        }
        
        /* Reason cards */
        .reason-up {
            background: rgba(231,76,60,0.08);
            border: 1px solid rgba(231,76,60,0.25);
            border-radius: 12px;
            padding: 14px 18px;
            margin: 8px 0;
            animation: slideR 0.5s ease-out;
            transition: all 0.3s;
        }
        .reason-up:hover { background: rgba(231,76,60,0.15); transform: translateX(4px); }
        .reason-down {
            background: rgba(46,204,113,0.08);
            border: 1px solid rgba(46,204,113,0.25);
            border-radius: 12px;
            padding: 14px 18px;
            margin: 8px 0;
            animation: slideL 0.5s ease-out;
            transition: all 0.3s;
        }
        .reason-down:hover { background: rgba(46,204,113,0.15); transform: translateX(-4px); }
        
        /* ============ PIPELINE STEPS ============ */
        .step-box {
            background: #141b2d;
            border-radius: 14px;
            padding: 22px;
            text-align: center;
            border-top: 3px solid;
            animation: slideUp 0.7s ease-out;
        }
        .step-num {
            font-size: 2.2rem;
            font-weight: 900;
            margin-bottom: 6px;
        }
        .step-box h4 { color: #e0e6ed; margin: 0 0 8px 0; }
        .step-box p { color: #7a8ba5; font-size: 0.85rem; line-height: 1.5; margin: 0; }
        
        /* ============ SCANNING ANIMATION ============ */
        .scan-anim {
            text-align: center;
            font-size: 1.2rem;
            color: #4facfe;
            animation: blink 1.2s infinite;
        }
        
        /* ============ FOOTER ============ */
        .footer {
            text-align: center;
            color: #4a5568;
            font-size: 0.82rem;
            padding: 15px;
            margin-top: 30px;
            border-top: 1px solid rgba(255,255,255,0.04);
        }
        .footer a { color: #667eea; text-decoration: none; }
        .footer b { color: #98aaff; }
        
        /* ============ ANIMATIONS ============ */
        @keyframes fadeIn { from { opacity: 0; } to { opacity: 1; } }
        @keyframes slideUp { from { opacity: 0; transform: translateY(25px); } to { opacity: 1; transform: translateY(0); } }
        @keyframes popIn { 0% { opacity: 0; transform: scale(0.85); } 70% { transform: scale(1.03); } 100% { opacity: 1; transform: scale(1); } }
        @keyframes resultPop { from { opacity: 0; transform: translateY(30px) scale(0.95); } to { opacity: 1; transform: translateY(0) scale(1); } }
        @keyframes slideR { from { opacity: 0; transform: translateX(-15px); } to { opacity: 1; transform: translateX(0); } }
        @keyframes slideL { from { opacity: 0; transform: translateX(15px); } to { opacity: 1; transform: translateX(0); } }
        @keyframes blink { 0%,100% { opacity: 1; } 50% { opacity: 0.3; } }
    </style>
    """, unsafe_allow_html=True)


def render_nav(active="Home"):
    """Render top navigation bar."""
    pages = {
        "Home": "app",
        "Dashboard": "pages/1_Dashboard",
        "Scanner": "pages/2_Transaction_Scanner",
        "Optimizer": "pages/3_Threshold_Optimizer",
        "Performance": "pages/4_Model_Performance"
    }
    icons = {"Home": "🏠", "Dashboard": "📊", "Scanner": "🔎", "Optimizer": "⚙️", "Performance": "📈"}
    
    nav_html = '<div class="top-nav">'
    for name, path in pages.items():
        cls = "nav-item nav-active" if name == active else "nav-item"
        nav_html += f'<span class="{cls}">{icons[name]} {name}</span>'
    nav_html += '</div>'
    st.markdown(nav_html, unsafe_allow_html=True)


def render_footer():
    """Render consistent footer."""
    st.markdown("""
    <div class="footer">
        Built by <b>Giriraj Kudupudi</b> | MS Data Analytics | 
        <a href="https://github.com/GirirajKudupudi">GitHub</a> | 
        Model: XGBoost | ROC-AUC: 0.9988
    </div>
    """, unsafe_allow_html=True)
