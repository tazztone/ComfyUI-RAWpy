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
        assert mock_rawpy.postprocess.called, "postprocess should be called"
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

    def test_denoising_params_passed(self, mock_rawpy):
        """Verify denoising parameters are forwarded."""
        from raw_processing import FBDD_MODES

        process_raw(
            "test.arw",
            noise_thr=10.5,
            fbdd_noise_reduction="light",
            median_filter_passes=3,
        )
        call_args = mock_rawpy.postprocess.call_args
        assert call_args.kwargs["noise_thr"] == 10.5
        assert call_args.kwargs["fbdd_noise_reduction"] == FBDD_MODES["light"]
        assert call_args.kwargs["median_filter_passes"] == 3

    def test_half_size_passed(self, mock_rawpy):
        """Verify half_size parameter is forwarded."""
        process_raw("test.arw", half_size=True)
        call_args = mock_rawpy.postprocess.call_args
        assert call_args.kwargs["half_size"] is True

    def test_orientation_passed(self, mock_rawpy):
        """Verify orientation parameter is forwarded."""
        from raw_processing import ORIENTATION_MAP

        process_raw("test.arw", orientation_key="90° CW")
        call_args = mock_rawpy.postprocess.call_args
        assert call_args.kwargs["user_flip"] == ORIENTATION_MAP["90° CW"]

    def test_colorspace_passed(self, mock_rawpy):
        """Verify colorspace parameter is forwarded."""
        from raw_processing import OUTPUT_COLORSPACES

        process_raw("test.arw", colorspace_key="Adobe RGB")
        call_args = mock_rawpy.postprocess.call_args
        assert call_args.kwargs["output_color"] == OUTPUT_COLORSPACES["Adobe RGB"]

    def test_gamma_passed(self, mock_rawpy):
        """Verify gamma tuple is forwarded."""
        process_raw("test.arw", gamma=(1.0, 1.0))
        call_args = mock_rawpy.postprocess.call_args
        assert call_args.kwargs["gamma"] == (1.0, 1.0)

    def test_chromatic_aberration_passed(self, mock_rawpy):
        """Verify CA tuple is forwarded."""
        process_raw("test.arw", chromatic_aberration=(1.1, 0.9))
        call_args = mock_rawpy.postprocess.call_args
        assert call_args.kwargs["chromatic_aberration"] == (1.1, 0.9)

    def test_auto_wb_flag(self, mock_rawpy):
        """Verify use_auto_wb flag is set."""
        process_raw("test.arw", white_balance="auto")
        call_args = mock_rawpy.postprocess.call_args
        assert call_args.kwargs.get("use_auto_wb") is True
        assert "use_camera_wb" not in call_args.kwargs

    def test_thumbnail_dimensions_correction(self, mock_rawpy):
        """Verify 2D thumbnail is expanded to 3D."""
        import rawpy
        from unittest.mock import MagicMock

        mock_thumb = MagicMock()
        mock_thumb.format = rawpy.ThumbFormat.BITMAP
        # Create a single channel 2D image
        mock_thumb.data = np.full((10, 10), 128, dtype=np.uint8)

        mock_rawpy.extract_thumb.return_value = mock_thumb

        _, preview = process_raw("test.arw")

        assert preview.shape == (1, 10, 10, 3)
        # Should be grayscale (all channels equal)
        assert preview[0, 0, 0, 0] == preview[0, 0, 0, 1] == preview[0, 0, 0, 2]
