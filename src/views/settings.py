import flet as ft


def settings_view():
    return ft.Container(
        content=ft.Column(controls=[
            ft.Text("Settings View", size=24, weight=ft.FontWeight.BOLD),
            ft.TextField(label="Nome", hint_text="Digite seu nome"),
            ft.TextField(label="País", hint_text="País de residência"),
            ft.TextField(label="Cidade", hint_text="Cidade de residência"),
            ft.Dropdown(label="Idioma", value="pt", options=[
                ft.dropdown.Option("pt", "Português"),
                ft.dropdown.Option("en", "English"),
                ft.dropdown.Option("es", "Español"),
            ]),
            ft.Switch(label="Modo Escuro", value=True),
        ], 
        spacing=16,
    ),
    alignment=ft.Alignment.TOP_LEFT,
    padding=20,
    expand=True
    
    )