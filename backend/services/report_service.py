"""
services/report_service.py — Helpers for building downloadable report artifacts.

Thin wrappers that delegate to the root-level reporting modules so the
routers do not need to import from outside the backend package directly.
"""

import io
import os
import sys

import pandas as pd

# Add project root to path so we can import the reporting modules.
_HERE = os.path.dirname(os.path.abspath(__file__))
_ROOT = os.path.abspath(os.path.join(_HERE, "..", ".."))
if _ROOT not in sys.path:
    sys.path.insert(0, _ROOT)

from reporting.excel_report import build_constraints_excel  # noqa: E402
from reporting.html_report_generator import generate_html_report  # noqa: E402


def build_excel(artifacts: dict) -> bytes:
    """
    Build the constraints Excel report from pre-computed DataFrames.

    Args:
        artifacts: dict produced by validation_service.run_full_validation,
                   keyed with the same names used by build_constraints_excel.

    Returns:
        Raw .xlsx bytes ready for storage or streaming.
    """
    buf = build_constraints_excel(
        Schedule_check=artifacts["Schedule_check"],
        crew_mistake_1=artifacts["crew_mistake_1"],
        crew_mistake_11=artifacts["crew_mistake_11"],
        crew_mistake_2=artifacts["crew_mistake_2"],
        crew_mistake_3=artifacts["crew_mistake_3"],
        aircraft_issue=artifacts["aircraft_issue"],
        Block_hour_issue_1=artifacts["Block_hour_issue_1"],
        Block_hour_issue_2=artifacts["Block_hour_issue_2"],
        duty_hour_issue=artifacts["duty_hour_issue"],
        sector_issue_1=artifacts["sector_issue_1"],
        sector_issue_2=artifacts["sector_issue_2"],
        swaps_issue=artifacts["swaps_issue"],
        get_short_time_diffs_df=artifacts["get_short_time_diffs_df"],
        pairings_issue_1=artifacts["pairings_issue_1"],
        LTC_check=artifacts["LTC_check"],
        training_issue=artifacts["training_issue"],
        Crew_swaps_violation=artifacts["Crew_swaps_violation"],
        comparison_master=artifacts["comparison_master"],
        output_master=artifacts["output_master"],
        validation_report_1=artifacts["validation_report_1"],
        crew_ac_stats=artifacts["crew_ac_stats"],
        metrics_df=artifacts["metrics_df"],
    )
    return buf.getvalue()


def build_html(artifacts: dict) -> str:
    """
    Build the HTML report string from pre-computed DataFrames and KPI values.

    Args:
        artifacts: dict produced by validation_service.run_full_validation.

    Returns:
        Self-contained HTML string.
    """
    return generate_html_report(
        schedule_date=artifacts["schedule_date"],
        metrics_df=artifacts["metrics_df"],
        validation_report_1=artifacts["validation_report_1"],
        crew_ac_stats=artifacts["crew_ac_stats"],
        Schedule_check=artifacts["Schedule_check"],
        unassigned_flights_crew=artifacts["unassigned_flights_crew"],
        Standby_crew=artifacts["Standby_crew"],
        leaves_working=artifacts["leaves_working"],
        crew_mistake_1=artifacts["crew_mistake_1"],
        crew_mistake_11=artifacts["crew_mistake_11"],
        crew_mistake_2=artifacts["crew_mistake_2"],
        crew_mistake_3=artifacts["crew_mistake_3"],
        aircraft_issue=artifacts["aircraft_issue"],
        Block_hour_issue_1=artifacts["Block_hour_issue_1"],
        Block_hour_issue_2=artifacts["Block_hour_issue_2"],
        duty_hour_issue=artifacts["duty_hour_issue"],
        sector_issue_1=artifacts["sector_issue_1"],
        sector_issue_2=artifacts["sector_issue_2"],
        output_crew_stats=artifacts["output_crew_stats"],
        swaps_issue=artifacts["swaps_issue"],
        get_short_time_diffs_df=artifacts["get_short_time_diffs_df"],
        pairings_issue_1=artifacts["pairings_issue_1"],
        LTC_check=artifacts["LTC_check"],
        training_issue=artifacts["training_issue"],
        aircraft_kpi=artifacts["aircraft_kpi"],
        flight_kpi=artifacts["flight_kpi"],
        sectors_kpi=artifacts["sectors_kpi"],
        aircraft_starting_on_kpi=artifacts["aircraft_starting_on_kpi"],
        aircraft_ending_on_kpi=artifacts["aircraft_ending_on_kpi"],
        utilized_captain=artifacts["utilized_captain"],
        utilized_first_officer=artifacts["utilized_first_officer"],
        utilized_flight_attendant=artifacts["utilized_flight_attendant"],
        Standyby_captain=artifacts["Standyby_captain"],
        Standyby_first_officer=artifacts["Standyby_first_officer"],
        Standyby_flight_attendant=artifacts["Standyby_flight_attendant"],
        aircraft_input_kpi=artifacts["aircraft_input_kpi"],
        flight_input_kpi=artifacts["flight_input_kpi"],
        sectors_input_kpi=artifacts["sectors_input_kpi"],
        available_captain=artifacts["available_captain"],
        available_first_officer=artifacts["available_first_officer"],
        available_flight_attendant=artifacts["available_flight_attendant"],
        df_validation=artifacts.get("df_validation"),
        df_validation_captain=artifacts.get("df_validation_captain"),
        df_validation_FO=artifacts.get("df_validation_FO"),
        df_validation_FA=artifacts.get("df_validation_FA"),
    )
