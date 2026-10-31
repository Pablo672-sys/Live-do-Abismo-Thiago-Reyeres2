from __future__ import annotations

import os
from pathlib import Path


def _env_first(*names: str, default: str) -> str:
    """Return the first non-empty environment variable from the supported aliases."""
    for name in names:
        value = os.getenv(name)
        if value and value.strip():
            return value.strip()
    return default


def _env_path(*names: str, default: Path) -> Path:
    return Path(_env_first(*names, default=str(default))).expanduser()


PROJECT_DIR = _env_path(
    "BONECO_GAME_DIR",
    default=Path("/media/allana/Dados240/BONECO_GAME"),
)
# Keep the external reference project separate from the active game directory.
REFERENCE_PROJECT_DIR = _env_path(
    "BONECO_REFERENCE_PROJECT_DIR",
    default=PROJECT_DIR,
)
# The published .env.example uses BONECO_ASSETS_DIR; older deployments may use
# BONECO_GAME_ASSETS_DIR. Support both so the original avatar/voice assets are found.
ASSETS_DIR = _env_path(
    "BONECO_GAME_ASSETS_DIR",
    "BONECO_ASSETS_DIR",
    default=PROJECT_DIR / "assets",
)
PRIVATE_DIR = PROJECT_DIR / "private"
RUNS_DIR = _env_path(
    "BONECO_GAME_RUNTIME_DIR",
    "BONECO_RUNTIME_DIR",
    default=PROJECT_DIR / "runs",
)
LOGS_DIR = PROJECT_DIR / "logs"
TEMPLATES_DIR = PROJECT_DIR / "src" / "boneco_game" / "templates"
STATIC_DIR = PROJECT_DIR / "src" / "boneco_game" / "static"

DEFAULT_AVATAR = _env_first("BONECO_GAME_AVATAR", "BONECO_DEFAULT_AVATAR", default="BONECO_MAPA_2D")
DEFAULT_MAP = os.getenv("BONECO_GAME_MAP", "Padrao")
DEFAULT_HOST = _env_first("BONECO_GAME_HOST", "BONECO_HOST", default="127.0.0.1")
DEFAULT_PORT = int(_env_first("BONECO_GAME_PORT", "BONECO_PORT", default="9292"))
DEFAULT_WIDTH = int(_env_first("BONECO_GAME_WIDTH", "BONECO_STREAM_WIDTH", default="720"))
DEFAULT_HEIGHT = int(_env_first("BONECO_GAME_HEIGHT", "BONECO_STREAM_HEIGHT", default="1280"))
DEFAULT_STREAM_DISPLAY = _env_first("BONECO_GAME_STREAM_DISPLAY", "BONECO_STREAM_DISPLAY", default=":98")
DEFAULT_STREAM_FPS = int(_env_first("BONECO_GAME_STREAM_FPS", "BONECO_STREAM_FPS", default="30"))
DEFAULT_STREAM_BITRATE = int(_env_first("BONECO_GAME_STREAM_BITRATE", "BONECO_STREAM_BITRATE", default="2500"))
DEFAULT_STREAM_AUDIO_SOURCE = _env_first(
    "BONECO_GAME_STREAM_AUDIO_SOURCE",
    "BONECO_STREAM_AUDIO_SOURCE",
    default="default",
)

STREAMLABS_CONFIG_FILE = PRIVATE_DIR / "streamlabs_tiktok.json"
LIVE_AI_CONFIG_FILE = PRIVATE_DIR / "live_text_ai.json"
LIVE_RUNTIME_CONFIG_FILE = PRIVATE_DIR / "live_runtime.json"
LIVE_CONTROL_CONFIG_FILE = PRIVATE_DIR / "live_control.json"
BLACKLIST_FILE = PRIVATE_DIR / "chat_blacklist_terms.txt"
MONITOR_START_SCRIPT = PROJECT_DIR / "scripts" / "start_tiktok_monitor.sh"
MONITOR_NETWORK_FILE = RUNS_DIR / "monitor_network.json"
MONITOR_STATUS_FILE = RUNS_DIR / "monitor_status.json"


def ensure_runtime_dirs() -> None:
    for path in (ASSETS_DIR, PRIVATE_DIR, RUNS_DIR, LOGS_DIR):
        path.mkdir(parents=True, exist_ok=True)
