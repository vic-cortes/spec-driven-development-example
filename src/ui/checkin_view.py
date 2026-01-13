"""Flet check-in view for patient arrival registration."""

from typing import Callable, List, Optional

import flet as ft

from src.models.checkin import CheckIn
from src.models.patient import Patient
from src.services.checkin_service import checkin_service
from src.services.logger import logger
from src.services.patient_service import patient_service
from src.utils.phone import format_phone_display, is_valid_phone, normalize_phone


class CheckInView(ft.UserControl):
    """Check-in screen for patient arrival registration."""

    def __init__(self, on_checkin_complete: Optional[Callable] = None):
        super().__init__()
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
            icon=ft.icons.SEARCH,
            on_click=self._on_search_click,
            disabled=True,
        )

        self.result_area = ft.Column(spacing=10, visible=False)

        self.status_text = ft.Text("", color=ft.colors.GREEN, visible=False)

        # Patient selection (for shared phone numbers)
        self.patient_selection = ft.Column(spacing=5, visible=False)

        # New patient creation form
        self.new_patient_form = ft.Column(spacing=10, visible=False)
        self._setup_new_patient_form()

    def _setup_new_patient_form(self):
        """Setup the new patient creation form."""
        self.first_name_input = ft.TextField(label="First Name", width=200)

        self.last_name_input = ft.TextField(label="Last Name", width=200)

        self.create_button = ft.ElevatedButton(
            "Create & Check In",
            icon=ft.icons.PERSON_ADD,
            on_click=self._on_create_patient_click,
            color=ft.colors.WHITE,
            bgcolor=ft.colors.GREEN,
        )

        self.cancel_button = ft.TextButton("Cancel", on_click=self._on_cancel_click)

        form_title = ft.Text("Create New Patient", weight=ft.FontWeight.BOLD)
        name_row = ft.ResponsiveRow(
            [ft.Col(self.first_name_input, col=6), ft.Col(self.last_name_input, col=6)]
        )
        button_row = ft.Row([self.create_button, self.cancel_button], spacing=10)

        self.new_patient_form.controls = [form_title, name_row, button_row]

    def build(self):
        """Build the check-in view."""
        title = ft.Text(
            "Patient Check-In", size=24, weight=ft.FontWeight.BOLD, color=ft.colors.BLUE
        )

        search_row = ft.ResponsiveRow(
            [ft.Col(self.phone_input, col=8), ft.Col(self.search_button, col=4)]
        )

        return ft.Container(
            content=ft.Column(
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
            ),
            padding=20,
        )

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

        if not phone_text:
            self._show_error("Please enter a phone number")
            return

        if not is_valid_phone(phone_text):
            self._show_error("Please enter a valid phone number")
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
            color=ft.colors.ORANGE,
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
            color=ft.colors.BLUE,
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

        if not first_name or not last_name:
            self._show_error("Please enter both first and last name")
            return

        try:
            # Create patient and check in
            patient = patient_service.create_minimal_patient(
                first_name, last_name, phone_text
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
                color = ft.colors.GREEN
            elif was_repeat:
                message = f"🔄 Updated check-in time for: {patient.full_name}"
                color = ft.colors.BLUE
            else:
                message = f"✅ Checked in: {patient.full_name}"
                color = ft.colors.GREEN

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
        self._show_status(f"❌ {message}", ft.colors.RED)

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
