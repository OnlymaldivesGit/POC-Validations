"""
pages/page_constraints.py — Page 3: Constraints Validator.

Renders date selection, file loading, solver output upload, runs the full
constraint validation pipeline (Rules C-1 through C-19), displays results,
and provides Excel and HTML report downloads.
"""

import time
from datetime import datetime, timedelta, date

import pandas as pd
import streamlit as st
import plotly.express as px

from config import (
    AVAILABLE_STATUS,
    LEAVE_STATUS,
    PRELOADED_START_DATE,
    PRELOADED_END_DATE,
    MODEL_VALIDATIONS_DIR,
    FILE_IDENTIFIERS,
    CONSTRAINTS_REPORT_FILENAME,
    HTML_REPORT_FILENAME,
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
    schedule_input_processing,
)
from processing.output_processing import (
    Schedule_output_processing,
    Schedule_output_processing_2,
    output_master_processing,
    crew_ac_stats_processing,
    overnight_flights,
)
from validation.checklist import (
    Schedule_check_fun,
    unassigned_flights,
    crew_check_fun,
    aircraft_check,
    Stats_check_fun,
    swaps_check_fun,
    get_short_time_diffs,
    seniority_check_fun,
    training_pairing_check,
)
from reporting.html_report_generator import generate_html_report
from reporting.excel_report import build_constraints_excel
from utils.clustering import cluster_fun


def _load_preloaded_files(schedule_date: str) -> dict:
    d = MODEL_VALIDATIONS_DIR
    raw_crew_stats = pd.read_excel(f"{d}Crew Stats.xlsx", sheet_name=schedule_date)
    return {
        "aircraft":         pd.read_excel(f"{d}Aircrafts.xlsx"),
        "crew_aircraft":    pd.read_excel(f"{d}Crew AC Matrix.xlsx"),
        "seniority":        pd.read_excel(f"{d}Crew Pairing.xlsx"),
        "logsheet":         pd.read_excel(f"{d}Log sheet.xlsx"),
        "crew_master":      pd.read_excel(f"{d}Resources.xlsx"),
        "expiry_data":      pd.read_excel(f"{d}Training Expiry.xlsx"),
        "flight_training":  pd.read_excel(f"{d}Training Pairings.xlsx"),
        "month_plan":       pd.read_excel(f"{d}Month plan.xlsx"),
        "crew_stats":       new_crew_stats(raw_crew_stats),
        "input_flight_plan": pd.read_excel(f"{d}Flight Plan.xlsx"),
    }


