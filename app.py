
import pandas as pd
from datetime import datetime, timedelta
import numpy as np
from functools import reduce
import warnings
warnings.filterwarnings("ignore")
import streamlit as st
from streamlit_option_menu import option_menu
import time
import io as io_module
from datetime import date

# Page configuration
st.set_page_config(
    page_title="TMA Crew Scheduler",
    page_icon="✈️",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS for modern dashboard look
st.markdown("""
    <style>
    /* Main background and fonts */
    .main {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        padding: 0;
    }
    
    .block-container {
        padding-top: 2rem;
        padding-bottom: 2rem;
        background: transparent;
    }
    
    /* Sidebar styling */
    [data-testid="stSidebar"] {
        background: #1e293b !important;
    }
    
    [data-testid="stSidebar"] > div:first-child {
        background: #1e293b !important;
    }
    
    /* Force all sidebar text to be white */
    [data-testid="stSidebar"] * {
        color: #ffffff !important;
    }
    
    [data-testid="stSidebar"] p,
    [data-testid="stSidebar"] span,
    [data-testid="stSidebar"] div {
        color: #ffffff !important;
    }
    
    /* Card styling */
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
    
    /* Header styling */
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
    
    .dashboard-subtitle {
        color: #64748b;
        font-size: 1.1rem;
    }
    
    /* Metric cards */
    .metric-card {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        border-radius: 12px;
        padding: 20px;
        color: white;
        text-align: center;
        box-shadow: 0 8px 20px rgba(102, 126, 234, 0.3);
    }
    
    .metric-value {
        font-size: 2.5rem;
        font-weight: 700;
        margin: 10px 0;
    }
    
    .metric-label {
        font-size: 0.75rem;
        opacity: 0.9;
        text-transform: uppercase;
        letter-spacing: 1px;
    }
    
    /* Button styling */
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
    
    /* Download button */
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
    
    /* Expander styling */
    .streamlit-expanderHeader {
        background: linear-gradient(135deg, #f8fafc 0%, #e2e8f0 100%);
        border-radius: 10px;
        font-weight: 600;
        color: #334155;
        border: 2px solid #e2e8f0;
    }
    
    .streamlit-expanderHeader:hover {
        border-color: #667eea;
    }
    
    /* Sidebar expander styling */
    [data-testid="stSidebar"] .streamlit-expanderHeader {
        background: #334155 !important;
        border: 2px solid #475569 !important;
        color: #ffffff !important;
    }
    
    [data-testid="stSidebar"] .streamlit-expanderHeader:hover {
        background: #475569 !important;
        border-color: #64748b !important;
    }
    
    [data-testid="stSidebar"] .streamlit-expanderHeader svg {
        fill: #ffffff !important;
    }
    
    [data-testid="stSidebar"] .streamlit-expanderContent {
        background: #1e293b !important;
        border: 1px solid #334155 !important;
    }
    
    /* File uploader */
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
    
    /* Date input */
    .stDateInput > div > div > input {
        border-radius: 8px;
        border: 2px solid #e2e8f0;
    }
    
    /* Dataframe styling */
    .dataframe {
        border-radius: 10px;
        overflow: hidden;
        box-shadow: 0 4px 6px rgba(0,0,0,0.05);
    }
    
    /* Status badges */
    .status-badge {
        display: inline-block;
        padding: 5px 15px;
        border-radius: 20px;
        font-size: 0.85rem;
        font-weight: 600;
        margin: 5px;
    }
    
    .status-success {
        background: #d1fae5;
        color: #065f46;
    }
    
    .status-error {
        background: #fee2e2;
        color: #991b1b;
    }
    
    .status-warning {
        background: #fef3c7;
        color: #92400e;
    }
    
    /* Spinner */
    .stSpinner > div {
        border-color: #667eea !important;
    }
    
    /* Info box */
    .info-box {
        background: linear-gradient(135deg, #e0e7ff 0%, #ddd6fe 100%);
        border-left: 4px solid #667eea;
        border-radius: 8px;
        padding: 15px 20px;
        margin: 15px 0;
        color: #1e293b;
    }
    
    /* Success message */
    .success-message {
        background: linear-gradient(135deg, #d1fae5 0%, #a7f3d0 100%);
        border-left: 4px solid #10b981;
        border-radius: 8px;
        padding: 15px 20px;
        margin: 15px 0;
        color: #065f46;
        font-weight: 500;
    }
    
    /* Error message */
    .error-message {
        background: linear-gradient(135deg, #fee2e2 0%, #fecaca 100%);
        border-left: 4px solid #ef4444;
        border-radius: 8px;
        padding: 15px 20px;
        margin: 15px 0;
        color: #991b1b;
        font-weight: 500;
    }
    
    /* Section header */
    .section-header {
        font-size: 1.5rem;
        font-weight: 700;
        color: #1e293b;
        margin: 25px 0 15px 0;
        padding-bottom: 10px;
        border-bottom: 3px solid #667eea;
    }
    
    /* Hide Streamlit branding */
    #MainMenu {visibility: hidden;}
    footer {visibility: hidden;}
    header {visibility: hidden;}
    </style>
""", unsafe_allow_html=True)

available_status = ["1", "Li", "LC"]
leave_status = ["X", "AL", "AU", "PAL", "EM", "ML", "M"]


# Functions import
from input_processing import schedule_input_processing
from input_processing import aircraft_processing
from input_processing import crew_aircraft_processing
from input_processing import crew_stats_processing
from input_processing import logsheet_processing
from input_processing import month_plan_processing
from input_processing import flight_training_processing
from input_processing import expiry_data_processing
from input_processing import seniority_processing
from input_processing import crew_master_processing
from input_processing import merged_data_fun
from input_processing import crew_stats_xml
from input_processing import new_crew_stats

from output_processing import Schedule_output_processing
from output_processing import Schedule_output_processing_2
from output_processing import output_master_processing
from output_processing import crew_ac_stats_processing
from output_processing import overnight_flights
from input_validations import input_validation_fun

from checklist import Schedule_check_fun
from checklist import crew_check_fun
from checklist import aircraft_check
from checklist import Stats_check_fun
from checklist import swaps_check_fun
from checklist import seniority_check_fun
from checklist import training_pairing_check
from checklist import get_short_time_diffs
from checklist import unassigned_flights


from clustering import cluster_fun


# Sidebar Design and Layout
with st.sidebar:
    st.markdown("""
        <div style="text-align: center; padding: 20px 0; margin-bottom: 20px;">
            <h1 style="color: #ffffff; font-size: 2rem; margin-bottom: 5px;">✈️ TMA Crew</h1>
            <p style="color: #e2e8f0; font-size: 1rem; font-weight: 500;">Scheduler & Validator</p>
        </div>
    """, unsafe_allow_html=True)
    
    selected = option_menu(
        menu_title=None,
        options=[
            "Crew Stats Generator",
            "Input Data Validator",
            "Constraints Validator"
        ],
        icons=["graph-up", "clipboard-check", "shield-check"],
        menu_icon="cast",
        default_index=0,
        styles={
            "container": {
                "padding": "5px", 
                "background-color": "#1e293b"
            },
            "icon": {
                "color": "#ffffff", 
                "font-size": "22px"
            },
            "nav-link": {
                "font-size": "16px",
                "text-align": "left",
                "margin": "8px 0",
                "padding": "16px 20px",
                "border-radius": "12px",
                "color": "#ffffff !important",
                "background-color": "#334155",
                "font-weight": "600",
            },
            "nav-link-selected": {
                "background-color": "#6366f1",
                "font-weight": "700",
                "color": "#ffffff !important",
                "box-shadow": "0 4px 15px rgba(99, 102, 241, 0.5)",
            },
        }
    )
    
    st.markdown("<br>", unsafe_allow_html=True)
    
    # Info section
    with st.expander("ℹ️ About", expanded=False):
        st.markdown("""
            <div style="color: #ffffff; font-size: 0.9rem; line-height: 1.6;">
                <p><strong>Version:</strong> 2.0</p>
                <p><strong>Last Updated:</strong> Nov 2025</p>
                <p>Comprehensive crew scheduling validation and reporting system.</p>
            </div>
        """, unsafe_allow_html=True)

    
    with st.expander("👨‍💻 Developer", expanded=False):
        st.markdown("""
            <div style="color: #ffffff; font-size: 0.9rem; line-height: 1.6;">
                <p><strong>Name:</strong> Himanshu Gupta</p>
                <p><strong>Department:</strong> Corporate strategy</p>
                <p><strong>Contact:</strong> +960 7375336</p>
            </div>
        """, unsafe_allow_html=True)

# Main content area
if selected == "Crew Stats Generator":
    st.markdown("""
        <div class="dashboard-header">
            <div class="dashboard-title">📊 Crew Stats Generator</div>
            <div class="dashboard-subtitle">Generate comprehensive crew statistics reports</div>
        </div>
    """, unsafe_allow_html=True)
    
    col1, col2 = st.columns([2, 1])
    
    with col1:
        st.markdown('<div class="dashboard-card">', unsafe_allow_html=True)
        st.markdown("### 📁 Upload Crew Stats File")
        crewstats_xml = st.file_uploader(
            "Select crew stats macro (XLSM format)",
            type=["xlsm"],
            help="Upload the Excel macro-enabled file containing crew statistics"
        )
        st.markdown('</div>', unsafe_allow_html=True)
    
    with col2:
        st.markdown('<div class="dashboard-card">', unsafe_allow_html=True)
        st.markdown("### ℹ️ Instructions")
        st.markdown("""
            1. Upload the crew stats macro file
            2. Click 'Generate Report'
            3. Review the output
            4. Download the results
        """)
        st.markdown('</div>', unsafe_allow_html=True)
    
    if crewstats_xml is not None:
        st.markdown('<div class="info-box">✅ File uploaded successfully!</div>', unsafe_allow_html=True)
    
    col1, col2, col3 = st.columns([1, 1, 2])
    with col2:
        generate_btn = st.button("🚀 Generate Report", use_container_width=True, type="primary")
    
    if generate_btn:
        if crewstats_xml is not None:
            with st.spinner("⚙️ Processing crew statistics..."):
                sectors = pd.read_excel(crewstats_xml, engine='openpyxl', sheet_name="Sectors")
                flt = pd.read_excel(crewstats_xml, engine='openpyxl', sheet_name="FLT")
                day_27th = pd.read_excel(crewstats_xml, engine='openpyxl', sheet_name="27 Days")
                day_364th = pd.read_excel(crewstats_xml, engine='openpyxl', sheet_name="364 Days")
                
                crew_stats_output, crew_stats_output_2 = crew_stats_xml(sectors, flt, day_27th, day_364th)
                
                time.sleep(0.5)  # Brief pause for UX
            
            st.markdown('<div class="success-message">✨ Report generated successfully!</div>', unsafe_allow_html=True)
            
            # Metrics
            col1, col2, col3 = st.columns(3)
            with col1:
                st.markdown(f"""
                    <div class="metric-card">
                        <div class="metric-label">Total Records</div>
                        <div class="metric-value">{len(crew_stats_output)}</div>
                    </div>
                """, unsafe_allow_html=True)
            
            
            
            with col2:
                st.markdown("""
                    <div class="metric-card" style="background: linear-gradient(135deg, #10b981 0%, #059669 100%);">
                        <div class="metric-label">Status</div>
                        <div class="metric-value">✓</div>
                    </div>
                """, unsafe_allow_html=True)
            
            st.markdown("<br>", unsafe_allow_html=True)
            
            # Results
            st.markdown('<div class="dashboard-card">', unsafe_allow_html=True)
            st.markdown("### 📋 Crew stats reports")
            st.dataframe(crew_stats_output, use_container_width=True, height=400)
            st.markdown('</div>', unsafe_allow_html=True)
            
            # Download
            output = io_module.BytesIO()
            with pd.ExcelWriter(output, engine='xlsxwriter') as writer:
                crew_stats_output.to_excel(writer, sheet_name='crew stats', index=False)            
            output.seek(0)
            
            col1, col2, col3 = st.columns([1, 1, 1])
            with col2:
                st.download_button(
                    label="📥 Download crew stats report",
                    data=output,
                    file_name="Crewstats.xlsx",
                    mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
                    use_container_width=True
                )
        else:
            st.markdown('<div class="error-message">⚠️ Please upload a crew stats file first!</div>', unsafe_allow_html=True)

if selected == "Input Data Validator" or selected == "Constraints Validator":
    
    if selected == "Input Data Validator":
        st.markdown("""
            <div class="dashboard-header">
                <div class="dashboard-title">🔍 Input Data Validator</div>
                <div class="dashboard-subtitle">Validate crew data integrity and completeness</div>
            </div>
        """, unsafe_allow_html=True)
    else:
        st.markdown("""
            <div class="dashboard-header">
                <div class="dashboard-title">🛡️ Constraints Validator</div>
                <div class="dashboard-subtitle">Validate scheduling constraints and regulations</div>
            </div>
        """, unsafe_allow_html=True)
    
    # Date selection
    st.markdown('<div class="dashboard-card">', unsafe_allow_html=True)
    col1, col2, col3 = st.columns([1, 2, 1])
    with col2:
        st.markdown("### 📅 Schedule Date")
        schedule_date = st.date_input(
            "Select the schedule date",
            help="Choose the date for validation"
        )
        schedule_date = schedule_date.strftime("%Y-%m-%d")
    st.markdown('</div>', unsafe_allow_html=True)
    
    prev_day = (datetime.strptime(schedule_date, "%Y-%m-%d") - timedelta(days=1)).strftime("%Y-%m-%d")
    next_day = (datetime.strptime(schedule_date, "%Y-%m-%d") + timedelta(days=1)).strftime("%Y-%m-%d")
    
    start_date = date(2025, 9, 1).strftime("%Y-%m-%d")
    end_date = date(2025, 9, 8).strftime("%Y-%m-%d")

    # File uploads
    if start_date <= schedule_date <= end_date:
        st.markdown('<div class="info-box">📂 Using pre-loaded validation data</div>', unsafe_allow_html=True)
        aircraft = pd.read_excel("Model Validations/Aircrafts.xlsx")
        crew_aircraft = pd.read_excel("Model Validations/Crew AC Matrix.xlsx")
        seniority = pd.read_excel("Model Validations/Crew Pairing.xlsx")
        logsheet = pd.read_excel("Model Validations/Log sheet.xlsx")
        crew_master = pd.read_excel("Model Validations/Resources.xlsx")
        expiry_data = pd.read_excel("Model Validations/Training Expiry.xlsx")
        flight_training = pd.read_excel("Model Validations/Training Pairings.xlsx")
        month_plan = pd.read_excel("Model Validations/Month plan.xlsx")
        crew_stats = pd.read_excel("Model Validations/Crew Stats.xlsx", sheet_name=schedule_date)
    else:
        st.markdown('<div class="dashboard-card">', unsafe_allow_html=True)
        st.markdown("### 📤 Upload Required Files")
        
        col1, col2, col3 = st.columns(3)
        
        with col1:
            aircraft_input = st.file_uploader("Aircraft Data", type=["xlsx", "xls"], key="aircraft")
            crew_aircraft_input = st.file_uploader("Crew Aircraft Matrix", type=["xlsx", "xls"], key="crew_ac")
            seniority_input = st.file_uploader("Crew Pairing", type=["xlsx", "xls"], key="seniority")
        
        with col2:
            logsheet_input = st.file_uploader("Logsheet", type=["xlsx", "xls"], key="logsheet")
            crew_master_input = st.file_uploader("Crew Resource", type=["xlsx", "xls"], key="crew_master")
            expiry_data_input = st.file_uploader("Crew License Expiry", type=["xlsx", "xls"], key="expiry")
        
        with col3:
            flight_training_input = st.file_uploader("Training Pairings", type=["xlsx", "xls"], key="training")
            month_plan_input = st.file_uploader("Monthly Plan", type=["xlsx", "xls"], key="month_plan")
            crew_stats_input = st.file_uploader("Crew Stats", type=["xlsx", "xls"], key="crew_stats")
        
        st.markdown('</div>', unsafe_allow_html=True)
        
        # Load uploaded files
        if aircraft_input is not None:
            aircraft = pd.read_excel(aircraft_input)
        if crew_aircraft_input is not None:
            crew_aircraft = pd.read_excel(crew_aircraft_input)
        if seniority_input is not None:
            seniority = pd.read_excel(seniority_input)
        if logsheet_input is not None:
            logsheet = pd.read_excel(logsheet_input)
        if crew_master_input is not None:
            crew_master = pd.read_excel(crew_master_input)
        if expiry_data_input is not None:
            expiry_data = pd.read_excel(expiry_data_input)
        if flight_training_input is not None:
            flight_training = pd.read_excel(flight_training_input)
        if month_plan_input is not None:
            month_plan = pd.read_excel(month_plan_input)
        if crew_stats_input is not None:
            crew_stats = pd.read_excel(crew_stats_input)
            crew_stats=new_crew_stats(crew_stats)

if selected == "Input Data Validator":
    col1, col2, col3 = st.columns([1, 1, 1])
    with col2:
        validate_btn = st.button("✅ Validate Data", use_container_width=True, type="primary")
    
    if validate_btn:
        with st.spinner("🔄 Processing data..."):
            aircraft = aircraft_processing(aircraft)
            crew_aircraft = crew_aircraft_processing(crew_aircraft)
            seniority = seniority_processing(seniority)
            logsheet = logsheet_processing(logsheet, prev_day)
            crew_master = crew_master_processing(crew_master)
            expiry_data = expiry_data_processing(expiry_data)
            flight_training = flight_training_processing(flight_training, schedule_date)
            month_plan = month_plan_processing(month_plan, schedule_date, prev_day, next_day)

            crew_stats = crew_stats_processing(crew_stats)
            merged_df = merged_data_fun(month_plan, crew_master, seniority, expiry_data, logsheet, crew_stats)
            input_issue_1, input_issue_2 = input_validation_fun(merged_df)
        
        st.markdown('<div class="success-message">✨ Validation completed successfully!</div>', unsafe_allow_html=True)
        
        # Metrics
        col1, col2, col3 = st.columns(3)
        with col1:
            st.markdown(f"""
                <div class="metric-card" style="background: linear-gradient(135deg, #f59e0b 0%, #d97706 100%);">
                    <div class="metric-label">Missing Resources</div>
                    <div class="metric-value">{len(input_issue_1)}</div>
                </div>
            """, unsafe_allow_html=True)
        
        with col2:
            st.markdown(f"""
                <div class="metric-card" style="background: linear-gradient(135deg, #ef4444 0%, #dc2626 100%);">
                    <div class="metric-label">Missing Stats</div>
                    <div class="metric-value">{len(input_issue_2)}</div>
                </div>
            """, unsafe_allow_html=True)
        
        with col3:
            status_color = "#10b981" if len(input_issue_1) == 0 and len(input_issue_2) == 0 else "#ef4444"
            status_text = "✓" if len(input_issue_1) == 0 and len(input_issue_2) == 0 else "⚠"
            st.markdown(f"""
                <div class="metric-card" style="background: linear-gradient(135deg, {status_color} 0%, {status_color} 100%);">
                    <div class="metric-label">Overall Status</div>
                    <div class="metric-value">{status_text}</div>
                </div>
            """, unsafe_allow_html=True)
        
        st.markdown("<br>", unsafe_allow_html=True)
        
        # Validation Results
        tab1, tab2 = st.tabs(["🔍 Validation 1: Missing Resources", "🔍 Validation 2: Missing Stats"])
        
        with tab1:
            st.markdown('<div class="dashboard-card">', unsafe_allow_html=True)
            if input_issue_1.empty:
                st.markdown('<div class="success-message">✅ No issues found - All crew resources are properly assigned!</div>', unsafe_allow_html=True)
            else:
                st.markdown("### ⚠️ Crew with Missing Resources")
                st.info("The table below shows crew members with missing resource data except their stats")
                st.dataframe(input_issue_1, use_container_width=True, height=400)
            st.markdown('</div>', unsafe_allow_html=True)
        
        with tab2:
            st.markdown('<div class="dashboard-card">', unsafe_allow_html=True)
            if input_issue_2.empty:
                st.markdown('<div class="success-message">✅ No issues found - All crew statistics are complete!</div>', unsafe_allow_html=True)
            else:
                st.markdown("### ⚠️ Crew with Missing Statistics")
                st.info("The table below shows crew members with missing statistical data")
                st.dataframe(input_issue_2, use_container_width=True, height=400)
            st.markdown('</div>', unsafe_allow_html=True)
        
        # Download
        output = io_module.BytesIO()
        with pd.ExcelWriter(output, engine='xlsxwriter') as writer:
            input_issue_1.to_excel(writer, sheet_name='Validation 1', index=False)
            input_issue_2.to_excel(writer, sheet_name='Validation 2', index=False)
            merged_df.to_excel(writer, sheet_name='Input data', index=False)
        
        output.seek(0)
        
        col1, col2, col3 = st.columns([1, 1, 1])
        with col2:
            st.download_button(
                label="📥 Download Validation Report",
                data=output,
                file_name="input_validation.xlsx",
                mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
                use_container_width=True
            )

if selected == "Constraints Validator":
    st.markdown('<div class="dashboard-card">', unsafe_allow_html=True)
    st.markdown("### 📤 Upload Flight Plans")
    col1, col2 = st.columns(2)
    with col1:
        input_flight_plan = st.file_uploader("Input Flight Plan", type=["xlsx", "xls"], key="input_plan")
    with col2:
        output_flight_plan = st.file_uploader("Solver Output", type=["xlsx", "xls"], key="output_plan")
    st.markdown('</div>', unsafe_allow_html=True)
    
    if input_flight_plan is not None:
        Schedule_input = pd.read_excel(input_flight_plan)
    
    if output_flight_plan is not None:
        Schedule_output = pd.read_excel(output_flight_plan)


    
    col1, col2, col3 = st.columns([1, 1, 1])
    with col2:
        validate_constraints_btn = st.button("🛡️ Validate Constraints", use_container_width=True, type="primary")
    
    if validate_constraints_btn:
        
        progress_bar = st.progress(0)
        status_text = st.empty()
        
        status_text.text("🔄 Processing aircraft data...")
        progress_bar.progress(10)
        aircraft = aircraft_processing(aircraft)
        
        status_text.text("🔄 Processing crew aircraft matrix...")
        progress_bar.progress(20)
        crew_aircraft = crew_aircraft_processing(crew_aircraft)
        
        status_text.text("🔄 Processing seniority data...")
        progress_bar.progress(30)
        seniority = seniority_processing(seniority)
        
        status_text.text("🔄 Processing logsheet...")
        progress_bar.progress(40)
        logsheet = logsheet_processing(logsheet, prev_day)
        crew_master = crew_master_processing(crew_master)
        
        status_text.text("🔄 Processing training data...")
        progress_bar.progress(50)
        expiry_data = expiry_data_processing(expiry_data)
        flight_training = flight_training_processing(flight_training, schedule_date)
        
        status_text.text("🔄 Processing schedules...")
        progress_bar.progress(60)
        month_plan = month_plan_processing(month_plan, schedule_date, prev_day, next_day)
        crew_stats = crew_stats_processing(crew_stats)
        Schedule_input = schedule_input_processing(Schedule_input)
        
        status_text.text("🔄 Merging data...")
        progress_bar.progress(70)
        merged_df = merged_data_fun(month_plan, crew_master, seniority, expiry_data, logsheet, crew_stats)
        
        status_text.text("🔄 Processing outputs...")
        progress_bar.progress(80)
        Schedule_output = Schedule_output_processing(Schedule_output)
        Schedule_output_2 = Schedule_output_processing_2(Schedule_output)
        output_master, output_crew_stats = output_master_processing(Schedule_output_2)
        
        status_text.text("🔄 Running validations...")
        progress_bar.progress(90)
        crew_ac_stats = crew_ac_stats_processing(Schedule_output_2, aircraft, crew_aircraft)
        comparison_master = merged_df.merge(output_master, on="Crew code", how="outer")
        
        # Validation checks
        available_working = comparison_master[(comparison_master["Schedule Day"].isin(available_status)) & (~comparison_master["Working Status"].isna())]
        Standby_crew = comparison_master[(comparison_master["Schedule Day"].isin(available_status)) & (comparison_master["Working Status"].isna())]
        leaves_working = comparison_master[(comparison_master["Schedule Day"].isin(leave_status)) & (~comparison_master["Working Status"].isna())]
        
        on_training=comparison_master[~(comparison_master["Schedule Day"].isin(leave_status+available_status))]
        on_training_working=on_training[~comparison_master["Working Status"].isna()]
        training_non_outstations = on_training[(on_training["Outstation airport"].isin(["", "MLE"]))]
        unassigned_flights_crew = unassigned_flights(Schedule_output)
        
        Schedule_check = Schedule_check_fun(Schedule_output, Schedule_input)
        crew_mistake_1, crew_mistake_11, crew_mistake_2, crew_mistake_3 = crew_check_fun(comparison_master, available_working)
        aircraft_issue = aircraft_check(crew_ac_stats)
        Block_hour_issue_1, Block_hour_issue_2, duty_hour_issue, sector_issue_1, sector_issue_2 = Stats_check_fun(available_working)
        swaps_issue = swaps_check_fun(output_master)
        pairings_issue_1, LTC_check = seniority_check_fun(Schedule_output, merged_df)
        training_issue = training_pairing_check(flight_training, Schedule_output)
        get_short_time_diffs_df = get_short_time_diffs(crew_ac_stats)

        output_df_kpi = overnight_flights(Schedule_output)



        aircraft_kpi=Schedule_output['Aircraft No.'].nunique()
        flight_kpi=Schedule_output['Flight No.'].nunique()
        sectors_kpi=len(Schedule_output)


        aircraft_starting_on_kpi=len(output_df_kpi[(output_df_kpi['Sector Position']=="Starting") & (output_df_kpi['ON']==1)])
        aircraft_ending_on_kpi=len(output_df_kpi[(output_df_kpi['Sector Position']=="Ending") & (output_df_kpi['ON']==1)])

        utilized_captain=Schedule_output['Captain'].nunique()
        utilized_first_officer=Schedule_output['First Officer'].nunique()
        utilized_flight_attendant=Schedule_output['Flight Attendant'].nunique()

        Standyby_captain=len(Standby_crew[Standby_crew['Crew Type_x']=="Captain"])
        Standyby_first_officer=len(Standby_crew[Standby_crew['Crew Type_x']=="First Officer"])
        Standyby_flight_attendant=len(Standby_crew[Standby_crew['Crew Type_x']=="Flight Attendant"])


        aircraft_input_kpi=Schedule_input['Aircraft No.'].nunique()
        flight_input_kpi=Schedule_input['Flight No.'].nunique()
        sectors_input_kpi=len(Schedule_input)
        
        test=merged_df[merged_df["Schedule Day"].isin(available_status)]

        available_captain=len(test[test["Crew Type"]=="Captain"])
        available_first_officer=len(test[test["Crew Type"]=='First Officer'])
        available_flight_attendant=len(test[test["Crew Type"]=='Flight Attendant'])



        progress_bar.progress(100)
        status_text.text("✅ Validation complete!")
        time.sleep(0.5)
        progress_bar.empty()
        status_text.empty()
        
        st.markdown('<div class="success-message">✨ All constraints validated successfully!</div>', unsafe_allow_html=True)
        
        # Summary metrics
        st.markdown("### 📊 Validation Summary")
        col1, col2, col3, col4,col5,col6,col7,col8 = st.columns(8)
        
        with col1:
            issues_count = len(Schedule_check) + len(unassigned_flights_crew)
            color = "#ef4444" if issues_count > 0 else "#10b981"
            st.markdown(f"""
                <div class="metric-card" style="background: linear-gradient(135deg, {color} 0%, {color} 100%);">
                    <div class="metric-label">Schedule Issues</div>
                    <div class="metric-value">{issues_count}</div>
                </div>
            """, unsafe_allow_html=True)
        
        with col2:
            Block_hour_issues = len(Block_hour_issue_1) + len(Block_hour_issue_2)
            color = "#ef4444" if Block_hour_issues > 0 else "#10b981"
            st.markdown(f"""
                <div class="metric-card" style="background: linear-gradient(135deg, {color} 0%, {color} 100%);">
                    <div class="metric-label"> BH violations</div>
                    <div class="metric-value">{Block_hour_issues}</div>
                </div>
            """, unsafe_allow_html=True)

        with col3:
            duty_hour_issues = len(duty_hour_issue)
            color = "#ef4444" if duty_hour_issues > 0 else "#10b981"
            st.markdown(f"""
                <div class="metric-card" style="background: linear-gradient(135deg, {color} 0%, {color} 100%);">
                    <div class="metric-label"> DH violations</div>
                    <div class="metric-value">{duty_hour_issues}</div>
                </div>
            """, unsafe_allow_html=True)

        with col4:
            sector_issues = len(output_crew_stats[output_crew_stats["Total sectors"] > 14]) + len(sector_issue_1)+len(sector_issue_2)
            color = "#ef4444" if sector_issues > 0 else "#10b981"
            st.markdown(f"""
                <div class="metric-card" style="background: linear-gradient(135deg, {color} 0%, {color} 100%);">
                    <div class="metric-label"> Sectors violations</div>
                    <div class="metric-value">{sector_issues}</div>
                </div>
            """, unsafe_allow_html=True)
        
        with col5:
            pairing_issues = len(pairings_issue_1) + len(LTC_check) + len(training_issue)
            color = "#ef4444" if pairing_issues > 0 else "#10b981"
            st.markdown(f"""
                <div class="metric-card" style="background: linear-gradient(135deg, {color} 0%, {color} 100%);">
                    <div class="metric-label">Pairing Issues</div>
                    <div class="metric-value">{pairing_issues}</div>
                </div>
            """, unsafe_allow_html=True)

        with col6:
            unavailable_issues = len(leaves_working) + len(crew_mistake_1) + len(crew_mistake_11)
            color = "#ef4444" if unavailable_issues > 0 else "#10b981"
            st.markdown(f"""
                <div class="metric-card" style="background: linear-gradient(135deg, {color} 0%, {color} 100%);">
                    <div class="metric-label">Status Issues</div>
                    <div class="metric-value">{unavailable_issues}</div>
                </div>
            """, unsafe_allow_html=True)
        
        with col7:
            overnight_issues = len(crew_mistake_2) + len(crew_mistake_3)
            color = "#ef4444" if overnight_issues > 0 else "#10b981"
            st.markdown(f"""
                <div class="metric-card" style="background: linear-gradient(135deg, {color} 0%, {color} 100%);">
                    <div class="metric-label">Overnight Issues</div>
                    <div class="metric-value">{overnight_issues}</div>
                </div>
            """, unsafe_allow_html=True)
        
        with col8:
            aircraft_issues = len(aircraft_issue) + len(swaps_issue)
            color = "#ef4444" if aircraft_issues > 0 else "#10b981"
            st.markdown(f"""
                <div class="metric-card" style="background: linear-gradient(135deg, {color} 0%, {color} 100%);">
                    <div class="metric-label">Aircraft Issues</div>
                    <div class="metric-value">{aircraft_issues}</div>
                </div>
            """, unsafe_allow_html=True)
        
        
        
        st.markdown("<br>", unsafe_allow_html=True)
        
        # Detailed results in expanders
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
            daily_sector_violation = output_crew_stats[output_crew_stats["Total sectors"] > 14]
            
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
        
        # Generate report
        validation_report_1 = comparison_master.copy()
        validation_report_1 = validation_report_1[validation_report_1["Working Status"] == 1]
        validation_report_1 = validation_report_1[[
            "Crew code", "Crew name", "Crew Type_x", "Seniority Level", "Is Instructor?",
            "Prev Day", "Schedule Day", "Next Day", "Expiry status", "Outstation airport",
            "Outstation Aircraft", "Max BH left", "Max BH left ON", "Max DH left",
            "Max sectors left", "Max more than 12 sectors", "Starting from", "Ending at",
            "Total flights", "Total aircrafts", "Duty hours", "Total sectors",
            "Block hours", "No. of swaps"
        ]]
        
        validation_report_1.columns = [
            "Crew code", "Crew Name", "Crew Type", "Seniority Level", "Is Instructor?",
            "Prev Day status", "Schedule Day status", "Next Day status", "Expiry status",
            "Prev day airport", "Prev day aircraft", "Max BH left", "Max BH left ON",
            "Max DH left", "Max sectors left", "Max more than 12 sectors",
            "Starting from", "Ending at", "Total flights", "Total aircrafts",
            "Total duty hours", "Total sectors", "Block hours", "No. of swaps"
        ]


        df_validation=validation_report_1.copy()

        df_validation=df_validation[['Crew code','Crew Type', 'Seniority Level', 'Max BH left', 'Max BH left ON', 'Max DH left','Max sectors left', 'Max more than 12 sectors', 'Starting from',
            'Ending at', 'Total flights', 'Total aircrafts', 'Total duty hours','Total sectors', 'Block hours', 'No. of swaps']]
        
        df_validation_captain=df_validation[df_validation["Crew Type"]=="Captain"]
        df_validation_FO=df_validation[df_validation["Crew Type"]=="First Officer"]
        df_validation_FA=df_validation[df_validation["Crew Type"]=="Flight Attendant"]


    
        # Create the dataframe
        metrics_df = pd.DataFrame({
            "Parameter": [
                'Total Aircraft in Schedule',
                'Total Flight in Schedule',
                'Total sectors in Schedule',
                'Total Available Crew in Month Plan',
                'Available Captains in Month Plan',
                'Available First Officers in Month Plan',
                'Available Cabin crew in Month Plan',
                'Total Aircraft Scheduled',
                'Aircraft Scheduled Starting ON',
                'Aircraft Scheduled Ending ON',
                'Total Flights Scheduled',
                'Total Sectors Scheduled',
                'Utilized Crew',
                'Utilized Captain',
                'Utilized First Officer',
                'Utilized Flight Attendant',
                'Total Standby crew',
                'Standby Captain',
                'Standby First Officer',
                'Standby Flight Attendant',
                "Total Swap percentage",
                "Captain Swap percentage",
                "First Officer Swap percentage",
                "Flight Attendant Swap percentage"
            ],
            'Value': [
                aircraft_input_kpi,
                flight_input_kpi,
                sectors_input_kpi,
                available_captain + available_first_officer + available_flight_attendant,
                available_captain,
                available_first_officer,
                available_flight_attendant,
                aircraft_kpi,
                aircraft_starting_on_kpi,
                aircraft_ending_on_kpi,
                flight_kpi,
                sectors_kpi,
                utilized_captain + utilized_first_officer + utilized_flight_attendant,
                utilized_captain,
                utilized_first_officer,
                utilized_flight_attendant,
                Standyby_captain + Standyby_first_officer + Standyby_flight_attendant,
                Standyby_captain,
                Standyby_first_officer,
                Standyby_flight_attendant,
                (df_validation['No. of swaps'] == 1).sum() / len(df_validation) * 100,
                (df_validation_captain['No. of swaps'] == 1).sum() / len(df_validation_captain) * 100,
                (df_validation_FO['No. of swaps'] == 1).sum() / len(df_validation_FO) * 100,
                (df_validation_FA['No. of swaps'] == 1).sum() / len(df_validation_FA) * 100
            ]
        })

        st.dataframe(metrics_df)


        # Download report
        st.markdown("<br>", unsafe_allow_html=True)
        output = io_module.BytesIO()
        with pd.ExcelWriter(output, engine='xlsxwriter') as writer:
            df_output = [
                (Schedule_check, 'Schedule_check'),
                (crew_mistake_1, 'Crew with Training 1'),
                (crew_mistake_11, 'Crew with Training 2'),
                (crew_mistake_2, 'Error in Starting points'),
                (crew_mistake_3, 'Error in Overnights'),
                (aircraft_issue, 'Error in aircrafts'),
                (Block_hour_issue_1, 'Error in Block hour 1'),
                (Block_hour_issue_2, 'Error in Block hour 2'),
                (duty_hour_issue, 'Error in duty hour'),
                (sector_issue_1, 'Error in sectors 1'),
                (sector_issue_2, 'Error in sectors 2'),
                (swaps_issue, 'Error in AC swaps'),
                (get_short_time_diffs_df, "AC swaps time"),
                (pairings_issue_1, 'Error in seniority pairings'),
                (LTC_check, 'Error in LTC pairings'),
                (training_issue, 'Error in training pairings'),
                (comparison_master, 'comparison_master'),
                (output_master, 'output_master'),
                (validation_report_1, 'Report 1'),
                (crew_ac_stats, 'Report 2'),
                (metrics_df,"Utilization metrics")
            ]
            
            for df, sheet_name in df_output:
                if not df.empty:
                    df.to_excel(writer, sheet_name=sheet_name, index=False)
        
        output.seek(0)



        st.markdown('<div class="section-header">📊 Key Performance Indicators</div>', unsafe_allow_html=True)

        st.markdown('<div class="dashboard-card">', unsafe_allow_html=True)

        # Create columns with spacing to group sections
        st.subheader(f"Available Aircarft and Crew")

        col1, col2, col3, gap1, col4, col5, col6, col7 = st.columns([1, 1, 1, 0.3, 1, 1, 1, 1])
        

        # ✈️ Aircraft & Operations (grouped together)
        with col1:
            st.markdown(f'''
                <div class="metric-card">
                    <div class="metric-label">Total Aircraft</div>
                    <div class="metric-value">{aircraft_input_kpi}</div>
                </div>
            ''', unsafe_allow_html=True)

        with col2:
            st.markdown(f'''
                <div class="metric-card">
                    <div class="metric-label">Total Flight</div>
                    <div class="metric-value">{flight_input_kpi}</div>
                </div>
            ''', unsafe_allow_html=True)

        with col3:
            st.markdown(f'''
                <div class="metric-card">
                    <div class="metric-label">Total sectors</div>
                    <div class="metric-value">{sectors_input_kpi}</div>
                </div>
            ''', unsafe_allow_html=True)

        # Gap 1 - Visual separator
        with gap1:
            st.markdown('<div style="border-left: 3px solid rgba(255,255,255,0.3); height: 100px; margin: 0 auto;"></div>', unsafe_allow_html=True)

        # 👥 Crew Utilization (grouped together)
        total_crew = available_captain + available_first_officer + available_flight_attendant

        with col4:
            st.markdown(f'''
                <div class="metric-card" style="background: linear-gradient(135deg, #10b981 0%, #059669 100%);">
                    <div class="metric-label">Total Available Crew</div>
                    <div class="metric-value">{total_crew}</div>
                </div>
            ''', unsafe_allow_html=True)

        with col5:
            st.markdown(f'''
                <div class="metric-card" style="background: linear-gradient(135deg, #10b981 0%, #059669 100%);">
                    <div class="metric-label">Available Captains</div>
                    <div class="metric-value">{available_captain}</div>
                </div>
            ''', unsafe_allow_html=True)

        with col6:
            st.markdown(f'''
                <div class="metric-card" style="background: linear-gradient(135deg, #10b981 0%, #059669 100%);">
                    <div class="metric-label">Available First Officers</div>
                    <div class="metric-value">{available_first_officer}</div>
                </div>
            ''', unsafe_allow_html=True)

        with col7:
            st.markdown(f'''
                <div class="metric-card" style="background: linear-gradient(135deg, #10b981 0%, #059669 100%);">
                    <div class="metric-label">Available Cabin crew</div>
                    <div class="metric-value">{available_flight_attendant}</div>
                </div>
            ''', unsafe_allow_html=True)

        
        st.markdown('</div>', unsafe_allow_html=True)



        st.subheader(f"")
        st.subheader(f"Scheduled Aircraft and Crew")
        # Create columns with spacing to group sections
        col1, col2, col3,col12,col13, gap1, col4, col5, col6, col7, gap2, col8, col9, col10, col11 = st.columns([1, 1, 1,1,1, 0.3, 1, 1, 1, 1, 0.3, 1, 1, 1, 1])
        

        # ✈️ Aircraft & Operations (grouped together)
        with col1:
            st.markdown(f'''
                <div class="metric-card">
                    <div class="metric-label">Total AC</div>
                    <div class="metric-value">{aircraft_kpi}</div>
                </div>
            ''', unsafe_allow_html=True)

        with col12:
            st.markdown(f'''
                <div class="metric-card">
                    <div class="metric-label">AC Starting ON</div>
                    <div class="metric-value">{aircraft_starting_on_kpi}</div>
                </div>
            ''', unsafe_allow_html=True)

        with col13:
            st.markdown(f'''
                <div class="metric-card">
                    <div class="metric-label">AC Ending ON</div>
                    <div class="metric-value">{aircraft_ending_on_kpi}</div>
                </div>
            ''', unsafe_allow_html=True)

        with col2:
            st.markdown(f'''
                <div class="metric-card">
                    <div class="metric-label">Total Flights</div>
                    <div class="metric-value">{flight_kpi}</div>
                </div>
            ''', unsafe_allow_html=True)

        with col3:
            st.markdown(f'''
                <div class="metric-card">
                    <div class="metric-label">Total Sectors</div>
                    <div class="metric-value">{sectors_kpi}</div>
                </div>
            ''', unsafe_allow_html=True)

        # Gap 1 - Visual separator
        with gap1:
            st.markdown('<div style="border-left: 3px solid rgba(255,255,255,0.3); height: 100px; margin: 0 auto;"></div>', unsafe_allow_html=True)

        # 👥 Crew Utilization (grouped together)
        total_crew = utilized_captain + utilized_first_officer + utilized_flight_attendant

        with col4:
            st.markdown(f'''
                <div class="metric-card" style="background: linear-gradient(135deg, #10b981 0%, #059669 100%);">
                    <div class="metric-label">Utilized Crew</div>
                    <div class="metric-value">{total_crew}</div>
                </div>
            ''', unsafe_allow_html=True)

        with col5:
            st.markdown(f'''
                <div class="metric-card" style="background: linear-gradient(135deg, #10b981 0%, #059669 100%);">
                    <div class="metric-label">Utilized Cap</div>
                    <div class="metric-value">{utilized_captain}</div>
                </div>
            ''', unsafe_allow_html=True)

        with col6:
            st.markdown(f'''
                <div class="metric-card" style="background: linear-gradient(135deg, #10b981 0%, #059669 100%);">
                    <div class="metric-label">Utilized FO</div>
                    <div class="metric-value">{utilized_first_officer}</div>
                </div>
            ''', unsafe_allow_html=True)

        with col7:
            st.markdown(f'''
                <div class="metric-card" style="background: linear-gradient(135deg, #10b981 0%, #059669 100%);">
                    <div class="metric-label">Utilized FA </div>
                    <div class="metric-value">{utilized_flight_attendant}</div>
                </div>
            ''', unsafe_allow_html=True)

        # Gap 2 - Visual separator
        with gap2:
            st.markdown('<div style="border-left: 3px solid rgba(255,255,255,0.3); height: 100px; margin: 0 auto;"></div>', unsafe_allow_html=True)

        # 🕐 Standby Crew (grouped together)
        total_standby = Standyby_captain + Standyby_first_officer + Standyby_flight_attendant

        with col8:
            st.markdown(f'''
                <div class="metric-card" style="background: linear-gradient(135deg, #f59e0b 0%, #d97706 100%);">
                    <div class="metric-label">Total Standby</div>
                    <div class="metric-value">{total_standby}</div>
                </div>
            ''', unsafe_allow_html=True)

        with col9:
            st.markdown(f'''
                <div class="metric-card" style="background: linear-gradient(135deg, #f59e0b 0%, #d97706 100%);">
                    <div class="metric-label">Standby Cap</div>
                    <div class="metric-value">{Standyby_captain}</div>
                </div>
            ''', unsafe_allow_html=True)

        with col10:
            st.markdown(f'''
                <div class="metric-card" style="background: linear-gradient(135deg, #f59e0b 0%, #d97706 100%);">
                    <div class="metric-label">Standby FO</div>
                    <div class="metric-value">{Standyby_first_officer}</div>
                </div>
            ''', unsafe_allow_html=True)

        with col11:
            st.markdown(f'''
                <div class="metric-card" style="background: linear-gradient(135deg, #f59e0b 0%, #d97706 100%);">
                    <div class="metric-label">Standby FA</div>
                    <div class="metric-value">{Standyby_flight_attendant}</div>
                </div>
            ''', unsafe_allow_html=True)

        st.markdown('</div>', unsafe_allow_html=True)

        st.subheader(f"")

        st.markdown('<div class="dashboard-card">', unsafe_allow_html=True)


        


        



        import plotly.express as px



        def create_top_performers_charts(df_validation, df_validation_captain, df_validation_FO, df_validation_FA):
        
            # Configuration
            TOP_N = 300
            
            # Define crew categories
            crew_categories = {
                'All Crew': df_validation,
                'Captains': df_validation_captain,
                'First Officers': df_validation_FO,
                'Flight Attendants': df_validation_FA
            }
            
            # Define metrics to analyze
            metrics = {
                'Block hours': {
                    'column': 'Block hours',
                    'title_suffix': 'Block Hours',
                    'y_label': 'Block Hours'
                },
                'Sectors': {
                    'column': 'Total sectors',
                    'title_suffix': 'Total sectors',
                    'y_label': 'Number of Total sectors'
                }
            }
            
            # Create charts for each metric
            for metric_name, metric_config in metrics.items():
                st.subheader(f"Top Crew by {metric_config['title_suffix']}")
                
                # Create columns for side-by-side display
                cols = st.columns(4)
                
                # Generate chart for each crew category
                for idx, (category_name, df) in enumerate(crew_categories.items()):
                    # Get top N performers
                    top_performers = df.nlargest(TOP_N, metric_config['column'])
                    
                    # Create interactive bar chart
                    fig = px.bar(
                        top_performers,
                        x='Crew code',
                        y=metric_config['column'],
                        title=f" {category_name}",
                        labels={
                            'Crew code': 'Crew Code',
                            metric_config['column']: metric_config['y_label']
                        },
                        hover_data=[metric_config['column']],
                        color_discrete_sequence=['#1f77b4']  # Consistent color scheme
                    )
                    
                    # Update layout for better readability
                    fig.update_layout(
                        xaxis_tickangle=-45,
                        height=400,
                        margin=dict(l=20, r=20, t=40, b=20)
                    )
                    
                    # Display chart in appropriate column
                    with cols[idx]:
                        st.plotly_chart(fig, use_container_width=True)
                
                # Add spacing between metrics
                st.markdown("---")

        


        # Usage in your Streamlit app
        create_top_performers_charts(
            df_validation,
            df_validation_captain,
            df_validation_FO,
            df_validation_FA
        )


        col1,col2,col3,col4=st.columns(4)

        with col1:
            fig_pie1 = px.pie(
                df_validation,
                names='No. of swaps',  # Replace 'X' with your actual column name
                title='Crew swaps',
                hole=0.3  # Optional: creates a donut chart (remove if you want a full pie)
            )

            st.plotly_chart(fig_pie1, use_container_width=True)


        with col2:
            fig_pie2 = px.pie(
                df_validation_captain,
                names='No. of swaps',  # Replace 'X' with your actual column name
                title='Captains swaps',
                hole=0.3  # Optional: creates a donut chart (remove if you want a full pie)
            )

            st.plotly_chart(fig_pie2, use_container_width=True)

        with col3:
            fig_pie3 = px.pie(
                df_validation_FO,
                names='No. of swaps',  # Replace 'X' with your actual column name
                title='First officer swaps',
                hole=0.3  # Optional: creates a donut chart (remove if you want a full pie)
            )

            st.plotly_chart(fig_pie3, use_container_width=True)

        with col4:
            fig_pie4 = px.pie(
                df_validation_FA,
                names='No. of swaps',  # Replace 'X' with your actual column name
                title='Flight Attendant swaps',
                hole=0.3  # Optional: creates a donut chart (remove if you want a full pie)
            )

            st.plotly_chart(fig_pie4, use_container_width=True)




        st.markdown('<div class="section-header">📊 Common Profile Crews</div>', unsafe_allow_html=True)

        st.markdown('<div class="dashboard-card">', unsafe_allow_html=True)


        crew_groups=validation_report_1.merge(crew_aircraft,on="Crew code")
        crew_groups.to_excel("Sample clustering.xlsx")
        df_grouped=cluster_fun(crew_groups)
        st.dataframe(df_grouped)


                
        col1, col2, col3 = st.columns([1, 1, 1])
        with col2:
            st.download_button(
                label="📥 Download Full Validation Report",
                data=output,
                file_name=f"TMA_validation_report_{schedule_date}.xlsx",
                mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
                use_container_width=True
            )

        