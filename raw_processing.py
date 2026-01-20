"""
Core RAW processing logic for ComfyUI-RAWpy.

This module is isolated from ComfyUI dependencies to allow for clean unit testing.
"""

import numpy as np
import rawpy
import torch

HIGHLIGHT_MODES = {
    "clip": rawpy.HighlightMode.Clip,
    "ignore": rawpy.HighlightMode.Ignore,
    "blend": rawpy.HighlightMode.Blend,
    "reconstruct": rawpy.HighlightMode.ReconstructDefault,
}

DEMOSAIC_ALGORITHMS = {
    "AHD": rawpy.DemosaicAlgorithm.AHD,
    "VNG": rawpy.DemosaicAlgorithm.VNG,
    "PPG": rawpy.DemosaicAlgorithm.PPG,
    "DCB": rawpy.DemosaicAlgorithm.DCB,
    "AMAZE": rawpy.DemosaicAlgorithm.AMAZE,
    "LINEAR": rawpy.DemosaicAlgorithm.LINEAR,
    "DHT": rawpy.DemosaicAlgorithm.DHT,
}

OUTPUT_COLORSPACES = {
    "sRGB": rawpy.ColorSpace.sRGB,
    "Adobe RGB": rawpy.ColorSpace.Adobe,
    "ProPhoto": rawpy.ColorSpace.ProPhoto,
    "Wide Gamut": rawpy.ColorSpace.Wide,
    "XYZ": rawpy.ColorSpace.XYZ,
    "ACES": rawpy.ColorSpace.ACES,
    "Rec2020": rawpy.ColorSpace.Rec2020,
    "raw": rawpy.ColorSpace.raw,
}

ORIENTATION_MAP = {
    "auto": None,
    "none": 0,
    "180°": 3,
    "90° CW": 6,
    "90° CCW": 5,
}


def process_raw(
    image_path,
    output_16bit=True,
    white_balance="camera",
    custom_wb=(1.0, 1.0, 1.0, 1.0),
    demosaic_key="AHD",
    orientation_key="auto",
    use_auto_bright=True,
    bright_adjustment=1.0,
    highlight_mode_key="clip",
    colorspace_key="sRGB",
    gamma=(2.222, 4.5),
    exp_shift=1.0,
    exp_preserve_highlights=0.0,
    chromatic_aberration=(1.0, 1.0),
):
    """
    Process a RAW image file and return a torch tensor.

    This function handles the interaction with rawpy and the conversion
    to the format expected by ComfyUI (float32 tensor [B, H, W, C]).
    """
    bps = 16 if output_16bit else 8

    # Prepare arguments for postprocess
    pp_args = {
        "output_bps": bps,
        "demosaic_algorithm": DEMOSAIC_ALGORITHMS.get(
            demosaic_key, rawpy.DemosaicAlgorithm.AHD
        ),
        "bright": bright_adjustment,
        "no_auto_bright": not use_auto_bright,
        "highlight_mode": HIGHLIGHT_MODES.get(
            highlight_mode_key, rawpy.HighlightMode.Clip
        ),
        "user_flip": ORIENTATION_MAP.get(orientation_key),
        "output_color": OUTPUT_COLORSPACES.get(colorspace_key, rawpy.ColorSpace.sRGB),
        "gamma": gamma,
        "chromatic_aberration": chromatic_aberration,
    }

    # Exposure Shift
    pp_args["exp_shift"] = exp_shift
    pp_args["exp_preserve_highlights"] = exp_preserve_highlights

    # White Balance
    if white_balance == "camera":
        pp_args["use_camera_wb"] = True
    elif white_balance == "auto":
        pp_args["use_auto_wb"] = True
    elif white_balance == "custom":
        pp_args["user_wb"] = list(custom_wb)
    # else daylight (default)

    with rawpy.imread(image_path) as raw:
        rgb = raw.postprocess(**pp_args)

        # Try to extract embedded thumbnail
        try:
            thumb = raw.extract_thumb()
        except Exception:
            thumb = None

    # Process Thumbnail
    if thumb is not None:
        try:
            if thumb.format == rawpy.ThumbFormat.JPEG:
                import io
                from PIL import Image

                # thumb.data is bytes
                pil_image = Image.open(io.BytesIO(thumb.data))
                # Convert to RGB if needed (JPEGs usually are, but safety first)
                pil_image = pil_image.convert("RGB")
                thumb_array = np.array(pil_image).astype(np.float32) / 255.0
            elif thumb.format == rawpy.ThumbFormat.BITMAP:
                # thumb.data is numpy array
                thumb_array = thumb.data.astype(np.float32) / 255.0
            else:
                # Unknown format, fallback
                thumb_array = np.zeros((1, 1, 3), dtype=np.float32)
        except Exception:
            thumb_array = np.zeros((1, 1, 3), dtype=np.float32)
    else:
        # No thumbnail found, return 1x1 black image
        thumb_array = np.zeros((1, 1, 3), dtype=np.float32)

    # Ensure thumbnail has 3 channels
    if thumb_array.ndim == 2:
        thumb_array = np.stack([thumb_array] * 3, axis=-1)

    thumb_tensor = torch.from_numpy(thumb_array).unsqueeze(0)

    # Convert to standard ComfyUI format (float32 [0,1])
    # rawpy output -> (H, W, 3) numpy array
    divisor = 65535.0 if output_16bit else 255.0
    img_array = rgb.astype(np.float32) / divisor

    # Convert numpy array to torch tensor
    return torch.from_numpy(img_array).unsqueeze(0), thumb_tensor
