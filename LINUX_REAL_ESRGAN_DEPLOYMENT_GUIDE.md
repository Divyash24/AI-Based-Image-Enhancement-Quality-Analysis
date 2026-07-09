# Linux Real-ESRGAN Deployment & Troubleshooting Guide

## Project Title

AI-Based Image Enhancement and Quality Analysis System

This guide explains the Linux setup, Real-ESRGAN integration, video enhancement pipeline, possible Vulkan/GPU issues, fallback engines, and recommended input limits.

---

## 1. Enhancement Backends Used in This Project

The project supports multiple enhancement engines:

### 1. OpenCV CPU Engine

Used for:

- Fast image enhancement
- Denoising
- Sharpening
- Brightness correction
- Contrast enhancement
- CLAHE
- Gamma correction
- Saturation improvement
- CPU fallback when AI engine fails

This engine works without GPU.

### 2. Real-ESRGAN NCNN Vulkan Engine

Used for:

- AI-based image super-resolution
- AI-based video frame enhancement
- Low-resolution image/video enhancement
- Detail improvement

This engine uses:

```text
realesrgan-ncnn-vulkan

On Linux, the executable name is:

realesrgan-ncnn-vulkan

On Windows, the executable name is:

realesrgan-ncnn-vulkan.exe

This backend uses .bin and .param models.

Example:

realesrgan-x4plus.bin
realesrgan-x4plus.param

It does not use .pth models.

 3. Optional PyTorch CPU Real-ESRGAN Engine

This is an optional future/secondary backend.

It uses .pth model files such as:

RealESRGAN_x4plus.pth
RealESRGAN_x2plus.pth

It requires:

torch
torchvision
torchaudio
realesrgan
basicsr
facexlib
gfpgan

This backend can run on CPU, but it is very slow for video.

4. Fallback Engine

If Real-ESRGAN fails due to missing GPU/Vulkan support, the system should use OpenCV CPU fallback.

Fallback idea:

Try Real-ESRGAN NCNN Vulkan
        ↓ if fails
Try CPU Real-ESRGAN if configured
        ↓ if fails
Use OpenCV CPU fallback

This ensures the application does not completely fail during demo.

2. Linux Folder Structure

After downloading the GitHub ZIP and extracting it, the project should look like this:

AI-Based-Image-Enhancement-Quality-Analysis-main/
│
├── app.py
├── requirements.txt
├── src/
├── tools/
│   └── realesrgan-ncnn-vulkan/
│       ├── realesrgan-ncnn-vulkan
│       ├── README_ubuntu.md
│       ├── input.jpg
│       ├── input2.jpg
│       ├── onepiece_demo.mp4
│       └── models/
│           ├── realesrgan-x4plus.bin
│           ├── realesrgan-x4plus.param
│           ├── realesrgan-x4plus-anime.bin
│           └── realesrgan-x4plus-anime.param
│
├── outputs/
└── temp/

The important Linux executable is:

tools/realesrgan-ncnn-vulkan/realesrgan-ncnn-vulkan
3. Linux Setup Steps

Open terminal inside the project folder where app.py is present.

Check folder:

ls

Expected files:

app.py  requirements.txt  src  tools

Create virtual environment:

python3 -m venv .venv

Activate virtual environment:

source .venv/bin/activate

Install dependencies:

pip install --upgrade pip
pip install -r requirements.txt

Give executable permission to Real-ESRGAN:

chmod +x $(find tools -type f -name "realesrgan-ncnn-vulkan" | head -n 1)

Test Real-ESRGAN help command:

$(find tools -type f -name "realesrgan-ncnn-vulkan" | head -n 1) -h

Run the application:

streamlit run app.py

Open in browser:

http://localhost:8501
4. One-Line Run Script Command

If run_linux.sh is available:

chmod +x run_linux.sh && ./run_linux.sh

This script performs:

1. Project file check
2. Virtual environment setup
3. Requirements installation
4. Real-ESRGAN permission setup
5. Real-ESRGAN test
6. Output folder creation
7. Streamlit app launch
5. Real-ESRGAN Manual Test

Help command is not enough to confirm full GPU/Vulkan processing.

Use this actual image processing test:

REALESRGAN=$(find tools -type f -name "realesrgan-ncnn-vulkan" | head -n 1)
DIR=$(dirname "$REALESRGAN")

chmod +x "$REALESRGAN"

"$REALESRGAN" \
  -i "$DIR/input.jpg" \
  -o temp_realesrgan_test.png \
  -n realesrgan-x4plus \
  -s 2 \
  -m "$DIR/models"

If this creates:

temp_realesrgan_test.png

then Real-ESRGAN is working correctly.

6. Why Real-ESRGAN May Fail on Linux

Real-ESRGAN NCNN Vulkan may fail even if Python packages are installed correctly.

Possible reasons:

1. Vulkan driver missing

Fix:

sudo apt update
sudo apt install libvulkan1 vulkan-tools mesa-vulkan-drivers -y
2. GPU not detected by Vulkan

Check:

vulkaninfo --summary

If no GPU/device is shown, Real-ESRGAN NCNN Vulkan will not work.

3. NVIDIA driver missing

Check:

nvidia-smi

If this fails, NVIDIA driver may not be installed properly.

Possible admin-level fix:

sudo ubuntu-drivers devices
sudo ubuntu-drivers autoinstall
sudo reboot
4. Running inside virtual machine

If Linux is running inside a VM without GPU passthrough, Vulkan GPU access may not work.

5. Old GPU without Vulkan support

Some old GPUs do not support Vulkan properly.

6. Permission issue

Fix:

chmod +x $(find tools -type f -name "realesrgan-ncnn-vulkan" | head -n 1)
7. Wrong binary selected

Linux binary should be:

realesrgan-ncnn-vulkan

Windows binary is:

realesrgan-ncnn-vulkan.exe

On Linux, .exe should not be used.

7. Important Difference Between NCNN and PyTorch Real-ESRGAN
NCNN Vulkan Version

Used in current setup.

Model files:

.bin
.param

Example:

realesrgan-x4plus.bin
realesrgan-x4plus.param

Requires:

Vulkan-supported GPU/graphics driver

Does not require:

torch
torchvision
torchaudio
.pth model
PyTorch CPU Version

Optional backend.

Model files:

.pth

Example:

RealESRGAN_x4plus.pth

Requires:

torch
torchvision
torchaudio
realesrgan
basicsr
facexlib
gfpgan

Can run on CPU but is much slower.

8. Recommended Input Limits
For Image Enhancement

Recommended input:

Format: JPG, JPEG, PNG, BMP, WEBP
Size: Up to 5 MB for smooth testing
Resolution: 480p to 1080p

For Real-ESRGAN:

Best test image: 300x300 to 800x800
Scale: 2x first

Avoid very large images during demo because Real-ESRGAN processing can take time.

For Video Enhancement

Video enhancement works frame-by-frame.

Pipeline:

Input Video
    ↓
Extract frame using OpenCV
    ↓
Enhance frame using Real-ESRGAN
    ↓
Write enhanced frame to output video
    ↓
Download enhanced video

Recommended test video:

Format: MP4
Duration: 5 to 10 seconds
Resolution: 360p or 480p
FPS: 24 or 30 FPS
Size: Up to 20 MB for testing

Avoid for demo:

Large 1080p videos
Long videos above 30 seconds
High FPS videos
Very large file size videos

Reason:

10 second video at 30 FPS = 300 frames
Each frame is processed separately by Real-ESRGAN

So processing time increases with:

Video duration
FPS
Resolution
Scale factor
GPU speed
9. Suggested Demo Flow
First Test

Run the app:

streamlit run app.py
Test Image Mode First

Use a small image.

Steps:

1. Upload image
2. Click Analyze Image
3. Click AI Enhance - Real-ESRGAN
4. Check before/after output
5. Download report
Then Test Video Mode

Use a short MP4 file.

Recommended:

5 seconds
480p
MP4

Steps:

1. Upload video
2. Check video info
3. Select scale 2x
4. Start Real-ESRGAN video enhancement
5. Wait for progress bar
6. Preview/download output
10. If Real-ESRGAN Fails During Demo

Use this explanation:

Real-ESRGAN NCNN Vulkan requires a working Vulkan-compatible GPU environment.
The current Linux system is not exposing a working Vulkan device or GPU driver.
The application can still continue using OpenCV CPU fallback to keep enhancement functional.

Then use:

Fast Enhance - OpenCV
Prompt Guided Enhancement
Auto Mode
OpenCV CPU Video Enhancement/Fallback
11. Quick Troubleshooting Commands

Check current folder:

ls

Find Real-ESRGAN binary:

find tools -type f -name "realesrgan-ncnn-vulkan"

Give permission:

chmod +x $(find tools -type f -name "realesrgan-ncnn-vulkan" | head -n 1)

Test help:

$(find tools -type f -name "realesrgan-ncnn-vulkan" | head -n 1) -h

Check Vulkan:

vulkaninfo --summary

Check NVIDIA GPU:

nvidia-smi

Install Vulkan packages:

sudo apt update
sudo apt install libvulkan1 vulkan-tools mesa-vulkan-drivers -y

Run app:

streamlit run app.py

Run app on all network interfaces:

streamlit run app.py --server.address=0.0.0.0 --server.port=8501
12. Stable Requirements

Recommended requirements.txt:

streamlit>=1.35.0
opencv-python-headless>=4.9.0
numpy<2
pillow>=10.0.0
matplotlib>=3.7.0
reportlab>=4.0.0
requests>=2.31.0
python-dotenv>=1.0.0

Avoid NumPy 2.x unless all dependent libraries support it properly.

13. Final Technical Explanation

This project supports both classical image processing and AI-based enhancement.

OpenCV is used for CPU-based enhancement tasks such as denoising, sharpening, brightness correction, contrast correction, CLAHE, gamma correction, and saturation improvement.

Real-ESRGAN NCNN Vulkan is integrated for AI-based super-resolution. It enhances images and videos by processing each video frame individually. This backend requires a Vulkan-supported GPU environment.

If the Real-ESRGAN backend fails due to missing GPU, missing Vulkan drivers, or unsupported hardware, the system can use CPU-based OpenCV fallback so that the application remains functional.

The project is designed to work as a flexible enhancement toolkit:

Image Enhancement
Video Enhancement
Quality Analysis
Real-ESRGAN Super Resolution
Prompt Guided Enhancement
OpenCV CPU Fallback
PDF Report Generation

---

## 14. PyTorch CPU Real-ESRGAN Backend

This project also supports an optional PyTorch CPU Real-ESRGAN backend.

This backend is used when the NCNN Vulkan Real-ESRGAN engine fails due to GPU/Vulkan issues.

Backend priority:

```text
1. Real-ESRGAN NCNN Vulkan
        ↓ if fails
