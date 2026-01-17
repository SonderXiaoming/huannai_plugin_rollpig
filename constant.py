# 插件目录
from pathlib import Path


PLUGIN_DIR = Path(__file__).parent
RES_DIR = PLUGIN_DIR / "resource"
PIGINFO_PATH = RES_DIR / "pig.json"
PIG_HUB_PATH = RES_DIR / "pig_hub.json"
IMAGE_DIR = RES_DIR / "image"
TODAY_PATH = RES_DIR / "today.json"
