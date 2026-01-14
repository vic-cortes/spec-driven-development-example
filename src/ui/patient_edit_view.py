"""Patient edit view for updating patient information."""

from typing import Callable, Optional

import flet as ft

from src.models.patient import Patient
from src.services.logger import logger
from src.services.patient_service import patient_service
from src.utils.phone import is_valid_phone, normalize_phone


class PatientEditView:
    """UI for editing patient information."""

    def __init__(
        self,
        patient: Patient,
        on_save: Optional[Callable] = None,
        on_cancel: Optional[Callable] = None,
    ):
        """
        Initialize the patient edit view.

        Args:
            patient: Patient to edit
            on_save: Callback when patient is saved successfully
            on_cancel: Callback when edit is cancelled
        """
        self.patient = patient
        self.on_save = on_save
        self.on_cancel = on_cancel

        # Form controls
        self.first_name_field = ft.TextField(
            label="First Name",
            value=patient.first_name,
            max_length=50,
            autofocus=True,
            expand=True,
        )

        self.last_name_field = ft.TextField(
            label="Last Name", value=patient.last_name, max_length=50, expand=True
        )

        self.phone_field = ft.TextField(
            label="Phone Number",
            value=self._format_phone_display(patient.phone),
            max_length=20,
            expand=True,
            hint_text="(555) 123-4567",
        )

        self.email_field = ft.TextField(
            label="Email (Optional)",
            value=patient.email or "",
            max_length=100,
            expand=True,
            hint_text="patient@example.com",
        )

        self.address_field = ft.TextField(
            label="Address (Optional)",
            value=patient.address or "",
            max_length=200,
            expand=True,
            multiline=True,
            min_lines=2,
            max_lines=3,
        )

        self.notes_field = ft.TextField(
            label="Notes (Optional)",
            value=patient.notes or "",
            max_length=500,
            expand=True,
            multiline=True,
            min_lines=3,
            max_lines=5,
        )

        # Status and error display
        self.status_text = ft.Text("", color=ft.Colors.RED)

        # Action buttons
        self.save_button = ft.ElevatedButton(
            "Save Changes",
            icon=ft.Icons.SAVE,
            on_click=self._handle_save,
            style=ft.ButtonStyle(bgcolor=ft.Colors.BLUE, color=ft.Colors.WHITE),
        )

        self.cancel_button = ft.TextButton(
            "Cancel", icon=ft.Icons.CANCEL, on_click=self._handle_cancel
        )

        # Build the view
        self.view = self._build_view()

    def _format_phone_display(self, phone: str) -> str:
        """Format phone number for display in edit field."""
        if len(phone) == 10:
            return f"({phone[:3]}) {phone[3:6]}-{phone[6:]}"
        return phone

    def _build_view(self) -> ft.Column:
        """Build the main edit view."""
        return ft.Column(
            controls=[
                # Header
                ft.Container(
                    content=ft.Row(
                        [
                            ft.Icon(ft.Icons.EDIT, size=24),
                            ft.Text(
                                f"Edit Patient: {self.patient.full_name}",
                                style=ft.TextThemeStyle.HEADLINE_SMALL,
                                weight=ft.FontWeight.BOLD,
                            ),
                        ]
                    ),
                    padding=ft.padding.only(bottom=20),
                ),
                # Form fields in responsive layout
                ft.ResponsiveRow(
                    [
                        ft.Column(
                            col={"xs": 12, "sm": 6}, controls=[self.first_name_field]
                        ),
                        ft.Column(
                            col={"xs": 12, "sm": 6}, controls=[self.last_name_field]
                        ),
                    ]
                ),
                ft.ResponsiveRow(
                    [
                        ft.Column(col={"xs": 12, "sm": 6}, controls=[self.phone_field]),
                        ft.Column(col={"xs": 12, "sm": 6}, controls=[self.email_field]),
                    ]
                ),
                ft.ResponsiveRow([ft.Column(col=12, controls=[self.address_field])]),
                ft.ResponsiveRow([ft.Column(col=12, controls=[self.notes_field])]),
                # Status message
                self.status_text,
                # Action buttons
                ft.Container(
                    content=ft.Row(
                        controls=[
                            self.cancel_button,
                            self.save_button,
                        ],
                        alignment=ft.MainAxisAlignment.END,
                        spacing=10,
                    ),
                    padding=ft.padding.only(top=20),
                ),
            ],
            spacing=15,
            expand=True,
        )

    def _handle_save(self, e):
        """Handle save button click."""
        try:
            self._clear_status()

            # Validate required fields
            first_name = self.first_name_field.value.strip()
            last_name = self.last_name_field.value.strip()
            phone = self.phone_field.value.strip()

            if not first_name:
                self._show_error("First name is required")
                self.first_name_field.focus()
                return

            if not last_name:
                self._show_error("Last name is required")
                self.last_name_field.focus()
                return

            if not phone:
                self._show_error("Phone number is required")
                self.phone_field.focus()
                return

            # Validate phone format
            if not is_valid_phone(phone):
                self._show_error("Invalid phone number format")
                self.phone_field.focus()
                return

            # Normalize phone
            normalized_phone = normalize_phone(phone)

            # Create updated patient object
            updated_patient = Patient(
                id=self.patient.id,
                first_name=first_name,
                last_name=last_name,
                phone=normalized_phone,
                email=self.email_field.value.strip() or None,
                address=self.address_field.value.strip() or None,
                notes=self.notes_field.value.strip() or None,
            )

            # Save the patient
            patient_service.update_patient(updated_patient)

            logger.info(f"Patient updated successfully: {updated_patient.masked_phone}")

            # Call success callback
            if self.on_save:
                self.on_save(updated_patient)

        except ValueError as e:
            self._show_error(str(e))
        except Exception as e:
            logger.error(f"Error updating patient: {str(e)}")
            self._show_error("An unexpected error occurred. Please try again.")

    def _handle_cancel(self, e):
        """Handle cancel button click."""
        if self.on_cancel:
            self.on_cancel()

    def _show_error(self, message: str):
        """Display error message."""
        self.status_text.value = message
        self.status_text.color = ft.Colors.RED
        self.status_text.update()

    def _show_success(self, message: str):
        """Display success message."""
        self.status_text.value = message
        self.status_text.color = ft.Colors.GREEN
        self.status_text.update()

    def _clear_status(self):
        """Clear status message."""
        self.status_text.value = ""
        self.status_text.update()

    def get_view(self) -> ft.Column:
        """Get the main view control."""
        return self.view


