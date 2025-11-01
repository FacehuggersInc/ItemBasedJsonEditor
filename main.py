from src.app import ItemBasedJsonEditorApp
import os, sys, subprocess, time

def update():
	here = os.path.abspath(os.path.dirname(sys.argv[0]))

	updater_path = os.path.join(here, "updater.py")
	install_path = here
	repo_zip = "https://github.com/FacehuggersInc/ItemBasedJsonEditor/archive/refs/heads/main.zip"
	relaunch_path = os.path.join(here, "main.py")

	creationflags = 0
	if os.name == "nt":  # Detach on Windows
		creationflags = subprocess.DETACHED_PROCESS | subprocess.CREATE_NEW_PROCESS_GROUP

	subprocess.Popen(
		[
			sys.executable,
			updater_path,
			install_path,
			repo_zip,
			relaunch_path,
			"force"
		],
		creationflags=creationflags,
		stdout=subprocess.DEVNULL,
		stderr=subprocess.DEVNULL,
		stdin=subprocess.DEVNULL,
		close_fds=True
	)

	# Optional short delay to ensure process spawn
	time.sleep(0.3)
	sys.exit(0)

if __name__ == "__main__":
	args = sys.argv
	if len(args) > 1 and args[1] == "force":
		APP = ItemBasedJsonEditorApp()
		APP.run()  # Start | go to src/app.py -> JsonEditorApp class to make changes
	else:
		update()