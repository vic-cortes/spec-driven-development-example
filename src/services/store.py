"""In-memory store for patients and check-ins."""

from datetime import date
from typing import Dict, List, Optional, Set

from src.models.checkin import CheckIn
from src.models.patient import Patient


class MemoryStore:
    """In-memory storage for patients and check-ins."""

    def __init__(self):
        self._patients: Dict[str, Patient] = {}  # id -> Patient
        self._checkins: Dict[str, CheckIn] = {}  # id -> CheckIn
        self._phone_index: Dict[str, Set[str]] = {}  # phone -> set of patient IDs
        self._patient_checkins: Dict[str, Set[str]] = (
            {}
        )  # patient_id -> set of checkin IDs

    # Patient operations
    def add_patient(self, patient: Patient) -> None:
        """Add a patient to the store."""
        self._patients[patient.id] = patient

        # Update phone index
        if patient.phone not in self._phone_index:
            self._phone_index[patient.phone] = set()
        self._phone_index[patient.phone].add(patient.id)

    def get_patient(self, patient_id: str) -> Optional[Patient]:
        """Get a patient by ID."""
        return self._patients.get(patient_id)

    def find_patients_by_phone(self, phone: str) -> List[Patient]:
        """Find all patients with the given phone number."""
        patient_ids = self._phone_index.get(phone, set())
        return [self._patients[pid] for pid in patient_ids if pid in self._patients]

    def update_patient(self, patient: Patient) -> None:
        """Update an existing patient."""
        old_patient = self._patients.get(patient.id)
        if not old_patient:
            raise ValueError(f"Patient {patient.id} not found")

        # Update phone index if phone changed
        if old_patient.phone != patient.phone:
            # Remove from old phone
            old_phone_set = self._phone_index.get(old_patient.phone, set())
            old_phone_set.discard(patient.id)
            if not old_phone_set:
                del self._phone_index[old_patient.phone]

            # Add to new phone
            if patient.phone not in self._phone_index:
                self._phone_index[patient.phone] = set()
            self._phone_index[patient.phone].add(patient.id)

        self._patients[patient.id] = patient

    def delete_patient(self, patient_id: str) -> bool:
        """Delete a patient and their check-ins."""
        patient = self._patients.get(patient_id)
        if not patient:
            return False

        # Remove from phone index
        phone_set = self._phone_index.get(patient.phone, set())
        phone_set.discard(patient_id)
        if not phone_set:
            del self._phone_index[patient.phone]

        # Delete associated check-ins
        checkin_ids = self._patient_checkins.get(patient_id, set()).copy()
        for checkin_id in checkin_ids:
            self.delete_checkin(checkin_id)

        # Delete patient
        del self._patients[patient_id]
        return True

    # Check-in operations
    def add_checkin(self, checkin: CheckIn) -> None:
        """Add a check-in to the store."""
        self._checkins[checkin.id] = checkin

        # Update patient-checkin index
        if checkin.patient_id not in self._patient_checkins:
            self._patient_checkins[checkin.patient_id] = set()
        self._patient_checkins[checkin.patient_id].add(checkin.id)

    def get_checkin(self, checkin_id: str) -> Optional[CheckIn]:
        """Get a check-in by ID."""
        return self._checkins.get(checkin_id)

    def find_checkin_by_patient_and_date(
        self, patient_id: str, check_date: date
    ) -> Optional[CheckIn]:
        """Find existing check-in for a patient on a specific date."""
        checkin_ids = self._patient_checkins.get(patient_id, set())
        for checkin_id in checkin_ids:
            checkin = self._checkins.get(checkin_id)
            if checkin and checkin.date == check_date:
                return checkin
        return None

    def list_checkins_for_date(self, check_date: date) -> List[CheckIn]:
        """Get all check-ins for a specific date."""
        return [
            checkin for checkin in self._checkins.values() if checkin.date == check_date
        ]

    def update_checkin(self, checkin: CheckIn) -> None:
        """Update an existing check-in."""
        if checkin.id not in self._checkins:
            raise ValueError(f"CheckIn {checkin.id} not found")
        self._checkins[checkin.id] = checkin

    def delete_checkin(self, checkin_id: str) -> bool:
        """Delete a check-in."""
        checkin = self._checkins.get(checkin_id)
        if not checkin:
            return False

        # Remove from patient-checkin index
        patient_checkins = self._patient_checkins.get(checkin.patient_id, set())
        patient_checkins.discard(checkin_id)
        if not patient_checkins:
            del self._patient_checkins[checkin.patient_id]

        # Delete check-in
        del self._checkins[checkin_id]
        return True

    # Utility methods
    def clear_all(self) -> None:
        """Clear all data (useful for testing)."""
        self._patients.clear()
        self._checkins.clear()
        self._phone_index.clear()
        self._patient_checkins.clear()

    def get_stats(self) -> Dict[str, int]:
        """Get storage statistics."""
        return {
            "total_patients": len(self._patients),
            "total_checkins": len(self._checkins),
            "unique_phones": len(self._phone_index),
        }


# Global store instance
store = MemoryStore()