2. Real-ESRGAN PyTorch CPU
        ↓ if fails
3. OpenCV CPU Fallback
Why CPU Real-ESRGAN is Added

The NCNN Vulkan version requires a working Vulkan-compatible GPU environment.

On some Linux systems, Real-ESRGAN NCNN Vulkan may fail because of:

Missing Vulkan driver
GPU not detected
NVIDIA driver issue
Virtual machine without GPU passthrough
Old GPU without Vulkan support

To avoid complete failure, PyTorch CPU Real-ESRGAN is added as a secondary AI backend.

15. CPU Real-ESRGAN Requirements

CPU Real-ESRGAN uses .pth model files.

Required model:

models/weights/RealESRGAN_x4plus.pth

Required Python packages:

torch
torchvision
torchaudio
basicsr
facexlib
gfpgan
realesrgan

These are kept separate in:

requirements_cpu_realesrgan.txt

Base requirements are kept in:

requirements.txt

This keeps the normal project setup lightweight.

16. CPU Real-ESRGAN Installation

Use the same virtual environment.

Do not create a separate environment.

python3 -m venv .venv
source .venv/bin/activate

Install base requirements:

pip install --upgrade pip
pip install -r requirements.txt

Install PyTorch CPU packages:

pip install torch==2.0.1 torchvision==0.15.2 torchaudio==2.0.2 --index-url https://download.pytorch.org/whl/cpu

