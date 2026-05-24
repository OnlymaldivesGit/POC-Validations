# LOGIC.md — Deep Technical Logic & Rules

---

## Data Flow

### Page 1: Crew Stats Generator

1. User uploads a `.xlsm` (Excel macro) file containing 4 sheets: `Sectors`, `FLT`, `27 Days`, `364 Days`.
2. `crew_stats_xml(sectors, flt, day_27th, day_364th)` merges the four sheets on `Crew` column.
3. Raw time values (`HH:MM` strings, `datetime.time` objects, floats) are normalised to decimal hours by `fun(x)`.
4. Derived limit columns are computed: `Min BH left`, `Min BH left ON`, `Min DH`, `Sectors Left`, `More than 12`.
5. Two DataFrames are returned: `crew_stats_output` (raw merged) and `crew_stats_output_2` (processed with limits).
6. `crew_stats_output` is shown in the UI and offered as an Excel download (`Crewstats.xlsx`).

---

### Page 2: Input Data Validator

1. User selects a date. Prev/next day dates are derived.
2. Files are loaded (pre-loaded or uploaded).
3. Each raw file is processed by its dedicated function (see Processing Functions section).
4. `merged_data_fun()` merges all input sources into a single `merged_df` keyed on `Crew code`.
5. `input_validation_fun(merged_df)` runs two checks on `merged_df`.
6. Results shown in two tabs; both violation DataFrames + `merged_df` exported as `input_validation.xlsx`.

---

### Page 3: Constraints Validator (main flow)

1. User selects date; loads 9 input files + 1 solver output file.
2. **Processing phase** (progress bar 10%–80%):
   - Each input file is processed by its dedicated function.
   - `merged_data_fun()` builds `merged_df` — the master crew input record.
   - `Schedule_output_processing()` normalises the solver output.
   - `Schedule_output_processing_2()` explodes wide-format output into per-crew-per-sector rows; computes block hours and Group IDs.
   - `output_master_processing()` aggregates per-crew statistics from the exploded output.
   - `crew_ac_stats_processing()` builds per-crew per-AC-assignment records with qualification lookup.
3. **Merge step**:
   - `comparison_master = merged_df.merge(output_master, on="Crew code", how="outer")` — joins input crew data with output schedule stats.
   - Crew who appear only in input (not scheduled) → right side NaN.
   - Crew who appear only in output (not in month plan) → left side NaN.
4. **Filtering** for downstream checks:
   - `available_working` — crew with `Schedule Day in available_status` AND `Working Status == 1` (they are available AND were actually scheduled).
   - `Standby_crew` — crew with `Schedule Day in available_status` AND `Working Status is NaN` (available but not used).
   - `leaves_working` — crew with `Schedule Day in leave_status` AND `Working Status not NaN` (on leave but scheduled — error).
   - `on_training` — crew whose schedule code is not leave and not available (training).
   - `on_training_working` — subset of `on_training` filtered by `comparison_master["Working Status"] == 1`.
5. **Validation checks** (progress bar 90%): 13 check functions called, producing violation DataFrames.
6. **KPI computation** — counts and percentages from the results.
7. **Report generation** — validation DataFrames assembled into `validation_report_1`, exported to 22-sheet Excel.
8. **Clustering** — `cluster_fun()` groups crew by identical parameter profiles using `CrewGrouping`.
9. **HTML report** — `generate_html_report()` builds a self-contained HTML string with embedded Chart.js charts; offered as download.

---

## Data Structures

### `merged_df` (core input DataFrame)
**Created by:** `merged_data_fun()` in `input_processing.py`  
**Schema:**

| Column | Type | Source |
|---|---|---|
| `Crew code` | str | `month_plan` |
| `Prev Day` | str | `month_plan` — status code for day before schedule date |
| `Schedule Day` | str | `month_plan` — status code for schedule date |
| `Next Day` | str | `month_plan` — status code for day after schedule date |
| `Crew name` | str | `crew_master` (left join) |
| `Crew Type` | str | `crew_master` — "Captain", "First Officer", "Flight Attendant" |
| `Seniority Level` | str | `seniority` — "Senior", "Junior", "Trainee" |
| `Is Instructor?` | str | `seniority` — "Yes" or "No" |
| `Expiry status` | str/int | `expiry_data` |
| `Outstation airport` | str | `logsheet` (previous day last arrival airport) or inferred as "MLE" |
| `Outstation Aircraft` | str | `logsheet` (previous day last aircraft) |
| `Max BH left` | float | `crew_stats` — remaining 28/365-day block hour capacity |
| `Max BH left ON` | float | `crew_stats` — same but with outstation adjustment |
| `Max DH left` | float | `crew_stats` — remaining duty hours |
| `Max sectors left` | float | `crew_stats` — remaining 6-day sector capacity |
| `Max more than 12 sectors` | float | `crew_stats` — remaining slots to fly >12 sectors |

**Size:** One row per crew member who appears in the month plan on schedule_date.  
**Key inference rule:** If `Prev Day not in available_status` and `Outstation airport == ""`, then `Outstation airport = "MLE"`.

---

### `Schedule_output` (raw solver output)
**Created by:** `pd.read_excel(output_flight_plan)` + `Schedule_output_processing()`  
**Schema:** `Date`, `Flight No.`, `Aircraft No.`, `STD - Scheduled Departure`, `STA - Scheduled Arrival`, `Dep. Airport`, `Arr. Airport`, `Captain`, `First Officer`, `Flight Attendant`  
**Shape:** One row per sector (leg), with crew codes as strings in the three crew columns.

---

### `Schedule_output_2` (exploded, per-crew-per-sector)
**Created by:** `Schedule_output_processing_2()`  
**Schema:**

