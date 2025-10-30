from src import *

class ToolbarItemBTN(ft.MenuItemButton):
	def __init__(self, name:str, icon:str, action:any):
		super().__init__(
			content=ft.Text(
				value = name,
				style = ft.TextStyle(
					size = 16,
					weight = ft.FontWeight.W_500
				)
			),
			style=ft.ButtonStyle(
				padding = 5,
				shape = ft.RoundedRectangleBorder(radius = 2)
			),
			leading=ft.Icon(icon),
			on_click=action,
		)

class ToolbarMenuBTN(ft.SubmenuButton):
	def __init__(self, name:str, items:list[ToolbarItemBTN], icon:str = ft.Icons.MENU_ROUNDED):
		super().__init__(
			leading=ft.Icon(icon),
			style=ft.ButtonStyle(
				padding = 5,
				shape = ft.RoundedRectangleBorder(radius = 2)
			),
			content = ft.Text(
				value = name,
				style = ft.TextStyle(
					size = 16,
					weight = ft.FontWeight.W_500
				)
			),
			controls = items
		)