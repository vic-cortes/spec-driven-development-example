# Tasks: International Phone Number Support

**Input**: Design documents from `/specs/002-international-phone/`
**Prerequisites**: plan.md (required), spec.md (required for user stories), research.md, data-model.md, contracts/

**Tests**: Tests are included as this feature requires strict validation and backward compatibility verification.

**Organization**: Tasks are grouped by user story to enable independent implementation and testing of each story.

## Format: `[ID] [P?] [Story] Description`

- **[P]**: Can run in parallel (different files, no dependencies)
- **[Story]**: Which user story this task belongs to (e.g., US1, US2, US3)
- Include exact file paths in descriptions

## Phase 1: Setup (Shared Infrastructure)

**Purpose**: Project initialization and international phone support infrastructure

- [x] T001 Create PhoneNumber entity in src/models/phone_number.py
- [x] T002 Create PhoneValidationService in src/services/phone_service.py
- [x] T003 [P] Create database migration script for country_code column

---

## Phase 2: Foundational (Blocking Prerequisites)

**Purpose**: Core phone validation infrastructure that MUST be complete before ANY user story implementation

**⚠️ CRITICAL**: No user story work can begin until this phase is complete

- [x] T004 Enhance existing phone utilities in src/utils/phone.py with international validation
- [x] T005 [P] Create unit tests for phone validation in tests/unit/test_phone_validation.py
- [x] T006 [P] Create unit tests for phone service in tests/unit/test_phone_service.py
- [x] T007 Execute database migration to add country_code field to patients table
- [x] T008 Update Patient model in src/models/patient.py with country_code field and formatted_phone property

**Checkpoint**: Foundation ready - user story implementation can now begin in parallel

---

## Phase 3: User Story 1 - US Phone Number Support (Priority: P1) 🎯 MVP

**Goal**: Enable registration and management of US patients with properly formatted +1 phone numbers

**Independent Test**: Enter US phone number during patient registration, verify it's formatted as "+1 (555) 123-4567" and stored correctly

### Tests for User Story 1

> **NOTE: Write these tests FIRST, ensure they FAIL before implementation**

- [x] T009 [P] [US1] Unit tests for US phone formatting in tests/unit/test_patient_model.py
- [x] T010 [P] [US1] Integration test for US patient registration in tests/integration/test_patient_registration.py

### Implementation for User Story 1

- [x] T011 [P] [US1] Implement US phone validation logic in PhoneValidationService
- [x] T012 [P] [US1] Add US phone formatting to Patient.formatted_phone property
- [x] T013 [US1] Update PatientService.create_patient in src/services/patient_service.py to handle country_code parameter
- [x] T014 [US1] Enhance checkin_view.py with country code dropdown defaulting to +1
- [x] T015 [US1] Update patient registration form validation to require exactly 10 digits
- [x] T016 [US1] Update arrivals view in src/ui/arrivals_view.py to display formatted US phone numbers

**Checkpoint**: US patients can be registered with +1 phone numbers and display correctly throughout the application

---

## Phase 4: User Story 2 - Mexican Phone Number Support (Priority: P2)

**Goal**: Enable registration and management of Mexican patients with properly formatted +52 phone numbers

**Independent Test**: Enter Mexican phone number with +52 country code, verify it's formatted as "+52 (551) 234-5678" and validates correctly

### Tests for User Story 2

- [x] T017 [P] [US2] Unit tests for Mexican phone formatting in tests/unit/test_phone_validation.py
- [x] T018 [P] [US2] Integration test for Mexican patient registration in tests/integration/test_patient_registration.py

### Implementation for User Story 2

- [x] T019 [P] [US2] Implement Mexican phone validation logic in PhoneValidationService  
- [x] T020 [P] [US2] Add Mexican phone formatting support to Patient.formatted_phone property
- [x] T021 [US2] Add +52 option to country code dropdown in checkin_view.py
- [x] T022 [US2] Update validation error messages for Mexican phone format requirements
- [x] T023 [US2] Test Mexican phone display formatting in arrivals view and patient edit view
- [x] T024 [US2] Create integration test for Mexican patient workflow in tests/integration/test_phone_display.py