| Column | Notes |
|---|---|
| `Date`, `Flight No.`, `Aircraft No.`, `STD`, `STA`, `Dep. Airport`, `Arr. Airport` | From Schedule_output |
| `Crew Type` | "Captain", "First Officer", or "Flight Attendant" |
| `Crew code` | Crew member for this row |
| `Block hours` | `(STA - STD).total_seconds() × 1.35 / 3600` |
| `Group id` | Increments whenever `Crew code` OR `Aircraft No.` changes from previous row (cumsum trick) |

**Purpose:** Each sector appears three times (once per crew role). `Group id` tracks contiguous segments where a crew member stays on the same aircraft.

---

### `output_master` (per-crew summary)
**Created by:** `output_master_processing()`  
**Schema:**

| Column | Meaning |
|---|---|
| `Crew code` | Crew identifier |
| `Crew Type` | Captain / First Officer / Flight Attendant |
| `Starting from` | Departure airport of their first sector |
| `Ending at` | Arrival airport of their last sector |
| `Total flights` | Count of unique flight numbers |
| `Total aircrafts` | Count of unique aircraft |
| `Total sectors` | Count of total sector rows (not unique flights) |
| `Block hours` | Sum of block hours across all sectors |
| `No. of swaps` | `nunique(Group id) - 1` — number of aircraft changes |
| `Duty hours` | `(last STA − first STD) in hours + 1.5` |
| `Working Status` | Always `1` (set during creation) |

---

### `comparison_master` (merged input + output)
**Created by:** `merged_df.merge(output_master, on="Crew code", how="outer")`  
**Purpose:** Single DataFrame with both planning data (what was expected) and schedule data (what the solver produced). Used for nearly all constraint checks.  
**Note:** `Crew Type` appears twice — as `Crew Type_x` (from `merged_df`) and `Crew Type_y` (from `output_master`).

---

### `crew_ac_stats` (per-crew per-AC-assignment)
**Created by:** `crew_ac_stats_processing()`  
**Schema:** `Group id`, `Crew code`, `Assigned AC`, `Start time`, `End time`, `Aircraft Type`, `qualified`  
**Purpose:** Each row = one contiguous block where a crew member was on one aircraft. Used for qualification checks and swap time gap checks.

---

### `metrics_df` (utilisation KPI table)
**Created in:** `app.py`  
**Schema:** `Parameter` (str), `Value` (numeric)  
**Content:** 24 rows covering aircraft counts, crew availability, utilisation, standby, and swap percentages by crew type.

---

## Validation Rules & Constraints

### INPUT VALIDATOR (Page 2)

---

#### Rule I-1: Missing Resource Data
**Function:** `input_validation_fun()` in `input_validations.py`  
**Operates on:** `merged_df` (after filtering out leave status rows)  
**Logic:** Any crew member not on leave who has an empty string in any of these columns:
```
'Crew code', 'Prev Day', 'Schedule Day', 'Next Day', 'Crew name',
'Crew Type', 'Seniority Level', 'Is Instructor?', 'Outstation airport'
```
Note: `Expiry status` is NOT included in this check (different from `merged_data_fun` which has it in `cols_empty`).  
**PASS:** All listed fields are non-empty for all non-leave crew.  
**FAIL:** One or more crew have at least one empty field. Returns subset of `merged_df` with just the 9 columns above.

---

#### Rule I-2: Missing Statistics
**Function:** `input_validation_fun()` in `input_validations.py`  
**Operates on:** `merged_df` (after filtering out leave status rows)  
**Logic:** Any crew member not on leave who has a value of `0` in any of:
```
'Max BH left', 'Max BH left ON', 'Max DH left', 'Max sectors left'
```
**PASS:** All four stat columns are non-zero for all non-leave crew.  
**FAIL:** Returns crew with any zero stat, plus columns `['Crew code', 'Prev Day', 'Schedule Day', 'Next Day', 'Crew name', 'Crew Type'] + cols_zero`.

---

### CONSTRAINTS VALIDATOR (Page 3)

---

#### Rule C-1: Schedule Consistency
**Function:** `Schedule_check_fun()` in `checklist.py`  
**Operates on:** `Schedule_output` (solver output) vs `Schedule_input` (flight plan input)  
**Logic:** Outer-merges output and input on `['Date', 'Flight No.', 'Aircraft No.', 'STD', 'STA', 'Dep. Airport', 'Arr. Airport']`. Any row that is NOT in both tables is a discrepancy.  
**PASS:** All rows appear in both input and output.  
**FAIL:** Returns rows with `_merge = 'only in output'` (solver added flights not in plan) or `'only in input'` (solver dropped planned flights).  
**UI label:** "Schedule Issues" (counted together with Rule C-2)

---

#### Rule C-2: Unassigned Flights
**Function:** `unassigned_flights()` in `checklist.py`  
**Operates on:** `Schedule_output`  
**Logic:** Any row in the solver output where `Captain`, `First Officer`, or `Flight Attendant` is null or empty string.  
**PASS:** Every flight has all three crew positions filled.  
**FAIL:** Returns the rows with missing crew positions.  
**UI label:** "Unassigned Flights"

---

#### Rule C-3: Leave Crew Scheduled
**Computed in:** `app.py` (not a separate function)  
**Operates on:** `comparison_master`  
**Logic:**
```python
leaves_working = comparison_master[
    (comparison_master["Schedule Day"].isin(leave_status)) &
    (~comparison_master["Working Status"].isna())
]
```
**PASS:** No crew with leave status appears in the schedule output.  
**FAIL:** Crew whose monthly plan shows a leave code (`X, AL, AU, PAL, EM, ML, M`) but who appear in the solver output.  
**UI label:** "Non-Available Crew Check" / counted in "Status Issues"

