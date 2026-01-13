"""Unit tests for international phone validation."""

from unittest.mock import patch

import pytest

from src.models.phone_number import PhoneNumber
from src.services.phone_service import PhoneValidationResult, phone_service


class TestPhoneNumberEntity:
    """Test the PhoneNumber entity class."""

    def test_create_valid_us_phone(self):
        """Test creating a valid US phone number."""
        phone = PhoneNumber.create("+1", "5551234567")

        assert phone.country_code == "+1"
        assert phone.digits == "5551234567"
        assert phone.validate() is True
        assert phone.is_valid() is True

    def test_create_valid_mexican_phone(self):
        """Test creating a valid Mexican phone number."""
        phone = PhoneNumber.create("+52", "5512345678")

        assert phone.country_code == "+52"
        assert phone.digits == "5512345678"
        assert phone.validate() is True
        assert phone.is_valid() is True

    def test_format_display_us_phone(self):
        """Test US phone number display formatting."""
        phone = PhoneNumber.create("+1", "5551234567")
        formatted = phone.format_display()

        assert formatted == "+1 (555) 123-4567"

    def test_format_display_mexican_phone(self):
        """Test Mexican phone number display formatting."""
        phone = PhoneNumber.create("+52", "5512345678")
        formatted = phone.format_display()

        assert formatted == "+52 (551) 234-5678"

    def test_format_masked_phone(self):
        """Test phone number privacy masking."""
        phone = PhoneNumber.create("+1", "5551234567")
        masked = phone.format_masked()

        assert masked == "***-4567"

    def test_invalid_country_code(self):
        """Test phone creation with invalid country code."""
        with pytest.raises(ValueError, match="Invalid phone number"):
            PhoneNumber.create("+33", "5551234567")  # France not supported

    def test_invalid_phone_length_short(self):
        """Test phone creation with too few digits."""
        with pytest.raises(ValueError, match="Invalid phone number"):
            PhoneNumber.create("+1", "12345")

    def test_invalid_phone_length_long(self):
        """Test phone creation with too many digits."""
        with pytest.raises(ValueError, match="Invalid phone number"):
            PhoneNumber.create("+1", "123456789012")

    def test_invalid_phone_non_digits(self):
        """Test phone creation with non-digit characters."""
        with pytest.raises(ValueError, match="Invalid phone number"):
            PhoneNumber.create("+1", "555abc4567")

    def test_parse_input_us_with_country_code(self):
        """Test parsing US input with explicit country code."""
        result = PhoneNumber.parse_input("+1 (555) 123-4567")

        assert result["digits"] == "5551234567"
        assert result["suggested_country"] == "+1"
        assert result["is_complete"] is True

    def test_parse_input_mexican_with_country_code(self):
        """Test parsing Mexican input with explicit country code."""
        result = PhoneNumber.parse_input("+52 551 234 5678")

        assert result["digits"] == "5512345678"
        assert result["suggested_country"] == "+52"
        assert result["is_complete"] is True

    def test_parse_input_no_country_code(self):
        """Test parsing input without country code."""
        result = PhoneNumber.parse_input("(555) 123-4567")

        assert result["digits"] == "5551234567"
        assert result["suggested_country"] is None
        assert result["is_complete"] is True

    def test_parse_input_incomplete(self):
        """Test parsing incomplete input."""
        result = PhoneNumber.parse_input("555-123")

        assert result["digits"] == "555123"
        assert result["suggested_country"] is None
        assert result["is_complete"] is False


