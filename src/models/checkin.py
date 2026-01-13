"""CheckIn model for the dental check-in system."""

import uuid
from dataclasses import dataclass
from datetime import date, datetime
from enum import Enum
from typing import Optional


class CheckInStatus(Enum):
    """Status of a check-in entry."""

    CHECKED_IN = "checked_in"
    ARRIVED = "arrived"


@dataclass
class CheckIn:
    """Represents a single patient arrival event."""

    id: str
    patient_id: str
    timestamp: datetime
    date: date
    status: CheckInStatus = CheckInStatus.CHECKED_IN
    route_note: Optional[str] = None

    def __post_init__(self):
        """Validate check-in data after initialization."""
        if not self.patient_id:
            raise ValueError("Patient ID is required")
        if self.date != self.timestamp.date():
            raise ValueError("Date must match timestamp date")

    @classmethod
    def create_new(cls, patient_id: str, route_note: Optional[str] = None) -> "CheckIn":
        """Create a new check-in for the given patient."""
        now = datetime.now()
        return cls(
            id=str(uuid.uuid4()),
            patient_id=patient_id,
            timestamp=now,
            date=now.date(),
            status=CheckInStatus.CHECKED_IN,
            route_note=route_note,
        )

    def update_timestamp(self) -> None:
        """Update the timestamp for repeated check-ins on the same day."""
        now = datetime.now()
        if now.date() != self.date:
            raise ValueError("Cannot update timestamp for different date")
        self.timestamp = now
