"""Seed/demo data loader for the mock integrations.

These are POC stand-ins. In a real deployment they would be replaced by
AD / Azure Graph / ServiceNow / Nexthink API calls.
"""
from __future__ import annotations

import json
from functools import lru_cache
from pathlib import Path

from ..config import get_settings

DATA_DIR = Path(__file__).resolve().parent.parent / "data"


@lru_cache
def load_employees() -> list[dict]:
    path = Path(get_settings().seed_data_dir) / "employees.json"
    if not path.exists():
        path = DATA_DIR / "employees.json"
    return json.loads(path.read_text(encoding="utf-8"))


@lru_cache
def load_bitlocker_keys() -> list[dict]:
    path = Path(get_settings().seed_data_dir) / "bitlocker_keys.json"
    if not path.exists():
        path = DATA_DIR / "bitlocker_keys.json"
    return json.loads(path.read_text(encoding="utf-8"))


def find_employee(employee_code: str) -> dict | None:
    code = employee_code.strip().upper()
    for emp in load_employees():
        if emp["employee_code"].upper() == code:
            return emp
    return None


def find_device_by_name(device_name: str) -> dict | None:
    name = device_name.strip().lower()
    for dev in load_bitlocker_keys():
        if dev["device_name"].lower() == name:
            return dev
    return None


def find_device_by_employee(employee_code: str) -> dict | None:
    code = employee_code.strip().upper()
    for dev in load_bitlocker_keys():
        if dev["employee_code"].upper() == code:
            return dev
    return None
