from src import *

from src.controls.etc import *
from src.controls.item import *
from src.controls.toolbar import *
from src.controls.dialogs import *

class EditorInstanceTab(ft.FloatingActionButton):
	def __init__(self, panel, uuid_key, key:str, switch_instance):
		self.__name = utility.readable_key(key)
		self.on_remove_func = None
		self.panel = panel
		self.instance_key = uuid_key
		self.instance : EditorInstance = None
		self.swticher = switch_instance

		self.name = ft.Text(
			value = self.__name,
			text_align=ft.TextAlign.CENTER,
			overflow = ft.TextOverflow.CLIP,
			style = ft.TextStyle(
				size = 17,
				weight = ft.FontWeight.BOLD
			)
		)

		self.__save_marker = ft.IconButton(
			icon = ft.Icons.SAVE_AS_ROUNDED,
			right = 0,
			top = -4,
			icon_color = "white",
			visible=False,
			data = False,
			on_click=None
		)

		self.split_btn = ft.FloatingActionButton(
			width = 30,
			height = 35,
			bgcolor = ft.Colors.TRANSPARENT,
			shape = ft.RoundedRectangleBorder(radius = 100),
			disabled_elevation=True,
			elevation = 0,
			content = ft.Icon(
				ft.Icons.VERTICAL_SPLIT_ROUNDED,
				color = "white",
			),
			tooltip = Tooltip(f"Split '{self.__name}'"),
			on_click = self.split
		)
		self.close_btn = ft.FloatingActionButton(
			width = 30,
			height = 35,
			bgcolor = ft.Colors.TRANSPARENT,
			shape = ft.RoundedRectangleBorder(radius = 100),
			disabled_elevation=True,
			elevation = 0,
			content = ft.Icon(
				ft.Icons.CLOSE,
				color = "white",
			),
			tooltip = Tooltip(f"Close '{self.__name}'"),
			on_click = self.remove_self
		)

		self.buttons = ft.Row(
			visible=False,
			alignment = ft.MainAxisAlignment.END,
			right = 5,
			top = -10,
			height = 45,
			controls = [
				self.split_btn,
				self.close_btn
			]
		)

		super().__init__(
			disabled_elevation=True,
			shape = ft.RoundedRectangleBorder(radius = 2),
			bgcolor = ft.Colors.with_opacity(0.2, ft.Colors.BROWN_800),
			height = 45,
			width = 175,
			elevation=0,
			hover_elevation=0,
			focus_elevation=0,
			clip_behavior = ft.ClipBehavior.ANTI_ALIAS_WITH_SAVE_LAYER,
			tooltip=Tooltip(self.__name),
			content = ft.GestureDetector(
				on_enter = self.show,
				on_exit = self.hide,
				height = 45,
				content = ft.SafeArea(
					minimum_padding = 8,
					height = 45,
					expand=False,
					content = ft.Stack(
						expand = True,
						height = 45,
						controls = [
							self.__save_marker,
							ft.Row(
								expand = True,
								height = 45,
								controls = [
									self.name,
									ft.Text(
										"...",
										overflow = ft.TextOverflow.CLIP,
										style = ft.TextStyle(
											size = 17,
											weight = ft.FontWeight.BOLD
										)
									)
								]
							),
							self.buttons
						]
					)
				)
			),
			on_click = self.switch
		)

	def get_instance(self):
		return self.panel.instance_storage[self.instance_key]

	def update_name(self, name):
		self.name.value = name
		self.tooltip = Tooltip(name)
		self.split_btn.tooltip = Tooltip(f"Split '{name}'")
		self.close_btn.tooltip = Tooltip(f"Close '{name}'")
		self.update()

	def mark_as_saved(self):
		self.__save_marker.visible = False
		self.__save_marker.data = False
		try:
			self.__save_marker.update()
		except: pass

	def mark_as_edited(self):
		self.__save_marker.visible = True
		self.__save_marker.data = True
		try:
			self.__save_marker.update()
		except: pass

	def switch(self, event):
		self.swticher(self.get_instance())

	def split(self, event):
		self.swticher(self.get_instance(), True)

	def select(self):
		self.bgcolor = ft.Colors.BROWN_500
		self.update()

	def select_as_split_tab(self):
		self.bgcolor = ft.Colors.BROWN_500
		self.update()

	def un_select(self):
		self.bgcolor = ft.Colors.with_opacity(0.2, ft.Colors.BROWN_800)
		self.update()

	def show(self, event = None):
		self.buttons.visible = True
		self.__save_marker.visible = False
		try:
			self.__save_marker.update()
			self.buttons.update()
		except: pass

	def hide(self, event = None):
		self.buttons.visible = False
		self.__save_marker.visible = self.__save_marker.data
		try:
			self.__save_marker.update()
			self.buttons.update()
		except: pass

	def remove_self(self, event = None):
		self.parent.controls.remove(self)
		self.parent.update()
		if self.on_remove_func:
			self.on_remove_func(self.get_instance())

