"""Unit tests for phone normalization utilities."""

import pytest

from src.utils.phone import format_phone_display, is_valid_phone, normalize_phone


class TestPhoneNormalization:
    """Test phone number normalization."""

    def test_normalize_phone_basic(self):
        """Test basic phone normalization."""
        assert normalize_phone("5551234567") == "5551234567"
        assert normalize_phone("555-123-4567") == "5551234567"
        assert normalize_phone("(555) 123-4567") == "5551234567"
        assert normalize_phone("555.123.4567") == "5551234567"
        assert normalize_phone(" 555 123 4567 ") == "5551234567"

    def test_normalize_phone_with_country_code(self):
        """Test phone normalization with country code."""
        assert normalize_phone("+1 555 123 4567") == "5551234567"
        assert normalize_phone("1-555-123-4567") == "5551234567"
        assert normalize_phone("15551234567") == "5551234567"

    def test_normalize_phone_invalid_length(self):
        """Test phone normalization with invalid lengths."""
        with pytest.raises(ValueError, match="too short"):
            normalize_phone("123456")  # Too short

        with pytest.raises(ValueError, match="too short"):
            normalize_phone("1234567")  # Still too short

        with pytest.raises(ValueError, match="too long"):
            normalize_phone("123456789012")  # 12 digits - definitely too long

    def test_normalize_phone_empty_or_none(self):
        """Test phone normalization with empty input."""
        with pytest.raises(ValueError, match="required"):
            normalize_phone("")

        with pytest.raises(ValueError, match="required"):
            normalize_phone("   ")

    def test_normalize_phone_various_formats(
        self, sample_phone_numbers, normalized_phone
    ):
        """Test normalization with various phone formats."""
        for phone in sample_phone_numbers:
            result = normalize_phone(phone)
            assert result == normalized_phone
            assert result.isdigit()

    def test_is_valid_phone(self):
        """Test phone validation without exceptions."""
        assert is_valid_phone("5551234567") is True
        assert is_valid_phone("555-123-4567") is True
        assert is_valid_phone("(555) 123-4567") is True
        assert is_valid_phone("+1 555 123 4567") is True

        assert is_valid_phone("") is False
        assert is_valid_phone("123456") is False  # Too short
        assert is_valid_phone("123456789012") is False  # Too long
        assert is_valid_phone("abc-def-ghij") is False  # No digits

    def test_format_phone_display(self):
        """Test phone formatting for display."""
        assert format_phone_display("5551234567") == "555-123-4567"
        assert format_phone_display("12345678") == "12345678"  # Non-standard length
        assert format_phone_display("123456789") == "123456789"  # Non-standard length


class TestPhoneEdgeCases:
    """Test edge cases in phone handling."""

    def test_normalize_phone_special_characters(self):
        """Test with various special characters."""
        assert normalize_phone("555*123#4567") == "5551234567"
        assert normalize_phone("555@123$4567") == "5551234567"
        assert normalize_phone("(555)-123.4567 ext 123") == "5551234567"

    def test_normalize_phone_international_formats(self):
        """Test international-style formats."""
        assert normalize_phone("+1-555-123-4567") == "5551234567"
        # Numbers without +1 prefix should be handled as regular numbers
        # or rejected if too long (001 is not a valid US area code pattern)

    def test_normalize_phone_minimum_valid(self):
        """Test minimum valid phone numbers."""
        assert normalize_phone("12345678") == "12345678"  # 8 digits (minimum)

        with pytest.raises(ValueError):
            normalize_phone("1234567")  # 7 digits (too short)
