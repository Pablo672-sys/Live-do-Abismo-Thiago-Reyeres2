from __future__ import annotations

import json
import math
import os
import re
import shutil
import subprocess
import sys
import threading
import unicodedata
import uuid
import wave
from pathlib import Path

from boneco_game.core.json_store import read_json
from boneco_game.core.settings import ASSETS_DIR, DEFAULT_AVATAR, LIVE_RUNTIME_CONFIG_FILE, PRIVATE_DIR, PROJECT_DIR, RUNS_DIR
from boneco_game.services.audio_timeline import analyze_audio_timeline, build_audio_timeline_payload, write_audio_timeline_json


def _default_voice_path() -> Path:
    configured = os.getenv("BONECO_TTS_VOICE_PATH", "").strip()
    if configured:
        return Path(configured).expanduser()
    candidates = (
        ASSETS_DIR / DEFAULT_AVATAR / "voz" / "VOZ_RAPIDA_MASCULINA.wav",
        ASSETS_DIR / DEFAULT_AVATAR / "Voz" / "VOZ_RAPIDA_MASCULINA.wav",
        ASSETS_DIR / "BONECO_MAPA_2D" / "voz" / "VOZ_RAPIDA_MASCULINA.wav",
    )
    return next((path for path in candidates if path.is_file()), candidates[0])


DEFAULT_VOICE = _default_voice_path()
XTTS_MODEL_NAME = "tts_models/multilingual/multi-dataset/xtts_v2"
PREPARED_AUDIO_DIR = RUNS_DIR / "prepared_audio"
TTS_ABBREVIATIONS_FILE = PRIVATE_DIR / "tts_abbreviations.json"
_XTTS_LOCK = threading.Lock()
_XTTS_MODEL: object | None = None
_TTS_ABBREVIATIONS_CACHE: dict[str, str] = {}
_TTS_ABBREVIATIONS_MTIME_NS = -1


def safe_tts_chunks(text: str, *, max_chars: int = 170) -> list[str]:
    clean = _prepare_tts_input(text)
    if not clean:
        return []
    return _split_tts_input(clean, max_chars=max_chars)


def synthesize_for_job(
    text: str,
    *,
    voice_path: Path = DEFAULT_VOICE,
    language: str = "pt",
    speed: float | None = None,
    pitch: float | None = None,
) -> dict[str, object]:
    if not voice_path.is_file():
        raise FileNotFoundError(
            f"Voz original do Boneco nao encontrada: {voice_path}. "
            "Confira BONECO_ASSETS_DIR, BONECO_TTS_VOICE_PATH e a pasta voz do avatar selecionado."
        )
    PREPARED_AUDIO_DIR.mkdir(parents=True, exist_ok=True)
    output = PREPARED_AUDIO_DIR / f"speech_{uuid.uuid4().hex}.wav"
    clean = _prepare_tts_input(text)
    chunks = _split_tts_input(clean, max_chars=_tts_safe_char_limit(language))
    resolved_speed, resolved_pitch = _resolve_voice_adjustments(speed=speed, pitch=pitch)
    needs_adjust = abs(resolved_speed - 1.0) >= 0.001 or abs(resolved_pitch) >= 0.001
    generated_output = output.with_name(f"{output.stem}_raw{output.suffix}") if needs_adjust else output

    if not chunks:
        _write_placeholder(generated_output, duration=0.35)
    elif len(chunks) == 1:
        _synthesize_chunk(chunks[0], generated_output, voice_path=voice_path, language=language)
    else:
        chunk_paths: list[Path] = []
        for index, chunk in enumerate(chunks):
            chunk_path = generated_output.with_name(f"{generated_output.stem}_part{index:02d}.wav")
            _synthesize_chunk(chunk, chunk_path, voice_path=voice_path, language=language)
            _trim_trailing_silence(chunk_path)
            chunk_paths.append(chunk_path)
        _concat_wavs(chunk_paths, generated_output)
        for chunk_path in chunk_paths:
            try:
                chunk_path.unlink()
            except OSError:
                pass

    if needs_adjust:
        _adjust_audio_if_needed(generated_output, output, speed=resolved_speed, pitch=resolved_pitch)
        try:
            generated_output.unlink()
        except OSError:
            pass
    _trim_trailing_silence(output)
    timeline_path = output.with_suffix(".json")
    micro_pause_max = _runtime_float("micro_pause_freeze_max", 0.35)
    try:
        timeline = write_audio_timeline_json(output, timeline_path, micro_pause_max=micro_pause_max)
    except Exception as exc:
        _write_tts_error(f"timeline_json {type(exc).__name__}: {exc} path={output}")
        timeline = analyze_audio_timeline(output, micro_pause_max=micro_pause_max)
    timeline_payload = build_audio_timeline_payload(output, timeline)
    return {
        "audio_path": str(output),
        "timeline_path": str(timeline_path),
        "timeline": timeline_payload,
        "chunks": chunks,
        "tts_input": clean,
        "voice_speed": resolved_speed,
        "voice_pitch": resolved_pitch,
    }