class EditorInstance(ft.Container):
	def __init__(self, panel, page, source_item, instance_tab):
		self.panel = panel
		self._page = page
		self.instance_tab = instance_tab
		self.source_item : KeyedItem = source_item
		self.was_saved = True

		self.was_compacted = False

		self.pairs = ft.Column(
			expand = True, 
			spacing = 4, 
			alignment=ft.MainAxisAlignment.SPACE_EVENLY,
			horizontal_alignment =  ft.CrossAxisAlignment.STRETCH,
		)

		super().__init__(
			expand = True,
			border_radius = 6,
			bgcolor = BGCOLOR2,
			padding = 5,
			content = ft.Column(
				width = float("inf"),
				spacing = 10,
				controls = [
					ft.Row(
						width = float("inf"),
						alignment = ft.MainAxisAlignment.END,
						controls = [
							ft.FloatingActionButton(
								disabled_elevation=True,
								width = 35, height = 35,
								shape = ft.RoundedRectangleBorder(radius = 2),
								content = ft.Icon(ft.Icons.SAVE_ALT),
								tooltip = Tooltip("Save"),
								on_click = self.save
							),
							ft.FloatingActionButton(
								disabled_elevation=True,
								width = 35, height = 35,
								shape = ft.RoundedRectangleBorder(radius = 2),
								content = ft.Icon(ft.Icons.ADD),
								tooltip = Tooltip("Add New Pair"),
								on_click = self.add_pair
							),
							ft.FloatingActionButton(
								disabled_elevation=True,
								width = 35, height = 35,
								shape = ft.RoundedRectangleBorder(radius = 2),
								content = ft.Icon(ft.Icons.DATA_OBJECT_ROUNDED),
								tooltip = Tooltip("Copy Item Data"),
								on_click = self.copy_tree
							)
						]
					),
					ft.ListView(
						expand=True,
						controls = [self.pairs]
					)
				]
			)
		)

	def copy_tree(self, event = None):
		if not len(self.pairs.controls) > 0: return
		template = {}
		for ctrl in self.pairs.controls:
			key, value = ctrl.get_pair()
			if key in [UUID_KEY]: continue
			template[key] = value
		self._page.app.copy_to_clipboard(json.dumps(template))
		self._page.app.notify("Item Copied!")

	def add_pair(self, event = None):
		if not self.source_item: return
		self.pairs.controls.append(
			KeyValuePair(self._page.app, self, self.source_item, f"New Key {len(self.pairs.controls)}", "New Value String")
		)
		self.pairs.update()

	def mark_as_edited(self):
		self.was_saved = False
		self.instance_tab.mark_as_edited()

	def save(self, event = None):
		"""Saves Editor Pairs Data Back Into Its Group | Does not save anything to a file!"""
		if self.source_item:
			#Reconstruct
			template = {}
			for ctrl in self.pairs.controls:
				ctrl : KeyValuePair = ctrl
				key, value = ctrl.get_pair()
				template[key] = value
				ctrl.update_registry()

			if event:
				print(f"{event}|{template}")

			#Find Item & Replace with New Template
			group_items : list = self._page.navigator.get_group_data(self.source_item.group)
			to_change = None
			for itm in group_items:
				if itm[UUID_KEY] == self.source_item.data[UUID_KEY]:
					to_change = itm
					break

			template[UUID_KEY] = to_change[UUID_KEY]
			group_items.remove(to_change)
			group_items.append(template)

			#Update Current KeyedItem Instance
			self.source_item.data = template
			key = None
			for test_key in ORDERED_KEYS_FOR_ITEM_NAME:
				if template.get(test_key):
					key = template[test_key]
					break
			name = utility.readable_key(str(key))
			self.source_item.id = name
			try: #Updating while not on screen causes problems | 
				self.source_item.name.value = name
				self.source_item.update()
			except: pass

			try:
				self.instance_tab.update_name(name)
			except: pass

			for ctrl in self.pairs.controls:
				ctrl.update_registry()
			
			#Save to Group
			self._page.navigator.set_group_data(self.source_item.group, group_items)

			#Logging
			if not self.was_saved:
				self.was_saved = True
				self.instance_tab.mark_as_saved()
				self._page.app.notify(f"{self.source_item.name.value} Object Saved")
				self._page.app.LOGGER.info(f"EditorInstance <{self.source_item.group}:{self.source_item.name.value}> object was saved.")
			else:
				self._page.app.LOGGER.info(f"EditorInstance <{self.source_item.group}:{self.source_item.name.value}> object was saved ? it was already saved.")

			gc.collect() #memory cleanup

	def load(self):
		self.pairs.controls.clear()
		pairs = []
		for key, value in self.source_item.data.items():
			if key == UUID_KEY: 
				continue
			pairs.append( KeyValuePair(self._page.app, self, self.source_item, key, value) )
		
		self.pairs.controls = pairs
		self.pairs.update()
		self._page.app.LOGGER.info(f"EditorInstance <{self.source_item.group}:{self.source_item.name.value}> object was loaded/reloaded")

