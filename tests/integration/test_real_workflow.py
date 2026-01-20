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

    def test_thumbnail_is_small_via_exiftool(self, sample_raw_file):
        """
        Verify that the thumbnail output (via ExifTool) is the small embedded thumbnail.

        Sony ARW files contain 3 embedded images:
        - ThumbnailImage: ~4KB small thumbnail (extracted by ExifTool)
        - PreviewImage: ~150KB medium preview
        - JpgFromRaw: ~2.5MB full-res JPEG (returned by rawpy.extract_thumb())

        The node now outputs:
        - output[0]: Developed RAW image
        - output[1]: JpgFromRaw preview (from rawpy) - may be full-res
        - output[2]: ThumbnailImage (from ExifTool) - should be small
        """
        from unittest.mock import patch
        from nodes import LoadRawImage

        with patch("folder_paths.get_annotated_filepath") as mock_path:
            mock_path.return_value = sample_raw_file

            node = LoadRawImage()
            output = node.execute(image="placeholder.arw")

            image_batch = output[0]
            preview_batch = output[1]
            thumbnail_batch = output[2]

            main_height = image_batch.shape[1]
            main_width = image_batch.shape[2]
            thumbnail_height = thumbnail_batch.shape[1]
            thumbnail_width = thumbnail_batch.shape[2]

            # The ExifTool thumbnail should be TINY (usually 160x120 or similar)
            assert thumbnail_height < 500, (
                f"Thumbnail height {thumbnail_height} should be small (< 500px). "
                "ExifTool extraction may have failed."
            )
            assert thumbnail_width < 500, (
                f"Thumbnail width {thumbnail_width} should be small (< 500px). "
                "ExifTool extraction may have failed."
            )

            # Verify it's not a 1x1 fallback
            assert thumbnail_height > 1 and thumbnail_width > 1, (
                "Thumbnail is 1x1, indicating ExifTool extraction failed."
            )

            print(f"Main image: {main_width}x{main_height}")
            print(
                f"Preview (rawpy JpgFromRaw): {preview_batch.shape[2]}x{preview_batch.shape[1]}"
            )
            print(f"Thumbnail (ExifTool): {thumbnail_width}x{thumbnail_height}")
