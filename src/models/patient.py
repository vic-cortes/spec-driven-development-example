"""Patient model for the dental check-in system with international phone support."""

import uuid
from dataclasses import dataclass
from datetime import date
from typing import Optional

from src.services.phone_service import phone_service


@dataclass
class Patient:
    """Represents an individual patient receiving care with international phone support."""

    id: str
    first_name: str
    last_name: str
    phone: str  # normalized (digits-only, 10 digits)
    country_code: str = "+1"  # international country code ("+1" or "+52")
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

        # Enhanced phone validation for international support
        if not self.phone or len(self.phone) != 10:
            raise ValueError("Phone must be exactly 10 digits")
        if not self.phone.isdigit():
            raise ValueError("Phone must contain only digits (normalized)")

        # Validate country code
        if not phone_service.is_country_supported(self.country_code):
            raise ValueError(f"Unsupported country code: {self.country_code}")

        # Validate phone number for the specific country
        validation_result = phone_service.validate_phone(self.country_code, self.phone)
        if not validation_result.is_valid:
            raise ValueError(f"Invalid phone number: {validation_result.error_message}")

    @classmethod
    def create_minimal(
        cls, first_name: str, last_name: str, phone: str, country_code: str = "+1"
    ) -> "Patient":
        """Create a minimal patient record with required fields only."""
        return cls(
            id=str(uuid.uuid4()),
            first_name=first_name.strip(),
            last_name=last_name.strip(),
            phone=phone,
            country_code=country_code,
        )

    @property
    def formatted_phone(self) -> str:
        """Get formatted phone number for display."""
        return phone_service.format_phone(self.country_code, self.phone)

    @property
    def full_name(self) -> str:
        """Get the patient's full name."""
        return f"{self.first_name} {self.last_name}"

    @property
    def masked_phone(self) -> str:
        """Return phone with only last 4 digits visible."""
        if len(self.phone) <= 4:
            return "***" + self.phone
        return "***" + self.phone[-4:]
