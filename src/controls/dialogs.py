from src import *

from src.controls.etc import DialogTemplate, Tooltip

class SourceItem(ft.Container):
	def __init__(self, dialog, path:str = None, mod:str = None, data:any = None):
		self.dialog = dialog

		self.mod = mod if mod else "none"

		self.source_field = ft.TextField(
			expand = True,
			value="" if not path else path,
			text_style = VALUE_TEXT_STYLE,
			label="Source (Folder)",
			label_style=LABEL_TEXT_STYLE,
			dense=True,
			border_radius=6,
			border_width=0,
			bgcolor=BGCOLOR
		)

		self.browse_btn = ft.IconButton(icon=ft.Icons.CREATE_NEW_FOLDER_ROUNDED, tooltip=Tooltip("Browse"), on_click=self.load_file)

		self.open_folder_btn = ft.IconButton(icon=ft.Icons.FOLDER_ROUNDED, tooltip=Tooltip("Open Folder"), on_click=self.open_folder)

		self.options = [
			ft.DropdownOption(
				key = "No Modification",
				data = "none",
				content = ft.Text(
					"No Modification",
					style = ft.TextStyle(
						size = 16,
						weight = ft.FontWeight.W_500
					)
				)
			),
			ft.DropdownOption(
				key = "Path Splice",
				data = "path_splice",
				content = ft.Text(
					"Path Splice",
					style = ft.TextStyle(
						size = 16,
						weight = ft.FontWeight.W_500
					)
				)
			),
			ft.DropdownOption(
				key = "Random",
				data = "random",
				content = ft.Text(
					"Random",
					style = ft.TextStyle(
						size = 16,
						weight = ft.FontWeight.W_500
					)
				)
			)
		]

		self.modifier_selector = ft.Dropdown(
			width=250,
			padding = 0,
			filled=True,
			fill_color = BGCOLOR,
			dense=True,
			value=self.options[0].key,
			text_style = ft.TextStyle(
				size = 18,
				weight = ft.FontWeight.W_500
			),
			border_radius=4, border_color=ft.Colors.TRANSPARENT, border_width=0,
			options=self.options,
			on_change=self.__on_type_change
		)

		self.topr = ft.Row(
			expand = True,
			controls = [
				ft.IconButton(icon=ft.Icons.CLOSE, tooltip=Tooltip("Delete Source"), on_click=self.__remove_self),
				self.browse_btn,
				self.modifier_selector,
				self.source_field,
				self.open_folder_btn,
			]
		)
		self.modifiers = ft.Row(expand = True)

		super().__init__(
			bgcolor=BGCOLOR2,
			border_radius=6,
			padding=5,
			data = data,
			content = ft.Column(
				expand = True,
				controls = [
					self.topr, 
					self.modifiers
				]
			)
		)

		#Auto Fill / Configure when given data
		if path and mod:
			#Set Path Field
			self.source_field.value = path
			try:
				self.source_field.update()
			except:pass

			#Set Correct Dropdown Option
			for opt in self.options:
				if self.mod == opt.data:
					self.modifier_selector.value = opt.key
					break
			
			#Apply Extra Controls for Mod
			self.__on_type_change()

			#Apply Data to Controls
			match self.mod:
				case "path_splice":
					self.modifiers.controls[0].value = data
					try:
						self.modifiers.controls[0].update()
					except: pass
				case _: pass
		else:
			self.__on_type_change() #called for initial selection

	def open_folder(self, event = None):
		path = self.source_field.value
		if os.path.exists(path):
			if os.path.isfile(path):
				os.startfile( os.path.dirname(path) )
			else:
				os.startfile( path )

	def load_file_result(self, e: ft.FilePickerResultEvent = None):
		"""A Callback / Call to load data into Navigator and set loaded_path"""
		if (e and not e.path): return
		self.source_field.value = e.path.strip()
		self.source_field.update()

	def load_file(self, event = None):
		"""Opens File Explorer, Calls load_file_result when done"""
		self.dialog._page.app.open_explorer(
			"Choose a Folder ...",
			"C:\\",
			self.load_file_result,
			ExplorerTypes.FOLDER
		)

	def get_modifier_selection(self):
		for opt in self.options:
			if opt.key == self.modifier_selector.value:
				return opt.data

	def __on_type_change(self, event = None):
		"""Dropdown on_change call for adding controls to give extra data to Modification"""
		type = self.get_modifier_selection()
		self.modifiers.controls.clear()
		match type:
			case "path_splice":
				self.mod = "path_splice"
				self.modifiers.controls.append(
					ft.TextField(
						expand = True,
						value="",
						text_style = VALUE_TEXT_STYLE,
						label="Partial Path to Splice",
						label_style=LABEL_TEXT_STYLE,
						dense=True,
						border_radius=6,
						border_width=0,
						bgcolor=BGCOLOR
					)
				)
			case "random":
				self.mod = "random"

			case "none":
				self.mod = "none"

		try:
			self.modifiers.update()
		except: pass

	def __remove_self(self, event = None):
		self.parent.controls.remove(self)
		try:
			self.parent.update()
		except: pass

