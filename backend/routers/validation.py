"""
routers/validation.py — Endpoints that trigger crew schedule validation.

POST /api/validate/inputs — input completeness check only (Rules I-1 / I-2)
POST /api/validate        — full 19-rule constraints validation with GitHub storage
"""

import json
import logging
import os
import uuid
from datetime import datetime, timezone
from typing import Optional

from fastapi import APIRouter, File, Form, HTTPException, UploadFile

from config import FILE_IDENTIFIERS
from models.run_metadata import RunMetadata, RunSummary, ViolationCounts
from services.github_service import GitHubService
from services.report_service import build_excel, build_html
from services.validation_service import (
    _identify_file,
    run_full_validation,
    run_input_validation,
)

logger = logging.getLogger(__name__)
router = APIRouter(prefix="/validate", tags=["validation"])


def _get_gh() -> GitHubService:
    return GitHubService()


# ---------------------------------------------------------------------------
# Input validation only
# ---------------------------------------------------------------------------

@router.post("/inputs", summary="Run input completeness checks (Rules I-1 and I-2)")
async def validate_inputs(
    date:  str                   = Form(..., description="Schedule date YYYY-MM-DD"),
    files: list[UploadFile]      = File(default=[], description="Up to 9 input Excel files"),
):
    """
    Identify each uploaded file by filename keyword, run the two input
    validation rules, and return the violation lists.

    Returns:
        {
            "validation_1": [...],   # Rule I-1: missing resource fields
            "validation_2": [...],   # Rule I-2: zero stat values
            "clean": bool,
        }
    """
    file_bytes: dict[str, bytes] = {}
    for f in files:
        content = await f.read()
        ftype = _identify_file(f.filename or "")
        if ftype:
            file_bytes[ftype] = content
        else:
            logger.warning("validate/inputs: unrecognised file '%s' — skipped", f.filename)

    required = {"aircraft", "crew_aircraft", "seniority", "logsheet",
                "crew_master", "expiry_data", "flight_training", "month_plan", "crew_stats"}
    missing = required - file_bytes.keys()
    if missing:
        raise HTTPException(
            status_code=422,
            detail=f"Missing required files: {', '.join(sorted(missing))}",
        )

    try:
        result = run_input_validation(file_bytes, date)
    except Exception as exc:
        logger.exception("Input validation error for %s", date)
        raise HTTPException(status_code=500, detail=str(exc)) from exc

    return result


# ---------------------------------------------------------------------------
# Full constraints validation
# ---------------------------------------------------------------------------

