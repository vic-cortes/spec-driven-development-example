"""Integration tests for the check-in flow."""

from datetime import date, datetime

import pytest

from src.models.checkin import CheckIn, CheckInStatus
from src.models.patient import Patient
from src.services.store import MemoryStore
from src.utils.phone import normalize_phone


class TestCheckInFlow:
    """Test the complete check-in workflow."""

    @pytest.fixture
    def store(self):
        """Create a fresh memory store for testing."""
        store = MemoryStore()
        store.clear_all()
        return store

    @pytest.fixture
    def existing_patient(self, store):
        """Create an existing patient for testing."""
        patient = Patient(
            id="patient-001",
            first_name="Maria",
            last_name="Garcia",
            phone="5551234567",
            email="maria@test.com",
        )
        store.add_patient(patient)
        return patient

    def test_checkin_existing_patient(self, store, existing_patient):
        """Test checking in an existing patient."""
        # Verify patient exists
        patients = store.find_patients_by_phone("5551234567")
        assert len(patients) == 1
        patient = patients[0]

        # Create check-in
        checkin = CheckIn.create_new(patient.id)
        store.add_checkin(checkin)

        # Verify check-in was created
        assert checkin.patient_id == patient.id
        assert checkin.date == date.today()
        assert checkin.status.value == "checked_in"

        # Verify check-in can be retrieved
        retrieved_checkin = store.get_checkin(checkin.id)
        assert retrieved_checkin is not None
        assert retrieved_checkin.patient_id == patient.id

    def test_checkin_new_patient_creation(self, store):
        """Test creating a new patient and checking them in."""
        # Verify phone doesn't exist
        patients = store.find_patients_by_phone("5559999999")
        assert len(patients) == 0

        # Create minimal patient
        new_patient = Patient.create_minimal("John", "Doe", "5559999999")
        store.add_patient(new_patient)

        # Create check-in
        checkin = CheckIn.create_new(new_patient.id, route_note="New patient")
        store.add_checkin(checkin)

        # Verify both patient and check-in exist
        patients = store.find_patients_by_phone("5559999999")
        assert len(patients) == 1
        assert patients[0].full_name == "John Doe"

        retrieved_checkin = store.get_checkin(checkin.id)
        assert retrieved_checkin is not None
        assert retrieved_checkin.route_note == "New patient"

    def test_checkin_single_per_day_policy(self, store, existing_patient):
        """Test that only one check-in per day is allowed."""
        today = date.today()

        # First check-in
        checkin1 = CheckIn.create_new(existing_patient.id)
        store.add_checkin(checkin1)
        original_time = checkin1.timestamp

        # Try to find existing check-in for today
        existing_checkin = store.find_checkin_by_patient_and_date(
            existing_patient.id, today
        )
        assert existing_checkin is not None
        assert existing_checkin.id == checkin1.id

        # Simulate repeated arrival - update timestamp
        existing_checkin.update_timestamp()
        store.update_checkin(existing_checkin)

        # Verify timestamp was updated but same check-in
        updated_checkin = store.get_checkin(checkin1.id)
        assert updated_checkin.timestamp > original_time
        assert updated_checkin.date == today

        # Verify still only one check-in for today
        todays_checkins = store.list_checkins_for_date(today)
        patient_checkins_today = [
            c for c in todays_checkins if c.patient_id == existing_patient.id
        ]
        assert len(patient_checkins_today) == 1

    def test_checkin_shared_phone_disambiguation(self, store):
        """Test check-in flow with shared phone numbers."""
        # Create family with shared phone
        michael = Patient(
            id="patient-michael",
            first_name="Michael",
            last_name="Wilson",
            phone="5553336666",
        )
        sarah = Patient(
            id="patient-sarah",
            first_name="Sarah",
            last_name="Wilson",
            phone="5553336666",  # Same phone
        )

        store.add_patient(michael)
        store.add_patient(sarah)

        # Lookup by phone returns both
        patients = store.find_patients_by_phone("5553336666")
        assert len(patients) == 2

        # Check in Michael
        michael_checkin = CheckIn.create_new(michael.id)
        store.add_checkin(michael_checkin)

        # Check in Sarah
        sarah_checkin = CheckIn.create_new(sarah.id)
        store.add_checkin(sarah_checkin)

        # Verify both have separate check-ins today
        today = date.today()
        todays_checkins = store.list_checkins_for_date(today)
        wilson_checkins = [
            c for c in todays_checkins if c.patient_id in [michael.id, sarah.id]
        ]
        assert len(wilson_checkins) == 2

        # Verify each has their own check-in
        michael_checkin_today = store.find_checkin_by_patient_and_date(
            michael.id, today
        )
        sarah_checkin_today = store.find_checkin_by_patient_and_date(sarah.id, today)
        assert michael_checkin_today is not None
        assert sarah_checkin_today is not None
        assert michael_checkin_today.id != sarah_checkin_today.id

    def test_checkin_phone_normalization_flow(self, store):
        """Test check-in flow with different phone formats."""
        # Create patient with normalized phone
        patient = Patient.create_minimal("Jane", "Smith", "5551111111")
        store.add_patient(patient)

        # Test lookup with various formats
        test_formats = [
            "555-111-1111",
            "(555) 111-1111",
            "555.111.1111",
            "+1 555 111 1111",
        ]

        for phone_format in test_formats:
            normalized = normalize_phone(phone_format)
            patients = store.find_patients_by_phone(normalized)
            assert len(patients) == 1
            assert patients[0].full_name == "Jane Smith"

    def test_checkin_validation_errors(self, store):
        """Test check-in validation and error cases."""
        # Try to create check-in for non-existent patient
        with pytest.raises(ValueError, match="Patient ID is required"):
            CheckIn.create_new("")

        # Test date/timestamp mismatch validation
        with pytest.raises(ValueError, match="Date must match timestamp date"):
            CheckIn(
                id="test-checkin",
                patient_id="patient-001",
                timestamp=datetime(2026, 1, 1, 10, 0, 0),
                date=date(2026, 1, 2),  # Different date
                status=CheckInStatus.CHECKED_IN,
            )

    def test_todays_arrivals_view(self, store, existing_patient):
        """Test retrieving today's arrivals for display."""
        today = date.today()

        # No arrivals initially
        todays_arrivals = store.list_checkins_for_date(today)
        assert len(todays_arrivals) == 0

        # Add check-in
        checkin = CheckIn.create_new(existing_patient.id)
        store.add_checkin(checkin)

        # Verify arrival appears in today's list
        todays_arrivals = store.list_checkins_for_date(today)
        assert len(todays_arrivals) == 1
        assert todays_arrivals[0].patient_id == existing_patient.id

        # Add another patient and check-in
        patient2 = Patient.create_minimal("John", "Doe", "5559999999")
        store.add_patient(patient2)
        checkin2 = CheckIn.create_new(patient2.id)
        store.add_checkin(checkin2)

        # Verify both arrivals appear
        todays_arrivals = store.list_checkins_for_date(today)
        assert len(todays_arrivals) == 2
        patient_ids = {c.patient_id for c in todays_arrivals}
        assert existing_patient.id in patient_ids
        assert patient2.id in patient_ids
