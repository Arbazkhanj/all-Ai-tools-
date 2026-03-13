#!/bin/bash

# ============================================
# Download All Rembg Models
# Run: chmod +x download_models.sh && ./download_models.sh
# ============================================

MODELS_DIR="$HOME/.u2net"
mkdir -p "$MODELS_DIR"

echo "========================================"
echo "📥 Downloading Rembg Models"
echo "========================================"
echo "Location: $MODELS_DIR"
echo ""

# Array of models: "filename|url|size"
declare -a MODELS=(
    "isnet-general-use.onnx|https://github.com/danielgatis/rembg/releases/download/v0.0.0/isnet-general-use.onnx|177MB"
    "birefnet-general.onnx|https://github.com/danielgatis/rembg/releases/download/v0.0.0/BiRefNet-general-epoch_244.onnx|824MB"
    "birefnet-general-lite.onnx|https://github.com/danielgatis/rembg/releases/download/v0.0.0/BiRefNet-general-bb_swin_v1_tiny-epoch_232.onnx|?"
    "birefnet-dis.onnx|https://github.com/danielgatis/rembg/releases/download/v0.0.0/BiRefNet-DIS-epoch_590.onnx|?"
    "birefnet-hrsod.onnx|https://github.com/danielgatis/rembg/releases/download/v0.0.0/BiRefNet-HRSOD_DHU-epoch_115.onnx|?"
    "birefnet-cod.onnx|https://github.com/danielgatis/rembg/releases/download/v0.0.0/BiRefNet-COD-epoch_125.onnx|?"
    "birefnet-massive.onnx|https://github.com/danielgatis/rembg/releases/download/v0.0.0/BiRefNet-massive-TR_DIS5K_TR_TEs-epoch_420.onnx|?"
    "bria-rmbg.onnx|https://github.com/danielgatis/rembg/releases/download/v0.0.0/bria-rmbg-2.0.onnx|160MB"
    "sam-encoder.onnx|https://github.com/danielgatis/rembg/releases/download/v0.0.0/vit_b-encoder-quant.onnx|108MB"
    "sam-decoder.onnx|https://github.com/danielgatis/rembg/releases/download/v0.0.0/vit_b-decoder-quant.onnx|100MB"
)

TOTAL=${#MODELS[@]}
CURRENT=0

for MODEL_INFO in "${MODELS[@]}"; do
    IFS='|' read -r FILENAME URL SIZE <<< "$MODEL_INFO"
    CURRENT=$((CURRENT + 1))
    
    FILEPATH="$MODELS_DIR/$FILENAME"
    
    if [ -f "$FILEPATH" ]; then
        FILESIZE=$(du -h "$FILEPATH" | cut -f1)
        echo "[$CURRENT/$TOTAL] ✅ $FILENAME already exists ($FILESIZE)"
        continue
    fi
    
    echo "[$CURRENT/$TOTAL] 📥 Downloading $FILENAME ($SIZE)..."
    curl -L --progress-bar -o "$FILEPATH" "$URL"
    
    if [ $? -eq 0 ]; then
        echo "    ✅ Done!"
    else
        echo "    ❌ Failed!"
        rm -f "$FILEPATH"
    fi
    echo ""
done

echo "========================================"
echo "📊 Download Complete!"
echo "========================================"
echo ""
echo "Total Disk Usage:"
du -sh "$MODELS_DIR"
echo ""
echo "✨ All models ready to use!"
