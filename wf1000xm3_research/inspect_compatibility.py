#!/usr/bin/env python3
# /// script
# requires-python = ">=3.10"
# dependencies = ["pycryptodome"]
# ///
"""Inspect original WF-1000XM3 Sony voice-pack files for XM4-tool compatibility.

This is read-only. It never writes a patched voice pack and never serves files.
Provide original Sony CDN files captured/downloaded for the WF-1000XM3.

Usage:
    uv run wf1000xm3_research/inspect_compatibility.py \
      --model <captured-model> \
      --lang-pack <captured-lang-pack> \
      --info path/to/info.xml \
      --bin path/to/VP_language_UPG_XX.bin
"""
from __future__ import annotations

import argparse
import hashlib
import lzma
import re
import struct
import sys
import xml.etree.ElementTree as ET
from pathlib import Path

from Crypto.Cipher import AES


INFO_XML_KEY = bytes(
    [
        0x4F,
        0xA2,
        0x79,
        0x99,
        0xFF,
        0xD0,
        0x8B,
        0x1F,
        0xE4,
        0xD2,
        0x60,
        0xD5,
        0x7B,
        0x6D,
        0x3C,
        0x17,
    ]
)
VP_KEY = b"eibohjeCh6uegahf"
VP_IV = b"miefeinuShu9eilo"
HEADER_SIZE = 0x1000


def split_header(buf: bytes) -> tuple[list[str], bytes]:
    end = 0
    for _ in range(3):
        end = buf.index(b"\n", end) + 1
    while end < len(buf) and buf[end] in b"\r\n":
        end += 1
    return [line for line in buf[:end].decode().splitlines() if line.strip()], buf[end:]


