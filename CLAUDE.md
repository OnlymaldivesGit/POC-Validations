# CLAUDE.md — TMA Crew Scheduler & Validator

---

## Project Overview

**What it does:** This is a Streamlit web application that validates daily crew scheduling outputs produced by an optimization solver for Trans Maldivian Airways (TMA). Before a schedule is published, a crew planner uses this tool to:

1. **Generate crew statistics** — parse raw crew stats from an Excel macro file and produce a processed stats sheet (block hours, duty hours, sector counts).
2. **Validate input data** — confirm that all crew members in the monthly plan have complete master records, seniority data, logsheet positions, and non-zero statistics. Catches missing or zero data before the solver runs.
3. **Validate constraints** — take the solver's output schedule and run ~20 automated rule checks covering scheduling regulations (flight time limits, duty time, sectors, crew pairings, aircraft qualifications, outstation overnight assignments, etc.), then surface violations in the UI and export a full Excel + HTML report.

**Business problem:** Crew scheduling optimization produces a solution that may violate aviation regulations or airline-specific business rules. Manual verification across hundreds of crew members and flights is error-prone and slow. This tool automates that verification, quantifies violations by category, and generates downloadable audit reports.

**End users:** TMA crew planning / corporate strategy team (specifically developed by Himanshu Gupta, Corporate Strategy, +960 7375336). Version 2.0, last updated November 2025.

---

## Tech Stack

| Library | Version | Why it's used |
|---|---|---|
| Python | 3.11 | Runtime (via devcontainer `python:1-3.11-bookworm`) |
| Streamlit | 1.50.0 | Web UI, file upload, tabs, expanders, download buttons |
| streamlit-option-menu | 0.4.0 | Sidebar navigation menu |
| streamlit-aggrid | 1.1.9 | Interactive grid display with sorting, filtering, grouping |
| pandas | 2.3.3 | All data ingestion, transformation, and merging |
| numpy | 2.3.3 | Vectorised comparisons for limit calculations |
| openpyxl | 3.1.5 | Reading `.xlsx` and `.xlsm` files |
| xlsxwriter | 3.2.9 | Writing multi-sheet Excel validation report output |
| plotly | 6.4.0 | Interactive charts in the Constraints Validator (bar, pie) |
| scikit-learn | 1.7.2 | `LabelEncoder`, `StandardScaler` — used in clustering module |
| scipy | 1.16.3 | `pdist`, `squareform` — available but unused in active clustering path |
| matplotlib / seaborn | 3.10.7 / 0.13.2 | Imported in clustering module but not actively used |
| python-decouple | 3.8 | Present in requirements but not used in any module |

---

## Project Structure

```
POC-Validations/
├── app.py                    # Main Streamlit application — all three pages live here
├── input_processing.py       # All input file ingestion & normalisation functions
├── output_processing.py      # Solver output processing: block hours, duty hours, AC groups
├── checklist.py              # All constraint validation functions (the core logic)
├── input_validations.py      # Input completeness checks (missing fields / zero stats)
├── html_report_generator.py  # Generates the downloadable HTML validation report
├── clustering.py             # Crew grouping/clustering by identical parameter profiles
├── dashboard.py              # Standalone standalone flight roster analytics dashboard (separate entry point)
├── Commonfunction.py         # Shared AgGrid display helper (show_aggrid)
├── old_app.py                # Archived previous version of app.py (not active)
├── save_app.py               # Another archived backup of app.py (not active)
├── requirements.txt          # Pinned Python dependencies
├── Sample clustering.xlsx    # Auto-generated side-effect file written during validation
├── .devcontainer/
│   └── devcontainer.json     # GitHub Codespaces config — auto-installs deps and starts app
└── Model Validations/        # Pre-loaded reference data for dates 2025-09-01 to 2025-09-08
    ├── Aircrafts.xlsx         # Aircraft registry with type codes
    ├── Crew AC Matrix.xlsx    # Crew qualification matrix (which crew can fly which AC type)
    ├── Crew Pairing.xlsx      # Crew seniority levels and instructor status
    ├── Crew Stats.xlsx        # Multi-sheet daily crew statistics (one sheet per date)
    ├── Flight Plan.xlsx       # Input flight schedule (flights to be crewed)
    ├── Log sheet.xlsx         # Previous day actual flight log (for outstation detection)
    ├── Model Output.xlsx      # Sample solver output schedule with crew assignments
    ├── Month plan.xlsx        # Monthly roster with daily status codes per crew member
    ├── Resources.xlsx         # Crew master data (names, types)
    ├── Training Expiry.xlsx   # License/training expiry status per crew
    └── Training Pairings.xlsx # Instructor-trainee pairing schedule for flight training
```

