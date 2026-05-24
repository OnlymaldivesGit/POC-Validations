"""
rules.py — Validation rule registry for TMA Crew Scheduler.

Every validation rule enforced by the application is described here as a
structured metadata object.  The registry is the *authoritative* list of
rules; it does NOT contain the implementation (which lives in
validation/checklist.py and validation/input_validations.py).

Usage:
    from rules import RULE_REGISTRY, ValidationRule
    for rule in RULE_REGISTRY:
        print(rule.rule_id, rule.name, rule.severity)

    # Look up a specific rule:
    rule = next(r for r in RULE_REGISTRY if r.rule_id == "C-9")

KPI bucket values map directly to the 8 UI summary cards rendered in
pages/page_constraints.py:
    "Schedule" | "Status" | "Overnight" | "Aircraft"
    | "BlockHours" | "DutyHours" | "Sectors" | "Pairing"

Input-only rules ("Input" category) appear only on the Input Data Validator
page and do not contribute to any Constraints Validator KPI bucket.
"""

from __future__ import annotations
from dataclasses import dataclass, field


@dataclass(frozen=True)
class ValidationRule:
    """Immutable descriptor for a single validation rule."""

    rule_id: str
    # Canonical identifier used in LOGIC.md and CLAUDE.md (e.g. "C-1", "I-2").

    name: str
    # Short human-readable label shown in UI expanders and reports.

    category: str
    # Logical grouping. One of:
    # "Schedule", "Status", "Overnight", "Aircraft",
    # "BlockHours", "DutyHours", "Sectors", "Pairing", "Input"

    description: str
    # One sentence: exactly what condition this rule detects as a violation.

    kpi_bucket: str
    # Which of the 8 Constraints Validator summary cards this rule contributes
    # its violation count to. Use "N/A" for Input Validator rules.

    severity: str
    # "error"   — regulatory / safety rule; must be zero violations before publish.
    # "warning" — airline business rule; violations require planner review.

    known_bug: bool
    # True if CLAUDE.md documents a coding defect that may cause this rule to
    # produce incorrect results (false positives or false negatives).

    bug_description: str = field(default="")
    # Verbatim summary of the documented bug.  Empty string if known_bug=False.


# ---------------------------------------------------------------------------
# Input Validator rules  (prefix: I-)
# ---------------------------------------------------------------------------

_INPUT_RULES: list[ValidationRule] = [
    ValidationRule(
        rule_id="I-1",
        name="Missing Resource Data",
        category="Input",
        description=(
            "Flags any non-leave crew member who has an empty string in one or more "
            "of the required identity/position fields (Crew code, Prev Day, "
            "Schedule Day, Next Day, Crew name, Crew Type, Seniority Level, "
            "Is Instructor?, Outstation airport)."
        ),
        kpi_bucket="N/A",
        severity="error",
        known_bug=False,
    ),
    ValidationRule(
        rule_id="I-2",
        name="Missing Statistics",
        category="Input",
        description=(
            "Flags any non-leave crew member who has a zero value in any of the "
            "four FTL stat columns: Max BH left, Max BH left ON, Max DH left, "
            "Max sectors left — indicating the Crew Stats file did not supply data."
        ),
        kpi_bucket="N/A",
        severity="error",
        known_bug=False,
    ),
]

# ---------------------------------------------------------------------------
# Constraints Validator rules  (prefix: C-)
# ---------------------------------------------------------------------------

