from __future__ import annotations

import io
import json
import os
import shutil
import subprocess
import tempfile
import threading
import time
import urllib.request
import zipfile
from pathlib import Path, PurePosixPath
from typing import Any

from boneco_game.core.settings import PROJECT_DIR, RUNS_DIR

REMOTE = "origin"
BRANCH = "main"
REPO = "Pablo672-sys/Live-do-Abismo-Thiago-Reyeres2"
RESTART_SCRIPT = PROJECT_DIR / "scripts" / "start_clean_panel.sh"
WINDOWS_RESTART_SCRIPT = PROJECT_DIR / "Windows_instalar" / "REINICIAR.bat"
UPDATE_LOG = RUNS_DIR / "system_update.log"
ZIP_MARKER = RUNS_DIR / "zip_update_commit.txt"
_LOCK = threading.Lock()
_API_URL = f"https://api.github.com/repos/{REPO}/commits/{BRANCH}"
_ZIP_URL = f"https://github.com/{REPO}/archive/refs/heads/{BRANCH}.zip"
_PROTECTED_TOP_LEVEL = {".git", ".venv", "assets", "private", "runs", "logs", "config", "__pycache__"}
_PROTECTED_FILES = {".env", ".env.local", ".env.production"}


def _remote_info(timeout: float = 20) -> tuple[str, str]:
    request = urllib.request.Request(_API_URL, headers={"User-Agent": "Boneco-do-Abismo-Updater", "Accept": "application/vnd.github+json"})
    with urllib.request.urlopen(request, timeout=timeout) as response:
        payload = json.loads(response.read().decode("utf-8"))
    sha = str(payload.get("sha") or "")
    message = str((payload.get("commit") or {}).get("message") or "").splitlines()[0]
    if len(sha) != 40:
        raise RuntimeError("O GitHub não retornou um identificador de versão válido.")
    return sha, message


def status(*, fetch: bool = False) -> dict[str, Any]:
    RUNS_DIR.mkdir(parents=True, exist_ok=True)
    if (PROJECT_DIR / ".git").is_dir():
        return _git_status(fetch=fetch)
    result: dict[str, Any] = {
        "ok": True, "project_dir": str(PROJECT_DIR), "remote": REPO,
        "branch": BRANCH, "update_mode": "zip", "fetch_attempted": bool(fetch),
        "fetch_ok": None, "fetch_error": "", "dirty": False, "dirty_files": [],
        "ahead": 0, "behind": 0, "changed_files": [],
        "restart_available": True,
    }
    if not fetch:
        marker = ZIP_MARKER.read_text(encoding="utf-8").strip() if ZIP_MARKER.is_file() else ""
        result.update({"local_sha": marker, "local_short": marker[:8], "remote_sha": "", "remote_short": "", "update_available": False, "can_update": False})
        return result
    try:
        remote_sha, message = _remote_info()
        local_sha = ZIP_MARKER.read_text(encoding="utf-8").strip() if ZIP_MARKER.is_file() else ""
        available = not local_sha or local_sha != remote_sha
        result.update({
            "fetch_ok": True, "local_sha": local_sha, "local_short": local_sha[:8],
            "remote_sha": remote_sha, "remote_short": remote_sha[:8],
            "update_available": available, "can_update": available,
            "behind": 1 if available else 0, "changed_files": [message] if message else [],
            "message": "Instalação por ZIP: arquivos pessoais serão preservados.",
        })
        return result
    except Exception as exc:
        return {**result, "ok": False, "fetch_ok": False, "fetch_error": str(exc), "error": f"Não consegui consultar o GitHub: {exc}", "update_available": False, "can_update": False}


def update() -> dict[str, Any]:
    with _LOCK:
        if not (PROJECT_DIR / ".git").is_dir():
            return _update_zip()
        before = status(fetch=True)
        if not before.get("ok"):
            return before
        if before.get("branch") != BRANCH:
            return {**before, "ok": False, "error": f"Branch atual é {before.get('branch')!r}; atualização automática só é permitida na {BRANCH!r}."}
        if before.get("dirty"):
            return {**before, "ok": False, "error": "Existem alterações locais. Faça backup/commit das alterações antes de atualizar."}
        if int(before.get("ahead") or 0) > 0:
            return {**before, "ok": False, "error": "A cópia local possui commits que ainda não estão no GitHub. Envie-os antes de atualizar."}
        if not before.get("update_available"):
            return {**before, "ok": True, "updated": False, "message": "O sistema já está atualizado.", "restart_required": False}
        pulled = _git(["pull", "--ff-only", REMOTE, BRANCH], timeout=120)
        _append_log(f"[{time.strftime('%F %T')}] git pull --ff-only {REMOTE} {BRANCH}\n{pulled['stdout']}\n{pulled['stderr']}\n")
        if pulled["returncode"] != 0:
            return {**before, "ok": False, "updated": False, "error": pulled["stderr"] or pulled["stdout"] or "Falha ao atualizar o sistema."}
        after = status(fetch=False)
        return {**after, "ok": True, "updated": True, "message": "Atualização baixada. Reinicie o sistema para carregar o novo código.", "restart_required": True, "pull_output": (pulled["stdout"] or pulled["stderr"])[-6000:]}


