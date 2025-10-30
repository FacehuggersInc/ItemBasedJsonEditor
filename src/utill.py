from src import *

SUPPORTED_IMAGE_EXTS = {"png", "jpg", "jpeg", "bmp", "gif", "tiff", "webp"}

def readable_key(key: str) -> str:
	"""
	Convert a string key or id into a human-readable string.
	Examples:
		"iron_sword" -> "Iron Sword"
		"CRYSTALSTAFF" -> "Crystal Staff"
		"phantom-cloak" -> "Phantom Cloak"
		"fireStaff123" -> "Fire Staff 123"
	"""
	# Replace underscores, hyphens, and dots with spaces
	key = re.sub(r"[_\-.]+", " ", str(key))

	# Split camel case (e.g., "fireStaff" -> "fire Staff")
	key = re.sub(r"(?<=[a-z])(?=[A-Z])", " ", key)

	# Capitalize each word
	key = " ".join(word.capitalize() for word in key.split())

	return key

def random_string(length: int, include_chars:bool = True, include_symbols: bool = True, include_digits: bool = True) -> str:
	chars = []
	if include_chars: 
		chars += string.ascii_letters  # a-z + A-Z
	if include_digits:
		chars += string.digits     # 0-9
	if include_symbols:
		chars += string.punctuation  # !"#$%&'()*+,-./:;<=>?@[\]^_`{|}~

	return ''.join(random.choice(chars) for _ in range(length))

def hex_digest(text: str, algorithm: str = "sha256") -> str:
	"""Return the hexadecimal digest of a string using the given algorithm."""
	h = hashlib.new(algorithm)
	h.update(text.encode("utf-8"))
	return h.hexdigest()

def check_full_text(text:str) -> bool:
	has_punctuation = bool(re.search(r"[^\w\s]", text))
	has_newline = "\n" in text
	has_tab = "\t" in text
	return has_punctuation or has_newline or has_tab

def looks_like_path(s: str) -> bool:
	# Common path indicators
	if any(x in s for x in ("/", "\\", "./", "../")):
		return True
	# Drive letter on Windows (C:\something)
	if re.match(r"^[A-Za-z]:[\\/]", s):
		return True
	# Has file extension pattern like "file.txt" or "archive.tar.gz"
	if re.search(r"\.\w{1,5}$", s):
		return True
	# Looks like a hidden file or folder (.git, .env)
	if s.startswith(".") and len(s) > 1:
		return True
	return False

def load_and_pre_process_image(
	image_path: str,
	scale_factor: int = 4,
	enhance_contrast: float = 1.1,
	sharpen: bool = True,
	max_size: tuple[int, int] | None = None
) -> str:
	"""
	Loads an image, optionally upscales and enhances it for pixel art.
	If the image dimensions are >= max_size, returns raw base64 without processing.
	"""
	with open(image_path, "rb") as f:
		img_bytes = f.read()

	with Image.open(io.BytesIO(img_bytes)) as img:
		img = img.convert("RGBA")

		# Skip processing if over max_size
		if max_size and (img.width >= max_size[0] or img.height >= max_size[1]):
			with io.BytesIO() as buffer:
				img.save(buffer, format="PNG", optimize=True)
				return base64.b64encode(buffer.getvalue()).decode("utf-8")

		# Upscale using nearest neighbor
		new_size = (img.width * scale_factor, img.height * scale_factor)
		img = img.resize(new_size, resample=Image.NEAREST)

		# Enhancements
		if sharpen:
			img = ImageEnhance.Sharpness(img).enhance(1.2)
		if enhance_contrast != 1.0:
			img = ImageEnhance.Contrast(img).enhance(enhance_contrast)

		# Convert to base64
		with io.BytesIO() as buffer:
			img.save(buffer, format="PNG", optimize=True)
			return base64.b64encode(buffer.getvalue()).decode("utf-8")

def uplift_dict_values(data: dict) -> dict:
	"""
	Flatten a dictionary by uplifting values of nested dicts one level.

	Rules:
	- If a key's value is a dict, merge its keys into the parent dict.
	- If a key's value is not a dict, keep it as-is.
	- Only flattens one level deep.

	Example:
	{'a': {'x': 1, 'y': 2}, 'b': 3} → {'x': 1, 'y': 2, 'b': 3}
	"""
	if not isinstance(data, dict):
		return data  # Only process dicts

	new_data = {}
	for key, val in data.items():
		if isinstance(val, dict):
			# Merge nested dict into parent
			for sub_key, sub_val in val.items():
				new_data[sub_key] = sub_val
		else:
			new_data[key] = val

	return new_data

