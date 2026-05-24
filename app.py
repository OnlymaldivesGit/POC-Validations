"""
app.py — TMA Crew Scheduler & Validator — Streamlit entry point.

Responsibilities:
  - Configure the Streamlit page.
  - Inject shared CSS.
  - Render the sidebar navigation.
  - Initialise session state keys used across pages.
  - Route to the correct page module based on the menu selection.

No data processing, validation logic, or report generation lives here.
"""

import streamlit as st
from streamlit_option_menu import option_menu

from utils.styles import get_css
from pages import page_stats, page_input_validator, page_constraints

# ---------------------------------------------------------------------------
# Page config
# ---------------------------------------------------------------------------
st.set_page_config(
    page_title="TMA Crew Scheduler",
    page_icon="✈️",
    layout="wide",
    initial_sidebar_state="expanded",
)

st.markdown(get_css(), unsafe_allow_html=True)

# ---------------------------------------------------------------------------
# Session state initialisation
# ---------------------------------------------------------------------------
if "uploaded_data" not in st.session_state:
    st.session_state.uploaded_data = {}

# ---------------------------------------------------------------------------
# Sidebar
# ---------------------------------------------------------------------------
with st.sidebar:
    st.markdown(
        "<div style='text-align:center;padding:20px 0;margin-bottom:20px;'>"
        "<h1 style='color:#fff;font-size:2rem;'>✈️ TMA Crew</h1>"
        "<p style='color:#e2e8f0;'>Scheduler &amp; Validator</p></div>",
        unsafe_allow_html=True,
    )

    _NAV_STYLES = {
        "container": {"padding": "5px", "background-color": "#1e293b"},
        "icon": {"color": "#ffffff", "font-size": "22px"},
        "nav-link": {"font-size": "16px", "text-align": "left", "margin": "8px 0",
                     "padding": "16px 20px", "border-radius": "12px",
                     "color": "#ffffff !important", "background-color": "#334155",
                     "font-weight": "600"},
        "nav-link-selected": {"background-color": "#6366f1", "font-weight": "700",
                              "color": "#ffffff !important",
                              "box-shadow": "0 4px 15px rgba(99,102,241,0.5)"},
    }
    selected = option_menu(
        menu_title=None,
        options=["Crew Stats Generator", "Input Data Validator", "Constraints Validator"],
        icons=["graph-up", "clipboard-check", "shield-check"],
        menu_icon="cast", default_index=0, styles=_NAV_STYLES,
    )

    st.markdown("<br>", unsafe_allow_html=True)

    with st.expander("ℹ️ About", expanded=False):
        st.markdown("**Version:** 2.0 | **Updated:** Nov 2025  \nCrew scheduling validation system.")

    with st.expander("👨‍💻 Developer", expanded=False):
        st.markdown("**Himanshu Gupta** — Corporate Strategy  \n+960 7375336")

# ---------------------------------------------------------------------------
# Page routing
# ---------------------------------------------------------------------------
if selected == "Crew Stats Generator":
    page_stats.render()
elif selected == "Input Data Validator":
    page_input_validator.render()
elif selected == "Constraints Validator":
    page_constraints.render()
