"""Integration tests for patient edit flow."""

import pytest

from src.models.patient import Patient
from src.services.checkin_service import CheckInService
from src.services.patient_service import PatientService
from src.services.store import MemoryStore


class TestEditPatientFlow:
    """Integration tests for the patient edit workflow."""

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
    def checkin_service(self, store):
        """Create check-in service with test store."""
        return CheckInService(data_store=store)

    @pytest.fixture
    def existing_patient(self, patient_service):
        """Create an existing patient for editing tests."""
        return patient_service.create_minimal_patient("Jane", "Doe", "(555) 123-4567")

    def test_complete_patient_edit_flow(self, patient_service, existing_patient):
        """Test the complete flow of editing a patient's information."""
        original_phone = existing_patient.phone

        # Step 1: Retrieve the patient by their current phone
        found_patients = patient_service.find_by_phone(original_phone)
        assert len(found_patients) == 1
        patient_to_edit = found_patients[0]

        # Step 2: Modify patient information
        updated_patient = Patient(
            id=patient_to_edit.id,
            first_name="Jane",  # Keep same
            last_name="Smith",  # Changed last name
            phone="5559876543",  # Changed phone
            email="jane.smith@example.com",  # Added email
            address="123 Main St",  # Added address
        )

        # Step 3: Update the patient
        patient_service.update_patient(updated_patient)

        # Step 4: Verify old phone no longer finds the patient
        old_phone_results = patient_service.find_by_phone(original_phone)
        assert len(old_phone_results) == 0

        # Step 5: Verify new phone finds the updated patient
        new_phone_results = patient_service.find_by_phone("5559876543")
        assert len(new_phone_results) == 1
        updated_result = new_phone_results[0]

        assert updated_result.id == existing_patient.id
        assert updated_result.first_name == "Jane"
        assert updated_result.last_name == "Smith"
        assert updated_result.phone == "5559876543"
        assert updated_result.email == "jane.smith@example.com"
        assert updated_result.address == "123 Main St"

    def test_edit_patient_with_check_in_history(
        self, patient_service, checkin_service, existing_patient
    ):
        """Test editing a patient who has check-in history."""
        # Step 1: Patient checks in
        checkin = checkin_service.check_in_patient(existing_patient.id)
        assert checkin is not None

        # Step 2: Edit the patient's phone
        updated_patient = Patient(
            id=existing_patient.id,
            first_name=existing_patient.first_name,
            last_name=existing_patient.last_name,
            phone="5559876543",  # New phone
            email="updated@example.com",
        )
        patient_service.update_patient(updated_patient)

        # Step 3: Verify patient can still be found by new phone
        found_patients = patient_service.find_by_phone("5559876543")
        assert len(found_patients) == 1
        assert found_patients[0].id == existing_patient.id

        # Step 4: Verify check-in history is preserved
        # (In a real system, we'd verify the check-in still references the correct patient)
        todays_checkins = checkin_service.list_today()
        assert len(todays_checkins) == 1
        assert todays_checkins[0].patient_id == existing_patient.id

    def test_edit_patient_phone_creates_potential_duplicate(self, patient_service):
        """Test editing a patient's phone to match another patient's phone."""
        # Step 1: Create two patients
        patient1 = patient_service.create_minimal_patient(
            "Alice", "Johnson", "5551111111"
        )
        patient2 = patient_service.create_minimal_patient("Bob", "Wilson", "5552222222")

        # Step 2: Try to change patient1's phone to match patient2's phone
        conflicting_patient = Patient(
            id=patient1.id,
            first_name="Alice",
            last_name="Johnson",
            phone="5552222222",  # Same as patient2
        )

        # Step 3: Update should succeed (the service doesn't prevent duplicates)
        patient_service.update_patient(conflicting_patient)

        # Step 4: Verify both patients can be found by the same phone
        duplicate_results = patient_service.find_by_phone("5552222222")
        assert len(duplicate_results) == 2
        patient_ids = [p.id for p in duplicate_results]
        assert patient1.id in patient_ids
        assert patient2.id in patient_ids

    def test_edit_patient_validation_errors(self, patient_service, existing_patient):
        """Test that validation errors are handled during patient editing."""
        # Test empty first name
        with pytest.raises(ValueError, match="First name is required"):
            invalid_patient = Patient(
                id=existing_patient.id,
                first_name="",
                last_name="Doe",
                phone="5559876543",
            )
            patient_service.update_patient(invalid_patient)

        # Test empty last name
        with pytest.raises(ValueError, match="Last name is required"):
            invalid_patient = Patient(
                id=existing_patient.id,
                first_name="Jane",
                last_name="",
                phone="5559876543",
            )
            patient_service.update_patient(invalid_patient)

        # Test invalid phone
        with pytest.raises(ValueError, match="Phone must contain only digits"):
            invalid_patient = Patient(
                id=existing_patient.id,
                first_name="Jane",
                last_name="Doe",
                phone="not-a-phone",
            )
            patient_service.update_patient(invalid_patient)

    def test_edit_patient_preserves_minimal_record_status(self, patient_service):
        """Test that editing a minimal patient preserves its minimal status."""
        # Create minimal patient
        minimal_patient = patient_service.create_minimal_patient(
            "Test", "User", "5555555555"
        )

        # Edit to add email but keep minimal structure
        updated_patient = Patient(
            id=minimal_patient.id,
            first_name="Test",
            last_name="User",
            phone="5556666666",  # Changed phone
            email="test@example.com",  # Added email
        )
        patient_service.update_patient(updated_patient)

        # Verify patient was updated
        found_patients = patient_service.find_by_phone("5556666666")
        assert len(found_patients) == 1
        updated_result = found_patients[0]

        assert updated_result.email == "test@example.com"
        assert updated_result.phone == "5556666666"
        # Other fields should still be None/empty for minimal record
        assert updated_result.birth_date is None
        assert updated_result.address is None
        assert updated_result.notes is None

    def test_edit_patient_round_trip_consistency(
        self, patient_service, existing_patient
    ):
        """Test that editing and retrieving a patient maintains data consistency."""
        # Edit with all fields
        updated_patient = Patient(
            id=existing_patient.id,
            first_name="Updated",
            last_name="Name",
            phone="5551112222",
            email="updated@test.com",
            address="456 Oak Ave",
            notes="Updated notes",
        )

        patient_service.update_patient(updated_patient)

        # Retrieve by ID
        retrieved_by_id = patient_service.get_patient(existing_patient.id)
        assert retrieved_by_id is not None

        # Retrieve by phone
        retrieved_by_phone = patient_service.find_by_phone("5551112222")
        assert len(retrieved_by_phone) == 1
        retrieved_by_phone = retrieved_by_phone[0]

        # Both retrieval methods should return the same data
        assert retrieved_by_id.id == retrieved_by_phone.id
        assert retrieved_by_id.first_name == retrieved_by_phone.first_name
        assert retrieved_by_id.last_name == retrieved_by_phone.last_name
        assert retrieved_by_id.phone == retrieved_by_phone.phone
        assert retrieved_by_id.email == retrieved_by_phone.email
        assert retrieved_by_id.address == retrieved_by_phone.address
        assert retrieved_by_id.notes == retrieved_by_phone.notes

        # Verify all fields were updated correctly
        assert retrieved_by_id.first_name == "Updated"
        assert retrieved_by_id.last_name == "Name"
        assert retrieved_by_id.phone == "5551112222"
        assert retrieved_by_id.email == "updated@test.com"
        assert retrieved_by_id.address == "456 Oak Ave"
        assert retrieved_by_id.notes == "Updated notes"
