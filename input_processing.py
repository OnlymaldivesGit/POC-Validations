import pandas as pd
from datetime import datetime, timedelta
import numpy as np
from functools import reduce

available_status=["1","Li","LC"]
leave_status=["X","AL","AU","PAL","EM","ML","M"]

def fun(x):
  import datetime
  if pd.isnull(x):
      return 0
  if isinstance(x, float):
      return x
  if isinstance(x, datetime.time):
      return x.hour + x.minute / 60
  if isinstance(x, str) and ':' in x:
      hour, minute = x.split(':')[0:2]
      return int(hour) + int(minute) / 60
  return 0




def crew_stats_xml(sectors,flt,day_27th,day_364th):
    sectors = sectors[~sectors['Crew'].str.contains('Total|Applied', na=False)]

    flt = flt[~flt['Crew'].str.contains('Total|Applied', na=False)]
    flt.drop(["Job Title","7 Days Flight Time"],axis=1,inplace=True)

    day_27th = day_27th[~day_27th['Resource No.'].str.contains('Total|Applied', na=False)]
    day_27th=day_27th[['Resource No.',"Flight time"]]
    day_27th.columns=['Crew','27th Day FT']

    day_364th = day_364th[~day_364th['Ressource No.'].str.contains('Total|Applied', na=False)]
    day_364th=day_364th[['Ressource No.'	,"Flight time"]]
    day_364th.columns=['Crew','364th Day FT']

    dfs = [flt,sectors, day_27th, day_364th]
    merged_df = reduce(lambda left, right: pd.merge(left, right, on='Crew', how='left'), dfs)
    merged_df=merged_df[['Crew','28 Days Flight Time', '365 Days Flight Time', '28 Days Duty Time', '27th Day FT','364th Day FT', '-1D', '-2D', '-3D', '-4D', '-5D', '-6D', '-7D' ]]
    merged_df.columns=['Crew','28 Days Flight Time', '365 Days Flight Time', '28 Days Duty Time', '28th Day.Flight time','365th Day.Flight time', '-1D', '-2D', '-3D', '-4D', '-5D', '-6D', '-7D', ]

    merged_df_2=merged_df.copy()

    cols= ['28 Days Flight Time', '365 Days Flight Time', '28 Days Duty Time', '28th Day.Flight time','365th Day.Flight time']
    merged_df_2[cols] = merged_df_2[cols].applymap(fun)

    merged_df_2=merged_df_2[["Crew",'-1D', '-2D', '-3D', '-4D', '-5D', '-6D', '-7D','28 Days Flight Time','28th Day.Flight time', '365 Days Flight Time','365th Day.Flight time','28 Days Duty Time']]

    merged_df_2["Min BH left"]=np.minimum(100 - merged_df_2["28 Days Flight Time"],1000 - merged_df_2["365 Days Flight Time"])
    merged_df_2["Min BH left ON"]=np.minimum(102 - merged_df_2["28 Days Flight Time"]-merged_df_2["28th Day.Flight time"],1002 - merged_df_2["365 Days Flight Time"]-merged_df_2["365th Day.Flight time"])
    merged_df_2["Min DH"]=210-merged_df_2["28 Days Duty Time"]
    merged_df_2["Sectors Left"] = 48 - merged_df_2[["-1D", "-2D", "-3D", "-4D","-5D","-6D"]].sum(axis=1)
    merged_df_2["More than 12"]=2 - (merged_df_2['-1D'] > 12).astype(int) + (merged_df_2['-2D'] > 12).astype(int) + (merged_df_2['-3D'] > 12).astype(int)
    merged_df_2.columns= ["Crew code",'-1D', '-2D', '-3D', '-4D', '-5D', '-6D', '-7D', '28 Days BH','27th Day BH', '365 Days BH', '364th Day BH','28 Days DT', 'Min BH left', 'Min BH left ON', 'Min DH','Sectors Left', 'More than 12']

    return merged_df,merged_df_2







def schedule_input_processing(Schedule_input):
    Schedule_input["Flight No."] = Schedule_input["Flight No."].str.strip()
    Schedule_input['Aircraft No.'] = Schedule_input['Aircraft No.'].str.strip()
    Schedule_input['STD -  Scheduled Departure'] = Schedule_input['STD -  Scheduled Departure'].astype(str).str.strip()
    Schedule_input['STA -  Scheduled Arrival'] = Schedule_input['STA -  Scheduled Arrival'].astype(str).str.strip()
    Schedule_input['Dep. Airport'] = Schedule_input['Dep. Airport'].str.strip()
    Schedule_input['Arr. Airport'] = Schedule_input['Arr. Airport'].str.strip()
    Schedule_input=Schedule_input[Schedule_input['Dep. Airport']!=Schedule_input['Arr. Airport']]
    return Schedule_input

def aircraft_processing(aircraft):
    aircraft=aircraft[["Aircraft code","Aircraft Type"]]
    aircraft.columns=["Aircraft Code","Aircraft Type"]
    return aircraft

def crew_aircraft_processing(crew_aircraft):
    crew_aircraft['Crew code'] = crew_aircraft['Crew code'].str.replace(r'\s*\(.*?\)', '', regex=True).str.strip()
    crew_aircraft=crew_aircraft[['Crew code', '100', '200', '300', '400', '200-G950', '300-G600', '300-G950',
       '300-GI275']]
    return crew_aircraft


