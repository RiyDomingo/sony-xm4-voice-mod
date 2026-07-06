# Sony WH-1000XM4 Quiet English Voice Pack

This repo contains quieted English voice-guidance packs for the Sony
WH-1000XM4. Each pack keeps the original English prompts, but reduces their
volume and stores them in a different Sony language slot so the headphones do
not fall back to the stock pack.

The practical result is simple: you can install several quieter English presets
once, then switch between them in the Sony Headphones Connect app by changing
language.

---

## Volume presets

The pack filenames tell you two things:

- `english_<volume>`: the audio is English at that reduced volume
- `in_<language>_slot`: the Sony app language slot used to store it

| Volume | App language |
|--------|--------------|
| 5%     | French       |
| 2.5%   | German       |
| 1%     | Spanish      |
| 60%    | Italian      |
| 50%    | Portuguese   |
| 40%    | Dutch        |
| 30%    | Swedish      |
| 20%    | Finnish      |
| 10%    | Turkish      |
| 100%   | English stock |

Once installed, these appear in the app as normal language choices, but the
audio played is quiet English.

---

## Files that matter

| Path | Purpose |
|------|---------|
| `swap_vp.py` | mitmproxy addon that serves the active pack |
| `patched.bin` | Active voice-pack payload served by the proxy |
| `patched_info.xml` | Active matching metadata served by the proxy |
| `english_*_slot.bin` | Prebuilt quiet English pack |
| `english_*_slot_info.xml` | Matching metadata for that pack |
| `make_quiet_english_pack.sh` | Rebuild one pack |
| `build_all_increments.sh` | Rebuild the full preset set |

Do not mix a `.bin` from one preset with an `_info.xml` from another preset.

---

## Install one or more presets

### 1. Start the proxy

```bash
mitmdump -s swap_vp.py --listen-port 8080
```

### 2. Configure the phone

1. Find your computer's local IP address.
2. On the phone, open `Settings > Wi-Fi > <your network> > Configure Proxy`.
3. Set the proxy to `Manual`.
4. Enter your computer IP and port `8080`.
5. In Safari on the phone, open `http://mitm.it`.
6. Install the `mitmproxy` certificate profile.
7. In `Settings > General > About > Certificate Trust Settings`, fully trust
   the `mitmproxy` root certificate.

### 3. Choose a preset and make it active

Copy the matching pair you want into the filenames the proxy serves.

Example for 30% volume:

```bash
cp english_30pct_in_swedish_slot.bin patched.bin
cp english_30pct_in_swedish_slot_info.xml patched_info.xml
```

Preset mapping:

| Volume | Commands | App language to install |
|--------|----------|-------------------------|
| 5% | `cp english_5pct_in_french_slot.bin patched.bin` and `cp english_5pct_in_french_slot_info.xml patched_info.xml` | French |
| 2.5% | `cp english_2_5pct_in_german_slot.bin patched.bin` and `cp english_2_5pct_in_german_slot_info.xml patched_info.xml` | German |
| 1% | `cp english_1pct_in_spanish_slot.bin patched.bin` and `cp english_1pct_in_spanish_slot_info.xml patched_info.xml` | Spanish |
| 60% | `cp english_60pct_in_italian_slot.bin patched.bin` and `cp english_60pct_in_italian_slot_info.xml patched_info.xml` | Italian |
| 50% | `cp english_50pct_in_portuguese_slot.bin patched.bin` and `cp english_50pct_in_portuguese_slot_info.xml patched_info.xml` | Portuguese |
| 40% | `cp english_40pct_in_dutch_slot.bin patched.bin` and `cp english_40pct_in_dutch_slot_info.xml patched_info.xml` | Dutch |
| 30% | `cp english_30pct_in_swedish_slot.bin patched.bin` and `cp english_30pct_in_swedish_slot_info.xml patched_info.xml` | Swedish |
| 20% | `cp english_20pct_in_finnish_slot.bin patched.bin` and `cp english_20pct_in_finnish_slot_info.xml patched_info.xml` | Finnish |
| 10% | `cp english_10pct_in_turkish_slot.bin patched.bin` and `cp english_10pct_in_turkish_slot_info.xml patched_info.xml` | Turkish |

### 4. Install it from Sony Headphones Connect

1. Open Sony Headphones Connect on the phone.
2. Go to Voice Guidance Language.
3. Select the app language for the preset you activated.
4. Let the download and install finish.

Repeat Step 3 and Step 4 for any other presets you want installed. After that,
you can switch between those installed quiet levels directly in the app without
running the build pipeline again.

### 5. Clean up

1. Turn the Wi-Fi proxy back off on the phone.
2. Remove the `mitmproxy` profile if you no longer need it.
3. Stop `mitmdump`.

---

## Revert to stock English

To go back to the official Sony prompts:

1. Make sure the proxy is off.
2. Open Sony Headphones Connect.
3. Switch Voice Guidance Language back to English.
4. Let the app fetch the official pack from Sony.

---

## Rebuild the packs

If you want to regenerate the pack set instead of using the prebuilt files:

```bash
./make_quiet_english_pack.sh
./build_all_increments.sh
```

The repo also keeps older experiments in `legacy_ambiguous_outputs/` and
`legacy_replaced_volume_outputs/`. Those are archival outputs, not the normal
installation targets.

---

## Risks

> [!CAUTION]
> - Trusting the `mitmproxy` certificate allows HTTPS interception on the phone
>   while that certificate remains trusted.
> - Voice-pack flashing is lower risk than firmware flashing, but it is still a
>   device modification and carries some chance of failure.
