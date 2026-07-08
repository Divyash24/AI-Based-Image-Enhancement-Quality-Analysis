def map_prompt_to_actions(prompt: str) -> list[str]:
    prompt = prompt.lower().strip()
    actions = []

    if "sharp" in prompt or "sharper" in prompt:
        actions.append("sharpen")

    if "clear" in prompt or "clarity" in prompt or "clearer" in prompt:
        actions.extend(["denoise", "sharpen"])

    if "noise" in prompt or "denoise" in prompt or "grain" in prompt:
        actions.append("denoise")

    if "low light" in prompt or "dark" in prompt or "bright" in prompt:
        actions.extend(["gamma_correction", "clahe"])

    if "contrast" in prompt:
        actions.append("contrast_correction")

    if "color" in prompt or "colour" in prompt or "colorful" in prompt or "saturation" in prompt:
        actions.append("saturation_boost")

    if "upscale" in prompt or "resolution" in prompt or "4k" in prompt:
        actions.append("realesrgan_upscale")

    if "text" in prompt:
        actions.extend(["contrast_correction", "sharpen"])

    if "face" in prompt or "details" in prompt:
        actions.extend(["denoise", "sharpen", "contrast_correction"])

    if not actions:
        actions.append("balanced_enhancement")

    return list(dict.fromkeys(actions))