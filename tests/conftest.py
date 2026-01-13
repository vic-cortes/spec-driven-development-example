"""Basic pytest configuration for the patient check-in app."""

import pytest


@pytest.fixture
def sample_phone_numbers():
    """Fixture providing various phone number formats for testing."""
    return [
        "5551234567",
        "(555) 123-4567",
        "555-123-4567",
        "555.123.4567",
        "+1 555 123 4567",
        " 555 123 4567 ",
    ]


@pytest.fixture
def normalized_phone():
    """Expected normalized phone number."""
    return "5551234567"
