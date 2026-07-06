"""mitmproxy addon: serve captured original Sony files for proxy-path testing.

This is for the WF-1000XM3 unmodified proxy test only. It refuses to run unless
explicit original file paths are provided through environment variables.

Required environment:
    SONY_ORIGINAL_INFO=/path/to/original/info.xml
    SONY_ORIGINAL_BIN=/path/to/original/VP_language_UPG_XX.bin

Optional environment:
    SONY_ORIGINAL_DISCLAIMER=/path/to/original/disclaimer.xml
    SONY_TARGET_MODEL=<captured model path>
    SONY_TARGET_LANG_PACK=<captured language pack>

Run example:
    SONY_ORIGINAL_INFO=wf1000xm3_research/original/<model>/<lang>/info.xml \
    SONY_ORIGINAL_BIN=wf1000xm3_research/original/<model>/<lang>/VP_language_UPG_XX.bin \
    mitmdump -s wf1000xm3_research/serve_original_vp.py --listen-port 8080
"""
from __future__ import annotations

import os
from pathlib import Path

from mitmproxy import ctx, http


SONY_HOSTS = ("info.update.sony.net", "update.sony.net")
ORIGINAL_INFO = Path(os.environ["SONY_ORIGINAL_INFO"]) if os.environ.get("SONY_ORIGINAL_INFO") else None
ORIGINAL_BIN = Path(os.environ["SONY_ORIGINAL_BIN"]) if os.environ.get("SONY_ORIGINAL_BIN") else None
ORIGINAL_DISCLAIMER = (
    Path(os.environ["SONY_ORIGINAL_DISCLAIMER"]) if os.environ.get("SONY_ORIGINAL_DISCLAIMER") else None
)
TARGET_MODEL = os.environ.get("SONY_TARGET_MODEL")
TARGET_LANG_PACK = os.environ.get("SONY_TARGET_LANG_PACK")


def _is_sony_update_host(host: str) -> bool:
    return any(h in host for h in SONY_HOSTS)


def _target_matches(path: str) -> bool:
    if TARGET_MODEL and f"/{TARGET_MODEL}/" not in path:
        return False
    if TARGET_LANG_PACK and f"/{TARGET_LANG_PACK}/" not in path:
        return False
    return True


def _make_response(path: Path, content_type: str) -> http.Response:
    body = path.read_bytes()
    return http.Response.make(
        200,
        body,
        {
            "Content-Type": content_type,
            "Content-Length": str(len(body)),
            "Cache-Control": "no-store",
        },
    )


def load(loader) -> None:
    missing = []
    if not ORIGINAL_INFO:
        missing.append("SONY_ORIGINAL_INFO")
    elif not ORIGINAL_INFO.exists():
        missing.append(f"SONY_ORIGINAL_INFO file not found: {ORIGINAL_INFO}")
    if not ORIGINAL_BIN:
        missing.append("SONY_ORIGINAL_BIN")
    elif not ORIGINAL_BIN.exists():
        missing.append(f"SONY_ORIGINAL_BIN file not found: {ORIGINAL_BIN}")
    if ORIGINAL_DISCLAIMER and not ORIGINAL_DISCLAIMER.exists():
        missing.append(f"SONY_ORIGINAL_DISCLAIMER file not found: {ORIGINAL_DISCLAIMER}")
    if missing:
        raise RuntimeError("serve_original_vp is not configured: " + "; ".join(missing))
    ctx.log.warn("serve_original_vp loaded: serving ORIGINAL Sony files only, not modified packs")
    ctx.log.info(f"  info={ORIGINAL_INFO}")
    ctx.log.info(f"  bin={ORIGINAL_BIN}")
    if ORIGINAL_DISCLAIMER:
        ctx.log.info(f"  disclaimer={ORIGINAL_DISCLAIMER}")
    if TARGET_MODEL or TARGET_LANG_PACK:
        ctx.log.info(f"  target filter model={TARGET_MODEL or '*'} lang={TARGET_LANG_PACK or '*'}")


def request(flow: http.HTTPFlow) -> None:
    host = flow.request.pretty_host
    path = flow.request.path
    if not _is_sony_update_host(host):
        return

    ctx.log.info(f"[sony-original] {flow.request.method} {host}{path}")
    if not _target_matches(path):
        ctx.log.warn(f"[sony-original] target filter did not match; passing through {path}")
        return

    if path.endswith("/info.xml") and "VGIDLPB" in path:
        flow.response = _make_response(ORIGINAL_INFO, "application/octet-stream")
        ctx.log.info(f"[sony-original] served original info.xml ({ORIGINAL_INFO.stat().st_size:,} B)")
        return

    if "/VP_" in path and path.endswith(".bin"):
        flow.response = _make_response(ORIGINAL_BIN, "application/octet-stream")
        ctx.log.info(f"[sony-original] served original VP bin ({ORIGINAL_BIN.stat().st_size:,} B)")
        return

    if ORIGINAL_DISCLAIMER and path.endswith("/disclaimer.xml"):
        flow.response = _make_response(ORIGINAL_DISCLAIMER, "application/xml")
        ctx.log.info(
            f"[sony-original] served original disclaimer ({ORIGINAL_DISCLAIMER.stat().st_size:,} B)"
        )