**Checkpoint**: Mexican patients can be registered with +52 phone numbers with proper validation and display formatting

---

## Phase 5: User Story 3 - Country Code Selection and Strict Validation (Priority: P3)

**Goal**: Implement mandatory country code selection and strict 10-digit validation to ensure data quality

**Independent Test**: Attempt to save patient with invalid phone length, verify clear validation error; test country code dropdown functionality

### Tests for User Story 3

- [ ] T025 [P] [US3] Unit tests for strict validation rules in tests/unit/test_phone_validation.py
- [ ] T026 [P] [US3] UI component tests for country dropdown in tests/integration/test_phone_input_validation.py

### Implementation for User Story 3

- [ ] T027 [P] [US3] Create InternationalPhoneInput component in src/ui/components/international_phone_input.py
- [ ] T028 [P] [US3] Implement real-time validation feedback in phone input component
- [ ] T029 [US3] Update patient_edit_view.py to use InternationalPhoneInput component
- [ ] T030 [US3] Add comprehensive validation error messages for all invalid phone scenarios
- [ ] T031 [US3] Implement country code change handling with validation reset
- [ ] T032 [US3] Add form submission validation to prevent saving invalid phone numbers

**Checkpoint**: All phone number entries require country code selection and pass strict 10-digit validation

---

## Phase 6: Polish & Cross-cutting Concerns

**Purpose**: Finalization, performance optimization, and comprehensive testing

- [ ] T033 [P] Update existing patient records with default +1 country code via data migration
- [ ] T034 [P] Create comprehensive end-to-end test in tests/integration/test_international_phone_complete.py
- [ ] T035 [P] Update privacy logging to handle international phone number masking
- [ ] T036 [P] Performance test phone validation and formatting under load
- [ ] T037 Add backward compatibility tests for existing phone number data
- [ ] T038 Update quickstart documentation with final implementation details
- [ ] T039 Create phone number troubleshooting guide for common validation errors

---

## Dependencies

### User Story Dependencies
- **User Story 1**: Can start immediately after Phase 2
- **User Story 2**: Can start in parallel with User Story 1 (independent)
- **User Story 3**: Can start after foundational validation is complete (T004-T008)

### Parallel Execution Opportunities

#### Within User Story 1:
- T009, T010 (tests) can run in parallel
- T011, T012 (validation and formatting) can run in parallel
- T014, T015, T016 (UI updates) can run after T013 (service update)

#### Within User Story 2:
- T017, T018 (tests) can run in parallel
- T019, T020 (validation and formatting) can run in parallel 
- T021, T022, T023 (UI updates) can run in parallel after validation is ready

#### Within User Story 3:
- T025, T026 (tests) can run in parallel
- T027, T028 (component creation) can run in parallel
- T030, T031, T032 (validation enhancements) can run after component is ready

#### Phase 6 Polish:
- T033, T034, T035, T036 can all run in parallel
- T037 depends on data migration (T033)

---

## Implementation Strategy

### MVP Approach
**Recommended MVP**: User Story 1 only (US phone number support)
- Provides immediate value for primary user base
- Establishes international phone infrastructure
- Can be deployed independently for US-only operations

### Incremental Delivery
1. **Phase 1-2 + User Story 1**: US phone support MVP
2. **+ User Story 2**: Full US/Mexican phone support
3. **+ User Story 3**: Enhanced validation and UX polish
4. **+ Phase 6**: Production-ready with full testing

### Quality Gates
- All tests must pass before story completion
- Integration tests verify end-to-end story functionality
- Backward compatibility maintained throughout
- Performance benchmarks met (< 2 second validation/formatting)