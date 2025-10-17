cols_empty = ['Crew code', 'Prev Day', 'Schedule Day', 'Next Day', 'Crew name','Crew Type', 'Seniority Level', 'Is Instructor?', 'Outstation airport']
cols_zero = ['Max BH left','Max BH left ON', 'Max DH left', 'Max sectors left']

available_status=["1","Li","LC"]
leave_status=["X","AL","AU","PAL","EM","ML"]

def input_validation_fun(merged_df):
      merged_df=merged_df[~merged_df['Schedule Day'].isin(leave_status)]
      input_issue_1=merged_df[merged_df[cols_empty].eq("").any(axis=1)]
      input_issue_2=merged_df[merged_df[cols_zero].eq(0).any(axis=1)]
      return input_issue_1[cols_empty], input_issue_2[['Crew code']+cols_zero]
