import flet as ft


def home_view(t):
    return ft.Container(
        content=ft.Text(t("home.welcome"), size=20, weight=ft.FontWeight.BOLD),
        alignment=ft.Alignment.TOP_LEFT,
        expand=True,
    )
