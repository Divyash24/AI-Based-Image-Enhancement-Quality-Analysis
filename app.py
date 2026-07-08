from pathlib import Path
from io import BytesIO
from datetime import datetime

import streamlit as st
from PIL import Image

from src.prompt_mapper import map_prompt_to_actions
from src.analyzer import analyze_image
from src.enhancer_opencv import fast_enhance, enhance_with_actions
from src.auto_pipeline import auto_enhance
from src.hybrid_ai_enhancer import hybrid_ai_enhance
from src.report_generator import generate_pdf_report
from src.enhancer_clipdrop import cloud_enhance_clipdrop, is_clipdrop_configured


OUTPUT_DIR = Path("outputs")
ENHANCED_DIR = OUTPUT_DIR / "enhanced"
REPORT_DIR = OUTPUT_DIR / "reports"

ENHANCED_DIR.mkdir(parents=True, exist_ok=True)
REPORT_DIR.mkdir(parents=True, exist_ok=True)


st.set_page_config(
    page_title="AI Image Enhancement System",
    page_icon="✨",
    layout="wide",
)


def init_session_state():
    defaults = {
        "input_image": None,
        "output_image": None,
        "analysis_done": False,
        "selected_method": None,
        "prompt_actions": [],
        "file_name": None,
        "input_metrics": None,
        "output_metrics": None,
        "auto_actions": [],
        "auto_reasons": [],
        
    }

    for key, value in defaults.items():
        if key not in st.session_state:
            st.session_state[key] = value


def reset_processing_state():
    st.session_state.output_image = None
    st.session_state.analysis_done = False
    st.session_state.selected_method = None
    st.session_state.prompt_actions = []
    st.session_state.input_metrics = None
    st.session_state.output_metrics = None
    st.session_state.auto_actions = []
    st.session_state.auto_reasons = []


def apply_enhancement(image, method_name, actions=None):
    st.session_state.input_metrics = analyze_image(image)

    if actions is None:
        enhanced_image = fast_enhance(image)
    else:
        enhanced_image = enhance_with_actions(image, actions)

    st.session_state.output_image = enhanced_image
    st.session_state.output_metrics = analyze_image(enhanced_image)
    st.session_state.selected_method = method_name
    st.session_state.analysis_done = True


def apply_ai_enhancement(image):
    result = hybrid_ai_enhance(image, force_realesrgan=True)

    st.session_state.input_metrics = result["input_metrics"]
    st.session_state.output_metrics = result["output_metrics"]
    st.session_state.output_image = result["enhanced_image"]

    st.session_state.selected_method = "AI Enhance - Real-ESRGAN"
    st.session_state.analysis_done = True

    st.session_state.auto_actions = result["actions"]
    st.session_state.auto_reasons = result["reasons"]
    st.session_state.backend_used = result["backend_used"]

def apply_cloud_enhancement(image):
    if not is_clipdrop_configured():
        st.error("Clipdrop API key missing. Add CLIPDROP_API_KEY in .env file.")
        return

    st.session_state.input_metrics = analyze_image(image)

    enhanced_image = cloud_enhance_clipdrop(image, scale=2)

    st.session_state.output_image = enhanced_image
    st.session_state.output_metrics = analyze_image(enhanced_image)
    st.session_state.selected_method = "Cloud Enhance - Clipdrop"
    st.session_state.backend_used = "Clipdrop Cloud API"
    st.session_state.analysis_done = True

def image_to_download_bytes(image: Image.Image) -> bytes:
    buffer = BytesIO()
    image.convert("RGB").save(buffer, format="PNG")
    return buffer.getvalue()

init_session_state()



