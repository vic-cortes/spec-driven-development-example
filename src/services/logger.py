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
    sensitive_fields = {"phone", "email", "address", "birth_date", "notes"}
    masked_data = {}

    for key, value in data.items():
        if key.lower() in sensitive_fields:
            if key.lower() == "phone" and isinstance(value, str):
                if len(value) >= 4:
                    masked_data[key] = "***" + value[-4:]
                else:
                    masked_data[key] = "***" + value
            elif key.lower() == "email" and isinstance(value, str) and "@" in value:
                username, domain = value.split("@", 1)
                masked_username = username[:2] + "***" if len(username) > 2 else "***"
                masked_data[key] = f"{masked_username}@{domain}"
            else:
                masked_data[key] = "***MASKED***"
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
                else:
                    masked_args.append(arg)
            record.args = tuple(masked_args)

        return super().format(record)


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