def _identify_file_type(uploaded_file) -> str | None:
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
    st.markdown('<div class="dashboard-card">', unsafe_allow_html=True)
    st.markdown("### 📤 Upload Required Files")
    uploaded_files = st.file_uploader(
        "Upload Excel Files (Multiple files supported)",
        type=["xlsx", "xls"],
        accept_multiple_files=True,
        key="constraints_multi_file_upload",
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

        if st.session_state.uploaded_data.get("crew_stats") is not None:
            st.session_state.uploaded_data["crew_stats"] = new_crew_stats(
                st.session_state.uploaded_data["crew_stats"]
            )

    st.markdown("</div>", unsafe_allow_html=True)


def _create_top_performers_charts(df_all, df_cap, df_fo, df_fa):
    TOP_N = 300
    crew_categories = {
        "All Crew": df_all,
        "Captains": df_cap,
        "First Officers": df_fo,
        "Flight Attendants": df_fa,
    }
    metrics = {
        "Block hours": {"column": "Block hours", "title_suffix": "Block Hours", "y_label": "Block Hours"},
        "Sectors":     {"column": "Total sectors", "title_suffix": "Total sectors", "y_label": "Number of Total sectors"},
    }

    for metric_name, metric_config in metrics.items():
        st.subheader(f"Top Crew by {metric_config['title_suffix']}")
        cols = st.columns(4)
        for idx, (category_name, df) in enumerate(crew_categories.items()):
            df_clean = df.copy()
            df_clean[metric_config["column"]] = pd.to_numeric(df_clean[metric_config["column"]], errors="coerce")
            df_clean = df_clean.dropna(subset=[metric_config["column"]])
            df_clean = df_clean.sort_values(metric_config["column"], ascending=False).reset_index(drop=True)
            top_performers = df_clean.head(TOP_N).copy()
            top_performers["Rank"] = range(1, len(top_performers) + 1)
            top_performers["Display_Label"] = top_performers["Rank"].astype(str) + ". " + top_performers["Crew code"]

            fig = px.bar(
                top_performers,
                x="Display_Label",
                y=metric_config["column"],
                title=category_name,
                labels={"Display_Label": "Crew Code (Ranked)", metric_config["column"]: metric_config["y_label"]},
                hover_data={"Display_Label": False, "Crew code": True, metric_config["column"]: True, "Rank": True},
                color_discrete_sequence=["#1f77b4"],
            )
            fig.update_layout(xaxis_tickangle=-45, height=400, margin=dict(l=20, r=20, t=40, b=20), showlegend=False)
            if len(top_performers) > 50:
                fig.update_xaxes(tickmode="linear", tick0=0, dtick=10)
            with cols[idx]:
                st.plotly_chart(fig, use_container_width=True)
        st.markdown("---")


def render() -> None:
    """
    Rule: C-1 through C-19
    Purpose: Render the Constraints Validator page: date selection, multi-file
             upload or pre-load, solver output upload, full validation pipeline,
             KPI display, violation expanders, clustering, and report downloads.
    """
    st.markdown(
        """
        <div class="dashboard-header">
            <div class="dashboard-title">🛡️ Constraints Validator</div>
            <div class="dashboard-subtitle">Validate scheduling constraints and regulations</div>
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
            "Select the schedule date", help="Choose the date for validation", key="constraints_date"
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
        for k, v in raw.items():
            st.session_state.uploaded_data[k] = v
    else:
        _render_upload_section()

    # --- Solver output uploader ---
    st.markdown('<div class="dashboard-card">', unsafe_allow_html=True)
    st.markdown("### 📤 Upload Crew Schedule")
    col1, col2 = st.columns(2)
    with col1:
        output_flight_plan = st.file_uploader("Solver Output", type=["xlsx", "xls"], key="output_plan")
    st.markdown("</div>", unsafe_allow_html=True)

    Schedule_output = None
    if output_flight_plan is not None:
        Schedule_output = pd.read_excel(output_flight_plan)

    # --- Validate button ---
    col1, col2, col3 = st.columns([1, 1, 1])
    with col2:
        validate_constraints_btn = st.button(
            "🛡️ Validate Constraints", use_container_width=True, type="primary"
        )

    if not validate_constraints_btn:
        return

    data = st.session_state.uploaded_data

    progress_bar = st.progress(0)
    status_text = st.empty()

    status_text.text("🔄 Processing aircraft data...")
    progress_bar.progress(10)
    aircraft_df = aircraft_processing(data["aircraft"])

    status_text.text("🔄 Processing crew aircraft matrix...")
    progress_bar.progress(20)
    crew_aircraft_df = crew_aircraft_processing(data["crew_aircraft"])

    status_text.text("🔄 Processing seniority data...")
    progress_bar.progress(30)
    seniority_df = seniority_processing(data["seniority"])

    status_text.text("🔄 Processing logsheet...")
    progress_bar.progress(40)
    logsheet_df = logsheet_processing(data["logsheet"], prev_day)
    crew_master_df = crew_master_processing(data["crew_master"])

    status_text.text("🔄 Processing training data...")
    progress_bar.progress(50)
    expiry_df = expiry_data_processing(data["expiry_data"])
    flight_training_df = flight_training_processing(data["flight_training"], schedule_date)

    status_text.text("🔄 Processing schedules...")
    progress_bar.progress(60)
    month_plan_df = month_plan_processing(data["month_plan"], schedule_date, prev_day, next_day)
    crew_stats_df = crew_stats_processing(data["crew_stats"])
    Schedule_input = schedule_input_processing(data["input_flight_plan"])

    status_text.text("🔄 Merging data...")
    progress_bar.progress(70)
    merged_df = merged_data_fun(
        month_plan_df, crew_master_df, seniority_df, expiry_df, logsheet_df, crew_stats_df
    )

    status_text.text("🔄 Processing outputs...")
    progress_bar.progress(80)
    Schedule_output = Schedule_output_processing(Schedule_output)
    Schedule_output_2 = Schedule_output_processing_2(Schedule_output)
    output_master, output_crew_stats = output_master_processing(Schedule_output_2)

    status_text.text("🔄 Running validations...")
    progress_bar.progress(90)
    crew_ac_stats = crew_ac_stats_processing(Schedule_output_2, aircraft_df, crew_aircraft_df)
    comparison_master = merged_df.merge(output_master, on="Crew code", how="outer")

    available_working = comparison_master[
        (comparison_master["Schedule Day"].isin(AVAILABLE_STATUS))
        & (~comparison_master["Working Status"].isna())
    ]
    Standby_crew = comparison_master[
        (comparison_master["Schedule Day"].isin(AVAILABLE_STATUS))
        & (comparison_master["Working Status"].isna())
    ]
    leaves_working = comparison_master[
        (comparison_master["Schedule Day"].isin(LEAVE_STATUS))
        & (~comparison_master["Working Status"].isna())
    ]
    on_training = comparison_master[
        ~(comparison_master["Schedule Day"].isin(LEAVE_STATUS + AVAILABLE_STATUS))
    ]

    unassigned_flights_crew = unassigned_flights(Schedule_output)
    Schedule_check = Schedule_check_fun(Schedule_output, Schedule_input)
    crew_mistake_1, crew_mistake_11, crew_mistake_2, crew_mistake_3 = crew_check_fun(
        comparison_master, available_working
    )
    aircraft_issue = aircraft_check(crew_ac_stats)
    Block_hour_issue_1, Block_hour_issue_2, duty_hour_issue, sector_issue_1, sector_issue_2 = Stats_check_fun(
        available_working
    )
    swaps_issue = swaps_check_fun(output_master)
    pairings_issue_1, LTC_check = seniority_check_fun(Schedule_output, merged_df)
    training_issue = training_pairing_check(flight_training_df, Schedule_output)
    get_short_time_diffs_df = get_short_time_diffs(crew_ac_stats)
    output_df_kpi = overnight_flights(Schedule_output)

    complete_scheduled = Schedule_output[
        (Schedule_output["Captain"].notna())
        & (Schedule_output["Captain"].str.strip() != "")
        & (Schedule_output["First Officer"].notna())
        & (Schedule_output["First Officer"].str.strip() != "")
        & (Schedule_output["Flight Attendant"].notna())
        & (Schedule_output["Flight Attendant"].str.strip() != "")
    ]

    aircraft_kpi = Schedule_output["Aircraft No."].nunique()
    flight_kpi = Schedule_output["Flight No."].nunique()
    sectors_kpi = len(complete_scheduled)
    aircraft_starting_on_kpi = len(
        output_df_kpi[(output_df_kpi["Sector Position"] == "Starting") & (output_df_kpi["ON"] == 1)]
    )
    aircraft_ending_on_kpi = len(
        output_df_kpi[(output_df_kpi["Sector Position"] == "Ending") & (output_df_kpi["ON"] == 1)]
    )
    utilized_captain = Schedule_output["Captain"].nunique()
    utilized_first_officer = Schedule_output["First Officer"].nunique()
    utilized_flight_attendant = Schedule_output["Flight Attendant"].nunique()
    Standyby_captain = len(Standby_crew[Standby_crew["Crew Type_x"] == "Captain"])
    Standyby_first_officer = len(Standby_crew[Standby_crew["Crew Type_x"] == "First Officer"])
    Standyby_flight_attendant = len(Standby_crew[Standby_crew["Crew Type_x"] == "Flight Attendant"])
    aircraft_input_kpi = Schedule_input["Aircraft No."].nunique()
    flight_input_kpi = Schedule_input["Flight No."].nunique()
    sectors_input_kpi = len(Schedule_input)

    test = merged_df[merged_df["Schedule Day"].isin(AVAILABLE_STATUS)]
    available_captain = len(test[test["Crew Type"] == "Captain"])
    available_first_officer = len(test[test["Crew Type"] == "First Officer"])
    available_flight_attendant = len(test[test["Crew Type"] == "Flight Attendant"])

    progress_bar.progress(100)
    status_text.text("✅ Validation complete!")
    time.sleep(0.5)
    progress_bar.empty()
    status_text.empty()

    st.markdown(
        '<div class="success-message">✨ All constraints validated successfully!</div>',
        unsafe_allow_html=True,
    )

    # --- Summary metrics ---
    st.markdown("### 📊 Validation Summary")
    col1, col2, col3, col4, col5, col6, col7, col8 = st.columns(8)

    def _kpi_card(label, count):
        color = "#ef4444" if count > 0 else "#10b981"
        return (
            f'<div class="metric-card" style="background:linear-gradient(135deg,{color} 0%,{color} 100%);">'
            f'<div class="metric-label">{label}</div>'
            f'<div class="metric-value">{count}</div></div>'
        )

    with col1:
        st.markdown(_kpi_card("Schedule Issues", len(Schedule_check) + len(unassigned_flights_crew)), unsafe_allow_html=True)
    with col2:
        st.markdown(_kpi_card("BH violations", len(Block_hour_issue_1) + len(Block_hour_issue_2)), unsafe_allow_html=True)
    with col3:
        st.markdown(_kpi_card("DH violations", len(duty_hour_issue)), unsafe_allow_html=True)
    with col4:
        daily_sector_violation = output_crew_stats[output_crew_stats["Total sectors"] > 14]
        st.markdown(_kpi_card("Sectors violations", len(daily_sector_violation) + len(sector_issue_1) + len(sector_issue_2)), unsafe_allow_html=True)
    with col5:
        st.markdown(_kpi_card("Pairing Issues", len(pairings_issue_1) + len(LTC_check) + len(training_issue)), unsafe_allow_html=True)
    with col6:
        st.markdown(_kpi_card("Status Issues", len(leaves_working) + len(crew_mistake_1) + len(crew_mistake_11)), unsafe_allow_html=True)
    with col7:
        st.markdown(_kpi_card("Overnight Issues", len(crew_mistake_2) + len(crew_mistake_3)), unsafe_allow_html=True)
    with col8:
        st.markdown(_kpi_card("Aircraft Issues", len(aircraft_issue) + len(swaps_issue)), unsafe_allow_html=True)

    st.markdown("<br>", unsafe_allow_html=True)

    # --- Violation expanders ---
    with st.expander("🔍 Standby Crew", expanded=False):
        if Standby_crew.empty:
            st.markdown('<div class="success-message">✅ All crew have been utilized</div>', unsafe_allow_html=True)
        else:
            st.dataframe(Standby_crew, use_container_width=True)
            st.info("Following crew has been kept for standby for the full day")

    with st.expander("✈️ Unassigned Flights", expanded=False):
        if unassigned_flights_crew.empty:
            st.markdown('<div class="success-message">✅ All flights have been assigned</div>', unsafe_allow_html=True)
        else:
            st.dataframe(unassigned_flights_crew, use_container_width=True)
            st.warning("Following flights have one or more missing crew")

    with st.expander("📋 Schedule Check", expanded=False):
        if Schedule_check.empty:
            st.markdown('<div class="success-message">✅ No errors in schedule</div>', unsafe_allow_html=True)
        else:
            st.dataframe(Schedule_check, use_container_width=True)
            st.warning("The table above shows sectors, flights, and aircraft that have been modified in the output")

    with st.expander("⚠️ Non-Available Crew Check", expanded=False):
        if leaves_working.empty:
            st.markdown('<div class="success-message">✅ No crew on leave is being scheduled</div>', unsafe_allow_html=True)
        else:
            st.dataframe(leaves_working[["Crew code", "Schedule Day", "Working Status"]], use_container_width=True)
            st.error("Crew members on leave have been allocated to flights")

    with st.expander("🎓 Error in crew on Training", expanded=False):
        col1, col2 = st.columns(2)
        with col1:
            if crew_mistake_1.empty:
                st.markdown('<div class="success-message">✅ No errors with crew on training at base</div>', unsafe_allow_html=True)
            else:
                st.dataframe(crew_mistake_1, use_container_width=True)
                st.error("Crew on training at base have been scheduled to flights")
        with col2:
            if crew_mistake_11.empty:
                st.markdown('<div class="success-message">✅ No errors with crew on training at outstation</div>', unsafe_allow_html=True)
            else:
                st.dataframe(crew_mistake_11, use_container_width=True)
                st.error("Crew on training at outstation don't have 1 flight")

    with st.expander("📍 Starting Point Errors", expanded=False):
        if crew_mistake_2.empty:
            st.markdown('<div class="success-message">✅ No errors in crew starting points</div>', unsafe_allow_html=True)
        else:
            st.dataframe(crew_mistake_2, use_container_width=True)
            st.error("Crew with mismatched starting points detected")

    with st.expander("🌙 Next day Overnight Assignment Errors", expanded=False):
        if crew_mistake_3.empty:
            st.markdown('<div class="success-message">✅ No errors with overnight assignments</div>', unsafe_allow_html=True)
        else:
            st.dataframe(crew_mistake_3, use_container_width=True)
            st.error("Crew incorrectly assigned for overnights")

    with st.expander("✈️ Aircraft Eligibility Errors", expanded=False):
        if aircraft_issue.empty:
            st.markdown('<div class="success-message">✅ No aircraft assignment errors</div>', unsafe_allow_html=True)
        else:
            st.dataframe(aircraft_issue, use_container_width=True)
            st.error("Crew assigned to ineligible aircraft")

    with st.expander("⏰ Block Hour Violations", expanded=False):
        col1, col2 = st.columns(2)
        with col1:
            st.markdown("**Crew ending at MLE:**")
            if Block_hour_issue_1.empty:
                st.markdown('<div class="success-message">✅ No violations</div>', unsafe_allow_html=True)
            else:
                st.dataframe(Block_hour_issue_1, use_container_width=True)
                st.error("Block hour limit violations detected")
        with col2:
            st.markdown("**Crew ending at outstation:**")
            if Block_hour_issue_2.empty:
                st.markdown('<div class="success-message">✅ No violations</div>', unsafe_allow_html=True)
            else:
                st.dataframe(Block_hour_issue_2, use_container_width=True)
                st.error("Block hour limit violations detected")

    with st.expander("📅 Monthly Duty Hour Violations", expanded=False):
        if duty_hour_issue.empty:
            st.markdown('<div class="success-message">✅ No duty hour violations</div>', unsafe_allow_html=True)
        else:
            st.dataframe(duty_hour_issue, use_container_width=True)
            st.error("Crew have exceeded duty hour limits")

    with st.expander("🔢 Sector Violations", expanded=False):
        if daily_sector_violation.empty:
            st.markdown('<div class="success-message">✅ No daily sector violations</div>', unsafe_allow_html=True)
        else:
            st.dataframe(daily_sector_violation, use_container_width=True)
            st.error("Crew have exceeded the daily sector limit of 14")
        if sector_issue_1.empty:
            st.markdown('<div class="success-message">✅ No weekly sector violations</div>', unsafe_allow_html=True)
        else:
            st.dataframe(sector_issue_1, use_container_width=True)
            st.error("Crew have exceeded the weekly sector limit of 48")
        if sector_issue_2.empty:
            st.markdown('<div class="success-message">✅ No violations of >12 sector rule</div>', unsafe_allow_html=True)
        else:
            st.dataframe(sector_issue_2, use_container_width=True)
            st.error("Crew have exceeded 12 sectors more than twice")

    with st.expander("🔄 Aircraft Swap Violations", expanded=False):
        if swaps_issue.empty:
            st.markdown('<div class="success-message">✅ No swap count violations</div>', unsafe_allow_html=True)
        else:
            st.dataframe(swaps_issue, use_container_width=True)
            st.error("Crew have exceeded the aircraft swap limit of 1")
        if get_short_time_diffs_df.empty:
            st.markdown('<div class="success-message">✅ No time difference violations</div>', unsafe_allow_html=True)
        else:
            st.dataframe(get_short_time_diffs_df, use_container_width=True)
            st.error("Aircraft swaps with less than 45 minutes detected")

    with st.expander("👥 Pairing Rule Violations", expanded=False):
        if pairings_issue_1.empty:
            st.markdown('<div class="success-message">✅ No senior-junior pairing violations</div>', unsafe_allow_html=True)
        else:
            st.dataframe(pairings_issue_1, use_container_width=True)
            st.error("Senior-junior pairing rules violated")
        if LTC_check.empty:
            st.markdown('<div class="success-message">✅ No LTC pairing violations</div>', unsafe_allow_html=True)
        else:
            st.dataframe(LTC_check, use_container_width=True)
            st.error("LTC trainee pairing rules violated")
        if training_issue.empty:
            st.markdown('<div class="success-message">✅ No training pairing violations</div>', unsafe_allow_html=True)
        else:
            st.dataframe(training_issue, use_container_width=True)
            st.error("Training pairing rules violated")

    # --- Build validation_report_1 ---
    validation_report_1 = comparison_master.copy()
    validation_report_1 = validation_report_1[validation_report_1["Working Status"] == 1]
    validation_report_1 = validation_report_1[[
        "Crew code", "Crew name", "Crew Type_x", "Seniority Level", "Is Instructor?",
        "Prev Day", "Schedule Day", "Next Day", "Expiry status", "Outstation airport",
        "Outstation Aircraft", "Max BH left", "Max BH left ON", "Max DH left",
        "Max sectors left", "Max more than 12 sectors", "Starting from", "Ending at",
        "Total flights", "Total aircrafts", "Duty hours", "Total sectors",
        "Block hours", "No. of swaps",
    ]]
    validation_report_1.columns = [
        "Crew code", "Crew Name", "Crew Type", "Seniority Level", "Is Instructor?",
        "Prev Day status", "Schedule Day status", "Next Day status", "Expiry status",
        "Prev day airport", "Prev day aircraft", "Max BH left", "Max BH left ON",
        "Max DH left", "Max sectors left", "Max more than 12 sectors",
        "Starting from", "Ending at", "Total flights", "Total aircrafts",
        "Total duty hours", "Total sectors", "Block hours", "No. of swaps",
    ]

    Crew_swaps_violation = validation_report_1[validation_report_1["No. of swaps"] > 1]

    df_validation = validation_report_1[[
        "Crew code", "Crew Type", "Seniority Level", "Max BH left", "Max BH left ON",
        "Max DH left", "Max sectors left", "Max more than 12 sectors", "Starting from",
        "Ending at", "Total flights", "Total aircrafts", "Total duty hours",
        "Total sectors", "Block hours", "No. of swaps",
    ]].copy()
    df_validation_captain = df_validation[df_validation["Crew Type"] == "Captain"]
    df_validation_FO = df_validation[df_validation["Crew Type"] == "First Officer"]
    df_validation_FA = df_validation[df_validation["Crew Type"] == "Flight Attendant"]

    # --- Metrics DataFrame ---
    metrics_df = pd.DataFrame({
        "Parameter": [
            "Total Aircraft in Schedule", "Total Flight in Schedule", "Total sectors in Schedule",
            "Total Available Crew in Month Plan", "Available Captains in Month Plan",
            "Available First Officers in Month Plan", "Available Cabin crew in Month Plan",
            "Total Aircraft Scheduled", "Aircraft Scheduled Starting ON", "Aircraft Scheduled Ending ON",
            "Total Flights Scheduled", "Total Sectors Scheduled",
            "Utilized Crew", "Utilized Captain", "Utilized First Officer", "Utilized Flight Attendant",
            "Total Standby crew", "Standby Captain", "Standby First Officer", "Standby Flight Attendant",
            "Total Swap percentage", "Captain Swap percentage",
            "First Officer Swap percentage", "Flight Attendant Swap percentage",
        ],
        "Value": [
            aircraft_input_kpi, flight_input_kpi, sectors_input_kpi,
            available_captain + available_first_officer + available_flight_attendant,
            available_captain, available_first_officer, available_flight_attendant,
            aircraft_kpi, aircraft_starting_on_kpi, aircraft_ending_on_kpi,
            flight_kpi, sectors_kpi,
            utilized_captain + utilized_first_officer + utilized_flight_attendant,
            utilized_captain, utilized_first_officer, utilized_flight_attendant,
            Standyby_captain + Standyby_first_officer + Standyby_flight_attendant,
            Standyby_captain, Standyby_first_officer, Standyby_flight_attendant,
            (df_validation["No. of swaps"] > 0).sum() / len(df_validation) * 100,
            (df_validation_captain["No. of swaps"] > 0).sum() / len(df_validation_captain) * 100,
            (df_validation_FO["No. of swaps"] > 0).sum() / len(df_validation_FO) * 100,
            (df_validation_FA["No. of swaps"] > 0).sum() / len(df_validation_FA) * 100,
        ],
    })

    # --- Excel download (build before charts since the button appears after) ---
    output_bytes = build_constraints_excel(
        Schedule_check=Schedule_check,
        crew_mistake_1=crew_mistake_1,
        crew_mistake_11=crew_mistake_11,
        crew_mistake_2=crew_mistake_2,
        crew_mistake_3=crew_mistake_3,
        aircraft_issue=aircraft_issue,
        Block_hour_issue_1=Block_hour_issue_1,
        Block_hour_issue_2=Block_hour_issue_2,
        duty_hour_issue=duty_hour_issue,
        sector_issue_1=sector_issue_1,
        sector_issue_2=sector_issue_2,
        swaps_issue=swaps_issue,
        get_short_time_diffs_df=get_short_time_diffs_df,
        pairings_issue_1=pairings_issue_1,
        LTC_check=LTC_check,
        training_issue=training_issue,
        Crew_swaps_violation=Crew_swaps_violation,
        comparison_master=comparison_master,
        output_master=output_master,
        validation_report_1=validation_report_1,
        crew_ac_stats=crew_ac_stats,
        metrics_df=metrics_df,
    )

    # --- KPI section ---
    st.markdown('<div class="section-header">📊 Key Performance Indicators</div>', unsafe_allow_html=True)
    st.markdown('<div class="dashboard-card">', unsafe_allow_html=True)
    st.subheader("Available Aircraft and Crew")

    col1, col2, col3, gap1, col4, col5, col6, col7 = st.columns([1, 1, 1, 0.3, 1, 1, 1, 1])
    with col1:
        st.markdown(f'<div class="metric-card"><div class="metric-label">Total Aircraft</div><div class="metric-value">{aircraft_input_kpi}</div></div>', unsafe_allow_html=True)
    with col2:
        st.markdown(f'<div class="metric-card"><div class="metric-label">Total Flight</div><div class="metric-value">{flight_input_kpi}</div></div>', unsafe_allow_html=True)
    with col3:
        st.markdown(f'<div class="metric-card"><div class="metric-label">Total sectors</div><div class="metric-value">{sectors_input_kpi}</div></div>', unsafe_allow_html=True)
    with gap1:
        st.markdown('<div style="border-left:3px solid rgba(255,255,255,0.3);height:100px;margin:0 auto;"></div>', unsafe_allow_html=True)
    total_crew_avail = available_captain + available_first_officer + available_flight_attendant
    with col4:
        st.markdown(f'<div class="metric-card" style="background:linear-gradient(135deg,#10b981 0%,#059669 100%);"><div class="metric-label">Total Available Crew</div><div class="metric-value">{total_crew_avail}</div></div>', unsafe_allow_html=True)
    with col5:
        st.markdown(f'<div class="metric-card" style="background:linear-gradient(135deg,#10b981 0%,#059669 100%);"><div class="metric-label">Available Captains</div><div class="metric-value">{available_captain}</div></div>', unsafe_allow_html=True)
    with col6:
        st.markdown(f'<div class="metric-card" style="background:linear-gradient(135deg,#10b981 0%,#059669 100%);"><div class="metric-label">Available First Officers</div><div class="metric-value">{available_first_officer}</div></div>', unsafe_allow_html=True)
    with col7:
        st.markdown(f'<div class="metric-card" style="background:linear-gradient(135deg,#10b981 0%,#059669 100%);"><div class="metric-label">Available Cabin crew</div><div class="metric-value">{available_flight_attendant}</div></div>', unsafe_allow_html=True)
    st.markdown("</div>", unsafe_allow_html=True)

    st.subheader("")
    st.subheader("Scheduled Aircraft and Crew")
    col1, col2, col3, col12, col13, gap1, col4, col5, col6, col7, gap2, col8, col9, col10, col11 = st.columns([1, 1, 1, 1, 1, 0.3, 1, 1, 1, 1, 0.3, 1, 1, 1, 1])
    with col1:
        st.markdown(f'<div class="metric-card"><div class="metric-label">Total AC</div><div class="metric-value">{aircraft_kpi}</div></div>', unsafe_allow_html=True)
    with col12:
        st.markdown(f'<div class="metric-card"><div class="metric-label">AC Starting ON</div><div class="metric-value">{aircraft_starting_on_kpi}</div></div>', unsafe_allow_html=True)
    with col13:
        st.markdown(f'<div class="metric-card"><div class="metric-label">AC Ending ON</div><div class="metric-value">{aircraft_ending_on_kpi}</div></div>', unsafe_allow_html=True)
    with col2:
        st.markdown(f'<div class="metric-card"><div class="metric-label">Total Flights</div><div class="metric-value">{flight_kpi}</div></div>', unsafe_allow_html=True)
    with col3:
        st.markdown(f'<div class="metric-card"><div class="metric-label">Total Sectors</div><div class="metric-value">{sectors_kpi}</div></div>', unsafe_allow_html=True)
    with gap1:
        st.markdown('<div style="border-left:3px solid rgba(255,255,255,0.3);height:100px;margin:0 auto;"></div>', unsafe_allow_html=True)
    total_utilized = utilized_captain + utilized_first_officer + utilized_flight_attendant
    with col4:
        st.markdown(f'<div class="metric-card" style="background:linear-gradient(135deg,#10b981 0%,#059669 100%);"><div class="metric-label">Utilized Crew</div><div class="metric-value">{total_utilized}</div></div>', unsafe_allow_html=True)
    with col5:
        st.markdown(f'<div class="metric-card" style="background:linear-gradient(135deg,#10b981 0%,#059669 100%);"><div class="metric-label">Utilized Cap</div><div class="metric-value">{utilized_captain}</div></div>', unsafe_allow_html=True)
    with col6:
        st.markdown(f'<div class="metric-card" style="background:linear-gradient(135deg,#10b981 0%,#059669 100%);"><div class="metric-label">Utilized FO</div><div class="metric-value">{utilized_first_officer}</div></div>', unsafe_allow_html=True)
    with col7:
        st.markdown(f'<div class="metric-card" style="background:linear-gradient(135deg,#10b981 0%,#059669 100%);"><div class="metric-label">Utilized FA</div><div class="metric-value">{utilized_flight_attendant}</div></div>', unsafe_allow_html=True)
    with gap2:
        st.markdown('<div style="border-left:3px solid rgba(255,255,255,0.3);height:100px;margin:0 auto;"></div>', unsafe_allow_html=True)
    total_standby = Standyby_captain + Standyby_first_officer + Standyby_flight_attendant
    with col8:
        st.markdown(f'<div class="metric-card" style="background:linear-gradient(135deg,#f59e0b 0%,#d97706 100%);"><div class="metric-label">Total Standby</div><div class="metric-value">{total_standby}</div></div>', unsafe_allow_html=True)
    with col9:
        st.markdown(f'<div class="metric-card" style="background:linear-gradient(135deg,#f59e0b 0%,#d97706 100%);"><div class="metric-label">Standby Cap</div><div class="metric-value">{Standyby_captain}</div></div>', unsafe_allow_html=True)
    with col10:
        st.markdown(f'<div class="metric-card" style="background:linear-gradient(135deg,#f59e0b 0%,#d97706 100%);"><div class="metric-label">Standby FO</div><div class="metric-value">{Standyby_first_officer}</div></div>', unsafe_allow_html=True)
    with col11:
        st.markdown(f'<div class="metric-card" style="background:linear-gradient(135deg,#f59e0b 0%,#d97706 100%);"><div class="metric-label">Standby FA</div><div class="metric-value">{Standyby_flight_attendant}</div></div>', unsafe_allow_html=True)
    st.markdown("</div>", unsafe_allow_html=True)

    st.subheader("")
    st.markdown('<div class="dashboard-card">', unsafe_allow_html=True)

    _create_top_performers_charts(df_validation, df_validation_captain, df_validation_FO, df_validation_FA)

    col1, col2, col3, col4 = st.columns(4)
    with col1:
        fig_pie1 = px.pie(df_validation, names="No. of swaps", title="Crew swaps", hole=0.3)
        st.plotly_chart(fig_pie1, use_container_width=True)
    with col2:
        fig_pie2 = px.pie(df_validation_captain, names="No. of swaps", title="Captains swaps", hole=0.3)
        st.plotly_chart(fig_pie2, use_container_width=True)
    with col3:
        fig_pie3 = px.pie(df_validation_FO, names="No. of swaps", title="First officer swaps", hole=0.3)
        st.plotly_chart(fig_pie3, use_container_width=True)
    with col4:
        fig_pie4 = px.pie(df_validation_FA, names="No. of swaps", title="Flight Attendant swaps", hole=0.3)
        st.plotly_chart(fig_pie4, use_container_width=True)

    st.markdown("</div>", unsafe_allow_html=True)

    # --- Clustering ---
    st.markdown('<div class="section-header">📊 Common Profile Crews</div>', unsafe_allow_html=True)
    st.markdown('<div class="dashboard-card">', unsafe_allow_html=True)
    crew_groups = validation_report_1.merge(crew_aircraft_df, on="Crew code")
    df_grouped = cluster_fun(crew_groups)
    st.dataframe(df_grouped)
    st.markdown("</div>", unsafe_allow_html=True)

    # --- Download buttons ---
    col1, col2, col3 = st.columns([1, 1, 1])
    with col2:
        st.download_button(
            label="📥 Download Full Validation Report",
            data=output_bytes,
            file_name=CONSTRAINTS_REPORT_FILENAME.format(date=schedule_date),
            mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
            use_container_width=True,
        )

    html_report = generate_html_report(
        schedule_date=schedule_date,
        metrics_df=metrics_df,
        validation_report_1=validation_report_1,
        crew_ac_stats=crew_ac_stats,
        Schedule_check=Schedule_check,
        unassigned_flights_crew=unassigned_flights_crew,
        Standby_crew=Standby_crew,
        leaves_working=leaves_working,
        crew_mistake_1=crew_mistake_1,
        crew_mistake_11=crew_mistake_11,
        crew_mistake_2=crew_mistake_2,
        crew_mistake_3=crew_mistake_3,
        aircraft_issue=aircraft_issue,
        Block_hour_issue_1=Block_hour_issue_1,
        Block_hour_issue_2=Block_hour_issue_2,
        duty_hour_issue=duty_hour_issue,
        sector_issue_1=sector_issue_1,
        sector_issue_2=sector_issue_2,
        output_crew_stats=output_crew_stats,
        swaps_issue=swaps_issue,
        get_short_time_diffs_df=get_short_time_diffs_df,
        pairings_issue_1=pairings_issue_1,
        LTC_check=LTC_check,
        training_issue=training_issue,
        aircraft_kpi=aircraft_kpi,
        flight_kpi=flight_kpi,
        sectors_kpi=sectors_kpi,
        aircraft_starting_on_kpi=aircraft_starting_on_kpi,
        aircraft_ending_on_kpi=aircraft_ending_on_kpi,
        utilized_captain=utilized_captain,
        utilized_first_officer=utilized_first_officer,
        utilized_flight_attendant=utilized_flight_attendant,
        Standyby_captain=Standyby_captain,
        Standyby_first_officer=Standyby_first_officer,
        Standyby_flight_attendant=Standyby_flight_attendant,
        aircraft_input_kpi=aircraft_input_kpi,
        flight_input_kpi=flight_input_kpi,
        sectors_input_kpi=sectors_input_kpi,
        available_captain=available_captain,
        available_first_officer=available_first_officer,
        available_flight_attendant=available_flight_attendant,
        df_validation=df_validation,
        df_validation_captain=df_validation_captain,
        df_validation_FO=df_validation_FO,
        df_validation_FA=df_validation_FA,
    )

    col1, col2, col3 = st.columns([1, 1, 1])
    with col2:
        st.download_button(
            label="📄 Download HTML Report",
            data=html_report,
            file_name=HTML_REPORT_FILENAME.format(date=schedule_date),
            mime="text/html",
            use_container_width=True,
        )
