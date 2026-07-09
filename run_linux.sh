#!/bin/bash

set -e

echo "======================================"
echo " AI Image Enhancement Linux Setup"
echo "======================================"

cd "$(dirname "$0")"

echo "[1/8] Checking project files..."

if [ ! -f "app.py" ]; then
    echo "ERROR: app.py not found. Please run this script from project root."
    exit 1
fi

if [ ! -f "requirements.txt" ]; then
    echo "ERROR: requirements.txt not found."
    exit 1
fi

if [ ! -d "src" ]; then
    echo "ERROR: src folder not found."
    exit 1
fi

echo "[2/8] Creating virtual environment..."

if [ ! -d ".venv" ]; then
    python3 -m venv .venv
fi

echo "[3/8] Activating virtual environment..."

source .venv/bin/activate

echo "[4/8] Installing base Python dependencies..."

pip install --upgrade pip
pip install -r requirements.txt

echo "[5/8] Installing optional PyTorch CPU Real-ESRGAN backend..."

set +e

pip install torch==2.0.1 torchvision==0.15.2 torchaudio==2.0.2 --index-url https://download.pytorch.org/whl/cpu

if [ -f "requirements_cpu_realesrgan.txt" ]; then
    pip install -r requirements_cpu_realesrgan.txt
fi

CPU_INSTALL_STATUS=$?

set -e

if [ $CPU_INSTALL_STATUS -eq 0 ]; then
    echo "CPU Real-ESRGAN dependencies installed."
else
    echo "WARNING: CPU Real-ESRGAN dependencies failed to install."
    echo "App will still run with NCNN Vulkan or OpenCV fallback."
fi

echo "[6/8] Setting Real-ESRGAN NCNN executable permission..."

REALESRGAN_PATH=$(find tools -type f -name "realesrgan-ncnn-vulkan" | head -n 1)

if [ -z "$REALESRGAN_PATH" ]; then
    echo "WARNING: Linux Real-ESRGAN NCNN executable not found inside tools folder."
else
    chmod +x "$REALESRGAN_PATH"
    echo "Real-ESRGAN NCNN found at:"
    echo "$REALESRGAN_PATH"

    if "$REALESRGAN_PATH" -h > /dev/null 2>&1; then
        echo "Real-ESRGAN NCNN help test passed."
    else
        echo "WARNING: Real-ESRGAN NCNN help test failed."
        echo "App will still start and try CPU/OpenCV fallback."
    fi
fi

echo "[7/8] Checking CPU Real-ESRGAN model..."

if [ -f "models/weights/RealESRGAN_x4plus.pth" ]; then
    echo "CPU Real-ESRGAN model found."
else
    echo "WARNING: models/weights/RealESRGAN_x4plus.pth not found."
    echo "CPU Real-ESRGAN will not work until this file is added."
fi

echo "[8/8] Creating output folders..."

mkdir -p outputs/enhanced
mkdir -p outputs/reports
mkdir -p outputs/videos
mkdir -p temp

echo "======================================"
echo "Setup completed."
echo "Starting Streamlit app..."
echo "Open browser at: http://localhost:8501"
echo "======================================"

streamlit run app.py --server.address=0.0.0.0 --server.port=8501