"""
Speech for ag-footage: Doubao file ASR 2.0 with word timestamps and speaker labels, through Artistic Genius
(the gateway's doubao-asr routes: submit an mp3, poll the task). Config from the environment or scripts/.env:

    AG_OMNI_KEY   an Artistic Genius token of the Omni 创作优选 group; without it the transcript is skipped
"""

from __future__ import annotations

import json
import subprocess
import sys
import threading
import time
import uuid
from concurrent.futures import ThreadPoolExecutor

from client import FootageError, ag_root, omni_key, post, tagged

ASR_MODEL = "doubao-seedasr-auc"
# Speaker diarization changes the text (fewer, merged utterances; 100 → 一百), so it runs as a second pass.
ASR_PASS_TEXT = {"enable_itn": True, "enable_punc": True, "show_speech_rate": True,
                 "enable_emotion_detection": True, "enable_gender_detection": True}
ASR_PASS_SPEAKER = {"enable_itn": True, "enable_punc": True, "enable_speaker_info": True,
                    "ssd_version": "200"}  # 200 separated 5 speakers where 300 merged them into 3
ASR_MAX_SEC = 3600  # the gateway bills recognition by the second, up to one hour a job
ASR_POLL_SEC = 2
ASR_WAIT_PER_AUDIO_SEC = 0.3  # measured ≈0.09s per audio second; 3× margin for queueing
REQUEST_TIMEOUT = 600
_jobs = threading.BoundedSemaphore(6)  # recognition jobs in flight: what six clips at once ran before the two
                                       # passes of a clip ran side by side


class SpeechError(RuntimeError):
    pass


def log(msg: str) -> None:
    print(f"[ag-footage] {msg}", file=sys.stderr, flush=True)


def find_key() -> str:
    return omni_key()


def _gateway(method: str, path: str, body=None, content_type: str | None = None) -> dict:
    """One call to the gateway's doubao-asr routes (client.post: retries on 429/5xx/network errors)."""
    headers = {"Authorization": f"Bearer {find_key()}", **({"Content-Type": content_type} if content_type else {})}
    try:
        _, data = post(f"{ag_root()}/doubao-asr/v1/{path}", headers, body, REQUEST_TIMEOUT, method=method)
    except FootageError as e:
        raise SpeechError(f"ASR: {e}") from e
    return data


def _multipart(fields: dict, mp3: bytes) -> tuple[bytes, str]:
    """multipart/form-data: the text fields, then the audio as file field `audio`."""
    boundary = uuid.uuid4().hex
    parts = [f'--{boundary}\r\nContent-Disposition: form-data; name="{k}"\r\n\r\n{v}\r\n'.encode("utf-8") for k, v in fields.items()]
    parts.append(f'--{boundary}\r\nContent-Disposition: form-data; name="audio"; filename="audio.mp3"\r\n'
                 f'Content-Type: audio/mpeg\r\n\r\n'.encode("utf-8") + mp3 + f"\r\n--{boundary}--\r\n".encode("utf-8"))
    return b"".join(parts), f"multipart/form-data; boundary={boundary}"


def _run(cmd: list, timeout: float) -> subprocess.CompletedProcess:
    try:
        return subprocess.run(cmd, capture_output=True, timeout=timeout)
    except FileNotFoundError as e:
        raise SpeechError(f"{cmd[0]} not found on PATH (install ffmpeg)") from e
    except subprocess.TimeoutExpired as e:
        raise SpeechError(f"{cmd[0]} exceeded {timeout:g}s") from e


def probe_duration(path: str) -> float:
    proc = _run(["ffprobe", "-v", "error", "-show_entries", "format=duration", "-of", "json", path], 60)
    try:
        return float(json.loads(proc.stdout or b"{}")["format"]["duration"])
    except (KeyError, TypeError, ValueError):
        raise SpeechError(f"ffprobe cannot read an audio duration from {path}")


