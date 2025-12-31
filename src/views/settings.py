import flet as ft


def settings_view():
    return ft.Container(
        content=ft.Text("Settings", size=24, weight=ft.FontWeight.BOLD),
        alignment=ft.Alignment.TOP_LEFT,
        expand=True,
    )
