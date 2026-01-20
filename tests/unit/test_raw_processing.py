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
        result = process_raw(
            "test.arw",
            output_16bit=True,
            white_balance="camera",
            highlight_mode_key="clip",
        )
        assert result.shape == (1, 100, 100, 3)
        assert result.dtype == torch.float32

    def test_16bit_normalization(self, mock_rawpy):
        """Verify 16-bit values are normalized to [0, 1]."""
        mock_rawpy.postprocess.return_value = np.full(
            (10, 10, 3), 65535, dtype=np.uint16
        )
        result = process_raw("test.arw", output_16bit=True)
        assert result.max() == pytest.approx(1.0, rel=0.01)

    def test_8bit_normalization(self, mock_rawpy):
        """Verify 8-bit values are normalized to [0, 1]."""
        mock_rawpy.postprocess.return_value = np.full((10, 10, 3), 255, dtype=np.uint8)
        result = process_raw("test.arw", output_16bit=False)
        assert result.max() == pytest.approx(1.0, rel=0.01)

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
