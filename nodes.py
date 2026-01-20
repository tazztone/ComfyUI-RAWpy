import folder_paths
import hashlib
import numpy as np

import os
from comfy_api.latest import io, ui

try:
    from .raw_processing import (
        process_raw,
        HIGHLIGHT_MODES,
        DEMOSAIC_ALGORITHMS,
        OUTPUT_COLORSPACES,
        ORIENTATION_MAP,
    )
except ImportError:
    # Fallback for unit testing where nodes is imported as top-level
    from raw_processing import (
        process_raw,
        HIGHLIGHT_MODES,
        DEMOSAIC_ALGORITHMS,
        OUTPUT_COLORSPACES,
        ORIENTATION_MAP,
    )


def _get_files():
    input_dir = folder_paths.get_input_directory()
    files = []
    for root, dirs, filenames in os.walk(input_dir):
        for filename in filenames:
            files.append(os.path.relpath(os.path.join(root, filename), input_dir))
    return sorted(files)


class LoadRawImage(io.ComfyNode):
    """Simple Load RAW Image node with essential settings."""

    @classmethod
    def define_schema(cls):
        return io.Schema(
            node_id="Load Raw Image",
            display_name="Load RAW Image (Simple) 📷",
            category="image/raw",
            description="Load a RAW image with essential settings. Outputs the developed image, full-res preview (from rawpy), and small thumbnail (via ExifTool).",
            inputs=[
                io.Combo.Input("image", _get_files(), upload=io.UploadType.image),
                io.Boolean.Input(
                    "output_16bit",
                    default=True,
                    tooltip="High Quality Mode (16-bit): Keeps the full dynamic range of the RAW file (float32). Disable for standard 8-bit output (smaller memory usage).",
                ),
                io.Combo.Input(
                    "white_balance",
                    ["camera", "auto", "daylight"],
                    default="camera",
                    tooltip="• Camera: Use the settings shot with the photo.\n• Auto: Calculate WB from the image data.\n• Daylight: Standard daylight preset (~5500K).",
                ),
                io.Combo.Input(
                    "highlight_mode",
                    list(HIGHLIGHT_MODES.keys()),
                    default="clip",
                    tooltip="How to handle blown-out highlights:\n• Clip: Standard, clipls white to max.\n• Blend: Blends clipped channels (fixes pink highlights).\n• Reconstruct: Estimates missing data (slower but best).",
                ),
            ],
            outputs=[
                io.Image.Output(),
                io.Image.Output("preview"),
                io.Image.Output("thumbnail"),
            ],
        )

    @classmethod
    def execute(
        cls, image, output_16bit=True, white_balance="camera", highlight_mode="clip"
    ) -> io.NodeOutput:
        image_path = folder_paths.get_annotated_filepath(image)
        try:
            # Main RAW processing (image + preview from rawpy)
            image_tensor, preview_tensor = process_raw(
                image_path,
                output_16bit=output_16bit,
                white_balance=white_balance,
                highlight_mode_key=highlight_mode,
            )

            # Try to extract small thumbnail via ExifTool
            try:
                from .thumbnail_extraction import (
                    extract_thumbnail_exiftool,
                    bytes_to_tensor,
                    is_exiftool_available,
                )
            except ImportError:
                from thumbnail_extraction import (
                    extract_thumbnail_exiftool,
                    bytes_to_tensor,
                    is_exiftool_available,
                )

            thumbnail_tensor = None
            if is_exiftool_available():
                thumb_bytes = extract_thumbnail_exiftool(image_path, "ThumbnailImage")
                if thumb_bytes:
                    thumbnail_tensor = bytes_to_tensor(thumb_bytes)

            # Fallback: if ExifTool failed, use 1x1 black placeholder
            if thumbnail_tensor is None:
                import torch

                thumbnail_tensor = torch.zeros((1, 1, 1, 3))

            return io.NodeOutput(image_tensor, preview_tensor, thumbnail_tensor)
        except Exception as e:
            raise RuntimeError(f"Failed to load RAW image: {str(e)}")