class SourcesDialog(DialogTemplate):
	def __init__(self, page):
		self._page = page

		self.raw_sources = self._page.app.DATA['sources']

		self.header = ft.Row(
			width = float("inf"),
			controls = [
				ft.Text(
					value = "Sources",
					style = ft.TextStyle(
						size = 22,
						weight = ft.FontWeight.W_500
					)
				),
				ft.Row(
					expand = True,
					alignment = ft.MainAxisAlignment.END,
					controls = [
						ft.FloatingActionButton(
							disabled_elevation=True,
							width = 35, height = 35,
							shape = ft.RoundedRectangleBorder(radius=2),
							content = ft.Icon(ft.Icons.ADD),
							tooltip=Tooltip("Add Source"),
							on_click = self.add_source
						)
					]
				)
			]
		)

		self.sources = ft.ListView(
			expand = True,
			spacing = 5
		)

		for path, item in self.raw_sources.items():
			print(f"Loaded SourceItem: {path, item}")
			for type in item:
				self.sources.controls.append(
					SourceItem(self, path, type, item[type])
				)

		content = ft.Column(
			expand = True,
			controls = [
				self.header,
				ft.Container(
					expand = True,
					bgcolor = BGCOLOR2,
					border_radius=4,
					content = self.sources
				)
			]
		)

		super().__init__(
			"", 
			ft.SafeArea(
				minimum_padding = 10,
				content = content
			), 
			1000, 
			650, 
			None,
			modal=False
		)

	def add_source(self, event = None):
		self.sources.controls.append(
			SourceItem(self)
		)
		self.sources.update()

class SideChoiceDialog(DialogTemplate):
	def __init__(self, on_choice_made:any = None):
		side_choice_row = ft.Row(
			alignment=ft.MainAxisAlignment.CENTER,
			spacing = 5,
			controls = [
				ft.FloatingActionButton(
					width = 150,
					height = 300,
					bgcolor = ft.Colors.BROWN,
					content = ft.Text(
						"LEFT",
						style = ft.TextStyle(
							size = 20,
							weight = ft.FontWeight.BOLD
						)
					),
					on_click = lambda _, c="left": on_choice_made(c)
				),
				ft.FloatingActionButton(
					width = 150,
					height = 300,
					bgcolor = ft.Colors.BROWN,
					content = ft.Text(
						"RIGHT",
						style = ft.TextStyle(
							size = 20,
							weight = ft.FontWeight.BOLD
						)
					),
					on_click = lambda _, c="right": on_choice_made(c)
				)
			]
		)

		content = ft.Container(
			expand = True,
			bgcolor = BGCOLOR2,
			border_radius=4,
			content = ft.Column(
				horizontal_alignment=ft.CrossAxisAlignment.CENTER,
				alignment=ft.MainAxisAlignment.CENTER,
				spacing = 5,
				controls = [
					side_choice_row,
					ft.FloatingActionButton(
						width = 300,
						height = 75,
						bgcolor = ft.Colors.BROWN,
						content = ft.Text(
							"FILL BOTH SIDES",
							style = ft.TextStyle(
								size = 20,
								weight = ft.FontWeight.BOLD
							)
						),
						on_click = lambda _, c="fill": on_choice_made(c)
					)
				]
			)
		)

		super().__init__(
			"Where should it Go?", 
			ft.SafeArea(
				minimum_padding = 10,
				content = content
			), 
			500, 
			450, 
			None,
			modal=False
		)

