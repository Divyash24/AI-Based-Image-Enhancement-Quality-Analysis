# 🖼️ AI-Based Image Enhancement and Quality Analysis System

A professional Python-based image enhancement application developed as a DRDO internship project.  
The system takes a blurred, low-quality, low-resolution, noisy, or low-contrast image as input, analyzes its quality, enhances it using image processing and AI-based techniques, and generates a detailed PDF report.

---

## 🚀 Project Title

**AI-Based Image Enhancement and Quality Analysis System**

---

## 🎯 Objective

The objective of this project is to build a practical and demo-ready image enhancement system that can:

- 📊 Analyze the quality of an input image
- 🔍 Detect common image quality issues
- ⚙️ Enhance image clarity using OpenCV-based processing
- 🧠 Apply AI-based super-resolution using local Real-ESRGAN
- ☁️ Optionally use Clipdrop cloud enhancement API
- 🖼️ Generate before/after comparison
- 💾 Download the enhanced image
- 📄 Generate a PDF quality analysis report

This project focuses only on **single image enhancement**.  
Video processing and motion blur video restoration are not included.

---

## ✨ Key Features

- 📤 Upload single image
- 👁️ Preview input image
- 📊 Analyze image quality
- 🚨 Detect image issues
- ⚡ Fast OpenCV enhancement
- 🧠 Local AI enhancement using Real-ESRGAN
- 🤖 Auto enhancement mode
- 💬 Prompt-guided local enhancement
- ☁️ Optional cloud enhancement using Clipdrop API
- 🔁 Before/after image comparison
- 💾 Save enhanced image
- 📄 Generate downloadable PDF report

---

## 📊 Image Quality Metrics

The system calculates the following metrics:

- Blur Score
- Sharpness Score
- Noise Level
- Brightness
- Contrast
- Resolution
- Overall Quality Score

---

## 🚨 Detected Image Issues

The system can detect:

- Blurry image
- Noisy image
- Low contrast
- Dark image
- Over-bright image
- Low resolution image

---

## 🛠️ Enhancement Modes

### ⚡ 1. Fast Enhance - OpenCV

This mode applies a balanced image enhancement pipeline using OpenCV.

Techniques used:

- Denoising
- CLAHE
- Gamma correction
- Brightness correction
- Contrast correction
- Saturation boost
- Sharpening

---

### 🧠 2. AI Enhance - Real-ESRGAN

This mode uses local Real-ESRGAN as an AI-based super-resolution engine.

Real-ESRGAN is mainly used for:

- Low-resolution image upscaling
- Super-resolution
- Detail enhancement

OpenCV preprocessing and postprocessing are used to stabilize the final output.

---

### 🤖 3. Auto Mode

Auto Mode analyzes the input image and automatically selects the required enhancement actions.

Example:

- Noisy image → denoising
- Blurry image → sharpening
- Dark image → gamma correction + CLAHE
- Low contrast image → contrast correction
- Low resolution image → super-resolution

---

### 💬 4. Prompt Guided Enhancement

This feature allows the user to type simple enhancement instructions.

Example prompts:

- `make this image sharper`
- `reduce noise and improve clarity`
- `enhance low light`
- `make this image colorful`
- `upscale and sharpen this image`

The system maps prompt keywords to local enhancement actions.

| Prompt Keyword | Enhancement Action |
|---|---|
| sharper | sharpening |
| clearer | denoise + sharpen |
| low light | gamma correction + CLAHE |
| colorful | saturation boost |
| upscale | Real-ESRGAN / upscaling |
| text clearer | contrast + sharpen |

This feature works locally and does not require an LLM API.

---

### ☁️ 5. Cloud Enhance - Clipdrop

This is an optional cloud-based enhancement mode.

The app works without Clipdrop API.  
If a Clipdrop API key is provided, the image can be sent to Clipdrop for cloud enhancement/upscaling.

---

## 🧰 Tech Stack

- Python
- Streamlit
- OpenCV
- NumPy
- Pillow
- Matplotlib
- ReportLab
- Requests
- python-dotenv
- Real-ESRGAN NCNN Vulkan executable
- Optional Clipdrop API

---

## 📁 Folder Structure

