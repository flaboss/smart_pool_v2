import flet as ft


def base_layout(content: ft.Control):
    return ft.Container(bgcolor="#121212", padding=20, content=content, expand=True)
