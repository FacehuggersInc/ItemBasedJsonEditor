import os, sys, time, shutil, zipfile, subprocess, tempfile
import urllib.request

def log(text: str):
	print(f"[UPDATER]: {text}")

def main():
	os.system("CLS" if os.name == "nt" else "clear")

	if len(sys.argv) < 4:
		log("No given arguments. Expected: python updater.py <install_path> <github_zip_url> <relaunch_path> [args...]")
		sys.exit(1)

	install_path = os.path.abspath(sys.argv[1])
	github_zip_url = sys.argv[2]
	relaunch_path = sys.argv[3]
	relaunch_args = sys.argv[4:]

	temp_dir = tempfile.mkdtemp()
	zip_path = os.path.join(temp_dir, "update.zip")

	try:
		# 1. Download the repo zip
		log(f"Downloading : {github_zip_url}")
		with urllib.request.urlopen(github_zip_url) as response, open(zip_path, "wb") as out_file:
			shutil.copyfileobj(response, out_file)

		# 2. Extract it
		log("Extracting update ...")
		with zipfile.ZipFile(zip_path, 'r') as zip_ref:
			zip_ref.extractall(temp_dir)

		# 3. Find the extracted repo root folder
		extracted_folders = [f for f in os.listdir(temp_dir) if os.path.isdir(os.path.join(temp_dir, f))]
		if not extracted_folders:
			log("Error: No files extracted.")
			sys.exit(1)
		repo_root = os.path.join(temp_dir, extracted_folders[0])

		# 4. Copy files into install path
		log(f"Copying and replacing files to {install_path} ...")
		for root, _, files in os.walk(repo_root):
			rel_path = os.path.relpath(root, repo_root)
			target_dir = os.path.join(install_path, rel_path)
			os.makedirs(target_dir, exist_ok=True)
			for file in files:
				src_file = os.path.join(root, file)
				dst_file = os.path.join(target_dir, file)
				shutil.copy2(src_file, dst_file)

		# 5. Relaunch target and exit immediately
		log("Waiting for file handles to release ...")
		time.sleep(1)

		log(f"Relaunching: {relaunch_path}")
		if relaunch_path.lower().endswith(".py"):
			subprocess.Popen([sys.executable, relaunch_path] + relaunch_args,
								stdout=subprocess.DEVNULL,
								stderr=subprocess.DEVNULL,
								stdin=subprocess.DEVNULL,
								close_fds=True)
		else:
			subprocess.Popen([relaunch_path] + relaunch_args,
								stdout=subprocess.DEVNULL,
								stderr=subprocess.DEVNULL,
								stdin=subprocess.DEVNULL,
								close_fds=True)

		log("Done — exiting updater.")
		sys.exit(0)

	except Exception as e:
		log(f"Update failed: {e}")
		input("[UPDATER] Press ENTER to exit ...")

	finally:
		shutil.rmtree(temp_dir, ignore_errors=True)

if __name__ == "__main__":
	main()