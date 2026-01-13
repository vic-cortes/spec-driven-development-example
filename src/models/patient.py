"""Patient model for the dental check-in system."""

import uuid
from dataclasses import dataclass
from datetime import date
from typing import Optional


@dataclass
class Patient:
    """Represents an individual patient receiving care."""

    id: str
    first_name: str
    last_name: str
    phone: str  # normalized (digits-only)
    email: Optional[str] = None
    birth_date: Optional[date] = None
    address: Optional[str] = None
    notes: Optional[str] = None

    def __post_init__(self):
        """Validate patient data after initialization."""
        if not self.first_name.strip():
            raise ValueError("First name is required")
        if not self.last_name.strip():
            raise ValueError("Last name is required")
        if not self.phone or len(self.phone) < 8:
            raise ValueError("Phone must be at least 8 digits")
        if not self.phone.isdigit():
            raise ValueError("Phone must contain only digits (normalized)")

    @classmethod
    def create_minimal(cls, first_name: str, last_name: str, phone: str) -> "Patient":
        """Create a minimal patient record with required fields only."""
        return cls(
            id=str(uuid.uuid4()),
            first_name=first_name.strip(),
            last_name=last_name.strip(),
            phone=phone,
        )

    @property
    def full_name(self) -> str:
        """Return the patient's full name."""
        return f"{self.first_name} {self.last_name}"

    @property
    def masked_phone(self) -> str:
        """Return phone with only last 4 digits visible."""
        if len(self.phone) <= 4:
            return "***" + self.phone
        return "***" + self.phone[-4:]
