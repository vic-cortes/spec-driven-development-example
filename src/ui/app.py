"""Main Flet application with navigation and check-in functionality."""

import flet as ft

from src.data.mock_seed import seed_mock_data
from src.services.logger import logger
from src.ui.checkin_view import CheckInView


class DentalCheckInApp:
    """Main application class for the dental check-in system."""

    def __init__(self, page: ft.Page):
        self.page = page
        self.setup_page()
        self.setup_navigation()
        self.setup_views()

        # Seed mock data on startup
        seed_mock_data()
        logger.info("Dental check-in app started")

    def setup_page(self):
        """Configure the main page settings."""
        self.page.title = "Dental Patient Check-In"
        self.page.window_width = 500
        self.page.window_height = 700
        self.page.window_resizable = True
        self.page.window_min_width = 400
        self.page.window_min_height = 600

        # Mobile-friendly settings
        self.page.adaptive = True
        self.page.theme_mode = ft.ThemeMode.LIGHT

        # Padding for mobile devices
        self.page.padding = ft.Padding(left=10, top=10, right=10, bottom=10)

    def setup_navigation(self):
        """Setup navigation bar."""
        self.nav_rail = ft.NavigationRail(
            selected_index=0,
            label_type=ft.NavigationRailLabelType.SELECTED,
            min_width=100,
            min_extended_width=200,
            destinations=[
                ft.NavigationRailDestination(
                    icon=ft.Icons.LOGIN, selected_icon=ft.Icons.LOGIN, label="Check-In"
                ),
                ft.NavigationRailDestination(
                    icon=ft.Icons.LIST,
                    selected_icon=ft.Icons.LIST,
                    label="Today's Arrivals",
                ),
            ],
            on_change=self.on_nav_change,
            visible=True,
        )

        # For mobile, use bottom navigation instead
        self.bottom_nav = ft.NavigationBar(
            destinations=[
                ft.NavigationBarDestination(
                    icon=ft.Icons.LOGIN, selected_icon=ft.Icons.LOGIN, label="Check-In"
                ),
                ft.NavigationBarDestination(
                    icon=ft.Icons.LIST, selected_icon=ft.Icons.LIST, label="Arrivals"
                ),
            ],
            on_change=self.on_nav_change,
            selected_index=0,
        )

    def setup_views(self):
        """Setup application views."""
        # Check-in view
        self.checkin_view = CheckInView(on_checkin_complete=self.on_checkin_complete)

        # Today's arrivals placeholder (will be implemented in Phase 4)
        self.arrivals_view = ft.Container(
            content=ft.Column(
                [
                    ft.Text(
                        "Today's Arrivals",
                        size=24,
                        weight=ft.FontWeight.BOLD,
                        color=ft.Colors.BLUE,
                    ),
                    ft.Divider(),
                    ft.Text("Coming soon in Phase 4...", size=16, color=ft.Colors.GREY),
                ]
            ),
            padding=20,
        )

        # Main content area
        self.content_area = ft.Container(content=self.checkin_view, expand=True)

        # Responsive layout
        self.desktop_layout = ft.Row(
            [self.nav_rail, ft.VerticalDivider(width=1), self.content_area], expand=True
        )

        self.mobile_layout = ft.Column(
            [self.content_area, self.bottom_nav], expand=True
        )

        # Start with desktop layout
        self.current_layout = self.desktop_layout
        self.page.add(self.current_layout)

    def on_nav_change(self, e):
        """Handle navigation changes."""
        selected_index = e.control.selected_index

        if selected_index == 0:
            # Check-in view
            self.content_area.content = self.checkin_view
            logger.info("Switched to check-in view")
        elif selected_index == 1:
            # Today's arrivals view
            self.content_area.content = self.arrivals_view
            logger.info("Switched to arrivals view")

        # Update both navigation controls
        self.nav_rail.selected_index = selected_index
        self.bottom_nav.selected_index = selected_index

        self.page.update()

    def on_checkin_complete(self, checkin, patient):
        """Handle check-in completion."""
        logger.info(f"Check-in completed for {patient.full_name}")
        # Could trigger arrivals view refresh here in Phase 4

    def handle_resize(self):
        """Handle window resize for responsive layout."""
        # Switch between desktop and mobile layouts based on width
        if self.page.window_width < 600:
            if self.current_layout != self.mobile_layout:
                self.page.controls.clear()
                self.page.add(self.mobile_layout)
                self.current_layout = self.mobile_layout
                self.nav_rail.visible = False
        else:
            if self.current_layout != self.desktop_layout:
                self.page.controls.clear()
                self.page.add(self.desktop_layout)
                self.current_layout = self.desktop_layout
                self.nav_rail.visible = True

        self.page.update()

    def show_info_dialog(self, title: str, message: str):
        """Show an information dialog."""
        dialog = ft.AlertDialog(
            title=ft.Text(title),
            content=ft.Text(message),
            actions=[ft.TextButton("OK", on_click=lambda e: self.page.close_dialog())],
        )

        self.page.dialog = dialog
        dialog.open = True
        self.page.update()


def main(page: ft.Page):
    """Main entry point for the Flet app."""
    app = DentalCheckInApp(page)

    # Handle page resize for responsive layout
    def on_resize(e):
        app.handle_resize()

    page.on_resize = on_resize

    # Initial resize check
    app.handle_resize()


if __name__ == "__main__":
    ft.app(target=main)
