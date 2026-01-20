"""
Unit tests for ExifTool-based thumbnail extraction.
"""

import pytest
from unittest.mock import patch, MagicMock
import numpy as np
import torch


@pytest.mark.unit
class TestThumbnailExtraction:
    """Tests for the thumbnail_extraction module."""

    def test_is_exiftool_available_success(self):
        """Test detection of ExifTool when available."""
        from thumbnail_extraction import is_exiftool_available

        with patch("subprocess.run") as mock_run:
            mock_run.return_value = MagicMock(returncode=0)
            assert is_exiftool_available() is True

    def test_is_exiftool_available_not_found(self):
        """Test detection when ExifTool is not installed."""
        from thumbnail_extraction import is_exiftool_available

        with patch("subprocess.run", side_effect=FileNotFoundError):
            assert is_exiftool_available() is False

    def test_extract_thumbnail_exiftool_success(self):
        """Test successful thumbnail extraction."""
        from thumbnail_extraction import extract_thumbnail_exiftool

        fake_jpeg_bytes = b"\xff\xd8\xff\xe0" + b"\x00" * 100  # Fake JPEG header

        with patch("subprocess.run") as mock_run:
            mock_run.return_value = MagicMock(returncode=0, stdout=fake_jpeg_bytes)
            result = extract_thumbnail_exiftool("test.arw", "ThumbnailImage")
            assert result == fake_jpeg_bytes

    def test_extract_thumbnail_exiftool_failure(self):
        """Test graceful failure when extraction fails."""
        from thumbnail_extraction import extract_thumbnail_exiftool
        import subprocess

        with patch(
            "subprocess.run", side_effect=subprocess.CalledProcessError(1, "exiftool")
        ):
            result = extract_thumbnail_exiftool("test.arw", "ThumbnailImage")
            assert result is None

    def test_bytes_to_tensor_shape(self):
        """Test conversion of JPEG bytes to tensor."""
        from thumbnail_extraction import bytes_to_tensor
        from PIL import Image
        import io

        # Create a small test image
        img = Image.new("RGB", (50, 30), color="blue")
        buffer = io.BytesIO()
        img.save(buffer, format="JPEG")
        jpeg_bytes = buffer.getvalue()

        tensor = bytes_to_tensor(jpeg_bytes)

        assert isinstance(tensor, torch.Tensor)
        assert tensor.ndim == 4
        assert tensor.shape == (1, 30, 50, 3)  # B, H, W, C
        assert tensor.dtype == torch.float32
        assert tensor.min() >= 0.0
        assert tensor.max() <= 1.0
