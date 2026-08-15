import os
from dotenv import load_dotenv

load_dotenv()

DISCORD_TOKEN = os.getenv("DISCORD_TOKEN", "")
BOT_PREFIX = os.getenv("BOT_PREFIX", "!")
GUILD_ID = os.getenv("GUILD_ID", "")
DEFAULT_TIMES = 1
MAX_TIMES = 50
BLAME_START_PRESET = "Raid started!"
BLAME_FINISH_PRESET = "Raid finished!"
THANKS_LINE = "thanks for using our bot."

_PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
ASSETS_DIR = os.getenv("ASSETS_DIR", os.path.join(_PROJECT_ROOT, "assets"))
DOWNLOADS_DIR = os.getenv("DOWNLOADS_DIR", os.path.join(_PROJECT_ROOT, "downloads"))
PRESET1_FILES_DIR = os.getenv("PRESET1_FILES_DIR", os.path.join(_PROJECT_ROOT, "preset1files"))
UNTHUGS_MESSAGE_FILE = os.path.join(ASSETS_DIR, "message.txt")
LOG_FILE = os.path.join(_PROJECT_ROOT, "logs", "bot.log")

FILES_PER_MESSAGE = int(os.getenv("FILES_PER_MESSAGE", "3") or "3")


def get_guild_ids() -> list[int] | None:
    if not GUILD_ID:
        return None
    try:
        return [int(g.strip()) for g in GUILD_ID.split(",") if g.strip()]
    except ValueError:
        return None
