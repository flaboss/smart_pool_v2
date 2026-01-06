import flet as ft
from datetime import datetime
from database.pool_service import PoolService
from database.analysis_service import AnalysisService
from database.local_storage import LocalStorage
from ml_models.pool_analyzer import PoolAnalyzer

class AnalysisContent(ft.Container):
    def __init__(self, t):
        super().__init__(expand=True)
        self.t = t
        self.user_id = LocalStorage.get_auth().get("user_id") if LocalStorage.get_auth() else "guest"
        self.current_view = "menu" # menu, form, result
        self.pools = []
        self.analysis_result = None
        
        # Form Controls
        self.pool_dropdown = ft.Dropdown(
            label=self.t("analysis.select_pool"),
            options=[],
            border_color=ft.Colors.OUTLINE
        )
        self.ph_field = ft.TextField(label=self.t("analysis.ph"), keyboard_type=ft.KeyboardType.NUMBER, border_color=ft.Colors.OUTLINE)
        self.chlorine_field = ft.TextField(label=self.t("analysis.chlorine"), keyboard_type=ft.KeyboardType.NUMBER, border_color=ft.Colors.OUTLINE)
        self.alkalinity_field = ft.TextField(label=self.t("analysis.alkalinity"), keyboard_type=ft.KeyboardType.NUMBER, border_color=ft.Colors.OUTLINE)
        self.cyanuric_field = ft.TextField(label=self.t("analysis.cyanuric"), keyboard_type=ft.KeyboardType.NUMBER, border_color=ft.Colors.OUTLINE)
        self.observation_field = ft.TextField(
            label=self.t("analysis.observation"), 
            hint_text=self.t("analysis.observation_hint"), 
            multiline=True, 
            min_lines=2,
            border_color=ft.Colors.OUTLINE
        )
        self.has_image = False
        
        self.file_picker = None # Disabled for now
        
        self.photo_options_dialog = ft.AlertDialog(
            title=ft.Text(self.t("analysis.dialog_title")),
            actions=[
                ft.TextButton(self.t("analysis.option_camera"), on_click=self._on_camera_click),
                ft.TextButton(self.t("analysis.option_gallery"), on_click=self._on_gallery_click),
                ft.TextButton(self.t("common.cancel"), on_click=self._close_photo_dialog)
            ],
            actions_alignment=ft.MainAxisAlignment.END,
        )

        self.main_container = ft.Container(expand=True)
        self.content = self.main_container

        self.refresh_view()

    def did_mount(self):
        # Determine if we need to fetch pools
        self._load_pools()
        # Add dialog to page overlay
        if self.page:
            self.page.overlay.append(self.photo_options_dialog)
            self.page.update()

    def _load_pools(self):
        # Syncing might be async, but we can get local pools immediately
        self.pools = PoolService.get_pools(self.user_id)
        self.pool_dropdown.options = [
            ft.dropdown.Option(p.get('id'), p.get('name')) for p in self.pools
        ]
        if self.pools:
            self.pool_dropdown.value = self.pools[0].get('id')
        self.update()

    def refresh_view(self):
        if self.current_view == "menu":
            self.main_container.content = self._build_menu()
        elif self.current_view == "form":
            self.main_container.content = self._build_form()
        elif self.current_view == "result":
            self.main_container.content = self._build_result()
        try:
            if self.page:
                 self.main_container.update()
        except RuntimeError:
            pass

    def _build_menu(self):
        return ft.Column(
            controls=[
                ft.Container(height=20),
                ft.Text(self.t("analysis.title"), size=24, weight=ft.FontWeight.BOLD, color=ft.Colors.ON_SURFACE),
                ft.Container(height=40),
                self._create_menu_button(
                    self.t("analysis.menu_water"), 
                    ft.Icons.WATER_DROP, 
                    ft.Colors.PRIMARY, 
                    lambda e: self._navigate_to("form")
                ),
                ft.Container(height=20),
                self._create_menu_button(
                    f"{self.t('analysis.menu_chat')} {self.t('analysis.coming_soon')}", 
                    ft.Icons.CHAT_BUBBLE, 
                    ft.Colors.GREY, 
                    None,
                    disabled=True
                )
            ],
            horizontal_alignment=ft.CrossAxisAlignment.CENTER,
            expand=True
        )

    def _create_menu_button(self, text, icon, color, on_click, disabled=False):
        return ft.Container(
            content=ft.Row(
                controls=[
                    ft.Icon(icon, size=40, color=ft.Colors.ON_PRIMARY_CONTAINER if not disabled else ft.Colors.GREY_400),
                    ft.Text(text, size=18, weight=ft.FontWeight.BOLD, color=ft.Colors.ON_PRIMARY_CONTAINER if not disabled else ft.Colors.GREY_400, expand=True)
                ],
                alignment=ft.MainAxisAlignment.CENTER,
            ),
            bgcolor=ft.Colors.PRIMARY_CONTAINER if not disabled else ft.Colors.GREY_200,
            padding=30,
            border_radius=15,
            on_click=on_click,
            disabled=disabled,
            ink=True,
        )

    def _build_form(self):
        return ft.Column(
            controls=[
                ft.Row([
                    ft.IconButton(ft.Icons.ARROW_BACK, on_click=lambda e: self._navigate_to("menu"), icon_color=ft.Colors.ON_SURFACE),
                    ft.Text(self.t("analysis.menu_water"), size=20, weight=ft.FontWeight.BOLD, color=ft.Colors.ON_SURFACE),
                ]),
                ft.Container(height=10),
                self.pool_dropdown,
                self.ph_field,
                self.chlorine_field,
                self.alkalinity_field,
                self.cyanuric_field,
                self.observation_field,
                ft.Container(height=10),
                ft.OutlinedButton(
                    content=ft.Row([
                        ft.Icon(ft.Icons.CAMERA_ALT, color=ft.Colors.PRIMARY if not self.has_image else ft.Colors.GREEN),
                        ft.Text(self.t("analysis.take_photo") if not self.has_image else self.t("analysis.photo_taken"), color=ft.Colors.PRIMARY if not self.has_image else ft.Colors.GREEN)
                    ], alignment=ft.MainAxisAlignment.CENTER),
                    on_click=self._open_photo_dialog,
                    style=ft.ButtonStyle(
                        side=ft.BorderSide(1, ft.Colors.PRIMARY if not self.has_image else ft.Colors.GREEN)
                    )
                ),
                ft.Container(height=20),
                ft.FilledButton(
                    content=self.t("analysis.analyze_btn"),
                    on_click=self._on_analyze_click,
                    width=float('inf'), # Full width
                    style=ft.ButtonStyle(padding=15)
                )
            ],
            scroll=ft.ScrollMode.AUTO,
            expand=True
        )

    def _build_result(self):
        if not self.analysis_result:
            return ft.Container()
        
        return ft.Column(
            controls=[
                 ft.Row([
                    ft.IconButton(ft.Icons.ARROW_BACK, on_click=lambda e: self._navigate_to("menu"), icon_color=ft.Colors.ON_SURFACE),
                    ft.Text(self.t("analysis.result_title"), size=20, weight=ft.FontWeight.BOLD, color=ft.Colors.ON_SURFACE),
                ]),
                ft.Container(height=20),
                ft.Container(
                    content=ft.Column([
                        ft.Text(self.t("analysis.result_title"), weight=ft.FontWeight.BOLD, size=18, color=ft.Colors.ON_SURFACE_VARIANT),
                        ft.Markdown(self.analysis_result['analysis'], extension_set=ft.MarkdownExtensionSet.GITHUB_WEB),
                        ft.Divider(),
                        ft.Text(self.t("analysis.recommendation"), weight=ft.FontWeight.BOLD, size=18, color=ft.Colors.ON_SURFACE_VARIANT),
                         ft.Markdown(self.analysis_result['recommendation'], extension_set=ft.MarkdownExtensionSet.GITHUB_WEB),
                    ]),
                    padding=20,
                    bgcolor="surfaceVariant",
                    border_radius=10,
                ),
                ft.Container(height=20),
                ft.FilledButton(
                    content=self.t("analysis.back_menu"),
                    on_click=lambda e: self._navigate_to("menu"),
                    width=float('inf')
                )
            ],
            scroll=ft.ScrollMode.AUTO,
            expand=True
        )

    def _navigate_to(self, view_name):
        self.current_view = view_name
        self.refresh_view()

    # def _on_image_picked(self, e):
    #     if e.files and len(e.files) > 0:
    #         self.image_path = e.files[0].path
    #         self.has_image = True
    #         self.page.show_dialog(ft.SnackBar(content=ft.Text("Image loaded!")))
    #         self.refresh_view()
    #     else:
    #         # User cancelled
    #         pass

    def _open_photo_dialog(self, e):
        self.photo_options_dialog.open = True
        self.page.update()

    def _close_photo_dialog(self, e):
        self.photo_options_dialog.open = False
        self.page.update()

    def _on_camera_click(self, e):
        # Placeholder for Camera
        self.photo_options_dialog.open = False
        self._mock_photo_taken(None) # Re-use mock for now
        self.page.update()

    def _on_gallery_click(self, e):
        # Placeholder for Gallery
        self.photo_options_dialog.open = False
        self._mock_photo_taken(None) # Re-use mock for now
        self.page.update()

    def _mock_photo_taken(self, e):
        self.image_path = "mock_image.jpg" # Dummy path
        self.has_image = True
        self.page.show_dialog(ft.SnackBar(content=ft.Text("Mock Photo Taken")))
        self.refresh_view()

    async def _on_analyze_click(self, e):
        # Validate inputs
        if not self.ph_field.value or not self.chlorine_field.value:
             self.page.show_dialog(ft.SnackBar(ft.Text(self.t("analysis.error_required_fields"))))
             return

        try:
            params = {
                'pool_id': self.pool_dropdown.value,
                'ph': self.ph_field.value,
                'chlorine': self.chlorine_field.value,
                'alkalinity': self.alkalinity_field.value or None,
                'cyanuric_acid': self.cyanuric_field.value or None,
                'observation': self.observation_field.value,
                'has_image': self.has_image,
                'timestamp': datetime.now().isoformat()
            }
        except ValueError:
            pass
            
        # Refine params for analyzer
        # We ensure they are strings or None, Analyzer handles the logic
        safe_params = {
            'ph': self.ph_field.value,
            'chlorine': self.chlorine_field.value,
            'alkalinity': self.alkalinity_field.value or None,
            'cyanuric_acid': self.cyanuric_field.value or None,
            'observation': self.observation_field.value,
            'has_image': self.has_image,
            'image_path': self.image_path
        }

        # Run Analysis
        result = PoolAnalyzer.analyze(safe_params, self.t)
        self.analysis_result = result
        
        # Save Result
        save_data = {
            **params,
            **result
        }
        await AnalysisService.save_analysis(self.user_id, save_data)
        
        self.current_view = "result"
        self.refresh_view()

def analysis_view(t):
    return ft.Container(
        content=AnalysisContent(t),
        padding=20,
        expand=True,
    )
