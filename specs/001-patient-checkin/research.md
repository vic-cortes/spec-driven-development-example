# Phase 0 Research: Patient Check-In (Phone)

## Decisions

- **UI Framework**: Flet
  - Rationale: Single-codebase desktop app with responsive layout; simple deployment; Python-native.
  - Alternatives: Tkinter (limited modern UI), PySide/PyQt (heavier), Kivy (mobile-oriented but different patterns).

- **Storage (MVP)**: In-memory mock store
  - Rationale: User explicitly requested no DB; enables rapid iteration and demo.
  - Alternatives: SQLite (constitution baseline; planned for later); JSON files (risk of corruption; no need).

- **Phone Normalization**: Digits-only; strip spaces, dashes, parentheses; optionally country code handling TBD.
  - Rationale: Reliable lookup regardless of formatting.
  - Alternatives: Strict format validation (higher friction).

- **Single-per-Day Check-In**: Update timestamp if repeated
  - Rationale: Prevent duplicates; keep arrivals list clean.
  - Alternatives: Allow multiple entries (adds complexity to UI).

- **Shared Phone Policy**: Prompt selection among matches
  - Rationale: Realistic for families; avoids hard uniqueness constraints.
  - Alternatives: Enforce unique phone (blocks valid scenarios); require second identifier upfront (adds friction).

- **Routing to Doctor/Specialty**: Separate assignment workflow
  - Rationale: Keep check-in fast/minimal; assistants/doctors assign later.
  - Alternatives: Manual selection at check-in (slows primary flow); auto-routing (needs rules not yet defined).

- **Mobile Readiness (iPad/iPhone)**: Responsive layout and touch-friendly controls; avoid desktop-only patterns.
  - Rationale: Prepare UI to scale to tablet/phone sizes for future packaging/web view.
  - Alternatives: Desktop-only (limits portability).

## Patterns & Best Practices

- Flet responsive UI:
  - Use `ResponsiveRow`, `Column`, `Row` with `expand` to adapt.
  - Prefer form components with validation (`TextField` validators; real-time feedback).
  - Use `Page.theme_mode`, spacing, and adaptive sizes for touch targets.

- Privacy-safe logging:
  - Mask phone numbers (e.g., `***1234` last 4 digits only).
  - Avoid storing PII in logs; log events with minimal context.

- Test strategy:
  - Unit: phone normalization, matching, in-memory store behaviors.
  - Integration: simple end-to-end check-in + arrivals list (store + UI boundary).

## Open Items

- Country code handling for phone numbers (assume local for MVP).
- Future packaging for iOS/iPadOS (out-of-scope for MVP; ensure responsive design now).