def encode_mp3(path: str, duration: float) -> bytes:
    proc = _run(["ffmpeg", "-hide_banner", "-loglevel", "error", "-ss", "0", "-t", f"{duration:.3f}",
                 "-i", path, "-vn", "-ac", "1", "-ar", "16000", "-c:a", "libmp3lame", "-b:a", "64k",
                 "-f", "mp3", "pipe:1"], 900)
    if proc.returncode != 0 or not proc.stdout:
        raise SpeechError(f"ffmpeg could not decode audio: {proc.stderr.decode(errors='replace')[:300]}")
    return proc.stdout


def _asr_pass(mp3: bytes, options: dict, duration: float) -> list[dict]:
    """Submit one recognition job and poll until done. Returns raw utterances ([] for silence)."""
    with _jobs:
        body, content_type = _multipart({"duration": f"{duration:.3f}", "format": "mp3",
                                         "request": json.dumps(options)}, mp3)
        task_id = _gateway("POST", "submit", body, content_type).get("task_id")
        if not task_id:
            raise SpeechError("ASR submit returned no task id")
        wait = max(REQUEST_TIMEOUT, duration * ASR_WAIT_PER_AUDIO_SEC)
        deadline = time.monotonic() + wait
        while True:
            time.sleep(ASR_POLL_SEC)
            data = _gateway("GET", f"query/{task_id}")
            if data.get("status") == "SUCCESS":  # silence comes back as a result without utterances
                return ((data.get("result") or {}).get("result") or {}).get("utterances") or []
            if data.get("status") == "FAILURE":
                raise SpeechError(f"ASR failed: {data.get('fail_reason') or 'unknown'}")
            if time.monotonic() > deadline:
                raise SpeechError(f"ASR job not finished within {wait:.0f}s")


def _utterance(u: dict) -> dict:
    extra = u.get("additions") or {}
    out = {"start": u["start_time"] / 1000, "end": u["end_time"] / 1000, "text": u.get("text", "").strip()}
    if extra.get("speaker"):
        out["speaker"] = extra["speaker"]
    for k in ("emotion", "gender"):
        if extra.get(k):
            out[k] = extra[k]
    if extra.get("speech_rate"):
        out["speech_rate"] = round(float(extra["speech_rate"]), 2)
    # start_time -1 marks placeholder spaces between Chinese and Latin words.
    out["words"] = [{"start": w["start_time"] / 1000, "end": w["end_time"] / 1000, "text": w["text"]}
                    for w in u.get("words") or [] if w.get("start_time", -1) >= 0]
    return out


def _overlap(a: dict, b: dict) -> float:
    return max(0.0, min(a["end"], b["end"]) - max(a["start"], b["start"]))


def transcribe(path: str) -> dict:
    """Two passes side by side: text + word times, and speaker labels mapped on by time overlap."""
    if not find_key():
        raise SpeechError("AG_OMNI_KEY is not set (environment or scripts/.env): an Artistic Genius token of the "
                          "Omni 创作优选 group; transcript skipped")
    duration = probe_duration(path)
    if duration > ASR_MAX_SEC:
        raise SpeechError(f"Audio longer than {ASR_MAX_SEC // 60} minutes: cut the clip into shorter files; transcript skipped")
    mp3 = encode_mp3(path, duration)
    log(f"asr: text + word timestamps, and speaker labels ({duration:.0f}s)…")
    with ThreadPoolExecutor(2) as ex:
        utts, labelled = ([_utterance(u) for u in raw] for raw in
                          ex.map(tagged(lambda options: _asr_pass(mp3, options, duration)),
                                 (ASR_PASS_TEXT, ASR_PASS_SPEAKER)))
    for u in utts:
        best = max(labelled, key=lambda s: _overlap(u, s), default=None)
        if best and _overlap(u, best) > 0:
            u["speaker"] = best["speaker"]
    # Pass 1 can drop a speaker who cuts in without a pause; pass 2 keeps them, so fill the gaps from it.
    utts += [s for s in labelled if not any(_overlap(s, u) > 0 for u in utts)]
    utts.sort(key=lambda u: u["start"])
    return {"model": ASR_MODEL, "duration": round(duration, 2), "segments": utts}
