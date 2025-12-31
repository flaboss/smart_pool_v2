import flet as ft


def pools_view():
    return ft.Container(
        content=ft.Text("Pools", size=24, weight=ft.FontWeight.BOLD),
        alignment=ft.Alignment.TOP_LEFT,
        expand=True,
    )
