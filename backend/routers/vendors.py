"""
routers/vendors.py — CRUD endpoints for solver vendor configuration.

Vendors are stored as a JSON file in the GitHub outputs branch so the
registry is version-controlled and survives redeployments.
"""

import uuid
from datetime import datetime, timezone

from fastapi import APIRouter, HTTPException

from models.vendor import Vendor, VendorCreate, VendorsFile
from services.github_service import GitHubService

router = APIRouter(prefix="/vendors", tags=["vendors"])


def _get_gh() -> GitHubService:
    return GitHubService()


@router.get("", response_model=list[Vendor], summary="List all vendors")
def list_vendors():
    """Return every vendor registered in the GitHub vendors.json."""
    data = _get_gh().get_vendors()
    return data.get("vendors", [])


@router.post("", response_model=Vendor, status_code=201, summary="Register a new vendor")
def create_vendor(body: VendorCreate):
    """
    Add a new solver vendor.  A UUID is generated server-side; the record
    is appended to the GitHub vendors.json.
    """
    gh = _get_gh()
    data = gh.get_vendors()
    vendors: list[dict] = data.get("vendors", [])

    new_vendor = Vendor(
        id=str(uuid.uuid4()),
        name=body.name,
        active=body.active,
        solver_output_columns=body.solver_output_columns,
        created_at=datetime.now(timezone.utc).isoformat(),
    )
    vendors.append(new_vendor.model_dump())
    gh.save_vendors({"vendors": vendors})
    return new_vendor


@router.put("/{vendor_id}", response_model=Vendor, summary="Update a vendor")
def update_vendor(vendor_id: str, body: VendorCreate):
    """
    Replace the mutable fields of an existing vendor.  The created_at and id
    fields are preserved; raises 404 if the vendor_id is unknown.
    """
    gh = _get_gh()
    data = gh.get_vendors()
    vendors: list[dict] = data.get("vendors", [])

    for i, v in enumerate(vendors):
        if v.get("id") == vendor_id:
            updated = Vendor(
                id=vendor_id,
                name=body.name,
                active=body.active,
                solver_output_columns=body.solver_output_columns,
                created_at=v.get("created_at", datetime.now(timezone.utc).isoformat()),
            )
            vendors[i] = updated.model_dump()
            gh.save_vendors({"vendors": vendors})
            return updated

    raise HTTPException(status_code=404, detail=f"Vendor '{vendor_id}' not found")


@router.delete("/{vendor_id}", status_code=204, summary="Remove a vendor")
def delete_vendor(vendor_id: str):
    """
    Permanently remove a vendor from the registry.  Raises 404 if the
    vendor_id is unknown.
    """
    gh = _get_gh()
    data = gh.get_vendors()
    vendors: list[dict] = data.get("vendors", [])

    before = len(vendors)
    vendors = [v for v in vendors if v.get("id") != vendor_id]
    if len(vendors) == before:
        raise HTTPException(status_code=404, detail=f"Vendor '{vendor_id}' not found")

    gh.save_vendors({"vendors": vendors})
