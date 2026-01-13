# Data Model: Patient Check-In (Phone)

## Entities

### Patient
- `id`: string (UUID)
- `first_name`: string
- `last_name`: string
- `phone`: string (digits-only normalized)
- `email`: optional string
- `birth_date`: optional date (ISO)
- `address`: optional string
- `notes`: optional string (avoid sensitive info)

Constraints:
- Phone not globally unique; disambiguation by record selection.

### CheckIn
- `id`: string (UUID)
- `patient_id`: string (UUID)
- `timestamp`: datetime (ISO UTC)
- `date`: date (ISO)
- `status`: enum {"checked_in"}
- `route_note`: optional string (for future assignment workflow)

Rules:
- Single CheckIn per Patient per day; repeated arrivals update `timestamp`.

## Derived Views

### TodayArrivals
- List of `CheckIn` for `date == today` joined with `Patient` name and masked phone.

## Validation
- Phone must be digits-only, length >= 8 (configurable).
- Names required for minimal patient creation.
- Logs must not include full phone or name (masked phone only).
