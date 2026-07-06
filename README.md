# Sony WH-1000XM4 Quiet English Voice Pack

Custom Sony WH-1000XM4 voice-guidance packs with the original English prompts
reduced to quieter volume levels, then stored in alternate language slots so
they can be installed reliably and switched inside the Sony Headphones Connect
app.

This repository is no longer just the original voice-pack modding toolkit. It
packages a specific end result:

- quiet English voice packs at multiple volume levels
- build scripts for regenerating those packs
- the proxy and packer tooling needed to install or rebuild them

The upstream reverse-engineering and pack-format work still lives here because
the quiet packs depend on it, but the main project is the quiet English pack
set.

---

## Included voice-pack slots

Each pack contains English audio, but is installed into a non-English Sony app
language slot to avoid fallback to the stock prompts.

| Volume | Sony app language slot |
|--------|------------------------|
| 5%     | French                 |
| 2.5%   | German                 |
| 1%     | Spanish                |
| 60%    | Italian                |
| 50%    | Portuguese             |
| 40%    | Dutch                  |
| 30%    | Swedish                |
| 20%    | Finnish                |
| 10%    | Turkish                |
| 100%   | English stock prompts  |

Generated files in the repo follow this naming pattern:

```text
english_<volume>_in_<language>_slot.bin
english_<volume>_in_<language>_slot_info.xml
```

---

## Repo contents

| Path | Purpose |
|------|---------|
| `README_LOCAL.md` | Detailed local install workflow |
| `make_quiet_english_pack.sh` | Build one quiet English pack for a target slot |
| `build_all_increments.sh` | Build the full preset volume set |
| `quiet_slots/` | Extracted quiet English MP3 prompt slots |
| `swap_vp.py` | mitmproxy addon that serves the active patched files |
| `pack_voice_pack.py` | Rebuild Sony-format `.bin` voice packs |
| `pack_info_xml.py` | Forge matching `info.xml` metadata |
| `extract_slots.py` | Extract MP3 slots from an official Sony pack |
| `NOTES.md` | Reverse-engineering notes and format details |

Legacy experiment outputs are kept in `legacy_ambiguous_outputs/` and
`legacy_replaced_volume_outputs/` for reference, not normal use.

---

## Quick install flow

### 1. Start the proxy

```bash
mitmdump -s swap_vp.py --listen-port 8080
```

### 2. Activate one pack

Example for 30% volume in the Swedish slot:

```bash
cp english_30pct_in_swedish_slot.bin patched.bin
cp english_30pct_in_swedish_slot_info.xml patched_info.xml
```

### 3. Install from the iPhone app

1. Point the phone's Wi-Fi proxy at your computer on port `8080`.
2. Install and trust the mitmproxy certificate from `http://mitm.it`.
3. Open Sony Headphones Connect.
4. Choose the matching language slot in Voice Guidance Language.
5. Let the install finish.

Repeat with other pack pairs if you want multiple quiet levels available on the
headphones at once.

For the full step-by-step procedure, see
[README_LOCAL.md](/Volumes/Kimtigo%20TP3000%201TB/Documents/GitHub/sony-wh-1000xm4-quiet-voice-pack/README_LOCAL.md:1).

---

## Rebuilding packs

The repo includes the original modding pipeline if you want to regenerate or
change the packs:

```bash
./make_quiet_english_pack.sh
./build_all_increments.sh
```

These scripts depend on the lower-level tooling in this repo plus external
tools such as `uv`, `ffmpeg`, and `mitmdump`.

---

## Important caveat

Installing into the same language already active on the headphones can fall
back to stock Sony prompts. That is why this project stores quiet English audio
inside alternate language slots instead of replacing the active English slot
directly.

---

## Credits

This project builds on the reverse-engineering work and format research that
made WH-1000XM4 voice-pack repacking possible, especially:

- [HelgeSverre/sony-vp-extract](https://github.com/HelgeSverre/sony-vp-extract)
- the reverse-engineering notes preserved in `NOTES.md`

---

## Disclaimer

Use this on your own headphones and at your own risk. Sony voice-pack assets
remain copyrighted; do not redistribute official unmodified Sony files.
