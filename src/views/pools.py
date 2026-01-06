import flet as ft
import copy
from database.pool_service import PoolService
from database.local_storage import LocalStorage

class PoolsContent(ft.Container):
    def __init__(self, navigate, t, unit_system):
        super().__init__(expand=True)
        self.navigate = navigate
        self.t = t
        self.unit_system = unit_system
        self.user_id = LocalStorage.get_auth().get("user_id") if LocalStorage.get_auth() else "guest"
        self.current_view = "list"  # "list" or "form"
        self.editing_pool = None
        
        unit_str = "mts" if self.unit_system == "metric" else "ft"

        # Form controls
        self.name_field = ft.TextField(label=self.t("pools.name"), hint_text=self.t("pools.name_hint"), border_color=ft.Colors.OUTLINE)
        self.volume_field = ft.TextField(label=f"{self.t('pools.volume')} ({unit_str}³)", hint_text=self.t("pools.volume_hint"), keyboard_type=ft.KeyboardType.NUMBER, border_color=ft.Colors.OUTLINE)
        self.location_group = ft.RadioGroup(
            content=ft.Row([
                ft.Radio(value="outdoor", label=self.t("pools.location.outdoor")),
                ft.Radio(value="indoor", label=self.t("pools.location.indoor")),
            ])
        )
        self.equip_ionizer = ft.Checkbox(label=self.t("pools.equipment.ionizer"))
        self.equip_heater = ft.Checkbox(label=self.t("pools.equipment.heater"))
        self.equip_ozone = ft.Checkbox(label=self.t("pools.equipment.ozone"))
        self.equip_chlorinator = ft.Checkbox(label=self.t("pools.equipment.chlorinator"))
        
        # Dialog for delete confirmation
        self.confirm_dialog = ft.AlertDialog(
            modal=True,
            title=ft.Text(self.t("pools.delete")),
            content=ft.Text(self.t("pools.delete_confirm")),
            actions=[
                ft.TextButton(self.t("pools.cancel"), on_click=self._close_dialog),
                ft.TextButton(self.t("pools.delete"), on_click=self._confirm_delete, style=ft.ButtonStyle(color=ft.Colors.RED)),
            ],
            actions_alignment=ft.MainAxisAlignment.END,
        )
        self.pool_to_delete = None

        self.refresh_view()

    def refresh_view(self):
        # We need to add dialog to page overlay if not present
        try:
            if self.page and self.confirm_dialog not in self.page.overlay:
                self.page.overlay.append(self.confirm_dialog)
        except RuntimeError:
            pass

        if self.current_view == "list":
            self.content = self._build_list_view()
        else:
            self.content = self._build_form_view()
        
        try:
            self.update()
        except RuntimeError:
            pass

        try:
            self.update()
        except RuntimeError:
            pass

    def did_mount(self):
        """Called when control is added to page."""
        # Trigger background sync
        # We can't await here easily without freezing UI or run_task
        # Flet 0.21+ has self.page.run_task(self._sync_data)
        # But to be safe with older versions or simple runs:
        import asyncio
        # We can try to use asyncio.create_task if loop is running
        try:
            loop = asyncio.get_running_loop()
            loop.create_task(self._sync_data())
        except RuntimeError:
            pass

    async def _sync_data(self):
        await PoolService.sync_pools(self.user_id)
        # Refresh view after sync
        self.refresh_view()

    def _build_list_view(self):
        pools = PoolService.get_pools(self.user_id)
        
        cards = []
        for pool in pools:
            cards.append(self._create_pool_card(pool))

        if not cards:
            content = ft.Column(
                [
                    ft.Icon(ft.Icons.POOL, size=64, color=ft.Colors.GREY_400),
                    ft.Text(self.t("pools.no_pools"), color=ft.Colors.GREY_600),
                ],
                alignment=ft.MainAxisAlignment.CENTER,
                horizontal_alignment=ft.CrossAxisAlignment.CENTER,
            )
        else:
            content = ft.ListView(controls=cards, spacing=10, expand=True)

        return ft.Stack(
            controls=[
                ft.Column(
                    controls=[
                        ft.Text(
                            self.t("pools.manage"), 
                            size=16, 
                            color="onSurfaceVariant" # Theme aware color
                        ),
                        ft.Container(height=20),
                        ft.Container(content=content, expand=True),
                    ],
                    expand=True,
                ),
                ft.FloatingActionButton(
                    icon=ft.Icons.ADD,
                    on_click=self._on_add_click,
                    right=20,
                    bottom=20,
                )
            ],
            expand=True,
        )

    def _create_pool_card(self, pool):
        tags = []
        equipment = pool.get("equipment", [])
        
        # Helper for tags
        def create_tag(text):
            return ft.Container(
                content=ft.Text(text, size=12, color="onSurfaceVariant"),
                bgcolor="surfaceVariant",
                padding=5, 
                border_radius=5
            )

        if "heater" in equipment and equipment["heater"]:
            tags.append(create_tag(self.t("pools.equipment.heater")))
        if "ionizer" in equipment and equipment["ionizer"]:
            tags.append(create_tag(self.t("pools.equipment.ionizer")))
        if "ozone" in equipment and equipment["ozone"]:
            tags.append(create_tag(self.t("pools.equipment.ozone")))
        if "chlorinator" in equipment and equipment["chlorinator"]:
            tags.append(create_tag(self.t("pools.equipment.chlorinator")))
        
        unit_str = "mts³" if self.unit_system == "metric" else "ft³"

        return ft.Container(
            content=ft.Row(
                controls=[
                    ft.Icon(ft.Icons.POOL, color=ft.Colors.PRIMARY, size=40),
                    ft.Container(width=10),
                    ft.Column(
                        controls=[
                            ft.Text(pool.get("name", ""), weight=ft.FontWeight.BOLD, size=18, color=ft.Colors.ON_SURFACE),
                            ft.Row([
                                ft.Icon(ft.Icons.WB_SUNNY_OUTLINED if pool.get("location") == "outdoor" else ft.Icons.HOME, size=16, color="onSurfaceVariant"),
                                ft.Text(self.t(f"pools.location.{pool.get('location', 'outdoor')}"), size=14, color="onSurfaceVariant"),
                                ft.Text("•", color="onSurfaceVariant"),
                                ft.Text(f"{pool.get('volume', 0)} {unit_str}", size=14, color="onSurfaceVariant"),
                            ]),
                            ft.Row(tags, wrap=True) if tags else ft.Container(),
                        ],
                        expand=True,
                    ),
                    ft.Column([
                        ft.IconButton(ft.Icons.EDIT, on_click=lambda e, p=pool: self._on_edit_click(p), icon_color="onSurfaceVariant"),
                        ft.IconButton(ft.Icons.DELETE, on_click=lambda e, p=pool: self._on_delete_click(p), icon_color=ft.Colors.ERROR),
                    ])
                ],
                alignment=ft.MainAxisAlignment.START,
                vertical_alignment=ft.CrossAxisAlignment.START,
            ),
            padding=20,
            # Use theme-aware colors
            bgcolor="secondaryContainer",
            border_radius=10,
        )

    def _build_form_view(self):
        unit_str = "mts" if self.unit_system == "metric" else "ft" # Update label if unit changes? 
        # Actually fields are created in __init__, so they won't update automatically if we just change self.unit_system unless we recreate them or update label.
        # But for 'main.py' logic, the view is recreated when navigated to or updated?
        # In main.py `view_fn(navigate, t)` creates a NEW container. So __init__ is called.
        
        return ft.Column(
            controls=[
                ft.Row(
                    controls=[
                        ft.Text(
                            self.t("pools.edit") if self.editing_pool else self.t("pools.add"),
                            size=24,
                            weight=ft.FontWeight.BOLD,
                            color=ft.Colors.ON_SURFACE
                        ),
                        ft.IconButton(ft.Icons.POOL, on_click=lambda e: self._back_to_list(), icon_color=ft.Colors.ON_SURFACE),
                    ],
                    alignment=ft.MainAxisAlignment.SPACE_BETWEEN
                ),
                ft.Text(self.t("pools.details"), color="onSurfaceVariant"),
                ft.Container(height=20),
                ft.Container(
                    content=ft.Column([
                        ft.Text(self.t("pools.name"), weight=ft.FontWeight.BOLD, color=ft.Colors.ON_SURFACE),
                        self.name_field,
                        ft.Container(height=10),
                        ft.Text(f"{self.t('pools.volume')} ({unit_str}³)", weight=ft.FontWeight.BOLD, color=ft.Colors.ON_SURFACE),
                        ft.Row([
                            ft.Container(self.volume_field, expand=True),
                            ft.TextButton(
                                content=self.t("pools.calculator_btn"),
                                icon=ft.Icons.CALCULATE,
                                style=ft.ButtonStyle(
                                    padding=10,
                                ),
                                on_click=lambda _: self.navigate("cubic_calculator")
                            )
                        ]),
                        ft.Container(height=10),
                        ft.Text(self.t("pools.location"), weight=ft.FontWeight.BOLD, color=ft.Colors.ON_SURFACE),
                        self.location_group,
                        ft.Divider(),
                        ft.Text(self.t("pools.equipment"), weight=ft.FontWeight.BOLD, color=ft.Colors.ON_SURFACE),
                        self.equip_ionizer,
                        self.equip_heater,
                        self.equip_ozone,
                        self.equip_chlorinator,
                    ]),
                    padding=20,
                    bgcolor="surfaceVariant", # Theme aware background
                    border_radius=10,
                ),
                ft.Container(height=20),
                ft.FilledButton(
                    content=ft.Text(self.t("pools.save")),
                    on_click=self._save_pool,
                    style=ft.ButtonStyle(shape=ft.RoundedRectangleBorder(radius=20)),
                ),
            ],
            scroll=ft.ScrollMode.AUTO,
            expand=True,
        )

    def _on_add_click(self, e):
        self.editing_pool = None
        self.name_field.value = ""
        self.volume_field.value = ""
        self.location_group.value = "outdoor"
        self.equip_ionizer.value = False
        self.equip_heater.value = False
        self.equip_ozone.value = False
        self.equip_chlorinator.value = False
        
        self.current_view = "form"
        self.refresh_view()

    def _on_edit_click(self, pool):
        # Deep copy to avoid reference issues if mutable
        self.editing_pool = copy.deepcopy(pool) 
        
        self.name_field.value = str(pool.get("name", ""))
        self.volume_field.value = str(pool.get("volume", ""))
        self.location_group.value = pool.get("location", "outdoor")
        
        equipment = pool.get("equipment", {})
        self.equip_ionizer.value = bool(equipment.get("ionizer", False))
        self.equip_heater.value = bool(equipment.get("heater", False))
        self.equip_ozone.value = bool(equipment.get("ozone", False))
        self.equip_chlorinator.value = bool(equipment.get("chlorinator", False))
        
        self.current_view = "form"
        self.refresh_view()

    def _on_delete_click(self, pool):
        if self.page and self.confirm_dialog not in self.page.overlay:
            self.page.overlay.append(self.confirm_dialog)
        self.pool_to_delete = pool
        self.confirm_dialog.open = True
        self.page.update()

    async def _confirm_delete(self, e):
        if self.pool_to_delete:
            pool_id = self.pool_to_delete.get("id")
            await PoolService.delete_pool(self.user_id, pool_id)
            self.pool_to_delete = None
            
        self.confirm_dialog.open = False
        self.page.update()
        self.refresh_view()

    def _close_dialog(self, e):
        self.confirm_dialog.open = False
        self.page.update()

    def _back_to_list(self):
        self.current_view = "list"
        self.refresh_view()

    async def _save_pool(self, e):
        if not self.name_field.value:
            self.name_field.error_text = self.t("pools.error_name_required")
            self.name_field.update()
            return

        try:
            volume = float(self.volume_field.value)
        except ValueError:
            self.volume_field.error_text = self.t("pools.error_volume_invalid")
            self.volume_field.update()
            return

        pool_data = {
            "name": self.name_field.value,
            "volume": volume,
            "location": self.location_group.value,
            "equipment": {
                "ionizer": self.equip_ionizer.value,
                "heater": self.equip_heater.value,
                "ozone": self.equip_ozone.value,
                "chlorinator": self.equip_chlorinator.value,
            }
        }

        if self.editing_pool:
            pool_data["id"] = self.editing_pool["id"]
            # Preserve creation data if any
            if "created_at" in self.editing_pool:
                pool_data["created_at"] = self.editing_pool["created_at"]

        success = await PoolService.save_pool(self.user_id, pool_data)
        if success:
            self.current_view = "list"
            self.refresh_view()
        else:
            # Show error snackbar?
            pass

def pools_view(navigate, t, unit_system):
    return ft.Container(
        content=ft.Column(
            controls=[
                ft.Text(t("pools.title"), size=24, weight=ft.FontWeight.BOLD, color=ft.Colors.ON_SURFACE),
                ft.Container(
                    content=PoolsContent(navigate, t, unit_system),
                    expand=True
                )
            ],
        ),
        padding=20,
        expand=True,
    )