def _split_tts_input(text: str, *, max_chars: int) -> list[str]:
    clean = " ".join(str(text or "").split()).strip()
    if not clean:
        return []
    if len(clean) <= max_chars:
        return [clean]
    chunks: list[str] = []
    current = ""
    for sentence in _tts_sentence_candidates(clean):
        if not sentence:
            continue
        if len(sentence) > max_chars:
            if current:
                chunks.append(current.strip())
                current = ""
            chunks.extend(_split_long_tts_sentence(sentence, max_chars=max_chars))
            continue
        candidate = f"{current} {sentence}".strip()
        if current and len(candidate) > max_chars:
            chunks.append(current.strip())
            current = sentence
        else:
            current = candidate
    if current:
        chunks.append(current.strip())
    return [chunk for chunk in chunks if chunk]


def _tts_sentence_candidates(text: str) -> list[str]:
    # Depois da sanitizacao os pontos viram virgulas para evitar o XTTS falar
    # literalmente "ponto"; por isso a divisao considera virgulas.
    chunks = re.split(r"(?<=[,!?;:])\s+", text)
    if len(chunks) == 1:
        chunks = re.split(r"\s+(?=(?:e|mas|entao|então|porque|quando|depois)\b)", text, flags=re.IGNORECASE)
    return [chunk.strip(" ,;:") for chunk in chunks if chunk.strip(" ,;:")]


def _split_long_tts_sentence(sentence: str, *, max_chars: int) -> list[str]:
    words = sentence.split()
    parts: list[str] = []
    current = ""
    for word in words:
        if len(word) > max_chars:
            if current:
                parts.append(current.strip())
                current = ""
            parts.extend(word[index : index + max_chars] for index in range(0, len(word), max_chars))
            continue
        candidate = f"{current} {word}".strip() if current else word
        if len(candidate) > max_chars and current:
            parts.append(current.strip())
            current = word
        else:
            current = candidate
    if current:
        parts.append(current.strip())
    return parts


def _synthesize_chunk(text: str, output: Path, *, voice_path: Path, language: str) -> None:
    if os.getenv("BONECO_GAME_TTS_IN_PROCESS", "1").strip().lower() not in {"0", "false", "no", "off"}:
        if _synthesize_xtts_cached(text, output, voice_path=voice_path, language=language):
            _trim_trailing_silence(output)
            return

    script = PROJECT_DIR / "scripts" / "synthesize_xtts.py"
    python_bin = PROJECT_DIR / ".venv" / "bin" / "python"
    if not python_bin.exists():
        python_bin = Path(sys.executable)
    env = os.environ.copy()
    env.setdefault("NUMBA_CACHE_DIR", str(RUNS_DIR / "numba_cache"))
    env.setdefault("MPLCONFIGDIR", str(RUNS_DIR / "matplotlib"))
    env.setdefault("OMP_NUM_THREADS", os.getenv("BONECO_GAME_TTS_CPU_THREADS", "2"))
    env.setdefault("MKL_NUM_THREADS", os.getenv("BONECO_GAME_TTS_CPU_THREADS", "2"))
    env.setdefault("OPENBLAS_NUM_THREADS", os.getenv("BONECO_GAME_TTS_CPU_THREADS", "2"))
    timeout = max(20.0, float(os.getenv("BONECO_GAME_TTS_TIMEOUT", "90")))
    try:
        result = subprocess.run(
            [
                str(python_bin),
                str(script),
                "--text",
                text,
                "--output",
                str(output),
                "--voice",
                str(voice_path),
                "--language",
                language,
            ],
            cwd=str(PROJECT_DIR),
            env=env,
            capture_output=True,
            text=True,
            timeout=timeout,
            check=False,
        )
        if result.returncode == 0 and output.exists() and output.stat().st_size > 44:
            _trim_trailing_silence(output)
            return
        _write_tts_error(f"xtts rc={result.returncode} text={text[:160]} stderr={result.stderr[-1200:]}")
    except Exception as exc:
        _write_tts_error(f"xtts {type(exc).__name__}: {exc} text={text[:160]}")
    # O renderer deve receber somente a voz original sintetizada pelo XTTS.
    # Não substituir silenciosamente por uma voz genérica do Windows.
    error_message = f"tts_failed_xtts_original_voice text={text[:160]}"
    _write_tts_error(error_message)
    raise RuntimeError(error_message)


