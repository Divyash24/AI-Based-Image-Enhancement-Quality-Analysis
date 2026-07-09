from PIL import Image

from src.analyzer import analyze_image
from src.enhancer_opencv import fast_enhance, enhance_with_actions
from src.enhancer_realesrgan import ai_enhance_realesrgan

try:
    from src.enhancer_realesrgan_cpu import cpu_realesrgan_enhance
except Exception:
    cpu_realesrgan_enhance = None


def prepare_realesrgan_input(image: Image.Image, max_side: int = 320) -> Image.Image:
    image = image.convert("RGB")
    width, height = image.size

    largest_side = max(width, height)

    if largest_side > max_side:
        scale = max_side / largest_side
        new_width = int(width * scale)
        new_height = int(height * scale)
        image = image.resize((new_width, new_height), Image.Resampling.LANCZOS)

    width, height = image.size

    safe_width = max(64, (width // 8) * 8)
    safe_height = max(64, (height // 8) * 8)

    if (safe_width, safe_height) != image.size:
        image = image.resize((safe_width, safe_height), Image.Resampling.LANCZOS)

    return image


def hybrid_ai_enhance(image: Image.Image, force_realesrgan: bool = True) -> dict:
    input_metrics = analyze_image(image)
    backend_errors = []

    # 1. Try NCNN Vulkan Real-ESRGAN first
    try:
        safe_input = prepare_realesrgan_input(image, max_side=320)

        realesrgan_output = ai_enhance_realesrgan(
            image=safe_input,
            scale=4,
            model_name="realesrgan-x4plus",
        )

        final_output = enhance_with_actions(
            realesrgan_output,
            ["sharpen"],
        )

        output_metrics = analyze_image(final_output)

        return {
            "input_metrics": input_metrics,
            "output_metrics": output_metrics,
            "enhanced_image": final_output,
            "backend_used": "Real-ESRGAN NCNN Vulkan",
            "actions": ["NCNN Vulkan Real-ESRGAN", "Sharpen"],
            "reasons": ["GPU/Vulkan Real-ESRGAN backend completed successfully."],
        }

    except Exception as error:
        backend_errors.append(f"NCNN Vulkan failed: {str(error)[:180]}")

    # 2. Try PyTorch CPU Real-ESRGAN
    if cpu_realesrgan_enhance is not None:
        try:
            safe_input = prepare_realesrgan_input(image, max_side=256)

            cpu_output = cpu_realesrgan_enhance(
                image=safe_input,
                outscale=2,
                tile=128,
            )

            final_output = enhance_with_actions(
                cpu_output,
                ["sharpen"],
            )

            output_metrics = analyze_image(final_output)

            return {
                "input_metrics": input_metrics,
                "output_metrics": output_metrics,
                "enhanced_image": final_output,
                "backend_used": "Real-ESRGAN PyTorch CPU",
                "actions": ["PyTorch CPU Real-ESRGAN", "Sharpen"],
                "reasons": [
                    "NCNN Vulkan was unavailable.",
                    "PyTorch CPU Real-ESRGAN backend completed successfully.",
                ],
            }

        except Exception as error:
            backend_errors.append(f"PyTorch CPU failed: {str(error)[:180]}")
    else:
        backend_errors.append("PyTorch CPU backend import failed or not installed.")

    # 3. Final OpenCV CPU fallback
    fallback_output = fast_enhance(image)
    output_metrics = analyze_image(fallback_output)

    return {
        "input_metrics": input_metrics,
        "output_metrics": output_metrics,
        "enhanced_image": fallback_output,
        "backend_used": "OpenCV CPU Fallback",
        "actions": ["OpenCV Denoise", "CLAHE", "Gamma/Contrast", "Sharpen"],
        "reasons": backend_errors + [
            "Both Real-ESRGAN backends failed, so OpenCV CPU fallback was used."
        ],
    }