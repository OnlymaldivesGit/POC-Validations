"""
pages/page_input_validator.py — Page 2: Input Data Validator.

Renders date selection and file upload/pre-load UI, runs the input completeness
checks (Rules I-1 and I-2), displays results in two tabs, and provides the
Excel download.
"""

from datetime import datetime, timedelta, date

import pandas as pd
import streamlit as st

from config import (
    PRELOADED_START_DATE,
    PRELOADED_END_DATE,
    MODEL_VALIDATIONS_DIR,
    FILE_IDENTIFIERS,
    INPUT_VALIDATION_FILENAME,
)
from processing.input_processing import (
    aircraft_processing,
    crew_aircraft_processing,
    crew_stats_processing,
    expiry_data_processing,
    flight_training_processing,
    logsheet_processing,
    merged_data_fun,
    month_plan_processing,
    new_crew_stats,
    seniority_processing,
    crew_master_processing,
)
from validation.input_validations import input_validation_fun
from reporting.excel_report import build_input_validation_excel


def _load_preloaded_files(schedule_date: str) -> dict:
    """
    Rule: N/A
    Purpose: Load all nine reference Excel files from MODEL_VALIDATIONS_DIR for
             dates within the pre-loaded range, bypassing the file-upload flow.

    Args:
        schedule_date: ISO date string (YYYY-MM-DD) within the pre-loaded range.

    Returns:
        dict mapping internal variable names to raw DataFrames, identical in
        structure to st.session_state.uploaded_data populated by the upload flow.

    Known issues:
        Crew Stats is read as a sheet named after schedule_date; if the sheet is
        absent an openpyxl exception is raised with no user-friendly message.
    """
    d = MODEL_VALIDATIONS_DIR
    return {
        "aircraft":         pd.read_excel(f"{d}Aircrafts.xlsx"),
        "crew_aircraft":    pd.read_excel(f"{d}Crew AC Matrix.xlsx"),
        "seniority":        pd.read_excel(f"{d}Crew Pairing.xlsx"),
        "logsheet":         pd.read_excel(f"{d}Log sheet.xlsx"),
        "crew_master":      pd.read_excel(f"{d}Resources.xlsx"),
        "expiry_data":      pd.read_excel(f"{d}Training Expiry.xlsx"),
        "flight_training":  pd.read_excel(f"{d}Training Pairings.xlsx"),
        "month_plan":       pd.read_excel(f"{d}Month plan.xlsx"),
        "crew_stats":       pd.read_excel(f"{d}Crew Stats.xlsx", sheet_name=schedule_date),
    }


def _identify_file_type(uploaded_file) -> str | None:
    """
    Rule: N/A
    Purpose: Match an uploaded file to an internal variable name by checking
             the filename and, if needed, the first Excel sheet name against
             FILE_IDENTIFIERS keywords.

    Args:
        uploaded_file: A Streamlit UploadedFile object.

    Returns:
        The internal variable name string (e.g. 'aircraft') if matched,
        or None if no keyword matched.

    Known issues:
        If two uploaded files match the same keyword the second silently
        overwrites the first in st.session_state.uploaded_data.
    """
    base_name = uploaded_file.name.rsplit(".", 1)[0]
    for identifier, var_name in FILE_IDENTIFIERS.items():
        if identifier.lower() in base_name.lower():
            return var_name
    try:
        excel_file = pd.ExcelFile(uploaded_file)
        sheet_name = excel_file.sheet_names[0] if excel_file.sheet_names else ""
        for identifier, var_name in FILE_IDENTIFIERS.items():
            if identifier.lower() in sheet_name.lower():
                return var_name
    except Exception:
        pass
    return None


