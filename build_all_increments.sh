#!/bin/bash
set -e

echo "=== Building All Quiet English Voice Packs ==="

# Define the runs: (volume_fraction lang_code lang_name filename_percent_label)
runs=(
    "0.05 02 french 5"
    "0.025 03 german 2_5"
    "0.01 04 spanish 1"
    "0.60 05 italian 60"
    "0.50 06 portuguese 50"
    "0.40 07 dutch 40"
    "0.30 08 swedish 30"
    "0.20 09 finnish 20"
    "0.10 10 turkish 10"
)

for run in "${runs[@]}"; do
    read -r vol code name pct <<< "$run"
    display_pct=${pct/_/.}
    
    echo ""
    echo "=============================================="
    echo "Generating ${display_pct}% volume pack for ${name} (code ${code})..."
    echo "=============================================="
    
    ./make_quiet_english_pack.sh "$vol" "$code"
    
    mv patched.bin "english_${pct}pct_in_${name}_slot.bin"
    mv patched_info.xml "english_${pct}pct_in_${name}_slot_info.xml"
    
    echo "Saved to:"
    echo "  english_${pct}pct_in_${name}_slot.bin"
    echo "  english_${pct}pct_in_${name}_slot_info.xml"
done

echo ""
echo "=== All 9 quiet English packs generated successfully! ==="
