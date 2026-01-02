import flet as ft


def analysis_view(t):
    return ft.Container(
        content=ft.Text("Analysis", size=24, weight=ft.FontWeight.BOLD),
        align=ft.Alignment.TOP_LEFT,
        expand=True,
    )