def _render_upload_section() -> None:
    """
    Rule: N/A
    Purpose: Render the multi-file uploader, identify each file, store DataFrames
             into st.session_state.uploaded_data, and show upload status.

    Args:
        None (reads/writes st.session_state.uploaded_data).

    Returns:
        None (renders directly into the Streamlit page).

    Known issues:
        None
    """
    st.markdown('<div class="dashboard-card">', unsafe_allow_html=True)
    st.markdown("### 📤 Upload Required Files")
    uploaded_files = st.file_uploader(
        "Upload Excel Files (Multiple files supported)",
        type=["xlsx", "xls"],
        accept_multiple_files=True,
        key="multi_file_upload",
    )

    if uploaded_files:
        identified, unidentified = {}, []
        for f in uploaded_files:
            ftype = _identify_file_type(f)
            if ftype:
                df = pd.read_excel(f)
                identified[ftype] = {"dataframe": df, "filename": f.name}
                st.session_state.uploaded_data[ftype] = df
            else:
                unidentified.append(f.name)

        st.markdown("### Upload Status")
        if identified:
            st.success(f"✅ Successfully loaded {len(identified)} file(s):")
            for var_name, info in identified.items():
                st.write(f"- **{var_name}**: {info['filename']} ({len(info['dataframe'])} rows)")
        if unidentified:
            st.warning(f"⚠️ Could not identify {len(unidentified)} file(s):")
            for fn in unidentified:
                st.write(f"- {fn}")
            st.info("Please ensure filenames or sheet names match the expected format.")

        missing = set(FILE_IDENTIFIERS.values()) - set(identified.keys())
        if missing:
            st.info(f"📋 Still need: {', '.join(missing)}")

    st.markdown("</div>", unsafe_allow_html=True)


