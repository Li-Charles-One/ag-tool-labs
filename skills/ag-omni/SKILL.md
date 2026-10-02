---
name: ag-omni
description: "通过 Artistic Genius 做多模态视听分析：图像理解、UI 界面分析、文档/PDF OCR 文字提取，以及音视频总结与语音转写。需要 Artistic Genius 的 Gemini 分组令牌（或 mimo 分组令牌）。不要用于生成图片视频，或品牌设计规范（用 genius-design）。"
metadata:
  version: "1.0.0"
---

# AG Omni（视听）

This skill exists to **analyze images**, **analyze video/audio**, and **OCR**. Nothing else.

Everything goes through [Artistic Genius](https://artistic-genius.vip). Default provider `gemini`: `gemini-3.8-flash-high` via native Gemini `generateContent`. Alternative provider `mimo`: `mimo-v2.6-flash`. Any other multimodal endpoint can be configured as a custom provider.

Keys are Artistic Genius `sk-` tokens, and a token only works for the group it was created in (console → 令牌 → 新建令牌): a **Gemini-group** token in `AG_GEMINI_KEY` for the default provider, a **mimo-group** token in `AG_MIMO_KEY` for `--provider mimo`. A token from the wrong group gets `No available channel`.

Config, providers, proxy and verification: `references/usage.md`.

## Pick a mode

| User wants | Mode |
|---|---|
| What is in this picture | `describe` |
| Read text in a screenshot / photo / PDF | `ocr` |
| Critique a UI screenshot | `ui-review` |
| Read a chart | `chart-data` |
| List objects in a picture | `object-detect` |
| Diff two pictures | `compare` (`--compare-with <second>`) |
| What happened in this video / YouTube | `video-summary` |
| Text visible in a video | `video-ocr` |
| Critique a recording | `video-review` |
| Shot-by-shot video | `video-frame-analysis` |
| What is in this audio | `audio-summary` |
| Transcribe speech | `audio-transcribe` |
| Critique audio production | `audio-review` |
| Soundscape / events | `audio-scene` |

PDF accepts `ocr` (default), `describe`, `chart-data`, `ui-review`. Generic modes remap automatically: audio `describe`→`audio-summary`, `ocr`→`audio-transcribe`; video `describe`→`video-summary`, `ocr`→`video-ocr`.

## Run

```bash
python3 "<skill_dir>/scripts/vision.py" <file_or_url> <mode> [--output json|text] [--provider gemini|mimo]
python3 "<skill_dir>/scripts/vision.py" --check
```

`<skill_dir>` is this skill folder; on Windows use `python`. Needs `ffmpeg` / `ffprobe`, plus `pdftoppm` only for MiMo or page-mode PDF. No Python packages to install. Keys live in environment variables or `scripts/.env`, never in the package.

- Before running, confirm the file or URL exists and note the video length or PDF page count.
- Local video ≥ 15 min is segmented and indexed (`--no-long-video` disables); ffprobe injects the real duration.
- PDF: the `gemini` provider reads the whole document in one request; MiMo (or `VISION_PDF_PAGES=1`) renders pages and analyzes them one by one.
- Local media over 20MB is compressed into an analysis proxy automatically.
- `audio-transcribe` first asks the model whether a human voice is audible (one short extra request; `VISION_VOICE_CHECK=0` disables) and answers `NO_SPEECH_DETECTED` without transcribing when there is none.

## Report

- Image: `Summary`, `Observations`, `Extracted Text` (when requested), `Uncertainty`.
- Video: `Summary`, `Timeline`, `Key Moments`, `Uncertainty`.
- Audio: `Summary`, `Transcript or Key Segments`, `Speakers or Sound Events`, `Uncertainty`.
- Compare: `Unchanged`, `Added`, `Removed`, `Uncertain`.

Keep OCR as observed text and mark inferred repairs separately. Unreadable spans stay `[illegible]` (speech: `[inaudible]`); never guess. Report `NO_TEXT_FOUND` when the result says no text or speech was found (`audio-transcribe` answers `NO_SPEECH_DETECTED`). If long-media segmentation fails, report the failed segment and do not fabricate a summary.

Failures print `Error [CODE]: …` and exit with: `INPUT_NOT_FOUND` 3, `UNSUPPORTED_FORMAT` 4, `DEPENDENCY_MISSING` 5, `PROVIDER_ERROR` 6, `TIMEOUT` 7 (other errors 1; `--check` with missing tools 2). Report the code and message as-is.

## Gotchas

- This skill analyzes media and extracts text. It does not generate images or video.
- MiMo multimodal is `mimo-v2.6-flash` (image, audio and video verified). Do not switch to a `-pro` model: `mimo-v2.5-pro` cannot see or hear, and `mimo-v2.6-pro` is unverified.
- YouTube links work on the `gemini` provider only, not on `mimo`.
- `mimo` is slow on images: one screenshot takes about 45–65 s (video and audio are fine). Prefer `gemini` for images and PDF.
- Proxy, PDF page and long-video index files live under system TEMP (`ag-omni-proxy/`, `ag-omni-index/`) and are purged after 30 days.
