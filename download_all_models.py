#!/usr/bin/env python3
"""
Download all rembg models at once
Run: python download_all_models.py
"""

import os
from rembg.session_factory import new_session

# All available models
MODELS = [
    ("u2net", "176MB"),
    ("u2netp", "4MB"),
    ("u2net_human_seg", "168MB"),
    ("u2net_cloth_seg", "168MB"),
    ("silueta", "43MB"),
    ("isnet-general-use", "177MB"),
    ("isnet-anime", "168MB"),
    ("sam", "208MB (encoder+decoder)"),
    ("birefnet-general", "824MB"),
    ("birefnet-general-lite", "?"),
    ("birefnet-portrait", "928MB"),
    ("birefnet-dis", "?"),
    ("birefnet-hrsod", "?"),
    ("birefnet-cod", "?"),
    ("birefnet-massive", "?"),
    ("bria-rmbg", "160MB"),
]

print("=" * 60)
print("🚀 Downloading all rembg models...")
print("=" * 60)
print(f"Models directory: ~/.u2net/")
print("=" * 60)

downloaded = []
failed = []
skipped = []

for model_name, size in MODELS:
    try:
        print(f"\n📥 {model_name} ({size})...", end=" ", flush=True)
        
        # Check if already exists
        model_path = os.path.expanduser(f"~/.u2net/{model_name}.onnx")
        if os.path.exists(model_path):
            file_size = os.path.getsize(model_path) / (1024 * 1024)
            print(f"✅ Already exists ({file_size:.1f}MB)")
            skipped.append(model_name)
            continue
        
        # Download model
        session = new_session(model_name)
        print(f"✅ Downloaded!")
        downloaded.append(model_name)
        
    except Exception as e:
        print(f"❌ Failed: {e}")
        failed.append(model_name)

print("\n" + "=" * 60)
print("📊 DOWNLOAD SUMMARY")
print("=" * 60)

if downloaded:
    print(f"✅ Downloaded ({len(downloaded)}): {', '.join(downloaded)}")

if skipped:
    print(f"⏭️  Skipped (already exist) ({len(skipped)}): {', '.join(skipped)}")

if failed:
    print(f"❌ Failed ({len(failed)}): {', '.join(failed)}")

print("\n" + "=" * 60)
print("✨ All models ready! You can now use any model instantly.")
print("=" * 60)

# Show final disk usage
print("\n📦 Disk usage:")
os.system("du -sh ~/.u2net/")
