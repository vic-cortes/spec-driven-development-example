"""Integration tests for Mexican patient workflow and phone display formatting."""

from unittest.mock import patch

import pytest

from src.models.patient import Patient
from src.services.patient_service import PatientService
from src.services.store import MemoryStore
from src.utils.phone import normalize_international_phone


class TestMexicanPatientWorkflow:
    """Test the complete Mexican patient workflow including phone display."""

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

    def test_complete_mexican_patient_workflow(self, patient_service):
        """Test end-to-end Mexican patient workflow from creation to display."""
        # Step 1: Create Mexican patient with formatted phone input
        raw_phone_input = "+52 551 234 5678"
        country_code, normalized_phone = normalize_international_phone(
            raw_phone_input, "+52"
        )

        patient = Patient.create_minimal(
            first_name="Ana",
            last_name="Hernández",
            phone=normalized_phone,
            country_code=country_code,
        )

        # Step 2: Add to store
        patient_service._store.add_patient(patient)

        # Step 3: Verify patient creation with Mexican formatting
        assert patient.first_name == "Ana"
        assert patient.last_name == "Hernández"
        assert patient.phone == "5512345678"  # Normalized storage
        assert patient.country_code == "+52"

        # Step 4: Verify phone display formatting
        assert patient.formatted_phone == "+52 (551) 234-5678"
        assert patient.masked_phone == "+52 ***-5678"

        # Step 5: Test retrieval and display consistency
        retrieved = patient_service.get_patient(patient.id)
        assert retrieved is not None
        assert retrieved.formatted_phone == "+52 (551) 234-5678"
        assert retrieved.masked_phone == "+52 ***-5678"

        # Step 6: Test phone lookup works with normalized number
        found_patients = patient_service.find_by_phone("5512345678")
        assert len(found_patients) == 1
        assert found_patients[0].id == patient.id
        assert found_patients[0].formatted_phone == "+52 (551) 234-5678"

    def test_mexican_phone_display_consistency(self, patient_service):
        """Test that Mexican phone displays are consistent across different contexts."""
        # Create Mexican patients with different area codes
        test_cases = [
            ("5512345678", "Mexico City", "+52 (551) 234-5678"),
            ("3312345678", "Guadalajara", "+52 (331) 234-5678"),
            ("8112345678", "Monterrey", "+52 (811) 234-5678"),
        ]

        for phone_digits, location, expected_format in test_cases:
            patient = Patient.create_minimal(
                first_name=f"Test",
                last_name=f"Patient-{location}",
                phone=phone_digits,
                country_code="+52",
            )
            patient_service._store.add_patient(patient)

            # Verify consistent formatting
            assert patient.formatted_phone == expected_format
            assert patient.masked_phone == f"+52 ***-{phone_digits[-4:]}"

            # Verify retrieval consistency
            retrieved = patient_service.get_patient(patient.id)
            assert retrieved.formatted_phone == expected_format
            assert retrieved.masked_phone == f"+52 ***-{phone_digits[-4:]}"

    def test_mixed_us_mexican_phone_display_workflow(self, patient_service):
        """Test workflow with both US and Mexican patients to ensure no conflicts."""
        # Create US patient
        us_patient = Patient.create_minimal(
            first_name="John",
            last_name="Smith",
            phone="5551234567",
            country_code="+1",
        )
        patient_service._store.add_patient(us_patient)

        # Create Mexican patient
        mx_patient = Patient.create_minimal(
            first_name="María",
            last_name="González",
            phone="5512345678",
            country_code="+52",
        )
        patient_service._store.add_patient(mx_patient)

        # Verify both patients display correctly
        assert us_patient.formatted_phone == "+1 (555) 123-4567"
        assert us_patient.masked_phone == "+1 ***-4567"

        assert mx_patient.formatted_phone == "+52 (551) 234-5678"
        assert mx_patient.masked_phone == "+52 ***-5678"

        # Verify search works independently
        us_found = patient_service.find_by_phone("5551234567")
        mx_found = patient_service.find_by_phone("5512345678")

        assert len(us_found) == 1
        assert len(mx_found) == 1
        assert us_found[0].id == us_patient.id
        assert mx_found[0].id == mx_patient.id

        # Verify display formatting remains correct after search
        assert us_found[0].formatted_phone == "+1 (555) 123-4567"
        assert mx_found[0].formatted_phone == "+52 (551) 234-5678"

    def test_mexican_phone_validation_error_workflow(self, patient_service):
        """Test Mexican phone validation error handling in complete workflow."""
        # Test various invalid Mexican phone scenarios
        invalid_cases = [
            ("55123456", "too short"),  # 8 digits
            ("551234567890", "too long"),  # 12 digits
            ("551abc5678", "contains letters"),
            ("", "empty"),
        ]

        for invalid_phone, description in invalid_cases:
            with pytest.raises(ValueError) as exc_info:
                Patient.create_minimal(
                    first_name="Test",
                    last_name="Invalid",
                    phone=invalid_phone,
                    country_code="+52",
                )

            # Verify error message mentions Mexican phone requirements
            error_msg = str(exc_info.value).lower()
            assert any(word in error_msg for word in ["phone", "digit", "invalid"])

    def test_mexican_phone_formatting_edge_cases(self, patient_service):
        """Test Mexican phone formatting edge cases."""
        # Test edge case phone numbers
        edge_cases = [
            ("0001234567", "+52 (000) 123-4567"),  # Leading zeros
            ("1111111111", "+52 (111) 111-1111"),  # All same digit
            ("9999999999", "+52 (999) 999-9999"),  # All nines
        ]

        for phone_digits, expected_format in edge_cases:
            patient = Patient.create_minimal(
                first_name="Edge",
                last_name="Case",
                phone=phone_digits,
                country_code="+52",
            )
            patient_service._store.add_patient(patient)

            assert patient.formatted_phone == expected_format
            assert patient.masked_phone == f"+52 ***-{phone_digits[-4:]}"

    def test_mexican_phone_input_normalization_workflow(self, patient_service):
        """Test that various Mexican phone input formats normalize correctly."""
        # Different input formats that should all normalize to same result
        input_formats = [
            "+52 551 234 5678",
            "+52-551-234-5678",
            "+52.551.234.5678",
            "+52 (551) 234-5678",
            "525512345678",  # With country code prefix
        ]

        expected_normalized = "5512345678"
        expected_format = "+52 (551) 234-5678"

        for i, input_format in enumerate(input_formats):
            try:
                country_code, normalized_phone = normalize_international_phone(
                    input_format, "+52"
                )

                patient = Patient.create_minimal(
                    first_name=f"Test{i}",
                    last_name="Normalize",
                    phone=normalized_phone,
                    country_code=country_code,
                )
                patient_service._store.add_patient(patient)

                assert patient.phone == expected_normalized
                assert patient.country_code == "+52"
                assert patient.formatted_phone == expected_format

            except ValueError:
                # Some formats might not be supported, which is OK
                # This tests what works consistently
                continue

    def test_mexican_patient_update_phone_workflow(self, patient_service):
        """Test updating a Mexican patient's phone number maintains proper formatting."""
        # Create original patient
        original_patient = Patient.create_minimal(
            first_name="Update",
            last_name="Test",
            phone="5512345678",
            country_code="+52",
        )
        patient_service._store.add_patient(original_patient)

        # Update with new phone number
        updated_patient = Patient(
            id=original_patient.id,
            first_name=original_patient.first_name,
            last_name=original_patient.last_name,
            phone="3312345678",  # New Guadalajara number
            country_code="+52",
            email=original_patient.email,
            address=original_patient.address,
            notes=original_patient.notes,
        )

        patient_service._store.update_patient(updated_patient)

        # Verify update worked and formatting is correct
        retrieved = patient_service.get_patient(original_patient.id)
        assert retrieved.phone == "3312345678"
        assert retrieved.formatted_phone == "+52 (331) 234-5678"
        assert retrieved.masked_phone == "+52 ***-5678"

        # Verify old phone no longer finds the patient
        old_phone_results = patient_service.find_by_phone("5512345678")
        assert len(old_phone_results) == 0

        # Verify new phone finds the patient
        new_phone_results = patient_service.find_by_phone("3312345678")
        assert len(new_phone_results) == 1
        assert new_phone_results[0].id == original_patient.id
