"""
services/validation_service.py — Orchestration layer for crew validation.

Imports the root-level processing and validation packages by inserting the
project root into sys.path.  All validation logic stays in the root packages;
this service is purely an adapter/orchestrator for the API layer.
"""

import io
import logging
import os
import sys
from datetime import datetime, timedelta

import pandas as pd

# ---------------------------------------------------------------------------
# Ensure the project root is importable
# ---------------------------------------------------------------------------
_HERE = os.path.dirname(os.path.abspath(__file__))
_ROOT = os.path.abspath(os.path.join(_HERE, "..", ".."))
if _ROOT not in sys.path:
    sys.path.insert(0, _ROOT)

from processing.input_processing import (  # noqa: E402
    aircraft_processing,
    crew_aircraft_processing,
    crew_master_processing,
    crew_stats_processing,
    expiry_data_processing,
    flight_training_processing,
    logsheet_processing,
    merged_data_fun,
    month_plan_processing,
    new_crew_stats,
    schedule_input_processing,
    seniority_processing,
)
from processing.output_processing import (  # noqa: E402
    Schedule_output_processing,
    Schedule_output_processing_2,
    crew_ac_stats_processing,
    output_master_processing,
    overnight_flights,
)
from validation.checklist import (  # noqa: E402
    Schedule_check_fun,
    Stats_check_fun,
    aircraft_check,
    crew_check_fun,
    get_short_time_diffs,
    seniority_check_fun,
    swaps_check_fun,
    training_pairing_check,
    unassigned_flights,
)
from validation.input_validations import input_validation_fun  # noqa: E402
from config import (  # noqa: E402
    AVAILABLE_STATUS,
    LEAVE_STATUS,
    CANONICAL_SOLVER_COLUMNS,
)

logger = logging.getLogger(__name__)


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def _bytes_to_df(raw: bytes) -> pd.DataFrame:
    """Parse Excel bytes (xlsx/xls) to a DataFrame."""
    return pd.read_excel(io.BytesIO(raw))


def _df_to_records(df: pd.DataFrame) -> list[dict]:
    """Convert a DataFrame to a JSON-serialisable list of dicts."""
    return df.where(pd.notnull(df), None).to_dict("records")


def _identify_file(filename: str) -> str | None:
    """Map an uploaded filename to its internal variable name."""
    from config import FILE_IDENTIFIERS
    base = filename.rsplit(".", 1)[0]
    for identifier, var_name in FILE_IDENTIFIERS.items():
        if identifier.lower() in base.lower():
            return var_name
    return None


def normalise_solver_output(df: pd.DataFrame, column_map: dict) -> pd.DataFrame:
    """
    Rename vendor-specific column headers to the canonical TMA column names.

    Args:
        df:         Raw solver output DataFrame as loaded from the vendor file.
        column_map: dict with keys matching SolverColumnMap fields (e.g.
                    'date', 'flight_no') and values being the actual header
                    strings in the vendor file.

    Returns:
        DataFrame with headers renamed to TMA canonical names.  Only columns
        that differ from the canonical name are renamed; others are untouched.
    """
    rename: dict[str, str] = {}
    for field, vendor_col in column_map.items():
        canonical = CANONICAL_SOLVER_COLUMNS.get(field)
        if canonical and vendor_col != canonical and vendor_col in df.columns:
            rename[vendor_col] = canonical
    if rename:
        df = df.rename(columns=rename)
    return df


# ---------------------------------------------------------------------------
# Input validation  (Page 2 equivalent)
# ---------------------------------------------------------------------------

