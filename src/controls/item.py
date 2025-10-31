from src import *

from src.controls.etc import *
from src.controls.dialogs import KeyValueEffectAllDialog



class KeyValuePair(ft.Container):
	def __init__(self, app, instance, parent, key, value):
		self.app = app
		self.pair_parent : KeyedItem | KeyValuePair = parent
		self.instance = instance
		self.reference = None

		self.__loading_preview = False

		self.key_ = key
		self.value = value

		self.type = self.__resolve_type(value)
		self.type_history = {}

		# Layout containers
		self.compact = False
		self.fields = ft.Row(
			expand = True,
			spacing = 2
		)

		self.topr = ft.Row(
			expand = True,
			spacing = 2,
			alignment=ft.MainAxisAlignment.START, 
			vertical_alignment=ft.CrossAxisAlignment.START, 
			controls=[self.fields]
		)
		
		self.bottomr = ft.Row(
			expand = True,
			spacing = 2, 
			alignment=ft.MainAxisAlignment.START, 
			vertical_alignment=ft.CrossAxisAlignment.END, 
			visible=False
		)

		self.column = ft.Column(
			expand = True,
			spacing = 5, 
			controls=[self.topr, self.bottomr]
		)

		self.browse_button = None
		self.type_label = None

		super().__init__(
			border_radius = 6,
			bgcolor = BGCOLOR2,
			padding = 8,
			content = self.column
		)

		self.registry_visual_debounce = time.time()
		self.registry_visual_debounce_wait_time = 0.8
		self.__registry_visual_wait_thread : Thread = None

		self.decide_view() #self.reference created inside here

		



	## HELPERS
	def __resolve_type(self, value):
		if isinstance(value, dict):
			return dict
		if isinstance(value, list):
			return list
		if isinstance(value, bool):
			return bool
		if isinstance(value, int):
			return int
		if isinstance(value, float):
			return float
		if isinstance(value, str):
			return str
		if value == None:
			return None

		return str

	def remove_self(self, e=None):
		parent = self.parent
		if parent:
			self.remove_references()

			parent.controls.remove(self)
			parent.update()

			if self.pair_parent.type in (dict, list): #this is required for just dict and list pairs
				self.pair_parent.value = self.pair_parent.get_value() #update value
	
	def detect_primitive(self, value: str) -> tuple:
		"""
		Try to detect and convert a string to its corresponding primitive type.
		Returns (type_name, converted_value)
		Possible types: int, float, bool, None, str
		"""
		if not isinstance(value, str):
			return type(value).__name__, value

		# Strip whitespace
		v = value.strip().lower()

		# None / null
		if v in ("none", "null"):
			self.type = None
			return "none"

		# Boolean
		if v in ("true", "false"):
			self.type = bool
			return "bool"

		# Integer
		if v.isdigit() or (v.startswith('-') and v[1:].isdigit()):
			try:
				self.type = int
				return "int"
			except ValueError:
				pass

		# Float
		try:
			f = float(value)
			# Only treat as float if it has decimal or exponent
			if "." in value or "e" in value.lower():
				self.type = float
				return "float"
		except ValueError:
			pass
		
		# Fallback → string
		self.type = str
		return "str"

	def calc_width_via_text_len(self, text:str, min_length:int = 85, max_length:int = 250):
		return min(max_length, max(len(text) * 16, min_length))

	def remove_references(self):
		#Cleanup Old References
		if self.reference and self.app.DATA["registry"].get(self.reference):
			references : list[str] = list(self.app.DATA["registry"].keys())
			for key in references:
				id = key.rsplit("@", 1)
				if id[0] in self.reference and not key == self.reference:
					print(f"Cleaned Up Ref: {id[0]} : {id[1]}")
					del self.app.DATA["registry"][key]
			del self.app.DATA["registry"][self.reference]


	## CORE - HERE
	def remove_self_from_all(self, event = None):
		"""Applies Only New KeyValue Pairs to All Items"""
		group_key = self.instance.source_item.group
		items = self.app.PAGE.navigator.get_group_data( group_key )

		#Force Save Instances So they Keep Data and Still Get new Values
		for instance in self.app.PAGE.editor.instances.controls:
			if not instance.was_saved:
				instance.save()

		
		# In your add_self_to_all method:
		pair = self.get_pair()  # e.g., (0, "prompt1")

		# Build pydash path string by traversing upwards
		path_parts = []
		current = self

		while isinstance(current, KeyValuePair):
			current_pair = current.get_pair()
			key = current_pair[0]
			
			# Format based on type
			if isinstance(key, int):
				path_parts.append(f"[{key}]")
			else:
				path_parts.append(str(key))
			
			current = current.pair_parent

		# Reverse to get root-to-target order
		path_parts.reverse()

		# Build pydash path string
		pydash_path = ""
		for i, part in enumerate(path_parts[:-1]):  # Exclude the last part (that's target_key)
			if part.startswith("["):
				pydash_path += part
			else:
				if i > 0 and not path_parts[i-1].startswith("["):
					pydash_path += "."
				pydash_path += part

		# If path is empty (root level), just use the target key
		if not pydash_path:
			if isinstance(pair[0], int):
				pydash_path = f"[{pair[0]}]"
			else:
				pydash_path = str(pair[0])
		else:
			# Append target key
			if isinstance(pair[0], int):
				pydash_path += f"[{pair[0]}]"
			else:
				pydash_path += f".{pair[0]}"

		# Now apply to all items
		for item in items:
			try:
				pdash.unset(item, pydash_path)
			except Exception as e:
				self.app.LOGGER.error(f"Remove from all failed to occur on instance because {e}\n  :  {pair}\n  :  {pydash_path}\n  :  {path_parts}\n  :  {item}", True)

		self.app.PAGE.navigator.set_group_data( group_key, items )
		self.app.PAGE.navigator.load_items(force_refresh=True)
		self.app.dialog(close = True)

	def add_self_to_all(self, event = None):
		"""Applies Only New KeyValue Pairs to All Items"""
		group_key = self.instance.source_item.group
		items = self.app.PAGE.navigator.get_group_data( group_key )

		#Force Save Instances So they Keep Data and Still Get new Values
		for instance in self.app.PAGE.editor.instances.controls:
			if not instance.was_saved:
				instance.save()

		# In your add_self_to_all method:
		pair = self.get_pair()  # e.g., (0, "prompt1")

		# Build pydash path string by traversing upwards
		path_parts = []
		current = self

		while isinstance(current, KeyValuePair):
			current_pair = current.get_pair()
			key = current_pair[0]
			
			# Format based on type
			if isinstance(key, int):
				path_parts.append(f"[{key}]")
			else:
				path_parts.append(str(key))
			
			current = current.pair_parent

		# Reverse to get root-to-target order
		path_parts.reverse()

		# Build pydash path string
		pydash_path = ""
		for i, part in enumerate(path_parts[:-1]):  # Exclude the last part (that's target_key)
			if part.startswith("["):
				pydash_path += part
			else:
				if i > 0 and not path_parts[i-1].startswith("["):
					pydash_path += "."
				pydash_path += part

		# If path is empty (root level), just use the target key
		if not pydash_path:
			if isinstance(pair[0], int):
				pydash_path = f"[{pair[0]}]"
			else:
				pydash_path = str(pair[0])
		else:
			# Append target key
			if isinstance(pair[0], int):
				pydash_path += f"[{pair[0]}]"
			else:
				pydash_path += f".{pair[0]}"

		# Now apply to all items
		for item in items:
			try:
				pdash.set_(item, pydash_path, pair[1])
			except Exception as e:
				self.app.LOGGER.error(f"Apply to all failed to occur on instance because {e}\n  :  {pair}\n  :  {pydash_path}\n  :  {path_parts}\n  :  {item}", True)

		self.app.PAGE.navigator.set_group_data( group_key, items )
		self.app.PAGE.navigator.load_items(force_refresh=True)
		self.app.dialog(close = True)

	def open_effect_dialog(self, event = None):
		dialog = KeyValueEffectAllDialog(self.add_self_to_all, self.remove_self_from_all)
		self.app.dialog(dialog)

	def update_registry(self):
		"""Updates Registry with Current Data"""

		old_ref = self.reference
		ref_val = self.app.DATA["registry"].get(old_ref)
		if not ref_val == None:
			del self.app.DATA["registry"][old_ref]

		# Generate the new reference
		new_ref = self.create_reference()
		self.reference = new_ref

		#Cleanup Old References
		references : list[str] = list(self.app.DATA["registry"].keys())
		for key in references:
			id = key.rsplit("@", 1)
			if id[0] in self.reference and not key == self.reference:
				print(f"Cleaned Up Ref: {id[0]} : {id[1]}")
				del self.app.DATA["registry"][key]

		# Reassign the registry entry
		if ref_val:
			self.app.DATA["registry"][new_ref] = ref_val

		# Persist the changes
		self.check_registry_visuals()

	def new_registry_old(self, key_path, value):
		if self.reference not in self.app.DATA["registry"]:
			self.app.DATA["registry"][self.reference] = {}

		pointer = self.app.DATA["registry"][self.reference]
		keys = key_path.split(".")

		for key in keys[:-1]:
			if key not in pointer or not isinstance(pointer[key], dict):
				pointer[key] = {}
			pointer = pointer[key]

		# Set the final key
		pointer[keys[-1]] = value

	def new_registry(self, key_path, value):
		if not self.reference:
			# No valid reference yet — skip until created
			self.reference = self.create_reference()

		if self.reference not in self.app.DATA["registry"]:
			self.app.DATA["registry"][self.reference] = {}

		pointer = self.app.DATA["registry"][self.reference]
		keys = key_path.split(".")

		for key in keys[:-1]:
			if key not in pointer or not isinstance(pointer[key], dict):
				pointer[key] = {}
			pointer = pointer[key]

		pointer[keys[-1]] = value

	def create_reference(self) -> str:
		"""
		Build a unique, consistent identifier path by walking up through pair_parent chain.
		Each KeyValuePair contributes:
			key_field.value + HEX digest of its value_field.value
		The top-level KeyedItem contributes:
			group + id
		Example result:
			"weapons.swords[iron_sword@a1b2c3]"
		"""
		def slugify(text: str) -> str:
			"""Reverse of readable_key — makes safe lowercase slugs."""
			text = re.sub(r"[^\w]+", "_", text.strip().lower())
			return re.sub(r"_+", "_", text).strip("_")

		parts = []

		current = self
		while current:
			# If it's a KeyValuePair
			if isinstance(current, KeyValuePair):
				part = ""
				if hasattr(current, "key_field"):
					part = str(current.key_field.value).strip()

				if hasattr(current, "value_field"):
					value = str(current.value_field.value).strip()
					uuid_id = uuid.uuid5(NOT_A_SECRET, value)
					if part:
						part += f"@{str(uuid_id)}"
					else:
						part += str(uuid_id)

				if part == "" and current.type == list:
					part = "collection"

				if part == "":
					part = "item"

				parts.append(part)
				current = getattr(current, "pair_parent", None)

			# If we've reached the top-level KeyedItem
			elif isinstance(current, KeyedItem):
				if hasattr(current, "id") and hasattr(current, "group"):
					parts.append(f"{current.group.strip()}.{slugify(current.id.strip())}")
					break
			else:
				break

		# Combine parts in hierarchical order
		parts.reverse()
		return ".".join(parts)

	def get_registry_value(self, key_path, default=None):
		"""
		Retrieve a value from the registry using a dot-separated key path.
		Example:
			get_registry_value("settings.video.resolution")
		"""
		registry = self.app.DATA.get("registry", {})
		data = registry.get(self.reference, {})

		pointer = data
		for key in key_path.split("."):
			if isinstance(pointer, dict) and key in pointer:
				pointer = pointer[key]
			else:
				return default
		return pointer

	def on_string_changed_key(self, event = None):
		self.instance.mark_as_edited()
		self.key_ = self.key_field.value
		self.update_registry()
		if hasattr(self, "key_field"):
			self.key_field.width = self.calc_width_via_text_len(self.key_field.value)
			self.key_field.update()

	def on_string_changed_value(self, e: ft.ControlEvent = None, ctrl:ft.TextField = None):
		"""Autodetect Type on Text Change"""
		self.instance.mark_as_edited()
		print("\nVALUE CHANGED")

		control: ft.TextField = e.control if e else ctrl
		text = control.value.strip()

		is_dict = text.startswith("{") and text.endswith("}")
		is_list = text.startswith("[") and text.endswith("]")

		if not is_dict and not is_list:
			type_str = self.detect_primitive(text)
			if type_str == "str":
				is_path_like = utility.looks_like_path(text)
				print(f"IS PATH?: {is_path_like} : {text}")
				if is_path_like:
					self.value_field.label = f"Value : PATH"
					self.value_field.tooltip = Tooltip(text)
					self.add_preview_image()

					index = 0
					for i, ctrl in enumerate(self.topr.controls):
						if ctrl == self.source_btn:
							index = i - 1
							break
					
					self.topr.controls.insert(index, self.browse_button)
					self.topr.update()

				else:
					if self.browse_button in self.topr.controls:
						self.topr.controls.remove(self.browse_button)
						self.topr.update()

					self.remove_preview_image()
					self.value_field.tooltip = None
					body = utility.check_full_text(text)
					if body:
						self.value_field.label = f"Value : BODY (STR)"
						self.value_field.multiline = True
						self.value_field.max_lines = 25
					else:
						self.value_field.label = f"Value : {type_str.upper()}"
						self.value_field.multiline = False
						self.value_field.max_lines = 1
			else:
				if self.browse_button in self.topr.controls:
					self.topr.controls.remove(self.browse_button)
					self.topr.update()

				self.remove_preview_image()
				self.value_field.tooltip = None
				self.value_field.label = f"Value : {type_str.upper()}"

			self.update_registry()
			self.value_field.update()
		else:
			if self.browse_button in self.topr.controls:
				self.topr.controls.remove(self.browse_button)
				self.topr.update()

			#Change Type to Dict or List
			self.type_history[self.type] = text
			data = utility.loads_flexible(text)
			if is_dict:
				self.type = dict
			elif is_list:
				self.type = list
			
			if is_dict:
				data = utility.uplift_dict_values(data)

			self.value = data
			self.decide_view()

	def get_value(self) -> int | float | bool | str | dict | list | None:
		"""Recursively reconstructs the current Python value (dict, list, or primitive)."""
		
		if self.type in (int, float, str, bool):
			raw = self.value_field.value if hasattr(self, "value_field") else str(self.value)
			if self.type == int:
				try:
					return int(raw)
				except:
					return 0
			if self.type == float:
				try:
					return float(raw)
				except:
					return 0.0
			if self.type == bool:
				return raw.lower() in ("true")
			return raw
		
		elif self.type == dict:
			data = {}
			for child in self.child_container.controls:
				# Dict children should always have string keys
				key = child.key_field.value if hasattr(child, "key_field") else str(child.key_)
				data[key] = child.get_value()
			return data
		
		elif self.type == list:
			arr = []
			children = self.child_container.controls
			for i, child in enumerate(children):
				# List items are indexed by position, not by their stored key
				arr.append(child.get_value())
			return arr
		
		else:
			return None

	def get_pair(self) -> tuple:
		"""Return (key, value) tuple for this element."""
		# Check if parent is a list-type KeyValuePair
		if isinstance(self.pair_parent, KeyValuePair) and self.pair_parent.type == list:
			# For list items, key should be an integer (the index)
			# Find our index in the parent's children
			try:
				parent_children = self.pair_parent.child_container.controls
				# Unpack any Column wrappers
				unpacked = []
				for child in parent_children:
					if isinstance(child, ft.Column):
						unpacked += child.controls
					else:
						unpacked.append(child)
				
				# Find our index
				key = unpacked.index(self)
			except (ValueError, AttributeError):
				# Fallback: try to convert stored key to int
				try:
					key = int(self.key_)
				except:
					key = 0
		else:
			# For dict items or root items, key is a string
			key = self.key_field.value if hasattr(self, "key_field") else str(self.key_)
		
		return (key, self.get_value())



	## RENDERS
	def __set_preview_image_thread(self, image, path):
		self.__loading_preview = True
		print("SETTING PREVIEW THREAD")

		parts = os.path.basename(path).split(".")
		image.content = ft.Image(
			src_base64 = utility.load_and_pre_process_image( path, max_size=(200, 200) ),
			fit = ft.ImageFit.SCALE_DOWN,
			anti_alias = True,
			filter_quality=ft.FilterQuality.HIGH,
			width = 75,
			height = 75,
			tooltip=Tooltip(f"{parts[0]} : {parts[-1].upper()}", wait_duration=1000)
		)
		image.update()
		self.topr.update()
		self.__loading_preview = False

	def set_preview_image(self, path):
		if self.__loading_preview:
			print("!!! LOADING PREVIEW ALREADY : set_preview_image")
			return
		image = ft.SafeArea(
			minimum_padding = 4,
			content = ft.Container(  #Place Holder
				width = 75, height = 75,
				border_radius=6,
				bgcolor=THEME_COLOR,
				content = ft.Icon(ft.Icons.TIMELAPSE_ROUNDED)
			)
		)

		self.value_field.data = [
			path,
			image
		]

		self.add_preview_image()

		Thread(target = self.__set_preview_image_thread, args = [image, path], name = "__set_preview_image_thread", daemon=True).start()

	def add_preview_image(self):
		#Preview Image
		print("ADD PREVIEW IMAGE")
		if self.value_field.data and self.value_field.data[0] and os.path.exists(self.value_field.data[0]):
			print("ADD PREVIEW IMAGE : IN")
			index = 0
			for i, ctrl in enumerate(self.topr.controls):
				if ctrl == self.fields:
					index = i + 1
					break

			self.topr.controls.insert(index, self.value_field.data[1])

			self.topr.update()

			print(f"ADD PREVIEW : HAS ADDED : {self.value_field.data[1] in self.topr.controls}")

	def remove_preview_image(self):
		if self.value_field.data and self.value_field.data[1] in self.topr.controls:
			self.topr.controls.remove( self.value_field.data[1] )
			self.topr.update()

			self.value_field.data = None

	def __replace_preview_image_thread(self, path):
		self.__loading_preview = True
		self.value_field.data[0] = path
		self.value_field.data[1].content.src_base64 = utility.load_and_pre_process_image(path)
		parts = os.path.basename(path).split(".")
		self.value_field.data[1].content.tooltip=Tooltip(f"{parts[0]} : {parts[-1].upper()}", wait_duration=1000)
		try:
			self.topr.update()
		except: pass
		self.__loading_preview = False

	def replace_preview_image(self, path):
		if self.__loading_preview:
			print("!!! LOADING PREVIEW ALREADY : replace_preview_image")
			return
		self.new_registry("paths.preview", path)
		Thread(target = self.__replace_preview_image_thread, args = [path,], name = "__replace_preview_image_thread", daemon=True).start()

	def debounce_waiting(self) -> bool:
		if time.time() - self.registry_visual_debounce <= self.registry_visual_debounce_wait_time:
			return True
		
		return False

	def __apply_registry_visuals_wait_thread(self, preview_path):
		#Wait until debounce time reaches over time
		while self.debounce_waiting():
			time.sleep(0.1)

		time.sleep(0.1)

		if self.value_field.data:
			print(f"Replacing Image : {preview_path}")
			self.replace_preview_image(preview_path)
		else:
			print(f"Setting Image : {preview_path}")
			self.set_preview_image( preview_path )

		self.__registry_visual_wait_thread = None

	def check_registry_visuals(self):
		preview_path = self.get_registry_value("paths.preview", None)
		if preview_path and hasattr(self, "value_field"):

			#Check if expected value IS the value of value_field
			expected_data = self.get_registry_value("paths.preview:expected", None)
			if not expected_data or not expected_data == self.value_field.value.strip():
				self.__registry_visual_wait_thread = None
				print("No Expected Value in Field")
				return
			
			print(expected_data)

			self.registry_visual_debounce = time.time()
			if self.__registry_visual_wait_thread == None:
				print("Launching Thread")
				self.__registry_visual_wait_thread = Thread(
					target = self.__apply_registry_visuals_wait_thread,
					name = "__apply_registry_visuals_wait_thread",
					args = [preview_path,]
				)
				self.__registry_visual_wait_thread.start()

	def decide_view(self):
		self.topr.controls.clear()
		self.fields.controls.clear()
		self.bottomr.controls.clear()

		self.topr.controls.append(self.fields)

		# Key (not shown for list items)
		if not (self.pair_parent.type == list):
			self.key_field = ft.TextField(
				width = self.calc_width_via_text_len(str(self.key_)) ,
				value=str(self.key_),
				text_style = VALUE_TEXT_STYLE,
				label=f"Key",
				label_style=LABEL_TEXT_STYLE,
				dense=True,
				border_radius=6,
				border_width=0,
				bgcolor=BGCOLOR2,
				data = "KEY",
				on_change = self.on_string_changed_key
			)
			self.fields.controls.append(self.key_field)

		delete_btn = ft.IconButton(
			icon=ft.Icons.CLOSE, 
			icon_color="red",
			icon_size = 20,
			tooltip=Tooltip("Delete Item"), 
			on_click=self.remove_self
		)
		

		global_add = ft.IconButton(
			icon=ft.Icons.MY_LIBRARY_ADD_ROUNDED, 
			icon_size = 20,
			tooltip=Tooltip("Global Adjust"), 
			on_click=self.open_effect_dialog
		)

		self.topr.controls.insert(
			0,
			ft.Row(
				spacing = 0,
				controls = [
					delete_btn,
					global_add
				]
			)
		)

		if self.type in (dict, list):
			self.type_label = ft.Column(
				height = 35,
				width = 105,
				visible=True,
				alignment=ft.MainAxisAlignment.CENTER,
				horizontal_alignment=ft.CrossAxisAlignment.CENTER,
				controls = [
					ft.Text(
						value = "DICTIONARY" if self.type == dict else "LIST",
						text_align=ft.TextAlign.CENTER,
						style = ft.TextStyle(
							size = 15,
							color = ft.Colors.with_opacity(0.5, ft.Colors.WHITE),
							weight = ft.FontWeight.BOLD
						)
					)
				]
			)
			self.topr.controls.insert(2, self.type_label)

		# --- Render field based on type ---
		if self.type in (int, float, bool, str, None):
			self.render_primitive()
		elif self.type in (dict, list):
			self.render_collection()

		try:
			self.update()
		except:
			pass

		self.reference = self.create_reference()
		self.check_registry_visuals()

	def render_primitive(self):
		val = str(self.value)

		def __open_source_panel(event = None, obj = None):
			self.app.PAGE.source.toggle(target = obj)

		self.source_btn = ft.IconButton(
			icon=ft.Icons.SOURCE_ROUNDED, 
			tooltip=Tooltip("Add from Source"),
			on_click = lambda _, o=self: __open_source_panel(obj = o)
		)
		if self.type is str:
			#STRINGS, PATHS, BODIES (large text)
			if utility.looks_like_path(val): #Path
				def __open_value(field):
					"""Opens a file or folder in Windows Explorer."""
					if os.path.exists(field.value):
						path = os.path.normpath(field.value)
						if os.path.isdir(path):
							os.startfile(path)  # opens the folder
						elif os.path.isfile(path):
							os.startfile(os.path.dirname(path))  # opens its parent folder
					else:
						self.app.notify(f"Field Path is likely a Source Path Spliced Value AND OR does not exist.", 3000)
					

				self.value_field = ft.TextField(
					expand=True, 
					value=val,
					text_style = VALUE_TEXT_STYLE,
					label="Value : PATH",
					label_style=LABEL_TEXT_STYLE,
					dense=True,
					border_radius=6, 
					border_width=0, 
					bgcolor = BGCOLOR2,
					tooltip = Tooltip(val),
					on_change=self.on_string_changed_value,
					
				)
				self.browse_button = ft.IconButton(icon=ft.Icons.FOLDER_OPEN, tooltip=Tooltip("Open Folder"), on_click=lambda _, f=self.value_field: __open_value(f))
				self.topr.controls += [self.browse_button, self.source_btn]
				self.fields.controls.append(self.value_field)
			else: #Str or Body
				body = utility.check_full_text(val)
				self.value_field = ft.TextField(
					expand=True, 
					value=val,
					text_style = VALUE_TEXT_STYLE,
					label="Value : BODY (STR)" if body else "Value : STR",
					label_style=LABEL_TEXT_STYLE,
					dense=True,
					multiline=body,
					max_lines=25 if body else 1,
					border_radius=6, 
					border_width=0, 
					bgcolor = BGCOLOR2,
					on_change=self.on_string_changed_value,
					
				)
				self.topr.controls += [self.source_btn]
				self.fields.controls.append(self.value_field)
		else:
			type_str = self.detect_primitive(val)

			# NUMBERS & BOOLS
			self.value_field = ft.TextField(
				expand=True, 
				value=val,
				text_style = VALUE_TEXT_STYLE,
				label=f"Value : {type_str.upper()}",
				label_style=LABEL_TEXT_STYLE,
				dense=True, 
				border_radius=6, 
				border_width=0,
				bgcolor = BGCOLOR2,
				on_change=self.on_string_changed_value,
				
			)
			self.topr.controls += [self.source_btn]
			self.fields.controls.append(self.value_field)

	def change_type(self, type:any):
		self.type_history[self.type] = self.value

		self.type = type
		self.value = " "
		self.decide_view()

	def render_collection(self):
		self.child_container = ft.Column(expand = True, spacing=2, width = float("inf"))
		self.render_children()

		def __copy_collection(obj):
			pair = obj.get_pair()
			key = pair[0]
			
			if isinstance(pair[1], dict):
				data = {}
				for key in pair[1]:
					if key in [UUID_KEY]: continue
					data[key] = pair[1][key]
				if not key:
					key = "dict"
			else:
				if not key:
					key = "list"
				data = pair[1]

			self.app.copy_to_clipboard( json.dumps({key:data}) )

		change_type_btn = ft.IconButton(
			icon=ft.Icons.CHANGE_HISTORY_ROUNDED, 
			tooltip=Tooltip("Revert to Primitive"),
			on_click=lambda 
			e, t=str: self.change_type(t)
		)
		add_btn = ft.IconButton(
			icon=ft.Icons.ADD, 
			tooltip=Tooltip("Add Pair"),
			on_click=lambda 
			e: self.add_child()
		)
		copy_btn = ft.IconButton(
			icon=ft.Icons.DATA_OBJECT_ROUNDED if self.type == dict else ft.Icons.DATA_ARRAY_ROUNDED, 
			tooltip=Tooltip(f"Copy Collection"), 
			on_click=lambda 
			e, o=self: __copy_collection(o)
		)
		self.topr.controls.append(
			ft.Row(
				expand = True,
				alignment=ft.MainAxisAlignment.END,
				controls = [change_type_btn, copy_btn, add_btn]
			)
		)

		self.bottomr.visible = True
		self.bottomr.controls += [self.child_container]

	def reorder(self, event:ft.WindowEvent):
		triggered = False

		#Get Position Index
		index = 0
		for i, ctrl in enumerate(self.topr.controls):
			index = i
			if ctrl == self.fields:
				break
			
		def less_than(value:int, values:list):
			for val in values:
				if value < val:
					return True
			return False

		#Check Size
		width = self.app.CORE.window.width
		if less_than(width, [1000, 1500]):
			triggered = True

		#Reorder
		if triggered and not self.compact:
			self.compact = True

			controls = self.fields.controls
			self.topr.controls.remove(self.fields)
			self.app.PAGE.editor.update_instance_pairs()

			if width < 1000 and len(self.app.PAGE.editor.instances.controls) == 1:
				self.fields = ft.Column(
					expand = True,
					spacing = 8,
					controls=controls
				)
			elif width < 1500 and len(self.app.PAGE.editor.instances.controls) > 1:
				self.fields = ft.Column(
					expand = True,
					spacing = 8,
					controls=controls
				)

			if self.type_label and self.type_label.visible:
				self.type_label.visible = False

			self.topr.controls.insert(index, self.fields)
			self.app.PAGE.editor.update_instance_pairs()

		#Reset
		if self.compact and not triggered:
			self.compact = False

			controls = self.fields.controls
			self.topr.controls.remove(self.fields)
			self.app.PAGE.editor.update_instance_pairs()

			self.fields = ft.Row(
				expand = True,
				spacing = 2,
				controls=controls
			)

			if self.type_label and not self.type_label.visible:
				self.type_label.visible = True

			self.topr.controls.insert(index, self.fields)
			self.app.PAGE.editor.update_instance_pairs()

	## CHILDREN
	def render_children(self):
		self.child_container.controls.clear()
		if isinstance(self.value, dict):
			for k, v in self.value.items():
				item = KeyValuePair(self.app, self.instance, self, k, v)
				self.child_container.controls.append( item )
		elif isinstance(self.value, list):
			for i, v in enumerate(self.value):
				item = KeyValuePair(self.app, self.instance, self, i, v)
				self.child_container.controls.append( item )

	def add_child(self):
		self.value = self.get_value()
		if isinstance(self.value, dict):
			new_key = f"key_{len(self.value)}"
			self.value[new_key] = ""
		elif isinstance(self.value, list):
			self.value.append("")
		self.render_children()
		self.update()
		self.instance.mark_as_edited()



