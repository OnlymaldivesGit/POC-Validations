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


available_status=["1","Li","LC"]
leave_status=["X","AL","AU","PAL","EM","ML"]


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


schedule_date = st.date_input("Select schedule date")
schedule_date = schedule_date.strftime("%Y-%m-%d")
prev_day = (datetime.strptime(schedule_date, "%Y-%m-%d") - timedelta(days=1)).strftime("%Y-%m-%d")
next_day = (datetime.strptime(schedule_date, "%Y-%m-%d") + timedelta(days=1)).strftime("%Y-%m-%d")

with st.sidebar:
    selected = option_menu(
        menu_title="Modules",  # Sidebar title
        options=[
            "Input Data Validator", 
            "Constraints Validator"
        ],
        icons=["file-earmark-excel",  "bar-chart"],
        menu_icon="gear",  # Top icon
        default_index=0,
        orientation="vertical"  # Ensures vertical left-side layout
    )

if selected == "Input Data Validator":
    st.title("Input Data Validator")

    if st.button("Validate the data"):

        aircraft=pd.read_excel("Model Validations/Aircrafts.xlsx")
        crew_aircraft=pd.read_excel("Model Validations/Crew AC Matrix.xlsx")
        seniority=pd.read_excel("Model Validations/Crew Pairing.xlsx")
        logsheet=pd.read_excel("Model Validations/Log sheet.xlsx")
        crew_master=pd.read_excel("Model Validations/Resources.xlsx")
        expiry_data=pd.read_excel("Model Validations/Training Expiry.xlsx")
        flight_training=pd.read_excel("Model Validations/Training Pairings.xlsx")
        month_plan=pd.read_excel("Model Validations/Month plan.xlsx")
        crew_stats=pd.read_excel("Crew Stats.xlsx",sheet_name=schedule_date)
        
        

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
            time.sleep(0.5)
            placeholder1_1 = st.empty()
            placeholder1_1.markdown("✅ First Validation Completed")
            st.dataframe(input_issue_1)
            st.markdown(
            "The table above shows the list of Crew data where crew resorts are missing except their stats",
            unsafe_allow_html=True
            )

        with st.spinner("⚪️ Validating the data..."):
            time.sleep(0.5)
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

    st.title("Constraints Validator")
    if st.button("Validate the data"):
        aircraft=pd.read_excel("Model Validations/Aircrafts.xlsx")
        crew_aircraft=pd.read_excel("Model Validations/Crew AC Matrix.xlsx")
        seniority=pd.read_excel("Model Validations/Crew Pairing.xlsx")
        logsheet=pd.read_excel("Model Validations/Log sheet.xlsx")
        crew_master=pd.read_excel("Model Validations/Resources.xlsx")
        expiry_data=pd.read_excel("Model Validations/Training Expiry.xlsx")
        flight_training=pd.read_excel("Model Validations/Training Pairings.xlsx")
        month_plan=pd.read_excel("Model Validations/Month plan.xlsx")
        crew_stats=pd.read_excel("Crew Stats.xlsx",sheet_name=schedule_date)

        
        

        if input_flight_plan is None:
            Schedule_input=pd.read_excel("Model Validations/Flight Plan.xlsx")
        else:
            Schedule_input=pd.read_excel(input_flight_plan)

        if output_flight_plan is None:
            Schedule_output=pd.read_excel("Model Validations/Model Output.xlsx")
        else:
            Schedule_output=pd.read_excel(output_flight_plan)



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
        output_master=output_master_processing(Schedule_output_2)
        crew_ac_stats=crew_ac_stats_processing(Schedule_output_2,aircraft,crew_aircraft)

        comparison_master =  merged_df.merge(output_master, on="Crew code", how="outer")

        available_working = comparison_master[(comparison_master["Schedule Day"].isin(available_status)) & (~comparison_master["Working Status"].isna())]
        Standby_crew = comparison_master[ (comparison_master["Schedule Day"].isin(available_status)) &(comparison_master["Working Status"].isna())]
        
        leaves_working=comparison_master[(comparison_master["Schedule Day"].isin(leave_status)) & (~comparison_master["Working Status"].isna())]
        
        on_training=comparison_master[~(comparison_master["Schedule Day"].isin(leave_status+available_status))]
        on_training_working=on_training[~comparison_master["Working Status"].isna()]
        training_non_outstations = on_training[(on_training["Outstation airport"].isin(["", "MLE"]))]

        with st.spinner("⚪️ Validating the Schedule..."):
            time.sleep(1)
            placeholder1 = st.empty()
            Schedule_check=Schedule_check_fun(Schedule_output,Schedule_input)
            placeholder1.markdown("✅ Schedule Validated")

        with st.spinner("⚪️ Validating the Crew Dependency..."):
            time.sleep(1)
            placeholder2 = st.empty()
            crew_mistake_1, crew_mistake_11,crew_mistake_2,crew_mistake_3=crew_check_fun(comparison_master,available_working)
            placeholder2.markdown("✅ Crew Dependency Validated")

        with st.spinner("⚪️ Validating the Aicraft Dependency..."):
            time.sleep(1)
            placeholder3 = st.empty()
            aircraft_issue=aircraft_check(crew_ac_stats)
            placeholder3.markdown("✅ Aicraft Dependency Validated")

        with st.spinner("⚪️ Validating the Crew Stats Depenedency..."):
            time.sleep(1)
            placeholder4 = st.empty()
            Block_hour_issue_1,Block_hour_issue_2,duty_hour_issue,sector_issue_1,sector_issue_2=Stats_check_fun(available_working)
            placeholder4.markdown("✅ Crew Stats Dependency Validated")

        with st.spinner("⚪️ Validating the crew swaps..."):
            time.sleep(1)
            placeholder5 = st.empty()
            swaps_issue=swaps_check_fun(output_master)
            placeholder5.markdown("✅ Crew swaps Validated")

        with st.spinner("⚪️ Validating the seniority pairings..."):
            time.sleep(1)
            placeholder6 = st.empty()
            pairings_issue_1, LTC_check=seniority_check_fun(Schedule_output,merged_df)
            placeholder6.markdown("✅ Seniority pairings Validated")

        with st.spinner("⚪️ Validating the Training Pairings..."):
            time.sleep(1)
            placeholder6 = st.empty()
            training_issue=training_pairing_check(flight_training, merged_df)
            placeholder6.markdown("✅ Training Pairings Validated")



        # Print of Data
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

        with st.expander("Training crew at base"):
            if crew_mistake_1.empty:
                st.markdown("No such errors",unsafe_allow_html=True)
            else:
                st.dataframe(crew_mistake_1)
                st.markdown(
                "The table above shows the list of crew who are on training and at base last night but has been scheduled to Flight ",
                unsafe_allow_html=True
                )
        with st.expander("Error in Training crew outstation"):
            if crew_mistake_11.empty:
                st.markdown("",unsafe_allow_html=True)
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

        with st.expander("Error in aircrafts"):
            if aircraft_issue.empty:
                st.markdown("No error into the aircarft assigment",unsafe_allow_html=True)
            else:
                st.dataframe(aircraft_issue)
                st.markdown(
                "The table above shows the list of crew who assigned to the ineligible aircrafts",
                unsafe_allow_html=True
                )


        with st.expander("Error in Block hour 1"):
            if Block_hour_issue_1.empty:
                st.markdown("No violation of block hour limitations",unsafe_allow_html=True)
            else:
                st.dataframe(Block_hour_issue_1)
                st.markdown(
                "The table above shows the list of crew who has violated the block hour limits",
                unsafe_allow_html=True
                )

        with st.expander("Error in Block hour 2"): 
            if Block_hour_issue_2.empty:
                st.markdown("No violation of block hour limitations",unsafe_allow_html=True)
            else:
                st.dataframe(Block_hour_issue_2)
                st.markdown(
                "The table above shows the list of crew who has violated the block hour limits for the overnights",
                unsafe_allow_html=True
                )

        with st.expander("Error in duty hour"):
            if duty_hour_issue.empty:
                st.markdown("No violation of duty hour limitations",unsafe_allow_html=True)
            else:
                st.dataframe(duty_hour_issue)
                st.markdown(
                "The table above shows the list of crew who has violated the duty hour limits",
                unsafe_allow_html=True
                )


        with st.expander("Error in sectors 1"):
            if sector_issue_1.empty:
                st.markdown("No violation of sectors limitations",unsafe_allow_html=True)
            else:
                st.dataframe(sector_issue_1)
                st.markdown(
                "The table above shows the list of crew who has violated the weekly sectors limits of 48",
                unsafe_allow_html=True
                )

        with st.expander("Error in sectors 2"):
            if sector_issue_2.empty:
                st.markdown("No violation of sectors limitations",unsafe_allow_html=True)
            else:
                st.dataframe(sector_issue_2)
                st.markdown(
                "The table above shows the list of crew who has violated the weekly sectors limits of 2 times more than 12 sectors",
                unsafe_allow_html=True
                )
            
            
        with st.expander("Error in AC swaps"):
            if swaps_issue.empty:
                st.markdown("No violation of swap rules",unsafe_allow_html=True)
            else:
                st.dataframe(swaps_issue)
                st.markdown(
                "The table above shows the list of crew who has violated the weekly sectors limits of 2 times more than 12 sectors",
                unsafe_allow_html=True
                )
        
        with st.expander("Error in seniority pairings"):
            if pairings_issue_1.empty:
                st.markdown("No violation of senior junior pairings",unsafe_allow_html=True)
            else:
                st.dataframe(pairings_issue_1)
                st.markdown(
                "The table above shows the list of crew who has violated senior junior pairings",
                unsafe_allow_html=True
                )

        with st.expander("Error in LTC pairings"):
            if LTC_check.empty:
                st.markdown("No violation of LTC Pairings",unsafe_allow_html=True)
            else:
                st.dataframe(LTC_check)
                st.markdown(
                "The table above shows the list of crew who has violated LTC Trainee pairings",
                unsafe_allow_html=True
                )

        with st.expander("Error in training pairings"):
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
            Schedule_check.to_excel(writer, sheet_name='Schedule_check', index=False)
            crew_mistake_1.to_excel(writer, sheet_name='Crew with Training 1', index=False)
            crew_mistake_11.to_excel(writer, sheet_name='Crew with Training 2', index=False)
            crew_mistake_2.to_excel(writer, sheet_name='Error in Starting points', index=False)
            crew_mistake_3.to_excel(writer, sheet_name='Error in Overnights', index=False)
            aircraft_issue.to_excel(writer, sheet_name='Error in aircrafts', index=False)
            Block_hour_issue_1.to_excel(writer, sheet_name='Error in Block hour 1', index=False)
            Block_hour_issue_2.to_excel(writer, sheet_name='Error in Block hour 2', index=False)
            duty_hour_issue.to_excel(writer, sheet_name='Error in duty hour', index=False)
            sector_issue_1.to_excel(writer, sheet_name='Error in sectors 1', index=False)
            sector_issue_2.to_excel(writer, sheet_name='Error in sectors 2', index=False)
            swaps_issue.to_excel(writer, sheet_name='Error in AC swaps', index=False)
            pairings_issue_1.to_excel(writer, sheet_name='Error in seniority pairings', index=False)
            LTC_check.to_excel(writer, sheet_name='Error in LTC pairings', index=False)
            training_issue.to_excel(writer, sheet_name='Error in training pairings', index=False)
            comparison_master.to_excel(writer, sheet_name='comparison_master', index=False)
            crew_ac_stats.to_excel(writer, sheet_name='crew_ac_stats', index=False)
            output_master.to_excel(writer, sheet_name='output_master', index=False)

        output.seek(0)
        st.download_button(
            label="📥 Download Validation Report",
            data=output,
            file_name="constraints_validation.xlsx",
            mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
        )
                


    


