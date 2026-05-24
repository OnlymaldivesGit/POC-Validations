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


def _get_gh() -> GitHubService:
    return GitHubService()


@router.get("/{date}", summary="List files stored in GitHub for a date")
def list_files_for_date(date: str):
    """
    Return all files in GitHub under outputs/{date}/, separated into:
      - inputs:  list of paths under outputs/{date}/inputs/
      - vendors: dict mapping vendor name → list of file paths
    """
    gh = _get_gh()
    all_files = gh.list_files(f"outputs/{date}")

    inputs: list[str] = []
    vendor_files: dict[str, list[str]] = {}

    for path in all_files:
        # Strip the date prefix to get the relative path
        rel = path.replace(f"outputs/{date}/", "", 1)
        parts = rel.split("/")

        if parts[0] == "inputs":
            inputs.append(path)
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

    content = await file.read()
    gh = _get_gh()
    path = f"outputs/{date}/inputs/{file.filename}"
    gh.write_file(
        path,
        content,
        f"upload: {file_type} for {date} ({file.filename})",
    )
    return {"path": path, "message": f"{file.filename} stored as '{file_type}' for {date}"}