---

## How to Run

### In GitHub Codespaces (automatic)
The `.devcontainer/devcontainer.json` handles everything:
```
updateContentCommand: pip install -r requirements.txt && pip install streamlit
postAttachCommand: streamlit run app.py --server.enableCORS false --server.enableXsrfProtection false
```
Port 8501 is forwarded and opened automatically.

### Local setup
```bash
pip install -r requirements.txt
streamlit run app.py
```

The app opens at `http://localhost:8501`.

### Environment variables / config
None required. No `.env` file, no environment variables, no secrets. All configuration is hardcoded.

---

## Input Files

### Automatic (pre-loaded) mode
For schedule dates **2025-09-01 through 2025-09-08**, files are auto-loaded from the `Model Validations/` directory. No upload required.

### Manual upload mode (any other date)
Files are uploaded via a multi-file uploader. The app identifies files by matching the filename (or first sheet name) against these keywords:

| Keyword in filename | Variable | Description |
|---|---|---|
| `Aircrafts` | `aircraft` | Aircraft registry |
| `Crew_Aircraft_Type_Matrix` | `crew_aircraft` | Crew AC qualifications |
| `Crew_Pairing` | `seniority` | Seniority + instructor status |
| `Log_Sheet` | `logsheet` | Previous day flight log |
| `Crew_Resource` | `crew_master` | Crew master data |
| `Crew_License_Expiry` | `expiry_data` | License expiry status |
| `Training_Pairings` | `flight_training` | Today's training pairing schedule |
| `Monthly_Plan` | `month_plan` | Monthly roster |
| `Crewstats` | `crew_stats` | Crew statistics |
| `Flight_Plan` | `input_flight_plan` | Input schedule (flight plan) |

For the Constraints Validator, the **solver output** (`Model Output.xlsx` format) is uploaded separately via the "Solver Output" uploader.

### Required columns per input file

**Aircrafts.xlsx:** `Aircraft code`, `Aircraft Type`

**Crew AC Matrix.xlsx:** `Crew code`, `100`, `200`, `300`, `400`, `200-G950`, `300-G600`, `300-G950`, `300-GI275` (aircraft type codes, value = 1 if qualified)

**Crew Pairing.xlsx:** `Crew code`, `Seniority Level` (Senior/Junior/Trainee), `LTC/CCI` (Yes/No)

**Log sheet.xlsx:** `Date`, `Flight No `, `Aircraft No `, `Actual Time of Arrival`, `Arr Airport`, `Captain`, `First Officer`, `Flight Attendant`

**Resources.xlsx:** `Crew code`, `Crew name`, `Flight personnel type` (Captain/First Officer/Flight Attendant)

**Training Expiry.xlsx:** `Crew code`, `Expiry`

**Training Pairings.xlsx:** `Date`, `Instructor`, `Trainee`, `Training Type`

**Month plan.xlsx:** `Crew code`, `Crew Name`, plus one column per date (column header = date string `YYYY-MM-DD`). Values are status codes (see Key Configuration).