class AdjustmentKeyValueItem(ft.Row):
	def __init__(self, dialog, key, value, tags:list=[]):
		"""This lives in the Adjustment Dialog not the Editor Environment"""
		self.id = key
		self.value = value
		self.dialog = dialog
		self.tags = tags

		self.key_field = ft.TextField(
			value = key,
			text_style = ft.TextStyle(
				size = 18,
				weight = ft.FontWeight.W_500
			),
			dense = True,
			width = 250,
			border_radius = 2, border_width=2,
			border_color = "green" if "created" in tags else None,
			bgcolor = BGCOLOR
		)

		self.value_field = ft.TextField(
			value = str(value),
			text_style = ft.TextStyle(
				size = 18,
				weight = ft.FontWeight.W_500
			),
			dense = True,
			width = 250,
			border_radius = 2, border_width=2,
			border_color = "green" if "created" in tags else None,
			bgcolor = BGCOLOR
		)

		super().__init__(
			height = 45,
			alignment=ft.MainAxisAlignment.CENTER,
			vertical_alignment=ft.CrossAxisAlignment.CENTER,
			controls = [
				ft.Row(
					controls = [
						ft.FloatingActionButton(
							width = 35,
							height = 35,
							shape = ft.RoundedRectangleBorder(radius = 2),
							disabled_elevation=True,
							content = ft.Icon(
								ft.Icons.CLOSE
							),
							on_click = self.remove_self
						)
					]
				),
				self.key_field,
				ft.Text(
					":",
					style = ft.TextStyle(
						size = 20,
						weight = ft.FontWeight.W_500
					)
				),
				self.value_field
			]
		)

	def get_type_string(self) -> str:
		if type(self.value) == dict: return "Dictionary"
		if type(self.value) == list: return "Array"

	def remove_self(self, event):
		self.dialog.changes.append((self.key_field.value, self.value_field.value))
		self.dialog.update_changes()
		self.parent.controls.remove(self)
		self.parent.update()

