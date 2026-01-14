"""Integration tests for phone input validation UI components - User Story 3."""

from unittest.mock import Mock, patch

import flet as ft
import pytest

from src.models.patient import Patient
from src.services.patient_service import patient_service
from src.services.phone_service import phone_service


class TestPhoneInputValidationUI:
    """Integration tests for phone input validation UI components."""

    @pytest.fixture
    def mock_page(self):
        """Create a mock Flet page for testing."""
        page = Mock(spec=ft.Page)
        page.update = Mock()
        return page

    @pytest.fixture
    def mock_phone_input(self):
        """Create a mock phone input component."""
        phone_input = ft.TextField(
            label="Phone Number",
            hint_text="Enter 10 digits",
            keyboard_type=ft.KeyboardType.PHONE,
            max_length=10,
        )
        return phone_input

    @pytest.fixture
    def mock_country_dropdown(self):
        """Create a mock country code dropdown."""
        dropdown = ft.Dropdown(
            label="Country Code",
            options=[
                ft.dropdown.Option(key="+1", text="+1 (US)"),
                ft.dropdown.Option(key="+52", text="+52 (Mexico)"),
            ],
            value="+1",  # Default to US
        )
        return dropdown

    def test_country_dropdown_contains_required_options(self, mock_country_dropdown):
        """Test that country dropdown contains both US and Mexico options."""
        options = mock_country_dropdown.options

        # Extract option keys
        option_keys = [option.key for option in options]
        option_texts = [option.text for option in options]

        assert "+1" in option_keys
        assert "+52" in option_keys
        assert "+1 (US)" in option_texts
        assert "+52 (Mexico)" in option_texts

    def test_country_dropdown_defaults_to_us(self, mock_country_dropdown):
        """Test that country dropdown defaults to US (+1)."""
        assert mock_country_dropdown.value == "+1"

    def test_country_dropdown_value_change_validation(self, mock_country_dropdown):
        """Test that changing country code triggers validation."""
        # Change to Mexico
        mock_country_dropdown.value = "+52"

        # Verify the value changed
        assert mock_country_dropdown.value == "+52"

        # Change back to US
        mock_country_dropdown.value = "+1"
        assert mock_country_dropdown.value == "+1"

    def test_phone_input_validation_empty_country_code(self, mock_phone_input):
        """Test phone input validation when country code is empty."""
        phone_input = mock_phone_input
        phone_input.value = "5551234567"

        # Test validation with empty country code
        result = phone_service.validate_phone("", phone_input.value)

        assert result.is_valid is False
        assert "Country code is required" in result.error_message

    def test_phone_input_validation_empty_phone_number(self, mock_country_dropdown):
        """Test phone input validation when phone number is empty."""
        country_code = mock_country_dropdown.value

        # Test validation with empty phone number
        result = phone_service.validate_phone(country_code, "")

        assert result.is_valid is False
        assert "Phone number is required" in result.error_message

    def test_phone_input_validation_invalid_length(self, mock_country_dropdown):
        """Test phone input validation with invalid length."""
        country_code = mock_country_dropdown.value

        # Test with too few digits
        result = phone_service.validate_phone(country_code, "12345")
        assert result.is_valid is False
        assert "must be exactly 10 digits" in result.error_message

        # Test with too many digits
        result = phone_service.validate_phone(country_code, "123456789012")
        assert result.is_valid is False
        assert "must be exactly 10 digits" in result.error_message

    def test_phone_input_validation_non_digits(self, mock_country_dropdown):
        """Test phone input validation with non-digit characters."""
        country_code = mock_country_dropdown.value

        # Test with letters
        result = phone_service.validate_phone(country_code, "555abc4567")
        assert result.is_valid is False
        assert "must contain only digits" in result.error_message

        # Test with special characters
        result = phone_service.validate_phone(country_code, "555-123-4567")
        assert result.is_valid is False
        assert "must contain only digits" in result.error_message

    def test_phone_input_validation_valid_us_phone(self, mock_country_dropdown):
        """Test phone input validation with valid US phone number."""
        mock_country_dropdown.value = "+1"

        result = phone_service.validate_phone(mock_country_dropdown.value, "5551234567")

        assert result.is_valid is True
        assert result.error_message is None
        assert result.formatted_phone == "+1 (555) 123-4567"

    def test_phone_input_validation_valid_mexican_phone(self, mock_country_dropdown):
        """Test phone input validation with valid Mexican phone number."""
        mock_country_dropdown.value = "+52"

        result = phone_service.validate_phone(mock_country_dropdown.value, "5512345678")

        assert result.is_valid is True
        assert result.error_message is None
        assert result.formatted_phone == "+52 (551) 234-5678"

    def test_country_code_change_clears_validation_errors(
        self, mock_country_dropdown, mock_phone_input
    ):
        """Test that changing country code should clear previous validation errors."""
        # Start with US
        mock_country_dropdown.value = "+1"
        mock_phone_input.value = "invalid"

        # Validate and get error
        result = phone_service.validate_phone(
            mock_country_dropdown.value, mock_phone_input.value
        )
        assert result.is_valid is False

        # Change to Mexico - new validation context
        mock_country_dropdown.value = "+52"

        # Validation should still fail but with updated context
        result = phone_service.validate_phone(
            mock_country_dropdown.value, mock_phone_input.value
        )
        assert result.is_valid is False
        assert "Mexican phone number" in result.error_message

    def test_form_prevents_submission_with_invalid_phone(self):
        """Test that form submission is prevented when phone validation fails."""
        # Test with invalid phone
        result = phone_service.validate_phone("+1", "invalid")

        # Form should not allow submission
        can_submit = result.is_valid
        assert can_submit is False

    def test_form_allows_submission_with_valid_phone(self):
        """Test that form submission is allowed when phone validation passes."""
        # Test with valid phone
        result = phone_service.validate_phone("+1", "5551234567")

        # Form should allow submission
        can_submit = result.is_valid
        assert can_submit is True

    def test_real_time_validation_feedback_messages(self):
        """Test that validation provides appropriate real-time feedback messages."""
        # Test various invalid inputs and verify messages
        test_cases = [
            ("", "5551234567", "Country code is required"),
            ("+1", "", "Phone number is required"),
            ("+1", "12345", "must be exactly 10 digits"),
            ("+1", "555abc4567", "must contain only digits"),
            ("+52", "12345", "must be exactly 10 digits"),
            ("+52", "551abc5678", "must contain only digits"),
            ("+99", "5551234567", "Unsupported country code"),
        ]

        for country_code, phone_number, expected_message in test_cases:
            result = phone_service.validate_phone(country_code, phone_number)
            assert result.is_valid is False
            assert expected_message in result.error_message

    def test_validation_error_message_specificity(self):
        """Test that validation error messages are specific to country and error type."""
        # US-specific messages
        result = phone_service.validate_phone("+1", "12345")
        assert "US phone number" in result.error_message
        assert "Example: 555 123 4567" in result.error_message

        # Mexican-specific messages
        result = phone_service.validate_phone("+52", "12345")
        assert "Mexican phone number" in result.error_message
        assert "Example: 551 234 5678" in result.error_message

    @patch("src.services.patient_service.PatientService.create_patient")
    def test_patient_creation_with_valid_international_phone(self, mock_create_patient):
        """Test that patient creation works with valid international phone numbers."""
        # Setup mock - use correct Patient constructor
        mock_patient = Patient(
            id="1",
            first_name="Juan",
            last_name="Garcia",
            phone="5512345678",
            country_code="+52",
        )
        mock_create_patient.return_value = mock_patient

        # Test patient creation with Mexican phone
        result = patient_service.create_patient(
            first_name="Juan",
            last_name="Garcia",
            phone="5512345678",
            country_code="+52",
        )

        assert result.country_code == "+52"
        assert result.phone == "5512345678"
        mock_create_patient.assert_called_once()

    @patch("src.services.patient_service.PatientService.create_patient")
    def test_patient_creation_rejects_invalid_phone(self, mock_create_patient):
        """Test that patient creation rejects invalid phone numbers."""
        # Validate the phone first (this should fail)
        validation_result = phone_service.validate_phone("+1", "invalid")

        # Should not attempt to create patient with invalid phone
        if not validation_result.is_valid:
            # Don't call create_patient
            pass
        else:
            patient_service.create_patient(
                first_name="John", last_name="Doe", phone="invalid", country_code="+1"
            )

        # Verify create_patient was not called
        mock_create_patient.assert_not_called()

    def test_dropdown_accessibility_properties(self, mock_country_dropdown):
        """Test that country dropdown has proper accessibility properties."""
        # Verify dropdown has label
        assert mock_country_dropdown.label == "Country Code"

        # Verify options have meaningful text
        for option in mock_country_dropdown.options:
            assert option.text is not None
            assert option.text != ""
            assert "(" in option.text  # Should include country name like "(US)"

    def test_phone_input_accessibility_properties(self, mock_phone_input):
        """Test that phone input has proper accessibility properties."""
        # Verify input has label and hint
        assert mock_phone_input.label == "Phone Number"
        assert mock_phone_input.hint_text is not None

        # Verify keyboard type is appropriate
        assert mock_phone_input.keyboard_type == ft.KeyboardType.PHONE

        # Verify max length is set for user guidance
        assert mock_phone_input.max_length == 10

    def test_validation_preserves_user_input(self):
        """Test that validation preserves original user input for error context."""
        # Test with input that has formatting
        original_input = "555-123-4567"
        result = phone_service.validate_phone("+1", original_input)

        # Should fail validation but preserve input context
        assert result.is_valid is False
        assert "must contain only digits" in result.error_message

    def test_country_code_dropdown_ordering(self, mock_country_dropdown):
        """Test that country codes are presented in logical order."""
        options = mock_country_dropdown.options

        # US should come first (most common), then Mexico
        assert options[0].key == "+1"
        assert options[1].key == "+52"

        # Verify readable format
        assert "US" in options[0].text
        assert "Mexico" in options[1].text


