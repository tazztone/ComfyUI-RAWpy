"""
Unit tests for Node classes in nodes.py.

These tests verify that ComfyUI inputs are correctly mapped to process_raw arguments.
"""

import pytest
from unittest.mock import MagicMock, patch
import sys
import os


@pytest.mark.unit
class TestLoadRawImage:
    """Tests for the simple LoadRawImage node."""

    def test_execute_maps_correctly(self):
        """Verify inputs are correctly passed to process_raw."""
        # Lazy import to ensure mocks are active
        import folder_paths
        from nodes import LoadRawImage

        with patch("nodes.process_raw") as mock_process:
            # Mock return value (image, preview)
            mock_process.return_value = ("MOCK_IMAGE", "MOCK_PREVIEW")

            # Mock folder_paths
            folder_paths.get_annotated_filepath.return_value = "/abs/path/to/test.arw"

            node = LoadRawImage()
            result = node.execute(
                image="test.arw",
                output_16bit=False,
                white_balance="daylight",
                highlight_mode="blend",
            )

            # verify generic folder path resolution
            folder_paths.get_annotated_filepath.assert_called_with("test.arw")

            # verify process_raw call
            mock_process.assert_called_once_with(
                "/abs/path/to/test.arw",
                output_16bit=False,
                white_balance="daylight",
                highlight_mode_key="blend",
            )

            # verify output wrapping
            assert result[0] == "MOCK_IMAGE"
            assert result[1] == "MOCK_PREVIEW"

    def test_error_handling(self):
        """Verify runtime errors are raised."""
        from nodes import LoadRawImage

        with patch("nodes.process_raw") as mock_process:
            mock_process.side_effect = Exception("Corrupt file")

            node = LoadRawImage()
            with pytest.raises(RuntimeError, match="Failed to load RAW image"):
                node.execute(image="bad.arw")


@pytest.mark.unit
class TestLoadRawImageAdvanced:
    """Tests for the advanced node."""

    def test_advanced_mapping(self):
        """Verify all advanced parameters are passed correctly."""
        from nodes import LoadRawImageAdvanced

        with patch("nodes.process_raw") as mock_process:
            mock_process.return_value = (None, None)

            node = LoadRawImageAdvanced()
            node.execute(
                image="test.arw",
                custom_wb_r=1.5,
                custom_wb_g1=1.0,
                custom_wb_b=2.0,
                custom_wb_g2=1.0,
                gamma_power=1.0,
                gamma_slope=0.0,
                ca_red_scale=1.01,
                ca_blue_scale=0.99,
                noise_thr=5.0,
            )

            call_args = mock_process.call_args
            kwargs = call_args.kwargs

            # customized tuples check
            assert kwargs["custom_wb"] == (1.5, 1.0, 2.0, 1.0)
            assert kwargs["gamma"] == (1.0, 0.0)
            assert kwargs["chromatic_aberration"] == (1.01, 0.99)
            assert kwargs["noise_thr"] == 5.0
