import flet as ft


def base_layout(content: ft.Control):
    return ft.Container(bgcolor=ft.Colors.SURFACE, padding=10, content=content, expand=True)
