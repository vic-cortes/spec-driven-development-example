# Data Model: International Phone Number Support

**Branch**: 002-international-phone  
**Date**: January 12, 2026  
**Status**: Phase 1 Complete

## Enhanced Entities

### Patient Entity (Updated)

**Purpose**: Core patient record with international phone support

**Fields**:
- `id`: string (UUID) - unique identifier  
- `first_name`: string - patient first name
- `last_name`: string - patient last name
- `phone`: string - normalized 10-digit phone number (digits only)
- `country_code`: string - phone country code ("+1" or "+52")
- `email`: optional string - contact email
- `birth_date`: optional date - date of birth
- `address`: optional string - mailing address
- `notes`: optional string - additional notes

**Relationships**: 
- One-to-many with CheckIn records
- Referenced by CheckInService for arrivals

**Validation Rules**:
- `first_name` and `last_name` required, non-empty
- `phone` must be exactly 10 digits (numeric string)
- `country_code` must be "+1" or "+52"
- `email` must be valid email format if provided

**New Properties**:
- `formatted_phone`: returns "+{country_code} ({area}) {exchange}-{number}"
- `international_phone`: returns full international format
- `masked_phone`: returns privacy-safe display format

### PhoneNumber Entity (New)

**Purpose**: Encapsulates phone number validation and formatting logic

**Fields**:
- `country_code`: string ("+1" or "+52")
- `digits`: string (exactly 10 digits)
- `raw_input`: string (original user input for auditing)

**Methods**:
- `validate()`: ensures 10-digit format and valid country code
- `format_display()`: returns "+{code} (xxx) xxx-xxxx" format
- `format_masked()`: returns privacy-safe "***-xxxx" format
- `is_valid()`: boolean validation check

**Validation Rules**:
- Digits must be exactly 10 characters, all numeric
- Country code must be "+1" or "+52"
- No letters, spaces, or special characters in digits field

### CountryCode Entity (New)

**Purpose**: Defines supported country codes and validation rules

**Fields**:
- `code`: string ("+1" or "+52") 
- `name`: string ("United States" or "Mexico")
- `display_name`: string ("+1 (US)" or "+52 (Mexico)")
- `pattern`: regex pattern for validation
- `format_template`: template for display formatting

**Static Data**:
```python
SUPPORTED_COUNTRIES = [
    CountryCode("+1", "United States", "+1 (US)", "^[0-9]{10}$", "+1 ({area}) {exchange}-{number}"),
    CountryCode("+52", "Mexico", "+52 (Mexico)", "^[0-9]{10}$", "+52 ({area}) {exchange}-{number}")
]
```

## Database Schema Changes

### Migration Script

```sql
-- Add country_code column to existing patients table
ALTER TABLE patients ADD COLUMN country_code TEXT DEFAULT '+1';

-- Update any existing NULL values to default US
UPDATE patients SET country_code = '+1' WHERE country_code IS NULL;

-- Add index for phone lookups with country code
CREATE INDEX IF NOT EXISTS idx_patients_phone_country ON patients(phone, country_code);
```

### Updated Schema

```sql
CREATE TABLE patients (
    id TEXT PRIMARY KEY,
    first_name TEXT NOT NULL,
    last_name TEXT NOT NULL,
    phone TEXT NOT NULL,
    country_code TEXT NOT NULL DEFAULT '+1',
    email TEXT,
    birth_date DATE,
    address TEXT,
    notes TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    
    CONSTRAINT check_country_code CHECK (country_code IN ('+1', '+52')),
    CONSTRAINT check_phone_format CHECK (phone GLOB '[0-9][0-9][0-9][0-9][0-9][0-9][0-9][0-9][0-9][0-9]'),
    CONSTRAINT check_phone_length CHECK (length(phone) = 10)
);
```

## State Transitions

### Phone Number Input Flow

1. **Initial State**: Empty form with country dropdown defaulted to "+1"
2. **Country Selection**: User selects country code from dropdown 
3. **Phone Input**: User enters 10-digit number (validation on each keystroke)
4. **Validation**: System validates exact 10-digit format
5. **Success State**: Phone formatted and displayed as "+{code} (xxx) xxx-xxxx"
6. **Error State**: Clear validation message shown for invalid input

### Data Storage Flow

1. **Input Normalization**: Remove all non-digit characters from user input
2. **Validation**: Ensure exactly 10 digits remain
3. **Country Code Assignment**: Store selected country code with normalized digits
4. **Persistence**: Save to database with constraints enforced
5. **Retrieval**: Load country code and digits, format for display

### Display Flow

1. **Data Loading**: Retrieve country_code and phone from database
2. **Format Selection**: Choose display format based on context (full, masked, etc.)
3. **Formatting**: Apply template to create consistent display
4. **Rendering**: Show formatted phone in UI components

## Backward Compatibility

### Existing Data Handling

- All existing phone numbers assumed to be US (+1) format
- Migration script adds "+1" country code to existing records
- Display logic updated to use new formatting while preserving data
- Validation remains the same (10-digit requirement)

### API Compatibility

- Existing `masked_phone` property maintained for backward compatibility
- New `formatted_phone` property added for international display
- `phone` field continues to store normalized digits-only format
- Country code stored separately to maintain data integrity