"""Unit tests for patient service duplicate detection and merge functionality."""

import pytest

from src.models.patient import Patient
from src.services.patient_service import PatientService
from src.services.store import MemoryStore


class TestPatientDuplicateDetection:
    """Test patient duplicate detection and merge operations."""

    @pytest.fixture
    def store(self):
        """Create a fresh memory store for testing."""
        store = MemoryStore()
        store.clear_all()
        return store

    @pytest.fixture
    def patient_service(self, store):
        """Create patient service with test store."""
        return PatientService(data_store=store)

    def test_find_potential_duplicates_empty_phone(self, patient_service):
        """Test duplicate detection with empty phone number."""
        duplicates = patient_service.find_potential_duplicates("")
        assert len(duplicates) == 0

    def test_find_potential_duplicates_invalid_phone(self, patient_service):
        """Test duplicate detection with invalid phone number."""
        duplicates = patient_service.find_potential_duplicates("invalid")
        assert len(duplicates) == 0

    def test_find_potential_duplicates_with_exclusion(self, patient_service):
        """Test duplicate detection with patient exclusion."""
        # Create two patients with same phone
        patient1 = patient_service.create_minimal_patient(
            "Alice", "Smith", "5551111111"
        )
        patient2 = patient_service.create_minimal_patient("Bob", "Smith", "5551111111")

        # Find duplicates excluding patient1
        duplicates = patient_service.find_potential_duplicates(
            "5551111111", exclude_patient_id=patient1.id
        )
        assert len(duplicates) == 1
        assert duplicates[0].id == patient2.id

        # Find duplicates excluding patient2
        duplicates = patient_service.find_potential_duplicates(
            "5551111111", exclude_patient_id=patient2.id
        )
        assert len(duplicates) == 1
        assert duplicates[0].id == patient1.id

    def test_update_patient_with_duplicate_check_no_duplicates(self, patient_service):
        """Test updating patient when no duplicates exist."""
        patient = patient_service.create_minimal_patient("John", "Doe", "5551234567")

        updated_patient = Patient(
            id=patient.id,
            first_name="John",
            last_name="Doe",
            phone="5559876543",  # New unique phone
            email="john@example.com",
        )

        result, duplicates = patient_service.update_patient_with_duplicate_check(
            updated_patient
        )

        assert result.phone == "5559876543"
        assert result.email == "john@example.com"
        assert len(duplicates) == 0

    def test_update_patient_with_duplicate_check_has_duplicates(self, patient_service):
        """Test updating patient when duplicates exist."""
        # Create two patients
        patient1 = patient_service.create_minimal_patient(
            "Alice", "Johnson", "5551111111"
        )
        patient2 = patient_service.create_minimal_patient("Bob", "Wilson", "5552222222")

        # Update patient2 to have same phone as patient1
        updated_patient = Patient(
            id=patient2.id,
            first_name="Bob",
            last_name="Wilson",
            phone="5551111111",  # Same as patient1
        )

        result, duplicates = patient_service.update_patient_with_duplicate_check(
            updated_patient
        )

        assert result.phone == "5551111111"
        assert len(duplicates) == 1
        assert duplicates[0].id == patient1.id

    def test_suggest_merge_candidates_nonexistent_patient(self, patient_service):
        """Test suggesting merge candidates for non-existent patient."""
        candidates = patient_service.suggest_merge_candidates("nonexistent-id")
        assert len(candidates) == 0

    def test_suggest_merge_candidates_no_duplicates(self, patient_service):
        """Test suggesting merge candidates when no duplicates exist."""
        patient = patient_service.create_minimal_patient("Jane", "Doe", "5551234567")

        candidates = patient_service.suggest_merge_candidates(patient.id)
        assert len(candidates) == 0

    def test_suggest_merge_candidates_has_duplicates(self, patient_service):
        """Test suggesting merge candidates when duplicates exist."""
        # Create patients with same phone
        patient1 = patient_service.create_minimal_patient(
            "Alice", "Brown", "5551111111"
        )
        patient2 = patient_service.create_minimal_patient(
            "Alice", "Brown", "5551111111"
        )
        patient3 = patient_service.create_minimal_patient("Bob", "Green", "5551111111")

        candidates = patient_service.suggest_merge_candidates(patient1.id)
        assert len(candidates) == 2
        candidate_ids = [c.id for c in candidates]
        assert patient2.id in candidate_ids
        assert patient3.id in candidate_ids
        assert patient1.id not in candidate_ids

    def test_merge_duplicate_patients_same_patient(self, patient_service):
        """Test merging a patient with itself should raise error."""
        patient = patient_service.create_minimal_patient("Test", "User", "5551234567")

        with pytest.raises(ValueError, match="Cannot merge patient with itself"):
            patient_service.merge_duplicate_patients(patient.id, patient.id)

    def test_merge_duplicate_patients_nonexistent_primary(self, patient_service):
        """Test merging when primary patient doesn't exist."""
        patient = patient_service.create_minimal_patient("Test", "User", "5551234567")

        with pytest.raises(ValueError, match="One or both patients not found"):
            patient_service.merge_duplicate_patients("nonexistent", patient.id)

    def test_merge_duplicate_patients_nonexistent_duplicate(self, patient_service):
        """Test merging when duplicate patient doesn't exist."""
        patient = patient_service.create_minimal_patient("Test", "User", "5551234567")

        with pytest.raises(ValueError, match="One or both patients not found"):
            patient_service.merge_duplicate_patients(patient.id, "nonexistent")

    def test_merge_duplicate_patients_has_additional_data(self, patient_service):
        """Test merging fails when duplicate has additional data."""
        # Create primary patient (minimal)
        primary = patient_service.create_minimal_patient("Alice", "Smith", "5551111111")

        # Create duplicate with additional data
        duplicate = Patient(
            id="dup-001",
            first_name="Alice",
            last_name="Smith",
            phone="5551111111",
            email="alice@example.com",  # Additional data
        )
        patient_service._store.add_patient(duplicate)

        # Merge should fail
        result = patient_service.merge_duplicate_patients(primary.id, duplicate.id)
        assert result is False

        # Duplicate should still exist
        assert patient_service.get_patient(duplicate.id) is not None

    def test_merge_duplicate_patients_successful_merge(self, patient_service):
        """Test successful merge of minimal duplicate patient."""
        # Create primary patient
        primary = patient_service.create_minimal_patient("Alice", "Smith", "5551111111")

        # Create minimal duplicate
        duplicate = patient_service.create_minimal_patient(
            "Alice", "Smith", "5551111111"
        )

        # Merge should succeed
        result = patient_service.merge_duplicate_patients(primary.id, duplicate.id)
        assert result is True

        # Duplicate should be deleted
        assert patient_service.get_patient(duplicate.id) is None

        # Primary should still exist
        assert patient_service.get_patient(primary.id) is not None

    def test_merge_notes_both_empty(self, patient_service):
        """Test note merging when both are empty."""
        result = patient_service._merge_notes(None, None)
        assert result is None

        result = patient_service._merge_notes("", "")
        assert result is None

    def test_merge_notes_one_empty(self, patient_service):
        """Test note merging when one is empty."""
        result = patient_service._merge_notes("Primary notes", None)
        assert result == "Primary notes"

        result = patient_service._merge_notes(None, "Duplicate notes")
        assert result == "Duplicate notes"

    def test_merge_notes_both_have_content(self, patient_service):
        """Test note merging when both have content."""
        result = patient_service._merge_notes("Primary notes", "Duplicate notes")
        expected = "Primary notes\n\n[Merged from duplicate record]\nDuplicate notes"
        assert result == expected
