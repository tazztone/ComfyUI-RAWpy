import folder_paths
import hashlib
import numpy as np

import os
from comfy_api.latest import io, ui
from .raw_processing import (
    process_raw,
    HIGHLIGHT_MODES,
    DEMOSAIC_ALGORITHMS,
    OUTPUT_COLORSPACES,
    ORIENTATION_MAP,
)


def _get_files():
    input_dir = folder_paths.get_input_directory()
    files = [
        f for f in os.listdir(input_dir) if os.path.isfile(os.path.join(input_dir, f))
    ]
    return sorted(files)


class LoadRawImage(io.ComfyNode):
    """Simple Load RAW Image node with essential settings."""

    @classmethod
    def define_schema(cls):
        return io.Schema(
            node_id="Load Raw Image",
            display_name="Load RAW Image (Simple) 📷",
            category="image/raw",
            description="Load a RAW image with essential settings.",
            inputs=[
                io.Combo.Input("image", _get_files(), image_upload=True),
                io.Boolean.Input(
                    "output_16bit",
                    default=True,
                    tooltip="Output 16-bit high dynamic range (float32)",
                ),
                io.Combo.Input(
                    "white_balance",
                    ["camera", "auto", "daylight"],
                    default="camera",
                    tooltip="White Balance Mode",
                ),
                io.Combo.Input(
                    "highlight_mode",
                    list(HIGHLIGHT_MODES.keys()),
                    default="clip",
                    tooltip="Highlight Reconstruction Mode",
                ),
            ],
            outputs=[io.Image.Output()],
        )

    @classmethod
    def execute(
        cls, image, output_16bit=True, white_balance="camera", highlight_mode="clip"
    ) -> io.NodeOutput:
        image_path = folder_paths.get_annotated_filepath(image)
        try:
            tensor = process_raw(
                image_path,
                output_16bit=output_16bit,
                white_balance=white_balance,
                highlight_mode_key=highlight_mode,
            )
            return io.NodeOutput(tensor)
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
                io.Combo.Input("image", _get_files(), image_upload=True),
                io.Boolean.Input(
                    "output_16bit",
                    default=True,
                    tooltip="Output 16-bit high dynamic range",
                ),
                # White Balance
                io.Combo.Input(
                    "white_balance",
                    ["camera", "auto", "daylight", "custom"],
                    default="camera",
                ),
                io.Float.Input(
                    "custom_wb_r", default=1.0, min=0.1, max=10.0, step=0.01
                ),
                io.Float.Input(
                    "custom_wb_g1", default=1.0, min=0.1, max=10.0, step=0.01
                ),
                io.Float.Input(
                    "custom_wb_b", default=1.0, min=0.1, max=10.0, step=0.01
                ),
                io.Float.Input(
                    "custom_wb_g2", default=1.0, min=0.1, max=10.0, step=0.01
                ),
                # Image Characteristics
                io.Combo.Input(
                    "highlight_mode", list(HIGHLIGHT_MODES.keys()), default="clip"
                ),
                io.Boolean.Input("use_auto_bright", default=True),
                io.Float.Input(
                    "bright_adjustment", default=1.0, min=0.1, max=10.0, step=0.1
                ),
                # Optics & Demosaicing
                io.Combo.Input(
                    "demosaic_algorithm",
                    list(DEMOSAIC_ALGORITHMS.keys()),
                    default="AHD",
                ),
                io.Combo.Input(
                    "orientation", list(ORIENTATION_MAP.keys()), default="auto"
                ),
                io.Float.Input(
                    "ca_red_scale", default=1.0, min=0.8, max=1.2, step=0.001
                ),
                io.Float.Input(
                    "ca_blue_scale", default=1.0, min=0.8, max=1.2, step=0.001
                ),
                # Color Science
                io.Combo.Input(
                    "output_colorspace", list(OUTPUT_COLORSPACES.keys()), default="sRGB"
                ),
                io.Float.Input(
                    "gamma_power", default=2.222, min=0.1, max=6.0, step=0.001
                ),
                io.Float.Input("gamma_slope", default=4.5, min=0.0, max=20.0, step=0.1),
                io.Float.Input("exp_shift", default=1.0, min=0.25, max=8.0, step=0.05),
                io.Float.Input(
                    "exp_preserve_highlights", default=0.0, min=0.0, max=1.0, step=0.05
                ),
            ],
            outputs=[io.Image.Output()],
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
    ) -> io.NodeOutput:
        image_path = folder_paths.get_annotated_filepath(image)
        try:
            tensor = process_raw(
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
            )
            return io.NodeOutput(tensor)
        except Exception as e:
            raise RuntimeError(f"Failed to load RAW image: {str(e)}")


NODE_DISPLAY_NAME_MAPPINGS = {
    "Load Raw Image": "Load RAW Image (Simple) 📷",
    "Load Raw Image Advanced": "Load RAW Image (Advanced) 📷",
}
