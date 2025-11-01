from src import *

from src.enviroment import EnvironmentPage
from src.controls.dialogs import *

class ItemBasedJsonEditorApp():
	def __init__(self):
		self.CORE :ft.Page = None
		self.FILEMANAGER = ft.FilePicker()

		self.EVENTS = {}

		self.LOGGER = utility.DateLogger(log_dir="logs")
		self.LOGGER.load()
		self.LOGGER.info("Initializing")

		self.DIALOGS = []
		self.last_dialog: ft.AlertDialog | None = None
		self.__transitioning = False  # prevent re-entry loops

		self.DATA = {
			"defaults" : {
				"name" : "New Item {i}",
				"id" : "new_item_{i}"
			},
			"lastdir" : None,
			"recent" : [],
			"sources" : {},
			"registry": {}
		}
		if os.path.exists("settings.json"):
			self.LOGGER.info("Loading Data (settings.json) ...")
			with open("settings.json", "r") as datafile:
				loaded = json.load(datafile)
				for key, item in loaded.items():
					self.DATA[key] = item

		self.global_path = f"C:\\"
		if self.DATA.get("lastdir"):
			self.global_path = self.DATA["lastdir"]

	def __on_window_event(self, event:ft.WindowEvent):
		type :ft.WindowEventType = event.type
		event_calls = self.EVENTS.get(type)
		if event_calls and len(event_calls) > 0:
			to_remove = []
			for call in event_calls:
				try:
					call(event)
				except Exception as e:
					print(f"On Window Event:{type} Exception:{e} for call:{call}")
					to_remove.append(call)
			
			#Cleanup Broken Events
			for callable in to_remove:
				self.EVENTS[type].remove(callable)



	def __file_manager_callback(self, event:any = None, callback:Optional[Callable] = None):
		"""Dont Call This. Gets Called when the user selects a file in the File Explorer opened by open_explorer. Will Call the Given Callback Function"""
		try:
			if event:
				if event.path and os.path.exists(event.path): 
					self.global_path = event.path
				else:
					if event.files:
						for file in event.files:
							if file.path and (os.path.exists(file.path) or os.path.exists( os.path.dirname(file.path) )):
								self.global_path = os.path.dirname(file.path)
								break

			callback(event)
			self.FILEMANAGER.on_result = None
		except Exception as e:
			self.LOGGER.error("Handled File Manager Callback Error: {e}", include_traceback=True)

	def subscribe_to_window_event(self, event:ft.WindowEventType, callable:Callable):
		if not self.EVENTS.get(event):
			self.EVENTS[event] = []
		self.EVENTS[event].append(callable)

	def open_explorer(self, title:str, callback:Callable, looking_for:ExplorerTypes, allow_multiple:bool = False, type:ft.FilePickerFileType = None, accepted_types:list[str] = [], initial_directory:str = None) -> None:
		"""Opens the File Explorer to get Folders or Files"""
		self.FILEMANAGER.on_result = lambda e,: self.__file_manager_callback(e, callback)
		match looking_for:
			case ExplorerTypes.FILES:
				self.FILEMANAGER.pick_files(
					dialog_title=title,
					initial_directory = self.global_path if not initial_directory else initial_directory,
					file_type = type,
					allow_multiple=allow_multiple,
					allowed_extensions = accepted_types
				)
			case ExplorerTypes.FOLDER:
				self.FILEMANAGER.get_directory_path(
					dialog_title=title,
					initial_directory = self.global_path if not initial_directory else initial_directory
				)
	
	def get_dialog(self):
		return self.DIALOGS[-1] if self.DIALOGS else None
	
	def dialog(self, dialog: ft.AlertDialog = None, close: bool = False):
		"""Unified dialog manager with timing delays to prevent flash/self-close."""
		if self.__transitioning:
			return
		self.__transitioning = True

		try:
			current = self.DIALOGS[-1] if self.DIALOGS else None

			# --- Case 1: Close and clear everything ---
			if close:
				if current:
					self.CORE.close(current)
					time.sleep(0.05)
				self.DIALOGS.clear()
				self.last_dialog = None
				return

			# --- Case 2: No dialog given → close current, reopen previous ---
			if dialog is None:
				if not self.DIALOGS:
					return
				self.CORE.close(current)
				#self.CORE.update()
				time.sleep(0.05)
				self.DIALOGS.pop()
				if self.DIALOGS:
					prev = self.DIALOGS[-1]
					self.CORE.open(prev)
					self.last_dialog = prev
				else:
					self.last_dialog = None
				return

			# --- Case 3: Same dialog → toggle (close it) ---
			if current == dialog:
				self.CORE.close(current)
				time.sleep(0.05)
				self.DIALOGS.pop()
				self.last_dialog = self.DIALOGS[-1] if self.DIALOGS else None
				return

			# --- Case 4: New dialog ---
			if dialog.on_dismiss is None:
				dialog.on_dismiss = lambda e: self.dialog(close=False)

			if current:
				self.CORE.close(current)
				time.sleep(0.07)  # give Flet time to commit the close

			self.DIALOGS.append(dialog)
			self.last_dialog = dialog
			self.CORE.open(dialog)
			time.sleep(0.03)  # brief settle delay

		finally:
			self.__transitioning = False

	def notify(self, content:ft.Control|str, ms_duration = 1500):
		try:
			bar = ft.SnackBar(
				content = content if not type(content) == str else ft.Text(content, style=ft.TextStyle(size = 18, weight=ft.FontWeight.BOLD, color = "white")),
				duration = ms_duration,
				bgcolor = ft.Colors.BROWN
			)
			self.CORE.open(bar)
		except Exception as e:
			self.LOGGER.error(f"Handled Notify Error: {e}", include_traceback=True)
	
	def copy_to_clipboard(self, text:str):
		self.CORE.set_clipboard(text)

	def get_clipboard(self) -> str:
		return self.CORE.get_clipboard()

	def build(self, page:ft.Page):
		"""Main Point to Add Controls / Customize the Application"""
		self.LOGGER.info("Building Application ...")
		page.window.center()

		self.CORE = page

		self.CORE.theme_mode = "dark"
		self.CORE.theme = ft.Theme(color_scheme_seed=THEME_COLOR)
		self.CORE.title = APP_NAME
		width = 950
		self.CORE.window.min_width = width
		self.CORE.window.width = width * 2
		self.CORE.window.height = 850

		self.CORE.padding = 5

		self.CORE.window.on_event = self.__on_window_event

		self.CORE.overlay.append(self.FILEMANAGER)

		self.PAGE = EnvironmentPage(self)

		self.CORE.add( self.PAGE )

	def run(self):
		"""Entrypoint to Application"""
		ft.app(target=self.build) ## BLOCKING

		#Reliable Save
		self.PAGE.editor.save() #saves all objects
		self.PAGE.save_all() #saves all objects within groups (this would not save any new changes within editorinstances is not saved to their group)

		#Check if SourcesDialog Dialog is Open and Save Sources Anyway
		dialog = self.get_dialog()
		if dialog and isinstance(dialog, SourcesDialog):
			self.LOGGER.info("Manually Saving Sources ...")
			self.PAGE.save_sources(dialog)

		#Save Data
		self.DATA["recent"] = self.PAGE.recent_files
		self.DATA["lastdir"] = self.global_path
		with open("settings.json", "w") as datafile:
			json.dump(self.DATA, datafile, indent = 4)

		self.LOGGER.log("Saved Instances.")
		self.LOGGER.close()