st.markdown(
    """
    <style>
        @import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700;800&display=swap');

        html, body, [class*="css"] {
            font-family: 'Inter', sans-serif;
        }

        .stApp {
            background:
                radial-gradient(circle at top left, rgba(168, 85, 247, 0.25), transparent 30%),
                radial-gradient(circle at top right, rgba(34, 211, 238, 0.20), transparent 28%),
                linear-gradient(135deg, #050816 0%, #0f172a 45%, #111827 100%);
            color: #f8fafc;
        }

        .block-container {
            padding-top: 1.4rem;
            padding-bottom: 2rem;
            max-width: 1500px;
        }

        h1, h2, h3, h4 {
            color: #ffffff !important;
        }

        p, label, span {
            color: #dbeafe;
        }

        .hero {
            padding: 32px;
            border-radius: 28px;
            background:
                linear-gradient(135deg, rgba(30, 41, 59, 0.95), rgba(15, 23, 42, 0.85)),
                linear-gradient(45deg, rgba(59, 130, 246, 0.15), rgba(236, 72, 153, 0.15));
            border: 1px solid rgba(148, 163, 184, 0.24);
            box-shadow: 0 24px 80px rgba(0, 0, 0, 0.35);
            margin-bottom: 22px;
        }

        .hero-title {
            font-size: 42px;
            line-height: 1.08;
            font-weight: 900;
            margin-bottom: 10px;
            background: linear-gradient(90deg, #ffffff, #93c5fd, #c084fc, #f9a8d4);
            -webkit-background-clip: text;
            -webkit-text-fill-color: transparent;
        }

        .hero-subtitle {
            font-size: 16px;
            color: #cbd5e1;
            max-width: 920px;
        }

        .chip-row {
            display: flex;
            gap: 10px;
            flex-wrap: wrap;
            margin-top: 18px;
        }

        .chip {
            padding: 8px 12px;
            border-radius: 999px;
            font-size: 12px;
            font-weight: 700;
            border: 1px solid rgba(148, 163, 184, 0.28);
            background: rgba(15, 23, 42, 0.7);
            color: #e0f2fe;
        }

        .chip-purple {
            background: rgba(126, 34, 206, 0.22);
            color: #e9d5ff;
        }

        .chip-cyan {
            background: rgba(8, 145, 178, 0.22);
            color: #cffafe;
        }

        .chip-pink {
            background: rgba(219, 39, 119, 0.20);
            color: #fce7f3;
        }

        .glass-card {
            padding: 20px;
            border-radius: 24px;
            background: rgba(15, 23, 42, 0.72);
            border: 1px solid rgba(148, 163, 184, 0.22);
            box-shadow: 0 18px 50px rgba(0, 0, 0, 0.28);
            backdrop-filter: blur(18px);
            margin-bottom: 18px;
        }

        .upload-card {
            padding: 30px;
            border-radius: 28px;
            text-align: center;
            background:
                linear-gradient(135deg, rgba(30, 41, 59, 0.82), rgba(15, 23, 42, 0.88)),
                radial-gradient(circle at top, rgba(34, 211, 238, 0.18), transparent 35%);
            border: 1px dashed rgba(125, 211, 252, 0.55);
            box-shadow: inset 0 0 40px rgba(59, 130, 246, 0.08);
            margin-bottom: 18px;
        }

        .upload-icon {
            font-size: 54px;
            margin-bottom: 6px;
        }

        .section-title {
            font-size: 20px;
            font-weight: 800;
            margin-bottom: 8px;
            color: #ffffff;
        }

        .section-subtitle {
            color: #94a3b8;
            font-size: 13px;
            margin-bottom: 14px;
        }

        .mini-title {
            color: #c4b5fd;
            font-size: 13px;
            font-weight: 800;
            text-transform: uppercase;
            letter-spacing: 0.08em;
            margin-bottom: 8px;
        }

        .status-card {
            padding: 14px;
            border-radius: 16px;
            background: rgba(2, 6, 23, 0.72);
            border: 1px solid rgba(148, 163, 184, 0.18);
            color: #cbd5e1;
            margin-bottom: 12px;
        }

        .method-box {
            padding: 14px;
            border-radius: 18px;
            background: linear-gradient(135deg, rgba(59, 130, 246, 0.18), rgba(168, 85, 247, 0.16));
            border: 1px solid rgba(147, 197, 253, 0.30);
            margin-bottom: 12px;
            font-weight: 700;
            color: #dbeafe;
        }

        .issue-pill {
            display: inline-block;
            padding: 7px 10px;
            border-radius: 999px;
            background: rgba(251, 191, 36, 0.14);
            color: #fde68a;
            border: 1px solid rgba(251, 191, 36, 0.25);
            font-size: 12px;
            font-weight: 700;
            margin: 4px 4px 4px 0;
        }

        .feature-grid {
            display: grid;
            grid-template-columns: repeat(3, 1fr);
            gap: 14px;
            margin-top: 18px;
        }

        .feature-card {
            padding: 18px;
            border-radius: 22px;
            background: rgba(15, 23, 42, 0.68);
            border: 1px solid rgba(148, 163, 184, 0.20);
            min-height: 130px;
        }

        .feature-icon {
            font-size: 28px;
            margin-bottom: 8px;
        }

        .feature-heading {
            color: #ffffff;
            font-weight: 800;
            margin-bottom: 6px;
        }

        .feature-text {
            color: #94a3b8;
            font-size: 13px;
        }

        .image-frame {
            border-radius: 22px;
            padding: 12px;
            background: rgba(2, 6, 23, 0.65);
            border: 1px solid rgba(148, 163, 184, 0.20);
        }

        .empty-output {
            min-height: 280px;
            border-radius: 22px;
            border: 1px dashed rgba(148, 163, 184, 0.35);
            background:
                radial-gradient(circle at center, rgba(59, 130, 246, 0.12), transparent 40%),
                rgba(2, 6, 23, 0.48);
            display: flex;
            align-items: center;
            justify-content: center;
            color: #94a3b8;
            font-weight: 700;
            text-align: center;
            padding: 20px;
        }

        .prompt-box {
            padding: 18px;
            border-radius: 24px;
            background:
                linear-gradient(135deg, rgba(30, 41, 59, 0.82), rgba(15, 23, 42, 0.84)),
                radial-gradient(circle at right, rgba(236, 72, 153, 0.16), transparent 32%);
            border: 1px solid rgba(244, 114, 182, 0.24);
            margin-top: 18px;
        }

        div.stButton > button {
            width: 100%;
            border: 0;
            border-radius: 14px;
            padding: 0.72rem 1rem;
            font-weight: 800;
            color: white;
            background: linear-gradient(135deg, #2563eb, #7c3aed, #db2777);
            box-shadow: 0 10px 28px rgba(59, 130, 246, 0.22);
            transition: 0.2s ease;
        }

        div.stButton > button:hover {
            transform: translateY(-1px);
            box-shadow: 0 14px 34px rgba(168, 85, 247, 0.26);
            border: 0;
            color: white;
        }

        div.stButton > button:disabled {
            background: rgba(51, 65, 85, 0.7);
            color: #94a3b8;
            box-shadow: none;
        }

        .stFileUploader {
            padding: 12px;
            border-radius: 18px;
            background: rgba(2, 6, 23, 0.40);
            border: 1px solid rgba(148, 163, 184, 0.18);
        }

        .stTextInput input {
            background: rgba(2, 6, 23, 0.82);
            color: #ffffff;
            border-radius: 14px;
            border: 1px solid rgba(148, 163, 184, 0.24);
            padding: 14px;
        }

        .stMetric {
            background: rgba(2, 6, 23, 0.62);
            border: 1px solid rgba(148, 163, 184, 0.16);
            border-radius: 16px;
            padding: 12px;
        }

        [data-testid="stMetricLabel"] {
            color: #93c5fd;
            font-weight: 700;
        }

        [data-testid="stMetricValue"] {
            color: #ffffff;
            font-weight: 900;
        }
        [data-testid="stDecoration"] {
            display: none;
       }

        [data-testid="stHeader"] {
            background: transparent;
       }

        #MainMenu {
        visibility: hidden;
    }

footer {
    visibility: hidden;
}
    </style>
    """,
    unsafe_allow_html=True,
)


