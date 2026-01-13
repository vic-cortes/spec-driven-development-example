import flet as ft


def main(page: ft.Page):
    """Main Flet app entry point."""
    page.title = "Dental Patient Check-In"
    page.window_width = 400
    page.window_height = 600
    page.window_resizable = True

    # Placeholder content
    page.add(
        ft.Text("Dental Patient Check-In", size=24, weight=ft.FontWeight.BOLD),
        ft.Text("Coming soon...", size=16),
    )


if __name__ == "__main__":
    ft.app(target=main)
