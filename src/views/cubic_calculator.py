import math
import flet as ft

def cubic_calculator_view(t, current_unit):
    volume = 0.0
    
    # Controls
    shape_dropdown = ft.Dropdown(
        label=t("calculator.shape"),
        value="round",
        options=[
            ft.dropdown.Option("rectangle", t("calculator.shape.rectangle")),
            ft.dropdown.Option("round", t("calculator.shape.round")),
        ],
    )
    unit = "mts" if current_unit == "metric" else "ft"
    radius_field = ft.TextField(label=t("calculator.radius") + "(" + unit + ")", keyboard_type=ft.KeyboardType.NUMBER)
    width_field = ft.TextField(label=t("calculator.width") + "(" + unit + ")", keyboard_type=ft.KeyboardType.NUMBER, visible=False)
    length_field = ft.TextField(label=t("calculator.length") + "(" + unit + ")", keyboard_type=ft.KeyboardType.NUMBER, visible=False)
    depth_field = ft.TextField(label=t("calculator.depth") + "(" + unit + ")", keyboard_type=ft.KeyboardType.NUMBER)

    result_text = ft.Text("", size=16, weight=ft.FontWeight.BOLD)

    async def copy_to_clipboard(e):
        if volume > 0:
            await ft.Clipboard().set(f"{volume:.3f}")
            e.page.show_dialog(ft.SnackBar(t("calculator.copied")))

    
    def _on_shape_change(e: ft.ControlEvent):
        shape = e.control.value
        if shape == "round":
            radius_field.visible = True
            width_field.visible = False
            length_field.visible = False
        else:  # rectangle
            radius_field.visible = False
            width_field.visible = True
            length_field.visible = True
        
        radius_field.update()
        width_field.update()
        length_field.update()

    def _compute(e: ft.ControlEvent):
        nonlocal volume
        try:
            depth = float(depth_field.value)
            if shape_dropdown.value == "round":
                r = float(radius_field.value)
                volume = math.pi * (r ** 2) * depth
            else: # rectangle
                w = float(width_field.value)
                l = float(length_field.value)
                volume = l * w * depth
            result_text.value = f'{t("calculator.volume")}: {volume:.3f} {unit}³'
            copy_btn.visible = True
        except Exception:
            result_text.value = t("calculator.error_invalid_input")
            copy_btn.visible = False
        result_text.update()
        copy_btn.update()
    
    shape_dropdown.on_select = _on_shape_change

    compute_btn = ft.Button(content=t("calculator.compute"), on_click=_compute)
    copy_btn = ft.IconButton(icon=ft.Icons.CONTENT_COPY, on_click=copy_to_clipboard, visible=False)
    
    return ft.Container(
        content=ft.Column(
            controls=[
                ft.Text(t("settings.calculator"), size=24, weight=ft.FontWeight.BOLD),
                shape_dropdown,
                radius_field,
                width_field,
                length_field,
                depth_field,
                ft.Row(controls=[compute_btn], alignment=ft.MainAxisAlignment.START, spacing=16),
                ft.Row(controls=[result_text, copy_btn], alignment=ft.MainAxisAlignment.START, spacing=16),
            ],
            spacing=12,
        ),
        alignment=ft.Alignment.TOP_LEFT,
        padding=20,
        expand=True,
    )
