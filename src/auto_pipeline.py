from PIL import Image

from src.analyzer import analyze_image
from src.enhancer_opencv import enhance_with_actions


def choose_auto_actions(metrics: dict) -> tuple[list[str], list[str]]:
    """
    Selects enhancement actions automatically based on image quality metrics.
    """

    actions = []
    reasons = []

    blur_score = metrics["blur_score"]
    sharpness_score = metrics["sharpness_score"]
    noise_level = metrics["noise_level"]
    brightness = metrics["brightness"]
    contrast = metrics["contrast"]
    width = metrics["width"]
    height = metrics["height"]

    if noise_level > 18:
        actions.append("denoise")
        reasons.append("Noise level is high, so denoising is required.")

    if blur_score < 100 or sharpness_score < 25:
        actions.append("sharpen")
        reasons.append("Image appears blurry or lacks sharpness.")

    if brightness < 80:
        actions.extend(["gamma_correction", "clahe"])
        reasons.append("Image is dark, so gamma correction and CLAHE are applied.")

    if contrast < 35:
        actions.extend(["clahe", "contrast_correction"])
        reasons.append("Low contrast detected, so contrast enhancement is applied.")

    if width < 800 or height < 600:
        actions.append("realesrgan_upscale")
        reasons.append("Low resolution detected, so upscaling is applied.")

    if not actions:
        actions.append("balanced_enhancement")
        reasons.append("No major issue detected, so balanced enhancement is applied.")

    # Remove duplicate actions while preserving order
    actions = list(dict.fromkeys(actions))

    return actions, reasons


def auto_enhance(image: Image.Image) -> dict:
    """
    Complete Auto Mode pipeline:
    1. Analyze image
    2. Choose best actions
    3. Enhance image
    4. Analyze enhanced output
    """

    input_metrics = analyze_image(image)
    actions, reasons = choose_auto_actions(input_metrics)

    enhanced_image = enhance_with_actions(image, actions)
    output_metrics = analyze_image(enhanced_image)

    return {
        "input_metrics": input_metrics,
        "output_metrics": output_metrics,
        "enhanced_image": enhanced_image,
        "actions": actions,
        "reasons": reasons,
    }