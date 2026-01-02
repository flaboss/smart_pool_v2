import flet as ft


def cubic_calculator_view():
    return ft.Container(
        content=ft.Text("Calculator", size=24, weight=ft.FontWeight.BOLD),
        alignment=ft.Alignment.TOP_LEFT,
        expand=True,
    )