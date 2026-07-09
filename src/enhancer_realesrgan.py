import subprocess
import uuid
from pathlib import Path

from PIL import Image
from click import command


ROOT_DIR = Path(__file__).resolve().parents[1]
TOOLS_DIR = ROOT_DIR / "tools"
TEMP_DIR = ROOT_DIR / "temp"

TEMP_DIR.mkdir(parents=True, exist_ok=True)


def find_realesrgan_exe() -> Path | None:
    """
    Finds realesrgan-ncnn-vulkan.exe automatically inside tools folder.
    """
    if not TOOLS_DIR.exists():
        return None

    matches = list(TOOLS_DIR.rglob("realesrgan-ncnn-vulkan.exe"))
    matches += list(TOOLS_DIR.rglob("realesrgan-ncnn-vulkan"))

    if not matches:
        return None

    return matches[0]


def get_realesrgan_models_dir(exe_path: Path) -> Path:
    """
    Real-ESRGAN models folder is usually beside the exe.
    """
    return exe_path.parent / "models"


def is_realesrgan_ready() -> bool:
    exe_path = find_realesrgan_exe()

    if exe_path is None:
        return False

    models_dir = get_realesrgan_models_dir(exe_path)

    return exe_path.exists() and models_dir.exists()


def get_realesrgan_setup_message() -> str:
    return (
        "Real-ESRGAN executable not found or models folder missing.\n\n"
        "Expected inside project tools folder:\n"
        "tools/.../realesrgan-ncnn-vulkan.exe\n"
        "tools/.../models/\n\n"
        "Run this in PowerShell to verify:\n"
        'Get-ChildItem -Path .\\tools -Recurse -Filter "realesrgan-ncnn-vulkan.exe"'
    )


def ai_enhance_realesrgan(
    image: Image.Image,
    scale: int = 2,
    model_name: str = "realesrgan-x4plus",
) -> Image.Image:
    """
    Runs Real-ESRGAN NCNN Vulkan locally using subprocess.
    Works offline after executable setup.
    """

    exe_path = find_realesrgan_exe()

    if exe_path is None:
        raise FileNotFoundError(get_realesrgan_setup_message())

    models_dir = get_realesrgan_models_dir(exe_path)

    if not models_dir.exists():
        raise FileNotFoundError(get_realesrgan_setup_message())

    unique_id = uuid.uuid4().hex

    input_path = TEMP_DIR / f"realesrgan_input_{unique_id}.png"
    output_path = TEMP_DIR / f"realesrgan_output_{unique_id}.png"

    image.convert("RGB").save(input_path)

    command = [
    str(exe_path),
    "-i",
    str(input_path),
    "-o",
    str(output_path),
    "-n",
    model_name,
    "-s",
    str(scale),
    "-m",
    str(models_dir),
    "-j",
    "1:1:1",
    "-g",
    "0",
    "-f",
    "png",
]

    result = subprocess.run(
        command,
        cwd=str(exe_path.parent),
        capture_output=True,
        text=True,
    )

    if result.returncode != 0:
        raise RuntimeError(
            "Real-ESRGAN failed.\n\n"
            f"Command:\n{' '.join(command)}\n\n"
            f"STDOUT:\n{result.stdout}\n\n"
            f"STDERR:\n{result.stderr}"
        )

    if not output_path.exists():
        raise RuntimeError("Real-ESRGAN did not generate output image.")

    enhanced_image = Image.open(output_path).convert("RGB")

    return enhanced_image