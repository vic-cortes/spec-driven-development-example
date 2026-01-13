"""Unit tests for listing today's check-ins."""

from datetime import date, datetime, timedelta

import pytest

from src.models.checkin import CheckIn, CheckInStatus
from src.models.patient import Patient
from src.services.checkin_service import CheckInService
from src.services.store import MemoryStore


class TestCheckInsToday:
    """Test retrieving today's check-ins from the service."""

    @pytest.fixture
    def store(self):
        """Create a fresh memory store for testing."""
        store = MemoryStore()
        store.clear_all()
        return store

    @pytest.fixture
    def checkin_service(self, store):
        """Create check-in service with test store."""
        return CheckInService(store)

    @pytest.fixture
    def sample_checkins(self, store):
        """Create sample check-ins for testing."""
        today = date.today()
        yesterday = today - timedelta(days=1)
        tomorrow = today + timedelta(days=1)

        # Create patients first
        patients = [
            Patient(
                id=f"patient-{i:03d}",
                first_name=f"Patient{i}",
                last_name="Test",
                phone=f"555000{i:04d}",
                email=f"patient{i}@test.com",
                date_of_birth=date(1980, 1, 1),
                created_at=datetime.now(),
                updated_at=datetime.now(),
            )
            for i in range(1, 6)
        ]

        for patient in patients:
            store.add_patient(patient)

        # Create check-ins for different dates
        checkins = [
            # Today's check-ins
            CheckIn(
                id="checkin-today-001",
                patient_id="patient-001",
                date=today,
                timestamp=datetime.combine(
                    today, datetime.min.time().replace(hour=9, minute=0)
                ),
                status=CheckInStatus.CHECKED_IN,
                route_note="Morning appointment",
                created_at=datetime.now(),
                updated_at=datetime.now(),
            ),
            CheckIn(
                id="checkin-today-002",
                patient_id="patient-002",
                date=today,
                timestamp=datetime.combine(
                    today, datetime.min.time().replace(hour=10, minute=30)
                ),
                status=CheckInStatus.ARRIVED,
                route_note="Follow-up visit",
                created_at=datetime.now(),
                updated_at=datetime.now(),
            ),
            CheckIn(
                id="checkin-today-003",
                patient_id="patient-003",
                date=today,
                timestamp=datetime.combine(
                    today, datetime.min.time().replace(hour=14, minute=15)
                ),
                status=CheckInStatus.ARRIVED,
                route_note="Routine cleaning",
                created_at=datetime.now(),
                updated_at=datetime.now(),
            ),
            # Yesterday's check-in (should not appear in today's list)
            CheckIn(
                id="checkin-yesterday-001",
                patient_id="patient-004",
                date=yesterday,
                timestamp=datetime.combine(
                    yesterday, datetime.min.time().replace(hour=15, minute=0)
                ),
                status=CheckInStatus.ARRIVED,
                route_note="Yesterday appointment",
                created_at=datetime.now(),
                updated_at=datetime.now(),
            ),
            # Tomorrow's check-in (should not appear in today's list)
            CheckIn(
                id="checkin-tomorrow-001",
                patient_id="patient-005",
                date=tomorrow,
                timestamp=datetime.combine(
                    tomorrow, datetime.min.time().replace(hour=11, minute=0)
                ),
                status=CheckInStatus.ARRIVED,
                route_note="Future appointment",
                created_at=datetime.now(),
                updated_at=datetime.now(),
            ),
        ]

        for checkin in checkins:
            store.save_checkin(checkin)

        return checkins

    def test_get_todays_arrivals_empty(self, checkin_service):
        """Test getting today's arrivals when there are none."""
        today = date.today()
        arrivals = checkin_service.list_today(target_date=today)

        assert isinstance(arrivals, list)
        assert len(arrivals) == 0

    def test_get_todays_arrivals_with_data(self, checkin_service, sample_checkins):
        """Test getting today's arrivals with sample data."""
        today = date.today()
        arrivals = checkin_service.list_today(target_date=today)

        assert isinstance(arrivals, list)
        assert len(arrivals) == 3  # Only today's check-ins

        # Verify all returned check-ins are for today
        for arrival in arrivals:
            assert arrival.date == today
            assert arrival.status == CheckInStatus.ARRIVED

        # Verify specific check-ins are present (use actual IDs from service)
        arrival_ids = {arrival.id for arrival in arrivals}
        # Note: actual IDs will be UUIDs from the service, so we check count and patient IDs
        patient_ids_in_arrivals = {arrival.patient_id for arrival in arrivals}
        expected_patient_ids = {"patient-001", "patient-002", "patient-003"}
        assert patient_ids_in_arrivals == expected_patient_ids

    def test_get_todays_arrivals_chronological_order(
        self, checkin_service, sample_checkins
    ):
        """Test that arrivals are returned in chronological order."""
        today = date.today()
        arrivals = checkin_service.list_today(target_date=today)

        assert len(arrivals) == 3

        # Verify chronological ordering (timestamps should be in order)
        for i in range(1, len(arrivals)):
            assert arrivals[i - 1].timestamp <= arrivals[i].timestamp

    def test_get_todays_arrivals_different_date(self, checkin_service, sample_checkins):
        """Test getting arrivals for a different date."""
        today = date.today()
        yesterday = today - timedelta(days=1)
        tomorrow = today + timedelta(days=1)

        # Yesterday should have no arrivals (fixture only creates today's)
        yesterday_arrivals = checkin_service.list_today(target_date=yesterday)
        assert len(yesterday_arrivals) == 0

        # Tomorrow should have no arrivals
        tomorrow_arrivals = checkin_service.list_today(target_date=tomorrow)
        assert len(tomorrow_arrivals) == 0

        # Today should have three arrivals
        today_arrivals = checkin_service.list_today(target_date=today)
        assert len(today_arrivals) == 3

    def test_get_todays_arrivals_default_date(self, checkin_service, sample_checkins):
        """Test getting arrivals with default date (today)."""
        # Call without specifying target_date (should default to today)
        arrivals = checkin_service.list_today()

        assert len(arrivals) == 3  # Today's arrivals
        for arrival in arrivals:
            assert arrival.date == date.today()

    def test_get_checkin_stats_today(self, checkin_service, sample_checkins):
        """Test getting check-in statistics for today."""
        today = date.today()
        stats = checkin_service.get_checkin_stats(target_date=today)

        assert isinstance(stats, dict)
        assert stats["total_checkins"] == 3
        assert stats["unique_patients"] == 3
        assert stats["date"] == today

    def test_get_checkin_stats_empty_day(self, checkin_service):
        """Test getting statistics for a day with no check-ins."""
        future_date = date.today() + timedelta(days=30)
        stats = checkin_service.get_checkin_stats(target_date=future_date)

        assert stats["total_checkins"] == 0
        assert stats["unique_patients"] == 0
        assert stats["date"] == future_date

    def test_get_arrival_summary(self, checkin_service, sample_checkins):
        """Test getting arrival summary string."""
        today = date.today()
        summary = checkin_service.get_arrival_summary(target_date=today)

        assert isinstance(summary, str)
        assert "3 patients checked in today" in summary.lower()

        # Test empty day
        future_date = date.today() + timedelta(days=30)
        empty_summary = checkin_service.get_arrival_summary(target_date=future_date)
        assert "0 patients checked in" in empty_summary.lower()

    def test_arrivals_patient_id_mapping(self, checkin_service, sample_checkins):
        """Test that we can map arrivals back to patient IDs correctly."""
        today = date.today()
        arrivals = checkin_service.list_today(target_date=today)

        # Verify patient ID mapping
        patient_ids = [arrival.patient_id for arrival in arrivals]
        expected_patient_ids = ["patient-001", "patient-002", "patient-003"]

        assert set(patient_ids) == set(expected_patient_ids)

        # Verify each arrival has required fields for UI display
        for arrival in arrivals:
            assert arrival.patient_id is not None
            assert arrival.timestamp is not None
            assert arrival.date is not None
            assert arrival.route_note is not None
            assert arrival.status == CheckInStatus.ARRIVED
