# Dental Patient Registry Constitution

## Core Principles

### I. Flet-First UI
- Build a desktop app using Flet only (no web server).
- Provide three main views: Patients, Appointments, Treatments.
- Use simple forms with validation and clear feedback (success/error).

### II. Local Persistence (SQLite)
- Store all data locally in a single SQLite database file.
- Validate inputs before writing; handle CRUD errors gracefully.
- Optional daily backup of the DB file to a `backups/` folder.

### III. Test-First (Non-Negotiable)
- Write tests before implementation for every feature.
- Unit tests for models and services; smoke tests for critical flows.
- Keep tests fast and deterministic.

### IV. Minimal Integration Testing
- Cover DB read/write and service–UI boundary with a few integration tests.
- Ensure patient creation, appointment scheduling, and treatment logging work end-to-end.

### V. Simplicity & Privacy
- Collect only necessary patient data; avoid storing sensitive notes when not required.
- No network access for patient data; logs must not include PII.
- Prefer straightforward code over abstractions until needed.

## Technical Baseline
- Python: >= 3.12
- UI: Flet >= 0.21
- Database: SQLite (standard library `sqlite3`)
- Testing: pytest (optional: pytest-cov)
- Suggested layout: `models/`, `services/`, `ui/`, `data/`, `tests/`.

### Minimal Data Model
- Patient: first_name, last_name, id_number, phone, email, birth_date, address, notes
- Appointment: patient_id, datetime, reason, status (scheduled/done/cancelled)
- Treatment: patient_id, description, date, cost, payment_status

## Development Workflow
1. Specify behavior (short spec or scenario).
2. Write failing tests (RED).
3. Implement the minimal code to pass (GREEN).
4. Refactor with tests green (REFACTOR).
5. Add/adjust UI forms and navigation in Flet.

### Code Standards
- PEP 8 style, type hints on public functions, concise docstrings.
- Domain names in English and self-explanatory.

## Governance
- This constitution defines the minimal, non-negotiable constraints.
- Every PR must include tests for new/changed behavior.
- Changes to data model require migration notes and tests.

**Version**: 1.0.0 | **Ratified**: 2026-01-12 | **Last Amended**: 2026-01-12