def crew_stats_processing(crew_stats):
    crew_stats=crew_stats[["Crew code",'Min BH left', 'Min BH left ON', 'Min DH', 'Sectors Left','More than 12']]
    crew_stats['Crew code'] = crew_stats['Crew code'].str.replace(r'\s*\(.*?\)', '', regex=True).str.strip()
    crew_stats.columns=['Crew code', 'Max BH left', 'Max BH left ON', 'Max DH left', 'Max sectors left',
        'Max more than 12 sectors']
    return crew_stats




def logsheet_processing(logsheet,prev_day):
    logsheet=logsheet[['Date', 'Flight No ','Aircraft No ','Actual Time of Arrival','Arr Airport','Captain', 'First Officer', 'Flight Attendant']]
    logsheet=logsheet[logsheet['Date']==prev_day]

    logsheet=logsheet.melt(
        id_vars=['Date', 'Flight No ','Aircraft No ','Actual Time of Arrival','Arr Airport'],
        value_vars=['Captain', 'First Officer', 'Flight Attendant'],
        var_name='Crew Type',
        value_name='Crew code'
    )
    logsheet['Crew code'] = logsheet['Crew code'].str.replace(r'\s*\(.*?\)', '', regex=True).str.strip()
    logsheet['Actual Time of Arrival'] = pd.to_datetime(logsheet['Actual Time of Arrival'], format='%H:%M',errors='coerce')


    idx = logsheet.groupby('Crew code')['Actual Time of Arrival'].idxmax()
    logsheet = logsheet.loc[idx]
    logsheet=logsheet[['Crew code',"Arr Airport",'Aircraft No ']]
    logsheet.columns=['Crew code',"Outstation airport","Outstation Aircraft"]

    logsheet["Outstation airport"] = logsheet["Outstation airport"].str.strip()
    logsheet["Outstation Aircraft"] = logsheet["Outstation Aircraft"].str.strip()
    return logsheet


def month_plan_processing(month_plan,schedule_date,prev_day,next_day):
    month_plan.columns = [str(col).split()[0] if str(col).startswith('2025-') else col for col in month_plan.columns]
    month_plan['Crew code'] = month_plan['Crew code'].str.strip()
    month_plan['Crew code'] = month_plan['Crew code'].str.replace(r'\s*\(.*?\)', '', regex=True).str.strip()
    month_plan=month_plan[['Crew code',prev_day,schedule_date,next_day]]
    month_plan.columns=["Crew code","Prev Day","Schedule Day","Next Day"]
    month_plan = month_plan[~month_plan['Schedule Day'].isna()]
    month_plan["Prev Day"]=month_plan["Prev Day"].astype(str)
    month_plan["Schedule Day"]=month_plan["Schedule Day"].astype(str)
    month_plan["Next Day"]=month_plan["Next Day"].astype(str)
    
    return month_plan

def flight_training_processing(flight_training,schedule_date):
    flight_training['Instructor'] = flight_training['Instructor'].str.strip()
    flight_training['Trainee'] = flight_training['Trainee'].str.strip()
    flight_training=flight_training[flight_training["Date"]==schedule_date]
    return flight_training


def expiry_data_processing(expiry_data):
    expiry_data=expiry_data[["Crew code","Expiry"]]
    expiry_data.columns=["Crew code","Expiry status"]
    expiry_data['Crew code'] = expiry_data['Crew code'].str.replace(r'\s*\(.*?\)', '', regex=True).str.strip()
    return expiry_data



def seniority_processing(seniority):
    seniority=seniority[['Crew code', 'Seniority Level',"LTC/CCI"]]
    seniority.columns=["Crew code","Seniority Level","Is Instructor?"]
    seniority['Crew code'] = seniority['Crew code'].str.strip()
    seniority['Crew code'] = seniority['Crew code'].str.replace(r'\s*\(.*?\)', '', regex=True).str.strip()
    return seniority



def crew_master_processing(crew_master):
    crew_master=crew_master[['Crew code', 'Crew name', 'Flight personnel type']]
    crew_master.columns=["Crew code","Crew name","Crew Type"]
    crew_master.dropna(subset=["Crew code"], inplace=True)
    crew_master['Crew code'] = crew_master['Crew code'].str.replace(r'\s*\(.*?\)', '', regex=True).str.strip()
    crew_master['Crew code'] = crew_master['Crew code'].str.strip()
    return crew_master



def merged_data_fun(month_plan,crew_master, seniority, expiry_data, logsheet,crew_stats):
    dfs = [month_plan,crew_master, seniority, expiry_data, logsheet,crew_stats]
    
    merged_df = reduce(lambda left, right: pd.merge(left, right, on='Crew code', how='left'), dfs)
   
    cols_empty = ['Crew code', 'Prev Day', 'Schedule Day', 'Next Day', 'Crew name','Crew Type', 'Seniority Level', 'Is Instructor?', 'Expiry status', 'Outstation airport']
    cols_zero = ['Max BH left','Max BH left ON', 'Max DH left', 'Max sectors left','Max more than 12 sectors']

    merged_df[cols_empty+["Outstation Aircraft"]] = merged_df[cols_empty+["Outstation Aircraft"]].fillna('')
    merged_df[cols_zero] = merged_df[cols_zero].fillna(0)
    merged_df[cols_zero]= merged_df[cols_zero].astype(float)

    values_to_check = available_status

    condition = (~merged_df['Prev Day'].isin(values_to_check)) & (merged_df['Outstation airport'] == "")
    merged_df.loc[condition, 'Outstation airport'] = 'MLE'
    return merged_df

