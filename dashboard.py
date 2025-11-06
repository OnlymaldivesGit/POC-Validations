import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from datetime import datetime, time
import numpy as np

# Page configuration
st.set_page_config(
    page_title="Flight Schedule Dashboard",
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
        font-size: 0.9rem;
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

# Header with gradient
st.markdown("""
    <div class="dashboard-header">
        <div class="dashboard-title">✈️ Flight Schedule Roster Dashboard</div>
        <div class="dashboard-subtitle">Comprehensive Aircraft & Crew Analytics</div>
    </div>
""", unsafe_allow_html=True)

# File uploader
uploaded_file = st.file_uploader("Upload Schedule Roster (CSV/Excel)", type=['csv', 'xlsx', 'xls'])

if uploaded_file is not None:
    # Load data
    try:
        if uploaded_file.name.endswith('.csv'):
            df = pd.read_csv(uploaded_file)
        else:
            df = pd.read_excel(uploaded_file)
        
        # Clean column names
        df.columns = df.columns.str.strip()
        
        # Convert date and time columns
        df['Date'] = pd.to_datetime(df['Date'], errors='coerce')
        
        # Parse STD and STA times
        def parse_time(time_str):
            if pd.isna(time_str):
                return None
            try:
                time_str = str(time_str).strip()
                if ':' in time_str:
                    return pd.to_datetime(time_str, format='%H:%M').time()
                else:
                    return pd.to_datetime(time_str, format='%H%M').time()
            except:
                return None
        
        df['STD'] = df['STD -  Scheduled Departure'].apply(parse_time)
        df['STA'] = df['STA -  Scheduled Arrival'].apply(parse_time)
        
        # Display data preview
        with st.expander("📋 Data Preview", expanded=False):
            st.dataframe(df.head(10), use_container_width=True)
        
        st.markdown("<br>", unsafe_allow_html=True)
        
        # =======================
        # KEY METRICS - ROW 1
        # =======================
        st.markdown('<div class="section-header">📊 Key Performance Indicators</div>', unsafe_allow_html=True)
        
        col1, col2, col3, col4 = st.columns(4)
        
        # 1. Total Aircraft
        total_aircraft = df['Aircraft No.'].nunique()
        
        # Get first and last occurrence of each aircraft
        aircraft_schedule = df.groupby('Aircraft No.').agg({
            'Date': ['min', 'max'],
            'STD': 'first',
            'STA': 'last'
        }).reset_index()
        
        aircraft_schedule.columns = ['Aircraft', 'First_Date', 'Last_Date', 'Start_Time', 'End_Time']
        
        # Aircraft starting ON (first flight of the day)
        ac_starting = len(aircraft_schedule)
        
        # Aircraft ending ON (last flight of the day)
        ac_ending = len(aircraft_schedule)
        
        with col1:
            st.metric("Total Aircraft", total_aircraft, delta=None, delta_color="off")
        with col2:
            st.metric("AC Starting ON", ac_starting, delta=None, delta_color="normal")
        with col3:
            st.metric("AC Ending ON", ac_ending, delta=None, delta_color="normal")
        with col4:
            # 2. Total Flights
            total_flights = df['Flight No.'].nunique()
            st.metric("Total Flights", total_flights)
        
        st.markdown("<br>", unsafe_allow_html=True)
        
        # =======================
        # KEY METRICS - ROW 2
        # =======================
        col5, col6, col7, col8 = st.columns(4)
        
        # 3. Total Sectors (each row is a sector/leg)
        total_sectors = len(df)
        
        with col5:
            st.metric("Total Sectors", total_sectors)
        
        # Route statistics
        with col6:
            unique_routes = df.groupby(['Dep. Airport', 'Arr. Airport']).size().reset_index()
            st.metric("Unique Routes", len(unique_routes))
        
        # Date range
        with col7:
            date_range = (df['Date'].max() - df['Date'].min()).days + 1
            st.metric("Schedule Days", date_range)
        
        # Average sectors per aircraft
        with col8:
            avg_sectors = total_sectors / total_aircraft
            st.metric("Avg Sectors/AC", f"{avg_sectors:.1f}")
        
        st.markdown("<br><br>", unsafe_allow_html=True)
        
        # =======================
        # CREW ANALYTICS
        # =======================
        st.markdown('<div class="section-header">👨‍✈️ Crew Resource Analysis</div>', unsafe_allow_html=True)
        
        # Function to parse crew members (handles comma-separated values)
        def parse_crew(crew_str):
            if pd.isna(crew_str):
                return []
            return [c.strip() for c in str(crew_str).split(',') if c.strip()]
        
        # Count crew members
        captains = set()
        first_officers = set()
        flight_attendants = set()
        
        utilized_captains = set()
        utilized_fos = set()
        utilized_fas = set()
        
        standby_captains = set()
        standby_fos = set()
        standby_fas = set()
        
        # Track sector counts per crew member
        captain_sectors = {}
        fo_sectors = {}
        fa_sectors = {}
        
        for idx, row in df.iterrows():
            caps = parse_crew(row['Captain'])
            fos = parse_crew(row['First Officer'])
            fas = parse_crew(row['Flight Attendant'])
            
            for cap in caps:
                captains.add(cap)
                if 'STBY' in cap.upper() or 'STANDBY' in cap.upper():
                    standby_captains.add(cap)
                else:
                    utilized_captains.add(cap)
                    captain_sectors[cap] = captain_sectors.get(cap, 0) + 1
            
            for fo in fos:
                first_officers.add(fo)
                if 'STBY' in fo.upper() or 'STANDBY' in fo.upper():
                    standby_fos.add(fo)
                else:
                    utilized_fos.add(fo)
                    fo_sectors[fo] = fo_sectors.get(fo, 0) + 1
            
            for fa in fas:
                flight_attendants.add(fa)
                if 'STBY' in fa.upper() or 'STANDBY' in fa.upper():
                    standby_fas.add(fa)
                else:
                    utilized_fas.add(fa)
                    fa_sectors[fa] = fa_sectors.get(fa, 0) + 1
        
        # Display crew metrics in tabs
        tab1, tab2, tab3 = st.tabs(["📊 Overview", "✅ Available", "🔄 Standby"])
        
        with tab1:
            col_c1, col_c2, col_c3 = st.columns(3)
            
            with col_c1:
                st.markdown("### 👨‍✈️ Captains")
                st.metric("Total Available", len(captains))
                st.metric("Utilized", len(utilized_captains))
                st.metric("Standby", len(standby_captains))
                if len(captains) > 0:
                    utilization = (len(utilized_captains) / len(captains)) * 100
                    st.progress(utilization / 100)
                    st.caption(f"Utilization: {utilization:.1f}%")
            
            with col_c2:
                st.markdown("### 👨‍✈️ First Officers")
                st.metric("Total Available", len(first_officers))
                st.metric("Utilized", len(utilized_fos))
                st.metric("Standby", len(standby_fos))
                if len(first_officers) > 0:
                    utilization = (len(utilized_fos) / len(first_officers)) * 100
                    st.progress(utilization / 100)
                    st.caption(f"Utilization: {utilization:.1f}%")
            
            with col_c3:
                st.markdown("### 👨‍✈️ Flight Attendants")
                st.metric("Total Available", len(flight_attendants))
                st.metric("Utilized", len(utilized_fas))
                st.metric("Standby", len(standby_fas))
                if len(flight_attendants) > 0:
                    utilization = (len(utilized_fas) / len(flight_attendants)) * 100
                    st.progress(utilization / 100)
                    st.caption(f"Utilization: {utilization:.1f}%")
        
        with tab2:
            col_av1, col_av2, col_av3 = st.columns(3)
            with col_av1:
                st.markdown("**Captains**")
                st.write(sorted(list(captains)))
            with col_av2:
                st.markdown("**First Officers**")
                st.write(sorted(list(first_officers)))
            with col_av3:
                st.markdown("**Flight Attendants**")
                st.write(sorted(list(flight_attendants)))
        
        with tab3:
            col_sb1, col_sb2, col_sb3 = st.columns(3)
            with col_sb1:
                st.markdown("**Captains**")
                if standby_captains:
                    st.write(sorted(list(standby_captains)))
                else:
                    st.info("No standby captains")
            with col_sb2:
                st.markdown("**First Officers**")
                if standby_fos:
                    st.write(sorted(list(standby_fos)))
                else:
                    st.info("No standby first officers")
            with col_sb3:
                st.markdown("**Flight Attendants**")
                if standby_fas:
                    st.write(sorted(list(standby_fas)))
                else:
                    st.info("No standby flight attendants")
        
        st.markdown("<br><br>", unsafe_allow_html=True)
        
        # =======================
        # TIME BUCKET ANALYSIS (2x2 MATRIX)
        # =======================
        st.markdown('<div class="section-header">⏰ Aircraft Schedule Time Matrix</div>', unsafe_allow_html=True)
        
        # Define time buckets
        def get_time_bucket(t):
            if t is None:
                return "Unknown"
            hour = t.hour
            if 0 <= hour < 6:
                return "00:00-06:00 (Night)"
            elif 6 <= hour < 12:
                return "06:00-12:00 (Morning)"
            elif 12 <= hour < 18:
                return "12:00-18:00 (Afternoon)"
            else:
                return "18:00-00:00 (Evening)"
        
        aircraft_schedule['Start_Bucket'] = aircraft_schedule['Start_Time'].apply(get_time_bucket)
        aircraft_schedule['End_Bucket'] = aircraft_schedule['End_Time'].apply(get_time_bucket)
        
        # Create pivot table for matrix
        matrix_data = aircraft_schedule.groupby(['Start_Bucket', 'End_Bucket']).size().reset_index(name='Count')
        matrix_pivot = matrix_data.pivot(index='Start_Bucket', columns='End_Bucket', values='Count').fillna(0)
        
        # Reorder for better visualization
        bucket_order = ["00:00-06:00 (Night)", "06:00-12:00 (Morning)", "12:00-18:00 (Afternoon)", "18:00-00:00 (Evening)"]
        matrix_pivot = matrix_pivot.reindex(index=bucket_order, columns=bucket_order, fill_value=0)
        
        # Create heatmap
        fig_matrix = go.Figure(data=go.Heatmap(
            z=matrix_pivot.values,
            x=matrix_pivot.columns,
            y=matrix_pivot.index,
            colorscale='Blues',
            text=matrix_pivot.values,
            texttemplate='%{text}',
            textfont={"size": 16},
            hoverongaps=False
        ))
        
        fig_matrix.update_layout(
            title="Aircraft Starting vs Ending Time Buckets",
            xaxis_title="Ending Time",
            yaxis_title="Starting Time",
            height=500,
            font=dict(size=12),
            paper_bgcolor='rgba(0,0,0,0)',
            plot_bgcolor='rgba(0,0,0,0)'
        )
        
        st.plotly_chart(fig_matrix, use_container_width=True)
        
        st.markdown("<br><br>", unsafe_allow_html=True)
        
        # =======================
        # CREW UTILIZATION ANALYSIS
        # =======================
        st.markdown('<div class="section-header">📈 Crew Utilization Analysis</div>', unsafe_allow_html=True)
        
        # Prepare data for most and least utilized crew
        captain_df = pd.DataFrame(list(captain_sectors.items()), columns=['Name', 'Sectors']).sort_values('Sectors', ascending=False)
        fo_df = pd.DataFrame(list(fo_sectors.items()), columns=['Name', 'Sectors']).sort_values('Sectors', ascending=False)
        fa_df = pd.DataFrame(list(fa_sectors.items()), columns=['Name', 'Sectors']).sort_values('Sectors', ascending=False)
        
        # Create tabs for different crew types
        crew_tab1, crew_tab2, crew_tab3 = st.tabs(["👨‍✈️ Captains", "👨‍✈️ First Officers", "👩‍✈️ Flight Attendants"])
        
        with crew_tab1:
            col_cap1, col_cap2 = st.columns(2)
            
            with col_cap1:
                st.markdown("#### Top 10 Most Utilized Captains")
                if len(captain_df) > 0:
                    top_captains = captain_df.head(10)
                    fig_cap_top = px.bar(
                        top_captains,
                        x='Sectors',
                        y='Name',
                        orientation='h',
                        color='Sectors',
                        color_continuous_scale='Greens',
                        text='Sectors'
                    )
                    fig_cap_top.update_layout(
                        showlegend=False,
                        height=400,
                        yaxis={'categoryorder': 'total ascending'},
                        paper_bgcolor='rgba(0,0,0,0)',
                        plot_bgcolor='rgba(0,0,0,0)'
                    )
                    fig_cap_top.update_traces(textposition='outside')
                    st.plotly_chart(fig_cap_top, use_container_width=True)
                else:
                    st.info("No captain data available")
            
            with col_cap2:
                st.markdown("#### Top 10 Least Utilized Captains")
                if len(captain_df) > 0:
                    bottom_captains = captain_df.tail(10).sort_values('Sectors', ascending=True)
                    fig_cap_bottom = px.bar(
                        bottom_captains,
                        x='Sectors',
                        y='Name',
                        orientation='h',
                        color='Sectors',
                        color_continuous_scale='Reds',
                        text='Sectors'
                    )
                    fig_cap_bottom.update_layout(
                        showlegend=False,
                        height=400,
                        yaxis={'categoryorder': 'total ascending'},
                        paper_bgcolor='rgba(0,0,0,0)',
                        plot_bgcolor='rgba(0,0,0,0)'
                    )
                    fig_cap_bottom.update_traces(textposition='outside')
                    st.plotly_chart(fig_cap_bottom, use_container_width=True)
                else:
                    st.info("No captain data available")
        
        with crew_tab2:
            col_fo1, col_fo2 = st.columns(2)
            
            with col_fo1:
                st.markdown("#### Top 10 Most Utilized First Officers")
                if len(fo_df) > 0:
                    top_fos = fo_df.head(10)
                    fig_fo_top = px.bar(
                        top_fos,
                        x='Sectors',
                        y='Name',
                        orientation='h',
                        color='Sectors',
                        color_continuous_scale='Greens',
                        text='Sectors'
                    )
                    fig_fo_top.update_layout(
                        showlegend=False,
                        height=400,
                        yaxis={'categoryorder': 'total ascending'},
                        paper_bgcolor='rgba(0,0,0,0)',
                        plot_bgcolor='rgba(0,0,0,0)'
                    )
                    fig_fo_top.update_traces(textposition='outside')
                    st.plotly_chart(fig_fo_top, use_container_width=True)
                else:
                    st.info("No first officer data available")
            
            with col_fo2:
                st.markdown("#### Top 10 Least Utilized First Officers")
                if len(fo_df) > 0:
                    bottom_fos = fo_df.tail(10).sort_values('Sectors', ascending=True)
                    fig_fo_bottom = px.bar(
                        bottom_fos,
                        x='Sectors',
                        y='Name',
                        orientation='h',
                        color='Sectors',
                        color_continuous_scale='Reds',
                        text='Sectors'
                    )
                    fig_fo_bottom.update_layout(
                        showlegend=False,
                        height=400,
                        yaxis={'categoryorder': 'total ascending'},
                        paper_bgcolor='rgba(0,0,0,0)',
                        plot_bgcolor='rgba(0,0,0,0)'
                    )
                    fig_fo_bottom.update_traces(textposition='outside')
                    st.plotly_chart(fig_fo_bottom, use_container_width=True)
                else:
                    st.info("No first officer data available")
        
        with crew_tab3:
            col_fa1, col_fa2 = st.columns(2)
            
            with col_fa1:
                st.markdown("#### Top 10 Most Utilized Flight Attendants")
                if len(fa_df) > 0:
                    top_fas = fa_df.head(10)
                    fig_fa_top = px.bar(
                        top_fas,
                        x='Sectors',
                        y='Name',
                        orientation='h',
                        color='Sectors',
                        color_continuous_scale='Greens',
                        text='Sectors'
                    )
                    fig_fa_top.update_layout(
                        showlegend=False,
                        height=400,
                        yaxis={'categoryorder': 'total ascending'},
                        paper_bgcolor='rgba(0,0,0,0)',
                        plot_bgcolor='rgba(0,0,0,0)'
                    )
                    fig_fa_top.update_traces(textposition='outside')
                    st.plotly_chart(fig_fa_top, use_container_width=True)
                else:
                    st.info("No flight attendant data available")
            
            with col_fa2:
                st.markdown("#### Top 10 Least Utilized Flight Attendants")
                if len(fa_df) > 0:
                    bottom_fas = fa_df.tail(10).sort_values('Sectors', ascending=True)
                    fig_fa_bottom = px.bar(
                        bottom_fas,
                        x='Sectors',
                        y='Name',
                        orientation='h',
                        color='Sectors',
                        color_continuous_scale='Reds',
                        text='Sectors'
                    )
                    fig_fa_bottom.update_layout(
                        showlegend=False,
                        height=400,
                        yaxis={'categoryorder': 'total ascending'},
                        paper_bgcolor='rgba(0,0,0,0)',
                        plot_bgcolor='rgba(0,0,0,0)'
                    )
                    fig_fa_bottom.update_traces(textposition='outside')
                    st.plotly_chart(fig_fa_bottom, use_container_width=True)
                else:
                    st.info("No flight attendant data available")
        
        st.markdown("<br><br>", unsafe_allow_html=True)
        
        # =======================
        # ADDITIONAL INSIGHTS
        # =======================
        st.markdown('<div class="section-header">📊 Aircraft Workload Distribution</div>', unsafe_allow_html=True)
        
        # Flight distribution by aircraft
        sectors_per_ac = df.groupby('Aircraft No.').size().reset_index(name='Sectors')
        fig_ac = px.bar(
            sectors_per_ac.sort_values('Sectors', ascending=False),
            x='Aircraft No.',
            y='Sectors',
            color='Sectors',
            color_continuous_scale='Viridis',
            title="Sectors per Aircraft"
        )
        fig_ac.update_layout(
            showlegend=False,
            height=400,
            paper_bgcolor='rgba(0,0,0,0)',
            plot_bgcolor='rgba(0,0,0,0)'
        )
        st.plotly_chart(fig_ac, use_container_width=True)
        
        st.markdown("<br>", unsafe_allow_html=True)
        
        # Success message
        st.markdown("""
            <div class="success-message">
                ✅ Dashboard generated successfully! All metrics and visualizations are ready.
            </div>
        """, unsafe_allow_html=True)
        
    except Exception as e:
        st.markdown(f"""
            <div class="error-message">
                ❌ Error processing file: {str(e)}
            </div>
        """, unsafe_allow_html=True)
        st.info("Please ensure your file has the correct column headers and format.")

else:
    # Landing page with instructions
    st.markdown("""
        <div class="info-box">
            <h3>👆 Please upload your schedule roster file to view the dashboard</h3>
        </div>
    """, unsafe_allow_html=True)
    
    st.markdown("""
    ### 📋 Expected File Format
    
    Your CSV/Excel file should contain the following columns:
    - **Date**: Schedule date
    - **Aircraft No.**: Aircraft registration/number
    - **Flight No.**: Flight number
    - **STD - Scheduled Departure**: Departure time (HH:MM format)
    - **STA - Scheduled Arrival**: Arrival time (HH:MM format)
    - **Dep. Airport**: Departure airport code
    - **Arr. Airport**: Arrival airport code
    - **Captain**: Captain name(s)
    - **First Officer**: First Officer name(s)
    - **Flight Attendant**: Flight Attendant name(s)
    - **Leg No.**: Leg number
    
    ### 📊 Dashboard Features
    - ✈️ Aircraft utilization metrics
    - 👨‍✈️ Comprehensive crew analytics
    - ⏰ Time-based schedule analysis (2x2 Matrix)
    - 📈 Top 10 Most & Least Utilized Crew (by type)
    - 💼 Crew workload insights with utilization percentages
    - 🛫 Aircraft workload distribution
    """)