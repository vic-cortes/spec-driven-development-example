# Quickstart: Patient Check-In (Phone)

## Overview
Dental office patient check-in system with phone-based lookup, patient management, and today's arrivals tracking. Supports patient information editing and duplicate detection.

## Prerequisites
- Python 3.12+
- Virtual environment (recommended)

## Setup & Installation

### 1. Create Virtual Environment
```bash
python -m venv .venv
source .venv/bin/activate  # On macOS/Linux
# or
.venv\Scripts\activate  # On Windows
```

### 2. Install Dependencies
```bash
.venv/bin/python -m pip install -e .
# This installs flet, pytest, and other dependencies from pyproject.toml
```

### 3. Verify Installation
```bash
.venv/bin/python -c "import flet; print('Flet version:', flet.__version__)"
```

## Running the Application

### Desktop Application (Default)
```bash
.venv/bin/python main.py
```

### Web Browser Mode
```bash
.venv/bin/python -c "
import flet as ft
from src.ui.app import main
ft.app(target=main, view=ft.AppView.WEB_BROWSER, port=8550)
"
```

## Application Features

### User Story 1: Patient Check-In ✅
- Enter patient phone number
- Automatic patient lookup
- Create minimal patient record if not found
- One check-in per patient per day policy

### User Story 2: Today's Arrivals ✅  
- View all patients who checked in today
- Display check-in time and masked phone numbers
- Real-time updates when patients check in

### User Story 3: Patient Information Editing ✅
- Edit patient details (phone, email, address, notes)
- Automatic duplicate detection on phone changes
- Data validation and error handling
- Merge duplicate patient records

## Testing

### Run All Tests
```bash
.venv/bin/python -m pytest
```

### Run Specific Test Suites
```bash
# Unit tests only
.venv/bin/python -m pytest tests/unit/ -v

# Integration tests only  
.venv/bin/python -m pytest tests/integration/ -v

# Phase 5 tests (patient editing)
.venv/bin/python -m pytest tests/unit/test_patient_update_phone.py -v
.venv/bin/python -m pytest tests/integration/test_edit_patient_flow.py -v
```

### Test Core Functionality
```bash
.venv/bin/python -c "
from src.services.patient_service import patient_service
from src.services.checkin_service import checkin_service

# Test patient creation and lookup
patient = patient_service.create_minimal_patient('Test', 'User', '555-123-4567')
found = patient_service.find_by_phone('555-123-4567')
print(f'✓ Patient lookup: {len(found)} found')

# Test check-in
checkin = checkin_service.check_in_patient(patient.id)
print(f'✓ Check-in created: {checkin.timestamp}')

print('Core functionality verified!')
"
```

## Navigation & Usage

### Check-In Screen
1. Enter patient phone number
2. Click "Search" or press Enter
3. If patient found: Review details and check in
4. If not found: Enter name to create minimal patient record

### Arrivals Screen  
1. Click "Today's Arrivals" in navigation
2. View list of checked-in patients
3. Click edit button (✏️) on any patient to modify their information

### Patient Editing
1. Click edit button on patient card in arrivals view
2. Modify patient information in the dialog
3. System will warn if phone changes create potential duplicates
4. Save changes to update patient record

## Architecture

### Project Structure
```
src/
├── models/          # Data models (Patient, CheckIn)
├── services/        # Business logic (PatientService, CheckInService)
├── ui/             # User interface (Flet views and components)
├── utils/          # Utilities (phone normalization)
└── data/           # Mock data seeding

tests/
├── unit/           # Unit tests for services and models
└── integration/    # End-to-end workflow tests
```

### Key Components
- **PatientService**: Patient CRUD, lookup, duplicate detection
- **CheckInService**: Check-in workflow, daily arrivals
- **MemoryStore**: In-memory data storage with indexing
- **Privacy Logger**: PII-safe logging with phone masking

## Data Privacy & Security
- Phone numbers are masked in logs (***1234)
- In-memory storage only (no persistent database)
- PII data is never logged in plain text
- Patient information validation and sanitization

## Mobile Responsiveness
- Responsive layout using Flet's ResponsiveRow/Column
- Touch-friendly controls and button sizing
- Adaptive navigation (desktop rail vs mobile bottom nav)
- Optimized for iPad/iPhone screen sizes

## Troubleshooting

### Application Won't Start
```bash
# Check Python environment
.venv/bin/python --version

# Check Flet installation  
.venv/bin/python -c "import flet; print('OK')"

# Check for import errors
.venv/bin/python -c "from src.ui.app import main; print('Imports OK')"
```

### Tests Failing
```bash
# Clear any cache
.venv/bin/python -m pytest --cache-clear

# Run with verbose output
.venv/bin/python -m pytest -v -s

# Check specific test
.venv/bin/python -m pytest tests/unit/test_patient_update_phone.py::TestPatientUpdatePhone::test_update_patient_phone_affects_lookup -v
```

### Performance Issues
- Check system resources (memory usage)
- Restart application to clear in-memory store
- Use web browser mode for better performance on some systems

## Development Notes
- Application uses in-memory storage - data resets on restart
- Mock data is automatically seeded on startup
- All user stories (US1, US2, US3) are fully implemented
- Privacy-first design with PII masking throughout
