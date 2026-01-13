---

description: "Task list for Patient Check-In (Phone)"
---

# Tasks: Patient Check-In (Phone)

**Input**: Design documents from `/specs/001-patient-checkin/`
**Prerequisites**: plan.md (required), spec.md (required), research.md, data-model.md, contracts/

**Tests**: Tests are included per constitution (Test-First). Write tests first.

**Organization**: Tasks are grouped by user story to enable independent implementation and testing.

## Format: `[ID] [P?] [Story] Description`

- **[P]**: Can run in parallel (different files, no dependencies)
- **[Story]**: Which user story this task belongs to (e.g., US1, US2, US3)
- Include exact file paths in descriptions

## Path Conventions

- Single project: source in `src/`, tests in `tests/`

---

## Phase 1: Setup (Shared Infrastructure)

**Purpose**: Project initialization and basic structure

- [x] T001 Create directories: `src/models/`, `src/services/`, `src/ui/`, `src/data/`, `src/utils/`, `tests/unit/`, `tests/integration/`
- [x] T002 [P] Add Flet dependency in `pyproject.toml` under `[project.dependencies]`
- [x] T003 [P] Create pytest config `tests/conftest.py` (basic setup)
- [x] T004 [P] Update entrypoint to run Flet app in `main.py`

---

## Phase 2: Foundational (Blocking Prerequisites)

**Purpose**: Core infrastructure that MUST be complete before ANY user story

**⚠️ CRITICAL**: No user story work can begin until this phase is complete

- [x] T005 Create Patient model in `src/models/patient.py`
- [x] T006 [P] Create CheckIn model in `src/models/checkin.py`
- [x] T007 [P] Implement phone normalization utility in `src/utils/phone.py`
- [x] T008 Implement in-memory store for patients/check-ins in `src/services/store.py`
- [x] T009 Configure privacy-safe logging (mask phones) in `src/services/logger.py`
- [x] T010 [P] Add mock data seeding script in `src/data/mock_seed.py`

**Checkpoint**: Foundation ready — user story implementation can now begin in parallel

---

## Phase 3: User Story 1 — Check in a patient by phone (Priority: P1) 🎯 MVP

**Goal**: Staff can register arrival by phone; create minimal patient if not found

**Independent Test**: Enter a phone on the check-in screen; confirm match or minimal creation; log saved locally

### Tests for User Story 1 (write FIRST)

- [x] T011 [P] [US1] Unit test: phone normalization in `tests/unit/test_phone.py`
- [x] T012 [P] [US1] Unit test: patient lookup by phone in `tests/unit/test_patient_lookup.py`
- [x] T013 [P] [US1] Integration test: check-in flow in `tests/integration/test_checkin_flow.py`

### Implementation for User Story 1

- [x] T014 [P] [US1] Implement `PatientService` (lookup/create minimal) in `src/services/patient_service.py`
- [x] T015 [P] [US1] Implement `CheckInService` (single-per-day policy) in `src/services/checkin_service.py`
- [x] T016 [US1] Implement Flet Check-In screen in `src/ui/checkin_view.py`
- [x] T017 [US1] Wire Flet app shell and navigation in `src/ui/app.py`
- [x] T018 [US1] Ensure masked phone logging during check-in in `src/services/logger.py`
- [x] T019 [US1] Seed demo patients in `src/data/mock_seed.py`

**Checkpoint**: User Story 1 fully functional and testable independently

---

## Phase 4: User Story 2 — View today's arrivals list (Priority: P2)

**Goal**: Staff sees list of today's check-ins with time and masked phone

**Independent Test**: Perform check-ins; verify list shows entries; empty state when none

### Tests for User Story 2 (write FIRST)

- [x] T020 [P] [US2] Integration test: arrivals list view in `tests/integration/test_arrivals_view.py`
- [x] T021 [P] [US2] Unit test: list today's check-ins in `tests/unit/test_checkins_today.py`

### Implementation for User Story 2

