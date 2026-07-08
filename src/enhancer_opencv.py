import cv2
import numpy as np
from PIL import Image


def pil_to_cv2(image: Image.Image) -> np.ndarray:
    rgb = np.array(image.convert("RGB"))
    return cv2.cvtColor(rgb, cv2.COLOR_RGB2BGR)


def cv2_to_pil(image: np.ndarray) -> Image.Image:
    rgb = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)
    return Image.fromarray(rgb)


def denoise_image(image: np.ndarray, strength: int = 6) -> np.ndarray:
    return cv2.fastNlMeansDenoisingColored(
        image,
        None,
        h=strength,
        hColor=strength,
        templateWindowSize=7,
        searchWindowSize=21,
    )


def apply_clahe(image: np.ndarray, clip_limit: float = 2.0) -> np.ndarray:
    lab = cv2.cvtColor(image, cv2.COLOR_BGR2LAB)
    l_channel, a_channel, b_channel = cv2.split(lab)

    clahe = cv2.createCLAHE(clipLimit=clip_limit, tileGridSize=(8, 8))
    enhanced_l = clahe.apply(l_channel)

    merged = cv2.merge((enhanced_l, a_channel, b_channel))
    return cv2.cvtColor(merged, cv2.COLOR_LAB2BGR)


def gamma_correction(image: np.ndarray, gamma: float = 1.25) -> np.ndarray:
    inv_gamma = 1.0 / gamma

    table = np.array(
        [((i / 255.0) ** inv_gamma) * 255 for i in range(256)]
    ).astype("uint8")

    return cv2.LUT(image, table)


def adjust_contrast_brightness(
    image: np.ndarray,
    alpha: float = 1.08,
    beta: int = 4,
) -> np.ndarray:
    return cv2.convertScaleAbs(image, alpha=alpha, beta=beta)


def boost_saturation(image: np.ndarray, saturation_scale: float = 1.15) -> np.ndarray:
    hsv = cv2.cvtColor(image, cv2.COLOR_BGR2HSV).astype(np.float32)
    hsv[:, :, 1] = np.clip(hsv[:, :, 1] * saturation_scale, 0, 255)
    hsv = hsv.astype(np.uint8)
    return cv2.cvtColor(hsv, cv2.COLOR_HSV2BGR)


def sharpen_image(image: np.ndarray, amount: float = 1.25) -> np.ndarray:
    blurred = cv2.GaussianBlur(image, (0, 0), sigmaX=1.2)
    sharpened = cv2.addWeighted(image, 1 + amount, blurred, -amount, 0)
    return np.clip(sharpened, 0, 255).astype(np.uint8)


def upscale_opencv(image: np.ndarray, scale: int = 2) -> np.ndarray:
    height, width = image.shape[:2]
    return cv2.resize(
        image,
        (width * scale, height * scale),
        interpolation=cv2.INTER_CUBIC,
    )


def get_basic_stats(image: np.ndarray) -> tuple[float, float]:
    gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
    brightness = float(np.mean(gray))
    contrast = float(np.std(gray))
    return brightness, contrast


def fast_enhance(image: Image.Image) -> Image.Image:
    """
    Balanced OpenCV enhancement pipeline.
    This works offline and gives visible improvement for demo.
    """

    cv_image = pil_to_cv2(image)

    brightness, contrast = get_basic_stats(cv_image)

    enhanced = cv_image.copy()

    enhanced = denoise_image(enhanced, strength=5)

    if brightness < 90:
        enhanced = gamma_correction(enhanced, gamma=1.35)

    if contrast < 45:
        enhanced = apply_clahe(enhanced, clip_limit=2.2)
    else:
        enhanced = apply_clahe(enhanced, clip_limit=1.5)

    enhanced = adjust_contrast_brightness(enhanced, alpha=1.08, beta=4)
    enhanced = boost_saturation(enhanced, saturation_scale=1.12)
    enhanced = sharpen_image(enhanced, amount=0.85)

    return cv2_to_pil(enhanced)


def enhance_with_actions(image: Image.Image, actions: list[str]) -> Image.Image:
    """
    Applies enhancement based on prompt-mapped actions.
    Real-ESRGAN action will be replaced with actual Real-ESRGAN in upcoming step.
    For now, upscale uses OpenCV bicubic resize.
    """

    cv_image = pil_to_cv2(image)
    enhanced = cv_image.copy()

    if "balanced_enhancement" in actions:
        return fast_enhance(image)

    for action in actions:
        if action == "denoise":
            enhanced = denoise_image(enhanced, strength=7)

        elif action == "sharpen":
            enhanced = sharpen_image(enhanced, amount=1.15)

        elif action == "gamma_correction":
            enhanced = gamma_correction(enhanced, gamma=1.35)

        elif action == "clahe":
            enhanced = apply_clahe(enhanced, clip_limit=2.4)

        elif action == "contrast_correction":
            enhanced = adjust_contrast_brightness(enhanced, alpha=1.15, beta=6)

        elif action == "saturation_boost":
            enhanced = boost_saturation(enhanced, saturation_scale=1.25)

        elif action == "realesrgan_upscale":
            enhanced = upscale_opencv(enhanced, scale=2)

    return cv2_to_pil(enhanced)