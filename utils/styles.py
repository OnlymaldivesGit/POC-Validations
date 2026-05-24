"""
utils/styles.py — Shared CSS for the TMA Crew Scheduler Streamlit app.

All st.markdown(unsafe_allow_html=True) CSS injections are centralised here
so the same visual style is applied consistently across every page module
and the main app.py without duplication.

Usage:
    from utils.styles import get_css
    st.markdown(get_css(), unsafe_allow_html=True)
"""


def get_css() -> str:
    """
    Rule: N/A
    Purpose: Return the full custom CSS string for injection via st.markdown.

    Returns:
        A <style>…</style> HTML string ready for use with
        st.markdown(get_css(), unsafe_allow_html=True).

    Known issues:
        None
    """
    return """
    <style>
    .main {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        padding: 0;
    }
    .block-container {
        padding-top: 2rem;
        padding-bottom: 2rem;
        background: transparent;
    }
    [data-testid="stSidebar"] {
        background: #1e293b !important;
    }
    [data-testid="stSidebar"] > div:first-child {
        background: #1e293b !important;
    }
    [data-testid="stSidebar"] * { color: #ffffff !important; }
    [data-testid="stSidebar"] p,
    [data-testid="stSidebar"] span,
    [data-testid="stSidebar"] div { color: #ffffff !important; }
    .dashboard-card {
        background: white;
        border-radius: 15px;
        padding: 25px;
        box-shadow: 0 10px 30px rgba(0,0,0,0.1);
        margin-bottom: 20px;
        transition: transform 0.3s ease, box-shadow 0.3s ease;
    }
    .dashboard-card:hover {
        transform: translateY(-5px);
        box-shadow: 0 15px 40px rgba(0,0,0,0.15);
    }
    .dashboard-header {
        background: white;
        border-radius: 15px;
        padding: 30px;
        margin-bottom: 30px;
        box-shadow: 0 10px 30px rgba(0,0,0,0.1);
    }
    .dashboard-title {
        font-size: 2.5rem;
        font-weight: 700;
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        margin-bottom: 10px;
    }
    .dashboard-subtitle { color: #64748b; font-size: 1.1rem; }
    .metric-card {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        border-radius: 12px;
        padding: 20px;
        color: white;
        text-align: center;
        box-shadow: 0 8px 20px rgba(102, 126, 234, 0.3);
    }
    .metric-value { font-size: 2.5rem; font-weight: 700; margin: 10px 0; }
    .metric-label {
        font-size: 0.75rem;
        opacity: 0.9;
        text-transform: uppercase;
        letter-spacing: 1px;
    }
    .stButton > button {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        color: white;
        border: none;
        border-radius: 10px;
        padding: 12px 30px;
        font-weight: 600;
        transition: all 0.3s ease;
        box-shadow: 0 5px 15px rgba(102, 126, 234, 0.3);
    }
    .stButton > button:hover {
        transform: translateY(-2px);
        box-shadow: 0 8px 25px rgba(102, 126, 234, 0.4);
    }
    .stDownloadButton > button {
        background: linear-gradient(135deg, #10b981 0%, #059669 100%);
        color: white;
        border: none;
        border-radius: 10px;
        padding: 12px 30px;
        font-weight: 600;
        transition: all 0.3s ease;
        box-shadow: 0 5px 15px rgba(16, 185, 129, 0.3);
    }
    .stDownloadButton > button:hover {
        transform: translateY(-2px);
        box-shadow: 0 8px 25px rgba(16, 185, 129, 0.4);
    }
    .streamlit-expanderHeader {
        background: linear-gradient(135deg, #f8fafc 0%, #e2e8f0 100%);
        border-radius: 10px;
        font-weight: 600;
        color: #334155;
        border: 2px solid #e2e8f0;
    }
    .streamlit-expanderHeader:hover { border-color: #667eea; }
    [data-testid="stSidebar"] .streamlit-expanderHeader {
        background: #334155 !important;
        border: 2px solid #475569 !important;
        color: #ffffff !important;
    }
    [data-testid="stSidebar"] .streamlit-expanderHeader:hover {
        background: #475569 !important;
        border-color: #64748b !important;
    }
    [data-testid="stSidebar"] .streamlit-expanderHeader svg { fill: #ffffff !important; }
    [data-testid="stSidebar"] .streamlit-expanderContent {
        background: #1e293b !important;
        border: 1px solid #334155 !important;
    }
    [data-testid="stFileUploader"] {
        background: white;
        border-radius: 10px;
        padding: 20px;
        border: 2px dashed #cbd5e1;
        transition: all 0.3s ease;
    }
    [data-testid="stFileUploader"]:hover {
        border-color: #667eea;
        background: #f8fafc;
    }
    .stDateInput > div > div > input {
        border-radius: 8px;
        border: 2px solid #e2e8f0;
    }
    .dataframe {
        border-radius: 10px;
        overflow: hidden;
        box-shadow: 0 4px 6px rgba(0,0,0,0.05);
    }
    .status-badge {
        display: inline-block;
        padding: 5px 15px;
        border-radius: 20px;
        font-size: 0.85rem;
        font-weight: 600;
        margin: 5px;
    }
    .status-success { background: #d1fae5; color: #065f46; }
    .status-error   { background: #fee2e2; color: #991b1b; }
    .status-warning { background: #fef3c7; color: #92400e; }
    .stSpinner > div { border-color: #667eea !important; }
    .info-box {
        background: linear-gradient(135deg, #e0e7ff 0%, #ddd6fe 100%);
        border-left: 4px solid #667eea;
        border-radius: 8px;
        padding: 15px 20px;
        margin: 15px 0;
        color: #1e293b;
    }
    .success-message {
        background: linear-gradient(135deg, #d1fae5 0%, #a7f3d0 100%);
        border-left: 4px solid #10b981;
        border-radius: 8px;
        padding: 15px 20px;
        margin: 15px 0;
        color: #065f46;
        font-weight: 500;
    }
    .error-message {
        background: linear-gradient(135deg, #fee2e2 0%, #fecaca 100%);
        border-left: 4px solid #ef4444;
        border-radius: 8px;
        padding: 15px 20px;
        margin: 15px 0;
        color: #991b1b;
        font-weight: 500;
    }
    .section-header {
        font-size: 1.5rem;
        font-weight: 700;
        color: #1e293b;
        margin: 25px 0 15px 0;
        padding-bottom: 10px;
        border-bottom: 3px solid #667eea;
    }
    #MainMenu { visibility: hidden; }
    footer     { visibility: hidden; }
    header     { visibility: hidden; }
    </style>
    """
