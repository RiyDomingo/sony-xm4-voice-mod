# Local Sony WH-1000XM4 Quiet English Voice Pack

This project creates a custom voice guidance pack for the Sony WH-1000XM4 headphones, where all English voice prompts are set to a quieter volume. 

To prevent the headphones from falling back to stock voice prompts (which happens if you install over the same language slot), we pack the quieter English voice prompts into alternative target slots. 

By using different target slots, you can install **multiple** custom volume levels on your headphones simultaneously and toggle between them directly inside the app.

---

## Language Assignments

We have mapped the custom English voice guidance packs to the 9 available non-English language slots. They correspond directly to the order of languages in the Sony app's settings:

*   **5% Volume** is stored under **French (Français)**
*   **2.5% Volume** is stored under **German (Deutsch)**
*   **1% Volume** is stored under **Spanish (Español)**
*   **60% Volume** is stored under **Italian (Italiano)**
*   **50% Volume** is stored under **Portuguese (Português)**
*   **40% Volume** is stored under **Dutch (Nederlands)**
*   **30% Volume** is stored under **Swedish (Svenska)**
*   **20% Volume** is stored under **Finnish (Suomi)**
*   **10% Volume** is stored under **Turkish (Türkçe)**
*   **100% Volume (Stock)** remains active under **English (English)**

Once these packs are installed, you can toggle between all these volume levels directly inside the Sony Headphones Connect app without running the proxy server again!

The filenames intentionally say `english_*_in_*_slot`: the audio inside each pack is quieted English, while the named language is only the Sony app slot used to store it.

---

## What Was Created

1. **`make_quiet_english_pack.sh`**: A shell script that automates downloading the official voice packs, extracting individual prompts, reducing the volume to a chosen amplitude, and packing the custom binaries for any target language code.
2. **`build_all_increments.sh`**: Helper script to generate all 9 packs in one batch.
3. **`slots/`**: A folder containing all the extracted original English voice guidance MP3 prompts.
4. **`english_5pct_in_french_slot.bin` / `english_5pct_in_french_slot_info.xml`**
5. **`english_2_5pct_in_german_slot.bin` / `english_2_5pct_in_german_slot_info.xml`**
6. **`english_1pct_in_spanish_slot.bin` / `english_1pct_in_spanish_slot_info.xml`**
7. **`english_60pct_in_italian_slot.bin` / `english_60pct_in_italian_slot_info.xml`**
8. **`english_50pct_in_portuguese_slot.bin` / `english_50pct_in_portuguese_slot_info.xml`**
9. **`english_40pct_in_dutch_slot.bin` / `english_40pct_in_dutch_slot_info.xml`**
10. **`english_30pct_in_swedish_slot.bin` / `english_30pct_in_swedish_slot_info.xml`**
11. **`english_20pct_in_finnish_slot.bin` / `english_20pct_in_finnish_slot_info.xml`**
12. **`english_10pct_in_turkish_slot.bin` / `english_10pct_in_turkish_slot_info.xml`**

Older ambiguous outputs, if present, are kept in **`legacy_ambiguous_outputs/`** and should not be used for normal installation. The replaced 90%, 80%, and 70% packs are kept in **`legacy_replaced_volume_outputs/`**.

---

## Installation Process

The local proxy script (`swap_vp.py`) will serve whichever files are currently named **`patched.bin`** and **`patched_info.xml`**. You will install the packs one at a time by copying a matching `.bin` and `_info.xml` pair into those active proxy filenames.

### Step 1: Run the Proxy Server
Start `mitmdump` on your computer:
```bash
mitmdump -s swap_vp.py --listen-port 8080
```

### Step 2: Configure Mobile Device Proxy
1. Find your computer's local IP address (e.g. `192.168.1.X`).
2. On your phone, go to **Settings → Wi-Fi**, tap your connected network, select **Configure Proxy → Manual**, and enter your computer's IP as Server and `8080` as Port. Save it.
3. Open Safari or Chrome on your phone, navigate to `http://mitm.it`, download the profile, and install it.
4. **CRITICAL**: Go to **Settings → General → About → Certificate Trust Settings** and enable full trust for the `mitmproxy` root certificate.

