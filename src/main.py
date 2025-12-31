import flet as ft
from ui.layout import base_layout
from views.home import home_view
from views.pools import pools_view
from views.settings import settings_view
from views.analysis import analysis_view
from views.history import history_view


def main(page: ft.Page):
    page.title = "Smart Pool"
    page.theme_mode = ft.ThemeMode.SYSTEM
    page.bgcolor = "#121212"

    content = ft.Container(expand=True)

    views = {
        0: home_view,
        1: pools_view,
        2: analysis_view,
        3: history_view,
        4: settings_view,
    }

    def on_navigation_change(e):
        index = e.control.selected_index
        content.content = base_layout(views[index]())
        page.update()

    # Conteúdo inicial
    content.content = base_layout(home_view())

    # Menu inferior
    navigation = ft.NavigationBar(
        selected_index=0,
        destinations=[
            ft.NavigationBarDestination(icon=ft.Icons.HOME),
            ft.NavigationBarDestination(icon=ft.Icons.POOL),
            ft.NavigationBarDestination(icon=ft.Icons.AUTO_AWESOME),
            ft.NavigationBarDestination(icon=ft.Icons.HISTORY),
            ft.NavigationBarDestination(icon=ft.Icons.SETTINGS),
        ],
        on_change=on_navigation_change,
    )
    # Layout final
    page.add(
        ft.Column(
            controls=[
                content,
                navigation
            ],
            expand=True
        )
    )

ft.app(target=main)