def render() -> None:
    """
    Rule: I-1, I-2
    Purpose: Render the full Input Data Validator page: date selection, file
             loading (pre-loaded or upload), validation checks, result display,
             and Excel download.

    Args:
        None (reads from Streamlit widget state and st.session_state).

    Returns:
        None (renders directly into the Streamlit page).

    Known issues:
        None
    """
    st.markdown(
        """
        <div class="dashboard-header">
            <div class="dashboard-title">🔍 Input Data Validator</div>
            <div class="dashboard-subtitle">Validate crew data integrity and completeness</div>
        </div>
        """,
        unsafe_allow_html=True,
    )

    # --- Date selection ---
    st.markdown('<div class="dashboard-card">', unsafe_allow_html=True)
    col1, col2, col3 = st.columns([1, 2, 1])
    with col2:
        st.markdown("### 📅 Schedule Date")
        schedule_date_obj = st.date_input(
            "Select the schedule date", help="Choose the date for validation"
        )
        schedule_date = schedule_date_obj.strftime("%Y-%m-%d")
    st.markdown("</div>", unsafe_allow_html=True)

    prev_day = (datetime.strptime(schedule_date, "%Y-%m-%d") - timedelta(days=1)).strftime("%Y-%m-%d")
    next_day = (datetime.strptime(schedule_date, "%Y-%m-%d") + timedelta(days=1)).strftime("%Y-%m-%d")

    # --- File loading ---
    if PRELOADED_START_DATE <= schedule_date <= PRELOADED_END_DATE:
        st.markdown(
            '<div class="info-box">📂 Using pre-loaded validation data</div>',
            unsafe_allow_html=True,
        )
        raw = _load_preloaded_files(schedule_date)
        # Apply new_crew_stats so the schema matches what crew_stats_processing expects
        raw["crew_stats"] = new_crew_stats(raw["crew_stats"])
        for k, v in raw.items():
            st.session_state.uploaded_data[k] = v
    else:
        _render_upload_section()
        # Apply new_crew_stats to uploaded crew_stats if present
        if st.session_state.uploaded_data.get("crew_stats") is not None:
            st.session_state.uploaded_data["crew_stats"] = new_crew_stats(
                st.session_state.uploaded_data["crew_stats"]
            )

    # --- Validate button ---
    col1, col2, col3 = st.columns([1, 1, 1])
    with col2:
        validate_btn = st.button("✅ Validate Data", use_container_width=True, type="primary")

    if not validate_btn:
        return

    data = st.session_state.uploaded_data

    with st.spinner("🔄 Processing data..."):
        aircraft_df      = aircraft_processing(data["aircraft"])
        crew_aircraft_df = crew_aircraft_processing(data["crew_aircraft"])
        seniority_df     = seniority_processing(data["seniority"])
        logsheet_df      = logsheet_processing(data["logsheet"], prev_day)
        crew_master_df   = crew_master_processing(data["crew_master"])
        expiry_df        = expiry_data_processing(data["expiry_data"])
        flight_training_df = flight_training_processing(data["flight_training"], schedule_date)
        month_plan_df    = month_plan_processing(data["month_plan"], schedule_date, prev_day, next_day)
        crew_stats_df    = crew_stats_processing(data["crew_stats"])
        merged_df        = merged_data_fun(
            month_plan_df, crew_master_df, seniority_df,
            expiry_df, logsheet_df, crew_stats_df,
        )
        input_issue_1, input_issue_2 = input_validation_fun(merged_df)

    st.markdown(
        '<div class="success-message">✨ Validation completed successfully!</div>',
        unsafe_allow_html=True,
    )

    # --- Metric cards ---
    col1, col2, col3 = st.columns(3)
    with col1:
        st.markdown(
            f'<div class="metric-card" style="background:linear-gradient(135deg,#f59e0b 0%,#d97706 100%);">'
            f'<div class="metric-label">Missing Resources</div>'
            f'<div class="metric-value">{len(input_issue_1)}</div></div>',
            unsafe_allow_html=True,
        )
    with col2:
        st.markdown(
            f'<div class="metric-card" style="background:linear-gradient(135deg,#ef4444 0%,#dc2626 100%);">'
            f'<div class="metric-label">Missing Stats</div>'
            f'<div class="metric-value">{len(input_issue_2)}</div></div>',
            unsafe_allow_html=True,
        )
    with col3:
        color = "#10b981" if not len(input_issue_1) and not len(input_issue_2) else "#ef4444"
        symbol = "✓" if not len(input_issue_1) and not len(input_issue_2) else "⚠"
        st.markdown(
            f'<div class="metric-card" style="background:linear-gradient(135deg,{color} 0%,{color} 100%);">'
            f'<div class="metric-label">Overall Status</div>'
            f'<div class="metric-value">{symbol}</div></div>',
            unsafe_allow_html=True,
        )

    st.markdown("<br>", unsafe_allow_html=True)

    # --- Result tabs ---
    tab1, tab2 = st.tabs(["🔍 Validation 1: Missing Resources", "🔍 Validation 2: Missing Stats"])
    with tab1:
        st.markdown('<div class="dashboard-card">', unsafe_allow_html=True)
        if input_issue_1.empty:
            st.markdown(
                '<div class="success-message">✅ No issues found - All crew resources are properly assigned!</div>',
                unsafe_allow_html=True,
            )
        else:
            st.markdown("### ⚠️ Crew with Missing Resources")
            st.info("The table below shows crew members with missing resource data except their stats")
            st.dataframe(input_issue_1, use_container_width=True, height=400)
        st.markdown("</div>", unsafe_allow_html=True)

    with tab2:
        st.markdown('<div class="dashboard-card">', unsafe_allow_html=True)
        if input_issue_2.empty:
            st.markdown(
                '<div class="success-message">✅ No issues found - All crew statistics are complete!</div>',
                unsafe_allow_html=True,
            )
        else:
            st.markdown("### ⚠️ Crew with Missing Statistics")
            st.info("The table below shows crew members with missing statistical data")
            st.dataframe(input_issue_2, use_container_width=True, height=400)
        st.markdown("</div>", unsafe_allow_html=True)

    # --- Download ---
    output_bytes = build_input_validation_excel(input_issue_1, input_issue_2, merged_df)
    col1, col2, col3 = st.columns([1, 1, 1])
    with col2:
        st.download_button(
            label="📥 Download Validation Report",
            data=output_bytes,
            file_name=INPUT_VALIDATION_FILENAME,
            mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
            use_container_width=True,
        )
