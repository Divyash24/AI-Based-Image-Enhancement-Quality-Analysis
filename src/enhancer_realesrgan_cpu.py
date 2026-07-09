import os
import sys
from pathlib import Path

import cv2
import numpy as np
from PIL import Image


PROJECT_ROOT = Path(__file__).resolve().parent.parent
WEIGHTS_DIR = PROJECT_ROOT / "models" / "weights"
MODEL_PATH = WEIGHTS_DIR / "RealESRGAN_x4plus.pth"

_UPSAMPLER = None


def patch_torchvision_functional_tensor():
    """
    Some Real-ESRGAN/BasicSR versions expect:
    torchvision.transforms.functional_tensor

    In newer torchvision versions, this may not exist.
    This small patch maps it to torchvision.transforms.functional.
    """
    try:
        import torchvision.transforms.functional as functional

        if "torchvision.transforms.functional_tensor" not in sys.modules:
            sys.modules["torchvision.transforms.functional_tensor"] = functional
    except Exception:
        pass


def is_cpu_realesrgan_ready() -> bool:
    if not MODEL_PATH.exists():
        return False

    try:
        patch_torchvision_functional_tensor()
        import torch  # noqa: F401
        from basicsr.archs.rrdbnet_arch import RRDBNet  # noqa: F401
        from realesrgan import RealESRGANer  # noqa: F401

        return True
    except Exception:
        return False


def get_cpu_upsampler(tile: int = 128):
    global _UPSAMPLER

    if _UPSAMPLER is not None:
        return _UPSAMPLER

    if not MODEL_PATH.exists():
        raise FileNotFoundError(
            f"CPU Real-ESRGAN model not found: {MODEL_PATH}"
        )

    patch_torchvision_functional_tensor()

    import torch
    from basicsr.archs.rrdbnet_arch import RRDBNet
    from realesrgan import RealESRGANer

    cpu_threads = max(1, min(4, (os.cpu_count() or 2)))
    torch.set_num_threads(cpu_threads)

    model = RRDBNet(
        num_in_ch=3,
        num_out_ch=3,
        num_feat=64,
        num_block=23,
        num_grow_ch=32,
        scale=4,
    )

    _UPSAMPLER = RealESRGANer(
        scale=4,
        model_path=str(MODEL_PATH),
        model=model,
        tile=tile,
        tile_pad=10,
        pre_pad=0,
        half=False,
        device=torch.device("cpu"),
    )

    return _UPSAMPLER


def cpu_realesrgan_enhance(
    image: Image.Image,
    outscale: int = 2,
    tile: int = 128,
) -> Image.Image:
    """
    CPU PyTorch Real-ESRGAN enhancement.
    Slow but does not need Vulkan/GPU.
    """

    image = image.convert("RGB")

    rgb = np.array(image)
    bgr = cv2.cvtColor(rgb, cv2.COLOR_RGB2BGR)

    upsampler = get_cpu_upsampler(tile=tile)

    output_bgr, _ = upsampler.enhance(
        bgr,
        outscale=outscale,
    )

    output_rgb = cv2.cvtColor(output_bgr, cv2.COLOR_BGR2RGB)

    return Image.fromarray(output_rgb)