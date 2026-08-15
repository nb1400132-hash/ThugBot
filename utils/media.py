import os
import random
from pathlib import Path

import nextcord

from .config import ASSETS_DIR, DOWNLOADS_DIR, PRESET1_FILES_DIR, UNTHUGS_MESSAGE_FILE
from .logger import log

MEDIA_EXTS = {".gif", ".mp4", ".webp", ".png", ".jpg", ".jpeg", ".webm", ".mov"}

_msg_cache: str | None = None
_msg_loaded = False
_preset_cache: dict[str, str] = {}
_scan_cache: dict[str, tuple[list[str], float]] = {}


def _scan_files(folder_path: str) -> list[str]:
    folder = Path(folder_path).resolve()
    folder.mkdir(parents=True, exist_ok=True)
    try:
        current_mtime = folder.stat().st_mtime
    except OSError:
        current_mtime = 0.0
    cached = _scan_cache.get(str(folder))
    if cached is not None and cached[1] == current_mtime:
        return cached[0]
    out: list[str] = []
    try:
        for entry in os.scandir(folder):
            if not entry.is_file():
                continue
            if entry.name.startswith("."):
                continue
            if Path(entry.name).suffix.lower() not in MEDIA_EXTS:
                continue
            out.append(entry.path)
    except OSError as e:
        log.warning(f"could not scan {folder}: {e}")
        out = []
    _scan_cache[str(folder)] = (out, current_mtime)
    if not out:
        log.warning(f"no media files found in {folder}")
    else:
        log.info(f"found {len(out)} files in {folder.name}")
    return out


def _pick(folder_path: str, n: int) -> list[nextcord.File]:
    files = _scan_files(folder_path)
    if not files:
        return []
    if len(files) >= n:
        chosen = random.sample(files, n)
    else:
        chosen = random.choices(files, k=n)
    out: list[nextcord.File] = []
    for p in chosen:
        try:
            out.append(nextcord.File(p))
        except Exception as e:
            log.warning(f"could not open {p}: {e}")
    return out


def pick_random_files(n: int = 3) -> list[nextcord.File]:
    return _pick(DOWNLOADS_DIR, n)


def pick_preset1_files(n: int = 3) -> list[nextcord.File]:
    return _pick(PRESET1_FILES_DIR, n)


def load_unthugs_message() -> str:
    global _msg_cache, _msg_loaded
    if _msg_loaded:
        return _msg_cache or "nah we don't do that no more. gang gang."
    _msg_loaded = True
    path = Path(UNTHUGS_MESSAGE_FILE).resolve()
    if not path.exists():
        log.warning(f"message.txt missing at {path}, using default")
        _msg_cache = "nah we don't do that no more. gang gang."
        return _msg_cache
    _msg_cache = path.read_text(encoding="utf-8").strip()
    log.info(f"loaded unthugs message from {path.name}: {_msg_cache[:40]}...")
    return _msg_cache


def load_preset_message(filename: str) -> str:
    if filename in _preset_cache:
        return _preset_cache[filename]
    path = Path(ASSETS_DIR).resolve() / filename
    if not path.exists():
        log.warning(f"{filename} missing at {path}, using default")
        return f"[{filename} not found]"
    content = path.read_text(encoding="utf-8").strip()
    _preset_cache[filename] = content
    log.info(f"loaded {len(content)} chars from {filename}")
    return content
