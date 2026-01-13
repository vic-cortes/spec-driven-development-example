"""Phone number normalization utilities."""

import re
from typing import Optional


def normalize_phone(phone: str) -> str:
    """
    Normalize a phone number to digits-only format.

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


def is_valid_phone(phone: str) -> bool:
    """
    Check if a phone number is valid without raising exceptions.

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


def format_phone_display(phone: str) -> str:
    """
    Format a normalized phone number for display.

    Args:
        phone: Normalized phone number (digits only)

    Returns:
        Formatted phone number (e.g., "555-123-4567")
    """
    if len(phone) == 10:
        return f"{phone[:3]}-{phone[3:6]}-{phone[6:]}"
    else:
        return phone  # Return as-is for non-standard lengths
