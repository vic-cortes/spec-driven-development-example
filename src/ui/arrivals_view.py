"""Flet arrivals view for displaying today's patient check-ins."""

from datetime import date, datetime
from typing import List, Optional

import flet as ft

from src.models.checkin import CheckIn
from src.models.patient import Patient
from src.services.checkin_service import checkin_service
from src.services.logger import logger, mask_pii_data
from src.services.patient_service import patient_service
from src.ui.patient_edit_view import show_patient_edit_dialog
from src.utils.phone import format_phone_display


class ArrivalsView:
    """View for displaying today's patient arrivals."""

    def __init__(self, on_refresh: Optional[callable] = None):
        self.on_refresh = on_refresh

        # UI components
        self.refresh_button = ft.ElevatedButton(
            "Refresh",
            icon=ft.Icons.REFRESH,
            on_click=self._on_refresh_click,
        )

        self.arrivals_list = ft.Column(
            spacing=10,
            expand=True,
            scroll=ft.ScrollMode.AUTO,
            auto_scroll=True,
        )
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
            alignment=ft.Alignment(0, 0),  # center alignment
            expand=True,
            visible=False,
        )

        # Build the main content container
        self.container = ft.Container(
            content=self._build_content(),
            padding=ft.Padding(20, 20, 20, 20),
            expand=True,
        )

    def build(self) -> ft.Container:
        """Return the main container for this view."""
        return self.container

    def set_page(self, page):
        """Set the page reference for updates."""
        self.page = page

    def did_mount(self):
        """Called when the view is mounted to the page."""
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
                            color=ft.Colors.BLUE,
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
                                height=400,  # Set explicit height for better scroll behavior
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
        """Load and display today's arrivals with performance optimizations."""
        try:
            today = date.today()
            arrivals = checkin_service.list_today(today)

            # Cache the count to avoid recalculation
            count = len(arrivals)

            # Update status text with optimized string formatting
            if count == 0:
                self.status_text.value = "No patients have checked in yet today"
                self._show_empty_state()
            else:
                # Use more efficient pluralization
                patient_text = "patient" if count == 1 else "patients"
                self.status_text.value = f"{count} {patient_text} checked in today"
                self._show_arrivals_list(arrivals)

            logger.info(f"Loaded arrivals view: {count} arrivals for {today}")

        except Exception as e:
            logger.error(f"Error loading arrivals: {str(e)}")
            self.status_text.value = "Error loading arrivals"
            self.status_text.color = ft.Colors.ERROR
            self._show_empty_state()

    def _show_empty_state(self):
        """Show the empty state view."""
        self.empty_state.visible = True
        self.arrivals_list.controls.clear()

    def _show_arrivals_list(self, arrivals: List[CheckIn]):
        """Show the list of arrivals with optimized rendering."""
        self.empty_state.visible = False

        # Clear existing controls efficiently
        self.arrivals_list.controls.clear()

        # Batch create arrival cards for better performance
        new_cards = []
        for arrival in arrivals:
            try:
                arrival_card = self._create_arrival_card(arrival)
                new_cards.append(arrival_card)
            except Exception as e:
                logger.error(f"Error creating card for arrival {arrival.id}: {str(e)}")
                # Add error card as fallback
                new_cards.append(self._create_error_card(arrival))

        # Add all cards at once for better performance
        self.arrivals_list.controls.extend(new_cards)

    def _create_arrival_card(self, arrival: CheckIn) -> ft.Container:
        """Create a card widget for a single arrival."""
        try:
            logger.info(f"Creating arrival card for arrival ID: {arrival.id}")

            # Get patient details
            patient = patient_service.get_patient(arrival.patient_id)
            if not patient:
                logger.error(f"Patient not found for arrival: {arrival.patient_id}")
                return self._create_error_card(arrival)

            logger.info("Patient found, creating detailed card...")

            # Format time
            arrival_time = arrival.timestamp.strftime("%I:%M %p")

            # Create edit button
            edit_button = ft.IconButton(
                icon=ft.Icons.EDIT,
                tooltip="Edit Patient",
                icon_size=18,
                on_click=lambda e, p=patient: self._handle_edit_patient(p),
            )

            # Patient info section
            patient_info = ft.Column(
                [
                    ft.Row(
                        [
                            ft.Text(
                                patient.full_name,
                                size=16,
                                weight=ft.FontWeight.BOLD,
                                color=ft.Colors.BLUE_800,
                                expand=True,
                            ),
                            edit_button,
                        ],
                        vertical_alignment=ft.CrossAxisAlignment.CENTER,
                    ),
                    ft.Row(
                        [
                            ft.Icon(
                                ft.Icons.PHONE, size=16, color=ft.Colors.BLUE_GREY_600
                            ),
                            ft.Text(
                                patient.masked_phone,
                                size=14,
                                color=ft.Colors.BLUE_GREY_600,
                            ),
                        ],
                        spacing=5,
                    ),
                    ft.Row(
                        [
                            ft.Icon(
                                ft.Icons.ACCESS_TIME, size=16, color=ft.Colors.GREEN_600
                            ),
                            ft.Text(
                                f"Checked in at {arrival_time}",
                                size=14,
                                color=ft.Colors.GREEN_600,
                            ),
                        ],
                        spacing=5,
                    ),
                ],
                spacing=4,
                tight=True,
            )

            return ft.Container(
                content=patient_info,
                bgcolor=ft.Colors.WHITE,
                border=ft.border.all(1, ft.Colors.BLUE_GREY_200),
                border_radius=8,
                padding=ft.Padding(15, 12, 15, 12),
                margin=ft.margin.only(bottom=8),
                # Add hover effect with correct animation reference
                animate=ft.Animation(150, ft.AnimationCurve.EASE_IN_OUT),
            )

        except Exception as e:
            logger.error(f"Error creating arrival card: {str(e)}")
            import traceback

            logger.error(f"Full traceback: {traceback.format_exc()}")
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
            bgcolor=ft.Colors.RED_100,
            border_radius=ft.border_radius.all(8),
            padding=ft.Padding(15, 12, 15, 12),
            margin=ft.margin.only(bottom=5),
        )

    def _handle_edit_patient(self, patient: Patient):
        """Handle edit patient button click."""
        try:
            logger.info(f"Opening edit dialog for patient: {patient.masked_phone}")

            # Check if we have a page reference
            if not hasattr(self, "page") or not self.page:
                logger.error("No page reference available for patient edit dialog")
                return

            # Show edit dialog
            show_patient_edit_dialog(
                patient=patient, page=self.page, on_save=self._handle_patient_updated
            )

        except Exception as e:
            logger.error(f"Error opening patient edit dialog: {str(e)}")

    def _handle_patient_updated(self, updated_patient: Patient):
        """Handle successful patient update."""
        try:
            logger.info(f"Patient updated: {updated_patient.masked_phone}")

            # Refresh the arrivals view to show updated information
            self._load_arrivals()

            # Update the page
            if hasattr(self, "page") and self.page:
                self.page.update()

        except Exception as e:
            logger.error(f"Error handling patient update: {str(e)}")

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
