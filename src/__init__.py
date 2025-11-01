import flet as ft
from pathlib import Path
from threading import Thread, Timer as ThreadTimer
from datetime import datetime
import os, json, re, uuid, copy, string, random, io, base64, hashlib, gc, time, traceback, sys
from rapidfuzz import process, fuzz
from PIL import Image, ImageEnhance
from typing import Callable, Optional
from enum import Enum

import pydash as pdash

import src.utill as utility

class ExplorerTypes(Enum):
    FILES = 0
    FOLDER = 1

VERSION = "1.1.0"

APP_NAME = "Item Builder / Json Editor"

NOT_A_SECRET = uuid.UUID("12345678-1234-5678-1234-567812345678")

BGCOLOR = "#161616"
BGCOLOR2 = ft.Colors.with_opacity(0.1, ft.Colors.BLACK)
BGCOLOR3 = ft.Colors.with_opacity(0.5, ft.Colors.BLACK)

THEME_COLOR = "#3d2016"

VALUE_TEXT_STYLE = ft.TextStyle(
	size = 17,
	weight = ft.FontWeight.W_500
)

LABEL_TEXT_STYLE = ft.TextStyle(
	size = 15,
	weight =ft.FontWeight.BOLD
)


#json keys (in order) to try and get as the name of Items in Items List from Group 
# ( the value of any of these keys can be a value like "name_of_thing" or "name-of-thing", "NamedThing" and will be converted to "Name Of Thing" or "Named Thing" )
ORDERED_KEYS_FOR_ITEM_NAME = ["name", "id", "key"]

#Internal Key for Tracking Templates
UUID_KEY = "___UUID___"

FILE_ICONS = {
    # Text / Documents
    ".txt": ft.Icons.DESCRIPTION,
    ".md": ft.Icons.DESCRIPTION,
    ".rtf": ft.Icons.DESCRIPTION,
    ".doc": ft.Icons.ARTICLE,
    ".docx": ft.Icons.ARTICLE,
    ".pdf": ft.Icons.PICTURE_AS_PDF,
    
    # Code / Scripts
    ".py": ft.Icons.CODE,
    ".js": ft.Icons.CODE,
    ".ts": ft.Icons.CODE,
    ".json": ft.Icons.SETTINGS,
    ".xml": ft.Icons.CODE,
    ".html": ft.Icons.HTML,
    ".css": ft.Icons.CSS,
    ".cpp": ft.Icons.CODE,
    ".h": ft.Icons.CODE,
    ".java": ft.Icons.CODE,
    ".cs": ft.Icons.CODE,
    ".kt": ft.Icons.CODE,
    
	".ini" : ft.Icons.SETTINGS,
    ".yaml" : ft.Icons.SETTINGS,

    # Data
    ".csv": ft.Icons.TABLE_CHART,
    ".xlsx": ft.Icons.TABLE_CHART,
    ".xls": ft.Icons.TABLE_CHART,
    ".db": ft.Icons.STORAGE,
    ".sqlite": ft.Icons.STORAGE,
    ".sql": ft.Icons.DATA_OBJECT,
    ".yaml": ft.Icons.DATA_OBJECT,
    ".yml": ft.Icons.DATA_OBJECT,
    
    # Images
    ".png": ft.Icons.IMAGE,
    ".jpg": ft.Icons.IMAGE,
    ".jpeg": ft.Icons.IMAGE,
    ".gif": ft.Icons.IMAGE,
    ".bmp": ft.Icons.IMAGE,
    ".svg": ft.Icons.IMAGE,
    ".webp": ft.Icons.IMAGE,

    # Audio
    ".mp3": ft.Icons.MUSIC_NOTE,
    ".wav": ft.Icons.MUSIC_NOTE,
    ".flac": ft.Icons.MUSIC_NOTE,
    ".ogg": ft.Icons.MUSIC_NOTE,
    ".m4a": ft.Icons.MUSIC_NOTE,

    # Video
    ".mp4": ft.Icons.MOVIE,
    ".avi": ft.Icons.MOVIE,
    ".mkv": ft.Icons.MOVIE,
    ".mov": ft.Icons.MOVIE,
    ".webm": ft.Icons.MOVIE,

    # Archives
    ".zip": ft.Icons.FOLDER_ZIP,
    ".rar": ft.Icons.FOLDER_ZIP,
    ".7z": ft.Icons.FOLDER_ZIP,
    ".tar": ft.Icons.FOLDER_ZIP,
    ".gz": ft.Icons.FOLDER_ZIP,

    # Executables / Binaries
    ".exe": ft.Icons.COMPUTER,
    ".bat": ft.Icons.TERMINAL,
    ".sh": ft.Icons.TERMINAL,
    ".apk": ft.Icons.ANDROID,
    ".app": ft.Icons.LAPTOP_MAC,
    ".bin": ft.Icons.MEMORY,

    # 3D / Models
    ".obj": ft.Icons.VIEW_IN_AR,
    ".fbx": ft.Icons.VIEW_IN_AR,
    ".glb": ft.Icons.VIEW_IN_AR,
    ".gltf": ft.Icons.VIEW_IN_AR,
    ".blend": ft.Icons.VIEW_IN_AR,

    # Fonts
    ".ttf": ft.Icons.FONT_DOWNLOAD,
    ".otf": ft.Icons.FONT_DOWNLOAD,
    ".woff": ft.Icons.FONT_DOWNLOAD,
    ".woff2": ft.Icons.FONT_DOWNLOAD,
    
	".url": ft.Icons.LINK,
    ".lnk": ft.Icons.LINK,
    ".desktop": ft.Icons.LINK,

    # Misc
    ".ini": ft.Icons.SETTINGS,
    ".cfg": ft.Icons.SETTINGS,
    ".log": ft.Icons.NOTE,
    ".bak": ft.Icons.BACKUP,
    ".iso": ft.Icons.DISC_FULL,
}