class TestPhoneValidationService:
    """Test the PhoneValidationService class."""

    def test_validate_valid_us_phone(self):
        """Test validation of valid US phone number."""
        result = phone_service.validate_phone("+1", "5551234567")

        assert result.is_valid is True
        assert result.error_message is None
        assert result.normalized_phone == "5551234567"
        assert result.formatted_phone == "+1 (555) 123-4567"

    def test_validate_valid_mexican_phone(self):
        """Test validation of valid Mexican phone number."""
        result = phone_service.validate_phone("+52", "5512345678")

        assert result.is_valid is True
        assert result.error_message is None
        assert result.normalized_phone == "5512345678"
        assert result.formatted_phone == "+52 (551) 234-5678"

    def test_validate_invalid_country_code(self):
        """Test validation with unsupported country code."""
        result = phone_service.validate_phone("+33", "5551234567")

        assert result.is_valid is False
        assert "Unsupported country code" in result.error_message
        assert "+1, +52" in result.error_message

    def test_validate_invalid_phone_length_short(self):
        """Test validation with too few digits."""
        result = phone_service.validate_phone("+1", "12345")

        assert result.is_valid is False
        assert "must be exactly 10 digits" in result.error_message

    def test_validate_invalid_phone_length_long(self):
        """Test validation with too many digits."""
        result = phone_service.validate_phone("+1", "123456789012")

        assert result.is_valid is False
        assert "must be exactly 10 digits" in result.error_message

    def test_validate_invalid_phone_non_digits(self):
        """Test validation with non-digit characters."""
        result = phone_service.validate_phone("+1", "555abc4567")

        assert result.is_valid is False
        assert "must contain only digits" in result.error_message

    def test_validate_empty_phone(self):
        """Test validation with empty phone number."""
        result = phone_service.validate_phone("+1", "")

        assert result.is_valid is False
        assert "must be exactly 10 digits" in result.error_message

    def test_format_phone_full_us(self):
        """Test full formatting of US phone number."""
        formatted = phone_service.format_phone("+1", "5551234567", "full")

        assert formatted == "+1 (555) 123-4567"

    def test_format_phone_full_mexican(self):
        """Test full formatting of Mexican phone number."""
        formatted = phone_service.format_phone("+52", "5512345678", "full")

        assert formatted == "+52 (551) 234-5678"

    def test_format_phone_masked(self):
        """Test masked formatting of phone number."""
        formatted = phone_service.format_phone("+1", "5551234567", "masked")

        assert formatted == "***-4567"

    def test_format_invalid_phone_fallback(self):
        """Test formatting of invalid phone returns fallback."""
        formatted = phone_service.format_phone("+1", "123", "full")

        assert formatted == "+1 123"  # Fallback format

    def test_parse_phone_input_formatted_us(self):
        """Test parsing formatted US phone input."""
        result = phone_service.parse_phone_input("+1 (555) 123-4567")

        assert result["digits"] == "5551234567"
        assert result["suggested_country"] == "+1"
        assert result["is_complete"] is True

    def test_parse_phone_input_formatted_mexican(self):
        """Test parsing formatted Mexican phone input."""
        result = phone_service.parse_phone_input("+52 551-234-5678")

        assert result["digits"] == "5512345678"
        assert result["suggested_country"] == "+52"
        assert result["is_complete"] is True

    def test_parse_phone_input_digits_only(self):
        """Test parsing digits-only phone input."""
        result = phone_service.parse_phone_input("5551234567")

        assert result["digits"] == "5551234567"
        assert result["suggested_country"] is None
        assert result["is_complete"] is True

    def test_parse_phone_input_with_leading_one(self):
        """Test parsing phone input with leading 1 (US format)."""
        result = phone_service.parse_phone_input("15551234567")

        assert result["digits"] == "5551234567"
        assert result["suggested_country"] == "+1"
        assert result["is_complete"] is True

    def test_parse_phone_input_with_leading_52(self):
        """Test parsing phone input with leading 52 (Mexican format)."""
        result = phone_service.parse_phone_input("525512345678")

        assert result["digits"] == "5512345678"
        assert result["suggested_country"] == "+52"
        assert result["is_complete"] is True

    def test_parse_phone_input_incomplete(self):
        """Test parsing incomplete phone input."""
        result = phone_service.parse_phone_input("555-123")

        assert result["digits"] == "555123"
        assert result["suggested_country"] is None
        assert result["is_complete"] is False

    def test_get_supported_countries(self):
        """Test getting supported country codes."""
        countries = phone_service.get_supported_countries()

        assert "+1" in countries
        assert "+52" in countries
        assert countries["+1"]["name"] == "United States"
        assert countries["+52"]["name"] == "Mexico"

    def test_is_country_supported(self):
        """Test country code support checking."""
        assert phone_service.is_country_supported("+1") is True
        assert phone_service.is_country_supported("+52") is True
        assert phone_service.is_country_supported("+33") is False

    def test_normalize_phone_input(self):
        """Test phone input normalization."""
        normalized = phone_service.normalize_phone_input("+1 (555) 123-4567")

        assert normalized == "15551234567"

    def test_normalize_phone_input_complex_formatting(self):
        """Test normalization with complex formatting."""
        normalized = phone_service.normalize_phone_input("+52-551.234.5678")

        assert normalized == "525512345678"


class TestPhoneValidationEdgeCases:
    """Test edge cases and error conditions for phone validation."""

    def test_validation_service_exception_handling(self):
        """Test validation service handles exceptions gracefully."""
        # Test with None input
        result = phone_service.validate_phone("+1", None)
        assert result.is_valid is False
        assert "validation failed" in result.error_message

    def test_formatting_service_exception_handling(self):
        """Test formatting service handles exceptions gracefully."""
        # Test with None input
        formatted = phone_service.format_phone("+1", None, "full")
        assert formatted == "+1 None"  # Fallback format

    def test_parsing_service_exception_handling(self):
        """Test parsing service handles exceptions gracefully."""
        # Test with None input
        result = phone_service.parse_phone_input(None)
        assert result["digits"] == ""
        assert result["suggested_country"] is None
        assert result["is_complete"] is False

    def test_phone_number_string_representation(self):
        """Test phone number string representations."""
        phone = PhoneNumber.create("+1", "5551234567")

        assert str(phone) == "+1 (555) 123-4567"
        assert repr(phone) == "PhoneNumber(country_code='+1', digits='5551234567')"

    def test_phone_number_validation_edge_cases(self):
        """Test phone number validation with edge cases."""
        # Test with leading zeros
        phone = PhoneNumber.create("+1", "0001234567")
        assert phone.validate() is True

        # Test with all same digits
        phone = PhoneNumber.create("+1", "1111111111")
        assert phone.validate() is True

        # Test with all zeros
        phone = PhoneNumber.create("+1", "0000000000")
        assert phone.validate() is True

    def test_format_display_invalid_phone(self):
        """Test display formatting of invalid phone number."""
        # Create phone with invalid data (bypassing normal validation)
        phone = PhoneNumber("+1", "123", "+1 123")
        formatted = phone.format_display()

        # Should return unformatted for invalid phones
        assert formatted == "+1 123"
