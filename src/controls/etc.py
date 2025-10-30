from src import *

class Tooltip(ft.Tooltip):
	def __init__(self, content:str, image:ft.DecorationImage = None, wait_duration:int = 0):
		"""Custom Tooltip"""
		super().__init__(
			message = content if not image else "",
			image = image,
			bgcolor = BGCOLOR,
			border_radius=4,
			text_style = ft.TextStyle(
				size = 16.5,
				weight = ft.FontWeight.W_400
			),
			wait_duration = wait_duration,
			shadow = [
				ft.BoxShadow(2, 2, "black", ft.Offset(2, 2), ft.ShadowBlurStyle.NORMAL)
			]
		)


class DialogTemplate(ft.AlertDialog):
	def __init__(self, title, content, width=650, height=350, on_dismiss:any = None, modal:bool = False):
		content.width = width
		content.height = height
		super().__init__(
			content = content,
			content_padding = ft.padding.all(5),
			shape = ft.RoundedRectangleBorder(radius = 6),
			title = ft.Row(
				alignment=ft.MainAxisAlignment.CENTER,
				width = width,
				controls = [
					ft.Text(
						value = title,
						text_align=ft.TextAlign.CENTER,
						style = ft.TextStyle(
							size = 22,
							weight = ft.FontWeight.W_500
						)
					) if title else ft.Row(visible=False)
				]
			),
			title_padding = ft.padding.all(5),
			actions_padding = ft.padding.all(0),
			action_button_padding = ft.padding.all(0),
			on_dismiss = on_dismiss,
			modal=modal
		)