class ItemAdjustmentDialog(DialogTemplate):
	def __init__(self, panel, page):
		self.panel = panel
		self._page = page

		self.changes = []

		## BUILD
		self.template_items = ft.ListView(
			height = float("inf"),
			spacing = 5,
			auto_scroll=True,
			controls = []
		)

		self.group = self.panel.get_group_selection()
		self.template = self.panel.create_group_template( self.group[0] )
		items = self.template.items()
		for key, item in items:
			if key in [UUID_KEY]: continue
			i = len(items)
			for default, value in self._page.app.DATA["defaults"].items():
				if key == default:
					try:
						item = value.strip().format(i=i)
					except:
						item = value.strip()
			self.template_items.controls.append( AdjustmentKeyValueItem(self, key, item, ["original"]) )

		self.template_items.height = min(sum( [c.height if c.height else 1 for c in self.template_items.controls] ) + 50, 450)

		self.added_changes = ft.TextSpan(
			text = "",
			style = ft.TextStyle(
				size = 16,
				color = "green",
				weight=ft.FontWeight.BOLD
			),
			data = 0
		)
		self.removed_changes = ft.TextSpan(
			text = "",
			style = ft.TextStyle(
				size = 16,
				color = "red",
				weight=ft.FontWeight.BOLD
			),
			data = 0
		)

		self.changes_label = ft.Text(
			width = 200,
			text_align=ft.TextAlign.CENTER,
			spans = [
				self.added_changes,
				ft.TextSpan(
					text = "   :   ",
					style = ft.TextStyle(
						size = 16,
						color = "white"
					)
				),
				self.removed_changes
			]
		)

		container = ft.Container(
			expand = True,
			bgcolor=BGCOLOR2,
			padding = 10,
			content = ft.Column(
				expand=True,
				controls = [

					#Dialog Header
					ft.Row(
						width = float("inf"),
						alignment=ft.MainAxisAlignment.CENTER,
						vertical_alignment=ft.CrossAxisAlignment.CENTER,
						controls = [
							ft.Column( #Max Width Row | Should center with parent row
								width = 575,
								spacing = 2,
								controls = [
									ft.Row(
										vertical_alignment=ft.CrossAxisAlignment.CENTER,
										controls = [
											ft.Text(
												value = "Template Pairs",
												style = ft.TextStyle(
													size = 18,
													weight = ft.FontWeight.BOLD
												)
											),
											ft.Row(
												expand = True,
												alignment=ft.MainAxisAlignment.END,
												controls = [
													ft.FloatingActionButton(
														width = 35, height = 35,
														shape = ft.RoundedRectangleBorder(radius = 2),
														disabled_elevation=True,
														content = ft.Icon(ft.Icons.ADD),
														tooltip = Tooltip("Add Pair"),
														on_click = self.__add_adjust_item
													),
													ft.FloatingActionButton(
														disabled_elevation=True,
														width = 35, height = 35,
														shape = ft.RoundedRectangleBorder(radius = 2),
														content = ft.Icon(ft.Icons.DATA_OBJECT_ROUNDED),
														tooltip = Tooltip("Copy Blank Item Structure"),
														on_click = self.__copy_tree
													)
												]
											)
										]
									),
									ft.Text(
										value = "Quick adjust the Structure of the Item. Use { } to create a Dictionary OR [ ] to create a List",
										style = ft.TextStyle(
											size = 15,
											weight = ft.FontWeight.NORMAL,
											italic=True
										)
									),
									ft.Row(height = 5) #SPACER
								]
							)
						]
					),

					#Items
					self.template_items,

					ft.Row(
						expand = True,
						alignment=ft.MainAxisAlignment.CENTER,
						vertical_alignment=ft.CrossAxisAlignment.END,
						controls = [
							self.changes_label
						]
					),

					ft.Row(
						expand = True,
						alignment=ft.MainAxisAlignment.CENTER,
						vertical_alignment=ft.CrossAxisAlignment.END,
						controls = [
							ft.FloatingActionButton(
								width = 200,
								height = 55,
								shape = ft.RoundedRectangleBorder(radius = 4),
								bgcolor = ft.Colors.RED,
								content = ft.Row(
									expand = True,
									alignment=ft.MainAxisAlignment.CENTER,
									controls=[
										ft.Icon(ft.Icons.SETTINGS_SUGGEST_ROUNDED),
										ft.Text(
											value = "Adjust all Items\n to Match Template",
											text_align=ft.TextAlign.CENTER,
											style = ft.TextStyle(
												size = 17,
												weight = ft.FontWeight.W_600
											)
										)
									]
								),
								on_click = self.__adjust_all_dialog
							),
							ft.FloatingActionButton(
								width = 200,
								height = 55,
								shape = ft.RoundedRectangleBorder(radius = 4),
								bgcolor = ft.Colors.INVERSE_PRIMARY,
								content = ft.Row(
									expand = True,
									alignment=ft.MainAxisAlignment.CENTER,
									controls=[
										ft.Icon(ft.Icons.SETTINGS_SUGGEST_ROUNDED),
										ft.Text(
											value = "Add New Pairs\nto All Items",
											text_align=ft.TextAlign.CENTER,
											style = ft.TextStyle(
												size = 17,
												weight = ft.FontWeight.W_600
											)
										)
									]
								),
								on_click = self.__apply_to_all
							),
							ft.FloatingActionButton(
								width = 200,
								height = 55,
								shape = ft.RoundedRectangleBorder(radius = 4),
								bgcolor = ft.Colors.INVERSE_PRIMARY,
								content = ft.Row(
									expand = True,
									alignment=ft.MainAxisAlignment.CENTER,
									controls=[
										ft.Icon(ft.Icons.ADD),
										ft.Text(
											value = "Add New Item\nw/ this Template",
											text_align=ft.TextAlign.CENTER,
											style = ft.TextStyle(
												size = 17,
												weight = ft.FontWeight.W_600
											)
										)
									]
								),
								on_click = self.__add_new_item
							)
						]
					)
				]
			)
		)

		super().__init__( 
			f"Adjust / Add '{self.panel.group_select.value.split(":")[0].strip()}' Item",
			container,
			width = 650,
			height = 700
		)

	def update_changes(self):
		self.added_changes.data = sum([1 for ctrl in self.template_items.controls if type(ctrl) == AdjustmentKeyValueItem and "created" in ctrl.tags])
		self.added_changes.text = f"+ {self.added_changes.data}"
		self.removed_changes.data = sum([ 1 for change in self.changes if type(change) == tuple])
		self.removed_changes.text = f"- {self.removed_changes.data}"
		self.changes_label.update()

	def __copy_tree(self, event = None):
		copy = self.template
		del copy[UUID_KEY]
		self._page.app.copy_to_clipboard(json.dumps(copy))
		self._page.app.notify("Blank Item Copied!")

	def __add_adjust_item(self, event = None):
		item = AdjustmentKeyValueItem(self, f"New Key {len(self.template_items.controls)}", "New Value", ["created"])

		self.template_items.controls.append( item )
		self.template_items.height = min(sum( [c.height if c.height else 1 for c in self.template_items.controls] ) + 50, 450)
		self.template_items.update()

		self.changes.append(item)
		self.update_changes()

	def __add_new_item(self, event = None):
		items = self.panel.get_group_data( self.group[0] )

		final_template = {}
		for ctrl in self.template_items.controls:
			val = ctrl.value_field.value.strip()
			if val == "{}" or val.startswith("{") and val.endswith("}"):
				final_template[ctrl.key_field.value] = utility.uplift_dict_values(json.loads(val))
			elif val == "[]" or val.startswith("[") and val.endswith("]"):
				final_template[ctrl.key_field.value] = json.loads(val)
			else:
				final_template[ctrl.key_field.value] = val

		i = len(items)
		for default, value in self._page.app.DATA["defaults"].items():
			if final_template.get(default) and (final_template.get(default) == "" or final_template.get(default) == None):
				try:
					final_template[default] = value.strip().format(i=i)
				except:
					final_template[default] = value.strip()

		id = str(uuid.uuid4())

		final_template[UUID_KEY] = id
		
		items.append( final_template )
		self.panel.set_group_data( self.group[0], items )
		self._page.app.dialog(close = True)
		self.panel.load_items()

		keyeditem = None
		for item in self._page.navigator.items.controls:
			if item.data[UUID_KEY] == id:
				keyeditem = item
				break
		
		self._page.app.LOGGER.info(f"AdjustmentDialog added new item <{keyeditem.group}:{keyeditem.name.value}>")
		self._page.editor.new_instance( keyeditem, as_split=True )

	def __apply_to_all(self, event = None):
		"""Applies Only New KeyValue Pairs to All Items"""
		items = self.panel.get_group_data( self.group[0] )

		final_template = {}
		for ctrl in self.template_items.controls:
			val = ctrl.value_field.value.strip()
			if val == "{}" or val.startswith("{") and val.endswith("}"):
				final_template[ctrl.key_field.value] = utility.uplift_dict_values(json.loads(val))

			elif val == "[]" or val.startswith("[") and val.endswith("]"):
				final_template[ctrl.key_field.value] = json.loads(val)
			else:
				final_template[ctrl.key_field.value] = val

		#Force Save Instances So they Keep Data and Still Get new Values
		for instance in self._page.editor.instances.controls:
			if not instance.was_saved:
				instance.save()

		#Apply Keys
		for item in items:
			if not item.keys() == final_template.keys():
				for key in final_template.keys():
					if not item.get(key):
						item[key] = final_template[key]

		self.panel.set_group_data( self.group[0], items )
		self._page.app.dialog(close = True)
		self.panel.load_items(force_refresh = True)

	def __adjust_all(self, event = None):
		"""Applies Only New KeyValue Pairs to All Items"""
		items = self.panel.get_group_data( self.group[0] )

		final_template = {}
		for ctrl in self.template_items.controls:
			val = ctrl.value_field.value.strip()
			if val == "{}" or val.startswith("{") and val.endswith("}"):
				final_template[ctrl.key_field.value] = utility.uplift_dict_values(json.loads(val))

			elif val == "[]" or val.startswith("[") and val.endswith("]"):
				final_template[ctrl.key_field.value] = json.loads(val)
			else:
				final_template[ctrl.key_field.value] = val

		#Force Save Instances So they Keep Data and Still Get new Values
		for instance in self._page.editor.instances.controls:
			if not instance.was_saved:
				instance.save()

		for item in items:
			#Apply Keys
			for key in final_template.keys():
				if not item.get(key):
					item[key] = final_template[key]

			#Remove Keys
			item_keys = list(item.keys())
			to_remove = [change[0] for change in self.changes if type(change) == tuple]
			for key in item_keys:
				if key in final_template.keys(): continue
				elif key in to_remove:
					del item[key]

		self.panel.set_group_data( self.group[0], items )
		self._page.app.dialog(close = True)
		self.panel.load_items(force_refresh = True)

	def __adjust_all_dialog(self, event = None):
		new_dialog = DialogTemplate(
			"Are you Sure?",
			height = 115,
			content = ft.Column(
				expand = True,
				controls = [
					ft.Text(
						"New KEYS will be added and KEYS missing from this template will be REMOVED from ALL items.",
						text_align=ft.TextAlign.CENTER,
						style=ft.TextStyle(
							size = 19,
							weight = ft.FontWeight.NORMAL
						)
					),
					ft.Row(
						expand= True,
						alignment=ft.MainAxisAlignment.CENTER,
						controls = [
							ft.FloatingActionButton(
								disabled_elevation=True,
								bgcolor = ft.Colors.GREY_900,
								shape = ft.RoundedRectangleBorder(radius = 4),
								width = 150,
								height = 45,
								content = ft.Text(
									"Cancel",
									style = ft.TextStyle(
										size = 18,
										weight = ft.FontWeight.BOLD
									)
								),
								on_click = lambda _, c=True: self._page.app.dialog(close = c)
							),
							ft.FloatingActionButton(
								disabled_elevation=True,
								bgcolor = ft.Colors.RED,
								shape = ft.RoundedRectangleBorder(radius = 4),
								width = 150,
								height = 45,
								content = ft.Text(
									"Adjust All Items",
									style = ft.TextStyle(
										size = 18,
										weight = ft.FontWeight.BOLD
									)
								),
								on_click = self.__adjust_all
							)
						]
					)
				]
			)
		)
		
		self._page.app.dialog(new_dialog)