class DateLogger:
    """
    A logger that creates separate log files by date and automatically logs to the correct file.
    Features:
    - Automatic file creation by date (YYYY-MM-DD.log)
    - Compact log format with day and time
    - Automatic traceback capture when errors occur
    """

    def __init__(self, log_dir="logs", auto_traceback=True):
        """
        Initialize the DateLogger.
        
        Args:
            log_dir: Directory where log files will be stored
            auto_traceback: If True, automatically captures tracebacks for errors
        """
        self.log_dir = Path(log_dir)
        self.log_dir.mkdir(parents=True, exist_ok=True)
        self.auto_traceback = auto_traceback
        self.current_date = None
        self.current_file = None
        
    def load(self):
        self._ensure_correct_file()
        self.current_file.write("\n")

    def _get_log_file_path(self):
        """Get the log file path for today's date."""
        today = datetime.now().strftime("%Y-%m-%d")
        return self.log_dir / f"{today}.log"

    def _ensure_correct_file(self):
        """Ensure we're writing to today's log file."""
        today = datetime.now().strftime("%Y-%m-%d")
        
        # Check if date changed or file not open
        if self.current_date != today or self.current_file is None:
            # Close previous file if open
            if self.current_file is not None:
                self.current_file.close()
            
            # Open new file for today
            self.current_date = today
            log_path = self._get_log_file_path()
            self.current_file = open(log_path, "a", encoding="utf-8")\

    def _format_timestamp(self):
        """Format timestamp as Day HH:MM:SS"""
        now = datetime.now()
        day_name = now.strftime("%a")  # Mon, Tue, Wed, etc.
        time_str = now.strftime("%H:%M:%S")
        return f"{day_name} {time_str}"

    def _get_traceback(self):
        """Capture the current traceback if one exists."""
        exc_info = sys.exc_info()
        if exc_info[0] is not None:
            # Format the traceback
            tb_lines = traceback.format_exception(*exc_info)
            return "".join(tb_lines).strip()
        return None

    def log(self, message, level="INFO", include_traceback=None):
        """
        Log a message to today's log file.
        
        Args:
            message: The message to log
            level: Log level (INFO, WARNING, ERROR, DEBUG, etc.)
            include_traceback: Override auto_traceback setting for this log
        """
        self._ensure_correct_file()
        
        timestamp = self._format_timestamp()
        log_line = f"[{timestamp}] {level:8} | {message}\n"
        
        self.current_file.write(log_line)
        
        # Check if we should include traceback
        should_traceback = include_traceback if include_traceback is not None else self.auto_traceback
        
        if should_traceback and level in ("ERROR", "CRITICAL"):
            tb = self._get_traceback()
            if tb:
                # Indent traceback for readability
                indented_tb = "\n".join(f"    {line}" for line in tb.split("\n"))
                self.current_file.write(f"    Traceback:\n{indented_tb}\n")
        
        self.current_file.flush()  # Ensure it's written immediately

    def info(self, message):
        """Log an INFO level message."""
        self.log(message, level="INFO")

    def warning(self, message):
        """Log a WARNING level message."""
        self.log(message, level="WARNING")

    def error(self, message, include_traceback=True):
        """Log an ERROR level message with optional traceback."""
        self.log(message, level="ERROR", include_traceback=include_traceback)

    def debug(self, message):
        """Log a DEBUG level message."""
        self.log(message, level="DEBUG")

    def critical(self, message, include_traceback=True):
        """Log a CRITICAL level message with optional traceback."""
        self.log(message, level="CRITICAL", include_traceback=include_traceback)

    def close(self):
        """Close the current log file."""
        if self.current_file is not None:
            self.current_file.close()
            self.current_file = None

    def __del__(self):
        """Ensure file is closed when logger is destroyed."""
        self.close()

    def __enter__(self):
        """Context manager support."""
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        """Context manager support - close file on exit."""
        self.close()
        return False
	
import re
import json
import ast

# Regex helpers (kept somewhat conservative)
_RE_BOM = re.compile(r'^\ufeff')
_RE_JS_SINGLE_LINE_COMMENT = re.compile(r'//.*?(?=\n|$)')
_RE_JS_MULTI_LINE_COMMENT = re.compile(r'/\*.*?\*/', re.DOTALL)
_RE_TRAILING_COMMAS = re.compile(r',\s*(?=[}\]])')  # comma before } or ]
_RE_PY_NONE_TRUE_FALSE = re.compile(r'\b(None|True|False)\b')
_RE_UNQUOTED_KEYS = re.compile(r'(?P<prefix>[{,\s])(?P<key>[A-Za-z_][A-Za-z0-9_\-]*)\s*:(?=\s)')

def _replace_python_literals(match):
    v = match.group(1)
    if v == 'None': return 'null'
    if v == 'True': return 'true'
    if v == 'False': return 'false'
    return v

def sanitize_to_json_string(s: str) -> str:
    """Try to coerce common "almost JSON" strings into valid JSON text.
    Returns a JSON-compatible string (not parsed). Raises ValueError if impossible."""
    if not isinstance(s, str):
        return "{}"

    try:
        json.loads(s)
        return s
    except Exception:
        pass

    t = s.strip()

    t = _RE_BOM.sub('', t)

    t = _RE_JS_SINGLE_LINE_COMMENT.sub('', t)
    t = _RE_JS_MULTI_LINE_COMMENT.sub('', t)

    t = _RE_TRAILING_COMMAS.sub('', t)

    t = _RE_PY_NONE_TRUE_FALSE.sub(_replace_python_literals, t)

    def _quote_key(m):
        return f'{m.group("prefix")}"{m.group("key")}" :'
    t = _RE_UNQUOTED_KEYS.sub(lambda m: m.group("prefix") + '"' + m.group("key") + '":', t)

    t = re.sub(r"""'([^'\\]*(?:\\.[^'\\]*)*)'""", r'"\1"', t)

    # 8) Now try json.loads again
    try:
        json.loads(t)
        return t
    except Exception:
        pass

    try:
        py_obj = ast.literal_eval(t)
        return json.dumps(py_obj)
    except Exception as e:
        return s

def loads_flexible(s: str):
    """Return Python object parsed from s, using sanitization fallbacks."""
    js_text = sanitize_to_json_string(s)
    return json.loads(js_text)