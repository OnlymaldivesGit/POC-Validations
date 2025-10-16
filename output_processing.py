import pandas as pd
from datetime import datetime, timedelta
import numpy as np

schedule_date="2025-09-08"
prev_day = (datetime.strptime(schedule_date, "%Y-%m-%d") - timedelta(days=1)).strftime("%Y-%m-%d")
next_day = (datetime.strptime(schedule_date, "%Y-%m-%d") + timedelta(days=1)).strftime("%Y-%m-%d")




def Schedule_output_processing(Schedule_output):
    Schedule_output["Flight No."] = Schedule_output["Flight No."].str.strip()
    Schedule_output['Aircraft No.'] = Schedule_output['Aircraft No.'].str.strip()
    Schedule_output['STD -  Scheduled Departure'] = Schedule_output['STD -  Scheduled Departure'].str.strip()
    Schedule_output['STA -  Scheduled Arrival'] = Schedule_output['STA -  Scheduled Arrival'].str.strip()
    Schedule_output['Dep. Airport'] = Schedule_output['Dep. Airport'].str.strip()
    Schedule_output['Arr. Airport'] = Schedule_output['Arr. Airport'].str.strip()
    return Schedule_output


def Schedule_output_processing_2(Schedule_output):
    Schedule_output_2=Schedule_output.melt(
    id_vars=['Date', 'Flight No.', 'Aircraft No.', 'STD -  Scheduled Departure','STA -  Scheduled Arrival', 'Dep. Airport', 'Arr. Airport'],
    value_vars=['Captain','First Officer', 'Flight Attendant'],
    var_name='Crew Type',
    value_name='Crew code'
    )

    Schedule_output_2['STD -  Scheduled Departure'] = pd.to_datetime(Schedule_output_2['STD -  Scheduled Departure'], format='%H:%M:%S')
    Schedule_output_2['STA -  Scheduled Arrival'] = pd.to_datetime(Schedule_output_2['STA -  Scheduled Arrival'], format='%H:%M:%S')

    Schedule_output_2['Block hours'] = ((Schedule_output_2['STA -  Scheduled Arrival'] - Schedule_output_2['STD -  Scheduled Departure']).dt.total_seconds()+600) / 3600
    Schedule_output_2 = Schedule_output_2.sort_values(['Crew code', 'STD -  Scheduled Departure'])

    Schedule_output_2['Group id'] = (
        (Schedule_output_2[['Crew code', 'Aircraft No.']] != Schedule_output_2[['Crew code', 'Aircraft No.']].shift()).any(axis=1)
    ).cumsum()
    return Schedule_output_2


def output_master_processing(Schedule_output_2):
    first_sector=Schedule_output_2.loc[Schedule_output_2.groupby('Crew code')['STD -  Scheduled Departure'].idxmin()]
    last_sector=Schedule_output_2.loc[Schedule_output_2.groupby('Crew code')['STA -  Scheduled Arrival'].idxmax()]

    first_sector=first_sector[["Crew code","Dep. Airport",'STD -  Scheduled Departure']]
    first_sector.columns=["Crew code","Starting from","Start time"]

    last_sector=last_sector[["Crew code","Arr. Airport",'STA -  Scheduled Arrival']]
    last_sector.columns=["Crew code","Ending at","End time"]

    output_crew_stats=Schedule_output_2.groupby('Crew code').agg({
    'Flight No.': 'nunique',
    'Aircraft No.': 'nunique',
    'Date': 'count',
    'Block hours': 'sum',
    "Group id": lambda x: x.nunique() - 1
    }).reset_index()

    output_crew_stats.columns=['Crew code', 'Total flights', 'Total aircrafts', 'Total sectors', 'Block hours',"No. of swaps"]

    output_master=Schedule_output_2[["Crew code","Crew Type"]].drop_duplicates()
    output_master=output_master.merge(first_sector,on="Crew code",how="left")
    output_master=output_master.merge(last_sector,on="Crew code",how="left")
    output_master=output_master.merge(output_crew_stats,on="Crew code",how="left")
    output_master['Duty hours'] = (output_master['End time'] - output_master['Start time']) / pd.Timedelta(hours=1)+(75/60)
    output_master.drop(['Start time','End time'],axis=1,inplace=True)
    output_master["Working Status"]=1
    return output_master

def crew_ac_stats_processing(Schedule_output_2,aircraft,crew_aircraft):
    idx_minSTD = Schedule_output_2.groupby('Group id')['STD -  Scheduled Departure'].idxmin()
    idx_maxSTA = Schedule_output_2.groupby('Group id')['STA -  Scheduled Arrival'].idxmax()


    idx_minSTD_output = Schedule_output_2.loc[idx_minSTD, ["Group id","Crew code","Aircraft No.",'STD -  Scheduled Departure']].rename(columns={"Aircraft No.":"Assigned AC",'STD -  Scheduled Departure':"Start time"})
    idx_maxSTA_output = Schedule_output_2.loc[idx_maxSTA, ["Group id","Crew code","Aircraft No.",'STA -  Scheduled Arrival']].rename(columns={"Aircraft No.":"Assigned AC",'STA -  Scheduled Arrival':"End time"})


    crew_ac_stats=idx_minSTD_output.merge(idx_maxSTA_output,on=["Group id","Crew code","Assigned AC"])
    crew_ac_stats=crew_ac_stats.merge(aircraft,left_on=["Assigned AC"],right_on=["Aircraft Code"])
    crew_ac_stats['qualified'] = crew_ac_stats.apply(lambda x: crew_aircraft.loc[crew_aircraft['Crew code'] == x['Crew code'], x['Aircraft Type']].values[0], axis=1)
    return crew_ac_stats


