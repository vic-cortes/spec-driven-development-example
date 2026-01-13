# Feature Specification: Patient Check-In (Phone)

**Feature Branch**: `[001-patient-checkin]`  
**Created**: 2026-01-12  
**Status**: Draft  
**Input**: User description: "Modern in-clinic dental app; patient phone-based check-in; mock data allowed; English specs."

## User Scenarios & Testing *(mandatory)*

### User Story 1 - Check in a patient by phone (Priority: P1)

Reception staff enters a patient's phone number to register arrival. If the phone matches an existing patient, the system confirms check-in and displays the patient's name. If no match exists, staff can quickly create a minimal patient record and complete check-in.

**Why this priority**: Check-in is the primary entry point that enables all clinic workflows; without it, staff cannot organize the day's schedule.

**Independent Test**: Enter a phone number on the check-in screen and verify either a match confirmation or a minimal patient creation flow; results are saved to the local check-in log.

**Acceptance Scenarios**:

1. **Given** a known phone exists, **When** staff inputs that phone, **Then** the system confirms the patient's check-in with name and timestamp.
2. **Given** a phone is not found, **When** staff chooses "Create minimal record" and enters first/last name with phone, **Then** the system creates the record and confirms check-in.

---

### User Story 2 - View today's arrivals list (Priority: P2)

Assistants and doctors can view a simple list of all checked-in patients for the current day including time and status.

**Why this priority**: Staff needs situational awareness to coordinate patient flow.

**Independent Test**: Perform one or more check-ins; open the "Today's arrivals" view and verify all entries are listed and can be filtered by time.

**Acceptance Scenarios**:

1. **Given** patients have checked in, **When** staff opens today's arrivals, **Then** the list shows patient name, phone (masked), and check-in time.
2. **Given** no patients have checked in, **When** staff opens today's arrivals, **Then** the view shows an empty state message.

---

### User Story 3 - Correct a phone or basic details (Priority: P3)

Staff can edit a patient's phone or basic details when an error is detected, ensuring records remain accurate.

**Why this priority**: Data accuracy reduces friction and prevents duplicates.

**Independent Test**: Select an existing patient, edit phone or name, and verify the change reflects in subsequent searches and the arrivals log.

**Acceptance Scenarios**:

1. **Given** a patient's phone is incorrect, **When** staff updates the phone, **Then** future check-ins use the new phone successfully.
2. **Given** a duplicate minimal record is detected, **When** staff merges or deletes the duplicate [NEEDS CLARIFICATION: merge vs delete policy], **Then** check-ins reference a single correct patient record.

---

### Edge Cases

- Phone number entered with formatting (spaces, dashes) should be normalized before search.
- Invalid or too-short phone numbers must be rejected with a clear message.
- Multiple patients sharing a phone (family) must be disambiguated [NEEDS CLARIFICATION: prompt selection vs enforce unique phone].
- Repeated check-in on the same day should either update the existing entry or prevent duplicates [NEEDS CLARIFICATION: allow multiple entries vs single per day].

## Requirements *(mandatory)*

### Functional Requirements

- **FR-001**: System MUST allow staff to register a patient's arrival using a phone number and store a timestamped check-in entry.
- **FR-002**: System MUST search existing patients by normalized phone number and confirm check-in when a match is found.
- **FR-003**: System MUST provide a minimal patient creation flow (first_name, last_name, phone) when no match is found.
- **FR-004**: System MUST provide a "Today's arrivals" view listing all check-ins for the current day.
- **FR-005**: System MUST operate entirely on the clinic's local machine and avoid network access for patient data.
- **FR-006**: System MUST determine how a patient is routed to a doctor/specialty after check-in [NEEDS CLARIFICATION: manual selection at check-in vs separate assignment workflow].
- **FR-007**: System MUST define the retention period for check-in history [NEEDS CLARIFICATION: keep N days/months vs indefinite local history].
- **FR-008**: System MUST prevent logs from containing PII (no full phone/name in logs; mask where necessary).
- **FR-009**: System MUST support loading mock data to demonstrate functionality without real patient data.

### Key Entities *(include if feature involves data)*

- **Patient**: Represents an individual receiving care; key attributes include name, phone, optional basic demographics. Phone used for lookup; uniqueness policy is TBD.
- **CheckIn**: Represents a single arrival event; attributes include patient reference, check-in timestamp, day/date, optional status/note for routing.

### Assumptions

- Check-in occurs on a single local workstation inside the clinic.
- Phone numbers are normalized (digits-only) before search and storage.
- Phone is the primary lookup key but may not be globally unique (family/shared numbers possible).
- Demonstration may use mock data; no real patient data is required.

## Success Criteria *(mandatory)*

### Measurable Outcomes

- **SC-001**: Staff completes patient check-in in under 30 seconds for known patients (from entering phone to confirmation).
- **SC-002**: 95% of known patients are matched by phone on first attempt (normalized input).
- **SC-003**: "Today's arrivals" view loads in under 2 seconds with up to 200 entries.
- **SC-004**: 100% check-in operations function without network connectivity; no patient PII appears in application logs.
