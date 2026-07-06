# WF-1000XM3 Voice-Pack Compatibility Research

This folder is a safety harness for checking whether the WH-1000XM4 voice-pack
method can be adapted to Sony WF-1000XM3 earbuds. It must not be used to serve
modified files until the original WF-1000XM3 files pass the compatibility checks.

## 1. Capture Sony Traffic Without Swapping

Run the observe-only proxy:

```bash
mitmdump -s wf1000xm3_research/observe_sony_updates.py --listen-port 8080
```

On the phone:

1. Set Wi-Fi proxy to this computer, port `8080`.
2. Make sure the mitmproxy certificate is installed and fully trusted.
3. Connect the WF-1000XM3 in Sony Headphones Connect.
4. Open Voice Guidance Language and select a language only far enough to make
   the app fetch Sony metadata. Do not use `swap_vp.py`.

The capture is written to:

```text
wf1000xm3_research/sony_update_capture.tsv
```

Record the real WF-1000XM3 values from that file:

- model path, for example `HP002` on WH-1000XM4
- language pack, for example `VGIDLPB0404`
- content folder, for example `contents/0002`
- exact `VP_*.bin` filename
- `info.xml` and `disclaimer.xml` URLs

## 2. Download Original WF-1000XM3 Files

Only download original Sony files for the WF-1000XM3 URLs captured above.
Store them under a model-specific folder such as:

```text
wf1000xm3_research/original/<model>/<lang_pack>/
```

Do not copy any WH-1000XM4 `patched.bin` into this folder.

## 3. Run Offline Compatibility Inspection

```bash
uv run wf1000xm3_research/inspect_compatibility.py \
  --model <captured-model> \
  --lang-pack <captured-lang-pack> \
  --info wf1000xm3_research/original/<model>/<lang_pack>/info.xml \
  --bin wf1000xm3_research/original/<model>/<lang_pack>/VP_<language>_UPG_XX.bin
```

Hard stop if any structural check fails:

- manifest decryption
- model digest recomputation
- voice-pack AES/LZMA decoding
- TLV tag layout
- first-32-byte SHA-256 rule
- decompressed voice image layout
- MP3 slot expectations

`UNKNOWN` for disclaimer or cross-language behavior is not approval to install.
It means the next step is more observation, not modified flashing.

## 4. Approval Gates

Modified WF-1000XM3 installation is blocked until all are true:

1. The real WF-1000XM3 Sony URLs have been captured.
2. Original WF-1000XM3 `info.xml` and `VP_*.bin` pass offline inspection.
3. An unmodified WF-1000XM3 Sony pack served through a proxy is accepted.
4. The generated modified pack passes the same manifest/bin integrity checks.

Until then, treat WF-1000XM3 support as unproven.

## 5. Unmodified Proxy Test

Only after offline inspection passes, test the proxy path with original Sony
files. This checks whether mitmproxy itself is accepted by the app/device.

```bash
SONY_TARGET_MODEL=<captured-model> \
SONY_TARGET_LANG_PACK=<captured-lang-pack> \
SONY_ORIGINAL_INFO=wf1000xm3_research/original/<model>/<lang_pack>/info.xml \
SONY_ORIGINAL_BIN=wf1000xm3_research/original/<model>/<lang_pack>/VP_<language>_UPG_XX.bin \
mitmdump -s wf1000xm3_research/serve_original_vp.py --listen-port 8080
```

If the WF-1000XM3 rejects the original Sony bytes through this proxy path, stop.
That means modified-pack testing is not justified yet.
