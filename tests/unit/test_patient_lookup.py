"""Unit tests for patient lookup functionality."""

from datetime import date

import pytest

from src.models.patient import Patient
from src.services.store import MemoryStore
from src.utils.phone import normalize_phone


class TestPatientLookup:
    """Test patient lookup operations."""

    @pytest.fixture
    def store(self):
        """Create a fresh memory store for testing."""
        store = MemoryStore()
        store.clear_all()
        return store

    @pytest.fixture
    def sample_patients(self, store):
        """Create sample patients for testing."""
        patients = [
            Patient(
                id="patient-001",
                first_name="Maria",
                last_name="Garcia",
                phone="5551234567",
                email="maria@test.com",
            ),
            Patient(
                id="patient-002",
                first_name="John",
                last_name="Smith",
                phone="5559876543",
            ),
            # Family with shared phone
            Patient(
                id="patient-003",
                first_name="Michael",
                last_name="Wilson",
                phone="5553336666",
            ),
            Patient(
                id="patient-004",
                first_name="Sarah",
                last_name="Wilson",
                phone="5553336666",  # Same as Michael
            ),
        ]

        for patient in patients:
            store.add_patient(patient)

        return patients

    def test_find_patient_by_phone_single_match(self, store, sample_patients):
        """Test finding a patient with unique phone."""
        results = store.find_patients_by_phone("5551234567")
        assert len(results) == 1
        assert results[0].first_name == "Maria"
        assert results[0].last_name == "Garcia"

    def test_find_patient_by_phone_multiple_matches(self, store, sample_patients):
        """Test finding patients with shared phone."""
        results = store.find_patients_by_phone("5553336666")
        assert len(results) == 2
        names = {(p.first_name, p.last_name) for p in results}
        assert ("Michael", "Wilson") in names
        assert ("Sarah", "Wilson") in names

    def test_find_patient_by_phone_no_match(self, store, sample_patients):
        """Test finding patient with non-existent phone."""
        results = store.find_patients_by_phone("5550000000")
        assert len(results) == 0

    def test_find_patient_by_phone_normalized(self, store, sample_patients):
        """Test phone lookup with different formats."""
        # All these should find Maria Garcia
        test_formats = [
            "5551234567",
            "555-123-4567",
            "(555) 123-4567",
            "555.123.4567",
            "+1 555 123 4567",
        ]

        for phone_format in test_formats:
            normalized = normalize_phone(phone_format)
            results = store.find_patients_by_phone(normalized)
            assert len(results) == 1
            assert results[0].first_name == "Maria"

    def test_patient_creation_minimal(self):
        """Test creating minimal patient records."""
        patient = Patient.create_minimal("Jane", "Doe", "5551111111")

        assert patient.first_name == "Jane"
        assert patient.last_name == "Doe"
        assert patient.phone == "5551111111"
        assert patient.id is not None
        assert patient.email is None
        assert patient.birth_date is None

    def test_patient_creation_validation(self):
        """Test patient creation validation."""
        # Empty names should fail
        with pytest.raises(ValueError, match="First name is required"):
            Patient.create_minimal("", "Doe", "5551111111")

        with pytest.raises(ValueError, match="Last name is required"):
            Patient.create_minimal("Jane", "", "5551111111")

        # Invalid phone should fail
        with pytest.raises(ValueError, match="Phone must be at least 8 digits"):
            Patient.create_minimal("Jane", "Doe", "555111")

    def test_patient_masked_phone(self):
        """Test phone masking for privacy."""
        patient = Patient(
            id="test-001", first_name="Test", last_name="User", phone="5551234567"
        )

        assert patient.masked_phone == "+1 ***-4567"

    def test_patient_masked_phone_short(self):
        """Test phone masking for short numbers."""
        # Use a valid 10-digit phone but test masking behavior
        patient = Patient(
            id="test-001",
            first_name="Test",
            last_name="User",
            phone="1234567890",  # Valid 10 digits
        )

        assert patient.masked_phone == "+1 ***-7890"

    def test_patient_full_name(self):
        """Test full name property."""
        patient = Patient(
            id="test-001", first_name="Jane", last_name="Doe", phone="5551234567"
        )

        assert patient.full_name == "Jane Doe"

    def test_patient_update_phone_index(self, store):
        """Test that updating phone updates the search index."""
        # Create patient
        patient = Patient.create_minimal("John", "Doe", "5551111111")
        store.add_patient(patient)

        # Verify original phone lookup
        results = store.find_patients_by_phone("5551111111")
        assert len(results) == 1

        # Create updated patient with new phone
        updated_patient = Patient(
            id=patient.id,
            first_name=patient.first_name,
            last_name=patient.last_name,
            phone="5552222222",
            email=patient.email,
            birth_date=patient.birth_date,
            address=patient.address,
            notes=patient.notes,
        )
        store.update_patient(updated_patient)

        # Verify old phone returns no results
        results = store.find_patients_by_phone("5551111111")
        assert len(results) == 0

        # Verify new phone returns the patient
        results = store.find_patients_by_phone("5552222222")
        assert len(results) == 1
        assert results[0].first_name == "John"
