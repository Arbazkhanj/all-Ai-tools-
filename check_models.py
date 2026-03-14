#!/usr/bin/env python3
"""Check all rembg models status"""

import os
import time

MODELS_DIR = os.path.expanduser("~/.u2net")

MODELS = {
    "u2net": "168MB",
    "u2netp": "4MB", 
    "u2net_human_seg": "168MB",
    "u2net_cloth_seg": "168MB",
    "silueta": "43MB",
    "isnet-general-use": "177MB",
    "isnet-anime": "168MB",
    "bria-rmbg": "160MB",
    "birefnet-general": "824MB",
    "birefnet-portrait": "928MB",
}

print("=" * 60)
print("📊 Model Status Check")
print("=" * 60)
print()

total_size = 0
working_models = []
missing_models = []

for model, expected_size in MODELS.items():
    model_path = os.path.join(MODELS_DIR, f"{model}.onnx")
    
    # Check various filename formats
    possible_names = [
        f"{model}.onnx",
        f"{model.replace('-', '_')}.onnx",
        f"{model.replace('_', '-')}.onnx",
    ]
    
    found = False
    actual_size = 0
    
    for name in possible_names:
        path = os.path.join(MODELS_DIR, name)
        if os.path.exists(path):
            found = True
            actual_size = os.path.getsize(path) / (1024*1024)
            total_size += actual_size
            break
    
    if found:
        status = "✅"
        working_models.append(model)
    else:
        status = "❌"
        missing_models.append(model)
    
    size_str = f"{actual_size:.1f}MB" if found else expected_size
    print(f"{status} {model:25} {size_str:>10}")

print()
print("=" * 60)
print(f"📦 Total Downloaded: {total_size:.1f}MB")
print(f"✅ Working Models: {len(working_models)}/{len(MODELS)}")
print("=" * 60)

if missing_models:
    print()
    print("❌ Missing Models:")
    for m in missing_models:
        print(f"   - {m}")

print()
print("⚠️  IMPORTANT:")
print("   Large models (bria-rmbg, birefnet*) take 2-5 minutes to load first time.")
print("   This is normal - they need to load 800MB+ into RAM.")
print("   After first load, they'll be faster (cached in memory).")