def _synthesize_xtts_cached(text: str, output_path: Path, *, language: str, voice_path: Path) -> bool:
    global _XTTS_MODEL
    try:
        import torch
        from TTS.api import TTS

        # XTTS v2 permanece como motor único: CUDA quando disponível, CPU caso contrário.
        use_cuda = torch.cuda.is_available()
        if not use_cuda:
            torch.set_num_threads(max(1, int(os.getenv("BONECO_GAME_TTS_CPU_THREADS", "2"))))
        device = "cuda" if use_cuda else "cpu"
        with _XTTS_LOCK:
            if _XTTS_MODEL is None:
                _XTTS_MODEL = TTS(model_name=XTTS_MODEL_NAME).to(device)
            _XTTS_MODEL.tts_to_file(
                text=unicodedata.normalize("NFC", text),
                speaker_wav=[str(voice_path)],
                language=language,
                file_path=str(output_path),
                split_sentences=True,
            )
        return output_path.exists() and output_path.stat().st_size > 44
    except Exception as exc:
        _write_tts_error(f"xtts_cached {type(exc).__name__}: {exc}")
        try:
            import torch

            if torch.cuda.is_available():
                torch.cuda.empty_cache()
                if hasattr(torch.cuda, "ipc_collect"):
                    torch.cuda.ipc_collect()
        except Exception:
            pass
        return False


def _prepare_tts_input(text: object) -> str:
    clean = " ".join(str(text or "").split()).strip()
    if not clean:
        return "Teste de áudio da live."
    clean = _normalize_unicode_digits_for_tts(clean)
    clean = _restore_common_pt_br_accents(clean)
    clean = _expand_pt_br_abbreviations(clean)
    clean = _neutralize_tts_abusive_tokens(clean)
    clean = re.sub(r"(?:\d[\s.,:_-]*){6,}", " número grande ", clean)
    clean = re.sub(r"\.{2,}|…+", ", ", clean)
    clean = re.sub(r"(?<!\d)\.(?!\d)", ",", clean)
    clean = re.sub(r"\s+([,!?;:])", r"\1", clean)
    clean = re.sub(r"([,!?;:]){2,}", r"\1", clean)
    clean = re.sub(r"\b(\d)(?:\s*\1){2,}\b", r"\1 repetido", clean)
    clean = re.sub(r"\d{4,}", _spell_long_number_for_tts, clean)
    clean = re.sub(r"\s+", " ", clean).strip(" ,;:")
    clean = _apply_pt_br_tts_pronunciation(clean)
    return clean or "Teste de áudio da live."


def _normalize_unicode_digits_for_tts(text: str) -> str:
    parts: list[str] = []
    for char in text:
        try:
            parts.append(str(unicodedata.digit(char)))
        except (TypeError, ValueError):
            parts.append(char)
    return "".join(parts)


def _restore_common_pt_br_accents(text: object) -> str:
    clean = unicodedata.normalize("NFC", str(text or ""))
    word_replacements = {
        "acao": "ação",
        "acoes": "ações",
        "agradeco": "agradeço",
        "alem": "além",
        "alguem": "alguém",
        "ate": "até",
        "atencao": "atenção",
        "audiencia": "audiência",
        "coracao": "coração",
        "criacao": "criação",
        "decisao": "decisão",
        "direcao": "direção",
        "emocao": "emoção",
        "explicacao": "explicação",
        "funcao": "função",
        "geracao": "geração",
        "historia": "história",
        "ja": "já",
        "ninguem": "ninguém",
        "nao": "não",
        "operacao": "operação",
        "participacao": "participação",
        "presenca": "presença",
        "producao": "produção",
        "reacao": "reação",
        "relacao": "relação",
        "sequencia": "sequência",
        "silencio": "silêncio",
        "situacao": "situação",
        "tambem": "também",
        "transmissao": "transmissão",
        "voce": "você",
        "voces": "vocês",
    }

    def replace_word(match: re.Match[str]) -> str:
        word = match.group(0)
        replacement = word_replacements.get(word.casefold())
        if not replacement:
            return word
        if word.isupper():
            return replacement.upper()
        if word[:1].isupper():
            return replacement[:1].upper() + replacement[1:]
        return replacement

    return re.sub(r"\b[A-Za-zÀ-ÿ]+\b", replace_word, clean)


def _neutralize_tts_abusive_tokens(text: str) -> str:
    clean = re.sub(r"([A-Za-zÀ-ÿ0-9])\1{5,}", r"\1 repetido", text)
    clean = re.sub(r"\b[A-Za-zÀ-ÿ0-9_]*\d[A-Za-zÀ-ÿ0-9_]{5,}\b", " código grande ", clean)
    clean = re.sub(r"\b[A-Za-zÀ-ÿ]{26,}\b", " texto grande ", clean)
    return clean


