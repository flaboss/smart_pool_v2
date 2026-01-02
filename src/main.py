import logging
import flet as ft
from ui.layout import base_layout
from views.home import home_view
from views.pools import pools_view
from views.settings import settings_view
from views.analysis import analysis_view
from views.history import history_view
from views.cubic_calculator import cubic_calculator_view

logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)

def main(page: ft.Page):
    page.title = "Smart Pool"
    page.theme_mode = ft.ThemeMode.SYSTEM
    page.bgcolor = "#4C4D4F"

    print("Platform:", page.platform)

    if page.platform in (
        ft.PagePlatform.MACOS,
    ):
        print("Setting window size for desktop development")
        page.window.width = 390
        page.window.height = 844
        page.window.resizable = False
    
    content = ft.Container(expand=True)

    views = {
        "home": home_view,
        "pools": pools_view,
        "analysis": analysis_view,
        "history": history_view,
        "settings": settings_view,
        "cubic_calculator": cubic_calculator_view,
    }

    def navigate(view_key):
        view_fn = views[view_key]

        if view_key in ['pools']:
            content.content = base_layout(view_fn(navigate))
        else:
            content.content = base_layout(view_fn())
        page.update()


    def on_navigation_change(e):
        index = e.control.selected_index
        view_key = [k for k in views.keys()][index]
        logger.debug(f"Navigation changed to index: {index}: {view_key}")

        #import pdb; pdb.set_trace()
        #content.content = base_layout(views[index]())
        #content.content = base_layout(views[view_key]())
        navigate(view_key)
        ft.NavigationBar.selected_index = index
        page.update()

    # Conteúdo inicial
    navigate("home")

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

if __name__ == "__main__":
    ft.run(main)