def decrypt_info_xml(raw: bytes) -> tuple[list[str], bytes, str | None]:
    header, body = split_header(raw)
    trim = (len(body) // 16) * 16
    plain = AES.new(INFO_XML_KEY, AES.MODE_ECB).decrypt(body[:trim]).rstrip(b"\x00")
    digest = None
    for line in header:
        if line.startswith("digest:"):
            digest = line.split(":", 1)[1]
    return header, plain, digest


def compute_info_digest(plain: bytes, lang_pack: str, model: str) -> str:
    body_sha1 = hashlib.sha1(plain).hexdigest()
    return hashlib.sha1((body_sha1 + lang_pack + model).encode("utf-8")).hexdigest()


def walk_tlv(header: bytes) -> list[tuple[int, int, int, bytes]]:
    entries = []
    pos = 0x100
    while pos + 4 <= HEADER_SIZE:
        tag, length = struct.unpack_from("<HH", header, pos)
        if tag in (0, 0xFFFF) or pos + 4 + length > HEADER_SIZE:
            break
        value = header[pos + 4 : pos + 4 + length]
        entries.append((pos, tag, length, value))
        pos += 4 + length
    return entries


def parse_lzma_props(blob: bytes) -> dict[str, int]:
    props = blob[0]
    lc = props % 9
    rem = props // 9
    lp = rem % 5
    pb = rem // 5
    dict_size = struct.unpack_from("<I", blob, 1)[0]
    declared_size = struct.unpack_from("<Q", blob, 5)[0]
    return {
        "props_byte": props,
        "lc": lc,
        "lp": lp,
        "pb": pb,
        "dict_size": dict_size,
        "declared_size": declared_size,
    }


def decrypt_voice_pack(raw: bytes) -> tuple[bytes, bytes, bytes, dict[str, int]]:
    if len(raw) < HEADER_SIZE + 16:
        raise ValueError("voice pack is too small")
    header = raw[:HEADER_SIZE]
    encrypted_body = raw[HEADER_SIZE:]
    if len(encrypted_body) % 16 != 0:
        raise ValueError("encrypted body length is not AES-block aligned")
    decrypted = AES.new(VP_KEY, AES.MODE_CBC, VP_IV).decrypt(encrypted_body)
    params = parse_lzma_props(decrypted)
    filters = [
        {
            "id": lzma.FILTER_LZMA1,
            "lc": params["lc"],
            "lp": params["lp"],
            "pb": params["pb"],
            "dict_size": params["dict_size"],
        }
    ]
    d = lzma.LZMADecompressor(format=lzma.FORMAT_RAW, filters=filters)
    decompressed = d.decompress(decrypted[13:], max_length=max(params["declared_size"], 0x100000))
    return header, encrypted_body, decompressed, params


def parse_voice_image(img: bytes) -> dict[str, object]:
    version, entries = struct.unpack_from("<II", img, 0)
    if entries == 0 or entries > 256:
        raise ValueError(f"implausible voice entry count: {entries}")
    table_end = 8 + entries * 8
    first_abs = struct.unpack_from("<I", img, 12)[0]
    base = first_abs - table_end
    slots = []
    for i in range(entries):
        size, abs_off = struct.unpack_from("<II", img, 8 + i * 8)
        file_off = abs_off - base
        data = img[file_off : file_off + size]
        mp3_like = data.startswith(b"ID3") or data[:2] in (b"\xff\xfb", b"\xff\xf3", b"\xff\xf2")
        slots.append({"index": i, "size": size, "offset": file_off, "mp3_like": mp3_like})
    return {"version": version, "entries": entries, "base_offset": base, "slots": slots}


def check(name: str, ok: bool | None, detail: str) -> tuple[str, bool | None, str]:
    return name, ok, detail


def status(ok: bool | None) -> str:
    if ok is True:
        return "PASS"
    if ok is False:
        return "FAIL"
    return "UNKNOWN"


def main() -> int:
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument("--model", required=True, help="Captured CDN model path, e.g. HP002")
    p.add_argument("--lang-pack", required=True, help="Captured language pack, e.g. VGIDLPB0404")
    p.add_argument("--info", type=Path, required=True, help="Original captured/downloaded info.xml")
    p.add_argument("--bin", type=Path, required=True, help="Original captured/downloaded VP_*.bin")
    args = p.parse_args()

    results: list[tuple[str, bool | None, str]] = []

    info_raw = args.info.read_bytes()
    info_ok = False
    xml_text = ""
    try:
        _header_lines, info_plain, original_digest = decrypt_info_xml(info_raw)
        xml_text = info_plain.decode("utf-8")
        info_ok = "<InformationFile" in xml_text
        expected_digest = compute_info_digest(info_plain, args.lang_pack, args.model)
        results.append(check("same Sony manifest encryption key", info_ok, f"decrypted XML bytes={len(info_plain)}"))
        results.append(
            check(
                "same or supported model digest string",
                original_digest == expected_digest,
                f"header digest={original_digest} recomputed={expected_digest} model={args.model}",
            )
        )
    except Exception as exc:
        results.append(check("same Sony manifest encryption key", False, str(exc)))
        results.append(check("same or supported model digest string", False, "manifest did not decrypt"))

    fw_size = fw_mac = fw_uri = disclaimer_uri = disclaimer_mac = None
    if info_ok:
        try:
            root = ET.fromstring(xml_text)
            for dist in root.iter():
                if dist.tag.endswith("Distribution"):
                    dist_id = dist.attrib.get("ID")
                    if dist_id == "FW":
                        fw_size = int(dist.attrib.get("Size", "-1"))
                        fw_mac = dist.attrib.get("MAC")
                        fw_uri = dist.attrib.get("URI")
                    elif dist_id == "Disclaimer":
                        disclaimer_uri = dist.attrib.get("URI")
                        disclaimer_mac = dist.attrib.get("MAC")
        except Exception as exc:
            results.append(check("manifest XML parse", False, str(exc)))

    bin_raw = args.bin.read_bytes()
    sha256_rule = hashlib.sha256(bin_raw[0x100:]).digest() == bin_raw[:32] if len(bin_raw) >= 0x100 else False
    results.append(
        check(
            "same first-32-byte SHA-256 rule over file[0x100:end]",
            sha256_rule,
            f"file[0:32]={bin_raw[:32].hex()} sha256(file[0x100:])={hashlib.sha256(bin_raw[0x100:]).hexdigest()}",
        )
    )

    if fw_size is not None and fw_mac is not None:
        actual_mac = hashlib.sha1(bin_raw).hexdigest()
        results.append(
            check(
                "manifest FW size/MAC matches original .bin",
                fw_size == len(bin_raw) and fw_mac.lower() == actual_mac,
                f"manifest size={fw_size} actual={len(bin_raw)} manifest MAC={fw_mac} actual={actual_mac}",
            )
        )

    try:
        header, encrypted_body, decompressed, lzma_params = decrypt_voice_pack(bin_raw)
        results.append(check("same VP_*.bin AES key/IV", True, f"decrypted body={len(encrypted_body)} B"))
        tlv = walk_tlv(header)
        tags = {tag: (offset, length, value) for offset, tag, length, value in tlv}
        expected_tags = {0x0011, 0x0012, 0x0013, 0x0014}
        results.append(
            check(
                "same TLV structure",
                expected_tags.issubset(tags),
                "tags=" + ", ".join(f"0x{tag:04x}:{length}" for _, tag, length, _ in tlv),
            )
        )
        image = parse_voice_image(decompressed)
        slot_count = int(image["entries"])
        slots = image["slots"]
        mp3_like = sum(1 for s in slots if s["size"] == 0 or s["mp3_like"])
        results.append(
            check(
                "same decompressed image structure",
                slot_count == 54 and len(decompressed) == 0x100000,
                f"version={image['version']} entries={slot_count} size={len(decompressed)} base=0x{image['base_offset']:x}",
            )
        )
        results.append(
            check(
                "same MP3 codec expectations",
                mp3_like == slot_count,
                f"mp3-like slots={mp3_like}/{slot_count} lzma={lzma_params}",
            )
        )
    except Exception as exc:
        results.append(check("same VP_*.bin AES key/IV", False, str(exc)))
        results.append(check("same TLV structure", False, "voice pack did not decrypt/decompress"))
        results.append(check("same decompressed image structure", False, "voice pack did not decrypt/decompress"))
        results.append(check("same MP3 codec expectations", False, "voice pack did not decrypt/decompress"))

    disclaimer_known = None
    disclaimer_detail = "manifest did not expose Disclaimer distribution"
    if disclaimer_uri or disclaimer_mac:
        disclaimer_known = None
        disclaimer_detail = f"URI={disclaimer_uri} MAC={disclaimer_mac}; download/compare separately"
    results.append(check("same disclaimer MAC behavior", disclaimer_known, disclaimer_detail))
    results.append(check("same cross-language install behavior", None, "requires live unmodified proxy install test"))

    if fw_uri:
        model_match = f"/{args.model}/" in fw_uri
        lang_match = f"/{args.lang_pack}/" in fw_uri
        filename_match = bool(re.search(r"/VP_[^/]+\.bin$", fw_uri))
        results.append(
            check(
                "captured manifest URI matches target model/language",
                model_match and lang_match and filename_match,
                f"FW URI={fw_uri}",
            )
        )

    print("\nWF-1000XM3 compatibility matrix")
    print("=" * 36)
    hard_fail = False
    structural_names = {
        "same Sony manifest encryption key",
        "same or supported model digest string",
        "same VP_*.bin AES key/IV",
        "same TLV structure",
        "same first-32-byte SHA-256 rule over file[0x100:end]",
        "same decompressed image structure",
        "same MP3 codec expectations",
    }
    for name, ok, detail in results:
        print(f"{status(ok):7s} {name}")
        print(f"        {detail}")
        if name in structural_names and ok is False:
            hard_fail = True

    print("\nDecision")
    if hard_fail:
        print("STOP: at least one structural compatibility check failed. Do not install a modified WF pack.")
        return 2
    if any(ok is None for _, ok, _ in results):
        print("HOLD: structural checks passed so far, but live disclaimer/cross-language behavior is still unknown.")
        return 1
    print("PASS: offline checks passed. Proceed only with the unmodified proxy test before any modified pack.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
