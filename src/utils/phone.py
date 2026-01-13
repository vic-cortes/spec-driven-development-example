"""Phone number normalization utilities with international support."""

import re
from typing import Optional, Tuple

from src.services.phone_service import phone_service


def normalize_phone(phone: str) -> str:
    """
    Normalize a phone number to digits-only format.

    LEGACY FUNCTION: Maintains backward compatibility.
    For new international phone support, use normalize_international_phone().

    Args:
        phone: Input phone number in any format

    Returns:
        Digits-only phone number

    Raises:
        ValueError: If phone is invalid or too short
    """
    if not phone or not phone.strip():
        raise ValueError("Phone number is required")

    # Remove all non-digit characters, but handle extensions by stopping at first extension keyword
    cleaned = phone.strip()
    for ext_keyword in [" ext ", " extension ", " x "]:
        if ext_keyword in cleaned.lower():
            cleaned = cleaned.split(ext_keyword)[0]

    digits_only = re.sub(r"[^\d]", "", cleaned)

    # Handle country code (assume +1 for US numbers)
    if digits_only.startswith("1") and len(digits_only) == 11:
        digits_only = digits_only[1:]  # Remove country code

    # Validate length
    if len(digits_only) < 8:
        raise ValueError(
            f"Phone number too short: {len(digits_only)} digits (minimum 8)"
        )

    if len(digits_only) > 10:
        raise ValueError(
            f"Phone number too long: {len(digits_only)} digits (maximum 10)"
        )

    return digits_only


def normalize_international_phone(
    phone: str, country_code: Optional[str] = None
) -> Tuple[str, str]:
    """
    Normalize an international phone number to digits-only format with country code.

    Args:
        phone: Input phone number in any format
        country_code: Explicit country code ("+1" or "+52"), if None will attempt auto-detection

    Returns:
        Tuple of (country_code, digits_only)

    Raises:
        ValueError: If phone is invalid or country code not supported
    """
    if not phone or not phone.strip():
        raise ValueError("Phone number is required")

    # Parse the input to extract components
    parsed = phone_service.parse_phone_input(phone)

    # Determine country code
    final_country_code = country_code or parsed.get("suggested_country", "+1")

    if not final_country_code:
        final_country_code = "+1"  # Default to US

    # Validate the phone number
    validation_result = phone_service.validate_phone(
        final_country_code, parsed["digits"]
    )

    if not validation_result.is_valid:
        raise ValueError(f"Invalid phone number: {validation_result.error_message}")

    return final_country_code, parsed["digits"]


def is_valid_phone(phone: str) -> bool:
    """
    Check if a phone number is valid without raising exceptions.

    LEGACY FUNCTION: Maintains backward compatibility.
    For new international phone support, use is_valid_international_phone().

    Args:
        phone: Input phone number

    Returns:
        True if phone is valid, False otherwise
    """
    try:
        normalize_phone(phone)
        return True
    except ValueError:
        return False


def is_valid_international_phone(
    phone: str, country_code: Optional[str] = None
) -> bool:
    """
    Check if an international phone number is valid without raising exceptions.

    Args:
        phone: Input phone number
        country_code: Explicit country code ("+1" or "+52"), if None will attempt auto-detection

    Returns:
        True if phone is valid, False otherwise
    """
    try:
        normalize_international_phone(phone, country_code)
        return True
    except ValueError:
        return False


def format_phone_display(phone: str) -> str:
    """
    Format a normalized phone number for display.

    LEGACY FUNCTION: Maintains backward compatibility.
    For new international phone support, use format_international_phone_display().

    Args:
        phone: Normalized phone number (digits only)

    Returns:
        Formatted phone number (e.g., "555-123-4567")
    """
    if len(phone) == 10:
        return f"{phone[:3]}-{phone[3:6]}-{phone[6:]}"
    else:
        return phone  # Return as-is for non-standard lengths


def format_international_phone_display(country_code: str, phone_digits: str) -> str:
    """
    Format an international phone number for display.

    Args:
        country_code: Country code ("+1" or "+52")
        phone_digits: Normalized phone number (digits only)

    Returns:
        Formatted international phone number (e.g., "+1 (555) 123-4567")
    """
    return phone_service.format_phone(country_code, phone_digits, "full")


def mask_phone_display(phone: str) -> str:
    """
    Format a phone number with privacy masking.

    LEGACY FUNCTION: Maintains backward compatibility.
    For new international phone support, use mask_international_phone_display().

    Args:
        phone: Normalized phone number (digits only)

    Returns:
        Masked phone number (e.g., "***-4567")
    """
    if len(phone) >= 4:
        return f"***-{phone[-4:]}"
    else:
        return "***"


def mask_international_phone_display(country_code: str, phone_digits: str) -> str:
    """
    Format an international phone number with privacy masking.

    Args:
        country_code: Country code ("+1" or "+52")
        phone_digits: Normalized phone number (digits only)

    Returns:
        Masked international phone number (e.g., "***-4567")
    """
    return phone_service.format_phone(country_code, phone_digits, "masked")


# Backward compatibility aliases
def get_display_phone(phone: str) -> str:
    """Alias for format_phone_display for backward compatibility."""
    return format_phone_display(phone)