class EditorPanel(ft.Container):
	def __init__(self, page:any):
		self._page = page

		self.instance_storage = {}

		self.instance_tabs = ft.Row(
			expand = True,
			wrap=True,
			spacing = 2,
			run_spacing=2,
			controls = []
		)

		self.instances = ft.Row(
			expand = True,
			spacing = 5,
		)

		self.holding = []

		super().__init__(
			border_radius = 6,
			expand = True,
			bgcolor = ft.Colors.SECONDARY_CONTAINER,
			padding = 0,
			content = ft.Column(
				expand = True,
				spacing = 0,
				controls = [
					ft.Container(
						border_radius = 6,
						width =float("inf"),
						padding = 4,
						bgcolor=BGCOLOR2,
						content = ft.Row(
							expand = True,
							controls = [
								self.instance_tabs,
								ft.Row(
									alignment=ft.MainAxisAlignment.END,
									controls = [
										ft.IconButton(
											icon = ft.Icons.ADD,
											icon_size=30,
											tooltip = Tooltip("Add New Item"),
											on_click = self.add_new_item
										)
									]
								)
							]
						)
					),
					ft.Container(
						border_radius = 6,
						expand = True,
						bgcolor = ft.Colors.SECONDARY_CONTAINER,
						padding = 5,
						content = self.instances
					)
				]
			)
		)

	def get_instances(self):
		return self.instances.controls

	def save(self, event = None):
		self._page.app.LOGGER.info(f"Editor is attempting to save all instances ...")
		for instance in self.instance_storage.values():
			instance.save()

	def add_new_item(self, event = None):
		group = self._page.navigator.get_group_selection()
		if not group:
			return

		items = self._page.navigator.get_group_data( group[0] )

		template = self._page.navigator.create_group_template( group[0] )

		i = len(items)
		for default, value in self._page.app.DATA["defaults"].items():
			if template.get(default):
				try:
					template[default] = value.strip().format(i=i)
				except:
					template[default] = value.strip()

		id = str(uuid.uuid4()) 

		template[UUID_KEY] = id
		
		items.append( template )
		self._page.navigator.set_group_data( group[0], items )
		self._page.navigator.load_items(force_refresh = True)

		keyeditem : KeyedItem = None
		for item in self._page.navigator.items.controls:
			if item.data[UUID_KEY] == id:
				keyeditem = item
				break
		
		self._page.app.LOGGER.info(f"Editor added new item <{keyeditem.group}:{keyeditem.name.value}>")
		self.new_instance( keyeditem, as_split=True )

	def remove_instance(self, instance:EditorInstance):
		self._page.app.LOGGER.info(f"Editor is removing EditorInstance <{instance.source_item.group}:{instance.source_item.name.value}>")
		instance.save()
		if instance in self.instances.controls:
			self.instances.controls.remove(instance)
			self.instances.update()

		gc.collect()

	def __on_side_choice_made(self, choice:str):
		new_instance = self.holding[0]

		match choice:
			case "left":
				left_instance = self.instances.controls[0]
				self.instances.controls.remove(left_instance)
				self.instances.controls.insert(0, new_instance)

			case "right":
				right_instance = self.instances.controls[1]
				self.instances.controls.remove(right_instance)
				self.instances.controls.append(new_instance)

			case "fill":
				self.instances.controls.clear()
				self.instances.controls = [new_instance]

		self._page.app.dialog(close = True)

		self.instances.update()
		new_instance.load()
		self.holding.clear()

		for instance_tab in self.instance_tabs.controls:
			instance_tab.un_select()
			if instance_tab.get_instance() in self.instances.controls:
				if len(self.instances.controls) < 2:
					instance_tab.select()
				else:
					instance_tab.select_as_split_tab()

	def switch_instance(self, new_instance:EditorInstance = None, as_split:bool = False):
		if new_instance in self.instances.controls: return

		for instance in self.instances.controls:
			instance.save()

		if not as_split:
			self.instances.controls.clear()
			self.instances.controls = [new_instance]
		else:
			if len(self.instances.controls) < 2:
				self.instances.controls.append( new_instance )
			else:
				self.holding.append(new_instance)
				dialog = SideChoiceDialog(self.__on_side_choice_made)
				self._page.app.dialog(dialog)
				return
		
		self.instances.update()
		new_instance.load()

		for instance_tab in self.instance_tabs.controls:
			instance_tab.un_select()
			if instance_tab.get_instance() in self.instances.controls:
				if len(self.instances.controls) < 2:
					instance_tab.select()
				else:
					instance_tab.select_as_split_tab()

	def new_instance(self, item:KeyedItem, as_split:bool = False):
		"""Loads Editor Controls"""
		gc.collect()

		if self._page.source.visible:
			self._page.source.close()

		#If Opened Already
		for instance_tab in self.instance_tabs.controls:
			if instance_tab.get_instance().source_item.name.value == item.name.value:
				self.switch_instance(instance_tab.get_instance(), as_split)
				return
		
		#Create Instance Tab
		tab = EditorInstanceTab(self, item.data[UUID_KEY], item.name.value, self.switch_instance)

		#Create Instance
		instance = EditorInstance(self, self._page, item, tab)

		tab.on_remove_func = self.remove_instance

		self.instance_storage[item.data[UUID_KEY]] = instance

		self.instance_tabs.controls.append(tab)
		self.instance_tabs.update()

		self.switch_instance(instance, as_split = not len(self.instances.controls) < 2 or as_split)