class LoadRawImageAdvanced(io.ComfyNode):
    """Advanced Load RAW Image node with full control."""

    @classmethod
    def define_schema(cls):
        return io.Schema(
            node_id="Load Raw Image Advanced",
            display_name="Load RAW Image (Advanced) 📷",
            category="image/raw",
            description="Load a RAW image with professional control over all development parameters.",
            inputs=[
                # Core
                # Core
                io.Combo.Input(
                    "image",
                    _get_files(),
                    upload=io.UploadType.image,
                    tooltip="Select a raw file from your input directory (supports subfolders).",
                ),
                io.Boolean.Input(
                    "output_16bit",
                    default=True,
                    tooltip="High Quality Mode (16-bit): Keeps the full dynamic range of the RAW file (float32). Disable for standard 8-bit output (smaller memory usage).",
                ),
                # White Balance
                io.Combo.Input(
                    "white_balance",
                    ["camera", "auto", "daylight", "custom"],
                    default="camera",
                    tooltip="• Camera: As shot.\n• Auto: Calculated from image.\n• Daylight: Standard preset.\n• Custom: Use manual multipliers below.",
                ),
                io.Float.Input(
                    "custom_wb_r",
                    default=1.0,
                    min=0.1,
                    max=10.0,
                    step=0.01,
                    tooltip="Red multiplier (Only used when White Balance is 'Custom').",
                ),
                io.Float.Input(
                    "custom_wb_g1",
                    default=1.0,
                    min=0.1,
                    max=10.0,
                    step=0.01,
                    tooltip="Green1 multiplier (Only used when White Balance is 'Custom').",
                ),
                io.Float.Input(
                    "custom_wb_b",
                    default=1.0,
                    min=0.1,
                    max=10.0,
                    step=0.01,
                    tooltip="Blue multiplier (Only used when White Balance is 'Custom').",
                ),
                io.Float.Input(
                    "custom_wb_g2",
                    default=1.0,
                    min=0.1,
                    max=10.0,
                    step=0.01,
                    tooltip="Green2 multiplier (Only used when White Balance is 'Custom').",
                ),
                # Image Characteristics
                io.Combo.Input(
                    "highlight_mode",
                    list(HIGHLIGHT_MODES.keys()),
                    default="clip",
                    tooltip="How to handle blown-out highlights:\n• Clip: Standard.\n• Blend: Fixes pink highlights.\n• Reconstruct: Estimates missing details.",
                ),
                io.Boolean.Input(
                    "use_auto_bright",
                    default=True,
                    tooltip="Automatically stretch exposure to fill the histogram.",
                ),
                io.Float.Input(
                    "bright_adjustment",
                    default=1.0,
                    min=0.1,
                    max=10.0,
                    step=0.1,
                    tooltip="Brightness multiplier (1.0 = original).",
                ),
                # Optics & Demosaicing
                io.Combo.Input(
                    "demosaic_algorithm",
                    list(DEMOSAIC_ALGORITHMS.keys()),
                    default="AHD",
                    tooltip="Algorithm to convert Bayer pattern to RGB:\n• AHD: Adaptive Homogeneity (Best balance).\n• PPG: Patterned Pixel (Fast).\n• VNG: Variable Number of Gradients (Good for noise).\n• AMAZE: Aliasing Minimization (Sharpest).",
                ),
                io.Combo.Input(
                    "orientation",
                    list(ORIENTATION_MAP.keys()),
                    default="auto",
                    tooltip="Rotate/Flip image.\n• Auto: Use camera metadata.\n• None: Raw sensor orientation.",
                ),
                io.Float.Input(
                    "ca_red_scale",
                    default=1.0,
                    min=0.8,
                    max=1.2,
                    step=0.001,
                    tooltip="Chromatic Aberration Correction (Red channel scale).",
                ),
                io.Float.Input(
                    "ca_blue_scale",
                    default=1.0,
                    min=0.8,
                    max=1.2,
                    step=0.001,
                    tooltip="Chromatic Aberration Correction (Blue channel scale).",
                ),
                # Color Science
                io.Combo.Input(
                    "output_colorspace",
                    list(OUTPUT_COLORSPACES.keys()),
                    default="sRGB",
                    tooltip="Target color space for the output image.\n• sRGB: Standard web/screen.\n• Adobe RGB: Wider gamut (print).\n• ProPhoto: Extreme gamut.",
                ),
                io.Float.Input(
                    "gamma_power",
                    default=2.222,
                    min=0.1,
                    max=6.0,
                    step=0.001,
                    tooltip="Gamma encoding power.\n• 2.222: Standard sRGB.\n• 1.0: Linear response.",
                ),
                io.Float.Input(
                    "gamma_slope",
                    default=4.5,
                    min=0.0,
                    max=20.0,
                    step=0.1,
                    tooltip="Gamma curve slope at the origin (linear toe). Standard is 4.5.",
                ),
                io.Float.Input(
                    "exp_shift",
                    default=1.0,
                    min=0.25,
                    max=8.0,
                    step=0.05,
                    tooltip="Exposure push/pull before conversion (Digital exposure compensation).",
                ),
                io.Float.Input(
                    "exp_preserve_highlights",
                    default=0.0,
                    min=0.0,
                    max=1.0,
                    step=0.05,
                    tooltip="When shifting exposure logic, how much to preserve highlights from clipping (0.0 - 1.0).",
                ),
                # Denoising
                io.Float.Input(
                    "noise_thr",
                    default=0.0,
                    min=0.0,
                    max=100.0,
                    step=0.1,
                    tooltip="Wavelet Denoising Threshold. Higher values remove more noise but may blur details. 0 = Off.",
                ),
                io.Combo.Input(
                    "fbdd_noise_reduction",
                    ["off", "light", "full"],
                    default="off",
                    tooltip="Fix Bad Data Demosaicing (Impulse Noise Reduction). Reduces color artifacts from dead pixels.",
                ),
                io.Int.Input(
                    "median_filter_passes",
                    default=0,
                    min=0,
                    max=10,
                    tooltip="Number of post-demosaic 3x3 median filter passes to reduce color moiré.",
                ),
                # Performance
                io.Boolean.Input(
                    "half_size",
                    default=False,
                    tooltip="Develop the image at half resolution (4x faster). Great for previews.",
                ),
            ],
            outputs=[
                io.Image.Output(),
                io.Image.Output("preview"),
                io.Image.Output("thumbnail"),
            ],
        )

    @classmethod
    def execute(
        cls,
        image,
        output_16bit=True,
        white_balance="camera",
        custom_wb_r=1.0,
        custom_wb_g1=1.0,
        custom_wb_b=1.0,
        custom_wb_g2=1.0,
        highlight_mode="clip",
        use_auto_bright=True,
        bright_adjustment=1.0,
        demosaic_algorithm="AHD",
        orientation="auto",
        ca_red_scale=1.0,
        ca_blue_scale=1.0,
        output_colorspace="sRGB",
        gamma_power=2.222,
        gamma_slope=4.5,
        exp_shift=1.0,
        exp_preserve_highlights=0.0,
        noise_thr=0.0,
        fbdd_noise_reduction="off",
        median_filter_passes=0,
        half_size=False,
    ) -> io.NodeOutput:
        image_path = folder_paths.get_annotated_filepath(image)
        try:
            image_tensor, preview_tensor = process_raw(
                image_path,
                output_16bit=output_16bit,
                white_balance=white_balance,
                custom_wb=(custom_wb_r, custom_wb_g1, custom_wb_b, custom_wb_g2),
                demosaic_key=demosaic_algorithm,
                orientation_key=orientation,
                use_auto_bright=use_auto_bright,
                bright_adjustment=bright_adjustment,
                highlight_mode_key=highlight_mode,
                colorspace_key=output_colorspace,
                gamma=(gamma_power, gamma_slope),
                exp_shift=exp_shift,
                exp_preserve_highlights=exp_preserve_highlights,
                chromatic_aberration=(ca_red_scale, ca_blue_scale),
                noise_thr=noise_thr if noise_thr > 0 else None,
                fbdd_noise_reduction=fbdd_noise_reduction,
                median_filter_passes=median_filter_passes,
                half_size=half_size,
            )

            # Try to extract small thumbnail via ExifTool
            try:
                from .thumbnail_extraction import (
                    extract_thumbnail_exiftool,
                    bytes_to_tensor,
                    is_exiftool_available,
                )
            except ImportError:
                from thumbnail_extraction import (
                    extract_thumbnail_exiftool,
                    bytes_to_tensor,
                    is_exiftool_available,
                )

            thumbnail_tensor = None
            if is_exiftool_available():
                thumb_bytes = extract_thumbnail_exiftool(image_path, "ThumbnailImage")
                if thumb_bytes:
                    thumbnail_tensor = bytes_to_tensor(thumb_bytes)

            # Fallback: if ExifTool failed, use 1x1 black placeholder
            if thumbnail_tensor is None:
                import torch

                thumbnail_tensor = torch.zeros((1, 1, 1, 3))

            return io.NodeOutput(image_tensor, preview_tensor, thumbnail_tensor)
        except Exception as e:
            raise RuntimeError(f"Failed to load RAW image: {str(e)}")


NODE_DISPLAY_NAME_MAPPINGS = {
    "Load Raw Image": "Load RAW Image (Simple) 📷",
    "Load Raw Image Advanced": "Load RAW Image (Advanced) 📷",
}
