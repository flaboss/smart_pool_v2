import flet as ft
from database.firebase_auth import FirebaseAuth


def login_view(page, t, set_language, current_language, on_login_success):
    """Login view with language selector and account creation option."""
    
    # State for login/signup mode
    is_signup_mode = [False]  # Use list to allow mutation in nested functions
    
    # Form fields
    email_field = ft.Ref[ft.TextField]()
    password_field = ft.Ref[ft.TextField]()
    confirm_password_field = ft.Ref[ft.TextField]()
    error_text = ft.Ref[ft.Text]()
    submit_button = ft.Ref[ft.Button]()
    toggle_button = ft.Ref[ft.TextButton]()
    
    def toggle_mode(e):
        """Toggle between login and signup modes."""
        is_signup_mode[0] = not is_signup_mode[0]
        confirm_password_field.current.visible = is_signup_mode[0]
        submit_button.current.text = t("login.signup") if is_signup_mode[0] else t("login.login")
        toggle_button.current.text = t("login.have_account") if is_signup_mode[0] else t("login.create_account")
        error_text.current.value = ""
        error_text.current.visible = False
        page.update()
    
    async def handle_submit(e):
        """Handle login or signup submission."""
        email = email_field.current.value
        password = password_field.current.value
        
        # Basic validation
        if not email or not email.strip():
            error_text.current.value = t("login.error_email_required")
            error_text.current.visible = True
            page.update()
            return
        
        if not password or len(password) < 6:
            error_text.current.value = t("login.error_password_length")
            error_text.current.visible = True
            page.update()
            return
        
        # Disable button during processing
        submit_button.current.disabled = True
        error_text.current.visible = False
        page.update()
        
        try:
            if is_signup_mode[0]:
                confirm_password = confirm_password_field.current.value
                if password != confirm_password:
                    error_text.current.value = t("login.error_password_mismatch")
                    error_text.current.visible = True
                    submit_button.current.disabled = False
                    page.update()
                    return
                
                # Firebase signup
                success, user_id, token, error_msg = await FirebaseAuth.sign_up(email, password)
                
                if success:
                    # Clear error and proceed
                    error_text.current.visible = False
                    on_login_success(email, user_id, token)
                else:
                    error_text.current.value = error_msg or t("login.error_signup_failed")
                    error_text.current.visible = True
                    submit_button.current.disabled = False
                    page.update()
            else:
                # Firebase login
                success, user_id, token, error_msg = await FirebaseAuth.sign_in(email, password)
                
                if success:
                    # Clear error and proceed
                    error_text.current.visible = False
                    on_login_success(email, user_id, token)
                else:
                    error_text.current.value = error_msg or t("login.error_login_failed")
                    error_text.current.visible = True
                    submit_button.current.disabled = False
                    page.update()
        except Exception as ex:
            error_text.current.value = f"An error occurred: {str(ex)}"
            error_text.current.visible = True
            submit_button.current.disabled = False
            page.update()
    
    # Create the view
    return ft.Container(
        bgcolor=ft.Colors.SURFACE,
        content=ft.Column(
            controls=[
                # Language selector
                ft.Container(
                    content=ft.Dropdown(
                        label=t("settings.language"),
                        value=current_language,
                        options=[
                            ft.dropdown.Option("pt", "Português"),
                            ft.dropdown.Option("en", "English"),
                            ft.dropdown.Option("es", "Español"),
                        ],
                        on_select=lambda e: set_language(e.control.value),
                    ),
                    alignment=ft.Alignment.TOP_RIGHT,
                    padding=ft.Padding.only(right=20, top=20),
                ),
                
                # Main content
                ft.Container(
                    content=ft.Column(
                        controls=[
                            ft.Text(
                                t("login.title"),
                                size=32,
                                weight=ft.FontWeight.BOLD,
                                text_align=ft.TextAlign.CENTER,
                            ),
                            ft.Text(
                                t("login.subtitle"),
                                size=16,
                                text_align=ft.TextAlign.CENTER,
                                color=ft.Colors.GREY,
                            ),
                            ft.Divider(height=40, color=ft.Colors.TRANSPARENT),
                            
                            # Email field
                            ft.TextField(
                                ref=email_field,
                                label=t("login.email"),
                                hint_text=t("login.email_hint"),
                                keyboard_type=ft.KeyboardType.EMAIL,
                            ),
                            
                            # Password field
                            ft.TextField(
                                ref=password_field,
                                label=t("login.password"),
                                hint_text=t("login.password_hint"),
                                password=True,
                                can_reveal_password=True,
                            ),
                            
                            # Confirm password field (only visible in signup mode)
                            ft.TextField(
                                ref=confirm_password_field,
                                label=t("login.confirm_password"),
                                hint_text=t("login.confirm_password_hint"),
                                password=True,
                                can_reveal_password=True,
                                visible=False,
                            ),
                            
                            # Error message
                            ft.Text(
                                ref=error_text,
                                color=ft.Colors.RED,
                                visible=False,
                                size=12,
                            ),
                            
                            # Submit button
                            ft.Button(
                                ref=submit_button,
                                content=t("login.login"),
                                on_click=handle_submit,
                                height=50,
                            ),
                            
                            # Toggle between login and signup
                            ft.Row(
                                controls=[
                                    ft.Text(t("login.no_account")),
                                    ft.TextButton(
                                        ref=toggle_button,
                                        content=t("login.create_account"),
                                        on_click=toggle_mode,
                                    ),
                                ],
                                alignment=ft.MainAxisAlignment.CENTER,
                            ),
                        ],
                        horizontal_alignment=ft.CrossAxisAlignment.STRETCH,
                        spacing=16,
                    ),
                    padding=40,
                    alignment=ft.Alignment.CENTER,
                    expand=True,
                ),
            ],
            spacing=0,
            expand=True,
        ),
        expand=True,
    )

