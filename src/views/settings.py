import flet as ft
from database.local_storage import LocalStorage


def settings_view(
    navigate, set_theme_mode, current_theme_mode, t, set_language, curr_lang,
    set_global_unit, curr_unit, logout
):
    mode_true = True if current_theme_mode == ft.ThemeMode.DARK else False
    
    # Load saved user info
    saved_prefs = LocalStorage.get_all_preferences()
    saved_name = saved_prefs.get("name", "")
    saved_country = saved_prefs.get("country", "")
    saved_city = saved_prefs.get("city", "")
    
    # Create text fields with saved values
    name_field = ft.TextField(
        label=t("settings.name"),
        hint_text=t("settings.name_hint"),
        value=saved_name,
        on_change=lambda e: LocalStorage.save_preference("name", e.control.value),
    )
    country_field = ft.TextField(
        label=t("settings.country"),
        hint_text=t("settings.country_hint"),
        value=saved_country,
        on_change=lambda e: LocalStorage.save_preference("country", e.control.value),
    )
    city_field = ft.TextField(
        label=t("settings.city"),
        hint_text=t("settings.city_hint"),
        value=saved_city,
        on_change=lambda e: LocalStorage.save_preference("city", e.control.value),
    )

    return ft.Container(
        bgcolor=ft.Colors.SURFACE,
        content=ft.Column(
            controls=[
                ft.Text(t("settings.title"), size=24, weight=ft.FontWeight.BOLD),
                name_field,
                country_field,
                city_field,
                ft.Dropdown(
                    label=t("settings.language"),
                    value=curr_lang,
                    options=[
                        ft.dropdown.Option("pt", "Português"),
                        ft.dropdown.Option("en", "English"),
                        ft.dropdown.Option("es", "Español"),
                    ],
                    on_select=lambda e: set_language(
                        e.control.value, view_key="settings"
                    ),
                ),
                ft.Switch(
                    label=t("settings.dark_mode"),
                    value=mode_true,
                    on_change=lambda e: set_theme_mode(e.control.value),
                ),
                ft.Dropdown(
                    label=t("settings.units"), 
                    value=curr_unit, 
                    options=[
                        ft.dropdown.Option("metric", "m³"),
                        ft.dropdown.Option("imperial", "ft³"),
                ],
                    on_select=lambda e: set_global_unit(e.control.value),
                ),
                ft.TextButton(
                    t("settings.calculator"),
                    on_click=lambda e: navigate("cubic_calculator"),
                ),
                ft.Divider(),
                ft.Button(
                    content=t("settings.logout"),
                    icon=ft.Icons.LOGOUT,
                    on_click=lambda e: logout(),
                    color=ft.Colors.RED,
                ),
            ],
            spacing=16,
        ),
        alignment=ft.Alignment.TOP_LEFT,
        padding=20,
        expand=True,
    )
