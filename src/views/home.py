import flet as ft


def home_view():
    return ft.Container(
        content=ft.Text("Welcome to Smart Pool", size=20, weight=ft.FontWeight.BOLD),
        alignment=ft.Alignment.TOP_LEFT,
        expand=True,
    )