class KeyValueEffectAllDialog(DialogTemplate):
	def __init__(self, opt1_add:any = None, opt2_remove:any = None):
		side_choice_row = ft.Row(
			alignment=ft.MainAxisAlignment.CENTER,
			spacing = 5,
			controls = [
				ft.FloatingActionButton(
					width = 200,
					height = 70,
					bgcolor = ft.Colors.GREEN,
					shape =ft.RoundedRectangleBorder(radius = 2),
					content = ft.SafeArea(
						minimum_padding = 5,
						content = ft.Row(
							expand = True,
							controls = [
								ft.Icon(ft.Icons.ADD),
								ft.Text(
									"Add To\nAll Items",
									style = ft.TextStyle(
										size = 20,
										weight = ft.FontWeight.BOLD
									)
								)
							]
						)
					),
					on_click = opt1_add
				),
				ft.FloatingActionButton(
					width = 200,
					height = 70,
					bgcolor = ft.Colors.RED,
					shape =ft.RoundedRectangleBorder(radius = 2),
					content = ft.SafeArea(
						minimum_padding = 5,
						content = ft.Row(
							expand = True,
							controls = [
								ft.Icon(ft.Icons.REMOVE),
								ft.Text(
									"Remove From\nAll Items",
									style = ft.TextStyle(
										size = 20,
										weight = ft.FontWeight.BOLD
									)
								)
							]
						)
					),
					on_click = opt2_remove
				),
			]
		)

		content = ft.Container(
			expand = True,
			bgcolor = BGCOLOR2,
			border_radius=4,
			content = ft.Column(
				horizontal_alignment=ft.CrossAxisAlignment.CENTER,
				alignment=ft.MainAxisAlignment.CENTER,
				spacing = 5,
				controls = [
					side_choice_row,
				]
			)
		)

		super().__init__(
			"Choose an Option", 
			ft.SafeArea(
				minimum_padding = 10,
				content = content
			), 
			500, 
			125, 
			None,
			modal=False
		)