**Crew Stats.xlsx:** Either a multi-sheet file (one sheet per date, sheet name = `YYYY-MM-DD`) or a single-sheet file. Columns: `Crew code`, `-1D` through `-7D`, `28 Days BH`, `27th Day BH`, `365 Days BH`, `364th Day BH`, `28 Days DT`, `Min BH left`, `Min BH left ON`, `Min DH`, `Sectors Left`, `More than 12`.

**Solver Output (Model Output.xlsx format):** `Date`, `Flight No.`, `Aircraft No.`, `STD -  Scheduled Departure`, `STA -  Scheduled Arrival`, `Dep. Airport`, `Arr. Airport`, `Captain`, `First Officer`, `Flight Attendant`

**Flight Plan (input):** Same columns as solver output minus the crew columns, plus `Date`.

---

## Output / Report

### On-screen output
- **Validation Summary** — 8 colour-coded KPI cards (red = issues exist, green = clean)
- **KPI Section** — available aircraft/crew counts, scheduled counts, utilized vs standby breakdowns
- **Expanders** — one per check category; each shows a DataFrame of violations or a green "no issues" box
- **Bar charts** — top crew by block hours and sectors (4 panels: all, captain, FO, FA)
- **Pie charts** — aircraft swap distribution by crew type
- **Common Profile Crews** — crew grouped by identical parameter profiles (clustering result)

### Downloadable outputs

| File | Format | Content |
|---|---|---|
| `Crewstats.xlsx` | Excel, 1 sheet | Processed crew statistics from the macro file |
| `input_validation.xlsx` | Excel, 3 sheets | Validation 1 (missing resources), Validation 2 (missing stats), Input data |
| `TMA_validation_report_{date}.xlsx` | Excel, 22 sheets | All violation DataFrames, comparison master, output master, crew AC stats, utilisation metrics |
| `TMA_validation_report_{date}.html` | HTML | Self-contained visual report with accordions, charts (Chart.js), and all DataFrames |

---

## Key Configuration

### Status codes (hardcoded in multiple files)
```python
available_status = ["1", "Li", "LC"]   # Crew is available to fly
leave_status = ["X", "AL", "AU", "PAL", "EM", "ML", "M"]  # Crew on leave
# Any other code = training
```

### Flight time limits (hardcoded in `input_processing.py`)
| Limit | Threshold |
|---|---|
| 28-day block hours (ending at MLE) | 100 hours |
| 28-day block hours (ending outstation) | 98 hours |
| 365-day block hours (ending at MLE) | 1,000 hours |
| 365-day block hours (ending outstation) | 998 hours |
| 28-day duty time | 210 hours |
| 6-day sector count | 48 sectors |
| Daily sector limit | 14 sectors |
| >12 sectors in a day | Allowed max 2 times in the look-back window (-1D, -2D, -3D) |

### Block hours formula
`Block hours = (STA - STD) × 1.35 / 3600` (applied to each sector; `1.35` is a block-time multiplier)

### Duty hours formula
`Duty hours = (last STA − first STD) + 1.5 hours` (90 minutes ground time added)

### Aircraft swap gap minimum
`45 minutes` between end of first AC assignment and start of second

### Maximum aircraft swaps per crew per day
`1` (crews with `No. of swaps > 1` are flagged)

### Valid seniority pairings (Captain - FO - FA)
```
Senior - Senior - Senior
Senior - Junior - Senior
Senior - Senior - Junior
Senior - Trainee - Senior  (requires Captain to be LTC/CCI instructor)
Junior - Senior - Senior
```

### Home base
`MLE` (Velana International Airport, Male, Maldives)

### Pre-loaded date range
`2025-09-01` to `2025-09-08` (hardcoded in `app.py` lines 532–533)

---

## Known Issues / Broken Logic

