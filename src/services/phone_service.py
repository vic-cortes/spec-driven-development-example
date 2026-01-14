"""Phone validation service for international phone number support."""

import re
from typing import Any, Dict, Optional

from src.models.phone_number import PhoneNumber
from src.services.logger import logger


class PhoneValidationResult:
    """Result of phone validation operation."""

    def __init__(
        self,
        is_valid: bool,
        error_message: Optional[str] = None,
        normalized_phone: Optional[str] = None,
        formatted_phone: Optional[str] = None,
    ):
        self.is_valid = is_valid
        self.error_message = error_message
        self.normalized_phone = normalized_phone
        self.formatted_phone = formatted_phone


class PhoneValidationService:
    """
    Service for validating and formatting international phone numbers.

    Supports US (+1) and Mexican (+52) phone numbers with strict validation
    and standardized formatting.
    """

    def __init__(self):
        """Initialize the phone validation service."""
        self.supported_countries = {
            "+1": {
                "name": "United States",
                "code": "US",
                "display_name": "+1 (US)",
                "pattern": r"^[0-9]{10}$",
                "format": "(XXX) XXX-XXXX",
            },
            "+52": {
                "name": "Mexico",
                "code": "MX",
                "display_name": "+52 (Mexico)",
                "pattern": r"^[0-9]{10}$",
                "format": "(XXX) XXX-XXXX",
            },
        }
        logger.info(
            "PhoneValidationService initialized with supported countries: +1, +52"
        )

    def validate_phone(
        self, country_code: str, phone_digits: str
    ) -> PhoneValidationResult:
        """
        Validate a phone number for a specific country code.

        Args:
            country_code: Country code for validation context ("+1" or "+52")
            phone_digits: Exactly 10 digits

        Returns:
            PhoneValidationResult: Validation result with error details if invalid
        """
        try:
            # Check if country code is supported
            if country_code not in self.supported_countries:
                return PhoneValidationResult(
                    is_valid=False,
                    error_message=f"Unsupported country code: {country_code}. Supported: +1, +52",
                )

            # Check if phone_digits is exactly 10 digits
            if phone_digits is None:
                return PhoneValidationResult(
                    is_valid=False,
                    error_message="Phone validation failed: phone cannot be None",
                )

            if not phone_digits or len(phone_digits) != 10:
                country_name = self.supported_countries[country_code]["name"]
                if country_code == "+52":
                    return PhoneValidationResult(
                        is_valid=False,
                        error_message=f"Mexican phone number must be exactly 10 digits (currently {len(phone_digits)} digits). Example: 551 234 5678",
                    )
                else:
                    return PhoneValidationResult(
                        is_valid=False,
                        error_message=f"US phone number must be exactly 10 digits (currently {len(phone_digits)} digits). Example: (555) 123-4567",
                    )

            # Check if all characters are digits
            if not phone_digits.isdigit():
                if country_code == "+52":
                    return PhoneValidationResult(
                        is_valid=False,
                        error_message="Mexican phone number must contain only digits 0-9. Example: 551 234 5678",
                    )
                else:
                    return PhoneValidationResult(
                        is_valid=False,
                        error_message="US phone number must contain only digits 0-9. Example: (555) 123-4567",
                    )

            # Validate against country pattern
            pattern = self.supported_countries[country_code]["pattern"]
            if not re.match(pattern, phone_digits):
                country_name = self.supported_countries[country_code]["name"]
                if country_code == "+52":
                    return PhoneValidationResult(
                        is_valid=False,
                        error_message=f"Invalid Mexican phone number format. Use 10 digits after +52. Example: +52 551 234 5678",
                    )
                else:
                    return PhoneValidationResult(
                        is_valid=False,
                        error_message=f"Invalid US phone number format. Use 10 digits after +1. Example: +1 (555) 123-4567",
                    )

            # Create phone number for additional validation
            phone_number = PhoneNumber.create(country_code, phone_digits)
            formatted = phone_number.format_display()

            logger.info(f"Phone validation successful: {phone_number.format_masked()}")

            return PhoneValidationResult(
                is_valid=True, normalized_phone=phone_digits, formatted_phone=formatted
            )

        except Exception as e:
            logger.error(f"Phone validation error: {str(e)}")
            return PhoneValidationResult(
                is_valid=False,
                error_message=f"Phone number validation failed: {str(e)}",
            )

    def format_phone(
        self, country_code: str, phone_digits: str, format_type: str = "full"
    ) -> str:
        """
        Format a validated phone number for display.

        Args:
            country_code: Country code ("+1" or "+52")
            phone_digits: 10-digit phone number
            format_type: "full" or "masked"

        Returns:
            str: Formatted phone number
        """
        try:
            # Validate inputs first
            validation_result = self.validate_phone(country_code, phone_digits)
            if not validation_result.is_valid:
                logger.warning(
                    f"Cannot format invalid phone: {validation_result.error_message}"
                )
                return f"{country_code} {phone_digits}"  # Return unformatted

            # Create phone number and format
            phone_number = PhoneNumber.create(country_code, phone_digits)

            if format_type == "masked":
                return phone_number.format_masked()
            else:
                return phone_number.format_display()

        except Exception as e:
            logger.error(f"Phone formatting error: {str(e)}")
            return f"{country_code} {phone_digits}"  # Fallback to basic format

    def parse_phone_input(self, raw_input: str) -> Dict[str, Any]:
        """
        Parse user input to extract digits and detect potential country.

        Args:
            raw_input: Raw user input with any formatting

        Returns:
            dict: Parsed components with keys:
                - digits: Extracted digits
                - suggested_country: Auto-detected country code if determinable
                - is_complete: Whether input has exactly 10 digits
        """
        try:
            result = PhoneNumber.parse_input(raw_input)

            # Log the parsing result (without PII)
            digits_masked = (
                result["digits"][-4:] if len(result["digits"]) >= 4 else "***"
            )
            logger.info(
                f"Parsed phone input: digits ending in {digits_masked}, "
                f"suggested country: {result['suggested_country']}, "
                f"complete: {result['is_complete']}"
            )

            return result

        except Exception as e:
            logger.error(f"Phone input parsing error: {str(e)}")
            return {"digits": "", "suggested_country": None, "is_complete": False}

    def get_supported_countries(self) -> Dict[str, Dict[str, str]]:
        """
        Get list of supported country codes.

        Returns:
            dict: Supported countries with display information
        """
        return self.supported_countries.copy()

    def is_country_supported(self, country_code: str) -> bool:
        """
        Check if a country code is supported.

        Args:
            country_code: Country code to check

        Returns:
            bool: True if supported, False otherwise
        """
        return country_code in self.supported_countries

    def normalize_phone_input(self, raw_input: str) -> str:
        """
        Extract only digits from phone input.

        Args:
            raw_input: Raw phone input with formatting

        Returns:
            str: Digits-only phone number
        """
        if raw_input is None:
            return ""
        if not isinstance(raw_input, str):
            return ""
        return re.sub(r"[^\d]", "", raw_input)


# Singleton instance for global use
phone_service = PhoneValidationService()
