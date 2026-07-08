import os
from io import BytesIO

import requests
from dotenv import load_dotenv
from PIL import Image


load_dotenv()


CLIPDROP_UPSCALE_URL = "https://clipdrop-api.co/image-upscaling/v1/upscale"


def is_clipdrop_configured() -> bool:
    api_key = os.getenv("CLIPDROP_API_KEY")
    return bool(api_key)


def calculate_target_size(image: Image.Image, scale: int = 2) -> tuple[int, int]:
    width, height = image.size

    target_width = min(width * scale, 4096)
    target_height = min(height * scale, 4096)

    return target_width, target_height


def cloud_enhance_clipdrop(image: Image.Image, scale: int = 2) -> Image.Image:
    """
    Optional cloud enhancement using Clipdrop Image Upscaling API.
    Requires CLIPDROP_API_KEY in .env file.
    """

    api_key = os.getenv("CLIPDROP_API_KEY")

    if not api_key:
        raise RuntimeError(
            "Clipdrop API key not found. Please add CLIPDROP_API_KEY in .env file."
        )

    target_width, target_height = calculate_target_size(image, scale=scale)

    image_buffer = BytesIO()
    image.convert("RGB").save(image_buffer, format="JPEG", quality=95)
    image_buffer.seek(0)

    response = requests.post(
        CLIPDROP_UPSCALE_URL,
        files={
            "image_file": ("input.jpg", image_buffer, "image/jpeg"),
        },
        data={
            "target_width": str(target_width),
            "target_height": str(target_height),
        },
        headers={
            "x-api-key": api_key,
        },
        timeout=120,
    )

    if not response.ok:
        try:
            error_message = response.json()
        except Exception:
            error_message = response.text

        raise RuntimeError(f"Clipdrop API failed: {error_message}")

    output_image = Image.open(BytesIO(response.content)).convert("RGB")
    return output_image