_CONSTRAINT_RULES: list[ValidationRule] = [
    ValidationRule(
        rule_id="C-1",
        name="Schedule Consistency",
        category="Schedule",
        description=(
            "Detects any sector present in the solver output but missing from "
            "the flight plan input, or present in the input but absent from the "
            "output — indicating the solver added or dropped planned flights."
        ),
        kpi_bucket="Schedule",
        severity="error",
        known_bug=False,
    ),
    ValidationRule(
        rule_id="C-2",
        name="Unassigned Flights",
        category="Schedule",
        description=(
            "Flags any flight in the solver output where the Captain, First Officer, "
            "or Flight Attendant position is null or empty — meaning the solver left "
            "a crew seat unfilled."
        ),
        kpi_bucket="Schedule",
        severity="error",
        known_bug=False,
    ),
    ValidationRule(
        rule_id="C-3",
        name="Leave Crew Scheduled",
        category="Status",
        description=(
            "Flags crew members whose monthly-plan Schedule Day code is a leave "
            "status (X, AL, AU, PAL, EM, ML, M) but who nonetheless appear in the "
            "solver output as assigned to flights."
        ),
        kpi_bucket="Status",
        severity="error",
        known_bug=False,
    ),
    ValidationRule(
        rule_id="C-4",
        name="Training Crew at Base Scheduled",
        category="Status",
        description=(
            "Flags crew members on a training schedule code who are positioned at "
            "the home base (MLE or no outstation logged) but have been assigned to "
            "flights — training crew at base must not fly."
        ),
        kpi_bucket="Status",
        severity="error",
        known_bug=True,
        bug_description=(
            "on_training_working is built by filtering the 'on_training' subset using "
            "a boolean mask from the full comparison_master DataFrame. Pandas aligns "
            "on index, but if comparison_master was not reset-indexed the mask can "
            "silently drop rows. See CLAUDE.md: 'Index alignment risk in crew_check_fun'."
        ),
    ),
    ValidationRule(
        rule_id="C-5",
        name="Training Crew at Outstation — Wrong Flight Count",
        category="Status",
        description=(
            "Flags training-coded crew members who are positioned at an outstation "
            "but have been assigned to anything other than exactly one flight — they "
            "are permitted one sector to return to base, no more and no less."
        ),
        kpi_bucket="Status",
        severity="error",
        known_bug=True,
        bug_description=(
            "crew_mistake_11 filters from on_training (all training crew at outstations) "
            "rather than on_training_working. Crew not in the schedule at all have "
            "Total flights = NaN, and NaN != 1 evaluates True, so they are incorrectly "
            "flagged. See CLAUDE.md: 'crew_mistake_11 catches non-working crew'."
        ),
    ),
    ValidationRule(
        rule_id="C-6",
        name="Starting Position Mismatch",
        category="Overnight",
        description=(
            "Flags crew members whose first scheduled departure airport does not match "
            "the outstation airport recorded for them at the end of the previous day "
            "(from the logsheet or inferred as MLE)."
        ),
        kpi_bucket="Overnight",
        severity="error",
        known_bug=False,
    ),
    ValidationRule(
        rule_id="C-7",
        name="Overnight Assignment When Next Day is Leave",
        category="Overnight",
        description=(
            "Flags crew members who end their last scheduled flight at a non-MLE "
            "airport while their next-day monthly-plan status is a leave code — "
            "meaning no return flight is planned for them."
        ),
        kpi_bucket="Overnight",
        severity="error",
        known_bug=False,
    ),
    ValidationRule(
        rule_id="C-8",
        name="Aircraft Qualification",
        category="Aircraft",
        description=(
            "Flags any crew member assigned to fly an aircraft type for which their "
            "Crew AC Matrix qualification value is not exactly 1.0 — they are either "
            "unqualified (0), missing from the matrix (NaN), or flagged Not Found."
        ),
        kpi_bucket="Aircraft",
        severity="error",
        known_bug=False,
    ),
    ValidationRule(
        rule_id="C-9",
        name="Block Hour Limit — Ending at MLE",
        category="BlockHours",
        description=(
            "Flags available crew whose today's scheduled block hours exceed their "
            "remaining 28-day or 365-day block hour capacity (100h / 1000h limits) "
            "when they are ending the day at the home base."
        ),
        kpi_bucket="BlockHours",
        severity="error",
        known_bug=False,
    ),
    ValidationRule(
        rule_id="C-10",
        name="Block Hour Limit — Ending at Outstation",
        category="BlockHours",
        description=(
            "Same as C-9 but using the tighter outstation limits (98h / 998h) for "
            "crew ending their day away from MLE, since those crew will consume "
            "additional block hours flying home tomorrow."
        ),
        kpi_bucket="BlockHours",
        severity="error",
        known_bug=False,
    ),
    ValidationRule(
        rule_id="C-11",
        name="Monthly Duty Hour Limit",
        category="DutyHours",
        description=(
            "Flags available crew whose today's duty hours (first STD to last STA "
            "plus 1.5h ground buffer) would cause them to exceed the 28-day duty "
            "time limit of 210 hours."
        ),
        kpi_bucket="DutyHours",
        severity="error",
        known_bug=False,
    ),
    ValidationRule(
        rule_id="C-12",
        name="Weekly Sector Limit",
        category="Sectors",
        description=(
            "Flags available crew whose today's scheduled sectors exceed their "
            "remaining 6-day rolling sector budget (48-sector limit across -1D "
            "through -6D plus today)."
        ),
        kpi_bucket="Sectors",
        severity="error",
        known_bug=False,
    ),
    ValidationRule(
        rule_id="C-13",
        name="Long-Day Sector Rule (>12 sectors)",
        category="Sectors",
        description=(
            "Flags available crew who are scheduled for more than 12 sectors today "
            "but have already used both allowed long-day slots in their -1D/-2D/-3D "
            "look-back window (Max more than 12 sectors == 0)."
        ),
        kpi_bucket="Sectors",
        severity="error",
        known_bug=True,
        bug_description=(
            "The 'More than 12' column is computed with a Python operator-precedence "
            "bug: '2 - A + B + C' instead of '2 - (A + B + C)'. Crew who flew >12 "
            "sectors on all three look-back days get a value of 3 instead of -1, "
            "so this rule never triggers for that edge case. See CLAUDE.md: "
            "'More than 12 formula bug'."
        ),
    ),
    ValidationRule(
        rule_id="C-14",
        name="Daily Sector Limit",
        category="Sectors",
        description=(
            "Flags any crew member — regardless of remaining weekly budget — who "
            "is scheduled for more than 14 sectors in a single day."
        ),
        kpi_bucket="Sectors",
        severity="error",
        known_bug=False,
    ),
    ValidationRule(
        rule_id="C-15",
        name="Aircraft Swap Count",
        category="Aircraft",
        description=(
            "Flags crew members who change aircraft more than once during their "
            "duty day — the maximum permitted number of aircraft swaps is 1."
        ),
        kpi_bucket="Aircraft",
        severity="warning",
        known_bug=False,
    ),
    ValidationRule(
        rule_id="C-16",
        name="Aircraft Swap Time Gap",
        category="Aircraft",
        description=(
            "Flags crew members who swap aircraft with fewer than 45 minutes between "
            "the end of their first aircraft assignment and the start of their second."
        ),
        kpi_bucket="Aircraft",
        severity="warning",
        known_bug=False,
    ),
    ValidationRule(
        rule_id="C-17",
        name="Crew Pairing Seniority",
        category="Pairing",
        description=(
            "Flags any flight where the combination of Captain / First Officer / "
            "Flight Attendant seniority levels does not match one of the five "
            "approved pairing patterns defined in VALID_SENIORITY_PAIRINGS."
        ),
        kpi_bucket="Pairing",
        severity="error",
        known_bug=False,
    ),
    ValidationRule(
        rule_id="C-18",
        name="LTC Requirement for Trainee Pairing",
        category="Pairing",
        description=(
            "Flags flights where the FO is a Trainee but the Captain does not hold "
            "an LTC/CCI (Line Training Captain / Chief Check Instructor) qualification "
            "— only certified instructors may supervise trainee first officers."
        ),
        kpi_bucket="Pairing",
        severity="error",
        known_bug=False,
    ),
    ValidationRule(
        rule_id="C-19",
        name="Training Pairing Accuracy",
        category="Pairing",
        description=(
            "Flags instructor-trainee pairs from the training schedule where the "
            "actual pairing in the solver output does not match the planned pairing "
            "(i.e., the instructor is paired with a different trainee, or vice versa)."
        ),
        kpi_bucket="Pairing",
        severity="error",
        known_bug=False,
    ),
]