---

#### Rule C-4: Training Crew at Base Scheduled
**Function:** `crew_check_fun()` in `checklist.py` → returns `crew_mistake_1`  
**Operates on:** `comparison_master`  
**Logic:**
1. Filter to `on_training` (schedule code not in leave_status and not in available_status).
2. Filter `on_training_working` (those in step 1 who are also in the solver output — `Working Status == 1`).
3. Flag any of those whose `Outstation airport` is `""` or `"MLE"` (they are at base, not an outstation).

**Rationale:** Training crew at base should not be scheduled for flights (they're in simulator or ground training). Exception: training crew at an outstation may fly one sector to return home (see Rule C-5).  
**PASS:** No training-coded crew at MLE appears in the solver output.  
**FAIL:** Returns `['Crew code', 'Prev Day', 'Schedule Day', 'Next Day', 'Outstation airport', 'Working Status']`.  
**UI label:** "Error in crew on Training (left panel)"

---

#### Rule C-5: Training Crew at Outstation — Single Flight Only
**Function:** `crew_check_fun()` in `checklist.py` → returns `crew_mistake_11`  
**Operates on:** `comparison_master`  
**Logic:**
1. From `on_training`, filter those whose `Outstation airport` is NOT `""` or `"MLE"` (they are at an outstation).
2. Flag any of those where `Total flights != 1`.

**Rationale:** A training crew member at an outstation is permitted exactly one flight (to return to base). More than 1 flight or no flight at all is wrong.  
⚠️ **WARNING:** This uses `on_training` (all training crew at outstations), not `on_training_working`. Crew not in the schedule at all will have `Total flights = NaN`, and `NaN != 1` evaluates to `True`, so they are incorrectly flagged.  
**PASS:** Every training crew member at an outstation has exactly 1 flight.  
**FAIL:** Returns `['Crew code', 'Prev Day', 'Schedule Day', 'Outstation airport', 'Total flights', 'Working Status']`.  
**UI label:** "Error in crew on Training (right panel)"

---

#### Rule C-6: Starting Position Mismatch
**Function:** `crew_check_fun()` in `checklist.py` → returns `crew_mistake_2`  
**Operates on:** `available_working` (available crew who are scheduled)  
**Logic:**
```python
crew_mistake_2 = available_working[
    available_working["Starting from"] != available_working["Outstation airport"]
]
```
`Starting from` = departure airport of their first sector in the solver output.  
`Outstation airport` = where they were at end of the previous day (from logsheet or inferred as MLE).  
**PASS:** First sector departure matches previous day's last arrival location.  
**FAIL:** Returns `['Crew code', 'Starting from', 'Outstation airport', 'Prev Day', 'Schedule Day']`.  
**UI label:** "Starting Point Errors" / counted in "Overnight Issues"

---

#### Rule C-7: Overnight at Non-Home Base When Next Day is Leave
**Function:** `crew_check_fun()` in `checklist.py` → returns `crew_mistake_3`  
**Operates on:** `available_working`  
**Logic:**
1. Find crew whose last sector ends at a non-MLE airport (`Ending at != "MLE"`).
2. Of those, flag any whose `Next Day` status is a leave code.

```python
crew_mistake_3 = available_working[comparison_master['Ending at'] != "MLE"]
crew_mistake_3 = crew_mistake_3[crew_mistake_3["Next Day"].isin(leave_status)]
```
**Rationale:** If a crew member ends their day at an outstation and they're on leave tomorrow, there is no flight to bring them home.  
**PASS:** No available crew ends the day at an outstation if their next day is leave.  
**FAIL:** Returns `['Crew code', 'Next Day', 'Ending at']`.  
**UI label:** "Next day Overnight Assignment Errors" / counted in "Overnight Issues"

---

#### Rule C-8: Aircraft Qualification
**Function:** `aircraft_check()` in `checklist.py`  
**Operates on:** `crew_ac_stats`  
**Logic:**
```python
return crew_ac_stats[crew_ac_stats["qualified"] != 1.0]
```
`qualified` is looked up via `get_qualification()` in `crew_ac_stats_processing()`:
```python
matched = crew_aircraft.loc[crew_aircraft['Crew code'] == x['Crew code'], x['Aircraft Type']]
return matched.values[0] if not matched.empty else "Not found"
```
If the crew member's qualification value for the assigned aircraft type is not exactly `1.0`, they are unqualified.  
**PASS:** Every crew member is qualified (value = 1.0) for the aircraft type they are assigned to.  
**FAIL:** Returns the `crew_ac_stats` rows where qualification is not 1.0 (includes `0`, `NaN`, `"Not found"`).  
**UI label:** "Aircraft Eligibility Errors" / counted in "Aircraft Issues"

---

#### Rule C-9: Block Hour Limit (Ending at MLE)
**Function:** `Stats_check_fun()` in `checklist.py` → returns `Block_hour_issue_1`  
**Operates on:** `available_working`  
**Logic:**
```python
Block_hour_issue_1 = available_working[
    available_working["Block hours"] > available_working["Max BH left"]
]
```
`Block hours` = total block hours scheduled for today (sum across all sectors for this crew member).  
`Max BH left` = minimum of `(100 − 28-day BH)` and `(1000 − 365-day BH)`.  
**Threshold:** Block hours today must not exceed remaining 28-day capacity (100h limit) or remaining 365-day capacity (1000h limit).  
**PASS:** `Block hours ≤ Max BH left` for all available crew.  
**FAIL:** Crew whose today's schedule would push them over the 28-day or 365-day limit.  
**UI label:** "Block Hour Violations (Crew ending at MLE)" / counted in "BH violations"

---

#### Rule C-10: Block Hour Limit (Ending at Outstation)
**Function:** `Stats_check_fun()` in `checklist.py` → returns `Block_hour_issue_2`  
**Operates on:** `available_working`  
**Logic:**
```python
Block_hour_issue_2 = available_working[
    available_working["Block hours"] > available_working["Max BH left ON"]
]
Block_hour_issue_2 = Block_hour_issue_2[Block_hour_issue_2["Ending at"] != "MLE"]
```
`Max BH left ON` = minimum of `(98 − 28-day BH + 27th-day BH)` and `(998 − 365-day BH + 364th-day BH)`.  
**Rationale:** Crew ending at an outstation will fly home tomorrow, so today's limit is tighter (98h / 998h instead of 100h / 1000h). The 27th-day and 364th-day BH values are added back because those flying days will roll out of the window.  
**PASS:** No crew ending at outstation today exceeds the outstation block hour capacity.  
**FAIL:** Returns those who do.  
**UI label:** "Block Hour Violations (Crew ending at outstation)" / counted in "BH violations"

---

#### Rule C-11: Monthly Duty Hour Limit
**Function:** `Stats_check_fun()` in `checklist.py` → returns `duty_hour_issue`  
**Operates on:** `available_working`  
**Logic:**
```python
duty_hour_issue = available_working[
    available_working['Duty hours'] > available_working["Max DH left"]
]
```
`Duty hours` = total duty hours today (first STD to last STA + 1.5h).  
`Max DH left` = `210 − 28-day duty time`.  
**Threshold:** 28-day duty time limit is 210 hours.  
**PASS:** `Duty hours ≤ Max DH left` for all available crew.  
**FAIL:** Returns crew who would exceed the monthly duty time limit.  
**UI label:** "Monthly Duty Hour Violations" / counted in "DH violations"

---

#### Rule C-12: Weekly Sector Limit
**Function:** `Stats_check_fun()` in `checklist.py` → returns `sector_issue_1`  
**Operates on:** `available_working`  
**Logic:**
```python
sector_issue_1 = available_working[
    available_working['Total sectors'] > available_working["Max sectors left"]
]
```
`Total sectors` = number of sector rows for this crew member in today's schedule.  
`Max sectors left` = `48 − sum(-1D through -6D)` (sectors in the past 6 days).  
**Threshold:** Rolling 7-day window (including today) capped at 48 sectors.  
**PASS:** `Total sectors ≤ Max sectors left`.  
**FAIL:** Returns crew who exceed the 6-day sector budget.  
**UI label:** "Sector Violations (weekly)" / counted in "Sectors violations"

---

#### Rule C-13: >12 Sectors in a Day Limit
**Function:** `Stats_check_fun()` in `checklist.py` → returns `sector_issue_2`  
**Operates on:** `available_working`  
**Logic:**
```python
sector_issue_2 = available_working[
    (available_working['Total sectors'] > 12) &
    (available_working['Max more than 12 sectors'] == 0)
]
```
**Threshold:** A crew member may fly >12 sectors in a single day at most 2 times in any rolling window (looking at -1D, -2D, -3D). If they have already done this twice (i.e., `Max more than 12 sectors == 0`), they cannot fly >12 sectors today.  
⚠️ **WARNING:** `Max more than 12 sectors` is computed with a bug (see CLAUDE.md Rule I-2 warning). The formula `2 - A + B + C` instead of `2 - (A + B + C)` means this check will under-report violations.  
**PASS:** Any crew flying >12 sectors today still has remaining "slots" (value > 0).  
**FAIL:** Returns crew who would fly >12 sectors today but have no remaining allowance.  
**UI label:** "Sector Violations (>12 rule)" / counted in "Sectors violations"

---

#### Rule C-14: Daily Sector Limit
**Computed in:** `app.py` (not a separate function)  
**Operates on:** `output_crew_stats`  
**Logic:**
```python
daily_sector_violation = output_crew_stats[output_crew_stats["Total sectors"] > 14]
```
**Threshold:** A crew member may not fly more than 14 sectors in a single day.  
**PASS:** `Total sectors ≤ 14` for all crew.  
**FAIL:** Returns `output_crew_stats` rows exceeding 14.  
**UI label:** "Sector Violations (daily)" / counted in "Sectors violations"

---

#### Rule C-15: Aircraft Swap Count
**Function:** `swaps_check_fun()` in `checklist.py`  
**Operates on:** `output_master`  
**Logic:**
```python
return output_master[output_master["No. of swaps"] > 1]
```
`No. of swaps = nunique(Group id) - 1` where Group id increments when Crew code or Aircraft No. changes.  
**Threshold:** A crew member may swap to a different aircraft at most once per day.  
**PASS:** `No. of swaps ≤ 1` for all crew.  
**FAIL:** Returns crew with >1 swap.  
**UI label:** "Aircraft Swap Violations" / counted in "Aircraft Issues"

---

#### Rule C-16: Aircraft Swap Time Gap
**Function:** `get_short_time_diffs()` in `checklist.py`  
**Operates on:** `crew_ac_stats` (per-crew per-AC blocks)  
**Logic:**
1. Find crew members who have more than one aircraft assignment (`value_counts > 1`).
2. For each such crew, pair their first AC block end time with their second AC block start time.
3. Compute `Time difference = (Second AC start − First AC end) in minutes`.
4. Flag where `Time difference < 45` minutes.

**Threshold:** Minimum 45 minutes gap between releasing one aircraft and starting duties on another.  
**PASS:** All AC swaps have ≥ 45 minutes gap.  
**FAIL:** Returns table with `First AC ST`, `First AC ET`, `Second AC ST`, `Second AC ET`, `Time difference`.  
**UI label:** "Aircraft Swap Violations (time gap)" / shown in same expander as Rule C-15

---

#### Rule C-17: Crew Pairing Seniority
**Function:** `seniority_check_fun()` in `checklist.py` → returns `pairings_issue_1`  
**Operates on:** `Schedule_output` (per-sector, with Captain / FO / FA crew codes)  
**Logic:**
1. For each sector, look up the seniority level of the Captain, FO, and FA in `merged_df`.
2. Build a composite string `"{Cap level} - {FO level} - {FA level}"`.
3. Flag any sector where the composite is NOT in the allowed list.

**Valid pairings:**
```
'Senior - Senior - Senior'
'Senior - Junior - Senior'
'Senior - Senior - Junior'
'Senior - Trainee - Senior'
'Junior - Senior - Senior'
```

If a crew member's code is not found in `merged_df`, their level defaults to `"X"`, which will always fail the pairing check.  
**PASS:** Every sector's crew pairing matches one of the five valid combinations.  
**FAIL:** Returns sectors with invalid pairings, including the `Pairing` composite column.  
**UI label:** "Pairing Rule Violations (seniority)" / counted in "Pairing Issues"

---

#### Rule C-18: LTC/Instructor Requirement for Trainee Pairing
**Function:** `seniority_check_fun()` in `checklist.py` → returns `LTC_check`  
**Operates on:** `Schedule_output` (sectors with `Pairing == 'Senior - Trainee - Senior'`)  
**Logic:**
1. Identify sectors where the pairing is `'Senior - Trainee - Senior'` (FO is a trainee).
2. For each such sector, check if the Captain has `Is Instructor? == "Yes"` (i.e., `LTC/CCI == "Yes"` in the seniority data).
3. Flag sectors where Captain is NOT an instructor.

```python
LTC_check["Instructor check"] = LTC_check.apply(get_instructor_check, axis=1)
LTC_check = LTC_check[LTC_check["Instructor check"] == "No"]
```
**Rationale:** Only Line Training Captains (LTC) or Check/Chief Instructors (CCI) may fly with trainees in the FO seat.  
**PASS:** Every trainee-in-FO pairing has an LTC/CCI as Captain.  
**FAIL:** Returns sectors where a non-instructor captain is paired with a trainee FO.  
**UI label:** "Pairing Rule Violations (LTC)" / counted in "Pairing Issues"

---

#### Rule C-19: Training Pairing Accuracy
**Function:** `training_pairing_check()` in `checklist.py`  
**Operates on:** `flight_training` (today's instructor-trainee plan), `Schedule_output`  
**Logic:**
1. For each instructor, look up who they are actually flying with (as Captain → what FO).
2. For each trainee, look up who they are actually flying with (as FO → what Captain).
3. Compare `Actual Pairing` against the planned `Paired with` field.
4. Flag rows where they don't match.

**PASS:** Every instructor-trainee pairing in the training plan is accurately reflected in the solver output.  
**FAIL:** Returns rows from the training plan where the actual schedule does not match the planned pairing.  
**UI label:** "Pairing Rule Violations (training)" / counted in "Pairing Issues"

---

## Breakage Logic (CRITICAL SECTION)

A "break" is any violation of the rules above. The application detects, counts, and categorises all breaks as follows:

### Break Detection
Each validation function returns a DataFrame. An **empty** DataFrame = no violations (PASS). A **non-empty** DataFrame = one or more violations (FAIL), one violation per row.

### Break Categorisation and Counting

| UI Category | Break Count Formula | Rules Included |
|---|---|---|
| Schedule Issues | `len(Schedule_check) + len(unassigned_flights_crew)` | C-1, C-2 |
| BH violations | `len(Block_hour_issue_1) + len(Block_hour_issue_2)` | C-9, C-10 |
| DH violations | `len(duty_hour_issue)` | C-11 |
| Sectors violations | `len(daily_sector_violation) + len(sector_issue_1) + len(sector_issue_2)` | C-12, C-13, C-14 |
| Pairing Issues | `len(pairings_issue_1) + len(LTC_check) + len(training_issue)` | C-17, C-18, C-19 |
| Status Issues | `len(leaves_working) + len(crew_mistake_1) + len(crew_mistake_11)` | C-3, C-4, C-5 |
| Overnight Issues | `len(crew_mistake_2) + len(crew_mistake_3)` | C-6, C-7 |
| Aircraft Issues | `len(aircraft_issue) + len(swaps_issue)` | C-8, C-15 |

**Note:** Rule C-16 (swap time gap) is shown alongside Aircraft Issues but is NOT counted in the "Aircraft Issues" KPI metric.

### Break Surfacing in the UI
1. **Summary cards** at top of Constraints Validator page: 8 coloured metric cards (red = issues, green = clean).
2. **Expanders** below: one per issue category, each showing the full violation DataFrame or a green "no issues" box.
3. **Sidebar expander note in Excel report**: 22 separate sheets, one per violation DataFrame.
4. **HTML report**: Accordion sections for each category; red/green status badges inline.

### Severity Levels
There are no formal severity tiers in the code. All breaks are treated equivalently — they appear in the count, in the UI, and in the download. The only implicit priority is the ordering of the eight KPI cards, where Schedule Issues appear first.

---

## Processing Functions

### `fun(x)` — `input_processing.py`
**Inputs:** A cell value (NaN, float, `datetime.time`, or `"HH:MM"` string)  
**Output:** Decimal hours (float)  
**Logic:** Converts any time representation to a float:
- NaN → 0
- float → as-is
- `datetime.time` → `hour + minute/60`
- `"HH:MM"` string → split on `:`, parse

---

### `crew_stats_xml(sectors, flt, day_27th, day_364th)` — `input_processing.py`
**Inputs:** Four DataFrames from the `.xlsm` stats macro.  
**Output:** `(merged_df, merged_df_2)` — raw merged and processed with derived limits.  
**Steps:**
1. Removes `Total`/`Applied` summary rows from each input.
2. Standardises column names and selects relevant columns.
3. Merges all four on `Crew` (left join chain).
4. Converts BH/DT columns via `fun()`.
5. Computes `Min BH left`, `Min BH left ON`, `Min DH`, `Sectors Left`, `More than 12`.

---

### `new_crew_stats(crew_stats)` — `input_processing.py`
**Inputs:** Single-sheet crew stats DataFrame (same schema as Crew Stats.xlsx date sheets).  
**Output:** Processed crew stats with derived limit columns.  
**Purpose:** Used when crew stats come from an uploaded file (already in `new_crew_stats` format), recalculates limit columns in case the uploaded file has raw cumulative BH/DT values.

---

### `schedule_input_processing(Schedule_input)` — `input_processing.py`
**Inputs:** Flight plan DataFrame.  
**Output:** Cleaned flight plan.  
**Steps:**
1. Strips whitespace from all key columns.
2. Removes rows where `Dep. Airport == Arr. Airport` (ground turn-arounds).
3. Removes rows where `Flight No.` is NaN.

---

### `aircraft_processing(aircraft)` — `input_processing.py`
**Output:** `['Aircraft Code', 'Aircraft Type']` — two-column lookup table.

---

### `crew_aircraft_processing(crew_aircraft)` — `input_processing.py`
**Output:** `['Crew code', '100', '200', '300', '400', '200-G950', '300-G600', '300-G950', '300-GI275']`.  
**Steps:** Strips parenthetical suffixes from Crew code (e.g., `"AAFZ(C)"` → `"AAFZ"`). Selects qualification columns only.

---

### `crew_stats_processing(crew_stats)` — `input_processing.py`
**Output:** `['Crew code', 'Max BH left', 'Max BH left ON', 'Max DH left', 'Max sectors left', 'Max more than 12 sectors']`.  
**Note:** Reads pre-computed limits directly from the Crew Stats file. Renames `Min BH left` → `Max BH left`, etc. (naming is inverted but semantically they are "capacity remaining").

---

### `logsheet_processing(logsheet, prev_day)` — `input_processing.py`
**Inputs:** Log sheet DataFrame, previous day date string.  
**Output:** Per-crew last airport and last aircraft from previous day.  
**Steps:**
1. Selects relevant columns; filters to `Date == prev_day`.
2. Melts Captain / FO / FA columns → long format (one row per crew per sector).
3. Strips parenthetical suffixes from crew codes.
4. Parses `Actual Time of Arrival` as time.
5. **For each crew, keeps only the row with the latest arrival time** (last flight of the previous day → their outstation position).
6. Returns `['Crew code', 'Outstation airport', 'Outstation Aircraft']`.

---

### `month_plan_processing(month_plan, schedule_date, prev_day, next_day)` — `input_processing.py`
**Output:** `['Crew code', 'Prev Day', 'Schedule Day', 'Next Day']`.  
**Steps:**
1. Column headers that start with `'2025-'` are truncated to just the date portion.
2. Strips whitespace and parenthetical suffixes from `Crew code`.
3. Selects only the three relevant date columns plus `Crew code`.
4. Drops rows where `Schedule Day` is NaN (crew not in plan for this month).
5. Casts all three day columns to string.

---

### `flight_training_processing(flight_training, schedule_date)` — `input_processing.py`
**Output:** Training pairings DataFrame filtered to `Date == schedule_date`.

---

### `expiry_data_processing(expiry_data)` — `input_processing.py`
**Output:** `['Crew code', 'Expiry status']`.  
**Steps:** Selects `Crew code` and `Expiry` columns, renames, strips parenthetical suffixes.

---

### `seniority_processing(seniority)` — `input_processing.py`
**Output:** `['Crew code', 'Seniority Level', 'Is Instructor?']`.  
**Steps:** Selects and renames from `Crew Pairing.xlsx`. Strips crew code suffixes.

---

### `crew_master_processing(crew_master)` — `input_processing.py`
**Output:** `['Crew code', 'Crew name', 'Crew Type']`.  
**Steps:** Selects and renames from `Resources.xlsx`. Drops rows with null `Crew code`.

---

### `merged_data_fun(month_plan, crew_master, seniority, expiry_data, logsheet, crew_stats)` — `input_processing.py`
**Output:** `merged_df` — the master input record.  
**Steps:**
1. Left-join chain: `month_plan` → `crew_master` → `seniority` → `expiry_data` → `logsheet` → `crew_stats` (all on `Crew code`).
2. Fill NaN in string columns with `""`.
3. Fill NaN in numeric stat columns with `0`, cast to float.
4. **Outstation inference:** If `Prev Day not in available_status` AND `Outstation airport == ""`, set `Outstation airport = "MLE"`.

---

### `Schedule_output_processing(Schedule_output)` — `output_processing.py`
**Output:** Cleaned solver output (same schema).  
**Steps:** Strip whitespace from all string columns. Strip parenthetical suffixes from crew code columns.

---

### `Schedule_output_processing_2(Schedule_output)` — `output_processing.py`
**Output:** `Schedule_output_2` — exploded per-crew-per-sector with block hours and Group IDs.  
**Steps:**
1. Melt Captain/FO/FA → long format.
2. Remove null or empty crew codes.
3. Parse STD and STA as datetime.
4. Compute `Block hours = (STA − STD).total_seconds() × 1.35 / 3600`.
5. Sort by `(Crew code, STD)`.
6. Compute `Group id`:
   ```python
   (df[['Crew code','Aircraft No.']] != df[['Crew code','Aircraft No.']].shift()).any(axis=1).cumsum()
   ```
   Group id increments every time either the crew code OR the aircraft changes from the previous row.

---

### `output_master_processing(Schedule_output_2)` — `output_processing.py`
**Output:** `(output_master, output_crew_stats)`.  
**Steps:**
1. `first_sector` = for each crew, the row with the minimum STD (earliest departure).
2. `last_sector` = for each crew, the row with the maximum STA (latest arrival).
3. `output_crew_stats` = grouped by `Crew code`: count unique flights, unique aircraft, total sector rows, sum block hours, count unique Group ids minus 1 (= swaps).
4. Merge first_sector, last_sector, and output_crew_stats into `output_master`.
5. `Duty hours = (last STA − first STD) in hours + 1.5`.
6. Set `Working Status = 1` for all rows.

---

### `crew_ac_stats_processing(Schedule_output_2, aircraft, crew_aircraft)` — `output_processing.py`
**Output:** `crew_ac_stats` — one row per contiguous crew-aircraft assignment block.  
**Steps:**
1. For each `Group id`, find the row with minimum STD and maximum STA.
2. Merge those two to get start/end times per group block.
3. Merge with `aircraft` to get `Aircraft Type` from `Aircraft Code`.
4. Look up qualification: `crew_aircraft.loc[crew_aircraft['Crew code'] == x['Crew code'], x['Aircraft Type']]`.

---

### `overnight_flights(df)` — `output_processing.py`
**Output:** Subset of `Schedule_output` showing only first and last sector per aircraft, with `ON` flag.  
**Steps:**
1. For each `Aircraft No.`, find the first and last sector by STD.
2. Mark each row as `"Starting"` or `"Ending"`.
3. `ON = 1` if the aircraft starts away from MLE (Starting sector dep airport ≠ MLE) or ends away from MLE (Ending sector arr airport ≠ MLE).  
**Used for KPIs:** `aircraft_starting_on_kpi` and `aircraft_ending_on_kpi`.

---

### `cluster_fun(data)` — `clustering.py`
**Inputs:** `crew_groups` DataFrame (validation_report_1 merged with crew_aircraft).  
**Output:** `df_grouped` — input DataFrame with added `Group_ID` and `group_key` columns.  
**Steps:**
1. Drops non-clustering columns: `['Crew Name', 'Starting from', 'Ending at', 'Total flights', 'Total aircrafts', 'Total duty hours', 'Total sectors', 'Block hours', 'No. of swaps', 'Expiry status']`.
2. Applies categorical bucketing:
   - Day status codes → `"Working"` / `"Flight training"` / `"Not Available"` (via `day_status()`).
   - BH/DH/sectors → FTL buckets (via `FTL()`): `"0-4"`, `"4-6"`, `"6-8"`, `"8-10"`, `"10-12"`, `"12-14"`, `"Greater than 14"`.
   - `Max more than 12 sectors` → `"Possible"` / `"Not possible"`.
3. Uses `CrewGrouping.create_groups()` for exact matching: concatenates all non-ID column values into a `group_key` string, assigns `Group_ID` (e.g., `"Group_1"`).
4. ⚠️ Side effect: saves `crew_groups.to_excel("Sample clustering.xlsx")` before clustering.

---

### `generate_html_report(...)` — `html_report_generator.py`
**Inputs:** ~40 parameters — all violation DataFrames, all KPI values, and the four crew validation subsets.  
**Output:** A complete HTML string (self-contained, no external dependencies except CDN-loaded Chart.js).  
**Structure:**
1. Header with date and generation timestamp.
2. Summary grid of 8 coloured metric cards.
3. KPI accordion (available crew, scheduled crew, utilisation).
4. Detailed metrics table (the 24-row `metrics_df`).
5. One accordion per violation category (schedule, status, overnight, aircraft, BH, DH, sectors, swaps, pairings).
6. Crew performance accordion with Chart.js bar charts (top 300 crew by block hours and sectors).
7. Swap distribution accordion with Chart.js pie charts.
8. Footer with generation info.
9. JavaScript for accordion toggle and expand/collapse all.

---

## Business Rules

1. **Home base is MLE.** All airport comparisons that determine "outstation" use `"MLE"` as the reference home airport.

2. **Block hours are inflated by 1.35×.** The raw flight time (STA - STD) is multiplied by 1.35 to compute block hours. This is a standard airline practice to account for taxi and buffer time.

3. **Prev Day status drives outstation inference.** If a crew member was NOT on an available status yesterday (i.e., they were on leave or training), and there is no logsheet record for them, they are assumed to be at MLE. This is because leave/training crew generally remain at base.

4. **Training crew have two sub-rules:**
   - At base → cannot fly at all.
   - At outstation → must fly exactly one sector (to return home). No more, no less.

5. **Outstation overnight is only allowed if crew works tomorrow.** If a crew member's last sector ends at a non-MLE airport and their next-day status is a leave code, that's an error.

6. **Aircraft swap gap of 45 minutes.** This is the minimum ground time for a crew member to transition from one aircraft assignment to another.

7. **Swap count of 1 means one aircraft change in the day.** `No. of swaps = 0` means the crew stays on one aircraft all day. `No. of swaps = 1` means they switch once (allowed). More than 1 is flagged.

8. **Crew code parenthetical suffixes are stripped.** Codes like `AAFZ(C)` are normalised to `AAFZ` across all data sources before merging. The suffix appears to indicate crew type in the source systems but is redundant with the `Crew Type` column.

9. **Sector count uses "Total sectors" as row count, not unique flights.** A crew member who flies two legs of the same flight (e.g., a turnaround) counts as 2 sectors.

10. **Only "available" crew are checked for limit violations.** Crew on leave or training are excluded from the block hours / duty hours / sector limit checks. The reasoning is that their allocation is pre-defined and they shouldn't appear in the solver output anyway.

11. **Logsheet uses the latest-arrival-time record per crew.** If a crew member has multiple flights logged on the previous day, only their latest arrival (by `Actual Time of Arrival`) is used to determine their outstation position.

12. **Date ranges for pre-loaded data are hardcoded** to September 2025 (2025-09-01 to 2025-09-08). For any other date the user must upload all files manually.

---

## Checklist Generation

The "checklist" in this application is implicit — it manifests as the 8 summary KPI cards plus 13+ expandable sections on the Constraints Validator page. There is no explicit checklist data structure.

**What determines if a checklist item is checked (green):**
- The corresponding violation DataFrame has length 0.
- `if df.empty: show green box`.

**What determines if a checklist item is unchecked/flagged (red):**
- The corresponding violation DataFrame has length > 0.
- The violation count is shown in a red KPI card.
- The full DataFrame is shown inside the expander.

**Checklist items in order of display:**
1. Standby crew (informational, not a violation)
2. ✈️ Unassigned Flights (Rule C-2)
3. 📋 Schedule Check (Rule C-1)
4. ⚠️ Non-Available Crew Check (Rule C-3)
5. 🎓 Training crew errors — base (Rule C-4) + outstation (Rule C-5)
6. 📍 Starting Point Errors (Rule C-6)
7. 🌙 Next-day Overnight Errors (Rule C-7)
8. ✈️ Aircraft Eligibility Errors (Rule C-8)
9. ⏰ Block Hour Violations — MLE (Rule C-9) + outstation (Rule C-10)
10. 📅 Monthly Duty Hour Violations (Rule C-11)
11. 🔢 Sector Violations — daily (Rule C-14) + weekly (Rule C-12) + >12 rule (Rule C-13)
12. 🔄 Aircraft Swap Violations — count (Rule C-15) + time gap (Rule C-16)
13. 👥 Pairing Violations — seniority (Rule C-17) + LTC (Rule C-18) + training (Rule C-19)

---

## Edge Cases & Assumptions

### Handled edge cases

| Situation | How handled |
|---|---|
| Crew not in logsheet | `Outstation airport` becomes `""`, then inferred as `"MLE"` if Prev Day not available |
| Crew not in seniority file | `Seniority Level = ""`, `Is Instructor? = ""`; these crew will fail pairing checks (level appears as empty string in the pairing composite, not matching any valid pairing) |
| Crew in solver output but not in month plan | Appear in `comparison_master` with NaN month plan fields |
| Crew in month plan but not in solver output | Appear in `comparison_master` with NaN output fields; become part of `Standby_crew` if available |
| STD/STA in `HH:MM:SS` string format | `pd.to_datetime(x, format='%H:%M:%S')` in `Schedule_output_processing_2` |
| Block hours spanning midnight | Not explicitly handled; the formula `STA - STD` would give a negative value if STA < STD (overnight flights). The codebase does not appear to handle overnight sectors. ⚠️ |
| Files with parenthetical crew codes | `.str.replace(r'\s*\(.*?\)', '', regex=True)` normalises across all input sources |
| Duplicate crew in logsheet | Resolved by `idxmax()` on arrival time — latest arrival is kept |
| Month plan column headers as datetime objects | `str(col).split()[0]` converts `2025-09-08 00:00:00` to `2025-09-08` |
| Empty crew code in Resources.xlsx | `dropna(subset=["Crew code"])` in `crew_master_processing` |
| Solver output where crew is an empty string | `Schedule_output_processing_2` filters `Crew code != ''` |

### Unhandled edge cases / gaps

| Gap | Risk |
|---|---|
| Overnight flights (STA < STD) | Block hours would compute as negative; duty hours may be wrong |
| Crew appearing in the schedule under multiple crew types | `output_master` uses `drop_duplicates()` on `(Crew code, Crew Type)`, which keeps only the first type seen |
| `Max more than 12 sectors` formula bug | Silently allows more than 2 occurrences of >12 sectors per day in some configurations |
| Crew code mismatch between sources | If a crew code appears with different capitalisation or spacing in different files, merges will produce NaN fields without any error message |
| Training pairings for dates outside the schedule date | `flight_training_processing` filters to `Date == schedule_date`; if training is planned but has wrong date format, it is silently dropped |
| Aircraft type lookup for aircraft not in `aircraft` table | `crew_ac_stats_processing` would raise a KeyError on the `.merge()` if an aircraft code in the output is not in the Aircrafts file |
| Crew scheduled on a flight with `Dep. Airport == Arr. Airport` | Filtered out in `schedule_input_processing` for input, but NOT filtered in `Schedule_output_processing`. A solver output could contain zero-distance legs that would be counted as sectors. |
| Standby crew counted by `Crew Type_x` (month plan type) | If `Crew Type_x` column name depends on merge suffix and the column is missing (e.g., crew not in `merged_df`), this would raise a KeyError |
| Multi-file upload file identification | If two uploaded files match the same keyword, the second silently overwrites the first in `st.session_state.uploaded_data` |
| `Schedule_input` not uploaded in Constraints Validator | If no flight plan file is uploaded, `Schedule_input` is `None` and `Schedule_input_processing(None)` will raise an `AttributeError` |