def _update_zip() -> dict[str, Any]:
    before = status(fetch=True)
    if not before.get("ok"):
        return before
    if not before.get("update_available"):
        return {**before, "ok": True, "updated": False, "message": "O sistema já está atualizado.", "restart_required": False}
    remote_sha = str(before.get("remote_sha") or "")
    temp_path = ""
    try:
        request = urllib.request.Request(_ZIP_URL, headers={"User-Agent": "Boneco-do-Abismo-Updater"})
        with urllib.request.urlopen(request, timeout=90) as response:
            archive_bytes = response.read()
        with zipfile.ZipFile(io.BytesIO(archive_bytes)) as archive:
            members = archive.infolist()
            roots = {PurePosixPath(item.filename).parts[0] for item in members if PurePosixPath(item.filename).parts}
            if len(roots) != 1:
                raise RuntimeError("O pacote de atualização tem uma estrutura inesperada.")
            root = next(iter(roots))
            staged = Path(tempfile.mkdtemp(prefix="boneco-update-"))
            temp_path = str(staged)
            for item in members:
                member = PurePosixPath(item.filename)
                if len(member.parts) < 2 or member.parts[0] != root or item.is_dir():
                    continue
                relative = PurePosixPath(*member.parts[1:])
                if not relative.parts or relative.parts[0] in _PROTECTED_TOP_LEVEL or relative.name in _PROTECTED_FILES:
                    continue
                if any(part in {"..", ""} for part in relative.parts) or relative.is_absolute():
                    continue
                target = staged.joinpath(*relative.parts)
                target.parent.mkdir(parents=True, exist_ok=True)
                with archive.open(item) as source, target.open("wb") as destination:
                    shutil.copyfileobj(source, destination)
        # A extração é validada e feita numa área temporária; arquivos pessoais ficam intocados.
        for source in staged.rglob("*"):
            if not source.is_file():
                continue
            relative = source.relative_to(staged)
            destination = PROJECT_DIR / relative
            destination.parent.mkdir(parents=True, exist_ok=True)
            shutil.copy2(source, destination)
        ZIP_MARKER.write_text(remote_sha + "\n", encoding="utf-8")
        _append_log(f"[{time.strftime('%F %T')}] ZIP update installed commit={remote_sha}\n")
        after = status(fetch=False)
        after.update({"ok": True, "updated": True, "message": "Atualização baixada com segurança. Feche e abra novamente o Boneco para carregar o código novo.", "restart_required": True, "update_mode": "zip"})
        return after
    except Exception as exc:
        _append_log(f"[{time.strftime('%F %T')}] ZIP update failed: {type(exc).__name__}: {exc}\n")
        return {**before, "ok": False, "updated": False, "error": f"Falha ao instalar atualização: {exc}. Nenhum arquivo pessoal foi removido.", "restart_required": False}
    finally:
        if temp_path:
            shutil.rmtree(temp_path, ignore_errors=True)


