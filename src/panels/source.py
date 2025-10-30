from src import *

from src.controls.etc import *
from src.controls.item import *
from src.controls.toolbar import *
from src.controls.dialogs import *

class SourcesPanel(ft.Container):
	def __init__(self, page:any):
		self._page = page

		self.loading_items = False
		self.loading_thread = None
		self.source_seed = ""
		self.last_source_mod = None

		self.sources : dict = self._page.app.DATA['sources']
		self.registry = self._page.app.DATA['registry']

		self.loaded_items = []

		self.target : KeyValuePair = None
		self.target_label = ft.Text(
			"",
			width = 350,
			text_align=ft.TextAlign.CENTER,
			style = ft.TextStyle(
				size = 17,
				weight = ft.FontWeight.BOLD
			)
		)

		# Source Selector
		self.source_select = ft.Dropdown(
			on_change = self.load_items,
			enable_search = False,
			dense=True,
			width = 235,
			filled=True,
			fill_color=BGCOLOR,
			text_style = ft.TextStyle(
				size = 17,
				weight = ft.FontWeight.BOLD
			),
			label = "Source",
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
			label = "Search Files",
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
			visible = False,
			height = float("inf"),
			width = 350,
			bgcolor = ft.Colors.SECONDARY_CONTAINER,
			padding = 5,
			content = ft.Container(
				expand = True,
				border_radius = 6,
				bgcolor = BGCOLOR,
				clip_behavior=ft.ClipBehavior.NONE,
				content = ft.Column(
					expand = True,
					spacing = 5,
					controls = [
						ft.Row(
							controls = [
								ft.IconButton(ft.Icons.ARROW_FORWARD_IOS_ROUNDED, on_click=self.close, icon_size=15, tooltip=Tooltip("Close Sources")),
								ft.IconButton(ft.Icons.REFRESH_ROUNDED, on_click=self.refresh, tooltip=Tooltip("Refresh Current Source")),
								self.source_select,
							]
						),
						self.search_field,
						self.target_label,
						self.items_container
					]
				)
			)
		)

	def refresh(self, event = None):
		self.load_items(override=True)

	def check_source_for_diff(self) -> bool:
		"""Creates / Compares a Mash of hex-a-digested strings for every file name, size and source folders length; as a seed. It Checks it against the last seed to see if there are differences"""
		path = self.get_source_selection()[3]
		files = os.listdir(path)
		seed = "".join( [ utility.hex_digest(f"{file}{os.path.getsize( os.path.join(path, file))}") for file in files ] ) + utility.hex_digest( str(len(files)) )
		if seed == self.source_seed: 
			return False

		self.source_seed = seed
		return True

	def set_target_data(self):
		if self.target:
			item = self.target.instance.source_item.id.lower().replace(" ","_")

			#If Parent is a Dictionary or List
			if isinstance(self.target.pair_parent, KeyValuePair) and (self.target.pair_parent.type == dict or self.target.pair_parent.type == list):
				if self.target.pair_parent.type == dict: #parent dict
					self.target_label.value = f"Target : {item} > {self.target.pair_parent.key_field.value}.{self.target.key_field.value}"
				else: #parent list
					index = self.target.parent.controls.index(self.target)
					self.target_label.value = f"Target : {item} > list.{index}"
			else:
				self.target_label.value = f"Target : {item} > {self.target.key_field.value}"
			self.target_label.update()
		else:
			self.target_label.value = f""
			self.target_label.update()

	def toggle(self, event = None, target:KeyValuePair = None):
		if self.visible and target and not target == self.target:
			self.target = target
			self._page.app.notify(f"Source Target Changed to {self.target.instance.source_item.id} > {self.target.key_field.value}", 3000)
			self.set_target_data()
			return

		if self.visible:
			self.close(event)
		else:
			self.open(event, target = target)

	def open(self, event = None, target:KeyValuePair = None):
		self.visible = True
		self.target = target
		self.set_target_data()

		self.clear()
		self.load()
		
		self.update()

	def close(self, event = None):
		self.visible = False
		self.target = None
		self.clear()
		self.update()

	def set_source_data(self, key, mod, value):
		for opt in self.group_select.options:
			if opt.data[0] == key and opt.data[1] == mod:
				opt.data[2] = value
				break

	def get_source_data(self, key, mod):
		for opt in self.group_select.options:
			if opt.data[0] == key and opt.data[1] == mod:
				return opt.data[2]

	def get_source_selection(self) -> list[str, dict, str]:
		for opt in self.source_select.options:
			if opt.data[4] == self.source_select.value:
				return opt.data

	def clear(self):
		self.source_seed = ""
		self.source_select.options.clear()
		self.items.controls.clear()

	def __set_target_value(self, orig_path:str, mod:str, data:dict, mod_result:str):
		self.target.value_field.value = mod_result
		self.target.instance.mark_as_edited()

		self._page.LOGGER.info(f"SourcePanel is setting a source <lk:{self.target.key}:{str(self.target.type)}> as <{mod_result}:expected> from modification <type:{mod}> w/ applied <data:{data}>")

		#How Data Is Applied after process_mods handles it
		match mod:
			case "path_splice" | "random" | "none":
				if orig_path.split(".")[-1] in utility.SUPPORTED_IMAGE_EXTS:
					self.target.new_registry("paths.preview", orig_path)
					self.target.new_registry("paths.preview:expected", mod_result)
					if self.target.value_field.data:
						self.target.replace_preview_image(orig_path)
					else:
						self.target.set_preview_image(orig_path)
		
		self.target.value_field.update()
		self.target.on_string_changed_value(ctrl = self.target.value_field)

	def process_mods(self, path:str, mod:str, data:any) -> any:
		match mod:
			case "path_splice":
				full = Path(path.replace("\\", "/"))
				partial = Path(data.replace("\\", "/"))

				# Get how many parts partial has
				partial_depth = len(partial.parts)

				# Keep everything in full *after* the same depth as partial
				tail = full.parts[partial_depth:]
				tail_path = Path(*tail) if tail else Path()

				# Join and return normalized path
				result = Path(partial) / tail_path
				return str(result)
				
			case _: return path

	def load_items_thread(self, event = None):
		self.items.controls.clear()

		data = self.get_source_selection()
		
		self.file_grid = ft.GridView(
			expand = True,
			visible = True,
			runs_count = 3,
			spacing = 2
		)

		file_items = [self.file_grid]
		self.items.controls = file_items
		self.items.update()

		files = os.listdir(data[3])
		self._page.app.LOGGER.info(f"SourcePanel is loading a fresh source ({data[3]})")
		mod = data[1]

		#Item Modification
		if mod == "random":
			random.shuffle(files)
			files = [files[0]]

		#Create Item Controls
		for file in files:
			parts = file.split(".")
			ext = parts[-1]
			path = os.path.join( data[3], file )
			if ext in utility.SUPPORTED_IMAGE_EXTS:
				self.file_grid.controls.append(
					ft.FloatingActionButton(
						bgcolor=ft.Colors.TRANSPARENT,
						disabled_elevation=True,
						elevation=0,
						content = ft.Image(
							src_base64 = utility.load_and_pre_process_image( path, max_size=(200, 200)),
							fit = ft.ImageFit.SCALE_DOWN,
							anti_alias = True,
							filter_quality = ft.FilterQuality.HIGH
						),
						tooltip=Tooltip(f"{parts[0]} : {ext.upper()}", wait_duration=1000),
						data = [file, path], 
						on_click = lambda _, p=path, m=data[1], d=data[2]: self.__set_target_value(p, m, d, self.process_mods(p, m, d) )
					)
				)
			else:
				self.file_grid.controls.append(
					ft.FloatingActionButton(
						bgcolor=ft.Colors.TRANSPARENT,
						disabled_elevation=True,
						elevation=0,
						content = ft.Icon(FILE_ICONS.get(f".{ext}", ft.Icons.FILE_PRESENT_ROUNDED), size=50,),
						tooltip=Tooltip(f"{parts[0]} : {ext}", wait_duration=1000),
						data = [file, path],
						on_click= lambda _, p=path, m=data[1], d=data[2]: self.__set_target_value( self.process_mods(p, m, d) )
					)
				)

			self.file_grid.update()

		if mod == "random":
			self.file_grid.controls.append(
				ft.FloatingActionButton(
					bgcolor=ft.Colors.TRANSPARENT,
					disabled_elevation=True,
					elevation=0,
					content = ft.Icon(ft.Icons.AUTORENEW_ROUNDED, size=50),
					tooltip=Tooltip(f"Randomize Again..."),
					data = "RANDOMIZER",
					on_click= lambda _, o=True: self.load_items(override=o)
				)
			)

		self.items.update()

		gc.collect()

		self.loaded_items = self.file_grid.controls

		self.last_item_count = len(self.file_grid.controls)
		self.loading_items = False
		self.loading_thread = None
		self.source_select.disabled = False
		self.source_select.update()

	def search_load_items(self, items):
		self.file_grid.controls = items
		self.file_grid.update()

	def load_items(self, event = None, override:bool = False):
		if self.loading_items: return

		source = self.get_source_selection()
		if source[1] == "random" or not self.last_source_mod == source[1]: override = True
		if not self.check_source_for_diff() and not override: return

		self.last_source_mod = source[1]

		self.loading_items = True
		self.source_select.disabled = True
		self.source_select.update()
		self.loading_thread = Thread(target = self.load_items_thread)
		self.loading_thread.start()

	def load(self, event = None):
		self.sources = self._page.app.DATA["sources"]

		if not len(self.sources) > 0:
			self._page.app.notify("No Sources. Add a Source in Sources in the Toolbar", 3500)
			return
		
		for path in self.sources:
			if not (path and os.path.exists(path)): continue
			key = os.path.basename(path).split(".")[0]
			data = self.sources[path]
			for mod in data:
				name = f"{utility.readable_key(key)} : { utility.readable_key( mod ) }"
				
				#Dont Allow Re-adding Groups
				if name in [opt.key for opt in self.source_select.options]: continue
				
				self.source_select.options.append(
					ft.DropdownOption(
						key = name,
						data = [key, mod, data[mod], path, name],
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
		
		self.source_select.value = self.source_select.options[0].key
		self.source_select.update()

		if len(self.items.controls) <= 0: self.load_items()

	## SEARCHING
	def get_items(self):
		return self.loaded_items

	def __search(self, event=None):

		minCatch = 0.75
		source = self.get_source_selection()
		if not source: return
		if source[1] == "random": return

		query = (self.search_field.value or "").strip()
		if not query:
			self.search_load_items( self.loaded_items )
			return
		
		items = self.loaded_items
		names = [item.data[0].split(".")[0] for item in items]
		queried = []

		# *query* - Match items that have query somewhere inside of text
		if query.startswith("*") and query.endswith("*") and len(query) > 2:
			term = query.strip("*")
			queried = [
				item for item in items
				if term.lower() in item.data[0].split(".")[0]
			]

		# * prefix - Match items that END with the text (case-insensitive)
		elif query.startswith("*") and len(query) > 1:
			suffix = query[1:].lower()
			queried = [
				item for item in items
				if item.data[0].split(".")[0].lower().endswith(suffix)
			]
		# * suffix - Match items that START with the text (case-insensitive)
		elif query.endswith("*") and len(query) > 1:
			prefix = query[:-1].lower()
			queried = [
				item for item in items
				if item.data[0].split(".")[0].lower().startswith(prefix)
			]

		#Fuzzy Search Fallback
		else:
			results = process.extract(
				query,
				names,
				scorer=fuzz.WRatio,
				limit=None
			)

			for item in items:
				for name, score, _ in results:
					if item.data[0].split(".")[0] == name and score >= minCatch * 100:  # 0–100 scale
						queried.append(item)
						break

		queried = sorted(queried, key=lambda x: x.data[0], reverse=False)

		# Update
		self.search_load_items( queried )
