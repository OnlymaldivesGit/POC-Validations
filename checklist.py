# List of Checks

# All crew used are available ( if not, they must be on training and only doing first flight)
# Starting Position of Crew
# No crew should end duty overnight if thy are not working tomorrow
# No. of crew swaps should be less than 2
# Block hours, Duty Hours and sectors limits are being full filled
# Schedule should match ( AC, Flights, Sectors etc)
import pandas as pd

available_status=["1","Li","LC"]
leave_status=["X","AL","AU","PAL","EM","ML","M"]


def Schedule_check_fun(Schedule_output,Schedule_input):
    Schedule_check=Schedule_output.merge(
        Schedule_input,
        on=['Date', 'Flight No.', 'Aircraft No.', 'STD -  Scheduled Departure','STA -  Scheduled Arrival', 'Dep. Airport', 'Arr. Airport'],
        how="outer",indicator=True
    )
    Schedule_check['_merge'] = Schedule_check['_merge'].map({
        'left_only': 'only in output',
        'right_only': 'only in input',
        'both': 'both'
    })
    Schedule_check=Schedule_check[Schedule_check["_merge"]!="both"]
    return Schedule_check[['Flight No.', 'Aircraft No.', 'STD -  Scheduled Departure','STA -  Scheduled Arrival', 'Dep. Airport', 'Arr. Airport']]


def crew_check_fun(comparison_master,available_working):
    on_training=comparison_master[~(comparison_master["Schedule Day"].isin(leave_status+available_status))]
    on_training_working=on_training[comparison_master["Working Status"]==1]

    crew_mistake_1 = on_training_working[(on_training_working["Outstation airport"].isin(["", "MLE"]))]
    crew_mistake_1=crew_mistake_1[['Crew code', 'Prev Day', 'Schedule Day', 'Next Day',"Outstation airport",'Working Status']]

    on_training_working_outstations = on_training[~(on_training["Outstation airport"].isin(["", "MLE"]))]
    crew_mistake_11=on_training_working_outstations[~(on_training_working_outstations['Total flights'] == 1)]
    crew_mistake_11=crew_mistake_11[['Crew code', 'Prev Day', 'Schedule Day','Outstation airport','Total flights','Working Status']]

    
    # Crew with mismatch Starting points
    crew_mistake_2=available_working[available_working["Starting from"]!=available_working["Outstation airport"]]
    crew_mistake_2=crew_mistake_2[["Crew code",'Starting from',"Outstation airport","Prev Day",'Schedule Day']]

    # Crew who are not supposed to assign for overnights
    crew_mistake_3=available_working[comparison_master['Ending at']!="MLE"]
    crew_mistake_3=crew_mistake_3[["Crew code",'Next Day','Ending at']]
    crew_mistake_3 = crew_mistake_3[crew_mistake_3["Next Day"].isin(leave_status)]
    
    return crew_mistake_1, crew_mistake_11,crew_mistake_2,crew_mistake_3

def aircraft_check(crew_ac_stats):
    return crew_ac_stats[crew_ac_stats["qualified"]!=1.0]


def Stats_check_fun(available_working):
    Block_hour_issue_1=available_working[available_working["Block hours"]>available_working["Max BH left"]]
    Block_hour_issue_2=available_working[available_working["Block hours"]>available_working["Max BH left ON"]]
    duty_hour_issue=available_working[available_working['Duty hours']>available_working["Max DH left"]]
    sector_issue_1=available_working[available_working['Total sectors']>available_working["Max sectors left"]]
    sector_issue_2 = available_working[((available_working['Total sectors'] > 12) & (available_working['Max more than 12 sectors'] == 0))]
    return Block_hour_issue_1,Block_hour_issue_2,duty_hour_issue,sector_issue_1,sector_issue_2


def swaps_check_fun(output_master):
    return output_master[output_master["No. of swaps"]>1]

