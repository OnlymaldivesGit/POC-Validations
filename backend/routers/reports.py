"""
routers/reports.py — Read-only endpoints for accessing historical run reports.

All run artifacts are fetched from the GitHub outputs branch via GitHubService.
The index.json file is used for fast listing/filtering without having to walk
the entire directory tree.
"""

from typing import Optional

from fastapi import APIRouter, HTTPException, Query
from fastapi.responses import Response

from services.github_service import GitHubService

router = APIRouter(prefix="/reports", tags=["reports"])


def _get_gh() -> GitHubService:
    return GitHubService()


@router.get("", summary="List historical validation runs")
def list_reports(
    date_from:  Optional[str] = Query(None, description="ISO date lower bound (inclusive)"),
    date_to:    Optional[str] = Query(None, description="ISO date upper bound (inclusive)"),
    vendor:     Optional[str] = Query(None, description="Vendor name filter (case-insensitive)"),
    status:     Optional[str] = Query(None, description="'complete' or 'failed'"),
    page:       int           = Query(1,  ge=1,  description="Page number"),
    per_page:   int           = Query(20, ge=1, le=200, description="Items per page"),
):
    """
    Return a paginated, filtered list of run summaries from outputs/index.json.
    Filtering is applied server-side after loading the full index.
    """
    gh = _get_gh()
    runs: list[dict] = gh.get_run_index()

    # Apply filters
    if date_from:
        runs = [r for r in runs if r.get("date", "") >= date_from]
    if date_to:
        runs = [r for r in runs if r.get("date", "") <= date_to]
    if vendor:
        runs = [r for r in runs if r.get("vendor", "").lower() == vendor.lower()]
    if status:
        runs = [r for r in runs if r.get("status", "") == status]

    # Sort newest first by timestamp
    runs.sort(key=lambda r: r.get("timestamp", ""), reverse=True)

    total = len(runs)
    start = (page - 1) * per_page
    page_runs = runs[start: start + per_page]

    return {
        "total":    total,
        "page":     page,
        "per_page": per_page,
        "runs":     page_runs,
    }


@router.get("/{run_id}", summary="Get full run metadata")
def get_report(run_id: str):
    """
    Return the full RunMetadata JSON for a specific run.  The index is
    consulted first to find the date/vendor path; then the per-run
    run_metadata.json is fetched from GitHub.
    """
    gh = _get_gh()
    runs = gh.get_run_index()
    info = next((r for r in runs if r.get("run_id") == run_id), None)
    if not info:
        raise HTTPException(status_code=404, detail=f"Run '{run_id}' not found in index")

    path = f"outputs/{info['date']}/{info['vendor']}/{run_id}/run_metadata.json"
    data = gh.read_json(path)
    if not data:
        raise HTTPException(status_code=404, detail="run_metadata.json not found in GitHub")
    return data


@router.get("/{run_id}/excel", summary="Stream Excel validation report")
def get_report_excel(run_id: str):
    """
    Return the .xlsx validation report for a run as a binary download.
    """
    gh = _get_gh()
    runs = gh.get_run_index()
    info = next((r for r in runs if r.get("run_id") == run_id), None)
    if not info:
        raise HTTPException(status_code=404, detail=f"Run '{run_id}' not found")

    path = f"outputs/{info['date']}/{info['vendor']}/{run_id}/validation_report.xlsx"
    try:
        content = gh.read_file(path)
    except Exception:
        raise HTTPException(status_code=404, detail="Excel report not found in GitHub")

    return Response(
        content=content,
        media_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
        headers={
            "Content-Disposition": f'attachment; filename="validation_report_{run_id}.xlsx"'
        },
    )


@router.get("/{run_id}/html", summary="Return HTML validation report")
def get_report_html(run_id: str):
    """
    Return the self-contained HTML validation report for a run.
    """
    gh = _get_gh()
    runs = gh.get_run_index()
    info = next((r for r in runs if r.get("run_id") == run_id), None)
    if not info:
        raise HTTPException(status_code=404, detail=f"Run '{run_id}' not found")

    path = f"outputs/{info['date']}/{info['vendor']}/{run_id}/validation_report.html"
    try:
        content = gh.read_file(path)
    except Exception:
        raise HTTPException(status_code=404, detail="HTML report not found in GitHub")

    return Response(content=content, media_type="text/html")