@router.post("", summary="Run full 19-rule constraints validation")
async def validate_constraints(
    date:               str              = Form(..., description="Schedule date YYYY-MM-DD"),
    vendor_id:          str              = Form(..., description="Vendor ID from /api/vendors"),
    use_github_inputs:  bool             = Form(False, description="Load input files from GitHub instead of uploading"),
    files:              list[UploadFile] = File(default=[], description="Input files + solver output"),
):
    """
    Full pipeline:
    1. Identify uploaded files by filename keyword.
    2. Optionally supplement with files already stored in GitHub.
    3. Look up the vendor column map.
    4. Run all 19 validation checks.
    5. Generate Excel + HTML reports.
    6. Save artifacts to GitHub under outputs/{date}/{vendor_name}/{run_id}/.
    7. Append run summary to outputs/index.json.
    8. Return JSON result (violation lists, KPI counts, run_id).
    """
    gh = _get_gh()

    # ------------------------------------------------------------------
    # 1. Resolve vendor
    # ------------------------------------------------------------------
    vendors_data = gh.get_vendors()
    vendor = next(
        (v for v in vendors_data.get("vendors", []) if v.get("id") == vendor_id),
        None,
    )
    if vendor is None:
        raise HTTPException(status_code=404, detail=f"Vendor '{vendor_id}' not found")

    column_map: dict = vendor.get("solver_output_columns", {})
    vendor_name: str = vendor["name"]

    # ------------------------------------------------------------------
    # 2. Collect file bytes from uploads
    # ------------------------------------------------------------------
    file_bytes: dict[str, bytes] = {}

    for f in files:
        content = await f.read()
        ftype = _identify_file(f.filename or "")
        if ftype:
            file_bytes[ftype] = content
        elif (f.filename or "").lower().endswith((".xlsx", ".xls")):
            # Treat unrecognised files as potential solver output if not yet set
            if "solver_output" not in file_bytes:
                file_bytes["solver_output"] = content
                logger.info("Treating '%s' as solver_output", f.filename)

    # ------------------------------------------------------------------
    # 3. Optionally load missing input files from GitHub
    # ------------------------------------------------------------------
    if use_github_inputs:
        github_paths = gh.list_files(f"outputs/{date}/inputs")
        for path in github_paths:
            filename = os.path.basename(path)
            ftype = _identify_file(filename)
            if ftype and ftype not in file_bytes:
                try:
                    file_bytes[ftype] = gh.read_file(path)
                    logger.info("Loaded '%s' from GitHub (%s)", ftype, path)
                except Exception:
                    logger.warning("Could not read GitHub file '%s'", path)

    # ------------------------------------------------------------------
    # 4. Validate required files are present
    # ------------------------------------------------------------------
    required_inputs = {
        "aircraft", "crew_aircraft", "seniority", "logsheet", "crew_master",
        "expiry_data", "flight_training", "month_plan", "crew_stats",
        "input_flight_plan",
    }
    missing_inputs = required_inputs - file_bytes.keys()
    if missing_inputs:
        raise HTTPException(
            status_code=422,
            detail=f"Missing required input files: {', '.join(sorted(missing_inputs))}",
        )
    if "solver_output" not in file_bytes:
        raise HTTPException(status_code=422, detail="Missing solver output file")

    # ------------------------------------------------------------------
    # 5. Run validation
    # ------------------------------------------------------------------
    run_id = str(uuid.uuid4())[:12]
    timestamp = datetime.now(timezone.utc).isoformat()
    status = "complete"

    try:
        result = run_full_validation(file_bytes, date, column_map)
    except Exception as exc:
        logger.exception("Full validation error for %s / vendor %s", date, vendor_name)
        raise HTTPException(status_code=500, detail=str(exc)) from exc

    artifacts = result.pop("_artifacts")

    # ------------------------------------------------------------------
    # 6. Generate and store reports in GitHub
    # ------------------------------------------------------------------
    base_path = f"outputs/{date}/{vendor_name}/{run_id}"

    try:
        # Solver output
        if "solver_output" in file_bytes:
            gh.write_file(
                f"{base_path}/solver_output.xlsx",
                file_bytes["solver_output"],
                f"run {run_id}: solver output for {date}",
            )

        # Excel report
        excel_bytes = build_excel(artifacts)
        gh.write_file(
            f"{base_path}/validation_report.xlsx",
            excel_bytes,
            f"run {run_id}: Excel report for {date}",
        )

        # HTML report
        html_string = build_html(artifacts)
        gh.write_file(
            f"{base_path}/validation_report.html",
            html_string.encode("utf-8"),
            f"run {run_id}: HTML report for {date}",
        )

    except Exception as exc:
        logger.exception("Failed to save artifacts for run %s", run_id)
        status = "failed"
        # Continue to save metadata even on partial failure

    # ------------------------------------------------------------------
    # 7. Build and store run metadata
    # ------------------------------------------------------------------
    violation_counts = ViolationCounts(**result["violation_counts"])
    run_metadata = RunMetadata(
        run_id=run_id,
        date=date,
        vendor=vendor_name,
        timestamp=timestamp,
        triggered_by="api",
        status=status,
        violation_counts=violation_counts,
        total_violations=result["total_violations"],
        available_crew=result["available_crew"]["total"],
        scheduled_crew=result["scheduled_crew"]["total"],
    )
    gh.write_json(
        f"{base_path}/run_metadata.json",
        run_metadata.model_dump(),
        f"run {run_id}: metadata for {date}",
    )

    # ------------------------------------------------------------------
    # 8. Update the global run index
    # ------------------------------------------------------------------
    run_summary = RunSummary(
        run_id=run_id,
        date=date,
        vendor=vendor_name,
        timestamp=timestamp,
        status=status,
        total_violations=result["total_violations"],
    )
    try:
        gh.append_run_to_index(run_summary.model_dump())
    except Exception:
        logger.warning("Could not update index.json for run %s", run_id)

    # ------------------------------------------------------------------
    # 9. Return response (no binary blobs)
    # ------------------------------------------------------------------
    return {
        "run_id":          run_id,
        "date":            date,
        "vendor":          vendor_name,
        "timestamp":       timestamp,
        "status":          status,
        **result,
    }
