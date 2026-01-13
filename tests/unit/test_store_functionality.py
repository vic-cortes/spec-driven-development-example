"""Unit tests for MemoryStore functionality and edge cases."""

from datetime import date, datetime

import pytest

from src.models.checkin import CheckIn
from src.models.patient import Patient
from src.services.store import MemoryStore


class TestMemoryStorePatients:
    """Test MemoryStore patient operations."""

    @pytest.fixture
    def store(self):
        """Create a fresh memory store for testing."""
        store = MemoryStore()
        store.clear_all()
        return store

    @pytest.fixture
    def sample_patient(self):
        """Create a sample patient for testing."""
        return Patient(
            id="test-patient-001",
            first_name="John",
            last_name="Doe",
            phone="5551234567",
            email="john@example.com",
        )

    def test_add_patient_updates_phone_index(self, store, sample_patient):
        """Test that adding a patient updates the phone index."""
        store.add_patient(sample_patient)

        # Check patient was added
        assert store.get_patient(sample_patient.id) == sample_patient

        # Check phone index was updated
        patients_by_phone = store.find_patients_by_phone("5551234567")
        assert len(patients_by_phone) == 1
        assert patients_by_phone[0].id == sample_patient.id

    def test_add_multiple_patients_same_phone(self, store):
        """Test adding multiple patients with same phone number."""
        patient1 = Patient(
            id="p1", first_name="Alice", last_name="Smith", phone="5551111111"
        )
        patient2 = Patient(
            id="p2", first_name="Bob", last_name="Smith", phone="5551111111"
        )

        store.add_patient(patient1)
        store.add_patient(patient2)

        # Both should be findable by phone
        patients = store.find_patients_by_phone("5551111111")
        assert len(patients) == 2
        patient_ids = [p.id for p in patients]
        assert "p1" in patient_ids
        assert "p2" in patient_ids

    def test_update_patient_phone_updates_index(self, store, sample_patient):
        """Test that updating patient phone updates the phone index."""
        store.add_patient(sample_patient)

        # Update patient with new phone
        updated_patient = Patient(
            id=sample_patient.id,
            first_name=sample_patient.first_name,
            last_name=sample_patient.last_name,
            phone="5559876543",  # New phone
            email=sample_patient.email,
        )
        store.update_patient(updated_patient)

        # Old phone should not find patient
        old_results = store.find_patients_by_phone("5551234567")
        assert len(old_results) == 0

        # New phone should find patient
        new_results = store.find_patients_by_phone("5559876543")
        assert len(new_results) == 1
        assert new_results[0].id == sample_patient.id

    def test_update_nonexistent_patient(self, store):
        """Test updating a patient that doesn't exist."""
        nonexistent = Patient(
            id="nonexistent", first_name="Test", last_name="User", phone="5551111111"
        )

        with pytest.raises(ValueError, match="Patient nonexistent not found"):
            store.update_patient(nonexistent)

    def test_delete_patient_removes_from_index(self, store, sample_patient):
        """Test that deleting a patient removes it from phone index."""
        store.add_patient(sample_patient)

        # Verify patient exists
        assert store.get_patient(sample_patient.id) is not None
        assert len(store.find_patients_by_phone(sample_patient.phone)) == 1

        # Delete patient
        result = store.delete_patient(sample_patient.id)
        assert result is True

        # Verify patient is gone
        assert store.get_patient(sample_patient.id) is None
        assert len(store.find_patients_by_phone(sample_patient.phone)) == 0

    def test_delete_nonexistent_patient(self, store):
        """Test deleting a patient that doesn't exist."""
        result = store.delete_patient("nonexistent")
        assert result is False

    def test_delete_patient_with_shared_phone(self, store):
        """Test deleting one patient when multiple share the same phone."""
        patient1 = Patient(
            id="p1", first_name="Alice", last_name="Smith", phone="5551111111"
        )
        patient2 = Patient(
            id="p2", first_name="Bob", last_name="Smith", phone="5551111111"
        )

        store.add_patient(patient1)
        store.add_patient(patient2)

        # Delete one patient
        store.delete_patient(patient1.id)

        # Other patient should still be findable by phone
        remaining = store.find_patients_by_phone("5551111111")
        assert len(remaining) == 1
        assert remaining[0].id == patient2.id

    def test_find_patients_by_nonexistent_phone(self, store):
        """Test finding patients by phone that doesn't exist."""
        results = store.find_patients_by_phone("9999999999")
        assert len(results) == 0


