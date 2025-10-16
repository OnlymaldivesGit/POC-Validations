import pandas as pd
xls = pd.ExcelFile("Crew Stats.xlsx")
print(xls.sheet_names)
