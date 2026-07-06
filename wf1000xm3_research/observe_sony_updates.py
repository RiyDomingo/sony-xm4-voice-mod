"""mitmproxy addon: observe Sony update traffic without modifying responses.

Use this for WF-1000XM3 research before any attempt to serve patched files.
It logs Sony CDN requests and writes a TSV capture file so the real model path,
language-pack IDs, content folders, and filenames can be inspected later.

Run with:
    mitmdump -s wf1000xm3_research/observe_sony_updates.py --listen-port 8080
"""
from __future__ import annotations

import csv
from datetime import datetime, timezone
from pathlib import Path
from urllib.parse import urlsplit

from mitmproxy import ctx, http


HERE = Path(__file__).resolve().parent
CAPTURE_TSV = HERE / "sony_update_capture.tsv"
SONY_HOSTS = ("info.update.sony.net", "update.sony.net")


def _is_sony_update_host(host: str) -> bool:
    return any(h in host for h in SONY_HOSTS)


def _classify_path(path: str) -> str:
    if path.endswith("/info/info.xml"):
        return "manifest"
    if path.endswith("/disclaimer.xml"):
        return "disclaimer"
    if "/VP_" in path and path.endswith(".bin"):
        return "voice_pack"
    if path.endswith(".xml"):
        return "xml"
    if path.endswith(".bin"):
        return "bin"
    return "other"


def _append_row(flow: http.HTTPFlow, response: http.Response | None = None) -> None:
    url = flow.request.pretty_url
    parts = urlsplit(url)
    path_bits = [p for p in parts.path.split("/") if p]
    row = {
        "time_utc": datetime.now(timezone.utc).isoformat(timespec="seconds"),
        "client": flow.client_conn.address[0] if flow.client_conn.address else "",
        "method": flow.request.method,
        "host": parts.netloc,
        "path": parts.path,
        "kind": _classify_path(parts.path),
        "model": path_bits[0] if len(path_bits) > 0 else "",
        "lang_pack": path_bits[1] if len(path_bits) > 1 else "",
        "content_folder": path_bits[3] if len(path_bits) > 3 and path_bits[2] == "contents" else "",
        "filename": path_bits[-1] if path_bits else "",
        "status": str(response.status_code) if response else "",
        "content_length": response.headers.get("Content-Length", "") if response else "",
        "content_type": response.headers.get("Content-Type", "") if response else "",
        "url": url,
    }
    exists = CAPTURE_TSV.exists()
    with CAPTURE_TSV.open("a", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=list(row))
        if not exists:
            writer.writeheader()
        writer.writerow(row)


def load(loader) -> None:
    ctx.log.info(
        "observe_sony_updates loaded: logging only, no response swapping. "
        f"Capture file: {CAPTURE_TSV}"
    )


def request(flow: http.HTTPFlow) -> None:
    host = flow.request.pretty_host
    if not _is_sony_update_host(host):
        return
    kind = _classify_path(flow.request.path)
    ctx.log.info(f"[sony-observe] {flow.request.method} {kind} {host}{flow.request.path}")
    _append_row(flow)


def response(flow: http.HTTPFlow) -> None:
    host = flow.request.pretty_host
    if not _is_sony_update_host(host) or not flow.response:
        return
    kind = _classify_path(flow.request.path)
    cl = flow.response.headers.get("Content-Length", "?")
    ctx.log.info(
        f"[sony-observe] response {flow.response.status_code} cl={cl} "
        f"{kind} {flow.request.path}"
    )
    _append_row(flow, flow.response)
