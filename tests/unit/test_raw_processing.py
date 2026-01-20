"""
Unit tests for isolated RAW processing logic.

These tests import `raw_processing` directly, avoiding all ComfyUI dependencies.
"""

import pytest
import numpy as np
import torch
from raw_processing import (
    process_raw,
    DEMOSAIC_ALGORITHMS,
    OUTPUT_COLORSPACES,
    HIGHLIGHT_MODES,
)


@pytest.mark.unit
class TestRawProcessing:
    """Tests for the isolated process_raw function."""

    def test_returns_correct_shape(self, mock_rawpy):
        """Verify output tensor has correct shape (B, H, W, C)."""
        image, preview = process_raw(
            "test.arw",
            output_16bit=True,
            white_balance="camera",
            highlight_mode_key="clip",
        )
        assert image.shape == (1, 100, 100, 3)
        assert image.dtype == torch.float32
        # Preview should be 1x1 black pixel by default in mock if not set
        assert preview.shape == (1, 1, 1, 3)

    def test_16bit_normalization(self, mock_rawpy):
        """Verify 16-bit values are normalized to [0, 1]."""
        mock_rawpy.postprocess.return_value = np.full(
            (10, 10, 3), 65535, dtype=np.uint16
        )
        image, _ = process_raw("test.arw", output_16bit=True)
        assert image.max() == pytest.approx(1.0, rel=0.01)

    def test_8bit_normalization(self, mock_rawpy):
        """Verify 8-bit values are normalized to [0, 1]."""
        mock_rawpy.postprocess.return_value = np.full((10, 10, 3), 255, dtype=np.uint8)
        image, _ = process_raw("test.arw", output_16bit=False)
        assert image.max() == pytest.approx(1.0, rel=0.01)

    def test_custom_white_balance_passed(self, mock_rawpy):
        """Verify custom white balance values are passed to rawpy."""
        process_raw("test.arw", white_balance="custom", custom_wb=(1.5, 1.0, 1.2, 1.0))
        mock_rawpy.postprocess.assert_called_once()
        call_args = mock_rawpy.postprocess.call_args
        assert call_args.kwargs["user_wb"] == [1.5, 1.0, 1.2, 1.0]

    def test_demosaic_algorithm_passed(self, mock_rawpy):
        """Verify demosaic algorithm enum is correctly resolved."""
        process_raw("test.arw", demosaic_key="AMAZE")
        call_args = mock_rawpy.postprocess.call_args
        assert call_args.kwargs["demosaic_algorithm"] == DEMOSAIC_ALGORITHMS["AMAZE"]

    def test_exposure_shift_passed(self, mock_rawpy):
        """Verify exposure shift parameters are forwarded."""
        process_raw("test.arw", exp_shift=2.0, exp_preserve_highlights=0.5)
        call_args = mock_rawpy.postprocess.call_args
        assert call_args.kwargs["exp_shift"] == 2.0
        assert call_args.kwargs["exp_preserve_highlights"] == 0.5

    def test_extract_jpeg_thumbnail(self, mock_rawpy):
        """Verify JPEG thumbnail extraction."""
        import rawpy
        from unittest.mock import MagicMock
        from PIL import Image
        import io

        # Create a fake JPEG
        img = Image.new("RGB", (50, 50), color="red")
        img_byte_arr = io.BytesIO()
        img.save(img_byte_arr, format="JPEG")
        jpeg_bytes = img_byte_arr.getvalue()

        mock_thumb = MagicMock()
        mock_thumb.format = rawpy.ThumbFormat.JPEG
        mock_thumb.data = jpeg_bytes

        mock_rawpy.extract_thumb.return_value = mock_thumb

        _, preview = process_raw("test.arw")

        assert preview.shape == (1, 50, 50, 3)
        # Red pixel should be approx (1.0, 0.0, 0.0)
        assert preview[0, 0, 0, 0] > 0.9
        assert preview[0, 0, 0, 1] < 0.1

    def test_extract_bitmap_thumbnail(self, mock_rawpy):
        """Verify Bitmap thumbnail extraction."""
        import rawpy
        from unittest.mock import MagicMock

        mock_thumb = MagicMock()
        mock_thumb.format = rawpy.ThumbFormat.BITMAP
        # Create a fake 20x20 RGB bitmap
        mock_thumb.data = np.full((20, 20, 3), 255, dtype=np.uint8)

        mock_rawpy.extract_thumb.return_value = mock_thumb

        _, preview = process_raw("test.arw")

        assert preview.shape == (1, 20, 20, 3)
        assert preview.max() == pytest.approx(1.0)

    def test_no_thumbnail_fallback(self, mock_rawpy):
        """Verify fallback when extract_thumb fails or returns None."""
        mock_rawpy.extract_thumb.side_effect = Exception("No thumb")

        _, preview = process_raw("test.arw")

        # Should be 1x1 black image
        assert preview.shape == (1, 1, 1, 3)
        assert preview.max() == 0.0
