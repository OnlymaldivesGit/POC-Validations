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



available_status=["1","Li","LC"]
leave_status=["X","AL","AU","PAL","EM","ML","M"]


from input_processing import schedule_input_processing
from input_processing import  aircraft_processing
from input_processing import  crew_aircraft_processing
from input_processing import  crew_stats_processing
from input_processing import  logsheet_processing
from input_processing import  month_plan_processing
from input_processing import  flight_training_processing
from input_processing import  expiry_data_processing
from input_processing import  seniority_processing
from input_processing import  crew_master_processing
from input_processing import merged_data_fun
from input_processing import crew_stats_xml 




from output_processing import  Schedule_output_processing
from output_processing import  Schedule_output_processing_2
from output_processing import  output_master_processing
from output_processing import  crew_ac_stats_processing
from input_validations import input_validation_fun

from checklist import Schedule_check_fun
from checklist import crew_check_fun
from checklist import aircraft_check
from checklist import Stats_check_fun
from checklist import swaps_check_fun
from checklist import seniority_check_fun
from checklist import training_pairing_check
from checklist import get_short_time_diffs



with st.sidebar:
    selected = option_menu(
        menu_title="Modules",  # Sidebar title
        options=[
            "Crew stats generator",
            "Input Data Validator", 
            "Constraints Validator"
        ],
        icons=["file-earmark-excel","file-earmark-excel",  "bar-chart"],
        menu_icon="gear",  # Top icon
        default_index=0,
        orientation="vertical"  # Ensures vertical left-side layout
    )

    
if selected == "Crew stats generator":
    crewstats_xml = st.file_uploader("Select crew stats macro", type=["xlsm"])

    if st.button("Generate the report"):
        if crewstats_xml is not None:
            sectors = pd.read_excel(crewstats_xml, engine='openpyxl', sheet_name="Sectors")
            flt = pd.read_excel(crewstats_xml, engine='openpyxl', sheet_name="FLT")
            day_27th = pd.read_excel(crewstats_xml, engine='openpyxl', sheet_name="27 Days")
            day_364th = pd.read_excel(crewstats_xml, engine='openpyxl', sheet_name="364 Days")

        crew_stats_output,crew_stats_output_2=crew_stats_xml(sectors,flt,day_27th,day_364th)

        output = io_module.BytesIO()
        with pd.ExcelWriter(output, engine='xlsxwriter') as writer:
            crew_stats_output.to_excel(writer, sheet_name='crew stats', index=False)
            crew_stats_output_2.to_excel(writer, sheet_name='crew stats validator', index=False)

        st.dataframe(crew_stats_output_2)

        output.seek(0)

        st.download_button(
            label="📥 Download crew stats",
            data=output,
            file_name="Crewstats.xlsx",
            mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
        )