st.markdown(
    """
    <div class="hero">
        <div class="hero-title">AI-Based Image Enhancement & Quality Analysis</div>
        <div class="hero-subtitle">
            Enhance. Analyze. Perfect. Make your visual assets look better than ever.
        </div>
        <div class="chip-row">
            <div class="chip chip-cyan">Single Image Only</div>
            <div class="chip chip-purple">Real-ESRGAN Ready</div>
            <div class="chip chip-pink">Prompt Guided</div>
            <div class="chip">Before / After Demo</div>
            <div class="chip">PDF Report</div>
        </div>
    </div>
    """,
    unsafe_allow_html=True,
)


uploaded_file = st.file_uploader(
    "Upload image",
    type=["png", "jpg", "jpeg", "bmp", "webp"],
    label_visibility="collapsed",
)


if uploaded_file is None:
    st.markdown(
        """
        <div class="upload-card">
            <div class="upload-icon">✨</div>
            <div class="section-title">Upload a blurred or low-quality image to begin</div>
            <div class="section-subtitle">
                After upload, the workspace will open with quality analysis, enhancement modes,
                before/after comparison, prompt enhancement, and report download options.
            </div>
        </div>
        """,
        unsafe_allow_html=True,
    )

    st.markdown(
        """
        <div class="feature-grid">
            <div class="feature-card">
                <div class="feature-icon">📊</div>
                <div class="feature-heading">Quality Analysis</div>
                <div class="feature-text">Blur score, sharpness, noise, brightness, contrast, resolution and overall score.</div>
            </div>
            <div class="feature-card">
                <div class="feature-icon">🧠</div>
                <div class="feature-heading">AI Enhancement</div>
                <div class="feature-text">Local Real-ESRGAN based super-resolution with OpenCV preprocessing and postprocessing.</div>
            </div>
            <div class="feature-card">
                <div class="feature-icon">💬</div>
                <div class="feature-heading">Prompt Mode</div>
                <div class="feature-text">Simple prompt-to-action mapping like sharper, clearer, low light, colorful, upscale.</div>
            </div>
        </div>
        """,
        unsafe_allow_html=True,
    )

