"""Patient service layer for lookup and management operations."""

from typing import List, Optional, Tuple

from src.models.patient import Patient
from src.services.logger import logger, mask_pii_data
from src.services.store import store
from src.utils.phone import (
    is_valid_phone,
    normalize_international_phone,
    normalize_phone,
)


class PatientService:
    """Service for patient-related operations."""

    def __init__(self, data_store=None):
        """Initialize the patient service."""
        self._store = data_store or store

    def find_by_phone(self, phone: str) -> List[Patient]:
        """
        Find patients by phone number.

        Args:
            phone: Phone number in any format

        Returns:
            List of patients matching the phone number

        Raises:
            ValueError: If phone number is invalid
        """
        if not is_valid_phone(phone):
            logger.warning(f"Invalid phone number format: {phone[:3]}***")
            raise ValueError(f"Invalid phone number format")

        normalized = normalize_phone(phone)
        patients = self._store.find_patients_by_phone(normalized)

        logger.info(
            f"Phone lookup returned {len(patients)} patients for phone {normalized[-4:]}***"
        )
        return patients

    def create_minimal_patient(
        self, first_name: str, last_name: str, phone: str
    ) -> Patient:
        """
        Create a minimal patient record.

        Args:
            first_name: Patient's first name
            last_name: Patient's last name
            phone: Phone number in any format

        Returns:
            Created patient

        Raises:
            ValueError: If input validation fails
        """
        if not first_name.strip():
            raise ValueError("First name is required")
        if not last_name.strip():
            raise ValueError("Last name is required")
        if not is_valid_phone(phone):
            raise ValueError("Invalid phone number")

        normalized_phone = normalize_phone(phone)
        patient = Patient.create_minimal(
            first_name.strip(), last_name.strip(), normalized_phone
        )

        self._store.add_patient(patient)

        # Log patient creation (with PII masking)
        patient_data = {
            "id": patient.id,
            "name": patient.full_name,
            "phone": patient.phone,
        }
        masked_data = mask_pii_data(patient_data)
        logger.info(f"Created minimal patient: {masked_data}")

        return patient

    def create_patient(
        self, first_name: str, last_name: str, phone: str, country_code: str = "+1"
    ) -> Patient:
        """
        Create a patient record with international phone number support.

        Args:
            first_name: Patient's first name
            last_name: Patient's last name
            phone: Phone number in any format
            country_code: Country code ("+1" or "+52"), defaults to "+1"

        Returns:
            Created patient

        Raises:
            ValueError: If input validation fails
        """
        if not first_name.strip():
            raise ValueError("First name is required")
        if not last_name.strip():
            raise ValueError("Last name is required")

        # Normalize international phone number
        try:
            normalized_country, normalized_phone = normalize_international_phone(
                phone, country_code
            )
        except ValueError as e:
            raise ValueError(f"Invalid phone number: {str(e)}")

        # Create patient with international support
        patient = Patient.create_minimal(
            first_name.strip(), last_name.strip(), normalized_phone, normalized_country
        )

        self._store.add_patient(patient)

        # Log patient creation (with PII masking)
        patient_data = {
            "id": patient.id,
            "name": patient.full_name,
            "phone": patient.phone,
            "country_code": patient.country_code,
        }
        masked_data = mask_pii_data(patient_data)
        logger.info(f"Created international patient: {masked_data}")

        return patient

    def get_patient(self, patient_id: str) -> Optional[Patient]:
        """Get a patient by ID."""
        return self._store.get_patient(patient_id)

    def update_patient(self, patient: Patient) -> None:
        """
        Update an existing patient.

        Args:
            patient: Updated patient object

        Raises:
            ValueError: If patient not found or validation fails
        """
        if not patient.first_name.strip():
            raise ValueError("First name is required")
        if not patient.last_name.strip():
            raise ValueError("Last name is required")
        if not is_valid_phone(patient.phone):
            raise ValueError("Invalid phone number")

        self._store.update_patient(patient)

        # Log update (with PII masking)
        patient_data = {
            "id": patient.id,
            "name": patient.full_name,
            "phone": patient.phone,
        }
        masked_data = mask_pii_data(patient_data)
        logger.info(f"Updated patient: {masked_data}")

    def search_and_create_workflow(self, phone: str) -> Tuple[List[Patient], bool]:
        """
        Combined workflow: search for patients by phone.

        Args:
            phone: Phone number to search for

        Returns:
            Tuple of (patients_found, needs_disambiguation)
            - patients_found: List of matching patients
            - needs_disambiguation: True if multiple patients found
        """
        try:
            patients = self.find_by_phone(phone)
            needs_disambiguation = len(patients) > 1
            return patients, needs_disambiguation
        except ValueError as e:
            logger.error(f"Phone search failed: {str(e)}")
            raise

    def find_potential_duplicates(
        self, phone: str, exclude_patient_id: str = None
    ) -> List[Patient]:
        """
        Find patients with the same phone number (potential duplicates).

        Args:
            phone: Phone number to check for duplicates
            exclude_patient_id: Patient ID to exclude from results (for updates)

        Returns:
            List of patients with matching phone numbers
        """
        if not is_valid_phone(phone):
            return []

        normalized = normalize_phone(phone)
        patients = self._store.find_patients_by_phone(normalized)

        if exclude_patient_id:
            patients = [p for p in patients if p.id != exclude_patient_id]

        return patients

    def update_patient_with_duplicate_check(
        self, patient: Patient
    ) -> Tuple[Patient, List[Patient]]:
        """
        Update a patient and return any potential duplicates found.

        Args:
            patient: Updated patient object

        Returns:
            Tuple of (updated_patient, potential_duplicates)

        Raises:
            ValueError: If patient not found or validation fails
        """
        # First validate the update
        if not patient.first_name.strip():
            raise ValueError("First name is required")
        if not patient.last_name.strip():
            raise ValueError("Last name is required")
        if not is_valid_phone(patient.phone):
            raise ValueError("Invalid phone number")

        # Check for potential duplicates before updating
        potential_duplicates = self.find_potential_duplicates(
            patient.phone, exclude_patient_id=patient.id
        )

        # Update the patient
        self.update_patient(patient)

        # Log potential duplicates if found
        if potential_duplicates:
            logger.warning(
                f"Patient update created potential duplicates: {len(potential_duplicates)} patients with same phone"
            )

        return patient, potential_duplicates

    def merge_duplicate_patients(
        self, primary_patient_id: str, duplicate_patient_id: str
    ) -> bool:
        """
        Merge a duplicate patient into the primary patient.

        Args:
            primary_patient_id: ID of patient to keep
            duplicate_patient_id: ID of patient to merge/delete

        Returns:
            True if merge successful, False if merge not allowed
        """
        primary = self._store.get_patient(primary_patient_id)
        duplicate = self._store.get_patient(duplicate_patient_id)

        if not primary or not duplicate:
            raise ValueError("One or both patients not found")

        if primary.id == duplicate.id:
            raise ValueError("Cannot merge patient with itself")

        # Check if duplicate has any check-ins (merge policy: don't delete if has history)
        # This is a simplified check - in Phase 3 we don't have the full check-in history check
        # Will be enhanced in later phases

        # For now, only allow deletion if it's a truly minimal record
        if (
            duplicate.email
            or duplicate.birth_date
            or duplicate.address
            or duplicate.notes
        ):
            logger.warning(
                f"Cannot merge patient {duplicate_patient_id} - has additional data"
            )
            return False

        # Merge strategy: keep primary, enhance with any missing data from duplicate
        merged_data_updated = False
        updated_primary = Patient(
            id=primary.id,
            first_name=primary.first_name,
            last_name=primary.last_name,
            phone=primary.phone,
            email=primary.email or duplicate.email,
            birth_date=primary.birth_date or duplicate.birth_date,
            address=primary.address or duplicate.address,
            notes=self._merge_notes(primary.notes, duplicate.notes),
        )

        # Check if any data was merged
        if (
            updated_primary.email != primary.email
            or updated_primary.birth_date != primary.birth_date
            or updated_primary.address != primary.address
            or updated_primary.notes != primary.notes
        ):
            merged_data_updated = True
            self.update_patient(updated_primary)

        # Delete the duplicate (simple case)
        success = self._store.delete_patient(duplicate_patient_id)
        if success:
            merge_details = (
                "with data merge" if merged_data_updated else "simple deletion"
            )
            logger.info(
                f"Merged duplicate patient {duplicate_patient_id} into {primary_patient_id} ({merge_details})"
            )

        return success

    def _merge_notes(self, primary_notes: str, duplicate_notes: str) -> str:
        """
        Merge notes from two patient records.

        Args:
            primary_notes: Notes from primary patient
            duplicate_notes: Notes from duplicate patient

        Returns:
            Merged notes string
        """
        if not primary_notes and not duplicate_notes:
            return None

        if not primary_notes:
            return duplicate_notes

        if not duplicate_notes:
            return primary_notes

        # Both have notes - merge them
        return f"{primary_notes}\n\n[Merged from duplicate record]\n{duplicate_notes}"

    def suggest_merge_candidates(self, patient_id: str) -> List[Patient]:
        """
        Suggest potential merge candidates for a patient based on phone number.

        Args:
            patient_id: ID of patient to find merge candidates for

        Returns:
            List of potential duplicate patients
        """
        patient = self.get_patient(patient_id)
        if not patient:
            return []

        return self.find_potential_duplicates(
            patient.phone, exclude_patient_id=patient_id
        )


# Global service instance
patient_service = PatientService()
