from PIL import Image

from src.analyzer import analyze_image
from src.enhancer_opencv import fast_enhance, enhance_with_actions
from src.enhancer_realesrgan import ai_enhance_realesrgan, is_realesrgan_ready

def prepare_realesrgan_input(image: Image.Image, max_side: int = 512) -> Image.Image:
    """
    Real-ESRGAN works best on small low-resolution inputs.
    Also force dimensions to multiples of 8 to avoid tile/grid artifacts.
    """

    image = image.convert("RGB")
    width, height = image.size
    largest_side = max(width, height)

    if largest_side > max_side:
        scale_ratio = max_side / largest_side
        width = int(width * scale_ratio)
        height = int(height * scale_ratio)

    # Make dimensions multiples of 8
    width = max(64, (width // 8) * 8)
    height = max(64, (height // 8) * 8)

    return image.resize((width, height), Image.Resampling.LANCZOS)


def hybrid_ai_enhance(image: Image.Image, force_realesrgan: bool = False) -> dict:
    """
    AI enhancement pipeline.

    force_realesrgan=True:
        Real-ESRGAN will be used for AI Enhance button.

    force_realesrgan=False:
        OpenCV safe enhancement will be used unless needed.
    """

    input_metrics = analyze_image(image)

    actions = []
    reasons = []

    # Stable fallback output
    opencv_output = fast_enhance(image)
    opencv_metrics = analyze_image(opencv_output)

    if force_realesrgan:
        if not is_realesrgan_ready():
            return {
                "enhanced_image": opencv_output,
                "input_metrics": input_metrics,
                "output_metrics": opencv_metrics,
                "actions": ["opencv_fallback"],
                "reasons": ["Real-ESRGAN setup was not ready, so OpenCV fallback was used."],
                "backend_used": "OpenCV Fallback",
            }

        try:
            # Preprocess before AI upscale
            safe_input = prepare_realesrgan_input(image, max_side=640)

        
            

            # Real-ESRGAN super-resolution
            realesrgan_output = ai_enhance_realesrgan(
                image=safe_input,
                scale=4,
                model_name="realesrgan-x4plus",
            )

            # Light postprocessing after AI upscale
            final_output = enhance_with_actions(
            realesrgan_output,
            ["sharpen"],
            )

            final_metrics = analyze_image(final_output)

            return {
                "enhanced_image": final_output,
                "input_metrics": input_metrics,
                "output_metrics": final_metrics,
                "actions": [
                    "opencv_preprocessing",
                    "realesrgan_super_resolution",
                    "opencv_postprocessing",
                ],
                "reasons": [
                    "Real-ESRGAN was force-applied for AI Enhance mode.",
                    "OpenCV preprocessing and postprocessing were used for quality stabilization.",
                ],
                "backend_used": "Real-ESRGAN + OpenCV",
            }

        except Exception as error:
            return {
                "enhanced_image": opencv_output,
                "input_metrics": input_metrics,
                "output_metrics": opencv_metrics,
                "actions": ["opencv_fallback"],
                "reasons": [f"Real-ESRGAN failed, so OpenCV fallback was used. Error: {error}"],
                "backend_used": "OpenCV Fallback",
            }

    # Default safe mode
    return {
        "enhanced_image": opencv_output,
        "input_metrics": input_metrics,
        "output_metrics": opencv_metrics,
        "actions": ["opencv_fast_enhancement"],
        "reasons": ["Safe OpenCV enhancement was used."],
        "backend_used": "OpenCV",
    }