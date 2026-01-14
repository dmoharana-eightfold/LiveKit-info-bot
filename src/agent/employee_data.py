"""
Employee Data Module

Handles loading and accessing employee data from JSON file.
Only provides raw data access - fuzzy matching is handled by fuzzy_search.py
"""

import json
import os
import logging
from dataclasses import dataclass
from typing import TypedDict

logger = logging.getLogger("agent.employee_data")


class EmployeeRecord(TypedDict):
    """Full employee record from the database."""
    name: str
    email: str
    role: str
    department: str
    salary: int  # Confidential - never expose


@dataclass
class EmployeeData:
    """Container for employee records loaded from JSON."""
    
    _employees: list[EmployeeRecord]
    
    @classmethod
    def load_from_file(cls, file_path: str) -> "EmployeeData":
        """Load employee data from a JSON file."""
        with open(file_path, "r") as f:
            data = json.load(f)
        logger.info(f"Loaded {len(data)} employees from {file_path}")
        return cls(_employees=data)
    
    @classmethod
    def load_default(cls) -> "EmployeeData":
        """Load employee data from the default location (src/mock_data.json)."""
        module_dir = os.path.dirname(os.path.dirname(__file__))
        default_path = os.path.join(module_dir, "mock_data.json")
        return cls.load_from_file(default_path)
    
    @property
    def employees(self) -> list[EmployeeRecord]:
        """Get all employee records (used by FuzzyNameMatcher)."""
        return self._employees
    
    def get_names(self) -> list[str]:
        """Get all employee names (used by Assistant for context)."""
        return [emp["name"] for emp in self._employees]


# Global instance - lazy loaded
_employee_data: EmployeeData | None = None


def get_employee_data() -> EmployeeData:
    """Get the global employee data instance (lazy loaded)."""
    global _employee_data
    if _employee_data is None:
        _employee_data = EmployeeData.load_default()
    return _employee_data
