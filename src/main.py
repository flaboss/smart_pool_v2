import logging
import flet as ft
from i18n.translator import Translator
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
    current_language = "pt"
    current_unit = "m"
    translator = Translator(lang=current_language)

    print("Platform:", page.platform)

    # if page.platform in (ft.PagePlatform.MACOS,):
    #     print("Setting window size for desktop development")
    #     page.window.width = 390
    #     page.window.height = 844
    #     page.window.resizable = False

    content = ft.Container(expand=True)

    views = {
        "home": home_view,
        "pools": pools_view,
        "analysis": analysis_view,
        "history": history_view,
        "settings": settings_view,
        "cubic_calculator": cubic_calculator_view,
    }

    def t(key):
        return translator.t(key)

    def set_language(lang, view_key="home"):
        translator.load(lang)
        nonlocal current_language
        current_language = lang
        navigate(view_key)

    def set_theme_mode(is_dark):
        page.theme_mode = ft.ThemeMode.DARK if is_dark else ft.ThemeMode.LIGHT
        page.bgcolor = "#4C4D4F" if is_dark else "#83CEF3"
        page.update()

    def set_global_unit(unit):
        nonlocal current_unit
        current_unit = unit
        print("Global unit set to:", current_unit)

    def navigate(view_key):
        view_fn = views[view_key]

        if view_key in ["pools"]:
            content.content = base_layout(view_fn(navigate, t))
        elif view_key in ["settings"]:
            content.content = base_layout(
                view_fn(
                    navigate,
                    set_theme_mode,
                    page.theme_mode,
                    t,
                    set_language,
                    current_language,
                    set_global_unit,
                    current_unit
                )
            )
        elif view_key in ["cubic_calculator"]:
            content.content = base_layout(
                view_fn(
                    t,
                    current_unit
                )
            )
        else:
            content.content = base_layout(view_fn(t))
        page.update()

    def on_navigation_change(e):
        index = e.control.selected_index
        view_key = [k for k in views.keys()][index]

        navigate(view_key)
        ft.NavigationBar.selected_index = index
        page.update()

    # Conteúdo inicial
    navigate("home")

    # Menu inferior
    navigation = ft.NavigationBar(
        selected_index=0,
        #height=56,
        elevation=0,
        destinations=[
            ft.NavigationBarDestination(icon=ft.Icons.HOME, adaptive=True),
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
            spacing=0,
            expand=True,
            controls=[
                ft.SafeArea(
                    expand=True,
                    content=content,
                ),
                navigation,
            ],
        )
    )


if __name__ == "__main__":
    ft.run(main)
