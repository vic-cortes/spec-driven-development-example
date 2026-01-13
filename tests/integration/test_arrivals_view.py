"""Integration tests for the arrivals list view."""

from datetime import date, datetime

import pytest

from src.models.checkin import CheckIn, CheckInStatus
from src.models.patient import Patient
from src.services.checkin_service import CheckInService
from src.services.patient_service import PatientService
from src.services.store import MemoryStore
from src.utils.phone import normalize_phone


class TestArrivalsView:
    """Test the arrivals list view functionality."""

    @pytest.fixture
    def store(self):
        """Create a fresh memory store for testing."""
        store = MemoryStore()
        store.clear_all()
        return store

    @pytest.fixture
    def patient_service(self, store):
        """Create patient service with test store."""
        return PatientService(store)

    @pytest.fixture
    def checkin_service(self, store):
        """Create check-in service with test store."""
        return CheckInService(store)

    @pytest.fixture
    def sample_patients(self, patient_service):
        """Create sample patients for testing."""
        patients = [
            Patient(
                id="patient-001",
                first_name="Maria",
                last_name="Garcia",
                phone="5551234567",
                email="maria.garcia@email.com",
                date_of_birth=date(1985, 3, 15),
                created_at=datetime.now(),
                updated_at=datetime.now(),
            ),
            Patient(
                id="patient-002",
                first_name="John",
                last_name="Smith",
                phone="5559876543",
                email="john.smith@email.com",
                date_of_birth=date(1978, 8, 22),
                created_at=datetime.now(),
                updated_at=datetime.now(),
            ),
            Patient(
                id="patient-003",
                first_name="Sarah",
                last_name="Johnson",
                phone="5555551234",
                email="sarah.j@email.com",
                date_of_birth=date(1992, 12, 3),
                created_at=datetime.now(),
                updated_at=datetime.now(),
            ),
        ]

        # Store patients
        for patient in patients:
            patient_service._store.save_patient(patient)

        return patients

    def test_empty_arrivals_list(self, checkin_service):
        """Test arrivals view when no one has checked in today."""
        today = date.today()
        arrivals = checkin_service.get_todays_arrivals(today)

        assert len(arrivals) == 0

        # Test that the service returns empty list for days with no arrivals
        stats = checkin_service.get_checkin_stats(today)
        assert stats["total_checkins"] == 0
        assert stats["unique_patients"] == 0

    def test_single_arrival_display(self, checkin_service, sample_patients):
        """Test arrivals view with one check-in."""
        patient = sample_patients[0]
        today = date.today()

        # Create a check-in for today
        checkin_result = checkin_service.check_in_patient(
            patient_id=patient.id, route_note="Routine cleaning"
        )

        assert checkin_result.success
        checkin = checkin_result.checkin

        # Get today's arrivals
        arrivals = checkin_service.get_todays_arrivals(today)

        assert len(arrivals) == 1
        assert arrivals[0].patient_id == patient.id
        assert arrivals[0].status == CheckInStatus.ARRIVED
        assert arrivals[0].checkin_date == today

        # Verify stats
        stats = checkin_service.get_checkin_stats(today)
        assert stats["total_checkins"] == 1
        assert stats["unique_patients"] == 1

    def test_multiple_arrivals_display(self, checkin_service, sample_patients):
        """Test arrivals view with multiple check-ins."""
        today = date.today()

        # Check in all sample patients
        checkin_results = []
        for i, patient in enumerate(sample_patients):
            result = checkin_service.check_in_patient(
                patient_id=patient.id, route_note=f"Appointment {i+1}"
            )
            assert result.success
            checkin_results.append(result)

        # Get today's arrivals
        arrivals = checkin_service.get_todays_arrivals(today)

        assert len(arrivals) == 3

        # Verify all patients are in the list
        patient_ids_in_arrivals = {arrival.patient_id for arrival in arrivals}
        expected_patient_ids = {patient.id for patient in sample_patients}
        assert patient_ids_in_arrivals == expected_patient_ids

        # Verify all are marked as arrived
        for arrival in arrivals:
            assert arrival.status == CheckInStatus.ARRIVED
            assert arrival.checkin_date == today

        # Verify stats
        stats = checkin_service.get_checkin_stats(today)
        assert stats["total_checkins"] == 3
        assert stats["unique_patients"] == 3

    def test_arrivals_chronological_order(self, checkin_service, sample_patients):
        """Test that arrivals are returned in chronological order."""
        today = date.today()

        # Check in patients with different times
        # (The service should handle chronological ordering)
        for patient in sample_patients:
            checkin_service.check_in_patient(
                patient_id=patient.id, route_note="Test appointment"
            )

        arrivals = checkin_service.get_todays_arrivals(today)

        # Verify arrivals are sorted by check-in time
        assert len(arrivals) == 3
        for i in range(1, len(arrivals)):
            assert arrivals[i - 1].checked_in_at <= arrivals[i].checked_in_at

    def test_arrivals_exclude_other_days(self, checkin_service, sample_patients):
        """Test that only today's arrivals are shown."""
        from datetime import timedelta

        patient = sample_patients[0]
        today = date.today()
        yesterday = today - timedelta(days=1)

        # Create a check-in for yesterday (if possible with test setup)
        # For this test, we'll just verify today's filtering works
        checkin_service.check_in_patient(
            patient_id=patient.id, route_note="Today's appointment"
        )

        # Get today's arrivals
        today_arrivals = checkin_service.get_todays_arrivals(today)
        yesterday_arrivals = checkin_service.get_todays_arrivals(yesterday)

        assert len(today_arrivals) == 1
        assert len(yesterday_arrivals) == 0  # No arrivals yesterday

    def test_arrivals_summary_formatting(self, checkin_service, sample_patients):
        """Test the arrival summary string formatting."""
        today = date.today()

        # Test empty summary
        summary = checkin_service.get_arrival_summary(today)
        assert "0 patients checked in today" in summary.lower()

        # Add some check-ins
        for i, patient in enumerate(sample_patients[:2]):
            checkin_service.check_in_patient(
                patient_id=patient.id, route_note=f"Appointment {i+1}"
            )

        # Test populated summary
        summary = checkin_service.get_arrival_summary(today)
        assert "2 patients checked in today" in summary.lower()

    def test_duplicate_checkin_prevention(self, checkin_service, sample_patients):
        """Test that duplicate check-ins for the same day are prevented."""
        patient = sample_patients[0]
        today = date.today()

        # First check-in should succeed
        result1 = checkin_service.check_in_patient(
            patient_id=patient.id, route_note="First appointment"
        )
        assert result1.success

        # Second check-in for same patient same day should fail
        result2 = checkin_service.check_in_patient(
            patient_id=patient.id, route_note="Duplicate appointment"
        )
        assert not result2.success
        assert "already checked in today" in result2.error_message.lower()

        # Should still only show one arrival
        arrivals = checkin_service.get_todays_arrivals(today)
        assert len(arrivals) == 1

    def test_phone_masking_in_arrivals_context(
        self, checkin_service, sample_patients, patient_service
    ):
        """Test that phone numbers can be retrieved for display masking."""
        patient = sample_patients[0]
        today = date.today()

        # Check in patient
        checkin_service.check_in_patient(
            patient_id=patient.id, route_note="Test appointment"
        )

        # Get arrivals and verify we can get patient info for masking
        arrivals = checkin_service.get_todays_arrivals(today)
        arrival = arrivals[0]

        # Get patient details for phone masking
        patient_details = patient_service.get_patient(arrival.patient_id)
        assert patient_details is not None
        assert patient_details.phone == "5551234567"

        # Verify phone masking utility works
        from src.services.logger import mask_pii_data

        masked_phone = mask_pii_data({"phone": patient_details.phone})
        assert masked_phone["phone"] != patient_details.phone
        assert "***" in masked_phone["phone"]
