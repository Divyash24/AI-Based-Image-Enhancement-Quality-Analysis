import cv2
import numpy as np
from PIL import Image


def pil_to_cv2(image: Image.Image) -> np.ndarray:
    """
    Converts PIL RGB image to OpenCV BGR image.
    """
    rgb_image = np.array(image.convert("RGB"))
    bgr_image = cv2.cvtColor(rgb_image, cv2.COLOR_RGB2BGR)
    return bgr_image


def calculate_blur_score(gray: np.ndarray) -> float:
    """
    Laplacian variance method.
    Lower score = more blurry.
    Higher score = sharper.
    """
    return float(cv2.Laplacian(gray, cv2.CV_64F).var())


def calculate_sharpness_score(gray: np.ndarray) -> float:
    """
    Tenengrad sharpness using Sobel gradients.
    Higher score = sharper image.
    """
    sobel_x = cv2.Sobel(gray, cv2.CV_64F, 1, 0, ksize=3)
    sobel_y = cv2.Sobel(gray, cv2.CV_64F, 0, 1, ksize=3)
    gradient_magnitude = np.sqrt(sobel_x ** 2 + sobel_y ** 2)
    return float(np.mean(gradient_magnitude))


def calculate_noise_level(gray: np.ndarray) -> float:
    """
    Estimates noise using difference between image and Gaussian blurred version.
    Higher value = more noise.
    """
    blurred = cv2.GaussianBlur(gray, (5, 5), 0)
    noise = cv2.absdiff(gray, blurred)
    return float(np.std(noise))


def calculate_brightness(gray: np.ndarray) -> float:
    """
    Average grayscale intensity.
    0 = black, 255 = white.
    """
    return float(np.mean(gray))


def calculate_contrast(gray: np.ndarray) -> float:
    """
    Standard deviation of grayscale intensity.
    Higher value = better contrast.
    """
    return float(np.std(gray))


def normalize_score(value: float, min_value: float, max_value: float) -> float:
    """
    Converts any metric to 0-100 range.
    """
    if max_value == min_value:
        return 0.0

    score = ((value - min_value) / (max_value - min_value)) * 100
    return float(np.clip(score, 0, 100))


def calculate_quality_score(
    blur_score: float,
    sharpness_score: float,
    noise_level: float,
    brightness: float,
    contrast: float,
    width: int,
    height: int,
) -> float:
    """
    Combines multiple metrics into a final quality score.
    This is heuristic-based, good for demo and report explanation.
    """

    blur_component = normalize_score(blur_score, 30, 500)
    sharpness_component = normalize_score(sharpness_score, 10, 80)

    # Less noise should give better score
    noise_component = 100 - normalize_score(noise_level, 5, 35)

    # Ideal brightness is around 120-150
    brightness_distance = abs(brightness - 135)
    brightness_component = 100 - normalize_score(brightness_distance, 0, 120)

    contrast_component = normalize_score(contrast, 20, 80)

    megapixels = (width * height) / 1_000_000
    resolution_component = normalize_score(megapixels, 0.3, 3.0)

    final_score = (
        blur_component * 0.22
        + sharpness_component * 0.20
        + noise_component * 0.16
        + brightness_component * 0.14
        + contrast_component * 0.16
        + resolution_component * 0.12
    )

    return round(float(np.clip(final_score, 0, 100)), 2)


def detect_issues(
    blur_score: float,
    noise_level: float,
    brightness: float,
    contrast: float,
    width: int,
    height: int,
) -> list[str]:
    issues = []

    if blur_score < 100:
        issues.append("Blurry image detected")

    if noise_level > 18:
        issues.append("Noise / grain detected")

    if contrast < 35:
        issues.append("Low contrast detected")

    if brightness < 80:
        issues.append("Dark image detected")

    if brightness > 190:
        issues.append("Over-bright image detected")

    if width < 800 or height < 600:
        issues.append("Low resolution image detected")

    if not issues:
        issues.append("No major quality issue detected")

    return issues


def analyze_image(image: Image.Image) -> dict:
    """
    Main analyzer function.
    Takes PIL image and returns all quality metrics.
    """

    cv_image = pil_to_cv2(image)
    gray = cv2.cvtColor(cv_image, cv2.COLOR_BGR2GRAY)

    height, width = gray.shape

    blur_score = calculate_blur_score(gray)
    sharpness_score = calculate_sharpness_score(gray)
    noise_level = calculate_noise_level(gray)
    brightness = calculate_brightness(gray)
    contrast = calculate_contrast(gray)

    quality_score = calculate_quality_score(
        blur_score=blur_score,
        sharpness_score=sharpness_score,
        noise_level=noise_level,
        brightness=brightness,
        contrast=contrast,
        width=width,
        height=height,
    )

    issues = detect_issues(
        blur_score=blur_score,
        noise_level=noise_level,
        brightness=brightness,
        contrast=contrast,
        width=width,
        height=height,
    )

    return {
        "resolution": f"{width} × {height}",
        "width": width,
        "height": height,
        "blur_score": round(blur_score, 2),
        "sharpness_score": round(sharpness_score, 2),
        "noise_level": round(noise_level, 2),
        "brightness": round(brightness, 2),
        "contrast": round(contrast, 2),
        "overall_quality_score": quality_score,
        "issues": issues,
    }