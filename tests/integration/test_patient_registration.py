"""Integration tests for US patient registration workflow."""

from unittest.mock import patch

import pytest

from src.models.patient import Patient
from src.services.patient_service import PatientService
from src.services.store import MemoryStore
from src.utils.phone import normalize_international_phone


class TestUSPatientRegistration:
    """Test the complete US patient registration workflow."""

    @pytest.fixture
    def store(self):
        """Create a fresh memory store for testing."""
        store = MemoryStore()
        store.clear_all()
        return store

    @pytest.fixture
    def patient_service(self, store):
        """Create a patient service with clean store."""
        return PatientService(store)

    def test_register_us_patient_with_raw_phone(self, patient_service):
        """Test registering a US patient with unformatted phone number."""
        # Test with phone input that needs normalization
        raw_phone = "(555) 123-4567"

        # Normalize the phone for storage
        country_code, normalized_phone = normalize_international_phone(raw_phone, "+1")

        # Create patient with US country code
        patient = Patient.create_minimal(
            first_name="John",
            last_name="Doe",
            phone=normalized_phone,  # Just the digits part
            country_code=country_code,
        )

        # Add to store via service
        patient_service._store.add_patient(patient)

        # Verify patient was created correctly
        assert patient.first_name == "John"
        assert patient.last_name == "Doe"
        assert patient.phone == "5551234567"  # Normalized to digits only
        assert patient.country_code == "+1"
        assert patient.formatted_phone == "+1 (555) 123-4567"

    def test_register_us_patient_formatted_display(self, patient_service):
        """Test US patient registration shows proper formatted phone."""
        # Create patient with normalized phone
        patient = Patient.create_minimal(
            first_name="Jane",
            last_name="Smith",
            phone="2025551234",  # DC area code
            country_code="+1",
        )

        patient_service._store.add_patient(patient)

        # Verify formatting is correct
        assert patient.formatted_phone == "+1 (202) 555-1234"

        # Verify lookup by phone works
        found_patients = patient_service.find_by_phone("2025551234")
        assert len(found_patients) == 1
        assert found_patients[0].id == patient.id
        assert found_patients[0].formatted_phone == "+1 (202) 555-1234"

    def test_us_patient_validation_workflow(self, patient_service):
        """Test full validation workflow for US patient registration."""
        # Test valid US phone numbers
        valid_us_phones = [
            "5551234567",  # Direct digits
            "3125559876",  # Chicago area
            "2025551234",  # DC area
            "4155552345",  # San Francisco area
        ]

        for i, phone in enumerate(valid_us_phones):
            patient = Patient.create_minimal(
                first_name=f"Test{i}",
                last_name="Patient",
                phone=phone,
                country_code="+1",
            )

            patient_service._store.add_patient(patient)

            # Verify patient exists and has correct formatting
            found = patient_service.find_by_phone(phone)
            assert len(found) == 1
            assert found[0].country_code == "+1"
            assert found[0].formatted_phone.startswith("+1 (")
            assert "-" in found[0].formatted_phone  # Has hyphen in format

    def test_us_patient_registration_validation_errors(self):
        """Test validation errors during US patient registration."""
        # Test invalid phone lengths
        with pytest.raises(ValueError, match="Phone must be exactly 10 digits"):
            Patient.create_minimal(
                first_name="Invalid",
                last_name="Phone",
                phone="555123456",  # 9 digits
                country_code="+1",
            )

        with pytest.raises(ValueError, match="Phone must be exactly 10 digits"):
            Patient.create_minimal(
                first_name="Invalid",
                last_name="Phone",
                phone="55512345678",  # 11 digits
                country_code="+1",
            )

        # Test non-digit characters
        with pytest.raises(ValueError, match="Phone must contain only digits"):
            Patient.create_minimal(
                first_name="Invalid",
                last_name="Phone",
                phone="555abc4567",  # Contains letters
                country_code="+1",
            )

    def test_default_us_country_code(self, patient_service):
        """Test that US country code is used by default."""
        # Create patient without explicit country code (should default to +1)
        patient = Patient.create_minimal(
            first_name="Default",
            last_name="User",
            phone="5551234567",
            # No country_code specified - should default to +1
        )

        patient_service._store.add_patient(patient)

        # Verify default country code
        assert patient.country_code == "+1"
        assert patient.formatted_phone == "+1 (555) 123-4567"

    def test_us_patient_lookup_and_display(self, patient_service):
        """Test full cycle: register, lookup, and display formatting."""
        # Register multiple US patients
        patients_data = [
            ("Alice", "Johnson", "3125559876"),
            ("Bob", "Wilson", "2025551234"),
            ("Carol", "Brown", "5551112222"),
        ]

        created_patients = []
        for first, last, phone in patients_data:
            patient = Patient.create_minimal(
                first_name=first, last_name=last, phone=phone, country_code="+1"
            )
            patient_service._store.add_patient(patient)
            created_patients.append(patient)

        # Test lookup and verify formatting
        for i, (_, _, phone) in enumerate(patients_data):
            found = patient_service.find_by_phone(phone)
            assert len(found) == 1

            patient = found[0]
            assert patient.id == created_patients[i].id
            assert patient.country_code == "+1"

            # Verify formatted phone follows US pattern
            formatted = patient.formatted_phone
            assert formatted.startswith("+1 (")
            assert ") " in formatted
            assert "-" in formatted

            # Verify phone display masking works with country code
            masked = patient.masked_phone
            assert masked.startswith("+1 ***-")
            assert masked.endswith(phone[-4:])

    def test_us_patient_persistence_and_retrieval(self, patient_service):
        """Test that US patient data persists correctly."""
        # Create and store patient
        original_patient = Patient.create_minimal(
            first_name="Persistence",
            last_name="Test",
            phone="5551234567",
            country_code="+1",
        )

        patient_service._store.add_patient(original_patient)

        # Retrieve by ID
        retrieved = patient_service.get_patient(original_patient.id)
        assert retrieved is not None
        assert retrieved.id == original_patient.id
        assert retrieved.first_name == "Persistence"
        assert retrieved.last_name == "Test"
        assert retrieved.phone == "5551234567"
        assert retrieved.country_code == "+1"
        assert retrieved.formatted_phone == "+1 (555) 123-4567"

        # Retrieve by phone
        found_by_phone = patient_service.find_by_phone("5551234567")
        assert len(found_by_phone) == 1
        assert found_by_phone[0].id == original_patient.id
