"""Flet check-in view for patient arrival registration."""

from typing import Callable, List, Optional

import flet as ft

from src.models.patient import Patient
from src.services.checkin_service import checkin_service
from src.services.logger import logger
from src.services.patient_service import patient_service
from src.utils.phone import (
    format_phone_display,
    is_valid_international_phone,
    is_valid_phone,
    normalize_phone,
)


class CheckInView(ft.Container):
    """Check-in screen for patient arrival registration."""

    def __init__(self, on_checkin_complete: Optional[Callable] = None):
        self.on_checkin_complete = on_checkin_complete

        # UI components
        self.phone_input = ft.TextField(
            label="Phone Number",
            hint_text="Enter patient's phone number",
            width=300,
            autofocus=True,
            on_change=self._on_phone_change,
            on_submit=self._on_phone_submit,
        )

        self.search_button = ft.ElevatedButton(
            "Search Patient",
            icon=ft.Icons.SEARCH,
            on_click=self._on_search_click,
            disabled=True,
        )

        self.result_area = ft.Column(spacing=10, visible=False)

        self.status_text = ft.Text("", color=ft.Colors.GREEN, visible=False)

        # Patient selection (for shared phone numbers)
        self.patient_selection = ft.Column(spacing=5, visible=False)

        # New patient creation form
        self.new_patient_form = ft.Column(spacing=10, visible=False)
        self._setup_new_patient_form()

        # Build the UI and call super with content
        content = self._build_content()
        super().__init__(
            content=content,
            padding=20,
            expand=True,
        )

    def _build_content(self):
        """Build the content for the container."""
        title = ft.Text(
            "Patient Check-In", size=24, weight=ft.FontWeight.BOLD, color=ft.Colors.BLUE
        )

        search_row = ft.ResponsiveRow(
            controls=[
                ft.Container(
                    content=self.phone_input, col={"sm": 12, "md": 8, "lg": 8}
                ),
                ft.Container(
                    content=self.search_button, col={"sm": 12, "md": 4, "lg": 4}
                ),
            ]
        )

        return ft.Column(
            [
                title,
                ft.Divider(),
                search_row,
                self.result_area,
                self.patient_selection,
                self.new_patient_form,
                self.status_text,
            ],
            spacing=15,
            horizontal_alignment=ft.CrossAxisAlignment.START,
            scroll=ft.ScrollMode.AUTO,
        )

    def _setup_new_patient_form(self):
        """Setup the new patient creation form."""
        self.first_name_input = ft.TextField(label="First Name", width=200)

        self.last_name_input = ft.TextField(label="Last Name", width=200)

        # Country code dropdown with default to US (+1)
        self.country_code_dropdown = ft.Dropdown(
            label="Country",
            width=150,
            value="+1",  # Default to US
            options=[
                ft.dropdown.Option("+1", "+1 (US)"),
                ft.dropdown.Option("+52", "+52 (Mexico)"),
            ],
            hint_text="Select country code",
        )

        self.create_button = ft.ElevatedButton(
            "Create & Check In",
            icon=ft.Icons.PERSON_ADD,
            on_click=self._on_create_patient_click,
            color=ft.Colors.WHITE,
            bgcolor=ft.Colors.GREEN,
        )

        self.cancel_button = ft.TextButton("Cancel", on_click=self._on_cancel_click)

        form_title = ft.Text("Create New Patient", weight=ft.FontWeight.BOLD)
        name_row = ft.ResponsiveRow(
            controls=[
                ft.Container(
                    content=self.first_name_input, col={"sm": 12, "md": 6, "lg": 6}
                ),
                ft.Container(
                    content=self.last_name_input, col={"sm": 12, "md": 6, "lg": 6}
                ),
            ]
        )
        # Add country code row
        country_row = ft.ResponsiveRow(
            controls=[
                ft.Container(
                    content=self.country_code_dropdown,
                    col={"sm": 12, "md": 12, "lg": 12},
                ),
            ]
        )
        button_row = ft.Row([self.create_button, self.cancel_button], spacing=10)

        self.new_patient_form.controls = [form_title, name_row, country_row, button_row]

    def _validate_phone_with_detailed_error(
        self, phone_text: str, country_code: str = "+1"
    ) -> str:
        """
        Validate phone number and return detailed error message if invalid.

        Args:
            phone_text: Phone number to validate
            country_code: Country code for validation context

        Returns:
            Empty string if valid, error message if invalid
        """
        if not phone_text.strip():
            return "Phone number is required"

        # Try to validate with international phone support
        if not is_valid_international_phone(phone_text, country_code):
            # Provide more specific error messages
            # Remove all non-digit characters to check length
            import re

            digits_only = re.sub(r"[^\d]", "", phone_text)

            if len(digits_only) < 10:
                return f"Phone number too short: {len(digits_only)} digits (need exactly 10)"
            elif len(digits_only) > 10:
                return f"Phone number too long: {len(digits_only)} digits (need exactly 10)"
            else:
                return "Invalid phone number format"

        return ""  # Valid phone number

    def _on_phone_change(self, e):
        """Handle phone input changes."""
        phone_text = self.phone_input.value.strip()
        self.search_button.disabled = not bool(phone_text)
        self._hide_results()
        self.update()

    def _on_phone_submit(self, e):
        """Handle Enter key in phone input."""
        if not self.search_button.disabled:
            self._on_search_click(e)

    def _on_search_click(self, e):
        """Handle search button click."""
        phone_text = self.phone_input.value.strip()

        # Enhanced phone validation with detailed error messages
        validation_error = self._validate_phone_with_detailed_error(phone_text)
        if validation_error:
            self._show_error(validation_error)
            return

        try:
            # Search for patients
            patients, needs_disambiguation = patient_service.search_and_create_workflow(
                phone_text
            )

            if not patients:
                # No patients found - show new patient form
                self._show_new_patient_form(phone_text)
            elif needs_disambiguation:
                # Multiple patients - show selection
                self._show_patient_selection(patients)
            else:
                # Single patient - check in directly
                self._check_in_patient(patients[0])

        except ValueError as e:
            self._show_error(f"Search failed: {str(e)}")

    def _show_new_patient_form(self, phone: str):
        """Show form to create new patient."""
        self._hide_results()

        normalized_phone = normalize_phone(phone)
        formatted_phone = format_phone_display(normalized_phone)

        info_text = ft.Text(
            f"No patient found for {formatted_phone}. Create new record:",
            color=ft.Colors.ORANGE,
        )

        self.result_area.controls = [info_text]
        self.result_area.visible = True
        self.new_patient_form.visible = True

        # Pre-fill first name field
        self.first_name_input.value = ""
        self.last_name_input.value = ""
        self.first_name_input.focus()

        self.update()

    def _show_patient_selection(self, patients: List[Patient]):
        """Show patient selection for shared phone numbers."""
        self._hide_results()

        info_text = ft.Text(
            f"Multiple patients found. Select the correct patient:",
            color=ft.Colors.BLUE,
        )

        selection_buttons = []
        for patient in patients:
            button = ft.ElevatedButton(
                f"{patient.full_name}",
                data=patient,
                on_click=self._on_patient_select,
                width=250,
            )
            selection_buttons.append(button)

        self.patient_selection.controls = [info_text] + selection_buttons
        self.patient_selection.visible = True

        self.result_area.visible = True
        self.update()

    def _on_patient_select(self, e):
        """Handle patient selection from disambiguation."""
        patient = e.control.data
        self._check_in_patient(patient)

    def _on_create_patient_click(self, e):
        """Handle create patient button click."""
        first_name = self.first_name_input.value.strip()
        last_name = self.last_name_input.value.strip()
        phone_text = self.phone_input.value.strip()
        country_code = self.country_code_dropdown.value or "+1"  # Default to US

        if not first_name or not last_name:
            self._show_error("Please enter both first and last name")
            return

        # Enhanced validation for phone number with selected country code
        validation_error = self._validate_phone_with_detailed_error(
            phone_text, country_code
        )
        if validation_error:
            self._show_error(validation_error)
            return

        try:
            # Create patient with international phone support and check in
            patient = patient_service.create_patient(
                first_name, last_name, phone_text, country_code
            )
            self._check_in_patient(patient, is_new=True)

        except ValueError as e:
            self._show_error(f"Failed to create patient: {str(e)}")

    def _check_in_patient(self, patient: Patient, is_new: bool = False):
        """Check in a patient."""
        try:
            checkin, was_repeat = checkin_service.complete_checkin_workflow(patient)

            # Show success message
            if is_new:
                message = f"✅ Created and checked in: {patient.full_name}"
                color = ft.Colors.GREEN
            elif was_repeat:
                message = f"🔄 Updated check-in time for: {patient.full_name}"
                color = ft.Colors.BLUE
            else:
                message = f"✅ Checked in: {patient.full_name}"
                color = ft.Colors.GREEN

            self._show_status(message, color)
            self._clear_form()

            # Notify parent if callback provided
            if self.on_checkin_complete:
                self.on_checkin_complete(checkin, patient)

        except ValueError as e:
            self._show_error(f"Check-in failed: {str(e)}")

    def _on_cancel_click(self, e):
        """Handle cancel button click."""
        self._clear_form()

    def _show_error(self, message: str):
        """Show error message."""
        self._show_status(f"❌ {message}", ft.Colors.RED)

    def _show_status(self, message: str, color: str):
        """Show status message."""
        self.status_text.value = message
        self.status_text.color = color
        self.status_text.visible = True
        self.update()

        # Auto-hide status after 3 seconds
        # Note: In a real app, you'd use a timer here
        logger.info(f"Check-in status: {message}")

    def _hide_results(self):
        """Hide all result areas."""
        self.result_area.visible = False
        self.patient_selection.visible = False
        self.new_patient_form.visible = False
        self.status_text.visible = False

    def _clear_form(self):
        """Clear the entire form."""
        self.phone_input.value = ""
        self.first_name_input.value = ""
        self.last_name_input.value = ""
        self._hide_results()
        self.search_button.disabled = True
        self.phone_input.focus()
        self.update()

    def reset(self):
        """Reset the check-in view to initial state."""
        self._clear_form()