def seniority_check_fun(Schedule_output,merged_df):

    def get_pairing_seniority(x):
        cap = merged_df.loc[merged_df['Crew code'] == x["Captain"], 'Seniority Level']
        fo = merged_df.loc[merged_df['Crew code'] == x["First Officer"], 'Seniority Level']
        fa = merged_df.loc[merged_df['Crew code'] == x["Flight Attendant"], 'Seniority Level']
        
        cap_level = cap.values[0] if not cap.empty else "X"
        fo_level = fo.values[0] if not fo.empty else "X"
        fa_level = fa.values[0] if not fa.empty else "X"
        
        return f"{cap_level} - {fo_level} - {fa_level}"

    Schedule_output["Pairing"] = Schedule_output.apply(get_pairing_seniority, axis=1)


    avaibale_pairings=['Senior - Senior - Senior', 'Senior - Junior - Senior','Senior - Senior - Junior', 'Senior - Trainee - Senior','Junior - Senior - Senior']

    pairings_issue_1=Schedule_output[~Schedule_output["Pairing"].isin(avaibale_pairings)]
    LTC_check=Schedule_output[Schedule_output["Pairing"]=='Senior - Trainee - Senior']

    def get_instructor_check(x):
        matched = merged_df.loc[merged_df['Crew code'] == x["Captain"], 'Is Instructor?']
        if not matched.empty:
            return matched.values[0]
        return None  # or "X" or False, depending on your desired fallback

    LTC_check["Instructor check"] = LTC_check.apply(get_instructor_check, axis=1)
    LTC_check=LTC_check[LTC_check["Instructor check"]=="No"]

    return pairings_issue_1, LTC_check


def training_pairing_check(flight_training, Schedule_output):
    def get_crew_list(row):
        code = row['Crew code']
        typ = row['Crew type']
        if typ == 'Instructor':
            # Find unique first officers where captain == code
            return ', '.join(Schedule_output[Schedule_output['Captain'] == code]['First Officer'].unique())
        elif typ == 'Trainee':
            # Find unique captains where first_officer == code
            return ', '.join(Schedule_output[Schedule_output['First Officer'] == code]['Captain'].unique())
        else:
            return ""
        
    flight_training_instructor=flight_training.drop(["Training Type"],axis=1).rename(columns={"Instructor":"Crew code","Trainee":"Paired with"})
    flight_training_instructor["Crew type"]="Instructor"

    flight_training_trainee=flight_training.drop(["Training Type"],axis=1).rename(columns={"Trainee":"Crew code","Instructor":"Paired with"})
    flight_training_trainee["Crew type"]="Trainee"

    flight_training_master = pd.concat([flight_training_instructor, flight_training_trainee], axis=0, ignore_index=True)
    flight_training_master['Actual Pairing'] = flight_training_master.apply(get_crew_list, axis=1)
    flight_training_master=flight_training_master[flight_training_master["Paired with"]!=flight_training_master["Actual Pairing"]]
    return flight_training_master
        
    

def get_short_time_diffs(df, crew_code_col='Crew code', start_col='Start time', end_col='End time', ac_col='Aircraft Code', min_gap=45):
    counts = df[crew_code_col].value_counts()
    multi_crew = counts[counts > 1].index
    tmp = df[df[crew_code_col].isin(multi_crew)].copy()

    tmp['start_seq'] = tmp.groupby(crew_code_col)[start_col].rank(method='first').astype(int)

    firsts = tmp[tmp['start_seq'] == 1][[crew_code_col, start_col, end_col, ac_col]]
    seconds = tmp[tmp['start_seq'] == 2][[crew_code_col, start_col, end_col, ac_col]]

    result = pd.merge(firsts, seconds, on=crew_code_col)
    result.columns = [
        crew_code_col, 'First AC ST', 'First AC ET', 'First AC code',
        'Second AC ST', 'Second AC ET', 'Second AC code']

    result['First AC ET'] = pd.to_datetime(result['First AC ET'])
    result['Second AC ST'] = pd.to_datetime(result['Second AC ST'])

    result['Time difference'] = (result['Second AC ST'] - result['First AC ET']).dt.total_seconds() / 60

    result = result[result["Time difference"] < min_gap]
    return result










