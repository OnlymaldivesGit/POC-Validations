"""
routers/files.py — File listing and upload endpoints.

Input Excel files are stored under outputs/{date}/inputs/ in the GitHub
outputs branch so they can be reused across multiple validation runs without
re-uploading.
"""

import os

from fastapi import APIRouter, File, Form, HTTPException, UploadFile

from services.github_service import GitHubService

router = APIRouter(prefix="/files", tags=["files"])

# Must stay in sync with FILE_IDENTIFIERS in frontend/src/lib/utils.js
_FILE_IDENTIFIERS: dict[str, str] = {
    "aircrafts":                 "aircraft",
    "crew_aircraft_type_matrix": "crew_aircraft",
    "crew_pairing":              "seniority",
    "log_sheet":                 "logsheet",
    "crew_resource":             "crew_master",
    "crew_license_expiry":       "expiry_data",
    "training_pairings":         "flight_training",
    "monthly_plan":              "month_plan",
    "crewstats":                 "crew_stats",
    "flight_plan":               "input_flight_plan",
}


def _identify_file_type(filename: str) -> str | None:
    stem = filename.lower().rsplit(".", 1)[0].replace(" ", "_")
    # Canonical stored names (e.g. "aircraft.xlsx") match directly
    if stem in _FILE_IDENTIFIERS.values():
        return stem
    # Fallback: keyword substring match for legacy / custom filenames
    for keyword, var_name in _FILE_IDENTIFIERS.items():
        if keyword in stem:
            return var_name
    return None


def _get_gh() -> GitHubService:
    return GitHubService()


@router.get("/{date}", summary="List files stored in GitHub for a date")
def list_files_for_date(date: str):
    """
    Return all files in GitHub under outputs/{date}/, separated into:
      - inputs:  list of objects {fileType, filename, path} under outputs/{date}/inputs/
      - vendors: dict mapping vendor name → list of file paths
    """
    gh = _get_gh()
    all_files = gh.list_files(f"outputs/{date}")

    # Load manifest for original filenames (written at upload time)
    manifest: dict = gh.read_json(f"outputs/{date}/inputs/manifest.json")

    inputs: list[dict] = []
    vendor_files: dict[str, list[str]] = {}

    for path in all_files:
        rel = path.replace(f"outputs/{date}/", "", 1)
        parts = rel.split("/")

        if parts[0] == "inputs":
            stored_name = parts[-1]
            if stored_name == "manifest.json":
                continue  # skip the manifest itself
            file_type = _identify_file_type(stored_name)
            original_name = manifest.get(file_type, stored_name) if file_type else stored_name
            inputs.append({
                "fileType": file_type,
                "filename": original_name,
                "path": path,
            })
        elif len(parts) >= 2:
            vendor_name = parts[0]
            vendor_files.setdefault(vendor_name, []).append(path)

    return {"date": date, "inputs": inputs, "vendors": vendor_files}


@router.post("/upload", summary="Upload an input file to GitHub for a date")
async def upload_file(
    date: str = Form(..., description="Schedule date YYYY-MM-DD"),
    file_type: str = Form(..., description="Internal variable name, e.g. 'aircraft'"),
    file: UploadFile = File(...),
):
    """
    Upload an Excel input file to the GitHub outputs branch at:
      outputs/{date}/inputs/{filename}

    Returns the stored path and a confirmation message.
    """
    if file.filename is None:
        raise HTTPException(status_code=400, detail="Uploaded file has no filename")

    original_name = file.filename
    content = await file.read()
    # Store under canonical name so listing can identify type without pattern matching
    ext = original_name.rsplit(".", 1)[-1] if "." in original_name else "xlsx"
    canonical_name = f"{file_type}.{ext}"
    gh = _get_gh()
    path = f"outputs/{date}/inputs/{canonical_name}"
    gh.write_file(path, content, f"upload: {file_type} for {date} ({original_name})")

    # Update the manifest so the original filename is preserved for display
    manifest_path = f"outputs/{date}/inputs/manifest.json"
    manifest = gh.read_json(manifest_path)
    manifest[file_type] = original_name
    gh.write_json(manifest_path, manifest, f"manifest: record {file_type} → {original_name}")

    return {
        "path": path,
        "filename": original_name,
        "fileType": file_type,
        "message": f"{original_name} stored as '{file_type}' for {date}",
    }
