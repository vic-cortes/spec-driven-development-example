"""Phone number entity with international support."""

import re
from dataclasses import dataclass
from typing import Optional


@dataclass
class PhoneNumber:
    """
    Represents a phone number with international country code support.

    Supports US (+1) and Mexican (+52) phone numbers with strict validation
    and standardized formatting.
    """

    country_code: str  # "+1" or "+52"
    digits: str  # exactly 10 digits
    raw_input: str  # original user input for auditing

    # Validation patterns for supported countries
    SUPPORTED_COUNTRIES = {
        "+1": {"name": "United States", "pattern": r"^[0-9]{10}$"},
        "+52": {"name": "Mexico", "pattern": r"^[0-9]{10}$"},
    }

    def __post_init__(self):
        """Validate phone number data after initialization."""
        if not self.validate():
            raise ValueError(f"Invalid phone number: {self.country_code} {self.digits}")

    def validate(self) -> bool:
        """
        Validate the phone number format and country code.

        Returns:
            bool: True if phone number is valid, False otherwise
        """
        # Check if country code is supported
        if self.country_code not in self.SUPPORTED_COUNTRIES:
            return False

        # Check if digits match the country's pattern
        pattern = self.SUPPORTED_COUNTRIES[self.country_code]["pattern"]
        if not re.match(pattern, self.digits):
            return False

        # Ensure digits are exactly 10 characters
        if len(self.digits) != 10:
            return False

        # Ensure all characters are digits
        if not self.digits.isdigit():
            return False

        return True

    def format_display(self) -> str:
        """
        Format phone number for display as "+{code} (xxx) xxx-xxxx".

        Returns:
            str: Formatted phone number

        Example:
            "+1 (555) 123-4567"
            "+52 (551) 234-5678"
        """
        if not self.validate():
            return f"{self.country_code} {self.digits}"  # Return unformatted if invalid

        # Format as: +country_code (area) exchange-number
        area = self.digits[:3]
        exchange = self.digits[3:6]
        number = self.digits[6:]

        return f"{self.country_code} ({area}) {exchange}-{number}"

    def format_masked(self) -> str:
        """
        Format phone number with privacy masking for display.

        Returns:
            str: Masked phone number showing only last 4 digits

        Example:
            "***-4567"
        """
        if len(self.digits) < 4:
            return "***"

        last_four = self.digits[-4:]
        return f"***-{last_four}"

    def is_valid(self) -> bool:
        """
        Check if the phone number is valid.

        Returns:
            bool: True if valid, False otherwise
        """
        return self.validate()

    @classmethod
    def create(
        cls, country_code: str, digits: str, raw_input: Optional[str] = None
    ) -> "PhoneNumber":
        """
        Create a PhoneNumber instance with validation.

        Args:
            country_code: Country code ("+1" or "+52")
            digits: Phone number digits (must be exactly 10 digits)
            raw_input: Original user input for auditing (optional)

        Returns:
            PhoneNumber: Validated phone number instance

        Raises:
            ValueError: If phone number is invalid
        """
        if raw_input is None:
            raw_input = f"{country_code} {digits}"

        return cls(country_code=country_code, digits=digits, raw_input=raw_input)

    @classmethod
    def parse_input(cls, raw_input: str) -> dict:
        """
        Parse user input to extract phone number components.

        Args:
            raw_input: Raw user input with any formatting

        Returns:
            dict: Parsed components with keys:
                - digits: Extracted digits
                - suggested_country: Auto-detected country code if determinable
                - is_complete: Whether input has exactly 10 digits
        """
        # Remove all non-digit characters
        digits = re.sub(r"[^\d]", "", raw_input)

        # Check for country code prefixes
        suggested_country = None
        if raw_input.startswith("+1") or raw_input.startswith("1"):
            suggested_country = "+1"
        elif raw_input.startswith("+52") or raw_input.startswith("52"):
            suggested_country = "+52"

        # If we detected a country prefix, remove it from digits
        if suggested_country == "+1" and digits.startswith("1") and len(digits) == 11:
            digits = digits[1:]  # Remove leading 1 for US numbers
        elif (
            suggested_country == "+52" and digits.startswith("52") and len(digits) == 12
        ):
            digits = digits[2:]  # Remove leading 52 for Mexican numbers

        return {
            "digits": digits,
            "suggested_country": suggested_country,
            "is_complete": len(digits) == 10,
        }

    def __str__(self) -> str:
        """String representation of the phone number."""
        return self.format_display()

    def __repr__(self) -> str:
        """Developer representation of the phone number."""
        return (
            f"PhoneNumber(country_code='{self.country_code}', digits='{self.digits}')"
        )