def _expand_pt_br_abbreviations(text: str) -> str:
    global _TTS_ABBREVIATIONS_CACHE, _TTS_ABBREVIATIONS_MTIME_NS
    try:
        mtime_ns = TTS_ABBREVIATIONS_FILE.stat().st_mtime_ns
    except OSError:
        return text
    if mtime_ns != _TTS_ABBREVIATIONS_MTIME_NS:
        try:
            raw = json.loads(TTS_ABBREVIATIONS_FILE.read_text(encoding="utf-8"))
            mapping = raw if isinstance(raw, dict) else {}
            _TTS_ABBREVIATIONS_CACHE = {
                str(key).casefold(): str(value).strip()
                for key, value in mapping.items()
                if str(key).strip() and str(value).strip()
            }
            _TTS_ABBREVIATIONS_MTIME_NS = mtime_ns
        except (OSError, json.JSONDecodeError):
            _TTS_ABBREVIATIONS_CACHE = {}
            _TTS_ABBREVIATIONS_MTIME_NS = mtime_ns
    if not _TTS_ABBREVIATIONS_CACHE:
        return text

    patterns = sorted(_TTS_ABBREVIATIONS_CACHE, key=len, reverse=True)
    expression = r"(?<![\wÀ-ÿ])(?:" + "|".join(re.escape(item) for item in patterns) + r")(?![\wÀ-ÿ])"

    def replace(match: re.Match[str]) -> str:
        original = match.group(0)
        replacement = _TTS_ABBREVIATIONS_CACHE.get(original.casefold(), original)
        if original.isupper() and replacement.isalpha():
            return replacement.upper()
        if original[:1].isupper() and replacement:
            return replacement[:1].upper() + replacement[1:]
        return replacement

    return re.sub(expression, replace, text, flags=re.IGNORECASE)


def _spell_long_number_for_tts(match: re.Match[str]) -> str:
    names = {
        "0": "zero",
        "1": "um",
        "2": "dois",
        "3": "três",
        "4": "quatro",
        "5": "cinco",
        "6": "seis",
        "7": "sete",
        "8": "oito",
        "9": "nove",
    }
    return " ".join(names.get(char, char) for char in match.group(0)[:8])


def _apply_pt_br_tts_pronunciation(text: str) -> str:
    clean = unicodedata.normalize("NFC", text)
    replacements = (
        (r"\bexpli", "espli"),
        (r"\bexplic", "esplic"),
        (r"\bexper", "esper"),
        (r"\bexped", "esped"),
        (r"\bexpos", "espos"),
        (r"\bexpress", "espress"),
        (r"\bexplo", "esplo"),
        (r"\bexpul", "espul"),
        (r"\bextra", "estra"),
        (r"\bextre", "estre"),
        (r"\bexter", "ester"),
        (r"\bexces", "esses"),
        (r"\bexce", "esse"),
        (r"\bexempl", "ezempl"),
        (r"\bexat", "ezat"),
        (r"\bexist", "ezist"),
        (r"\bexecut", "ezecut"),
        (r"\bexib", "ezib"),
        (r"\bexag", "ezag"),
        (r"\bexam", "ezam"),
    )
    for pattern, replacement in replacements:
        clean = re.sub(pattern, replacement, clean, flags=re.IGNORECASE)
    return clean.replace("Ç", "SS").replace("ç", "ss")


def _tts_safe_char_limit(language: str) -> int:
    default_limit = 190 if str(language or "pt").strip().lower().startswith("pt") else 220
    try:
        configured = int(float(os.getenv("BONECO_GAME_TTS_SAFE_CHAR_LIMIT", str(default_limit))))
    except (TypeError, ValueError):
        configured = default_limit
    return max(80, min(190, configured))


def _resolve_voice_adjustments(*, speed: float | None, pitch: float | None) -> tuple[float, float]:
    runtime = read_json(LIVE_RUNTIME_CONFIG_FILE, {})
    if not isinstance(runtime, dict):
        runtime = {}
    resolved_speed = _float_or_default(speed, _float_or_default(runtime.get("voice_speed"), 1.0))
    resolved_pitch = _float_or_default(pitch, _float_or_default(runtime.get("voice_pitch"), 0.0))
    return max(0.50, min(2.00, resolved_speed)), max(-2.0, min(2.0, resolved_pitch))


def _runtime_float(key: str, default: float) -> float:
    runtime = read_json(LIVE_RUNTIME_CONFIG_FILE, {})
    if not isinstance(runtime, dict):
        runtime = {}
    return _float_or_default(runtime.get(key), default)


def _float_or_default(value: object, default: float) -> float:
    try:
        return float(value)
    except (TypeError, ValueError):
        return float(default)
