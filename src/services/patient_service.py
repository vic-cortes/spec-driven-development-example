"""Patient service layer for lookup and management operations."""

from typing import List, Optional, Tuple

from src.models.patient import Patient
from src.services.logger import logger, mask_pii_data
from src.services.store import store
from src.utils.phone import is_valid_phone, normalize_phone


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

        # Delete the duplicate (simple case)
        success = self._store.delete_patient(duplicate_patient_id)
        if success:
            logger.info(
                f"Merged duplicate patient {duplicate_patient_id} into {primary_patient_id}"
            )

        return success


# Global service instance
patient_service = PatientService()
