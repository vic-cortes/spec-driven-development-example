# Quick Start: International Phone Number Support

**Feature**: International Phone Number Support  
**Branch**: 002-international-phone  
**Date**: January 12, 2026

## Overview

This feature adds support for US (+1) and Mexican (+52) phone numbers to the dental patient check-in system. It includes strict validation, country code selection, and standardized display formatting.

## Setup Instructions

### Prerequisites

- Python 3.12+
- Flet 0.80.1
- SQLite database (existing)
- pytest for testing

### Installation Steps

1. **Check out the feature branch**:
   ```bash
   git checkout 002-international-phone
   ```

2. **Install dependencies** (if not already installed):
   ```bash
   pip install -e .
   ```

3. **Run database migration**:
   ```bash
   python scripts/migrate_phone_schema.py
   ```

4. **Run tests to verify setup**:
   ```bash
   pytest tests/unit/test_phone_validation.py -v
   pytest tests/integration/test_international_phone.py -v
   ```

## Feature Description

### What's New

1. **Country Code Selection**: Dropdown with +1 (US) and +52 (Mexico) options
2. **Strict Validation**: Exactly 10 digits required for all phone numbers  
3. **Standardized Format**: All phones display as "+{code} (xxx) xxx-xxxx"
4. **Backward Compatibility**: Existing US numbers automatically get +1 country code

### User Experience

#### Patient Registration Flow

1. **Country Selection**: Staff selects country code from dropdown
2. **Phone Entry**: Staff enters exactly 10 digits (validation in real-time)
3. **Automatic Formatting**: System formats as "+1 (555) 123-4567"
4. **Error Handling**: Clear messages for invalid input

#### Patient Editing Flow

1. **Load Existing**: Current phone displays with country code
2. **Edit Mode**: Dropdown and input pre-filled with current values
3. **Validation**: Same strict 10-digit validation applies
4. **Save**: Updated phone number stored with new formatting

### Technical Components

#### Core Services

- **PhoneValidationService**: Validates and formats phone numbers
- **Enhanced PatientService**: Creates/updates patients with international phones  
- **Phone Utilities**: Parsing and normalization functions

#### UI Components

- **InternationalPhoneInput**: Composite Flet component with dropdown + input
- **PhoneDisplayText**: Read-only formatted phone display
- **Updated PatientEditView**: Enhanced with international phone input

#### Database Changes

- **New Column**: `country_code` added to patients table
- **Migration**: Existing records get "+1" default country code
- **Validation**: Database constraints ensure data integrity

## Usage Examples

### Creating a Patient

```python
from src.services.patient_service import patient_service

# US patient
patient = patient_service.create_patient(
    first_name="John",
    last_name="Smith", 
    country_code="+1",
    phone_digits="5551234567"
)
print(patient.formatted_phone)  # "+1 (555) 123-4567"

# Mexican patient
patient = patient_service.create_patient(
    first_name="Maria",
    last_name="Garcia",
    country_code="+52", 
    phone_digits="5512345678"
)
print(patient.formatted_phone)  # "+52 (551) 234-5678"
```

### Phone Validation

```python
from src.services.phone_service import phone_service

# Validate US number
result = phone_service.validate_phone("+1", "5551234567")
print(result.is_valid)  # True
print(result.formatted)  # "+1 (555) 123-4567"

# Validate invalid number  
result = phone_service.validate_phone("+52", "123")
print(result.is_valid)  # False
print(result.error_message)  # "Phone number must be exactly 10 digits"
```

### UI Integration

```python
import flet as ft
from src.ui.components.international_phone_input import InternationalPhoneInput

def build_patient_form():
    phone_input = InternationalPhoneInput(
        on_change=handle_phone_change,
        default_country="+1"
    )
    
    return ft.Column([
        ft.TextField(label="First Name"),
        ft.TextField(label="Last Name"),
        phone_input,
        ft.ElevatedButton("Save", on_click=save_patient)
    ])
```

## Testing

### Run All Tests

```bash
# Unit tests
pytest tests/unit/test_phone_validation.py
pytest tests/unit/test_patient_model.py  
pytest tests/unit/test_phone_service.py

# Integration tests
pytest tests/integration/test_patient_registration.py
pytest tests/integration/test_phone_display.py

# All tests
pytest tests/ -v
```

### Test Coverage

- Phone validation logic (US and Mexican formats)
- Patient model with country code field
- UI component validation and formatting
- Database migration and data integrity  
- End-to-end patient registration flows

## Troubleshooting

### Common Issues

1. **"Phone must be exactly 10 digits"**
   - Solution: Remove all spaces, dashes, parentheses from input
   - Only enter digits 0-9

2. **Migration fails**
   - Solution: Backup database first, check SQLite version compatibility
   - Run: `python scripts/check_migration_status.py`

3. **Existing data displays incorrectly**
   - Solution: Verify migration completed successfully
   - All existing numbers should show "+1" country code

4. **Validation errors in UI**  
   - Solution: Check Flet version (requires 0.80.1+)
   - Verify error_text property is properly cleared

### Verification Commands

```bash
# Check database schema
sqlite3 database.db ".schema patients"

# Verify migration
python -c "from src.services.patient_service import patient_service; print(patient_service.get_all()[0].country_code)"

# Test phone formatting
python -c "from src.services.phone_service import phone_service; print(phone_service.format_phone('+1', '5551234567'))"
```

## Configuration

### Default Settings

- **Default Country**: +1 (US)
- **Supported Countries**: US (+1), Mexico (+52)
- **Validation**: Exactly 10 digits required
- **Display Format**: "+{code} (xxx) xxx-xxxx"

### Customization Options

Currently no configuration options available. Future versions may include:
- Additional country codes
- Custom display formatting
- Validation strictness levels

## Next Steps

After implementing this feature:

1. **User Training**: Train staff on country code selection
2. **Data Cleanup**: Review existing phone numbers for accuracy  
3. **Monitoring**: Monitor for validation errors and user feedback
4. **Future Enhancement**: Consider adding more country codes if needed

## Support

For issues or questions:
- Check existing tests for usage examples
- Review contracts/ directory for API specifications  
- Examine research.md for technical decisions and alternatives