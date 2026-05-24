"""
config.py — Single source of truth for all TMA Crew Scheduler constants.

Every hardcoded value that was previously scattered across app.py,
input_processing.py, output_processing.py, checklist.py, and
input_validations.py is defined here with a descriptive name and a
one-line explanation of the value and why it was chosen.

Import pattern (in any module):
    from config import HOME_BASE, AVAILABLE_STATUS, BH_28DAY_LIMIT, ...
"""

# ---------------------------------------------------------------------------
# Status code lists
# ---------------------------------------------------------------------------

AVAILABLE_STATUS = ["1", "Li", "LC"]
# Codes in the monthly plan that mean the crew member is available to fly.
# "1" = standard working day, "Li" = Line Instructor, "LC" = Line Check.

LEAVE_STATUS = ["X", "AL", "AU", "PAL", "EM", "ML", "M"]
# Codes in the monthly plan that mean the crew member is on an approved leave.
# X=day-off, AL=annual leave, AU=authorised unpaid leave, PAL=personal leave,
# EM=emergency leave, ML=maternity/medical leave, M=miscellaneous leave.
# Any schedule code that is not in AVAILABLE_STATUS and not in LEAVE_STATUS
# is treated as a training code.

# ---------------------------------------------------------------------------
# Home base
# ---------------------------------------------------------------------------

HOME_BASE = "MLE"
# IATA code for Velana International Airport, Male, Maldives — TMA's base.
# Used to detect overnight outstation assignments and infer crew start position.

# ---------------------------------------------------------------------------
# Block hour limits  (ICAO / airline FTL regulation)
# ---------------------------------------------------------------------------

BH_28DAY_LIMIT = 100
# Maximum cumulative block hours a crew member may fly in any rolling 28-day
# window when they end the day at the home base (MLE). Regulatory limit.

BH_28DAY_ON_LIMIT = 98
# Same 28-day window cap, but for crew who end the day at an outstation.
# Tighter by 2 hours because they will fly home the next day, consuming
# remaining capacity. Calculated relative to the 27th-day rolling-off value.

BH_365DAY_LIMIT = 1000
# Maximum cumulative block hours a crew member may fly in any rolling 365-day
# (calendar year) window, ending at MLE. Regulatory limit.

BH_365DAY_ON_LIMIT = 998
# Same 365-day cap for crew ending at an outstation. Same 2-hour buffer logic
# as BH_28DAY_ON_LIMIT but for the annual window. Calculated relative to the
# 364th-day rolling-off value.

# ---------------------------------------------------------------------------
# Duty time limits
# ---------------------------------------------------------------------------

DT_28DAY_LIMIT = 210
# Maximum cumulative duty hours a crew member may accrue in any rolling 28-day
# window. Duty time = block time + ground duties; wider than block time.

DUTY_GROUND_TIME_HOURS = 1.5
# Fixed buffer (90 minutes) added to every duty period to account for
# pre-flight and post-flight ground duties. Applied as:
#   Duty hours = (last_STA - first_STD) + DUTY_GROUND_TIME_HOURS

# ---------------------------------------------------------------------------
# Sector limits
# ---------------------------------------------------------------------------

SECTOR_6DAY_LIMIT = 48
# Maximum number of sectors a crew member may fly in any rolling 6-day window
# (the look-back columns -1D through -6D). Regulatory limit.

SECTOR_DAILY_LIMIT = 14
# Absolute maximum number of sectors a single crew member may fly in one day.
# Exceeding this triggers Rule C-14 regardless of the 6-day budget.

SECTOR_LONG_DAY_THRESHOLD = 12
# Number of sectors in a day that constitutes a "long day". If a crew member
# flies more than this many sectors today AND has no remaining long-day
# allowance, Rule C-13 is triggered.

SECTOR_LONG_DAY_ALLOWANCE = 2
# Maximum number of "long days" (>SECTOR_LONG_DAY_THRESHOLD sectors) permitted
# in the look-back window of -1D, -2D, -3D. If a crew has already used both
# slots, they cannot fly another long day today.

SECTOR_LOOKBACK_DAYS = 6
# Number of prior-day columns used in the rolling sector calculation.
# Columns -1D through -6D are summed to compute 'Max sectors left'.

# ---------------------------------------------------------------------------
# Block hours formula multiplier
# ---------------------------------------------------------------------------

BLOCK_HOUR_MULTIPLIER = 1.35
# Inflation factor applied to raw flight time (STA - STD) to derive block hours.
# Accounts for taxi time, de-icing buffer, and standard airline block-time
# accounting conventions. Applied per sector before summing.

# ---------------------------------------------------------------------------
# Aircraft swap constraints
# ---------------------------------------------------------------------------

MAX_SWAPS_PER_DAY = 1
# Maximum number of aircraft changes a crew member may make in a single duty
# day. Rule C-15 flags any crew with No. of swaps > MAX_SWAPS_PER_DAY.