def run_input_validation(files: dict[str, bytes], date: str) -> dict:
    """
    Run the two input completeness checks (Rules I-1 and I-2).

    Args:
        files: dict mapping variable names ('aircraft', 'seniority', …) to
               raw Excel bytes.  All nine standard input files are expected.
        date:  Schedule date string in YYYY-MM-DD format.

    Returns:
        {
            "validation_1": list[dict],   # Rule I-1 violations
            "validation_2": list[dict],   # Rule I-2 violations
            "clean": bool,
        }
    """
    prev_day = (datetime.strptime(date, "%Y-%m-%d") - timedelta(days=1)).strftime("%Y-%m-%d")
    next_day = (datetime.strptime(date, "%Y-%m-%d") + timedelta(days=1)).strftime("%Y-%m-%d")

    aircraft_df        = aircraft_processing(_bytes_to_df(files["aircraft"]))
    crew_aircraft_df   = crew_aircraft_processing(_bytes_to_df(files["crew_aircraft"]))
    seniority_df       = seniority_processing(_bytes_to_df(files["seniority"]))
    logsheet_df        = logsheet_processing(_bytes_to_df(files["logsheet"]), prev_day)
    crew_master_df     = crew_master_processing(_bytes_to_df(files["crew_master"]))
    expiry_df          = expiry_data_processing(_bytes_to_df(files["expiry_data"]))
    flight_training_df = flight_training_processing(_bytes_to_df(files["flight_training"]), date)
    month_plan_df      = month_plan_processing(
        _bytes_to_df(files["month_plan"]), date, prev_day, next_day
    )
    raw_stats          = _bytes_to_df(files["crew_stats"])
    crew_stats_df      = crew_stats_processing(new_crew_stats(raw_stats))

    merged_df = merged_data_fun(
        month_plan_df, crew_master_df, seniority_df, expiry_df, logsheet_df, crew_stats_df
    )
    issue_1, issue_2 = input_validation_fun(merged_df)

    return {
        "validation_1": _df_to_records(issue_1),
        "validation_2": _df_to_records(issue_2),
        "clean": issue_1.empty and issue_2.empty,
    }


# ---------------------------------------------------------------------------
# Full constraints validation  (Page 3 equivalent)
# ---------------------------------------------------------------------------

