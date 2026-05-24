"""
pages/page_stats.py — Page 1: Crew Stats Generator.

Renders the file-upload UI, triggers crew_stats_xml processing, displays
results, and provides the Excel download.  All business logic is delegated to
processing/input_processing.py and reporting/excel_report.py.
"""

import time
import streamlit as st

from config import CREWSTATS_OUTPUT_FILENAME
from processing.input_processing import crew_stats_xml
from reporting.excel_report import build_crewstats_excel

try:
    import pandas as pd
except ImportError:
    pass  # pandas is a project-level dependency


def render() -> None:
    """
    Rule: N/A
    Purpose: Render the Crew Stats Generator page: upload an .xlsm macro file,
             process it with crew_stats_xml(), display results, and offer a
             one-sheet Excel download.

    Args:
        None (reads from Streamlit widget state).

    Returns:
        None (renders directly into the Streamlit page).

    Known issues:
        None
    """
    st.markdown(
        """
        <div class="dashboard-header">
            <div class="dashboard-title">📊 Crew Stats Generator</div>
            <div class="dashboard-subtitle">Generate comprehensive crew statistics reports</div>
        </div>
        """,
        unsafe_allow_html=True,
    )

    col1, col2 = st.columns([2, 1])
    with col1:
        st.markdown('<div class="dashboard-card">', unsafe_allow_html=True)
        st.markdown("### 📁 Upload Crew Stats File")
        crewstats_xml = st.file_uploader(
            "Select crew stats macro (XLSM format)",
            type=["xlsm"],
            help="Upload the Excel macro-enabled file containing crew statistics",
        )
        st.markdown("</div>", unsafe_allow_html=True)

    with col2:
        st.markdown('<div class="dashboard-card">', unsafe_allow_html=True)
        st.markdown("### ℹ️ Instructions")
        st.markdown(
            "1. Upload the crew stats macro file\n"
            "2. Click 'Generate Report'\n"
            "3. Review the output\n"
            "4. Download the results"
        )
        st.markdown("</div>", unsafe_allow_html=True)

    if crewstats_xml is not None:
        st.markdown(
            '<div class="info-box">✅ File uploaded successfully!</div>',
            unsafe_allow_html=True,
        )

    col1, col2, col3 = st.columns([1, 1, 2])
    with col2:
        generate_btn = st.button(
            "🚀 Generate Report", use_container_width=True, type="primary"
        )

    if generate_btn:
        if crewstats_xml is None:
            st.markdown(
                '<div class="error-message">⚠️ Please upload a crew stats file first!</div>',
                unsafe_allow_html=True,
            )
            return

        with st.spinner("⚙️ Processing crew statistics..."):
            sectors  = pd.read_excel(crewstats_xml, engine="openpyxl", sheet_name="Sectors")
            flt      = pd.read_excel(crewstats_xml, engine="openpyxl", sheet_name="FLT")
            day_27th  = pd.read_excel(crewstats_xml, engine="openpyxl", sheet_name="27 Days")
            day_364th = pd.read_excel(crewstats_xml, engine="openpyxl", sheet_name="364 Days")
            crew_stats_output, _ = crew_stats_xml(sectors, flt, day_27th, day_364th)
            time.sleep(0.5)

        st.markdown(
            '<div class="success-message">✨ Report generated successfully!</div>',
            unsafe_allow_html=True,
        )

        col1, col2, col3 = st.columns(3)
        with col1:
            st.markdown(
                f'<div class="metric-card">'
                f'<div class="metric-label">Total Records</div>'
                f'<div class="metric-value">{len(crew_stats_output)}</div>'
                f"</div>",
                unsafe_allow_html=True,
            )
        with col2:
            st.markdown(
                '<div class="metric-card" style="background:linear-gradient(135deg,#10b981 0%,#059669 100%);">'
                '<div class="metric-label">Status</div>'
                '<div class="metric-value">✓</div>'
                "</div>",
                unsafe_allow_html=True,
            )

        st.markdown("<br>", unsafe_allow_html=True)
        st.markdown('<div class="dashboard-card">', unsafe_allow_html=True)
        st.markdown("### 📋 Crew stats reports")
        st.dataframe(crew_stats_output, use_container_width=True, height=400)
        st.markdown("</div>", unsafe_allow_html=True)

        output_bytes = build_crewstats_excel(crew_stats_output)
        col1, col2, col3 = st.columns([1, 1, 1])
        with col2:
            st.download_button(
                label="📥 Download crew stats report",
                data=output_bytes,
                file_name=CREWSTATS_OUTPUT_FILENAME,
                mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
                use_container_width=True,
            )
