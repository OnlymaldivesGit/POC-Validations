"""
reporting/excel_report.py — Excel download report builders.

All BytesIO / ExcelWriter logic extracted from app.py so the page modules
stay free of report-generation concerns.  No business logic lives here —
these functions only package pre-computed DataFrames into workbooks.
"""

import io
import pandas as pd


def build_crewstats_excel(crew_stats_output: pd.DataFrame) -> io.BytesIO:
    """
    Rule: N/A
    Purpose: Package the processed crew statistics DataFrame into a one-sheet
             Excel workbook ready for st.download_button.

    Args:
        crew_stats_output: DataFrame produced by crew_stats_xml(); shape
                           (n_crew, 13+) with columns Crew code, 28 Days BH, etc.

    Returns:
        BytesIO buffer positioned at offset 0, containing a valid .xlsx file
        with a single sheet named 'crew stats'.

    Known issues:
        None
    """
    output = io.BytesIO()
    with pd.ExcelWriter(output, engine="xlsxwriter") as writer:
        crew_stats_output.to_excel(writer, sheet_name="crew stats", index=False)
    output.seek(0)
    return output


def build_input_validation_excel(
    input_issue_1: pd.DataFrame,
    input_issue_2: pd.DataFrame,
    merged_df: pd.DataFrame,
) -> io.BytesIO:
    """
    Rule: I-1, I-2
    Purpose: Package the two input validation violation tables plus the full
             merged input DataFrame into a three-sheet Excel workbook.

    Args:
        input_issue_1: Rule I-1 violations — crew with missing resource fields.
                       Columns: Crew code, Prev Day, Schedule Day, Next Day,
                       Crew name, Crew Type, Seniority Level, Is Instructor?,
                       Outstation airport.
        input_issue_2: Rule I-2 violations — crew with zero stat values.
                       Columns: Crew code, Prev Day, Schedule Day, Next Day,
                       Crew name, Crew Type, plus the four stat columns.
        merged_df:     Full merged crew input DataFrame (all crew in month plan).

    Returns:
        BytesIO buffer at offset 0, .xlsx with sheets
        'Validation 1', 'Validation 2', 'Input data'.

    Known issues:
        None
    """
    output = io.BytesIO()
    with pd.ExcelWriter(output, engine="xlsxwriter") as writer:
        input_issue_1.to_excel(writer, sheet_name="Validation 1", index=False)
        input_issue_2.to_excel(writer, sheet_name="Validation 2", index=False)
        merged_df.to_excel(writer, sheet_name="Input data", index=False)
    output.seek(0)
    return output


def build_constraints_excel(
    Schedule_check: pd.DataFrame,
    crew_mistake_1: pd.DataFrame,
    crew_mistake_11: pd.DataFrame,
    crew_mistake_2: pd.DataFrame,
    crew_mistake_3: pd.DataFrame,
    aircraft_issue: pd.DataFrame,
    Block_hour_issue_1: pd.DataFrame,
    Block_hour_issue_2: pd.DataFrame,
    duty_hour_issue: pd.DataFrame,
    sector_issue_1: pd.DataFrame,
    sector_issue_2: pd.DataFrame,
    swaps_issue: pd.DataFrame,
    get_short_time_diffs_df: pd.DataFrame,
    pairings_issue_1: pd.DataFrame,
    LTC_check: pd.DataFrame,
    training_issue: pd.DataFrame,
    Crew_swaps_violation: pd.DataFrame,
    comparison_master: pd.DataFrame,
    output_master: pd.DataFrame,
    validation_report_1: pd.DataFrame,
    crew_ac_stats: pd.DataFrame,
    metrics_df: pd.DataFrame,
) -> io.BytesIO:
    """
    Rule: C-1 through C-19
    Purpose: Package all constraint violation DataFrames plus summary tables into
             a 22-sheet Excel workbook for download.

    Args:
        All parameters are DataFrames produced by the constraint check functions
        in validation/checklist.py and assembled in pages/page_constraints.py.
        Empty DataFrames are silently skipped (no blank sheet created).

    Returns:
        BytesIO buffer at offset 0, .xlsx with up to 22 named sheets.

    Known issues:
        None
    """
    sheets = [
        (Schedule_check,          "Schedule_check"),
        (crew_mistake_1,          "Crew with Training 1"),
        (crew_mistake_11,         "Crew with Training 2"),
        (crew_mistake_2,          "Error in Starting points"),
        (crew_mistake_3,          "Error in Overnights"),
        (aircraft_issue,          "Error in aircrafts"),
        (Block_hour_issue_1,      "Error in Block hour 1"),
        (Block_hour_issue_2,      "Error in Block hour 2"),
        (duty_hour_issue,         "Error in duty hour"),
        (sector_issue_1,          "Error in sectors 1"),
        (sector_issue_2,          "Error in sectors 2"),
        (swaps_issue,             "Error in AC swaps"),
        (get_short_time_diffs_df, "AC swaps time"),
        (pairings_issue_1,        "Error in seniority pairings"),
        (LTC_check,               "Error in LTC pairings"),
        (training_issue,          "Error in training pairings"),
        (Crew_swaps_violation,    "Crew swaps violation"),
        (comparison_master,       "comparison_master"),
        (output_master,           "output_master"),
        (validation_report_1,     "Report 1"),
        (crew_ac_stats,           "Report 2"),
        (metrics_df,              "Utilization metrics"),
    ]
    output = io.BytesIO()
    with pd.ExcelWriter(output, engine="xlsxwriter") as writer:
        for df, sheet_name in sheets:
            if not df.empty:
                df.to_excel(writer, sheet_name=sheet_name, index=False)
    output.seek(0)
    return output