# ---------------------------------------------------------------------------
# Combined registry
# ---------------------------------------------------------------------------

RULE_REGISTRY: list[ValidationRule] = _INPUT_RULES + _CONSTRAINT_RULES
"""
Complete list of all validation rules in rule_id order.
Iterate this list to build reports, dashboards, or summary tables without
hard-coding rule IDs anywhere else in the codebase.
"""


# ---------------------------------------------------------------------------
# Convenience helpers
# ---------------------------------------------------------------------------

def get_rule(rule_id: str) -> ValidationRule:
    """Return the ValidationRule with the given rule_id, or raise KeyError."""
    for rule in RULE_REGISTRY:
        if rule.rule_id == rule_id:
            return rule
    raise KeyError(f"Rule '{rule_id}' not found in RULE_REGISTRY.")


def rules_for_kpi_bucket(bucket: str) -> list[ValidationRule]:
    """Return all rules that roll up into the named KPI bucket."""
    return [r for r in RULE_REGISTRY if r.kpi_bucket == bucket]


def buggy_rules() -> list[ValidationRule]:
    """Return all rules that have a documented known_bug."""
    return [r for r in RULE_REGISTRY if r.known_bug]


KPI_BUCKETS = [
    "Schedule",
    "BlockHours",
    "DutyHours",
    "Sectors",
    "Pairing",
    "Status",
    "Overnight",
    "Aircraft",
]
"""Ordered list of KPI bucket names matching the 8 summary cards in the UI."""
