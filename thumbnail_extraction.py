"""
Thumbnail extraction using ExifTool.

This module provides functions to extract specific embedded images from RAW files
using ExifTool, which can target individual tags like ThumbnailImage vs PreviewImage.

This is isolated from ComfyUI dependencies to allow for clean unit testing.
"""

import subprocess
import io
from typing import Optional, Literal, Tuple
import numpy as np
import torch
from PIL import Image


def is_exiftool_available() -> bool:
    """Check if exiftool is installed and accessible."""
    try:
        result = subprocess.run(["exiftool", "-ver"], capture_output=True, timeout=5)
        return result.returncode == 0
    except (FileNotFoundError, subprocess.TimeoutExpired):
        return False


def extract_thumbnail_exiftool(
    raw_path: str,
    thumbnail_type: Literal[
        "ThumbnailImage", "PreviewImage", "JpgFromRaw"
    ] = "ThumbnailImage",
) -> Optional[bytes]:
    """
    Extract specific embedded thumbnail using ExifTool.

    Args:
        raw_path: Path to RAW file
        thumbnail_type: Which embedded image to extract
            - ThumbnailImage: Small ~4KB thumbnail (IFD1)
            - PreviewImage: Medium ~150KB preview (IFD0)
            - JpgFromRaw: Full-size JPEG render (IFD2)

    Returns:
        Binary JPEG data or None if extraction fails
    """
    try:
        result = subprocess.run(
            ["exiftool", "-b", f"-{thumbnail_type}", raw_path],
            capture_output=True,
            check=True,
            timeout=10,
        )
        return result.stdout if result.stdout else None
    except (
        subprocess.CalledProcessError,
        FileNotFoundError,
        subprocess.TimeoutExpired,
    ):
        return None


def bytes_to_tensor(jpeg_bytes: bytes) -> torch.Tensor:
    """
    Convert JPEG bytes to ComfyUI-compatible tensor [B, H, W, C].

    Args:
        jpeg_bytes: Raw JPEG binary data

    Returns:
        float32 tensor normalized to [0, 1]
    """
    pil_image = Image.open(io.BytesIO(jpeg_bytes))
    pil_image = pil_image.convert("RGB")
    array = np.array(pil_image).astype(np.float32) / 255.0
    return torch.from_numpy(array).unsqueeze(0)


def extract_all_thumbnails(
    raw_path: str,
) -> Tuple[Optional[torch.Tensor], Optional[torch.Tensor], Optional[torch.Tensor]]:
    """
    Extract all three embedded images from a RAW file.

    Returns:
        Tuple of (thumbnail, preview, jpg_from_raw) tensors.
        Any may be None if extraction fails.
    """
    thumbnail = None
    preview = None
    jpg_from_raw = None

    thumb_bytes = extract_thumbnail_exiftool(raw_path, "ThumbnailImage")
    if thumb_bytes:
        thumbnail = bytes_to_tensor(thumb_bytes)

    preview_bytes = extract_thumbnail_exiftool(raw_path, "PreviewImage")
    if preview_bytes:
        preview = bytes_to_tensor(preview_bytes)

    jpg_bytes = extract_thumbnail_exiftool(raw_path, "JpgFromRaw")
    if jpg_bytes:
        jpg_from_raw = bytes_to_tensor(jpg_bytes)

    return thumbnail, preview, jpg_from_raw