### ⚠️ WARNING — "More than 12" formula bug (`input_processing.py`, lines 55 and 71)
```python
merged_df_2["More than 12"] = 2 - (merged_df_2['-1D'] > 12).astype(int) + (merged_df_2['-2D'] > 12).astype(int) + (merged_df_2['-3D'] > 12).astype(int)
```
Due to Python's left-to-right operator precedence, this evaluates as `(2 - A) + B + C`, not `2 - (A + B + C)`. A crew member who flew >12 sectors on all three prior days would get a value of `3` instead of `-1`. This means the constraint check (`Max more than 12 sectors == 0`) would never trigger for this edge case, silently allowing illegal assignments. The correct formula is:
```python
2 - ((df['-1D'] > 12).astype(int) + (df['-2D'] > 12).astype(int) + (df['-3D'] > 12).astype(int))
```
This bug exists in both `crew_stats_xml()` and `new_crew_stats()`.

### ⚠️ WARNING — Index alignment risk in `crew_check_fun` (`checklist.py`, line 39)
```python
on_training_working = on_training[comparison_master["Working Status"] == 1]
```
This filters the subset `on_training` using a boolean mask from the full `comparison_master`. While pandas aligns on index, if `comparison_master` was not reset-indexed this can silently drop rows or include unintended rows.

### ⚠️ WARNING — `crew_mistake_11` catches non-working crew (`checklist.py`, lines 44–46)
`on_training_working_outstations` is derived from `on_training` (all training crew at outstations), **not** from `on_training_working`. Any training crew at an outstation who is **not** in the schedule output at all will have `Total flights = NaN`, and `~(NaN == 1)` is `True`, so they are flagged as an error when they may simply be on legitimate ground duty.

### ⚠️ WARNING — Hardcoded dates in `output_processing.py` (lines 5–7)
```python
schedule_date = "2025-09-08"
prev_day = ...
next_day = ...
```
These variables are defined at module level but never used by any function in the file. They are dead code left from development.

### ⚠️ WARNING — Side-effect file write during validation (`app.py`, line 1639)
```python
crew_groups.to_excel("Sample clustering.xlsx")
```
Every time constraints are validated, `Sample clustering.xlsx` is overwritten in the working directory. This is a debugging artefact that should be removed.

### ⚠️ WARNING — `crew_mistake_2` uses wrong DataFrame (`checklist.py`, line 51)
```python
crew_mistake_2 = available_working[available_working["Starting from"] != available_working["Outstation airport"]]
```
`available_working` has the merged data including `Outstation airport`, but this column represents where the crew **was** at the end of the previous day, so the comparison `Starting from != Outstation airport` is correct. However, `available_working` here is the function's second parameter, which was already filtered to `Schedule Day in available_status` — this is correct.

### ⚠️ WARNING — Entire old implementation commented out (`html_report_generator.py`, lines 1–839)
The first 839 lines of `html_report_generator.py` are a complete commented-out version of the same function. The active code begins at line 840. This creates significant file bloat (97KB) and maintenance confusion.

### ⚠️ WARNING — `dashboard.py` is a separate standalone Streamlit app
`dashboard.py` has its own `st.set_page_config()` call and cannot be run as a page within `app.py`. It must be launched separately (`streamlit run dashboard.py`). There is no navigation link to it from `app.py`.

### ⚠️ WARNING — `old_app.py` and `save_app.py` are stale backups
Both files are full copies of older app versions, tracked in git, and never imported or referenced. They add confusion and should be removed or archived outside the repo.

### ⚠️ WARNING — Crew Stats for uploaded files vs pre-loaded files use different paths
- Pre-loaded: Crew Stats.xlsx is read with `sheet_name=schedule_date` and processed by `new_crew_stats()` which **recalculates** all limits from raw BH/DT data.
- Uploaded: `crew_stats` is processed by `new_crew_stats()` (line 654) which expects the same raw column names as the pre-loaded sheet. But `crew_stats_processing()` exists for a different column mapping (reading `Min BH left` etc. directly). The two paths are inconsistent and `crew_stats_processing()` is only called during the Constraints Validator flow (line 806), creating a dual-path risk.