else:
    image = Image.open(uploaded_file).convert("RGB")
    st.session_state.input_image = image
    st.session_state.file_name = uploaded_file.name

    st.markdown("## Workspace")

    left_col, center_col, right_col = st.columns([1.05, 2.35, 1.25], gap="large")

    with left_col:
        st.markdown('<div class="glass-card">', unsafe_allow_html=True)
        st.markdown('<div class="section-title">Control Center</div>', unsafe_allow_html=True)

        st.markdown(
            f"""
            <div class="status-card">
                <div class="mini-title">Selected Image</div>
                {uploaded_file.name}
            </div>
            """,
            unsafe_allow_html=True,
        )

        if st.button("Analyze Image"):
            st.session_state.input_metrics = analyze_image(image)
            st.session_state.analysis_done = True
            st.session_state.selected_method = "Quality Analysis"
            st.session_state.backend_used = None

        st.markdown('<div class="mini-title">Enhancement Modes</div>', unsafe_allow_html=True)

        if st.button("Fast Enhance - OpenCV"):
            st.session_state.backend_used = "OpenCV"
            apply_enhancement(image, "Fast Enhance - OpenCV")

        if st.button("AI Enhance - Real-ESRGAN"):
            with st.spinner("Running Real-ESRGAN AI enhancement..."):
                apply_ai_enhancement(image)

        if st.button("Cloud Enhance - Clipdrop"):
          with st.spinner("Running Clipdrop cloud enhancement..."):
            apply_cloud_enhancement(image)
        if st.button("Auto Mode"):
            with st.spinner("Auto Mode is analyzing and enhancing image..."):
                result = auto_enhance(image)

                st.session_state.input_metrics = result["input_metrics"]
                st.session_state.output_metrics = result["output_metrics"]
                st.session_state.output_image = result["enhanced_image"]
                st.session_state.auto_actions = result["actions"]
                st.session_state.auto_reasons = result["reasons"]
                st.session_state.selected_method = "Auto Mode"
                st.session_state.analysis_done = True
                st.session_state.backend_used = "Auto Pipeline"

        st.markdown("<br>", unsafe_allow_html=True)

        if st.session_state.output_image is not None:
            image_bytes = image_to_download_bytes(st.session_state.output_image)

            st.download_button(
                label="Save Enhanced Image",
                data=image_bytes,
                file_name=f"enhanced_image_{datetime.now().strftime('%Y%m%d_%H%M%S')}.png",
                mime="image/png",
                use_container_width=True,
            )

            if st.session_state.input_metrics is not None and st.session_state.output_metrics is not None:
                report_path = generate_pdf_report(
                    input_image=st.session_state.input_image,
                    output_image=st.session_state.output_image,
                    input_metrics=st.session_state.input_metrics,
                    output_metrics=st.session_state.output_metrics,
                    method_used=st.session_state.selected_method,
                    issues=st.session_state.input_metrics.get("issues", []),
                    backend_used=st.session_state.get("backend_used", None),
                )

                with open(report_path, "rb") as report_file:
                    st.download_button(
                        label="Download Report",
                        data=report_file,
                        file_name=report_path.name,
                        mime="application/pdf",
                        use_container_width=True,
                    )
        else:
            st.button("Save Enhanced Image", disabled=True)
            st.button("Download Report", disabled=True)

        st.markdown("</div>", unsafe_allow_html=True)

        st.markdown(
            """
            <div class="glass-card">
                <div class="mini-title">Pipeline Plan</div>
                <span class="issue-pill">Preprocess</span>
                <span class="issue-pill">Analyze</span>
                <span class="issue-pill">Enhance</span>
                <span class="issue-pill">Compare</span>
                <span class="issue-pill">Report</span>
            </div>
            """,
            unsafe_allow_html=True,
        )

    with center_col:
        st.markdown('<div class="glass-card">', unsafe_allow_html=True)
        st.markdown('<div class="section-title">Before / After Comparison</div>', unsafe_allow_html=True)
        st.markdown(
            '<div class="section-subtitle">Clear visual comparison will be shown here after enhancement.</div>',
            unsafe_allow_html=True,
        )

        before_col, after_col = st.columns(2, gap="medium")

        with before_col:
            st.markdown('<div class="mini-title">Input Image</div>', unsafe_allow_html=True)
            st.markdown('<div class="image-frame">', unsafe_allow_html=True)
            st.image(image, use_container_width=True)
            st.markdown("</div>", unsafe_allow_html=True)

        with after_col:
            st.markdown('<div class="mini-title">Enhanced Output</div>', unsafe_allow_html=True)

            if st.session_state.output_image is not None:
                st.markdown('<div class="image-frame">', unsafe_allow_html=True)
                st.image(st.session_state.output_image, use_container_width=True)
                st.markdown("</div>", unsafe_allow_html=True)
            else:
                st.markdown(
                    """
                    <div class="empty-output">
                        Enhanced image will appear here after processing
                    </div>
                    """,
                    unsafe_allow_html=True,
                )

        st.markdown("</div>", unsafe_allow_html=True)

        st.markdown('<div class="prompt-box">', unsafe_allow_html=True)
        st.markdown('<div class="section-title">Prompt Guided Enhancement</div>', unsafe_allow_html=True)
        st.markdown(
            '<div class="section-subtitle">Example: make this image sharper, reduce noise, enhance low light, upscale and sharpen.</div>',
            unsafe_allow_html=True,
        )

        prompt_col, button_col = st.columns([4, 1.2], gap="medium")

        with prompt_col:
            prompt = st.text_input(
                "Prompt",
                placeholder="Type a prompt to guide enhancement...",
                label_visibility="collapsed",
            )

        with button_col:
            prompt_clicked = st.button("Enhance with Prompt")

        if prompt_clicked:
            if prompt.strip():
                actions = map_prompt_to_actions(prompt)
                st.session_state.prompt_actions = actions
                st.session_state.backend_used = "Local Prompt-Guided OpenCV Pipeline"

                apply_enhancement(
                    image,
                    "Prompt Guided Enhancement",
                    actions=actions,
                )
            else:
                st.warning("Please enter a prompt first.")

        if st.session_state.prompt_actions:
            st.markdown(
                '<div class="method-box">Prompt mapped successfully</div>',
                unsafe_allow_html=True,
            )

            action_html = "".join(
                f'<span class="issue-pill">{action}</span>'
                for action in st.session_state.prompt_actions
            )

            st.markdown(action_html, unsafe_allow_html=True)

        st.markdown("</div>", unsafe_allow_html=True)

    with right_col:
        st.markdown('<div class="glass-card">', unsafe_allow_html=True)
        st.markdown('<div class="section-title">Quality Analysis</div>', unsafe_allow_html=True)

        if not st.session_state.analysis_done:
            st.markdown(
                """
                <div class="status-card">
                    Analysis not started yet.<br><br>
                    Click <b>Analyze Image</b> or choose any enhancement mode.
                </div>
                """,
                unsafe_allow_html=True,
            )

            st.markdown(
                """
                <div class="mini-title">Will Detect</div>
                <span class="issue-pill">Blurry Image</span>
                <span class="issue-pill">Noise</span>
                <span class="issue-pill">Low Contrast</span>
                <span class="issue-pill">Dark Image</span>
                <span class="issue-pill">Low Resolution</span>
                """,
                unsafe_allow_html=True,
            )

        else:
            metrics = st.session_state.input_metrics

            st.markdown(
                f"""
                <div class="method-box">
                    Method Selected:<br>{st.session_state.selected_method}
                </div>
                """,
                unsafe_allow_html=True,
            )

            if metrics is not None:
                st.metric("Resolution", metrics["resolution"])
                st.metric("Blur Score", metrics["blur_score"])
                st.metric("Sharpness Score", metrics["sharpness_score"])
                st.metric("Noise Level", metrics["noise_level"])
                st.metric("Brightness", metrics["brightness"])
                st.metric("Contrast", metrics["contrast"])
                st.metric("Overall Quality", f'{metrics["overall_quality_score"]}%')

                if st.session_state.output_metrics is not None:
                    output_metrics = st.session_state.output_metrics

                    improvement = (
                        output_metrics["overall_quality_score"]
                        - metrics["overall_quality_score"]
                    )

                    st.metric("Enhanced Quality", f'{output_metrics["overall_quality_score"]}%')
                    st.metric("Improvement", f"{round(improvement, 2)}%")
                    st.metric("Enhanced Resolution", output_metrics["resolution"])

                if st.session_state.get("backend_used", None) is not None:
                    st.metric("Backend Used", st.session_state.backend_used)

                if st.session_state.get("backend_used", None) == "OpenCV Fallback":
                    st.error("Real-ESRGAN fallback triggered.")
                    for reason in st.session_state.auto_reasons:
                        st.write(reason)

                if st.session_state.selected_method == "Auto Mode" and st.session_state.auto_actions:
                    st.markdown('<div class="mini-title">Auto Selected Actions</div>', unsafe_allow_html=True)

                    auto_action_html = "".join(
                        f'<span class="issue-pill">{action}</span>'
                        for action in st.session_state.auto_actions
                    )

                    st.markdown(auto_action_html, unsafe_allow_html=True)

                    st.markdown('<div class="mini-title">Auto Mode Reasoning</div>', unsafe_allow_html=True)

                    for reason in st.session_state.auto_reasons:
                        st.markdown(f"- {reason}")

                st.markdown('<div class="mini-title">Detected Issues</div>', unsafe_allow_html=True)

                issue_html = "".join(
                    f'<span class="issue-pill">{issue}</span>'
                    for issue in metrics["issues"]
                )

                st.markdown(issue_html, unsafe_allow_html=True)

            else:
                st.info("Click Analyze Image to calculate quality metrics.")

        st.markdown("</div>", unsafe_allow_html=True)