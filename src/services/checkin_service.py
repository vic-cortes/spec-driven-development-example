"""Check-in service layer for managing patient arrivals."""

from datetime import date, datetime
from typing import List, Optional, Tuple

from src.models.checkin import CheckIn
from src.models.patient import Patient
from src.services.logger import logger
from src.services.store import store


class CheckInService:
    """Service for check-in related operations."""

    def __init__(self, data_store=None):
        """Initialize the check-in service."""
        self._store = data_store or store

    def check_in_patient(
        self, patient_id: str, route_note: Optional[str] = None
    ) -> CheckIn:
        """
        Check in a patient, following single-per-day policy.

        Args:
            patient_id: ID of patient to check in
            route_note: Optional note for routing/assignment

        Returns:
            CheckIn record (new or updated)

        Raises:
            ValueError: If patient not found
        """
        # Verify patient exists
        patient = self._store.get_patient(patient_id)
        if not patient:
            raise ValueError(f"Patient {patient_id} not found")

        today = date.today()

        # Check for existing check-in today
        existing_checkin = self._store.find_checkin_by_patient_and_date(
            patient_id, today
        )

        if existing_checkin:
            # Update timestamp for repeated arrival
            existing_checkin.update_timestamp()
            if route_note:
                existing_checkin.route_note = route_note
            self._store.update_checkin(existing_checkin)

            logger.info(
                f"Updated check-in for patient {patient.full_name} at {existing_checkin.timestamp.strftime('%H:%M')}"
            )
            return existing_checkin
        else:
            # Create new check-in
            new_checkin = CheckIn.create_new(patient_id, route_note)
            self._store.add_checkin(new_checkin)

            logger.info(
                f"New check-in for patient {patient.full_name} at {new_checkin.timestamp.strftime('%H:%M')}"
            )
            return new_checkin

    def get_todays_arrivals(
        self, target_date: Optional[date] = None
    ) -> List[Tuple[CheckIn, Patient]]:
        """
        Get all arrivals for a specific date with patient information.

        Args:
            target_date: Date to get arrivals for (defaults to today)

        Returns:
            List of (CheckIn, Patient) tuples sorted by arrival time
        """
        if target_date is None:
            target_date = date.today()

        checkins = self._store.list_checkins_for_date(target_date)

        # Join with patient data
        arrivals = []
        for checkin in checkins:
            patient = self._store.get_patient(checkin.patient_id)
            if patient:  # Only include if patient still exists
                arrivals.append((checkin, patient))

        # Sort by arrival time
        arrivals.sort(key=lambda x: x[0].timestamp)

        logger.info(f"Retrieved {len(arrivals)} arrivals for {target_date}")
        return arrivals

    def get_checkin_by_id(self, checkin_id: str) -> Optional[CheckIn]:
        """Get a check-in by ID."""
        return self._store.get_checkin(checkin_id)

    def has_checked_in_today(
        self, patient_id: str, target_date: Optional[date] = None
    ) -> bool:
        """
        Check if a patient has already checked in today.

        Args:
            patient_id: ID of patient to check
            target_date: Date to check (defaults to today)

        Returns:
            True if patient has checked in, False otherwise
        """
        if target_date is None:
            target_date = date.today()

        existing_checkin = self._store.find_checkin_by_patient_and_date(
            patient_id, target_date
        )
        return existing_checkin is not None

    def get_checkin_stats(self, target_date: Optional[date] = None) -> dict:
        """
        Get check-in statistics for a date.

        Args:
            target_date: Date to get stats for (defaults to today)

        Returns:
            Dictionary with check-in statistics
        """
        if target_date is None:
            target_date = date.today()

        checkins = self._store.list_checkins_for_date(target_date)

        if not checkins:
            return {"total_arrivals": 0, "first_arrival": None, "last_arrival": None}

        timestamps = [c.timestamp for c in checkins]

        return {
            "total_arrivals": len(checkins),
            "first_arrival": min(timestamps),
            "last_arrival": max(timestamps),
        }

    def complete_checkin_workflow(
        self, patient: Patient, route_note: Optional[str] = None
    ) -> Tuple[CheckIn, bool]:
        """
        Complete workflow for checking in a patient.

        Args:
            patient: Patient to check in
            route_note: Optional routing note

        Returns:
            Tuple of (CheckIn, was_repeat_arrival)
        """
        was_repeat = self.has_checked_in_today(patient.id)
        checkin = self.check_in_patient(patient.id, route_note)

        return checkin, was_repeat

    def get_arrival_summary(self, target_date: Optional[date] = None) -> str:
        """
        Get a text summary of arrivals for display.

        Args:
            target_date: Date to summarize (defaults to today)

        Returns:
            Human-readable summary string
        """
        if target_date is None:
            target_date = date.today()

        arrivals = self.get_todays_arrivals(target_date)
        stats = self.get_checkin_stats(target_date)

        if not arrivals:
            return f"No arrivals yet today ({target_date})"

        summary_lines = [
            f"Today's Arrivals ({target_date}): {stats['total_arrivals']} patients",
            f"First arrival: {stats['first_arrival'].strftime('%H:%M')}",
            f"Last arrival: {stats['last_arrival'].strftime('%H:%M')}",
        ]

        return "\n".join(summary_lines)


# Global service instance
checkin_service = CheckInService()
