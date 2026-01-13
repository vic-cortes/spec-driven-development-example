"""Unit tests for Patient model with US phone number formatting."""

import uuid
from datetime import date

import pytest

from src.models.patient import Patient


class TestPatientModel:
    """Test Patient model functionality."""

    def test_patient_creation_with_us_phone(self):
        """Test creating a patient with US phone number."""
        patient = Patient(
            id=str(uuid.uuid4()),
            first_name="John",
            last_name="Doe",
            phone="5551234567",
            country_code="+1",
        )

        assert patient.first_name == "John"
        assert patient.last_name == "Doe"
        assert patient.phone == "5551234567"
        assert patient.country_code == "+1"

    def test_patient_us_formatted_phone_display(self):
        """Test US phone number formatting for display."""
        patient = Patient(
            id=str(uuid.uuid4()),
            first_name="Jane",
            last_name="Smith",
            phone="5551234567",
            country_code="+1",
        )

        # Test formatted phone property returns correct US format
        expected_format = "+1 (555) 123-4567"
        assert patient.formatted_phone == expected_format

    def test_patient_us_formatted_phone_different_number(self):
        """Test US phone formatting with different number."""
        patient = Patient(
            id=str(uuid.uuid4()),
            first_name="Bob",
            last_name="Wilson",
            phone="2025551234",
            country_code="+1",
        )

        # Test formatted phone property returns correct US format
        expected_format = "+1 (202) 555-1234"
        assert patient.formatted_phone == expected_format

    def test_patient_default_country_code_is_us(self):
        """Test that default country code is US (+1)."""
        patient = Patient(
            id=str(uuid.uuid4()),
            first_name="Alice",
            last_name="Johnson",
            phone="3125559876",
            # No country_code provided - should default to +1
        )

        assert patient.country_code == "+1"
        assert patient.formatted_phone == "+1 (312) 555-9876"

    def test_patient_invalid_phone_length(self):
        """Test validation fails for invalid phone length."""
        with pytest.raises(ValueError, match="Phone must be exactly 10 digits"):
            Patient(
                id=str(uuid.uuid4()),
                first_name="Invalid",
                last_name="Phone",
                phone="555123456",  # Only 9 digits
                country_code="+1",
            )

    def test_patient_invalid_phone_non_digits(self):
        """Test validation fails for non-digit characters in phone."""
        with pytest.raises(ValueError, match="Phone must contain only digits"):
            Patient(
                id=str(uuid.uuid4()),
                first_name="Invalid",
                last_name="Phone",
                phone="555abc4567",  # Contains letters, exactly 10 chars
                country_code="+1",
            )

    def test_patient_invalid_country_code(self):
        """Test validation fails for unsupported country code."""
        with pytest.raises(ValueError, match="Unsupported country code"):
            Patient(
                id=str(uuid.uuid4()),
                first_name="Invalid",
                last_name="Country",
                phone="5551234567",
                country_code="+44",  # UK not supported
            )

    def test_patient_create_minimal_us(self):
        """Test creating minimal patient with US phone number."""
        patient = Patient.create_minimal(
            first_name="Test",
            last_name="Patient",
            phone="5551234567",
            country_code="+1",
        )

        assert patient.first_name == "Test"
        assert patient.last_name == "Patient"
        assert patient.phone == "5551234567"
        assert patient.country_code == "+1"
        assert patient.formatted_phone == "+1 (555) 123-4567"
        assert patient.id  # Should have an ID
        assert len(patient.id) > 0

    def test_patient_create_minimal_defaults_to_us(self):
        """Test creating minimal patient defaults to US country code."""
        patient = Patient.create_minimal(
            first_name="Test",
            last_name="Patient",
            phone="5551234567",
            # No country_code - should default to +1
        )

        assert patient.country_code == "+1"
        assert patient.formatted_phone == "+1 (555) 123-4567"

    def test_patient_full_name_property(self):
        """Test full_name property combines first and last names."""
        patient = Patient(
            id=str(uuid.uuid4()),
            first_name="John",
            last_name="Doe",
            phone="5551234567",
            country_code="+1",
        )

        assert patient.full_name == "John Doe"

    def test_patient_masked_phone_property(self):
        """Test masked_phone property shows only last 4 digits."""
        patient = Patient(
            id=str(uuid.uuid4()),
            first_name="John",
            last_name="Doe",
            phone="5551234567",
            country_code="+1",
        )

        assert patient.masked_phone == "+1 ***-4567"

    def test_patient_required_fields_validation(self):
        """Test validation of required fields."""
        # Test empty first name
        with pytest.raises(ValueError, match="First name is required"):
            Patient(
                id=str(uuid.uuid4()),
                first_name="",
                last_name="Doe",
                phone="5551234567",
                country_code="+1",
            )

        # Test empty last name
        with pytest.raises(ValueError, match="Last name is required"):
            Patient(
                id=str(uuid.uuid4()),
                first_name="John",
                last_name="",
                phone="5551234567",
                country_code="+1",
            )

    def test_patient_optional_fields(self):
        """Test patient with all optional fields set."""
        patient = Patient(
            id=str(uuid.uuid4()),
            first_name="John",
            last_name="Doe",
            phone="5551234567",
            country_code="+1",
            email="john.doe@example.com",
            birth_date=date(1990, 1, 1),
            address="123 Main St, Anytown USA",
            notes="Regular patient",
        )

        assert patient.email == "john.doe@example.com"
        assert patient.birth_date == date(1990, 1, 1)
        assert patient.address == "123 Main St, Anytown USA"
        assert patient.notes == "Regular patient"
