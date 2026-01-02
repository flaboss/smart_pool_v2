import flet as ft


def history_view(t):
    return ft.Container(
        content=ft.Text("History", size=24, weight=ft.FontWeight.BOLD),
        alignment=ft.Alignment.TOP_LEFT,
        expand=True,
    )
