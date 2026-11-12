# Video download (`download.py`)

Routes per site, what was measured, and why the simpler routes do not work. The code is `scripts/download.py`; `footage.py` calls it for every link.

Fully automatic, in the script: `--download-only` when the user only wants the files; any other mode downloads links first by itself. Files go to `--download-dir` (default `~/Downloads/ag-footage/`), named `<title ≤60 bytes> [<id>].mp4`; a link already there is not downloaded again. Several links download `--jobs` at a time.

| Site | Route | Checked 2026-11-11 |
|---|---|---|
| B 站 and other yt-dlp sites | yt-dlp, ≤1080p | 2 links, 1080p |
| 小红书 | RedFox; then yt-dlp (link must carry `xsec_token`, refused without); then ego browser | RedFox 62 s 1280×720 at 0.7 Mb/s (the browser got the same note at 1.0 Mb/s); yt-dlp 70 s 1496×720 |
| 抖音 (`douyin.com`, `v.douyin.com` short links) | RedFox; then ego browser | RedFox, 3 links in parallel: 1080×1920 at 1.3–1.6 Mb/s (the browser got 720×1280 at 0.7 Mb/s, one 576×1024 at 0.09 Mb/s); a share message works |

A whole share message (「7.12 复制打开抖音… https://v.douyin.com/… 复制此链接」) works as input: it goes to RedFox as-is, and its link to the other routes.

RedFox（红狐数据）is reached through Artistic Genius, never directly: `POST <AG_BASE_URL without /v1>/redfox/v1/video-download` with `Authorization: Bearer <AG_OMNI_KEY>` and body `{"url": "<link or share message>", "site": "douyin" | "xhs"}`. The reply is RedFox's own body: success is `code` 2000 with `data.videoUrl` (or a `resources[]` item of `type` video). A successful call is billed to the Omni 创作优选 token; a RedFox error code comes back with HTTP 200 and costs nothing. No key, an error code, a note without video, a gateway error (wrong group, no balance) or a failed file download falls back silently to the next route; `--check` shows whether the key is set. The link is sent to the gateway and on to RedFox; the video file itself is downloaded straight from the site's CDN.

The browser route needs ego lite (`ego-browser` on PATH) with the user logged in to the site; each download opens its own task space and closes it. 抖音: the 精选 player (`jingxuan?modal_id=<id>`) is opened, and the file the player requests (a `douyinvod.com` URL carrying `__vid=<id>`) is saved from that page. 小红书: the file comes from the note data, `window.__INITIAL_STATE__.note.noteDetailMap[<id>].note.video.media.stream` (highest `height`). A login or verification wall fails with a hint: ask the user to log in in ego, then rerun.

Why not simpler:
- yt-dlp 抖音: its extractor (`tiktok.py`, `DouyinIE`) calls `/aweme/v1/web/aweme/detail/` with the video ID only; the site now needs an `a_bogus` signature that obfuscated page JavaScript computes, which yt-dlp does not run (a TODO in its source). The API answers 403 and yt-dlp says "Fresh cookies are needed" even with logged-in cookies.
- 抖音 in a fresh browser tab: opening `/video/<id>` redirects to 精选 with some other video; the page carries no video data and the `<video>` plays a `blob:`. Always check the saved file's duration against the page.
- 小红书 without `xsec_token`: the site answers 404「当前笔记暂时无法浏览」, in yt-dlp and in the browser alike. Links copied from search results or the share button have it.
