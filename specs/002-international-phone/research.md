# Research Phase: International Phone Number Support

**Branch**: 002-international-phone  
**Date**: January 12, 2026  
**Status**: Phase 0 Complete

## Research Tasks Completed

### 1. Flet Dropdown Components for Country Code Selection

**Decision**: Use `ft.Dropdown` with country code options  
**Rationale**: Native Flet component provides clean UI with value/text separation. Supports setting default values and change event handlers.  
**Implementation**: 
```python
country_dropdown = ft.Dropdown(
    label="Country Code",
    options=[
        ft.dropdown.Option(key="+1", text="+1 (US)"),
        ft.dropdown.Option(key="+52", text="+52 (Mexico)")
    ],
    value="+1",  # Default to US
    width=150
)
```

### 2. Phone Number Validation Patterns

**Decision**: Use regex patterns for strict 10-digit validation  
**Rationale**: Simple, fast, offline validation. No external dependencies required.  
**Patterns**:
- US: `^[0-9]{10}$` (exactly 10 digits)
- Mexico: `^[0-9]{10}$` (exactly 10 digits, current format)
- Combined validation with country code context

### 3. SQLite Schema Migration Strategy

**Decision**: Add `country_code` column with default "+1" for backward compatibility  
**Rationale**: Preserves existing data while enabling new international features. Default to US for existing records.  
**Migration**:
```sql
ALTER TABLE patients ADD COLUMN country_code TEXT DEFAULT '+1';
```

### 4. Phone Number Display Formatting

**Decision**: Implement format function `format_international_phone(country_code, digits)`  
**Rationale**: Centralized formatting logic ensures consistency across all UI components.  
**Format Pattern**: `+{country_code} ({area}) {exchange}-{number}`
- Example: "+1 (555) 123-4567", "+52 (551) 234-5678"

### 5. Form Validation Integration with Flet

**Decision**: Use Flet's built-in field validation with custom error messages  
**Rationale**: Maintains consistency with existing form validation patterns in the application.  
**Implementation**: Set `error_text` property on TextField when validation fails, clear when valid.

### 6. Backward Compatibility for Existing Phone Numbers

**Decision**: Migrate existing phone numbers by adding "+1" country code  
**Rationale**: Existing data is US-format, safe to assume US country code for all existing records.  
**Process**: 
1. Add country_code column with default "+1"
2. Update display logic to use new format
3. Maintain existing phone validation for data integrity

## Technical Decisions Summary

| Component | Decision | Alternative Considered |
|-----------|----------|----------------------|
| Country Selection | ft.Dropdown | ft.RadioGroup (rejected: takes more space) |
| Validation | Regex patterns | External library (rejected: adds dependency) |
| Database Migration | ADD COLUMN with default | New table (rejected: over-engineering) |
| Display Format | Centralized formatter | Component-level formatting (rejected: inconsistent) |
| Error Handling | Flet error_text | Modal dialogs (rejected: poor UX) |

## Implementation Approach

1. **Phase 1**: Enhance phone utilities with international support
2. **Phase 2**: Update Patient model with country_code field  
3. **Phase 3**: Enhance UI components with country dropdown
4. **Phase 4**: Update database schema with migration
5. **Phase 5**: Update display logic across all views

All research complete. Ready for Phase 1: Design & Contracts.