if selected == "Input Data Validator" or selected == "Constraints Validator":

    schedule_date = st.date_input("Select schedule date")
    schedule_date = schedule_date.strftime("%Y-%m-%d")
    prev_day = (datetime.strptime(schedule_date, "%Y-%m-%d") - timedelta(days=1)).strftime("%Y-%m-%d")
    next_day = (datetime.strptime(schedule_date, "%Y-%m-%d") + timedelta(days=1)).strftime("%Y-%m-%d")

    start_date = date(2025, 9, 1).strftime("%Y-%m-%d")
    end_date = date(2025, 9, 8).strftime("%Y-%m-%d")

    if start_date <= schedule_date <= end_date:
        aircraft=pd.read_excel("Model Validations/Aircrafts.xlsx")
        crew_aircraft=pd.read_excel("Model Validations/Crew AC Matrix.xlsx")
        seniority=pd.read_excel("Model Validations/Crew Pairing.xlsx")
        logsheet=pd.read_excel("Model Validations/Log sheet.xlsx")
        crew_master=pd.read_excel("Model Validations/Resources.xlsx")
        expiry_data=pd.read_excel("Model Validations/Training Expiry.xlsx")
        flight_training=pd.read_excel("Model Validations/Training Pairings.xlsx")
        month_plan=pd.read_excel("Model Validations/Month plan.xlsx")
        crew_stats=pd.read_excel("Model Validations/Crew Stats.xlsx",sheet_name=schedule_date)
    else:
        aircraft_input = st.file_uploader("Select aircraft data", type=["xlsx", "xls"])
        crew_aircraft_input = st.file_uploader("Select crew aircraft matrix", type=["xlsx", "xls"])
        seniority_input = st.file_uploader("Select seniority pairing sheet", type=["xlsx", "xls"])
        logsheet_input = st.file_uploader("Select the logsheet", type=["xlsx", "xls"])
        crew_master_input = st.file_uploader("Select crew master data", type=["xlsx", "xls"])
        expiry_data_input = st.file_uploader("Select the crew expiry", type=["xlsx", "xls"])
        flight_training_input= st.file_uploader("Select the flight training", type=["xlsx", "xls"])
        month_plan_input = st.file_uploader("Select the monthly plan", type=["xlsx", "xls"])
        crew_stats_input = st.file_uploader("Select the crew stats", type=["xlsx", "xls"])


        if aircraft_input is not None:
            aircraft=pd.read_excel(aircraft_input)

        if crew_aircraft_input is not None:
            crew_aircraft=pd.read_excel(crew_aircraft_input)

        if seniority_input is not None:
            seniority=pd.read_excel(seniority_input)

        if logsheet_input is not None:
            logsheet=pd.read_excel(logsheet_input)

        if crew_master_input is not None:
            crew_master=pd.read_excel(crew_master_input)

        if expiry_data_input is not None:
            expiry_data=pd.read_excel(expiry_data_input)

        if flight_training_input is not None:
            flight_training=pd.read_excel(flight_training_input)

        if month_plan_input is not None:
            month_plan=pd.read_excel(month_plan_input)

        if crew_stats_input is not None:
            crew_stats=pd.read_excel(crew_stats_input,sheet_name=schedule_date)





    



if selected == "Input Data Validator":
    if st.button("Validate the data"):
        aircraft=aircraft_processing(aircraft)
        crew_aircraft=crew_aircraft_processing(crew_aircraft)
        seniority=seniority_processing(seniority)
        logsheet=logsheet_processing(logsheet,prev_day)
        crew_master=crew_master_processing(crew_master)
        expiry_data=expiry_data_processing(expiry_data)
        flight_training=flight_training_processing(flight_training,schedule_date)
        month_plan=month_plan_processing(month_plan,schedule_date,prev_day,next_day)
        crew_stats=crew_stats_processing(crew_stats)


        merged_df=merged_data_fun(month_plan,crew_master, seniority, expiry_data, logsheet,crew_stats)
    
        input_issue_1,input_issue_2=input_validation_fun(merged_df)

        with st.spinner("⚪️ Validating the data..."):
            placeholder1_1 = st.empty()
            placeholder1_1.markdown("✅ First Validation Completed")
            st.dataframe(input_issue_1)
            st.markdown(
            "The table above shows the list of Crew data where crew resorts are missing except their stats",
            unsafe_allow_html=True
            )

        with st.spinner("⚪️ Validating the data..."):
            placeholder1_2 = st.empty()
            placeholder1_2.markdown("✅ Second Validation Completed")
            st.dataframe(input_issue_2)
            st.markdown(
            "The table above shows the list of Crew  where their stats are missing ",
            unsafe_allow_html=True
            )


            output = io_module.BytesIO()
            with pd.ExcelWriter(output, engine='xlsxwriter') as writer:
                input_issue_1.to_excel(writer, sheet_name='Validation 1', index=False)
                input_issue_2.to_excel(writer, sheet_name='Validation 2', index=False)
                merged_df.to_excel(writer, sheet_name='Input data ', index=False)

            output.seek(0)

            st.download_button(
                label="📥 Download Validation Report",
                data=output,
                file_name="input_validation.xlsx",
                mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
            )



