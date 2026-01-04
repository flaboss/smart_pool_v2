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
from database.local_storage import LocalStorage

logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)


def main(page: ft.Page):
    # Set default background to prevent black screen
    page.bgcolor = "#83CEF3"  # Light blue default
    page.title = "Smart Pool"
    
    # Load saved preferences with error handling
    try:
        saved_prefs = LocalStorage.get_all_preferences()
    except Exception as e:
        print(f"Error loading preferences: {e}")
        saved_prefs = {}
    
    current_language = saved_prefs.get("language", "pt")
    current_unit = saved_prefs.get("unit", "metric")
    saved_theme = saved_prefs.get("theme", "system")
    
    # Set theme mode
    if saved_theme == "dark":
        page.theme_mode = ft.ThemeMode.DARK
        page.bgcolor = "#4C4D4F"
    elif saved_theme == "light":
        page.theme_mode = ft.ThemeMode.LIGHT
        page.bgcolor = "#83CEF3"
    else:
        page.theme_mode = ft.ThemeMode.SYSTEM
        # System theme will be set automatically
    
    translator = Translator(lang=current_language)
    is_authenticated = False
    user_email = None
    user_id = None

    # Check for saved authentication with error handling
    try:
        saved_auth = LocalStorage.get_auth()
        if saved_auth:
            is_authenticated = True
            user_email = saved_auth.get("email")
            user_id = saved_auth.get("user_id")
            print(f"Auto-login for user: {user_email}")
    except Exception as e:
        print(f"Error loading auth: {e}")
        saved_auth = None

    print("Platform:", page.platform)

    # Configure page padding for Android to avoid system bars
    if page.platform == ft.PagePlatform.ANDROID:
        page.padding = 0
        page.spacing = 0

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
        LocalStorage.save_preference("language", lang)
        if is_authenticated:
            navigate(view_key)
        else:
            show_login()

    def set_theme_mode(is_dark):
        page.theme_mode = ft.ThemeMode.DARK if is_dark else ft.ThemeMode.LIGHT
        page.bgcolor = "#4C4D4F" if is_dark else "#83CEF3"
        # Save theme preference
        theme_value = "dark" if is_dark else "light"
        LocalStorage.save_preference("theme", theme_value)
        page.update()

    def set_global_unit(unit):
        nonlocal current_unit
        current_unit = unit
        LocalStorage.save_preference("unit", unit)

    def logout():
        """Handle user logout."""
        nonlocal is_authenticated, user_email, user_id
        is_authenticated = False
        user_email = None
        user_id = None
        LocalStorage.clear_auth()
        show_login()

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
                    current_unit,
                    logout
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
        
        def on_login_success(email, user_id_param=None):
            """Handle successful login."""
            nonlocal is_authenticated, user_email, user_id
            is_authenticated = True
            user_email = email
            user_id = user_id_param or email  # Use email as fallback if no user_id
            # Save authentication state
            LocalStorage.save_auth(user_id, email)
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
        height=56 if page.platform == ft.PagePlatform.ANDROID else None,
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

    # Layout final - use SafeArea to handle system bars on all platforms
    # On Android, this prevents content from going under status bar and navigation bar
    page.add(
        ft.SafeArea(
            expand=True,
            content=ft.Column(
                spacing=0,
                expand=True,
                controls=[
                    content,
                    nav_bar,
                ],
            ),
        )
    )
    
    # Initialize app - show login or home based on authentication
    try:
        if is_authenticated:
            navigation.current.visible = True
            navigate("home")
        else:
            show_login()
    except Exception as e:
        print(f"Error initializing app: {e}")
        import traceback
        traceback.print_exc()
        # Show error message on page
        page.add(
            ft.Container(
                content=ft.Column([
                    ft.Text("Error initializing app", size=20, weight=ft.FontWeight.BOLD),
                    ft.Text(str(e), size=12),
                ]),
                padding=20,
                alignment=ft.Alignment.CENTER,
                expand=True,
            )
        )
        page.update()


if __name__ == "__main__":
    ft.run(main)
