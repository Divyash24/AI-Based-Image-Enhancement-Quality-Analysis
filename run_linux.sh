#!/bin/bash

set -e

echo "======================================"
echo " AI Image Enhancement Linux Setup"
echo "======================================"

cd "$(dirname "$0")"

echo "[1/7] Checking project files..."

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

if [ ! -d "tools" ]; then
    echo "ERROR: tools folder not found. Real-ESRGAN files are missing."
    exit 1
fi

echo "[2/7] Creating virtual environment..."

python3 -m venv .venv

echo "[3/7] Activating virtual environment..."

source .venv/bin/activate

echo "[4/7] Installing Python dependencies..."

pip install --upgrade pip
pip install -r requirements.txt

echo "[5/7] Setting Real-ESRGAN executable permission..."

REALESRGAN_PATH=$(find tools -type f -name "realesrgan-ncnn-vulkan" | head -n 1)

if [ -z "$REALESRGAN_PATH" ]; then
    echo "ERROR: Linux Real-ESRGAN executable not found inside tools folder."
    exit 1
fi

chmod +x "$REALESRGAN_PATH"

echo "Real-ESRGAN found at:"
echo "$REALESRGAN_PATH"

echo "[6/7] Testing Real-ESRGAN executable..."

"$REALESRGAN_PATH" -h > /dev/null 2>&1 || {
    echo "ERROR: Real-ESRGAN executable test failed."
    echo "Possible reason: missing Vulkan drivers."
    echo "Ask admin to run:"
    echo "sudo apt install libvulkan1 vulkan-tools mesa-vulkan-drivers -y"
    exit 1
}

echo "[7/7] Creating output folders..."

mkdir -p outputs/enhanced
mkdir -p outputs/reports
mkdir -p outputs/videos
mkdir -p temp

echo "======================================"
echo "Setup completed successfully."
echo "Starting Streamlit app..."
echo "Open browser at: http://localhost:8501"
echo "======================================"

streamlit run app.py --server.address=0.0.0.0 --server.port=8501