"""Unit tests for phone service layer functionality."""

from unittest.mock import MagicMock, patch

import pytest

from src.services.phone_service import PhoneValidationResult, PhoneValidationService


class TestPhoneServiceLayerFunctionality:
    """Test phone service layer business logic."""

    def setup_method(self):
        """Set up test fixtures."""
        self.service = PhoneValidationService()

    def test_service_initialization(self):
        """Test service initializes with correct configuration."""
        assert self.service is not None
        countries = self.service.get_supported_countries()
        assert "+1" in countries
        assert "+52" in countries

    def test_service_singleton_behavior(self):
        """Test that phone_service imports as singleton instance."""
        from src.services.phone_service import phone_service

        assert phone_service is not None
        assert isinstance(phone_service, PhoneValidationService)

    def test_validation_result_dataclass(self):
        """Test PhoneValidationResult dataclass functionality."""
        result = PhoneValidationResult(
            is_valid=True,
            normalized_phone="5551234567",
            formatted_phone="+1 (555) 123-4567",
            error_message=None,
        )

        assert result.is_valid is True
        assert result.normalized_phone == "5551234567"
        assert result.formatted_phone == "+1 (555) 123-4567"
        assert result.error_message is None

    def test_validation_error_result(self):
        """Test PhoneValidationResult for error cases."""
        result = PhoneValidationResult(
            is_valid=False,
            normalized_phone=None,
            formatted_phone=None,
            error_message="Invalid phone number format",
        )

        assert result.is_valid is False
        assert result.normalized_phone is None
        assert result.formatted_phone is None
        assert result.error_message == "Invalid phone number format"

    def test_service_validate_phone_integration(self):
        """Test service validation integrates with PhoneNumber model."""
        result = self.service.validate_phone("+1", "5551234567")

        assert result.is_valid is True
        assert result.normalized_phone == "5551234567"
        assert result.formatted_phone == "+1 (555) 123-4567"
        assert result.error_message is None

    def test_service_validate_phone_error_integration(self):
        """Test service validation error handling."""
        result = self.service.validate_phone("+99", "5551234567")

        assert result.is_valid is False
        assert result.normalized_phone is None
        assert result.formatted_phone is None
        assert "Unsupported country code" in result.error_message

    def test_service_format_phone_integration(self):
        """Test service formatting integrates with PhoneNumber model."""
        formatted = self.service.format_phone("+1", "5551234567", "full")
        assert formatted == "+1 (555) 123-4567"

        formatted = self.service.format_phone("+1", "5551234567", "masked")
        assert formatted == "***-4567"

    def test_service_parse_phone_input_integration(self):
        """Test service parsing integrates with PhoneNumber model."""
        result = self.service.parse_phone_input("+1 (555) 123-4567")

        assert result["digits"] == "5551234567"
        assert result["suggested_country"] == "+1"
        assert result["is_complete"] is True

    def test_service_country_validation(self):
        """Test service country code validation logic."""
        assert self.service.is_country_supported("+1") is True
        assert self.service.is_country_supported("+52") is True
        assert self.service.is_country_supported("+33") is False
        assert self.service.is_country_supported("invalid") is False

    def test_service_error_handling_robustness(self):
        """Test service handles various error conditions gracefully."""
        # Test with None values
        result = self.service.validate_phone(None, "5551234567")
        assert result.is_valid is False

        result = self.service.validate_phone("+1", None)
        assert result.is_valid is False

        # Test with empty strings
        result = self.service.validate_phone("", "5551234567")
        assert result.is_valid is False

        result = self.service.validate_phone("+1", "")
        assert result.is_valid is False

    def test_service_formatting_fallbacks(self):
        """Test service formatting provides appropriate fallbacks."""
        # Test with invalid phone number
        formatted = self.service.format_phone("+1", "123", "full")
        assert formatted == "+1 123"  # Fallback format

        # Test with invalid country code
        formatted = self.service.format_phone("+99", "5551234567", "full")
        assert formatted == "+99 5551234567"  # Fallback format

    def test_service_normalization_functionality(self):
        """Test service phone input normalization."""
        # Test various input formats
        assert self.service.normalize_phone_input("+1 (555) 123-4567") == "15551234567"
        assert self.service.normalize_phone_input("+52-551.234.5678") == "525512345678"
        assert self.service.normalize_phone_input("555 123 4567") == "5551234567"
        assert self.service.normalize_phone_input("5551234567") == "5551234567"

    def test_service_supported_countries_structure(self):
        """Test service supported countries data structure."""
        countries = self.service.get_supported_countries()

        # Test US country data
        us_data = countries["+1"]
        assert us_data["name"] == "United States"
        assert us_data["code"] == "US"
        assert us_data["format"] == "(XXX) XXX-XXXX"

        # Test Mexican country data
        mx_data = countries["+52"]
        assert mx_data["name"] == "Mexico"
        assert mx_data["code"] == "MX"
        assert mx_data["format"] == "(XXX) XXX-XXXX"

    def test_service_validation_business_logic(self):
        """Test service validation business rules."""
        service = self.service

        # Test strict 10-digit validation for supported countries
        result = service.validate_phone("+1", "5551234567")  # Valid
        assert result.is_valid is True

        result = service.validate_phone("+1", "555123456")  # Too short
        assert result.is_valid is False

        result = service.validate_phone("+1", "55512345678")  # Too long
        assert result.is_valid is False

        # Test digit-only requirement
        result = service.validate_phone("+1", "555abc4567")  # Contains letters
        assert result.is_valid is False

    def test_service_input_parsing_business_logic(self):
        """Test service input parsing business rules."""
        service = self.service

        # Test country code detection from formatted input
        result = service.parse_phone_input("+1 (555) 123-4567")
        assert result["suggested_country"] == "+1"

        result = service.parse_phone_input("+52 551 234 5678")
        assert result["suggested_country"] == "+52"

        # Test digit sequence detection with leading country codes
        result = service.parse_phone_input("15551234567")  # US with leading 1
        assert result["suggested_country"] == "+1"
        assert result["digits"] == "5551234567"

        result = service.parse_phone_input("525512345678")  # Mexico with leading 52
        assert result["suggested_country"] == "+52"
        assert result["digits"] == "5512345678"

        # Test no suggestion for ambiguous cases
        result = service.parse_phone_input("5551234567")  # Could be US without +1
        assert result["suggested_country"] is None
        assert result["digits"] == "5551234567"


