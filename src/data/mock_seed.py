"""Mock data seeding script for demonstration purposes."""

from datetime import date, datetime, timedelta
from typing import List

from src.models.checkin import CheckIn
from src.models.patient import Patient
from src.services.logger import logger
from src.services.store import store


def create_mock_patients() -> List[Patient]:
    """Create mock patient data for demonstration."""
    mock_patients = [
        Patient(
            id="patient-001",
            first_name="Maria",
            last_name="Garcia",
            phone="5551234567",
            email="maria.garcia@email.com",
            birth_date=date(1985, 3, 15),
            address="123 Main St, Anytown, ST 12345",
        ),
        Patient(
            id="patient-002",
            first_name="John",
            last_name="Smith",
            phone="5559876543",
            email="john.smith@email.com",
            birth_date=date(1978, 11, 22),
            address="456 Oak Ave, Somewhere, ST 67890",
        ),
        Patient(
            id="patient-003",
            first_name="Ana",
            last_name="Rodriguez",
            phone="5555551234",
            birth_date=date(1992, 7, 8),
            notes="Prefers morning appointments",
        ),
        Patient(
            id="patient-004",
            first_name="David",
            last_name="Johnson",
            phone="5552468135",
            email="d.johnson@email.com",
            address="789 Pine St, Elsewhere, ST 11111",
        ),
        Patient(
            id="patient-005",
            first_name="Carmen",
            last_name="Martinez",
            phone="5557891011",
            birth_date=date(1995, 12, 3),
        ),
        # Family sharing a phone number
        Patient(
            id="patient-006",
            first_name="Michael",
            last_name="Wilson",
            phone="5553336666",
            email="michael.wilson@email.com",
            birth_date=date(1980, 5, 10),
        ),
        Patient(
            id="patient-007",
            first_name="Sarah",
            last_name="Wilson",
            phone="5553336666",  # Same phone as Michael
            email="sarah.wilson@email.com",
            birth_date=date(1982, 9, 18),
        ),
    ]

    return mock_patients


def create_mock_checkins() -> List[CheckIn]:
    """Create mock check-in data for today and recent days."""
    today = date.today()
    yesterday = today - timedelta(days=1)

    # Today's check-ins
    todays_checkins = [
        CheckIn(
            id="checkin-001",
            patient_id="patient-001",  # Maria Garcia
            timestamp=datetime.combine(
                today, datetime.min.time().replace(hour=9, minute=15)
            ),
            date=today,
        ),
        CheckIn(
            id="checkin-002",
            patient_id="patient-003",  # Ana Rodriguez
            timestamp=datetime.combine(
                today, datetime.min.time().replace(hour=10, minute=30)
            ),
            date=today,
            route_note="Cleaning appointment",
        ),
        CheckIn(
            id="checkin-003",
            patient_id="patient-005",  # Carmen Martinez
            timestamp=datetime.combine(
                today, datetime.min.time().replace(hour=14, minute=45)
            ),
            date=today,
        ),
    ]

    # Yesterday's check-ins (for demonstration)
    yesterdays_checkins = [
        CheckIn(
            id="checkin-004",
            patient_id="patient-002",  # John Smith
            timestamp=datetime.combine(
                yesterday, datetime.min.time().replace(hour=11, minute=0)
            ),
            date=yesterday,
        ),
        CheckIn(
            id="checkin-005",
            patient_id="patient-004",  # David Johnson
            timestamp=datetime.combine(
                yesterday, datetime.min.time().replace(hour=15, minute=30)
            ),
            date=yesterday,
            route_note="Follow-up consultation",
        ),
    ]

    return todays_checkins + yesterdays_checkins


def seed_mock_data() -> None:
    """Seed the store with mock data."""
    logger.info("Seeding mock data...")

    # Clear existing data
    store.clear_all()

    # Add patients
    mock_patients = create_mock_patients()
    for patient in mock_patients:
        store.add_patient(patient)
        logger.info(
            f"Added patient: {patient.full_name} (phone: {patient.masked_phone})"
        )

    # Add check-ins
    mock_checkins = create_mock_checkins()
    for checkin in mock_checkins:
        store.add_checkin(checkin)
        patient = store.get_patient(checkin.patient_id)
        patient_name = patient.full_name if patient else "Unknown"
        logger.info(f"Added check-in for {patient_name} on {checkin.date}")

    stats = store.get_stats()
    logger.info(f"Mock data seeded successfully: {stats}")


def reset_todays_checkins() -> None:
    """Reset today's check-ins (useful for testing)."""
    today = date.today()
    todays_checkins = store.list_checkins_for_date(today)

    for checkin in todays_checkins:
        store.delete_checkin(checkin.id)

    logger.info(f"Cleared {len(todays_checkins)} check-ins for today")


if __name__ == "__main__":
    # Run seeding if executed directly
    seed_mock_data()

    # Display today's arrivals
    today = date.today()
    todays_arrivals = store.list_checkins_for_date(today)
    print(f"\nToday's arrivals ({today}):")
    for checkin in sorted(todays_arrivals, key=lambda c: c.timestamp):
        patient = store.get_patient(checkin.patient_id)
        if patient:
            print(
                f"  {checkin.timestamp.strftime('%H:%M')} - {patient.full_name} ({patient.masked_phone})"
            )

    if not todays_arrivals:
        print("  No arrivals yet today")
