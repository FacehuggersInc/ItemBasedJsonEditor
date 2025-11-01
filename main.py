from src.app import ItemBasedJsonEditorApp
import os, sys, subprocess

#Flet docs : https://flet.dev/docs/controls/layout

def update():
	here = os.path.dirname( sys.argv[0] )
	subprocess.Popen([
		sys.executable,                 # ensures same Python interpreter
		os.path.join(here, "updater.py"),                   # script to run
		here,                    # install path
		"https://github.com/FacehuggersInc/ItemBasedJsonEditor/archive/refs/heads/main.zip",  # ZIP download URL
		os.path.join(here, "main.py"),  # relaunch path
		"force"                         # updater bypass for this file
	])
	sys.exit(1)

if __name__ == "__main__":
	
	args = sys.argv
	if len(args) > 1:
		if args[1] == "force":
			APP = ItemBasedJsonEditorApp()
			APP.run() #Start | go to src/app.py -> JsonEditorApp Class to Make Changes to the App
		else:
			update()
	else:
		update()