class TestPhoneServiceErrorHandling:
    """Test phone service error handling and edge cases."""

    def setup_method(self):
        """Set up test fixtures."""
        self.service = PhoneValidationService()

    def test_validation_exception_handling(self):
        """Test validation handles exceptions gracefully."""
        # Mock PhoneNumber.create to raise exception
        with patch("src.services.phone_service.PhoneNumber.create") as mock_create:
            mock_create.side_effect = Exception("Test exception")

            result = self.service.validate_phone("+1", "5551234567")

            assert result.is_valid is False
            assert "Phone number validation failed" in result.error_message

    def test_formatting_exception_handling(self):
        """Test formatting handles exceptions gracefully."""
        # Mock PhoneNumber.create to raise exception
        with patch("src.services.phone_service.PhoneNumber.create") as mock_create:
            mock_create.side_effect = Exception("Test exception")

            formatted = self.service.format_phone("+1", "5551234567", "full")

            assert formatted == "+1 5551234567"  # Fallback format

    def test_parsing_exception_handling(self):
        """Test parsing handles exceptions gracefully."""
        # Mock PhoneNumber.parse_input to raise exception
        with patch("src.services.phone_service.PhoneNumber.parse_input") as mock_parse:
            mock_parse.side_effect = Exception("Test exception")

            result = self.service.parse_phone_input("+1 (555) 123-4567")

            assert result["digits"] == ""
            assert result["suggested_country"] is None
            assert result["is_complete"] is False

    def test_normalization_exception_handling(self):
        """Test normalization handles exceptions gracefully."""
        # Test with various problematic inputs
        assert self.service.normalize_phone_input(None) == ""
        assert self.service.normalize_phone_input("") == ""

        # Test with non-string input
        assert self.service.normalize_phone_input(123) == ""

    def test_service_handles_malformed_input(self):
        """Test service handles malformed input gracefully."""
        # Test validation with various malformed inputs
        test_cases = [
            (None, None),
            ("", ""),
            ("+1", ""),
            ("", "5551234567"),
            ("invalid", "5551234567"),
            ("+1", "invalid"),
        ]

        for country_code, phone_digits in test_cases:
            result = self.service.validate_phone(country_code, phone_digits)
            assert result.is_valid is False
            assert result.error_message is not None

    def test_service_handles_formatting_edge_cases(self):
        """Test service handles formatting edge cases."""
        # Test formatting with various problematic inputs
        test_cases = [
            (None, None, "full"),
            ("", "", "full"),
            ("+1", None, "full"),
            (None, "5551234567", "full"),
            ("+1", "5551234567", "invalid_format"),
        ]

        for country_code, phone_digits, format_type in test_cases:
            formatted = self.service.format_phone(
                country_code, phone_digits, format_type
            )
            # Should return some fallback format, not crash
            assert isinstance(formatted, str)
            assert len(formatted) > 0