class KeyedItem(ft.FloatingActionButton):
	def __init__(self, group_key:str, key:str, data:dict, on_click:Callable, on_copy:Callable, on_remove:Callable):
		self.id = key
		self.__name = utility.readable_key(key)
		self.group = group_key
		self.on_click_func = on_click
		self.on_remove_func = on_remove
		self.on_copy_func = on_copy
		self.type = None

		self.name = ft.Text(
			value = self.__name,
			style = ft.TextStyle(
				size = 17,
				weight = ft.FontWeight.BOLD
			)
		)

		self.buttons = ft.Row(
			visible=False,
			alignment = ft.MainAxisAlignment.END,
			right = 5,
			top = -8,
			height = 45,
			controls = [
				ft.FloatingActionButton(
					width = 30,
					height = 35,
					bgcolor = ft.Colors.TRANSPARENT,
					shape = ft.RoundedRectangleBorder(radius = 100),
					disabled_elevation=True,
					elevation = 0,
					content = ft.Icon(
						ft.Icons.VERTICAL_SPLIT_ROUNDED,
					),
					tooltip = Tooltip(f"Split '{self.__name}'"),
					on_click = self.split
				),
				ft.FloatingActionButton(
					width = 30,
					height = 35,
					bgcolor = ft.Colors.TRANSPARENT,
					shape = ft.RoundedRectangleBorder(radius = 100),
					disabled_elevation=True,
					elevation = 0,
					content = ft.Icon(
						ft.Icons.CONTROL_POINT_DUPLICATE_ROUNDED,
					),
					tooltip = Tooltip(f"Duplicate '{self.__name}'"),
					on_click = self.copy_self
				),
				ft.FloatingActionButton(
					width = 30,
					height = 35,
					bgcolor = ft.Colors.TRANSPARENT,
					shape = ft.RoundedRectangleBorder(radius = 100),
					disabled_elevation=True,
					elevation = 0,
					content = ft.Icon(
						ft.Icons.DELETE_FOREVER_ROUNDED,
					),
					tooltip = Tooltip(f"Delete '{self.__name}'"),
					on_click = self.remove_self
				)
			]
		)

		super().__init__(
			disabled_elevation=True,
			shape = ft.RoundedRectangleBorder(radius = 6),
			bgcolor = ft.Colors.with_opacity(0.2, THEME_COLOR),
			width = float("inf"),
			height = 35,
			content = ft.GestureDetector(
				on_enter = self.show,
				on_exit = self.hide,
				content = ft.SafeArea(
					minimum_padding = 4,
					expand=False,
					content = ft.Stack(
						expand = True,
						height = 35,
						controls = [
							ft.Row(
								width = float("inf"),
								controls = [
									self.name,
									self.buttons
								]
							),
							self.buttons
						]
					)
				)
			),
			data = data,
			on_click = self.clicked
		)
 
	def split(self, event):
		self.on_click_func(self, True)

	def show(self, event = None):
		self.buttons.visible = True
		try:
			self.buttons.update()
		except: pass

	def hide(self, event = None):
		self.buttons.visible = False
		try:
			self.buttons.update()
		except: pass

	def clicked(self, event):
		self.on_click_func(self)

	def remove_self(self, event):
		self.parent.controls.remove(self)
		self.parent.update()
		self.on_remove_func(self.group, self.data)

	def copy_self(self, event):
		self.on_copy_func(self)