```text
AI Image Enhancement/
│
├── app.py
├── requirements.txt
├── README.md
├── .env.example
│
├── src/
│   ├── __init__.py
│   ├── analyzer.py
│   ├── prompt_mapper.py
│   ├── enhancer_opencv.py
│   ├── enhancer_realesrgan.py
│   ├── hybrid_ai_enhancer.py
│   ├── enhancer_clipdrop.py
│   ├── auto_pipeline.py
│   └── report_generator.py
│
├── tools/
│   └── realesrgan-ncnn-vulkan/
│
├── outputs/
│   ├── enhanced/
│   └── reports/
│
├── samples/
│
└── temp/

⚙️ Installation Guide

Follow these steps to set up and run the project on Windows using PowerShell or VS Code terminal.

1. Clone or Open Project Folder

Open the project folder in VS Code.

cd "C:\Projects\AI Image Enhancement"
code .
2. Create Virtual Environment
python -m venv .venv
3. Activate Virtual Environment
.\.venv\Scripts\Activate.ps1

If PowerShell shows execution policy error, run:

Set-ExecutionPolicy -Scope CurrentUser RemoteSigned

Then activate again:

.\.venv\Scripts\Activate.ps1
4. Install Required Dependencies
pip install -r requirements.txt
📦 requirements.txt

The requirements.txt file should contain:

streamlit>=1.35.0
opencv-python>=4.9.0
numpy>=1.24.0
pillow>=10.0.0
matplotlib>=3.7.0
reportlab>=4.0.0
requests>=2.31.0
python-dotenv>=1.0.0
🧠 Real-ESRGAN Setup

This project uses the Real-ESRGAN NCNN Vulkan executable for local AI-based super-resolution.

Real-ESRGAN is not installed using pip in this project.
It is used through a local executable.

Expected executable path:

tools/realesrgan-ncnn-vulkan/.../realesrgan-ncnn-vulkan.exe
Check Real-ESRGAN Executable

Run this command from the project root:

Get-ChildItem -Path .\tools -Recurse -Filter "realesrgan-ncnn-vulkan.exe"
Test Real-ESRGAN Executable
$exe = Get-ChildItem -Path .\tools -Recurse -Filter "realesrgan-ncnn-vulkan.exe" | Select-Object -First 1
& $exe.FullName -h

If Real-ESRGAN is set up correctly, it will show command-line options.

Available Real-ESRGAN Models

The project can use models such as:

realesrgan-x4plus
realesrgan-x4plus-anime
realesr-animevideov3

For this project, the main model used is:

realesrgan-x4plus
☁️ Clipdrop API Setup

Clipdrop cloud enhancement is optional.

Create a .env file in the project root:

CLIPDROP_API_KEY=your_api_key_here

Also keep .env.example like this:

CLIPDROP_API_KEY=

If the API key is not provided, the application will still work using:

Fast Enhance - OpenCV
AI Enhance - Real-ESRGAN
Auto Mode
Prompt Guided Enhancement
▶️ Run the Application

Run the following command:

streamlit run app.py

The application will open in your browser.

Usually it opens at:

http://localhost:8501
🧪 Usage Flow
Upload an image
Click Analyze Image
View image quality metrics
Choose enhancement mode:
Fast Enhance - OpenCV
AI Enhance - Real-ESRGAN
Cloud Enhance - Clipdrop
Auto Mode
Use prompt-guided enhancement if needed
Compare before and after images
Save enhanced image
Download PDF report
📄 PDF Report Generation

The system generates a downloadable PDF report.

The report includes:

Enhancement method used
Backend used
Input image metrics
Output image metrics
Quality improvement percentage
Detected issues
Before/after image preview

Reports are stored in:

outputs/reports/


💾 Enhanced Image Output

Enhanced images can be downloaded directly from the application.

Output images are stored in:

outputs/enhanced/


🧠 Project Workflow
Upload Image
     ↓
Image Preview
     ↓
Quality Analysis
     ↓
Issue Detection
     ↓
Enhancement Mode Selection
     ↓
Image Enhancement
     ↓
Before / After Comparison
     ↓
Save Image / Generate Report
🔍 Quality Analysis Methods
Blur Score

Blur is calculated using Laplacian variance.
Lower value means more blur.
Higher value means sharper image.

Sharpness Score

Sharpness is calculated using Sobel gradient magnitude.
Higher value means stronger edges and better sharpness.

Noise Level

Noise is estimated by comparing the image with a Gaussian blurred version.

Brightness

Brightness is calculated using average grayscale intensity.

Contrast

Contrast is calculated using standard deviation of grayscale intensity.

Overall Quality Score

Overall quality score is calculated using a weighted combination of blur, sharpness, noise, brightness, contrast, and resolution.

📌 Project Scope
Included
Single image enhancement
Image quality analysis
OpenCV-based enhancement
Real-ESRGAN-based super-resolution
Prompt-guided local enhancement
Optional cloud enhancement
Before/after comparison
PDF report generation
Not Included
Video processing
Motion blur video restoration
Real-time webcam processing
Full prompt-based AI image editing using LLM APIs
🧾 Final Project Explanation

This project combines classical image processing and AI-based enhancement techniques.

OpenCV is used for stable enhancement operations such as denoising, CLAHE, gamma correction, brightness correction, contrast correction, saturation improvement, and sharpening.

Real-ESRGAN is integrated as a local AI super-resolution engine for low-resolution image enhancement. It is mainly used for image upscaling and detail enhancement.

The prompt-guided enhancement feature is implemented using a lightweight local rule-based system. It maps simple user instructions such as make sharper, reduce noise, or enhance low light to suitable image processing operations.

The Clipdrop cloud enhancement mode is optional. The application works without internet or API key using local OpenCV and Real-ESRGAN features.

🗣️ Demo Explanation

During demonstration, the project can be explained as:

This project is an AI-based image enhancement and quality analysis system. It accepts a single low-quality image as input, analyzes quality metrics such as blur, sharpness, noise, brightness, contrast, and resolution, detects issues, and applies suitable enhancement techniques. OpenCV is used for stable image processing operations, while Real-ESRGAN is used as a local AI super-resolution engine. The system also supports prompt-guided local enhancement, optional Clipdrop cloud enhancement, before/after comparison, enhanced image download, and PDF report generation.

🏁 Developed For

DRDO Internship Project

Project Title: AI-Based Image Enhancement and Quality Analysis System

👨‍💻 Developer

Developed by: Divyash Saxena

Branch: CSE (AI & ML)

Institution: J.S.S Academy of Technical Education, Noida