### Step 3: Flash the Volume Levels (One by One)
For each volume level you want to install, run the copy commands to activate the pack, then select the target language in the **Sony Headphones Connect** app and trigger the voice guidance install:

*   **To Install 5% (French)**:
    ```bash
    cp english_5pct_in_french_slot.bin patched.bin
    cp english_5pct_in_french_slot_info.xml patched_info.xml
    ```
    *Trigger "French" in the app.*
*   **To Install 2.5% (German)**:
    ```bash
    cp english_2_5pct_in_german_slot.bin patched.bin
    cp english_2_5pct_in_german_slot_info.xml patched_info.xml
    ```
    *Trigger "German" in the app.*
*   **To Install 1% (Spanish)**:
    ```bash
    cp english_1pct_in_spanish_slot.bin patched.bin
    cp english_1pct_in_spanish_slot_info.xml patched_info.xml
    ```
    *Trigger "Spanish" in the app.*
*   **To Install 60% (Italian)**:
    ```bash
    cp english_60pct_in_italian_slot.bin patched.bin
    cp english_60pct_in_italian_slot_info.xml patched_info.xml
    ```
    *Trigger "Italian" in the app.*
*   **To Install 50% (Portuguese)**:
    ```bash
    cp english_50pct_in_portuguese_slot.bin patched.bin
    cp english_50pct_in_portuguese_slot_info.xml patched_info.xml
    ```
    *Trigger "Portuguese" in the app.*
*   **To Install 40% (Dutch)**:
    ```bash
    cp english_40pct_in_dutch_slot.bin patched.bin
    cp english_40pct_in_dutch_slot_info.xml patched_info.xml
    ```
    *Trigger "Dutch" in the app.*
*   **To Install 30% (Swedish)**:
    ```bash
    cp english_30pct_in_swedish_slot.bin patched.bin
    cp english_30pct_in_swedish_slot_info.xml patched_info.xml
    ```
    *Trigger "Swedish" in the app.*
*   **To Install 20% (Finnish)**:
    ```bash
    cp english_20pct_in_finnish_slot.bin patched.bin
    cp english_20pct_in_finnish_slot_info.xml patched_info.xml
    ```
    *Trigger "Finnish" in the app.*
*   **To Install 10% (Turkish)**:
    ```bash
    cp english_10pct_in_turkish_slot.bin patched.bin
    cp english_10pct_in_turkish_slot_info.xml patched_info.xml
    ```
    *Trigger "Turkish" in the app.*

Do not mix files from different rows. The active `patched.bin` and `patched_info.xml` must always come from the same volume/language-slot pair.

### Step 4: Clean Up Proxy Settings
1. On your mobile device, turn the Wi-Fi proxy setting back to **Off**.
2. Go to **VPN & Device Management** on your phone and remove the `mitmproxy` profile.
3. Terminate `mitmdump` on your computer (`Ctrl + C`).

---

## How to Revert to Stock Voice Prompts

If you want to restore the official, loud Sony voice guidance prompts:
1. Ensure the `mitmdump` proxy is **not** running (so your phone traffic goes directly to Sony's CDN).
2. Open the **Sony Headphones Connect** app.
3. Go to **Voice Guidance Language** and switch back to **English** (or select the respective language again).
4. The app will fetch the official, unmodified voice pack from Sony's CDN and overwrite the custom pack.

---

## Remaining Risks & Security Warnings

> [!CAUTION]
> - **Proxy Certificate Risk**: A trusted root certificate allows the proxy server to decrypt HTTPS traffic. Remove the certificate from your phone immediately after installation.
> - **Bricking Hazard**: While the script recomputes integrity signatures correctly, updating voice guidance partition carries a minimal risk. Proceed at your own risk.
