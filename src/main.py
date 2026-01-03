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
from views.login import login_view

logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)


def main(page: ft.Page):
    page.title = "Smart Pool"
    page.theme_mode = ft.ThemeMode.SYSTEM
    current_language = "pt"
    current_unit = "m"
    translator = Translator(lang=current_language)
    is_authenticated = False
    user_email = None

    print("Platform:", page.platform)

    # Set window size for desktop development to simulate mobile view
    if page.platform in (ft.PagePlatform.MACOS, ft.PagePlatform.WINDOWS, ft.PagePlatform.LINUX):
        print("Setting window size for desktop development")
        page.window.width = 390
        page.window.height = 844
        page.window.resizable = False
        page.window.center()

    content = ft.Container(expand=True)
    navigation = ft.Ref[ft.NavigationBar]()

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
        if is_authenticated:
            navigate(view_key)
        else:
            show_login()

    def set_theme_mode(is_dark):
        page.theme_mode = ft.ThemeMode.DARK if is_dark else ft.ThemeMode.LIGHT
        page.bgcolor = "#4C4D4F" if is_dark else "#83CEF3"
        page.update()

    def set_global_unit(unit):
        nonlocal current_unit
        current_unit = unit

    def navigate(view_key):
        if not is_authenticated:
            show_login()
            return
        
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
        if not is_authenticated:
            show_login()
            return
        
        index = e.control.selected_index
        view_key = [k for k in views.keys()][index]

        navigate(view_key)
        navigation.current.selected_index = index
        page.update()

    def show_login():
        """Show the login page."""
        nonlocal is_authenticated
        is_authenticated = False
        
        def on_login_success(email):
            """Handle successful login."""
            nonlocal is_authenticated, user_email
            is_authenticated = True
            user_email = email
            # TODO: Store authentication state (e.g., in shared_preferences)
            # For now, just navigate to home
            navigation.current.visible = True
            navigate("home")
            page.update()
        
        def login_set_language(lang):
            """Set language from login page."""
            translator.load(lang)
            nonlocal current_language
            current_language = lang
            show_login()  # Refresh login page with new language
        
        content.content = login_view(
            page,
            t,
            login_set_language,
            current_language,
            on_login_success
        )
        
        # Hide navigation bar on login page
        navigation.current.visible = False
        page.update()

    # Menu inferior
    nav_bar = ft.NavigationBar(
        ref=navigation,
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
        visible=False,  # Hidden initially (login page)
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
                nav_bar,
            ],
        )
    )
    
    # Show login page initially
    show_login()


if __name__ == "__main__":
    ft.run(main)
