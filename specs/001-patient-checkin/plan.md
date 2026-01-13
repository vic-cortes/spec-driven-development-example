# Implementation Plan: Patient Check-In (Phone)

**Branch**: `[001-patient-checkin]` | **Date**: 2026-01-12 | **Spec**: `/specs/001-patient-checkin/spec.md`
**Input**: Feature specification from `/specs/001-patient-checkin/spec.md`

**Note**: This template is filled in by the `/speckit.plan` command. See `.specify/templates/commands/plan.md` for the execution workflow.

## Summary

Primary requirement: Staff registers patient arrival by phone; view today's arrivals; edit basic details. No database now; use mock/in-memory data. Prepare UI to scale to iPad/iPhone via responsive Flet layouts.

Technical approach: Implement a Flet desktop/mobile-ready interface with an in-memory store for Patients and CheckIns, normalized phone lookups, and a single-per-day check-in policy. Add mock seeding and privacy-safe logging. Later iterations can swap the store for SQLite with minimal changes via a service layer.

## Technical Context

<!--
  ACTION REQUIRED: Replace the content in this section with the technical details
  for the project. The structure here is presented in advisory capacity to guide
  the iteration process.
-->

**Language/Version**: Python 3.12  
**Primary Dependencies**: Flet (UI), typing-extensions (if needed)  
**Storage**: In-memory mock store (no DB for now)  
**Testing**: pytest (unit + simple integration)  
**Target Platform**: Desktop (macOS) + iPad/iPhone readiness (responsive UI)  
**Project Type**: Single desktop app with responsive UI  
**Performance Goals**: UI loads under 2s; interactions feel instant; 60 fps where applicable  
**Constraints**: Offline-only; no PII in logs; single check-in per patient per day; phone normalization  
**Scale/Scope**: Single clinic workstation; up to hundreds of check-ins/day; small patient set (mock)

## Constitution Check

*GATE: Must pass before Phase 0 research. Re-check after Phase 1 design.*

From constitution:
- Flet-first UI: Compliant (Flet chosen).
- Local Persistence (SQLite): TEMPORARY DEVIATION — using in-memory mock store for MVP; plan to add SQLite later via service layer without changing UI contracts.
- Test-First: Compliant — pytest for unit/integration.
- Minimal Integration Testing: Compliant — in-memory read/write and UI boundary tests.
- Simplicity & Privacy: Compliant — collect minimal data; mask phone in logs; offline-only.

Gate decision: PASS with a documented temporary deviation (storage). Justification: user requested no DB for now; mock data acceptable; architecture prepared to swap storage later.

Re-check (post Phase 1 design): PASS — design documents align with constitution, storage deviation remains justified with clear migration path.

## Project Structure

### Documentation (this feature)

```text
specs/[###-feature]/
├── plan.md              # This file (/speckit.plan command output)
├── research.md          # Phase 0 output (/speckit.plan command)
├── data-model.md        # Phase 1 output (/speckit.plan command)
├── quickstart.md        # Phase 1 output (/speckit.plan command)
├── contracts/           # Phase 1 output (/speckit.plan command)
└── tasks.md             # Phase 2 output (/speckit.tasks command - NOT created by /speckit.plan)
```

### Source Code (repository root)
<!--
  ACTION REQUIRED: Replace the placeholder tree below with the concrete layout
  for this feature. Delete unused options and expand the chosen structure with
  real paths (e.g., apps/admin, packages/something). The delivered plan must
  not include Option labels.
-->

```text
src/
├── models/
├── services/
├── ui/
└── data/

tests/
├── unit/
└── integration/
```

**Structure Decision**: Use a single-project Python app. UI in `src/ui/`, domain models in `src/models/`, service layer with in-memory store in `src/services/`, mock data in `src/data/`. Tests under `tests/`.

## Complexity Tracking

> **Fill ONLY if Constitution Check has violations that must be justified**

| Violation | Why Needed | Simpler Alternative Rejected Because |
|-----------|------------|-------------------------------------|
| [e.g., 4th project] | [current need] | [why 3 projects insufficient] |
| [e.g., Repository pattern] | [specific problem] | [why direct DB access insufficient] |

| Temporary no-DB | User explicitly requested mock/no DB | Service layer allows future SQLite swap with minimal changes |