- [x] T022 [P] [US2] Implement arrivals view UI in `src/ui/arrivals_view.py`
- [x] T023 [US2] Add service method `list_today()` in `src/services/checkin_service.py`
- [x] T024 [US2] Mask phone display in `src/ui/arrivals_view.py`

**Checkpoint**: User Stories 1 and 2 work independently

---

## Phase 5: User Story 3 — Correct phone or basic details (Priority: P3)

**Goal**: Staff edits patient phone/details; merges duplicates per policy

**Independent Test**: Edit phone or name; verify in lookup and arrivals log

### Tests for User Story 3 (write FIRST)

- [ ] T025 [P] [US3] Unit test: update patient phone affects lookup in `tests/unit/test_patient_update_phone.py`
- [ ] T026 [P] [US3] Integration test: edit patient flow in `tests/integration/test_edit_patient_flow.py`

### Implementation for User Story 3

- [ ] T027 [P] [US3] Implement patient edit view in `src/ui/patient_edit_view.py`
- [ ] T028 [US3] Implement update/validation in `src/services/patient_service.py`
- [ ] T029 [US3] Implement merge-first duplicate resolution in `src/services/patient_service.py`

**Checkpoint**: All user stories independently functional

---

## Phase N: Polish & Cross-Cutting Concerns

**Purpose**: Improvements across stories

- [ ] T030 [P] Documentation updates in `specs/001-patient-checkin/quickstart.md`
- [ ] T031 Code cleanup and Flet performance tweaks across `src/ui/`
- [ ] T032 [P] Additional unit tests in `tests/unit/`
- [ ] T033 Privacy & logging hardening in `src/services/logger.py`
- [ ] T034 Run quickstart validation using `specs/001-patient-checkin/quickstart.md`

---

## Dependencies & Execution Order

### Phase Dependencies

- Setup (Phase 1): No dependencies — start immediately
- Foundational (Phase 2): Depends on Setup — BLOCKS all user stories
- User Stories (Phase 3+): Depend on Foundational; proceed in priority order (P1 → P2 → P3) or in parallel
- Polish (Final Phase): Depends on desired user stories being complete

### User Story Dependencies

- User Story 1 (P1): No dependency on other stories
- User Story 2 (P2): Independent; may read data produced by US1
- User Story 3 (P3): Independent; updates Patient records used by US1/US2

### Within Each User Story

- Tests MUST be written and FAIL before implementation
- Models → Services → UI in order
- Keep stories independent; minimize cross-story coupling

### Parallel Opportunities

- [P] Setup tasks (T002–T004) can run together
- [P] Foundational tasks (T006–T010) can run together
- After Foundational, US1/US2/US3 can proceed in parallel by different devs
- [P] Test tasks and model creation within stories can run in parallel

---

## Parallel Example: User Story 1

```bash
# Parallelizable tasks for US1:
# Tests
Task: "Unit test: phone normalization in tests/unit/test_phone.py"
Task: "Unit test: patient lookup by phone in tests/unit/test_patient_lookup.py"
Task: "Integration test: check-in flow in tests/integration/test_checkin_flow.py"

# Models & Services
Task: "Implement PatientService in src/services/patient_service.py"
Task: "Implement CheckInService in src/services/checkin_service.py"
```

---

## Implementation Strategy

### MVP First (User Story 1 Only)

1. Complete Setup (Phase 1)
2. Complete Foundational (Phase 2)
3. Complete User Story 1 (Phase 3)
4. STOP and VALIDATE: Run tests and demo check-in flow

### Incremental Delivery

1. Setup + Foundational → foundation ready
2. Add US1 → test independently → demo
3. Add US2 → test independently → demo
4. Add US3 → test independently → demo

### Mobile Readiness

- Use Flet responsive layout (`ResponsiveRow`, `Column`, `Row`, `expand`) to adapt to iPad/iPhone sizes
- Touch-friendly controls; mask PII; offline-only behavior respected