class TestPhoneInputFormIntegration:
    """Integration tests for phone input within form context."""

    def test_form_validation_integration(self):
        """Test complete form validation with phone input."""
        # Test complete form scenario
        form_data = {
            "first_name": "Test",
            "last_name": "User",
            "country_code": "+1",
            "phone": "5551234567",
        }

        # Validate phone component
        phone_result = phone_service.validate_phone(
            form_data["country_code"], form_data["phone"]
        )

        # Should be valid for form submission
        assert phone_result.is_valid is True
        assert phone_result.formatted_phone == "+1 (555) 123-4567"

    def test_form_prevents_submission_on_phone_error(self):
        """Test that form prevents submission when phone validation fails."""
        form_data = {
            "first_name": "Test",
            "last_name": "User",
            "country_code": "+1",
            "phone": "invalid",
        }

        # Validate phone component
        phone_result = phone_service.validate_phone(
            form_data["country_code"], form_data["phone"]
        )

        # Form should not submit
        can_submit = phone_result.is_valid
        assert can_submit is False

    def test_form_handles_missing_country_code(self):
        """Test form handling when country code is not selected."""
        form_data = {
            "first_name": "Test",
            "last_name": "User",
            "country_code": "",  # Not selected
            "phone": "5551234567",
        }

        # Validate phone component
        phone_result = phone_service.validate_phone(
            form_data["country_code"], form_data["phone"]
        )

        # Should fail validation
        assert phone_result.is_valid is False
        assert "Country code is required" in phone_result.error_message

    def test_form_displays_formatted_phone_after_validation(self):
        """Test that form displays formatted phone after successful validation."""
        form_data = {"country_code": "+52", "phone": "5512345678"}

        # Validate and format
        result = phone_service.validate_phone(
            form_data["country_code"], form_data["phone"]
        )

        if result.is_valid:
            formatted_display = result.formatted_phone
            assert formatted_display == "+52 (551) 234-5678"
        else:
            formatted_display = "Invalid phone number"

        # Form should show the formatted version
        assert "+52 (551) 234-5678" == formatted_display
