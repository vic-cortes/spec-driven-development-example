"""International Phone Input Component for User Story 3 - Enhanced phone input with real-time validation."""

from typing import Callable, Optional

import flet as ft

from src.services.phone_service import phone_service


@ft.control
class InternationalPhoneInput(ft.Row):
    """
    Custom Flet control for international phone number input with real-time validation.

    Features:
    - Country code dropdown with US (+1) and Mexico (+52) support
    - Real-time phone number validation
    - User-friendly error messages
    - Proper formatting display
    - Accessibility support
    """

    def __init__(
        self,
        label: str = "Phone Number",
        hint_text: str = "Enter 10 digits",
        value: str = "",
        country_code: str = "+1",
        on_change: Optional[Callable] = None,
        on_validation: Optional[Callable] = None,
        width: Optional[int] = None,
        **kwargs,
    ):
        super().__init__(**kwargs)

        # Store properties
        self._label = label
        self._hint_text = hint_text
        self._value = value
        self._country_code = country_code
        self._on_change = on_change
        self._on_validation = on_validation
        self._width = width

        # Validation state
        self._is_valid = True
        self._error_message = None

        # Initialize controls
        self._init_controls()

    def _init_controls(self):
        """Initialize the country dropdown and phone input controls."""

        # Country code dropdown
        self._country_dropdown = ft.Dropdown(
            label="Country",
            options=[
                ft.dropdown.Option(key="+1", text="+1 (US)"),
                ft.dropdown.Option(key="+52", text="+52 (Mexico)"),
            ],
            value=self._country_code,
            width=120,
            on_change=self._on_country_change,
            tooltip="Select country code",
        )

        # Phone number input
        self._phone_input = ft.TextField(
            label=self._label,
            hint_text=self._hint_text,
            value=self._value,
            keyboard_type=ft.KeyboardType.PHONE,
            max_length=10,
            on_change=self._on_phone_change,
            expand=True,
            tooltip="Enter exactly 10 digits",
        )

        # Validation error display
        self._error_text = ft.Text(
            value="",
            color=ft.Colors.ERROR,
            size=12,
            visible=False,
        )

        # Formatted display (shows formatted phone after validation)
        self._formatted_display = ft.Text(
            value="",
            size=12,
            color=ft.Colors.PRIMARY,
            visible=False,
            weight=ft.FontWeight.W_500,
        )

        # Build the component layout
        self._build_layout()

    def _build_layout(self):
        """Build the component layout with proper spacing and alignment."""

        # Main input row
        input_row = ft.Row(
            controls=[
                self._country_dropdown,
                self._phone_input,
            ],
            alignment=ft.MainAxisAlignment.START,
            vertical_alignment=ft.CrossAxisAlignment.END,
            spacing=10,
            expand=True,
        )

        # Status column (for validation messages and formatted display)
        status_column = ft.Column(
            controls=[
                self._error_text,
                self._formatted_display,
            ],
            spacing=2,
            tight=True,
        )

        # Main column layout
        main_column = ft.Column(
            controls=[
                input_row,
                status_column,
            ],
            spacing=5,
            expand=True,
        )

        # Set the main control for this Row
        self.controls = [main_column]

        if self._width:
            self.width = self._width

    def _on_country_change(self, e):
        """Handle country code dropdown change."""
        self._country_code = e.control.value

        # Clear any previous validation when country changes
        self._clear_validation()

        # Re-validate with new country code if phone number exists
        if self._phone_input.value:
            self._validate_phone()

        # Trigger change callback if provided
        if self._on_change:
            self._on_change(e)

    def _on_phone_change(self, e):
        """Handle phone input change with real-time validation."""
        self._value = e.control.value

        # Perform real-time validation
        self._validate_phone()

        # Trigger change callback if provided
        if self._on_change:
            self._on_change(e)

    def _validate_phone(self):
        """Validate the current phone number and update UI accordingly."""

        # Get current values
        country_code = self._country_dropdown.value
        phone_value = self._phone_input.value

        # Validate using phone service
        result = phone_service.validate_phone(country_code, phone_value)

        # Update validation state
        self._is_valid = result.is_valid
        self._error_message = result.error_message

        # Update UI based on validation result
        if result.is_valid:
            self._show_success(result.formatted_phone)
        else:
            self._show_error(result.error_message)

        # Update the page
        self.update()

        # Trigger validation callback if provided
        if self._on_validation:
            self._on_validation(result)

    def _show_success(self, formatted_phone: str):
        """Show successful validation state."""
        # Hide error
        self._error_text.visible = False

        # Show formatted phone if phone is complete
        if len(self._phone_input.value) == 10:
            self._formatted_display.value = f"✓ {formatted_phone}"
            self._formatted_display.color = ft.Colors.GREEN
            self._formatted_display.visible = True
        else:
            self._formatted_display.visible = False

        # Clear any error styling on phone input
        self._phone_input.error_text = None

    def _show_error(self, error_message: str):
        """Show error validation state."""
        # Hide formatted display
        self._formatted_display.visible = False

        # Show error message
        if error_message:
            self._error_text.value = f"⚠ {error_message}"
            self._error_text.visible = True

        # Apply error styling to phone input
        self._phone_input.error_text = "Invalid input"

    def _clear_validation(self):
        """Clear all validation messages and styling."""
        self._error_text.visible = False
        self._formatted_display.visible = False
        self._phone_input.error_text = None
        self.update()

    # Public properties and methods

    @property
    def value(self) -> str:
        """Get the current phone number value."""
        return self._phone_input.value if self._phone_input else ""

    @value.setter
    def value(self, new_value: str):
        """Set the phone number value."""
        self._value = new_value
        if self._phone_input:
            self._phone_input.value = new_value
            self._validate_phone()

    @property
    def country_code(self) -> str:
        """Get the current country code."""
        return self._country_dropdown.value if self._country_dropdown else "+1"

    @country_code.setter
    def country_code(self, new_country_code: str):
        """Set the country code."""
        self._country_code = new_country_code
        if self._country_dropdown:
            self._country_dropdown.value = new_country_code
            if self._phone_input and self._phone_input.value:
                self._validate_phone()

    @property
    def is_valid(self) -> bool:
        """Check if the current input is valid."""
        return self._is_valid

    @property
    def error_message(self) -> Optional[str]:
        """Get the current error message if any."""
        return self._error_message

    @property
    def formatted_phone(self) -> Optional[str]:
        """Get the formatted phone number if valid."""
        if self._is_valid and self.value:
            result = phone_service.validate_phone(self.country_code, self.value)
            if result.is_valid:
                return result.formatted_phone
        return None

    def validate(self) -> bool:
        """Manually trigger validation and return result."""
        self._validate_phone()
        return self._is_valid

    def clear(self):
        """Clear the input and validation state."""
        if self._phone_input:
            self._phone_input.value = ""
        if self._country_dropdown:
            self._country_dropdown.value = "+1"
        self._clear_validation()
        self._is_valid = True
        self._error_message = None

    def set_error(self, error_message: str):
        """Manually set an error state (useful for form validation)."""
        self._is_valid = False
        self._error_message = error_message
        self._show_error(error_message)

    def focus(self):
        """Set focus to the phone input field."""
        if self._phone_input:
            self._phone_input.focus()

    def disable(self):
        """Disable the component."""
        if self._phone_input:
            self._phone_input.disabled = True
        if self._country_dropdown:
            self._country_dropdown.disabled = True

    def enable(self):
        """Enable the component."""
        if self._phone_input:
            self._phone_input.disabled = False
        if self._country_dropdown:
            self._country_dropdown.disabled = False


# Helper function to create an InternationalPhoneInput component easily
def create_international_phone_input(
    label: str = "Phone Number",
    hint_text: str = "Enter 10 digits",
    country_code: str = "+1",
    on_change: Optional[Callable] = None,
    on_validation: Optional[Callable] = None,
    **kwargs,
) -> InternationalPhoneInput:
    """
    Create an InternationalPhoneInput component with common defaults.

    Args:
        label: Label for the phone input field
        hint_text: Hint text for the phone input
        country_code: Default country code (+1 or +52)
        on_change: Callback for when input changes
        on_validation: Callback for when validation state changes
        **kwargs: Additional properties for the component

    Returns:
        Configured InternationalPhoneInput component
    """
    return InternationalPhoneInput(
        label=label,
        hint_text=hint_text,
        country_code=country_code,
        on_change=on_change,
        on_validation=on_validation,
        **kwargs,
    )
