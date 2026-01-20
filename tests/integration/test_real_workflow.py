"""
Integration tests using REAL data.

These tests use the sample_raw_file fixture to actually decode an image.
"""

import pytest
import torch
import numpy as np


@pytest.mark.integration
class TestRealExecution:
    """Tests that run the full pipeline on a real file."""

    def test_load_real_raw_file(self, sample_raw_file):
        """
        Test loading the sample .ARW file.
        This verifies that rawpy can actually read the bitstream and produce a tensor.
        """
        # We need to patch folder_paths just to return the absolute path directly,
        # since our sample file might not be in the standard input directory.
        from unittest.mock import patch

        # Lazy import
        from nodes import LoadRawImage

        with patch("folder_paths.get_annotated_filepath") as mock_path:
            mock_path.return_value = sample_raw_file

            node = LoadRawImage()
            # Execute with defaults
            output = node.execute(image="placeholder.arw")

            image_batch = output[0]  # First output is the image tensor
            preview_batch = output[1]  # Second is preview

            # Checks
            assert isinstance(image_batch, torch.Tensor)
            assert image_batch.ndim == 4  # B,H,W,C
            assert image_batch.shape[0] == 1
            assert image_batch.shape[3] == 3

            # Valid range
            assert image_batch.min() >= 0.0
            assert image_batch.max() <= 1.0

            # Check for non-black image (real data should have content)
            assert image_batch.mean() > 0.01

            # Check preview
            assert isinstance(preview_batch, torch.Tensor)
            assert preview_batch.ndim == 4
            assert preview_batch.shape[3] == 3

    def test_preview_is_smaller_than_main_image(self, sample_raw_file):
        """
        CRITICAL BUG TEST:
        Verify that the preview output is the embedded thumbnail (small resolution),
        NOT the full resolution image.

        This was a real bug where extract_thumb() silently failed and preview
        returned the same resolution as the main image.
        """
        from unittest.mock import patch
        from nodes import LoadRawImage

        with patch("folder_paths.get_annotated_filepath") as mock_path:
            mock_path.return_value = sample_raw_file

            node = LoadRawImage()
            output = node.execute(image="placeholder.arw")

            image_batch = output[0]
            preview_batch = output[1]

            main_height = image_batch.shape[1]
            main_width = image_batch.shape[2]
            preview_height = preview_batch.shape[1]
            preview_width = preview_batch.shape[2]

            # The preview should be SIGNIFICANTLY smaller than the main image
            # A typical RAW file is 6000x4000, while embedded JPEGs are usually 160x120 to 1600x1200
            # We assert preview is at most 50% of the main image dimensions
            assert preview_height < main_height * 0.5, (
                f"Preview height {preview_height} should be much smaller than main {main_height}. "
                "Thumbnail extraction likely failed!"
            )
            assert preview_width < main_width * 0.5, (
                f"Preview width {preview_width} should be much smaller than main {main_width}. "
                "Thumbnail extraction likely failed!"
            )

            # Also verify preview is not a 1x1 fallback black pixel
            assert preview_height > 1 and preview_width > 1, (
                "Preview is 1x1, indicating thumbnail extraction failed entirely."
            )
