"""Flet arrivals view for displaying today's patient check-ins."""

from datetime import date, datetime
from typing import List, Optional

import flet as ft

from src.models.checkin import CheckIn
from src.models.patient import Patient
from src.services.checkin_service import checkin_service
from src.services.logger import logger, mask_pii_data
from src.services.patient_service import patient_service
from src.utils.phone import format_phone_display


class ArrivalsView(ft.Container):
    """View for displaying today's patient arrivals."""

    def __init__(self, on_refresh: Optional[callable] = None):
        self.on_refresh = on_refresh

        # UI components
        self.refresh_button = ft.ElevatedButton(
            "Refresh",
            icon=ft.Icons.REFRESH,
            on_click=self._on_refresh_click,
        )

        self.arrivals_list = ft.Column(spacing=10, expand=True)
        self.status_text = ft.Text("", size=14, color=ft.Colors.BLUE_GREY_600)
        self.empty_state = ft.Container(
            content=ft.Column(
                [
                    ft.Icon(
                        ft.Icons.PEOPLE_OUTLINE, size=64, color=ft.Colors.BLUE_GREY_300
                    ),
                    ft.Text(
                        "No arrivals yet today",
                        size=18,
                        color=ft.Colors.BLUE_GREY_600,
                        text_align=ft.TextAlign.CENTER,
                    ),
                    ft.Text(
                        "Check-ins will appear here as patients arrive",
                        size=14,
                        color=ft.Colors.BLUE_GREY_400,
                        text_align=ft.TextAlign.CENTER,
                    ),
                ],
                horizontal_alignment=ft.CrossAxisAlignment.CENTER,
                spacing=10,
            ),
            alignment=ft.alignment.center,
            expand=True,
            visible=False,
        )

        # Build the UI
        content = self._build_content()
        super().__init__(
            content=content,
            padding=ft.Padding(20, 20, 20, 20),
            expand=True,
        )

        # Load initial data
        self._load_arrivals()

    def _build_content(self) -> ft.Column:
        """Build the main content layout."""
        return ft.Column(
            [
                # Header with title and refresh
                ft.Row(
                    [
                        ft.Text(
                            "Today's Arrivals",
                            size=24,
                            weight=ft.FontWeight.BOLD,
                            color=ft.Colors.PRIMARY,
                        ),
                        self.refresh_button,
                    ],
                    alignment=ft.MainAxisAlignment.SPACE_BETWEEN,
                    vertical_alignment=ft.CrossAxisAlignment.CENTER,
                ),
                # Status/summary text
                self.status_text,
                ft.Divider(height=1, color=ft.Colors.BLUE_GREY_200),
                # Content area (list or empty state)
                ft.Container(
                    content=ft.Stack(
                        [
                            # Scrollable arrivals list
                            ft.Container(
                                content=self.arrivals_list,
                                expand=True,
                            ),
                            # Empty state overlay
                            self.empty_state,
                        ],
                    ),
                    expand=True,
                ),
            ],
            spacing=15,
            expand=True,
        )

    def _load_arrivals(self):
        """Load and display today's arrivals."""
        try:
            today = date.today()
            arrivals = checkin_service.list_today(today)

            # Update status text
            count = len(arrivals)
            if count == 0:
                self.status_text.value = "No patients have checked in yet today"
                self._show_empty_state()
            else:
                plural = "patient" if count == 1 else "patients"
                self.status_text.value = f"{count} {plural} checked in today"
                self._show_arrivals_list(arrivals)

            logger.info(f"Loaded arrivals view: {count} arrivals for {today}")

        except Exception as e:
            logger.error(f"Error loading arrivals: {str(e)}")
            self.status_text.value = "Error loading arrivals"
            self.status_text.color = ft.Colors.ERROR
            self._show_empty_state()

        self.update()

    def _show_empty_state(self):
        """Show the empty state view."""
        self.empty_state.visible = True
        self.arrivals_list.controls.clear()

    def _show_arrivals_list(self, arrivals: List[CheckIn]):
        """Show the list of arrivals."""
        self.empty_state.visible = False
        self.arrivals_list.controls.clear()

        for arrival in arrivals:
            arrival_card = self._create_arrival_card(arrival)
            self.arrivals_list.controls.append(arrival_card)

    def _create_arrival_card(self, arrival: CheckIn) -> ft.Container:
        """Create a card widget for a single arrival."""
        try:
            # Get patient details
            patient = patient_service.get_patient(arrival.patient_id)
            if not patient:
                logger.error(f"Patient not found for arrival: {arrival.patient_id}")
                return self._create_error_card(arrival)

            # Format time
            time_str = arrival.timestamp.strftime("%I:%M %p")

            # Mask phone for display
            masked_data = mask_pii_data({"phone": patient.phone})
            phone_display = format_phone_display(masked_data["phone"])

            # Create patient name
            patient_name = f"{patient.first_name} {patient.last_name}"

            return ft.Container(
                content=ft.ResponsiveRow(
                    [
                        # Time column
                        ft.Container(
                            content=ft.Column(
                                [
                                    ft.Text(
                                        time_str,
                                        size=16,
                                        weight=ft.FontWeight.BOLD,
                                        color=ft.Colors.PRIMARY,
                                    ),
                                    ft.Text(
                                        "Arrived",
                                        size=12,
                                        color=ft.Colors.GREEN,
                                        weight=ft.FontWeight.W500,
                                    ),
                                ],
                                spacing=2,
                                horizontal_alignment=ft.CrossAxisAlignment.CENTER,
                            ),
                            col={"sm": 2, "md": 2, "lg": 2},
                            alignment=ft.alignment.center,
                        ),
                        # Patient info column
                        ft.Container(
                            content=ft.Column(
                                [
                                    ft.Text(
                                        patient_name,
                                        size=16,
                                        weight=ft.FontWeight.W500,
                                        color=ft.Colors.ON_SURFACE,
                                    ),
                                    ft.Text(
                                        phone_display,
                                        size=14,
                                        color=ft.Colors.ON_SURFACE_VARIANT,
                                    ),
                                ],
                                spacing=2,
                            ),
                            col={"sm": 6, "md": 6, "lg": 6},
                        ),
                        # Route/Notes column
                        ft.Container(
                            content=ft.Text(
                                arrival.route_note or "No notes",
                                size=14,
                                color=ft.Colors.ON_SURFACE_VARIANT,
                                italic=not arrival.route_note,
                            ),
                            col={"sm": 4, "md": 4, "lg": 4},
                        ),
                    ],
                    vertical_alignment=ft.CrossAxisAlignment.CENTER,
                ),
                bgcolor=ft.Colors.SURFACE_VARIANT,
                border_radius=ft.border_radius.all(8),
                padding=ft.Padding(15, 12, 15, 12),
                margin=ft.margin.only(bottom=5),
                border=ft.border.all(1, ft.Colors.OUTLINE_VARIANT),
            )

        except Exception as e:
            logger.error(f"Error creating arrival card: {str(e)}")
            return self._create_error_card(arrival)

    def _create_error_card(self, arrival: CheckIn) -> ft.Container:
        """Create an error card for arrivals that can't be displayed properly."""
        return ft.Container(
            content=ft.Row(
                [
                    ft.Icon(ft.Icons.ERROR_OUTLINE, color=ft.Colors.ERROR),
                    ft.Text(
                        f"Error loading arrival {arrival.id}",
                        color=ft.Colors.ERROR,
                    ),
                ],
                spacing=10,
            ),
            bgcolor=ft.Colors.ERROR_CONTAINER,
            border_radius=ft.border_radius.all(8),
            padding=ft.Padding(15, 12, 15, 12),
            margin=ft.margin.only(bottom=5),
        )

    def _on_refresh_click(self, e):
        """Handle refresh button click."""
        self._load_arrivals()

        if self.on_refresh:
            try:
                self.on_refresh()
            except Exception as refresh_error:
                logger.error(f"Error in refresh callback: {str(refresh_error)}")

    def refresh_data(self):
        """Public method to refresh the arrivals data."""
        self._load_arrivals()

    def get_arrival_count(self) -> int:
        """Get the current number of arrivals displayed."""
        return len(self.arrivals_list.controls) if hasattr(self, "arrivals_list") else 0
