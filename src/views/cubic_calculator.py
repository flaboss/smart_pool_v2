import flet as ft


def cubic_calculator_view(t):
    return ft.Container(
        content=ft.Text(t("settings.calculator"), size=24, weight=ft.FontWeight.BOLD),
        alignment=ft.Alignment.TOP_LEFT,
        expand=True,
    )
