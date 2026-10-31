from __future__ import annotations

from pathlib import Path

from fastapi import APIRouter, Request
from fastapi.responses import FileResponse, HTMLResponse, JSONResponse
from fastapi.templating import Jinja2Templates

from boneco_game.core.settings import ASSETS_DIR, PROJECT_DIR, TEMPLATES_DIR
from boneco_game.services.runtime_state import read_state, renderer_state
from boneco_game.services.media_library import avatar_dir, list_avatar_videos
from boneco_game.services.tts_service import DEFAULT_VOICE
from boneco_game.core.json_store import read_json
from boneco_game.core.settings import RUNS_DIR
from boneco_game.services.speech_queue import pop_next


router = APIRouter()
templates = Jinja2Templates(directory=str(TEMPLATES_DIR))


@router.get("/renderer", response_class=HTMLResponse)
def renderer(request: Request) -> HTMLResponse:
    return templates.TemplateResponse("renderer.html", {"request": request})


@router.get("/api/renderer/state", response_class=JSONResponse)
def api_renderer_state() -> JSONResponse:
    return JSONResponse(renderer_state())


@router.get("/api/renderer/next-speech", response_class=JSONResponse)
def api_next_speech() -> JSONResponse:
    job = pop_next()
    return JSONResponse({"job": job})

@router.get("/api/renderer/diagnostics", response_class=JSONResponse)
def api_renderer_diagnostics() -> JSONResponse:
    state = read_state()
    avatar = str(state.get("avatar") or "")
    root = avatar_dir(avatar)
    media = {
        "Mudo": list_avatar_videos(avatar, "Mudo"),
        "Dancando": list_avatar_videos(avatar, "Dancando"),
        "Falando": list_avatar_videos(avatar, "Falando"),
    }
    worker = read_json(RUNS_DIR / "tts_worker_status.json", {"state": "unknown"})
    return JSONResponse({
        "avatar": avatar,
        "assets_directory_exists": root.is_dir(),
        "media": {
            name: {"count": len(paths), "files": [path.name for path in paths[:30]]}
            for name, paths in media.items()
        },
        "voice": {"exists": DEFAULT_VOICE.is_file(), "filename": DEFAULT_VOICE.name},
        "tts_worker": worker,
    })


@router.get("/file")
def file_response(path: str) -> FileResponse:
    raw = Path(path)
    if not raw.is_absolute():
        raw = PROJECT_DIR / raw
    resolved = raw.resolve()
    allowed_roots = [PROJECT_DIR.resolve(), ASSETS_DIR.resolve()]
    if not any(str(resolved).startswith(str(root)) for root in allowed_roots):
        raise FileNotFoundError("Arquivo fora do projeto.")
    return FileResponse(
        str(resolved),
        headers={
            "Cache-Control": "no-store, no-cache, must-revalidate, max-age=0",
            "Pragma": "no-cache",
            "Expires": "0",
        },
    )
