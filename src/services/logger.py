"""Privacy-safe logging for the dental check-in system."""

import logging
import re
from typing import Any, Dict


def mask_phone(text: str) -> str:
    """
    Mask phone numbers in text for privacy-safe logging.

    Args:
        text: Input text that may contain phone numbers

    Returns:
        Text with phone numbers masked (showing only last 4 digits)
    """
    # Pattern to match various phone number formats
    phone_patterns = [
        r"\b\d{3}[-.]?\d{3}[-.]?\d{4}\b",  # 555-123-4567, 555.123.4567, 5551234567
        r"\(\d{3}\)\s?\d{3}[-.]?\d{4}",  # (555) 123-4567, (555)123-4567
        r"\+1[-.\s]?\d{3}[-.\s]?\d{3}[-.\s]?\d{4}",  # +1-555-123-4567
        r"\b\d{10}\b",  # 5551234567 (standalone 10 digits)
    ]

    result = text
    for pattern in phone_patterns:

        def mask_match(match):
            phone = re.sub(r"[^\d]", "", match.group())  # Extract digits only
            if len(phone) >= 4:
                return "***" + phone[-4:]
            return "***" + phone

        result = re.sub(pattern, mask_match, result)

    return result


def mask_pii_data(data: Dict[str, Any]) -> Dict[str, Any]:
    """
    Mask PII in a dictionary for safe logging.

    Args:
        data: Dictionary that may contain PII

    Returns:
        Dictionary with PII fields masked
    """
    # Expanded list of sensitive fields
    sensitive_fields = {
        "phone",
        "email",
        "address",
        "birth_date",
        "notes",
        "ssn",
        "social_security",
        "patient_id",
        "id",
        "first_name",
        "last_name",
        "name",
        "full_name",
        "street",
        "city",
        "zip",
        "zipcode",
        "postal_code",
    }

    masked_data = {}

    for key, value in data.items():
        if value is None:
            masked_data[key] = None
            continue

        key_lower = key.lower()

        if key_lower in sensitive_fields:
            if key_lower == "phone" and isinstance(value, str):
                # Enhanced phone masking
                cleaned_phone = re.sub(r"[^\d]", "", value)
                if len(cleaned_phone) >= 4:
                    masked_data[key] = "***" + cleaned_phone[-4:]
                elif len(cleaned_phone) > 0:
                    masked_data[key] = "***" + cleaned_phone
                else:
                    masked_data[key] = "***"
            elif key_lower == "email" and isinstance(value, str) and "@" in value:
                # Enhanced email masking
                username, domain = value.split("@", 1)
                if len(username) > 3:
                    masked_username = username[:1] + "***" + username[-1:]
                elif len(username) > 1:
                    masked_username = username[:1] + "***"
                else:
                    masked_username = "***"
                masked_data[key] = f"{masked_username}@{domain}"
            elif key_lower in {
                "first_name",
                "last_name",
                "name",
                "full_name",
            } and isinstance(value, str):
                # Mask names partially for debugging while preserving privacy
                if len(value) > 2:
                    masked_data[key] = value[:1] + "***" + value[-1:]
                elif len(value) > 0:
                    masked_data[key] = value[:1] + "***"
                else:
                    masked_data[key] = "***"
            elif key_lower == "id" and isinstance(value, str):
                # Mask IDs but keep enough for debugging
                if len(value) > 8:
                    masked_data[key] = value[:4] + "***" + value[-4:]
                elif len(value) > 4:
                    masked_data[key] = value[:2] + "***" + value[-2:]
                else:
                    masked_data[key] = "***" + value[-2:] if len(value) > 2 else "***"
            else:
                # Generic masking for other sensitive fields
                masked_data[key] = "***MASKED***"
        else:
            # Non-sensitive fields pass through but check for embedded PII
            if isinstance(value, str):
                masked_data[key] = mask_phone(
                    value
                )  # Check for phone numbers in any string
            else:
                masked_data[key] = value

    return masked_data


class PrivacySafeFormatter(logging.Formatter):
    """Custom log formatter that automatically masks PII."""

    def format(self, record):
        # Mask phone numbers in the log message
        if hasattr(record, "msg") and isinstance(record.msg, str):
            record.msg = mask_phone(record.msg)

        # Mask phone numbers in any string arguments
        if hasattr(record, "args") and record.args:
            masked_args = []
            for arg in record.args:
                if isinstance(arg, str):
                    masked_args.append(mask_phone(arg))
                elif isinstance(arg, dict):
                    # Handle dictionary arguments that might contain PII
                    masked_args.append(mask_pii_data(arg))
                else:
                    masked_args.append(arg)
            record.args = tuple(masked_args)

        return super().format(record)


def sanitize_log_message(message: str) -> str:
    """
    Sanitize a log message to remove any potential PII.

    Args:
        message: The log message to sanitize

    Returns:
        Sanitized message with PII masked
    """
    if not isinstance(message, str):
        return str(message)

    # Apply phone masking
    sanitized = mask_phone(message)

    # Additional patterns for common PII that might slip through
    pii_patterns = [
        (
            r"\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b",
            "[EMAIL]",
        ),  # Email addresses
        (r"\b\d{3}-?\d{2}-?\d{4}\b", "[SSN]"),  # SSN patterns
        (
            r"\b\d{4}[-\s]?\d{4}[-\s]?\d{4}[-\s]?\d{4}\b",
            "[CARD]",
        ),  # Credit card patterns
    ]

    for pattern, replacement in pii_patterns:
        sanitized = re.sub(pattern, replacement, sanitized, flags=re.IGNORECASE)

    return sanitized


def create_audit_log_entry(
    action: str, user_id: str, details: Dict[str, Any]
) -> Dict[str, Any]:
    """
    Create a privacy-safe audit log entry.

    Args:
        action: The action being performed
        user_id: ID of the user performing the action (masked)
        details: Additional details about the action

    Returns:
        Audit log entry with all PII properly masked
    """
    import datetime

    audit_entry = {
        "timestamp": datetime.datetime.now().isoformat(),
        "action": action,
        "user_id": user_id[:4] + "***" if len(user_id) > 4 else "***",
        "details": (
            mask_pii_data(details) if isinstance(details, dict) else str(details)
        ),
    }

    return audit_entry


def setup_privacy_safe_logger(name: str = "dental_checkin") -> logging.Logger:
    """
    Set up a privacy-safe logger.

    Args:
        name: Logger name

    Returns:
        Configured logger with PII masking
    """
    logger = logging.getLogger(name)

    # Avoid adding multiple handlers if logger already configured
    if logger.handlers:
        return logger

    logger.setLevel(logging.INFO)

    # Console handler
    console_handler = logging.StreamHandler()
    console_handler.setLevel(logging.INFO)

    # Privacy-safe formatter
    formatter = PrivacySafeFormatter(
        "%(asctime)s - %(name)s - %(levelname)s - %(message)s",
        datefmt="%Y-%m-%d %H:%M:%S",
    )
    console_handler.setFormatter(formatter)

    logger.addHandler(console_handler)

    return logger


# Create default logger instance
logger = setup_privacy_safe_logger()