if selected == "Constraints Validator":
    input_flight_plan = st.file_uploader("Select input flight plan", type=["xlsx", "xls"])
    output_flight_plan = st.file_uploader("Select the solver output", type=["xlsx", "xls"])

    if input_flight_plan is not None:
        Schedule_input=pd.read_excel(input_flight_plan)

    if output_flight_plan is not None:
        Schedule_output=pd.read_excel(output_flight_plan)

    if st.button("Validate the data"):

        aircraft=aircraft_processing(aircraft)
        crew_aircraft=crew_aircraft_processing(crew_aircraft)
        seniority=seniority_processing(seniority)
        logsheet=logsheet_processing(logsheet,prev_day)
        crew_master=crew_master_processing(crew_master)
        expiry_data=expiry_data_processing(expiry_data)
        flight_training=flight_training_processing(flight_training,schedule_date)
        month_plan=month_plan_processing(month_plan,schedule_date,prev_day,next_day)
        crew_stats=crew_stats_processing(crew_stats)
        Schedule_input=schedule_input_processing(Schedule_input)


        merged_df=merged_data_fun(month_plan,crew_master, seniority, expiry_data, logsheet,crew_stats)

        Schedule_output=Schedule_output_processing(Schedule_output)
        Schedule_output_2=Schedule_output_processing_2(Schedule_output)
        output_master,output_crew_stats=output_master_processing(Schedule_output_2)

        crew_ac_stats=crew_ac_stats_processing(Schedule_output_2,aircraft,crew_aircraft)
        comparison_master =  merged_df.merge(output_master, on="Crew code", how="outer")

        available_working = comparison_master[(comparison_master["Schedule Day"].isin(available_status)) & (~comparison_master["Working Status"].isna())]
        Standby_crew = comparison_master[ (comparison_master["Schedule Day"].isin(available_status)) &(comparison_master["Working Status"].isna())]
        
        leaves_working=comparison_master[(comparison_master["Schedule Day"].isin(leave_status)) & (~comparison_master["Working Status"].isna())]
        
        on_training=comparison_master[~(comparison_master["Schedule Day"].isin(leave_status+available_status))]
        on_training_working=on_training[~comparison_master["Working Status"].isna()]
        training_non_outstations = on_training[(on_training["Outstation airport"].isin(["", "MLE"]))]

        with st.spinner("⚪️ Validating the Schedule..."):
            placeholder1 = st.empty()
            Schedule_check=Schedule_check_fun(Schedule_output,Schedule_input)
            placeholder1.markdown("✅ Schedule Validated")

        with st.spinner("⚪️ Validating the Crew Dependency..."):
            placeholder2 = st.empty()
            crew_mistake_1, crew_mistake_11,crew_mistake_2,crew_mistake_3=crew_check_fun(comparison_master,available_working)
            placeholder2.markdown("✅ Crew Dependency Validated")

        with st.spinner("⚪️ Validating the Aicraft Dependency..."):
            placeholder3 = st.empty()
            aircraft_issue=aircraft_check(crew_ac_stats)
            placeholder3.markdown("✅ Aicraft Dependency Validated")

        with st.spinner("⚪️ Validating the crew FTL Depenedency..."):
            placeholder4 = st.empty()
            Block_hour_issue_1,Block_hour_issue_2,duty_hour_issue,sector_issue_1,sector_issue_2=Stats_check_fun(available_working)
            placeholder4.markdown("✅ Crew FTL Dependency Validated")

        with st.spinner("⚪️ Validating the crew swaps..."):
            placeholder5 = st.empty()
            swaps_issue=swaps_check_fun(output_master)
            placeholder5.markdown("✅ Crew swaps Validated")

        with st.spinner("⚪️ Validating the seniority pairings..."):
            placeholder6 = st.empty()
            pairings_issue_1, LTC_check=seniority_check_fun(Schedule_output,merged_df)
            placeholder6.markdown("✅ Seniority pairings Validated")

        with st.spinner("⚪️ Validating the Training Pairings..."):
            placeholder6 = st.empty()
            training_issue=training_pairing_check(flight_training, Schedule_output)
            placeholder6.markdown("✅ Training Pairings Validated")

        with st.spinner("⚪️ Validating the time difference between AC..."):
            placeholder7 = st.empty()
            get_short_time_diffs_df=get_short_time_diffs(crew_ac_stats)
            placeholder7.markdown("✅ Time differences Validated")



        # Print of Data


        with st.expander("Standby crew"):
            if Standby_crew.empty:
                st.markdown("All crew has been utilized",unsafe_allow_html=True)
            else:
                st.dataframe(Standby_crew)
                st.markdown(
                "Following crew has been kept for standby for the full day",
                unsafe_allow_html=True
                )


        with st.expander("Schedule check"):
            if Schedule_check.empty:
                st.markdown("No error in Schedule",unsafe_allow_html=True)
            else:
                st.dataframe(Schedule_check)
                st.markdown(
                "The table above shows the list of sectors, Flights, AC which have been modified in the output data",
                unsafe_allow_html=True
                )

        with st.expander("Non Available crew check"):
            if leaves_working.empty:
                st.markdown("No crew on leave is being scheduled",unsafe_allow_html=True)
            else:
                st.dataframe(leaves_working[["Crew code","Schedule Day","Working Status"]])
                st.markdown(
                "The table above shows the list of crew who are on leave but has been allocated to Flights",
                unsafe_allow_html=True
                )

        with st.expander("Error in crew on Training"):
            if crew_mistake_1.empty:
                st.markdown("No error with crew who are on training and at base",unsafe_allow_html=True)
            else:
                st.dataframe(crew_mistake_1)
                st.markdown(
                "The table above shows the list of crew who are on training and at base last night but has been scheduled to Flight ",
                unsafe_allow_html=True
                )
            
            if crew_mistake_11.empty:
                st.markdown("No error with crew who are on training and at outstation",unsafe_allow_html=True)
            else:
                st.dataframe(crew_mistake_11)
                st.markdown(
                "The table above shows the list of crew who are working and on Trainings starting from Outstation but has not 1 Flights",
                unsafe_allow_html=True
                )

        with st.expander("Error in Starting points"):
            if crew_mistake_2.empty:
                st.markdown("No error in crew starting point",unsafe_allow_html=True)
            else:
                st.dataframe(crew_mistake_2)
                st.markdown(
                "The table above shows the list of Crew with mismatch Starting points ",
                unsafe_allow_html=True
                )


        with st.expander("Error in next day overnights assignment"):
            if crew_mistake_3.empty:
                st.markdown("No error with overnight assigment for next day",unsafe_allow_html=True)
            else:
                st.dataframe(crew_mistake_3)
                st.markdown(
                "The table above shows the list of crew who are not supposed to assign for overnights",
                unsafe_allow_html=True
                )

        with st.expander("Error in aircraft eligibity"):
            if aircraft_issue.empty:
                st.markdown("No error into the aircarft assigment",unsafe_allow_html=True)
            else:
                st.dataframe(aircraft_issue)
                st.markdown(
                "The table above shows the list of crew who assigned to the ineligible aircrafts",
                unsafe_allow_html=True
                )


        with st.expander("Error in Block hour limitations"):
            if Block_hour_issue_1.empty:
                st.markdown("No violation of block hour limitations for crew ending at MLE",unsafe_allow_html=True)
            else:
                st.dataframe(Block_hour_issue_1)
                st.markdown(
                "The table above shows the list of crew who has violated the block hour limits (Ending at MLE)",
                unsafe_allow_html=True
                )

            if Block_hour_issue_2.empty:
                st.markdown("No violation of block hour limitations for crew ending outstation",unsafe_allow_html=True)
            else:
                st.dataframe(Block_hour_issue_2)
                st.markdown(
                "The table above shows the list of crew who has violated the block hour limits (Ending outstation)",
                unsafe_allow_html=True
                )

        with st.expander("Error in monthly duty hour"):
            if duty_hour_issue.empty:
                st.markdown("No violation of duty hour limitations",unsafe_allow_html=True)
            else:
                st.dataframe(duty_hour_issue)
                st.markdown(
                "The table above shows the list of crew who has violated the duty hour limits",
                unsafe_allow_html=True
                )

        with st.expander("Error in sectors limitation"):
            daily_sector_violation=output_crew_stats[output_crew_stats["Total sectors"]>14]
            
            if daily_sector_violation.empty:
                st.markdown("No violation of daily sector limitations",unsafe_allow_html=True)
            else:
                st.dataframe(daily_sector_violation)
                st.markdown(
                "The table above shows the list of crew who has violated the daily sectors limit of 14",
                unsafe_allow_html=True
                )

            if sector_issue_1.empty:
                st.markdown("No violation of Weekly sectors limit",unsafe_allow_html=True)
            else:
                st.dataframe(sector_issue_1)
                st.markdown(
                "The table above shows the list of crew who has violated the weekly sectors limits of 48",
                unsafe_allow_html=True
                )

            if sector_issue_2.empty:
                st.markdown("No violation of more than 12 sectors limitations",unsafe_allow_html=True)
            else:
                st.dataframe(sector_issue_2)
                st.markdown(
                "The table above shows the list of crew who has violated the weekly sectors limits of 2 times more than 12 sectors",
                unsafe_allow_html=True
                )
            
            
        with st.expander("Error in Aircraft Swaps limitations"):
            if swaps_issue.empty:
                st.markdown("No violation of swap count",unsafe_allow_html=True)
            else:
                st.dataframe(swaps_issue)
                st.markdown(
                "The table above shows the list of crew who has violated the aircraft swap limit of 1",
                unsafe_allow_html=True
                )

            if get_short_time_diffs_df.empty:
                st.markdown("No error into the time difference between aircrafts swaps",unsafe_allow_html=True)
            else:
                st.dataframe(get_short_time_diffs_df)
                st.markdown(
                "The table above shows the list where the assigned violated min 45 min difference between two aircraft assigment",
                unsafe_allow_html=True
                )
        
        with st.expander("Error in pairings rules"):
            if pairings_issue_1.empty:
                st.markdown("No violation of senior junior pairings",unsafe_allow_html=True)
            else:
                st.dataframe(pairings_issue_1)
                st.markdown(
                "The table above shows the list of crew who has violated senior junior pairings",
                unsafe_allow_html=True
                )

            if LTC_check.empty:
                st.markdown("No violation of LTC Pairings",unsafe_allow_html=True)
            else:
                st.dataframe(LTC_check)
                st.markdown(
                "The table above shows the list of crew who has violated LTC Trainee pairings",
                unsafe_allow_html=True
                )

            if training_issue.empty:
                st.markdown("No violation of training pairings",unsafe_allow_html=True)
            else:
                st.dataframe(training_issue)
                st.markdown(
                "The table above shows the list of crew who has violated training pairing",
                unsafe_allow_html=True
                )

        st.header("")
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
                (get_short_time_diffs_df,"AC swaps time"),
                (pairings_issue_1, 'Error in seniority pairings'),
                (LTC_check, 'Error in LTC pairings'),
                (training_issue, 'Error in training pairings'),
                (comparison_master, 'comparison_master'),
                (crew_ac_stats, 'crew_ac_stats'),
                (output_master, 'output_master')
            ]

            for df, sheet_name in df_output:
                if not df.empty:
                    df.to_excel(writer, sheet_name=sheet_name, index=False)

        output.seek(0)
        st.download_button(
            label="📥 Download Validation Report",
            data=output,
            file_name="constraints_validation.xlsx",
            mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
        )
                


    