MIN_SWAP_GAP_MINUTES = 45
# Minimum elapsed time in minutes between the end of one aircraft assignment
# and the start of another, when a crew member swaps aircraft mid-day.
# Rule C-16 flags gaps shorter than this threshold.

# ---------------------------------------------------------------------------
# Valid crew pairing combinations  (Captain seniority - FO seniority - FA seniority)
# ---------------------------------------------------------------------------

VALID_SENIORITY_PAIRINGS = [
    "Senior - Senior - Senior",   # Standard all-senior crew
    "Senior - Junior - Senior",   # Junior FO supervised by Senior Captain
    "Senior - Senior - Junior",   # Junior FA on a senior-crewed flight
    "Senior - Trainee - Senior",  # FO trainee; requires Captain to be LTC (Rule C-18)
    "Junior - Senior - Senior",   # Senior FO leads alongside Junior Captain
]
# Any pairing not in this list triggers Rule C-17. The 'Trainee' FO variant
# additionally requires the Captain to hold an LTC/CCI qualification (Rule C-18).

# ---------------------------------------------------------------------------
# Columns used for input validation checks
# ---------------------------------------------------------------------------

REQUIRED_NON_EMPTY_COLS = [
    "Crew code",
    "Prev Day",
    "Schedule Day",
    "Next Day",
    "Crew name",
    "Crew Type",
    "Seniority Level",
    "Is Instructor?",
    "Outstation airport",
]
# Columns in merged_df that must not be empty string for non-leave crew.
# Rule I-1. Note: 'Expiry status' is intentionally excluded here (it is filled
# in merged_data_fun but not validated by input_validation_fun).

REQUIRED_NON_ZERO_COLS = [
    "Max BH left",
    "Max BH left ON",
    "Max DH left",
    "Max sectors left",
]
# Stat columns in merged_df that must not be zero for non-leave crew.
# Rule I-2. A zero value indicates the crew stats file did not provide data.

# ---------------------------------------------------------------------------
# Aircraft type qualification columns (Crew AC Matrix)
# ---------------------------------------------------------------------------

AIRCRAFT_TYPE_COLUMNS = [
    "100",
    "200",
    "300",
    "400",
    "200-G950",
    "300-G600",
    "300-G950",
    "300-GI275",
]
# Column names in the Crew AC Matrix that correspond to TMA aircraft types.
# A value of 1.0 in a column means the crew member is qualified on that type.

# ---------------------------------------------------------------------------
# Pre-loaded model data  (demo / test date range)
# ---------------------------------------------------------------------------

PRELOADED_START_DATE = "2025-09-01"
# First date for which reference files in MODEL_VALIDATIONS_DIR are available.

PRELOADED_END_DATE = "2025-09-08"
# Last date for which reference files in MODEL_VALIDATIONS_DIR are available.
# For any date outside [PRELOADED_START_DATE, PRELOADED_END_DATE] the user
# must upload all files manually.

MODEL_VALIDATIONS_DIR = "Model Validations/"
# Relative path to the directory holding the pre-loaded Excel reference files.
# All pd.read_excel() calls for pre-loaded mode use this prefix.
# Update this path if the data folder is relocated (e.g., to "data/Model Validations/").

# ---------------------------------------------------------------------------
# File-upload identification keywords
# ---------------------------------------------------------------------------

FILE_IDENTIFIERS = {
    "Aircrafts":                 "aircraft",
    "Crew_Aircraft_Type_Matrix": "crew_aircraft",
    "Crew_Pairing":              "seniority",
    "Log_Sheet":                 "logsheet",
    "Crew_Resource":             "crew_master",
    "Crew_License_Expiry":       "expiry_data",
    "Training_Pairings":         "flight_training",
    "Monthly_Plan":              "month_plan",
    "Crewstats":                 "crew_stats",
    "Flight_Plan":               "input_flight_plan",
}
# Maps a keyword (matched case-insensitively against the uploaded filename or
# its first sheet name) to the internal variable name used throughout the app.
# Order matters only if two keywords could match the same filename — put more
# specific keywords first.

# ---------------------------------------------------------------------------
# Output file names
# ---------------------------------------------------------------------------

CREWSTATS_OUTPUT_FILENAME = "Crewstats.xlsx"
# Download filename for the Crew Stats Generator output.

INPUT_VALIDATION_FILENAME = "input_validation.xlsx"
# Download filename for the Input Data Validator Excel report.

CONSTRAINTS_REPORT_FILENAME = "TMA_validation_report_{date}.xlsx"
# Template for the Constraints Validator Excel report filename.
# Format with: CONSTRAINTS_REPORT_FILENAME.format(date=schedule_date)

HTML_REPORT_FILENAME = "TMA_validation_report_{date}.html"
# Template for the HTML report filename.
# Format with: HTML_REPORT_FILENAME.format(date=schedule_date)

# ---------------------------------------------------------------------------
# Chart / clustering settings
# ---------------------------------------------------------------------------

CLUSTERING_TOP_N = 300
# Maximum number of crew members shown in the HTML report bar charts.
# Crew are ranked by the metric (block hours or sectors) and the top N kept.