def schedule_restart(delay_seconds: float = 1.2) -> dict[str, Any]:
    if os.name == "nt":
        try:
            script = r"""
@echo off
timeout /t 2 /nobreak >nul
powershell -NoProfile -ExecutionPolicy Bypass -Command "$p=Get-NetTCPConnection -LocalPort 9292 -State Listen -ErrorAction SilentlyContinue | Select-Object -First 1 -ExpandProperty OwningProcess; if ($p) { $proc=Get-CimInstance Win32_Process -Filter ('ProcessId=' + $p) -ErrorAction SilentlyContinue; if ($proc -and $proc.CommandLine -match 'uvicorn.*boneco_game.main:app') { Stop-Process -Id $p -Force -ErrorAction SilentlyContinue } }"
timeout /t 2 /nobreak >nul
powershell -NoProfile -ExecutionPolicy Bypass -File "%~dp0..\start_boneco_windows.ps1"
"""
            WINDOWS_RESTART_SCRIPT.parent.mkdir(parents=True, exist_ok=True)
            WINDOWS_RESTART_SCRIPT.write_text(script, encoding="utf-8")
            subprocess.Popen(["cmd.exe", "/c", str(WINDOWS_RESTART_SCRIPT)], cwd=str(PROJECT_DIR), stdin=subprocess.DEVNULL, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL, creationflags=getattr(subprocess, "CREATE_NEW_PROCESS_GROUP", 0) | getattr(subprocess, "DETACHED_PROCESS", 0))
            return {"ok": True, "scheduled": True, "message": "Reinicialização do Windows agendada."}
        except OSError as exc:
            return {"ok": False, "error": f"Não foi possível agendar a reinicialização: {exc}"}
    if not RESTART_SCRIPT.is_file():
        return {"ok": False, "error": f"Script de reinicialização não encontrado: {RESTART_SCRIPT}"}
    launcher = f'sleep {max(0.5, float(delay_seconds)):.2f}; exec "{RESTART_SCRIPT}" >> "{UPDATE_LOG}" 2>&1'
    env = os.environ.copy()
    env["BONECO_GAME_DIR"] = str(PROJECT_DIR)
    try:
        subprocess.Popen(["bash", "-lc", launcher], cwd=str(PROJECT_DIR), env=env, stdin=subprocess.DEVNULL, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL, start_new_session=True)
    except OSError as exc:
        return {"ok": False, "error": f"Não foi possível agendar a reinicialização: {exc}"}
    return {"ok": True, "scheduled": True, "message": "Reinicialização agendada."}


def _git_status(*, fetch: bool) -> dict[str, Any]:
    result: dict[str, Any] = {"ok": True, "project_dir": str(PROJECT_DIR), "remote": REMOTE, "branch": BRANCH, "update_mode": "git", "fetch_attempted": bool(fetch), "fetch_ok": None, "fetch_error": ""}
    if fetch:
        fetched = _git(["fetch", "--prune", REMOTE, BRANCH], timeout=45)
        result["fetch_ok"] = fetched["returncode"] == 0
        result["fetch_error"] = fetched["stderr"] if fetched["returncode"] else ""
        if fetched["returncode"] != 0:
            return {**result, "ok": False, "error": fetched["stderr"] or "Falha ao consultar o GitHub."}
    local_sha = _git_text(["rev-parse", "HEAD"])
    remote_sha = _git_text(["rev-parse", f"{REMOTE}/{BRANCH}"])
    branch = _git_text(["branch", "--show-current"]) or BRANCH
    dirty_lines = _git_lines(["status", "--porcelain=v1", "--untracked-files=all"])
    ahead = behind = 0
    if local_sha and remote_sha:
        counts = _git_text(["rev-list", "--left-right", "--count", f"HEAD...{REMOTE}/{BRANCH}"]).split()
        if len(counts) >= 2:
            try:
                ahead, behind = int(counts[0]), int(counts[1])
            except ValueError:
                pass
    changed_files = _git_lines(["diff", "--name-only", f"HEAD..{REMOTE}/{BRANCH}"]) if behind > 0 else []
    return {**result, "branch": branch, "local_sha": local_sha, "local_short": local_sha[:8] if local_sha else "", "remote_sha": remote_sha, "remote_short": remote_sha[:8] if remote_sha else "", "ahead": ahead, "behind": behind, "update_available": behind > 0, "dirty": bool(dirty_lines), "dirty_files": dirty_lines[:80], "changed_files": changed_files[:120], "can_update": behind > 0 and not dirty_lines and ahead == 0 and branch == BRANCH, "restart_available": RESTART_SCRIPT.is_file() or os.name == "nt"}


def _git(args: list[str], *, timeout: float = 30) -> dict[str, Any]:
    try:
        proc = subprocess.run(["git", *args], cwd=str(PROJECT_DIR), capture_output=True, text=True, timeout=max(3.0, timeout), check=False)
        return {"returncode": proc.returncode, "stdout": (proc.stdout or "").strip(), "stderr": (proc.stderr or "").strip()}
    except subprocess.TimeoutExpired:
        return {"returncode": 124, "stdout": "", "stderr": "Tempo limite excedido."}
    except OSError as exc:
        return {"returncode": 127, "stdout": "", "stderr": str(exc)}


def _git_text(args: list[str]) -> str:
    result = _git(args)
    return result["stdout"] if result["returncode"] == 0 else ""


def _git_lines(args: list[str]) -> list[str]:
    return [line.strip() for line in _git_text(args).splitlines() if line.strip()]


def _append_log(text: str) -> None:
    try:
        RUNS_DIR.mkdir(parents=True, exist_ok=True)
        with UPDATE_LOG.open("a", encoding="utf-8") as handle:
            handle.write(text.rstrip() + "\n")
    except OSError:
        pass
