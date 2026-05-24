"""
models/vendor.py — Pydantic v2 models for solver vendor configuration.
"""

from pydantic import BaseModel


class SolverColumnMap(BaseModel):
    """Maps canonical TMA column roles to the actual header strings in a vendor file."""
    date: str = "Date"
    flight_no: str = "Flight No."
    aircraft_no: str = "Aircraft No."
    std: str = "STD -  Scheduled Departure"
    sta: str = "STA -  Scheduled Arrival"
    dep_airport: str = "Dep. Airport"
    arr_airport: str = "Arr. Airport"
    captain: str = "Captain"
    first_officer: str = "First Officer"
    flight_attendant: str = "Flight Attendant"


class Vendor(BaseModel):
    id: str
    name: str
    active: bool
    solver_output_columns: SolverColumnMap
    created_at: str


class VendorCreate(BaseModel):
    name: str
    solver_output_columns: SolverColumnMap = SolverColumnMap()
    active: bool = True


class VendorsFile(BaseModel):
    vendors: list[Vendor] = []