Install CPU Real-ESRGAN dependencies:

pip install -r requirements_cpu_realesrgan.txt

Run the app:

streamlit run app.py
17. CPU Real-ESRGAN Model File

CPU Real-ESRGAN requires:

RealESRGAN_x4plus.pth

Expected location:

models/weights/RealESRGAN_x4plus.pth

If the model is already included in the GitHub repo, no separate download is required.

If the model is missing, download it from the official Real-ESRGAN release and place it inside:

models/weights/

Final structure:

models/
└── weights/
    └── RealESRGAN_x4plus.pth
18. CPU Backend Speed Warning

CPU Real-ESRGAN works without GPU, but it is slow.

Recommended input for CPU Real-ESRGAN image testing:

Image size: 300x300 to 600x600
File size: below 5 MB
Scale: 2x

For video, CPU Real-ESRGAN is very slow because every frame is processed separately.

Example:

10 second video at 30 FPS = 300 frames

So for CPU video testing, use:

Duration: 3 to 5 seconds
Resolution: 360p or 480p
Format: MP4

For longer videos, use OpenCV fallback or NCNN Vulkan if GPU works.

19. If CPU Real-ESRGAN Fails

Possible reasons:

Torch installation failed
Torchvision version mismatch
RealESRGAN_x4plus.pth missing
basicsr import issue
NumPy version conflict
Low RAM or slow CPU

Recommended stable NumPy version:

numpy<2

If NumPy 2.x causes issues, reinstall:

pip uninstall numpy -y
pip install "numpy<2"

If PyTorch CPU installation fails, reinstall:

pip uninstall torch torchvision torchaudio -y
pip install torch==2.0.1 torchvision==0.15.2 torchaudio==2.0.2 --index-url https://download.pytorch.org/whl/cpu

Then:

pip install -r requirements_cpu_realesrgan.txt
20. Final Backend Explanation

The application is designed to be fail-safe.

If GPU/Vulkan works:

Real-ESRGAN NCNN Vulkan is used.

If GPU/Vulkan does not work:

PyTorch CPU Real-ESRGAN is used.

If both Real-ESRGAN backends fail:

OpenCV CPU Fallback is used.

This ensures that the project remains functional even when the Linux system does not provide proper GPU or Vulkan support.