class TestPhoneServiceBusinessRules:
    """Test business rules and constraints for phone service."""

    def setup_method(self):
        """Set up test fixtures."""
        self.service = PhoneValidationService()

    def test_strict_validation_rules(self):
        """Test enforcement of strict validation rules."""
        # Exactly 10 digits required
        valid_cases = ["5551234567", "0001234567", "1111111111", "0000000000"]

        for digits in valid_cases:
            result = self.service.validate_phone("+1", digits)
            assert result.is_valid is True, f"Failed for valid case: {digits}"

        # Invalid cases
        invalid_cases = [
            "555123456",  # 9 digits
            "55512345678",  # 11 digits
            "555",  # 3 digits
            "12345678901234567890",  # 20 digits
        ]

        for digits in invalid_cases:
            result = self.service.validate_phone("+1", digits)
            assert result.is_valid is False, f"Should fail for invalid case: {digits}"

    def test_supported_country_constraints(self):
        """Test supported country code constraints."""
        # Only +1 and +52 supported
        supported = ["+1", "+52"]
        unsupported = ["+33", "+44", "+49", "+81", "+86"]

        for country_code in supported:
            result = self.service.validate_phone(country_code, "5551234567")
            assert result.is_valid is True, f"Should support {country_code}"

        for country_code in unsupported:
            result = self.service.validate_phone(country_code, "5551234567")
            assert result.is_valid is False, f"Should not support {country_code}"

    def test_format_consistency_rules(self):
        """Test formatting consistency across different inputs."""
        # Same phone number should format consistently
        test_phone = "5551234567"

        us_format = self.service.format_phone("+1", test_phone, "full")
        mx_format = self.service.format_phone("+52", test_phone, "full")

        # Should have same internal structure but different country codes
        assert us_format.startswith("+1")
        assert mx_format.startswith("+52")
        assert "(555) 123-4567" in us_format
        assert "(555) 123-4567" in mx_format

    def test_parsing_consistency_rules(self):
        """Test parsing consistency across different formats."""
        # Different input formats for same number should parse consistently
        test_inputs = [
            "+1 (555) 123-4567",
            "+1-555-123-4567",
            "+1.555.123.4567",
            "+1 555 123 4567",
            "15551234567",
        ]

        expected_digits = "5551234567"
        expected_country = "+1"

        for input_format in test_inputs:
            result = self.service.parse_phone_input(input_format)
            assert (
                result["digits"] == expected_digits
            ), f"Parsing failed for: {input_format}"
            assert (
                result["suggested_country"] == expected_country
            ), f"Country detection failed for: {input_format}"

    def test_privacy_masking_rules(self):
        """Test privacy masking follows consistent rules."""
        # All masked formats should hide first 6 digits, show last 4
        test_cases = [("+1", "5551234567"), ("+52", "5512345678")]

        for country_code, digits in test_cases:
            masked = self.service.format_phone(country_code, digits, "masked")
            assert (
                masked == "***-" + digits[-4:]
            ), f"Masking rule violation for {country_code} {digits}"
