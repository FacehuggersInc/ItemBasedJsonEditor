from src import *

from src.controls.etc import *
from src.controls.item import *
from src.controls.toolbar import *
from src.controls.dialogs import *


from src.panels.editor import EditorPanel
from src.panels.navigator import NavigatorPanel
from src.panels.source import SourcesPanel

## PAGE
class EnvironmentPage(ft.Column):
	def __init__(self, app:any):
		## INIT
		self.app = app
		self.loaded_paths :list = []
		self.recent_files = self.app.DATA['recent']
		self.__save_as_holding = None

		## BUILD
		self.editor = EditorPanel(self)
		self.navigator = NavigatorPanel(self)
		self.source = SourcesPanel(self)

		self.recent_menu = ToolbarMenuBTN(
			"Recent", [
				ToolbarItemBTN(
					f" {os.path.basename(path)} ",
					ft.Icons.DATA_OBJECT_ROUNDED,
					lambda _, p=path: self.load_file_result(None, p)
				)
				for path in self.recent_files
			],
			ft.Icons.HISTORY_ROUNDED
		)

		self.__toolbar = ft.MenuBar(
			controls = [
				ToolbarMenuBTN(
					"File",
					[	
						ToolbarItemBTN("Save", ft.Icons.SAVE_ROUNDED, self.save_all),
						ToolbarItemBTN("Save As", ft.Icons.SAVE_AS_ROUNDED, self.open_save_file_as_dialog),
						ToolbarItemBTN("Open CWD", ft.Icons.FOLDER_ROUNDED, self.open_cwd),
						ToolbarItemBTN("Reload", ft.Icons.REFRESH_ROUNDED, self.open_reload_dialog),
						
					]
				),
				ToolbarMenuBTN(
					"View",
					[	
						ToolbarItemBTN("Items Panel", ft.Icons.VIEW_AGENDA, self.navigator.toggle),
						ToolbarItemBTN("Source Panel", ft.Icons.VIEW_AGENDA, self.source.toggle),
						
					],
					ft.Icons.VIEW_QUILT_ROUNDED
				),
				self.recent_menu,
				ToolbarItemBTN("Load", ft.Icons.FILE_OPEN_ROUNDED, self.load_file),
				ToolbarItemBTN("Sources", ft.Icons.SOURCE_ROUNDED, self.open_sources_dialog),
			]
		)

		self.app.subscribe_to_window_event(
			ft.WindowEventType.RESIZED,
			self.change_panel_docking
		)

		## FINAL
		self.panels = ft.Row(
			expand = True,
			spacing = 5,
			controls = [
				self.navigator,
				self.editor,
				self.source
			]
		)

		self.dock = ft.Stack(
			expand = True,
			controls = [
				self.panels
			]
		)

		super().__init__(
			expand = True,
			spacing = 5,
			controls = [
				self.__toolbar,
				self.dock
			]
		)

	## OTHER
	def open_cwd(self, event):
		os.startfile(os.getcwd())

	def open_sources_dialog(self, event = None):
		dialog = SourcesDialog(self)
		dialog.on_dismiss = lambda _, d=dialog: self.save_sources(d)
		self.app.dialog(dialog)
	
	def change_panel_docking(self, event):
		pass

	## LOAD
	def reload_file(self, event = None):
		if not self.loaded_paths: return

		self.navigator.clear()
		self.editor.clear()
		paths = self.loaded_paths
		self.loaded_paths = []
		for path in paths:
			self.load_file_result(path = path)
		self.app.LOGGER.info(f"Reloaded {len(paths)} Paths.")
		self.app.dialog(close = True)

	def open_reload_dialog(self, event = None):
		if not self.loaded_paths: return
		dialog = DialogTemplate(
			"Are you Sure?",
			height = 195,
			content = ft.Column(
				expand = True,
				controls = [
					ft.Text(
						"Reloading will NOT SAVE any data back to their Files! Reloading is intended to Update Groups & Items if data changed within the Source file(s). Essentially OVERWRITING Any Data you've changed recently that was not saved!",
						text_align=ft.TextAlign.CENTER,
						style=ft.TextStyle(
							size = 18,
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
								on_click = lambda _, c=True: self.app.dialog(close = c)
							),
							ft.FloatingActionButton(
								disabled_elevation=True,
								bgcolor = ft.Colors.BLUE_500,
								shape = ft.RoundedRectangleBorder(radius = 4),
								width = 150,
								height = 45,
								content = ft.Text(
									"Reload",
									style = ft.TextStyle(
										size = 18,
										weight = ft.FontWeight.BOLD
									)
								),
								on_click = self.reload_file
							)
						]
					)
				]
			)
		)
		self.app.dialog(dialog)

	def check_as_proper_json(self, data:dict):
		"""check's dict for proper template key > list > dict"""
		for key in data:
			if not isinstance(data[key], list):

				return False
			
			for item in data[key]:
				if not isinstance(item, dict):
					return False
		
		return True

	def load_file_result(self, e: ft.FilePickerResultEvent = None, path:str = ""):
		"""A Callback / Call to load data into Navigator and set loaded_path"""
		if (e and not e.files) or (not e and not path): return

		files = []
		if e and not path:
			files += [file.path for file in e.files]
		if path and not e:
			files.append(path)

		for file_to_load in files:
			if os.path.exists(file_to_load):
				with open(file_to_load, "r") as file:
					data = json.load(file)
					if self.check_as_proper_json(data):
						self.loaded_paths.append(file_to_load)
						self.navigator.load( file_to_load, data )
						if not (file_to_load in self.recent_files):
							self.app.LOGGER.info(f"Loaded JSON at {file}")
							self.recent_files.append(file_to_load)
							self.recent_files = self.recent_files[-10:]
					else:
						self.app.LOGGER.warning(f"JSON given did not follow proper template: dict key > list > dict item ({file})")
						self.app.notify(f"{os.path.basename(file_to_load)} is not an Accepted JSON Template", 3000)

	def load_file(self, event = None):
		"""Opens File Explorer, Calls load_file_result when done"""
		self.app.open_explorer(
			"Load a JSON File",
			self.load_file_result,
			ExplorerTypes.FILES,
			allow_multiple = True,
			type = ft.FilePickerFileType.CUSTOM,
			accepted_types = ["json"]
		)

	## SAVE
	def save_sources(self, dialog:SourcesDialog):
		new = {}
		for item in dialog.sources.controls:
			item : SourceItem = item

			path = item.source_field.value
			if not path: continue

			mod = item.mod
			opt = None
			match mod:
				case "path_splice":
					opt = item.modifiers.controls[0].value
				case _: pass

			if not new.get(path):
				new[path] = {mod:opt}
			else:
				new[path][mod] = opt

		self.app.DATA["sources"] = new

		try:
			self.app.dialog(close = True)
		except: pass #when app stops, this could error

		#Reload Sources
		if self.source.visible:
			self.source.clear()
			self.source.load()

	def save_json_file(self, path:str, data:dict):
		with open(path, "w") as file:
			json.dump(data, file)

	def save_all(self, event = None):
		if not (self.navigator and len(self.loaded_paths) > 0): return

		groups = self.navigator.get_groups()

		#Separate to Files
		fid_groups = {}
		for group in groups:
			group_key, items, fid, name = group
			if fid_groups.get(fid):
				fid_groups[fid][group_key] = items
			else:
				fid_groups[fid] = {group_key:items}

		#Save Files
		for path, data in fid_groups.items():
			self.save_json_file(path ,data)
			self.app.LOGGER.info(f"Saved File: {path}")

		try:
			self.app.notify(f"Saved {len(self.loaded_paths)} Files!", 2500)
		except: pass

	def save_as(self, e: ft.FilePickerResultEvent = None):
		if (e and not e.files) or not self.__save_as_holding: return

		new_file = e.files[0].path
		data :dict[str, list] = self.__save_as_holding[1]
		self.save_json_file(f"{new_file}.json" if not new_file.endswith(".json") else new_file, data)
		self.app.notify(f"Saved New File as {os.path.basename(new_file)}!", 2500)
		self.app.LOGGER.info(f"New Saved As File : {new_file}")
		self.app.dialog(close = True)

	def open_save_as_explorer(self, path:str, data:dict):
		self.__save_as_holding = (path, data)
		self.app.open_explorer(
			"Choose a JSON File / Rename",
			self.save_as,
			ExplorerTypes.FILES,
			type = ft.FilePickerFileType.ANY,
			initial_directory = os.path.dirname(path),
		)

	def open_save_file_as_dialog(self, event = None):
		groups = self.navigator.get_groups()

		#Separate to Files
		fid_groups = {}
		for group in groups:
			group_key, items, fid, name = group
			if fid_groups.get(fid):
				fid_groups[fid][group_key] = items
			else:
				fid_groups[fid] = {group_key:items}

		saveable_options = ft.Row(
			expand = True,
			spacing = 5,
			wrap = True,
			alignment = ft.MainAxisAlignment.CENTER,
			vertical_alignment = ft.CrossAxisAlignment.CENTER,
			run_spacing = 5,
			controls = [
				ft.FloatingActionButton(
					disabled_elevation=True,
					bgcolor = ft.Colors.LIGHT_GREEN_500,
					shape = ft.RoundedRectangleBorder(radius = 4),
					width = 200,
					height = 45,
					content = ft.Text(
						f"File: {os.path.basename(fid)}",
						style = ft.TextStyle(
							size = 18,
							color = "black",
							weight = ft.FontWeight.W_600
						)
					),
					on_click = lambda _, p=fid, d=fid_groups[fid]: self.open_save_as_explorer(p, d)
				) for fid in fid_groups
			]
		)

		dialog = DialogTemplate(
			"Which File are you Saving?",
			height = 250,
			content = ft.SafeArea(
				minimum_padding = 5,
				content = ft.Column(
					expand = True,
					controls = [
						ft.ListView(
							expand = True,
							controls = [saveable_options]
						),
						ft.Row(
							alignment=ft.MainAxisAlignment.CENTER,
							controls = [
								ft.FloatingActionButton(
									disabled_elevation=True,
									bgcolor = ft.Colors.GREY_900,
									shape = ft.RoundedRectangleBorder(radius = 4),
									width = 150,
									height = 45,
									content = ft.Text(
										"Close",
										style = ft.TextStyle(
											size = 18,
											weight = ft.FontWeight.BOLD
										)
									),
									on_click = lambda _, c=True: self.app.dialog(close = c)
								)
							]
						)
					]
				)
			)
		)
		self.app.dialog(dialog)