import flet as ft


def pools_view(navigate):
    return ft.Container(
        content=ft.Column(controls=[
            ft.Text("Pools", size=24, weight=ft.FontWeight.BOLD),
            ft.TextButton("Calculator", on_click=lambda e: navigate("cubic_calculator")),
        ], 
        spacing=16),
        alignment=ft.Alignment.TOP_LEFT,
        padding=20,
        expand=True
    )
