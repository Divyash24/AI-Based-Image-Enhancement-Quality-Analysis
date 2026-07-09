import cv2
import time
import numpy as np
from pathlib import Path
from PIL import Image

from src.enhancer_opencv import fast_enhance
from src.enhancer_realesrgan import ai_enhance_realesrgan

try:
    from src.enhancer_realesrgan_cpu import cpu_realesrgan_enhance
except Exception:
    cpu_realesrgan_enhance = None


OUTPUT_VIDEO_DIR = Path("outputs/videos")
OUTPUT_VIDEO_DIR.mkdir(parents=True, exist_ok=True)


def cv2_to_pil(frame: np.ndarray) -> Image.Image:
    rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
    return Image.fromarray(rgb)


def pil_to_cv2(image: Image.Image) -> np.ndarray:
    rgb = np.array(image.convert("RGB"))
    return cv2.cvtColor(rgb, cv2.COLOR_RGB2BGR)


def get_video_info(video_path: str) -> dict:
    cap = cv2.VideoCapture(video_path)

    if not cap.isOpened():
        raise RuntimeError("Unable to open video file.")

    fps = cap.get(cv2.CAP_PROP_FPS)
    frame_count = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))
    width = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
    height = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
    duration = frame_count / fps if fps else 0

    cap.release()

    return {
        "fps": round(fps, 2),
        "frame_count": frame_count,
        "width": width,
        "height": height,
        "duration": round(duration, 2),
        "resolution": f"{width} × {height}",
    }


def enhance_video_realesrgan(
    video_path: str,
    progress_callback=None,
    scale: int = 2,
    model_name: str = "realesrgan-x4plus",
    max_frames: int | None = None,
) -> tuple[str, dict]:

    start_time = time.time()

    cap = cv2.VideoCapture(video_path)

    if not cap.isOpened():
        raise RuntimeError("Unable to open video file.")

    fps = cap.get(cv2.CAP_PROP_FPS)
    total_frames = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))
    input_width = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
    input_height = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))

    frames_to_process = total_frames if max_frames is None else min(total_frames, max_frames)

    output_width = input_width * scale
    output_height = input_height * scale

    output_path = OUTPUT_VIDEO_DIR / f"realesrgan_video_{int(time.time())}.mp4"

    fourcc = cv2.VideoWriter_fourcc(*"mp4v")
    writer = cv2.VideoWriter(
        str(output_path),
        fourcc,
        fps if fps else 24,
        (output_width, output_height),
    )

    processed = 0
    backend_used = None
    backend_errors = []

    while processed < frames_to_process:
        ret, frame = cap.read()

        if not ret:
            break

        pil_frame = cv2_to_pil(frame)

        enhanced_pil = None

        # 1. Try NCNN Vulkan
        try:
            enhanced_pil = ai_enhance_realesrgan(
                image=pil_frame,
                scale=scale,
                model_name=model_name,
            )
            backend_used = "Real-ESRGAN NCNN Vulkan"

        except Exception as error:
            if processed == 0:
                backend_errors.append(f"NCNN Vulkan failed: {str(error)[:160]}")

        # 2. Try PyTorch CPU Real-ESRGAN
        if enhanced_pil is None and cpu_realesrgan_enhance is not None:
            try:
                enhanced_pil = cpu_realesrgan_enhance(
                    image=pil_frame,
                    outscale=scale,
                    tile=128,
                )
                backend_used = "Real-ESRGAN PyTorch CPU"

            except Exception as error:
                if processed == 0:
                    backend_errors.append(f"PyTorch CPU failed: {str(error)[:160]}")

        # 3. OpenCV fallback
        if enhanced_pil is None:
            enhanced_pil = fast_enhance(pil_frame)
            backend_used = "OpenCV CPU Fallback"

        enhanced_frame = pil_to_cv2(enhanced_pil)
        enhanced_frame = cv2.resize(enhanced_frame, (output_width, output_height))

        writer.write(enhanced_frame)

        processed += 1

        if progress_callback:
            progress_callback(processed / frames_to_process)

    cap.release()
    writer.release()

    processing_time = round(time.time() - start_time, 2)

    output_info = {
        "method": "Frame-by-Frame Video Enhancement",
        "backend_used": backend_used,
        "model": model_name,
        "scale": scale,
        "input_resolution": f"{input_width} × {input_height}",
        "output_resolution": f"{output_width} × {output_height}",
        "fps": round(fps, 2),
        "total_frames": total_frames,
        "frames_processed": processed,
        "processing_time_sec": processing_time,
        "backend_errors": backend_errors,
    }

    return str(output_path), output_info