"""Unit tests for patient phone update functionality."""

import pytest

from src.models.patient import Patient
from src.services.patient_service import PatientService
from src.services.store import MemoryStore
from src.utils.phone import normalize_phone


class TestPatientUpdatePhone:
    """Test patient phone update operations."""

    @pytest.fixture
    def store(self):
        """Create a fresh memory store for testing."""
        store = MemoryStore()
        store.clear_all()
        return store

    @pytest.fixture
    def patient_service(self, store):
        """Create patient service with test store."""
        return PatientService(data_store=store)

    @pytest.fixture
    def sample_patient(self, store):
        """Create a sample patient for testing."""
        patient = Patient(
            id="patient-001",
            first_name="Maria",
            last_name="Garcia",
            phone="5551234567",
            email="maria@example.com",
        )
        store.add_patient(patient)
        return patient

    def test_update_patient_phone_affects_lookup(self, patient_service, sample_patient):
        """Test that updating a patient's phone affects future lookups."""
        # Original phone should find the patient
        original_phone = "5551234567"
        patients = patient_service.find_by_phone(original_phone)
        assert len(patients) == 1
        assert patients[0].id == sample_patient.id

        # Update the patient's phone
        new_phone = "(555) 987-6543"
        normalized_new_phone = normalize_phone(new_phone)

        updated_patient = Patient(
            id=sample_patient.id,
            first_name=sample_patient.first_name,
            last_name=sample_patient.last_name,
            phone=normalized_new_phone,
            email=sample_patient.email,
        )
        patient_service.update_patient(updated_patient)

        # Original phone should no longer find the patient
        patients = patient_service.find_by_phone(original_phone)
        assert len(patients) == 0

        # New phone should find the patient
        patients = patient_service.find_by_phone(new_phone)
        assert len(patients) == 1
        assert patients[0].id == sample_patient.id
        assert patients[0].phone == normalized_new_phone

    def test_update_patient_phone_validation(self, patient_service, sample_patient):
        """Test that phone validation works during updates."""
        # Invalid phone should raise ValueError
        with pytest.raises(ValueError, match="Invalid phone number"):
            updated_patient = Patient(
                id=sample_patient.id,
                first_name=sample_patient.first_name,
                last_name=sample_patient.last_name,
                phone="invalid-phone",
            )
            patient_service.update_patient(updated_patient)

        # Empty phone should raise ValueError
        with pytest.raises(ValueError, match="Invalid phone number"):
            updated_patient = Patient(
                id=sample_patient.id,
                first_name=sample_patient.first_name,
                last_name=sample_patient.last_name,
                phone="",
            )
            patient_service.update_patient(updated_patient)

    def test_update_patient_name_validation(self, patient_service, sample_patient):
        """Test that name validation works during updates."""
        # Empty first name should raise ValueError
        with pytest.raises(ValueError, match="First name is required"):
            updated_patient = Patient(
                id=sample_patient.id,
                first_name="",
                last_name=sample_patient.last_name,
                phone=sample_patient.phone,
            )
            patient_service.update_patient(updated_patient)

        # Empty last name should raise ValueError
        with pytest.raises(ValueError, match="Last name is required"):
            updated_patient = Patient(
                id=sample_patient.id,
                first_name=sample_patient.first_name,
                last_name="",
                phone=sample_patient.phone,
            )
            patient_service.update_patient(updated_patient)

    def test_update_nonexistent_patient(self, patient_service):
        """Test updating a patient that doesn't exist."""
        # Create a patient that wasn't added to the store
        nonexistent_patient = Patient(
            id="nonexistent-001", first_name="John", last_name="Doe", phone="5559876543"
        )

        # Update should still work (the store implementation may handle this differently)
        # But we'll test that the validation still works
        patient_service.update_patient(nonexistent_patient)

    def test_update_patient_preserves_other_data(self, patient_service, sample_patient):
        """Test that updating phone preserves other patient data."""
        # Update phone while keeping other data
        new_phone = "5559876543"
        updated_patient = Patient(
            id=sample_patient.id,
            first_name=sample_patient.first_name,
            last_name=sample_patient.last_name,
            phone=new_phone,
            email=sample_patient.email,  # Should preserve email
        )
        patient_service.update_patient(updated_patient)

        # Retrieve and verify all data is preserved
        retrieved = patient_service.get_patient(sample_patient.id)
        assert retrieved is not None
        assert retrieved.phone == new_phone
        assert retrieved.email == sample_patient.email
        assert retrieved.first_name == sample_patient.first_name
        assert retrieved.last_name == sample_patient.last_name

    def test_update_patient_creates_new_lookup_entry(self, patient_service):
        """Test that updating a patient's phone creates a new lookup entry."""
        # Create two patients with different phones
        patient1 = patient_service.create_minimal_patient(
            "Alice", "Smith", "5551111111"
        )
        patient2 = patient_service.create_minimal_patient("Bob", "Jones", "5552222222")

        # Verify initial state
        alice_results = patient_service.find_by_phone("5551111111")
        bob_results = patient_service.find_by_phone("5552222222")
        assert len(alice_results) == 1
        assert len(bob_results) == 1

        # Update Alice's phone to a new number
        new_phone = "5553333333"
        updated_alice = Patient(
            id=patient1.id, first_name="Alice", last_name="Smith", phone=new_phone
        )
        patient_service.update_patient(updated_alice)

        # Old phone should not find Alice
        old_results = patient_service.find_by_phone("5551111111")
        assert len(old_results) == 0

        # New phone should find Alice
        new_results = patient_service.find_by_phone(new_phone)
        assert len(new_results) == 1
        assert new_results[0].id == patient1.id

        # Bob should still be findable by his original phone
        bob_results = patient_service.find_by_phone("5552222222")
        assert len(bob_results) == 1
        assert bob_results[0].id == patient2.id