class PatientEditDialog:
    """Modal dialog for editing patient information."""

    def __init__(
        self, patient: Patient, page: ft.Page, on_save: Optional[Callable] = None
    ):
        """
        Initialize the patient edit dialog.

        Args:
            patient: Patient to edit
            page: Flet page reference
            on_save: Callback when patient is saved successfully
        """
        self.patient = patient
        self.page = page
        self.on_save = on_save

        # Create edit view
        self.edit_view = PatientEditView(
            patient=patient, on_save=self._handle_save, on_cancel=self._handle_cancel
        )

        # Create dialog
        self.dialog = ft.AlertDialog(
            modal=True,
            title=ft.Text("Edit Patient Information"),
            content=ft.Container(
                content=self.edit_view.get_view(), width=500, height=600
            ),
            actions_alignment=ft.MainAxisAlignment.END,
        )

    def _handle_save(self, updated_patient: Patient):
        """Handle successful save."""
        self.page.dialog = None
        self.page.update()

        if self.on_save:
            self.on_save(updated_patient)

    def _handle_cancel(self):
        """Handle cancel."""
        self.page.dialog = None
        self.page.update()

    def show(self):
        """Show the edit dialog."""
        self.page.dialog = self.dialog
        self.dialog.open = True
        self.page.update()


def create_patient_edit_view(
    patient: Patient,
    on_save: Optional[Callable] = None,
    on_cancel: Optional[Callable] = None,
) -> ft.Column:
    """
    Factory function to create a patient edit view.

    Args:
        patient: Patient to edit
        on_save: Callback when patient is saved successfully
        on_cancel: Callback when edit is cancelled

    Returns:
        Column control containing the edit view
    """
    edit_view = PatientEditView(patient=patient, on_save=on_save, on_cancel=on_cancel)
    return edit_view.get_view()


def show_patient_edit_dialog(
    patient: Patient, page: ft.Page, on_save: Optional[Callable] = None
):
    """
    Show patient edit dialog.

    Args:
        patient: Patient to edit
        page: Flet page reference
        on_save: Callback when patient is saved successfully
    """
    dialog = PatientEditDialog(patient=patient, page=page, on_save=on_save)
    dialog.show()
