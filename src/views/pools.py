import flet as ft


def pools_view(navigate, t):
    return ft.Container(
        content=ft.Column(
            controls=[
                ft.Text(t("pools.title"), size=24, weight=ft.FontWeight.BOLD),
                ft.TextButton(
                    t("settings.calculator"),
                    on_click=lambda e: navigate("cubic_calculator"),
                ),
            ],
            spacing=16,
        ),
        alignment=ft.Alignment.TOP_LEFT,
        padding=20,
        expand=True,
    )
