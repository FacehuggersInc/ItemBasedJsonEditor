from src import *

from src.controls.etc import *
from src.controls.item import *
from src.controls.toolbar import *
from src.controls.dialogs import *

## PANELS
class NavigatorPanel(ft.Container):
	def __init__(self, page:any):
		self._page = page

		# Data Reference
		self.source : dict = None

		# Group Selector
		self.group_select = ft.Dropdown(
			on_change = self.load_items,
			enable_search = False,
			dense=True,
			width = 285,
			filled=True,
			fill_color=BGCOLOR,
			text_style = ft.TextStyle(
				size = 17,
				weight = ft.FontWeight.BOLD
			),
			hint_text = "Select Group",
			hint_style = ft.TextStyle(
				size = 16,
				weight = ft.FontWeight.BOLD
			),
			label = "Group",
			label_style=ft.TextStyle(
				size = 16,
				weight = ft.FontWeight.BOLD
			),
			
		)

		# Search
		self.search_field = ft.TextField(
			value = "",
			border_width = 2,
			border_color = ft.Colors.TRANSPARENT,
			border_radius= 6,
			bgcolor = BGCOLOR,
			label = "Search Items",
			on_change = self.__search,
			on_submit=self.__search,
			label_style = ft.TextStyle(
				size = 16,
				weight = ft.FontWeight.BOLD
			),
			text_style = ft.TextStyle(
				size = 17,
				weight = ft.FontWeight.W_400
			),
		)

		# Items List
		self.items = ft.ListView(
			expand = True,
			spacing = 2,
			height = float("inf")
		)

		self.items_container = ft.Container(
			expand=True,
			height = float("inf"),
			border_radius = 6,
			bgcolor = BGCOLOR,
			padding = 4,
			content = self.items
		)
		
		super().__init__(
			border_radius = 6,
			height = float("inf"),
			width = 350,
			bgcolor = ft.Colors.SECONDARY_CONTAINER,
			padding = 2,
			content = ft.Container(
				expand = True,
				border_radius = 6,
				bgcolor=BGCOLOR,
				clip_behavior=ft.ClipBehavior.NONE,
				content = ft.Column(
					expand = True,
					spacing = 5,
					controls = [
						ft.Row(
							width = float("inf"),
							spacing = 2,
							controls = [
								self.group_select,
								ft.IconButton(
									ft.Icons.EDIT_NOTE_ROUNDED, 
									on_click = self.__edit_group_item,
									icon_size = 32,
									tooltip=Tooltip("Add or Modify Item Template")
								),
							]
						),
						self.search_field,
						self.items_container
					]
				)
			)
		)


	## CORE
	def toggle(self, event = None):
		if self.visible:
			self.close(event)
		else:
			self.open(event)

	def open(self, event = None):
		self.visible = True
		self.update()

	def close(self, event = None):
		self.visible = False
		self.update()


	## SEARCHING
	def __search(self, event=None):
		minCatch = 0.75
		group = self.get_group_selection()
		if not group: return

		query = (self.search_field.value or "").strip()
		if not query:
			self.load_items()
			return

		names = []
		for item in group[1]:
			for test_key in ORDERED_KEYS_FOR_ITEM_NAME:
				if item.get(test_key):
					names.append(utility.readable_key(item.get(test_key)))
					break

		queried = []

		# *query* - Match items that have query somewhere inside of text
		if query.startswith("*") and query.endswith("*") and len(query) > 2:
			term = query.strip("*")
			queried = [
				item for item in self.get_items()
				if term.lower() in item.name.value.lower()
			]

		# * prefix - Match items that END with the text (case-insensitive)
		elif query.startswith("*") and len(query) > 1:
			suffix = query[1:].lower()
			queried = [
				item for item in self.get_items()
				if item.name.value.lower().endswith(suffix)
			]
		# * suffix - Match items that START with the text (case-insensitive)
		elif query.endswith("*") and len(query) > 1:
			prefix = query[:-1].lower()
			queried = [
				item for item in self.get_items()
				if item.name.value.lower().startswith(prefix)
			]

		#Fuzzy Search Fallback
		else:
			results = process.extract(
				query,
				names,
				scorer=fuzz.WRatio,
				limit=None
			)

			for item in self.get_items():
				for name, score, _ in results:
					if item.name.value == name and score >= minCatch * 100:  # 0–100 scale
						queried.append(item)
						break

		queried = sorted(queried, key=lambda x: x.name.value, reverse=False)

		# Update
		self.items.controls = queried
		self.items.update()



	## ITEMS
	def __edit_group_item(self, event=None):
		"""Group Add Blank Template"""
		if not self.group_select.value: return
		dialog = ItemAdjustmentDialog(self, self._page)
		self._page.app.dialog( dialog)

	def __remove_item(self, group_key, item):
		items = self.get_group_data(group_key)
		if not items: return

		to_remove = None
		for itm in items:
			if itm[UUID_KEY] == item[UUID_KEY]:
				to_remove = itm
				break
		
		if to_remove:
			items.remove( to_remove )
			self.set_group_data( group_key, items )

	def __load_preview(self, item:KeyedItem, as_split:bool = False):
		self._page.editor.new_instance(item, as_split)

	def __copy_self(self, keyed_item:KeyedItem):
		data : dict = copy.deepcopy( keyed_item.data )
		data[UUID_KEY] = str(uuid.uuid4())

		key = None
		found_key = None
		for test_key in ORDERED_KEYS_FOR_ITEM_NAME:
			if data.get(test_key):
				key = data[test_key]
				found_key = test_key
				break

		data[found_key] = f"{key}_{utility.random_string(3, False, False, True)}"

		group = self.get_group_selection()
		group[1].append( data )
		self.set_group_data( group[0], group[1] )

		self.items.controls.append(
			self.create_keyed_item(
				keyed_item.group,
				data
			)
		)
		self.items.controls = sorted(self.items.controls, key=lambda x: x.name.value, reverse=False)
		self.items.update()



	##GROUPING
	def create_group_template(self, group_key:str) -> dict:
		items = self.get_group_data(group_key)
		item = items[0]

		template = {}
		for key, value in item.items():
			new_value = None
			if type(value) == dict:
				new_value = {}
			elif type(value) == float:
				new_value = 0.0
			elif type(value) == int:
				new_value = 0
			elif type(value) == str:
				new_value = " "

			template[key] = new_value

		return template

	def set_group_data(self, key, value):
		for opt in self.group_select.options:
			if opt.data[0] == key:
				opt.data[1] = value
				break

	def get_group_data(self, key):
		for opt in self.group_select.options:
			if opt.data[0] == key:
				return opt.data[1]

	def get_group_selection(self) -> list[str, dict, str]:
		for opt in self.group_select.options:
			if opt.data[3] == self.group_select.value:
				return opt.data



	## LOADING
	def get_names(self):
		group = self.get_group_selection()

		names = []
		for item in group[1]:
			for test_key in ORDERED_KEYS_FOR_ITEM_NAME:
				if item.get(test_key):
					names.append(utility.readable_key(item.get(test_key)))
					break
		
		return names
	
	def create_keyed_item(self, group_key:str, item:dict):
		key = None
		for test_key in ORDERED_KEYS_FOR_ITEM_NAME:
			if item.get(test_key):
				key = item[test_key]
				break

		return KeyedItem(
			group_key,
			key,
			item,
			self.__load_preview,
			self.__copy_self,
			self.__remove_item
		)

	def get_items(self):
		group = self.get_group_selection()
		
		items = []
		for item in group[1]:
			items.append( self.create_keyed_item(group[0], item) )

		return items
	
	def get_groups(self) -> list[tuple[str, list, str, str]]:
		return [opt.data for opt in self.group_select.options]

	def load_items(self, event:ft.ControlEvent = None, force_refresh:bool = False):
		self.items.controls.clear()
		items = self.get_items()
		self.items.controls = sorted(items, key=lambda x: x.name.value, reverse=False)
		self.items.update()
		if force_refresh:
			for instance in self._page.editor.instances.controls:
				instance.load()

	def clear(self):
		self.source = None
		self.items.controls.clear()
		self.group_select.options.clear()
		self.update()

	def load(self, fid:str, source_data:dict):
		if not (isinstance(source_data, dict) and source_data): return

		self.source = source_data
		for key in self.source:
			name = f"{utility.readable_key(key)} : {os.path.basename(fid)}"
			data = self.source[key]

			#Dont Allow Re-adding Groups
			if name in [opt.key for opt in self.group_select.options]: continue

			#Create Internal Tracking IDs
			for item in data:
				item[UUID_KEY] = str(uuid.uuid4())
			
			self.group_select.options.append(
				ft.DropdownOption(
					key = name,
					data = [key, data, fid, name],
					content = ft.Text(
						value = name,
						width = 350,
						style = ft.TextStyle(
							size = 16,
							weight = ft.FontWeight.BOLD
						)
					)
				)
			)
		
		self.group_select.value = self.group_select.options[0].key
		self.group_select.update()

		if len(self.items.controls) <= 0: self.load_items()