def run_full_validation(
    files: dict[str, bytes],
    date: str,
    vendor_column_map: dict,
) -> dict:
    """
    Run the complete 19-rule constraints validation pipeline.

    Args:
        files:             dict mapping variable names to raw Excel bytes.
                           Must include all 10 standard input files plus
                           'solver_output'.
        date:              Schedule date string YYYY-MM-DD.
        vendor_column_map: dict from SolverColumnMap (field → vendor header).

    Returns:
        Comprehensive dict containing:
          - 'violations'       : dict of named violation lists (list[dict])
          - 'violation_counts' : the 8 KPI bucket counts
          - 'total_violations' : sum of all 8 buckets
          - 'available_crew'   : {'captain', 'first_officer', 'flight_attendant', 'total'}
          - 'scheduled_crew'   : same shape
          - 'standby_crew'     : same shape
          - 'output_master'    : list[dict]
          - 'validation_report': list[dict]   (validation_report_1)
          - '_artifacts'       : dict of raw DataFrames needed for report generation
                                 (stripped by the router before sending to client)
    """
    prev_day = (datetime.strptime(date, "%Y-%m-%d") - timedelta(days=1)).strftime("%Y-%m-%d")
    next_day = (datetime.strptime(date, "%Y-%m-%d") + timedelta(days=1)).strftime("%Y-%m-%d")

    # ------------------------------------------------------------------
    # 1. Process input files
    # ------------------------------------------------------------------
    aircraft_df        = aircraft_processing(_bytes_to_df(files["aircraft"]))
    crew_aircraft_df   = crew_aircraft_processing(_bytes_to_df(files["crew_aircraft"]))
    seniority_df       = seniority_processing(_bytes_to_df(files["seniority"]))
    logsheet_df        = logsheet_processing(_bytes_to_df(files["logsheet"]), prev_day)
    crew_master_df     = crew_master_processing(_bytes_to_df(files["crew_master"]))
    expiry_df          = expiry_data_processing(_bytes_to_df(files["expiry_data"]))
    flight_training_df = flight_training_processing(_bytes_to_df(files["flight_training"]), date)
    month_plan_df      = month_plan_processing(
        _bytes_to_df(files["month_plan"]), date, prev_day, next_day
    )
    raw_stats          = _bytes_to_df(files["crew_stats"])
    crew_stats_df      = crew_stats_processing(new_crew_stats(raw_stats))
    Schedule_input     = schedule_input_processing(_bytes_to_df(files["input_flight_plan"]))

    # ------------------------------------------------------------------
    # 2. Merge inputs
    # ------------------------------------------------------------------
    merged_df = merged_data_fun(
        month_plan_df, crew_master_df, seniority_df, expiry_df, logsheet_df, crew_stats_df
    )

    # ------------------------------------------------------------------
    # 3. Process solver output
    # ------------------------------------------------------------------
    raw_solver   = _bytes_to_df(files["solver_output"])
    solver_df    = normalise_solver_output(raw_solver, vendor_column_map)
    Schedule_output   = Schedule_output_processing(solver_df)
    Schedule_output_2 = Schedule_output_processing_2(Schedule_output)
    output_master, output_crew_stats = output_master_processing(Schedule_output_2)

    # ------------------------------------------------------------------
    # 4. Build comparison master & crew subsets
    # ------------------------------------------------------------------
    crew_ac_stats    = crew_ac_stats_processing(Schedule_output_2, aircraft_df, crew_aircraft_df)
    comparison_master = merged_df.merge(output_master, on="Crew code", how="outer")

    available_working = comparison_master[
        comparison_master["Schedule Day"].isin(AVAILABLE_STATUS)
        & ~comparison_master["Working Status"].isna()
    ]
    Standby_crew = comparison_master[
        comparison_master["Schedule Day"].isin(AVAILABLE_STATUS)
        & comparison_master["Working Status"].isna()
    ]
    leaves_working = comparison_master[
        comparison_master["Schedule Day"].isin(LEAVE_STATUS)
        & ~comparison_master["Working Status"].isna()
    ]
    on_training = comparison_master[
        ~comparison_master["Schedule Day"].isin(LEAVE_STATUS + AVAILABLE_STATUS)
    ]

    # ------------------------------------------------------------------
    # 5. Run all 19 checks
    # ------------------------------------------------------------------
    unassigned_flights_crew = unassigned_flights(Schedule_output)
    Schedule_check          = Schedule_check_fun(Schedule_output, Schedule_input)
    crew_mistake_1, crew_mistake_11, crew_mistake_2, crew_mistake_3 = crew_check_fun(
        comparison_master, available_working
    )
    aircraft_issue = aircraft_check(crew_ac_stats)
    Block_hour_issue_1, Block_hour_issue_2, duty_hour_issue, sector_issue_1, sector_issue_2 = (
        Stats_check_fun(available_working)
    )
    swaps_issue              = swaps_check_fun(output_master)
    pairings_issue_1, LTC_check = seniority_check_fun(Schedule_output, merged_df)
    training_issue           = training_pairing_check(flight_training_df, Schedule_output)
    get_short_time_diffs_df  = get_short_time_diffs(crew_ac_stats)
    output_df_kpi            = overnight_flights(Schedule_output)
    daily_sector_violation   = output_crew_stats[output_crew_stats["Total sectors"] > 14]

    # ------------------------------------------------------------------
    # 6. KPI counts
    # ------------------------------------------------------------------
    schedule_issues  = len(Schedule_check) + len(unassigned_flights_crew)
    bh_violations    = len(Block_hour_issue_1) + len(Block_hour_issue_2)
    dh_violations    = len(duty_hour_issue)
    sector_violations = len(daily_sector_violation) + len(sector_issue_1) + len(sector_issue_2)
    pairing_issues   = len(pairings_issue_1) + len(LTC_check) + len(training_issue)
    status_issues    = len(leaves_working) + len(crew_mistake_1) + len(crew_mistake_11)
    overnight_issues = len(crew_mistake_2) + len(crew_mistake_3)
    aircraft_issues  = len(aircraft_issue) + len(swaps_issue)

    violation_counts = {
        "schedule_issues":  schedule_issues,
        "bh_violations":    bh_violations,
        "dh_violations":    dh_violations,
        "sector_violations": sector_violations,
        "pairing_issues":   pairing_issues,
        "status_issues":    status_issues,
        "overnight_issues": overnight_issues,
        "aircraft_issues":  aircraft_issues,
    }
    total_violations = sum(violation_counts.values())

    # ------------------------------------------------------------------
    # 7. Crew utilisation KPIs
    # ------------------------------------------------------------------
    complete_scheduled = Schedule_output[
        Schedule_output["Captain"].notna()
        & (Schedule_output["Captain"].str.strip() != "")
        & Schedule_output["First Officer"].notna()
        & (Schedule_output["First Officer"].str.strip() != "")
        & Schedule_output["Flight Attendant"].notna()
        & (Schedule_output["Flight Attendant"].str.strip() != "")
    ]

    aircraft_kpi            = Schedule_output["Aircraft No."].nunique()
    flight_kpi              = Schedule_output["Flight No."].nunique()
    sectors_kpi             = len(complete_scheduled)
    aircraft_starting_on_kpi = len(
        output_df_kpi[(output_df_kpi["Sector Position"] == "Starting") & (output_df_kpi["ON"] == 1)]
    )
    aircraft_ending_on_kpi  = len(
        output_df_kpi[(output_df_kpi["Sector Position"] == "Ending") & (output_df_kpi["ON"] == 1)]
    )
    utilized_captain          = Schedule_output["Captain"].nunique()
    utilized_first_officer    = Schedule_output["First Officer"].nunique()
    utilized_flight_attendant = Schedule_output["Flight Attendant"].nunique()
    Standyby_captain          = len(Standby_crew[Standby_crew["Crew Type_x"] == "Captain"])
    Standyby_first_officer    = len(Standby_crew[Standby_crew["Crew Type_x"] == "First Officer"])
    Standyby_flight_attendant = len(Standby_crew[Standby_crew["Crew Type_x"] == "Flight Attendant"])
    aircraft_input_kpi        = Schedule_input["Aircraft No."].nunique()
    flight_input_kpi          = Schedule_input["Flight No."].nunique()
    sectors_input_kpi         = len(Schedule_input)

    available_test        = merged_df[merged_df["Schedule Day"].isin(AVAILABLE_STATUS)]
    available_captain     = len(available_test[available_test["Crew Type"] == "Captain"])
    available_fo          = len(available_test[available_test["Crew Type"] == "First Officer"])
    available_fa          = len(available_test[available_test["Crew Type"] == "Flight Attendant"])

    # ------------------------------------------------------------------
    # 8. Build validation_report_1
    # ------------------------------------------------------------------
    validation_report_1 = comparison_master[comparison_master["Working Status"] == 1][[
        "Crew code", "Crew name", "Crew Type_x", "Seniority Level", "Is Instructor?",
        "Prev Day", "Schedule Day", "Next Day", "Expiry status", "Outstation airport",
        "Outstation Aircraft", "Max BH left", "Max BH left ON", "Max DH left",
        "Max sectors left", "Max more than 12 sectors", "Starting from", "Ending at",
        "Total flights", "Total aircrafts", "Duty hours", "Total sectors",
        "Block hours", "No. of swaps",
    ]].copy()
    validation_report_1.columns = [
        "Crew code", "Crew Name", "Crew Type", "Seniority Level", "Is Instructor?",
        "Prev Day status", "Schedule Day status", "Next Day status", "Expiry status",
        "Prev day airport", "Prev day aircraft", "Max BH left", "Max BH left ON",
        "Max DH left", "Max sectors left", "Max more than 12 sectors",
        "Starting from", "Ending at", "Total flights", "Total aircrafts",
        "Total duty hours", "Total sectors", "Block hours", "No. of swaps",
    ]
    Crew_swaps_violation = validation_report_1[validation_report_1["No. of swaps"] > 1]

    df_validation = validation_report_1[[
        "Crew code", "Crew Type", "Seniority Level", "Max BH left", "Max BH left ON",
        "Max DH left", "Max sectors left", "Max more than 12 sectors", "Starting from",
        "Ending at", "Total flights", "Total aircrafts", "Total duty hours",
        "Total sectors", "Block hours", "No. of swaps",
    ]].copy()
    df_val_captain = df_validation[df_validation["Crew Type"] == "Captain"]
    df_val_fo      = df_validation[df_validation["Crew Type"] == "First Officer"]
    df_val_fa      = df_validation[df_validation["Crew Type"] == "Flight Attendant"]

    # ------------------------------------------------------------------
    # 9. Metrics DataFrame
    # ------------------------------------------------------------------
    metrics_df = pd.DataFrame({
        "Parameter": [
            "Total Aircraft in Schedule", "Total Flight in Schedule", "Total sectors in Schedule",
            "Total Available Crew in Month Plan", "Available Captains in Month Plan",
            "Available First Officers in Month Plan", "Available Cabin crew in Month Plan",
            "Total Aircraft Scheduled", "Aircraft Scheduled Starting ON", "Aircraft Scheduled Ending ON",
            "Total Flights Scheduled", "Total Sectors Scheduled",
            "Utilized Crew", "Utilized Captain", "Utilized First Officer", "Utilized Flight Attendant",
            "Total Standby crew", "Standby Captain", "Standby First Officer", "Standby Flight Attendant",
            "Total Swap percentage", "Captain Swap percentage",
            "First Officer Swap percentage", "Flight Attendant Swap percentage",
        ],
        "Value": [
            aircraft_input_kpi, flight_input_kpi, sectors_input_kpi,
            available_captain + available_fo + available_fa,
            available_captain, available_fo, available_fa,
            aircraft_kpi, aircraft_starting_on_kpi, aircraft_ending_on_kpi,
            flight_kpi, sectors_kpi,
            utilized_captain + utilized_first_officer + utilized_flight_attendant,
            utilized_captain, utilized_first_officer, utilized_flight_attendant,
            Standyby_captain + Standyby_first_officer + Standyby_flight_attendant,
            Standyby_captain, Standyby_first_officer, Standyby_flight_attendant,
            (df_validation["No. of swaps"] > 0).sum() / max(len(df_validation), 1) * 100,
            (df_val_captain["No. of swaps"] > 0).sum() / max(len(df_val_captain), 1) * 100,
            (df_val_fo["No. of swaps"] > 0).sum() / max(len(df_val_fo), 1) * 100,
            (df_val_fa["No. of swaps"] > 0).sum() / max(len(df_val_fa), 1) * 100,
        ],
    })

    # ------------------------------------------------------------------
    # 10. Assemble return value
    # ------------------------------------------------------------------
    return {
        # JSON-serialisable violation data
        "violations": {
            "schedule_check":          _df_to_records(Schedule_check),
            "unassigned_flights":      _df_to_records(unassigned_flights_crew),
            "leaves_working":          _df_to_records(
                leaves_working[["Crew code", "Schedule Day", "Working Status"]]
                if not leaves_working.empty else leaves_working
            ),
            "crew_mistake_1":          _df_to_records(crew_mistake_1),
            "crew_mistake_11":         _df_to_records(crew_mistake_11),
            "crew_mistake_2":          _df_to_records(crew_mistake_2),
            "crew_mistake_3":          _df_to_records(crew_mistake_3),
            "aircraft_issue":          _df_to_records(aircraft_issue),
            "block_hour_issue_1":      _df_to_records(Block_hour_issue_1),
            "block_hour_issue_2":      _df_to_records(Block_hour_issue_2),
            "duty_hour_issue":         _df_to_records(duty_hour_issue),
            "sector_issue_1":          _df_to_records(sector_issue_1),
            "sector_issue_2":          _df_to_records(sector_issue_2),
            "daily_sector_violation":  _df_to_records(daily_sector_violation),
            "swaps_issue":             _df_to_records(swaps_issue),
            "short_time_diffs":        _df_to_records(get_short_time_diffs_df),
            "pairings_issue_1":        _df_to_records(pairings_issue_1),
            "ltc_check":               _df_to_records(LTC_check),
            "training_issue":          _df_to_records(training_issue),
        },
        "violation_counts":   violation_counts,
        "total_violations":   total_violations,
        "available_crew": {
            "captain": available_captain, "first_officer": available_fo,
            "flight_attendant": available_fa, "total": available_captain + available_fo + available_fa,
        },
        "scheduled_crew": {
            "captain": utilized_captain, "first_officer": utilized_first_officer,
            "flight_attendant": utilized_flight_attendant,
            "total": utilized_captain + utilized_first_officer + utilized_flight_attendant,
        },
        "standby_crew": {
            "captain": Standyby_captain, "first_officer": Standyby_first_officer,
            "flight_attendant": Standyby_flight_attendant,
            "total": Standyby_captain + Standyby_first_officer + Standyby_flight_attendant,
        },
        "output_master":      _df_to_records(output_master),
        "validation_report":  _df_to_records(validation_report_1),
        # Raw DataFrames and scalars needed for report generation (stripped by router)
        "_artifacts": {
            "schedule_date":          date,
            "Schedule_check":         Schedule_check,
            "unassigned_flights_crew": unassigned_flights_crew,
            "Standby_crew":           Standby_crew,
            "leaves_working":         leaves_working,
            "crew_mistake_1":         crew_mistake_1,
            "crew_mistake_11":        crew_mistake_11,
            "crew_mistake_2":         crew_mistake_2,
            "crew_mistake_3":         crew_mistake_3,
            "aircraft_issue":         aircraft_issue,
            "Block_hour_issue_1":     Block_hour_issue_1,
            "Block_hour_issue_2":     Block_hour_issue_2,
            "duty_hour_issue":        duty_hour_issue,
            "sector_issue_1":         sector_issue_1,
            "sector_issue_2":         sector_issue_2,
            "output_crew_stats":      output_crew_stats,
            "swaps_issue":            swaps_issue,
            "get_short_time_diffs_df": get_short_time_diffs_df,
            "pairings_issue_1":       pairings_issue_1,
            "LTC_check":              LTC_check,
            "training_issue":         training_issue,
            "aircraft_kpi":           aircraft_kpi,
            "flight_kpi":             flight_kpi,
            "sectors_kpi":            sectors_kpi,
            "aircraft_starting_on_kpi": aircraft_starting_on_kpi,
            "aircraft_ending_on_kpi": aircraft_ending_on_kpi,
            "utilized_captain":       utilized_captain,
            "utilized_first_officer": utilized_first_officer,
            "utilized_flight_attendant": utilized_flight_attendant,
            "Standyby_captain":       Standyby_captain,
            "Standyby_first_officer": Standyby_first_officer,
            "Standyby_flight_attendant": Standyby_flight_attendant,
            "aircraft_input_kpi":     aircraft_input_kpi,
            "flight_input_kpi":       flight_input_kpi,
            "sectors_input_kpi":      sectors_input_kpi,
            "available_captain":      available_captain,
            "available_first_officer": available_fo,
            "available_flight_attendant": available_fa,
            "crew_ac_stats":          crew_ac_stats,
            "comparison_master":      comparison_master,
            "output_master":          output_master,
            "validation_report_1":    validation_report_1,
            "Crew_swaps_violation":   Crew_swaps_violation,
            "metrics_df":             metrics_df,
            "df_validation":          df_validation,
            "df_validation_captain":  df_val_captain,
            "df_validation_FO":       df_val_fo,
            "df_validation_FA":       df_val_fa,
        },
    }
