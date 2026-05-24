"""
backend/config.py — Environment variables and constants for the TMA Validator API.

Env vars are loaded from a .env file at startup via python-dotenv.
The validation constants are copied from the root config.py so this package
can run stand-alone (without the root project on sys.path).
"""

import os

from dotenv import load_dotenv

load_dotenv()

# ---------------------------------------------------------------------------
# Runtime environment
# ---------------------------------------------------------------------------

GITHUB_TOKEN: str = os.getenv("GITHUB_TOKEN", "")
GITHUB_REPO: str = os.getenv("GITHUB_REPO", "")
GITHUB_BRANCH: str = os.getenv("GITHUB_BRANCH", "outputs")
CORS_ORIGINS: list[str] = os.getenv("CORS_ORIGINS", "http://localhost:5173").split(",")

# ---------------------------------------------------------------------------
# Status codes  (copied from root config.py)
# ---------------------------------------------------------------------------

AVAILABLE_STATUS: list[str] = ["1", "Li", "LC"]
LEAVE_STATUS: list[str] = ["X", "AL", "AU", "PAL", "EM", "ML", "M"]
HOME_BASE: str = "MLE"

# ---------------------------------------------------------------------------
# Flight time limits  (copied from root config.py)
# ---------------------------------------------------------------------------

BH_28DAY_LIMIT: int = 100
BH_28DAY_ON_LIMIT: int = 98
BH_365DAY_LIMIT: int = 1000
BH_365DAY_ON_LIMIT: int = 998
DT_28DAY_LIMIT: int = 210
DUTY_GROUND_TIME_HOURS: float = 1.5
SECTOR_6DAY_LIMIT: int = 48
SECTOR_DAILY_LIMIT: int = 14
SECTOR_LONG_DAY_THRESHOLD: int = 12
BLOCK_HOUR_MULTIPLIER: float = 1.35
MAX_SWAPS_PER_DAY: int = 1
MIN_SWAP_GAP_MINUTES: int = 45

# ---------------------------------------------------------------------------
# File upload identification keywords  (copied from root config.py)
# ---------------------------------------------------------------------------

FILE_IDENTIFIERS: dict[str, str] = {
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

# ---------------------------------------------------------------------------
# Canonical solver output column names  (TMA defaults)
# ---------------------------------------------------------------------------

CANONICAL_SOLVER_COLUMNS: dict[str, str] = {
    "date":             "Date",
    "flight_no":        "Flight No.",
    "aircraft_no":      "Aircraft No.",
    "std":              "STD -  Scheduled Departure",
    "sta":              "STA -  Scheduled Arrival",
    "dep_airport":      "Dep. Airport",
    "arr_airport":      "Arr. Airport",
    "captain":          "Captain",
    "first_officer":    "First Officer",
    "flight_attendant": "Flight Attendant",
}

# ---------------------------------------------------------------------------
# GitHub storage paths
# ---------------------------------------------------------------------------

OUTPUTS_PREFIX: str = "outputs"
INDEX_PATH: str = "outputs/index.json"
VENDORS_PATH: str = "outputs/vendors.json"