class TestMemoryStoreCheckIns:
    """Test MemoryStore check-in operations."""

    @pytest.fixture
    def store(self):
        """Create a fresh memory store for testing."""
        store = MemoryStore()
        store.clear_all()
        return store

    @pytest.fixture
    def sample_checkin(self):
        """Create a sample check-in for testing."""
        return CheckIn(
            id="test-checkin-001",
            patient_id="patient-001",
            timestamp=datetime.now(),
            date=date.today(),
        )

    def test_add_checkin_updates_patient_index(self, store, sample_checkin):
        """Test that adding a check-in updates the patient-checkin index."""
        store.add_checkin(sample_checkin)

        # Check check-in was added
        assert store.get_checkin(sample_checkin.id) == sample_checkin

        # Check patient-checkin index was updated
        checkin = store.find_checkin_by_patient_and_date(
            sample_checkin.patient_id, sample_checkin.date
        )
        assert checkin.id == sample_checkin.id

    def test_find_checkin_by_patient_and_date_not_found(self, store):
        """Test finding check-in when none exists."""
        result = store.find_checkin_by_patient_and_date("nonexistent", date.today())
        assert result is None

    def test_list_checkins_for_date_empty(self, store):
        """Test listing check-ins for date when none exist."""
        results = store.list_checkins_for_date(date.today())
        assert len(results) == 0

    def test_list_checkins_for_date_multiple(self, store):
        """Test listing check-ins for date with multiple entries."""
        today = date.today()

        checkin1 = CheckIn(
            id="c1", patient_id="p1", timestamp=datetime.now(), date=today
        )
        checkin2 = CheckIn(
            id="c2", patient_id="p2", timestamp=datetime.now(), date=today
        )

        store.add_checkin(checkin1)
        store.add_checkin(checkin2)

        results = store.list_checkins_for_date(today)
        assert len(results) == 2
        checkin_ids = [c.id for c in results]
        assert "c1" in checkin_ids
        assert "c2" in checkin_ids

    def test_update_checkin_nonexistent(self, store):
        """Test updating a check-in that doesn't exist."""
        nonexistent = CheckIn(
            id="nonexistent",
            patient_id="p1",
            timestamp=datetime.now(),
            date=date.today(),
        )

        with pytest.raises(ValueError, match="CheckIn nonexistent not found"):
            store.update_checkin(nonexistent)

    def test_delete_checkin_removes_from_index(self, store, sample_checkin):
        """Test that deleting a check-in removes it from patient index."""
        store.add_checkin(sample_checkin)

        # Verify check-in exists
        assert store.get_checkin(sample_checkin.id) is not None

        # Delete check-in
        result = store.delete_checkin(sample_checkin.id)
        assert result is True

        # Verify check-in is gone
        assert store.get_checkin(sample_checkin.id) is None

        # Verify patient-checkin index is updated
        checkin = store.find_checkin_by_patient_and_date(
            sample_checkin.patient_id, sample_checkin.date
        )
        assert checkin is None

    def test_delete_nonexistent_checkin(self, store):
        """Test deleting a check-in that doesn't exist."""
        result = store.delete_checkin("nonexistent")
        assert result is False


class TestMemoryStoreUtilities:
    """Test MemoryStore utility methods."""

    @pytest.fixture
    def store(self):
        """Create a fresh memory store for testing."""
        store = MemoryStore()
        store.clear_all()
        return store

    def test_clear_all(self, store):
        """Test that clear_all removes all data."""
        # Add some data
        patient = Patient(
            id="p1", first_name="Test", last_name="User", phone="5551111111"
        )
        checkin = CheckIn(
            id="c1", patient_id="p1", timestamp=datetime.now(), date=date.today()
        )

        store.add_patient(patient)
        store.add_checkin(checkin)

        # Verify data exists
        assert store.get_patient("p1") is not None
        assert store.get_checkin("c1") is not None

        # Clear all
        store.clear_all()

        # Verify data is gone
        assert store.get_patient("p1") is None
        assert store.get_checkin("c1") is None
        assert len(store.find_patients_by_phone("5551111111")) == 0

        # Verify stats are zero
        stats = store.get_stats()
        assert stats["total_patients"] == 0
        assert stats["total_checkins"] == 0
        assert stats["unique_phones"] == 0

    def test_get_stats(self, store):
        """Test getting storage statistics."""
        # Initially empty
        stats = store.get_stats()
        assert stats["total_patients"] == 0
        assert stats["total_checkins"] == 0
        assert stats["unique_phones"] == 0

        # Add some data
        patient1 = Patient(
            id="p1", first_name="Alice", last_name="Smith", phone="5551111111"
        )
        patient2 = Patient(
            id="p2", first_name="Bob", last_name="Jones", phone="5552222222"
        )
        patient3 = Patient(
            id="p3", first_name="Carol", last_name="Brown", phone="5551111111"
        )  # Same phone as p1

        checkin1 = CheckIn(
            id="c1", patient_id="p1", timestamp=datetime.now(), date=date.today()
        )
        checkin2 = CheckIn(
            id="c2", patient_id="p2", timestamp=datetime.now(), date=date.today()
        )

        store.add_patient(patient1)
        store.add_patient(patient2)
        store.add_patient(patient3)
        store.add_checkin(checkin1)
        store.add_checkin(checkin2)

        # Check updated stats
        stats = store.get_stats()
        assert stats["total_patients"] == 3
        assert stats["total_checkins"] == 2
        assert stats["unique_phones"] == 2  # Two unique phone numbers

    def test_patient_deletion_removes_checkins(self, store):
        """Test that deleting a patient also removes their check-ins."""
        # Add patient and check-ins
        patient = Patient(
            id="p1", first_name="Test", last_name="User", phone="5551111111"
        )
        checkin1 = CheckIn(
            id="c1", patient_id="p1", timestamp=datetime.now(), date=date.today()
        )
        checkin2 = CheckIn(
            id="c2", patient_id="p1", timestamp=datetime.now(), date=date.today()
        )

        store.add_patient(patient)
        store.add_checkin(checkin1)
        store.add_checkin(checkin2)

        # Verify data exists
        assert store.get_patient("p1") is not None
        assert store.get_checkin("c1") is not None
        assert store.get_checkin("c2") is not None

        # Delete patient
        store.delete_patient("p1")

        # Verify patient and check-ins are gone
        assert store.get_patient("p1") is None
        assert store.get_checkin("c1") is None
        assert store.get_checkin("c2") is None
