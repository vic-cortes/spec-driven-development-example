# Implementation Plan: International Phone Number Support

**Branch**: `002-international-phone` | **Date**: January 12, 2026 | **Spec**: [spec.md](./spec.md)
**Input**: Feature specification from `/specs/002-international-phone/spec.md`

## Summary

Add support for US (+1) and Mexican (+52) phone numbers with strict 10-digit validation, mandatory country code dropdown selection, and standardized "+{code} (xxx) xxx-xxxx" display formatting. Enhance existing Flet-based dental patient registration system with international phone capabilities while maintaining backward compatibility.

## Technical Context

**Language/Version**: Python 3.12  
**Primary Dependencies**: Flet 0.80.1 (GUI framework), pytest 9.0.2  
**Storage**: SQLite (local persistence via existing store service)  
**Testing**: pytest with existing unit/integration structure  
**Target Platform**: Desktop application (Flet-based)  
**Project Type**: Single Flet desktop application  
**Performance Goals**: < 2 second phone validation and formatting  
**Constraints**: Offline-capable, no network dependencies for validation  
**Scale/Scope**: Enhanced phone support for existing patient registration system

## Constitution Check

*GATE: Must pass before Phase 0 research. Re-check after Phase 1 design.*

✅ **I. Flet-First UI**: Enhanced existing Flet components with international phone input (dropdown + text field). No additional frameworks introduced.  
✅ **II. Local Persistence (SQLite)**: Added country_code column to existing SQLite schema. No external database dependencies.  
✅ **III. Test-First (Non-Negotiable)**: Research phase identified test strategy. Unit tests for validation service, integration tests for UI flows.  
✅ **IV. Minimal Integration Testing**: Focus on phone input/validation and patient registration flows. Database migration testing included.  
✅ **V. Simplicity & Privacy**: Phone validation remains local (regex patterns). PII logging maintained with masked phone display.  

**Post-Design Re-evaluation**: ✅ All constitutional requirements satisfied  
**Design Impact**: Enhanced existing patterns without violating simplicity principles  
**Ready for Implementation**: Phase 2 (tasks) can proceed

## Project Structure

### Documentation (this feature)

```text
specs/002-international-phone/
├── plan.md              # This file (/speckit.plan command output)
├── research.md          # Phase 0 output (/speckit.plan command)
├── data-model.md        # Phase 1 output (/speckit.plan command)
├── quickstart.md        # Phase 1 output (/speckit.plan command)
├── contracts/           # Phase 1 output (/speckit.plan command)
└── tasks.md             # Phase 2 output (/speckit.tasks command - NOT created by /speckit.plan)
```

### Source Code (repository root)

```text
src/
├── models/
│   ├── patient.py           # Enhanced with country_code field
│   └── phone_number.py      # New: country code and formatting logic
├── services/
│   ├── patient_service.py   # Updated for international phone validation
│   └── phone_service.py     # New: validation and formatting service
├── ui/
│   ├── checkin_view.py      # Updated with country code dropdown
│   ├── patient_edit_view.py # Enhanced phone input with validation
│   └── arrivals_view.py     # Display updated phone formats
└── utils/
    └── phone.py             # Enhanced with international validation

tests/
├── unit/
│   ├── test_phone_validation.py  # New: international validation tests
│   ├── test_patient_model.py     # Updated: country code field tests
│   └── test_phone_service.py     # New: service layer tests
└── integration/
    ├── test_patient_registration.py  # Updated: international phone flows
    └── test_phone_display.py         # New: UI display format tests
```

**Structure Decision**: Single project structure maintained. Enhanced existing phone utilities and patient models with international support. Added new phone service for validation logic separation.

| Violation | Why Needed | Simpler Alternative Rejected Because |
|-----------|------------|-------------------------------------|
| [e.g., 4th project] | [current need] | [why 3 projects insufficient] |
| [e.g., Repository pattern] | [specific problem] | [why direct DB access insufficient] |
