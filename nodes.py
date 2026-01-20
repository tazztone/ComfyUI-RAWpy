import folder_paths
import hashlib
import numpy as np
import os
import rawpy
import torch
import comfy.io as io
from PIL import Image

HIGHLIGHT_MODES = {
    "clip": rawpy.HighlightMode.Clip,
    "ignore": rawpy.HighlightMode.Ignore,
    "blend": rawpy.HighlightMode.Blend,
    "reconstruct": rawpy.HighlightMode.ReconstructDefault,
}


class LoadRawImage(io.ComfyNode):
    """Load a RAW image."""

    @classmethod
    def define_schema(cls):
        input_dir = folder_paths.get_input_directory()
        files = [
            f
            for f in os.listdir(input_dir)
            if os.path.isfile(os.path.join(input_dir, f))
        ]

        return io.Schema(
            node_id="Load Raw Image",
            display_name="Load RAW Image 📷",
            category="image",
            description="Load a RAW image into ComfyUI.",
            inputs=[
                io.Combo.Input(
                    "image", sorted(files), image_upload=True, tooltip="Image to load."
                ),
                io.Boolean.Input(
                    "use_auto_bright",
                    default=True,
                    tooltip="automatic increase of brightness",
                ),
                io.Float.Input(
                    "bright_adjustment", default=1.0, min=0.1, max=3.0, step=0.1
                ),
                io.Combo.Input(
                    "highlight_mode", list(HIGHLIGHT_MODES.keys()), default="clip"
                ),
            ],
            outputs=[io.Image.Output()],
        )

    @classmethod
    def IS_CHANGED(cls, image, **kwargs):
        # Note: In V3 IS_CHANGED is still relevant for caching, but the signature might need check.
        # Assuming V1 style static method works or adapting logic if necessary.
        # The V3 guide suggests IS_CHANGED override is still valid or part of schema options.
        # For now, we'll keep the logic but simpler.
        image_path = folder_paths.get_annotated_filepath(image)
        m = hashlib.sha256()
        try:
            with open(image_path, "rb") as f:
                m.update(f.read())
            return m.digest().hex()
        except Exception:
            return float("nan")

    @classmethod
    def execute(
        cls, image, use_auto_bright=True, bright_adjustment=1.0, highlight_mode="clip"
    ):
        image_path = folder_paths.get_annotated_filepath(image)

        try:
            with rawpy.imread(image_path) as raw:
                rgb = raw.postprocess(
                    bright=bright_adjustment,
                    highlight_mode=HIGHLIGHT_MODES[highlight_mode],
                    no_auto_bright=not use_auto_bright,
                    output_bps=8,
                )

            img = Image.fromarray(rgb)

            if img.mode != "RGB":
                img = img.convert("RGB")

            # Convert to numpy array normalized to 0-1 range as expected by ComfyUI
            img_array = np.array(img).astype(np.float32) / 255.0
            img_array = torch.from_numpy(img_array).unsqueeze(0)

            return io.NodeOutput(img_array)

        except Exception as e:
            raise RuntimeError(f"Failed to load RAW image: {str(e)}")


NODE_DISPLAY_NAME_MAPPINGS = {"Load Raw Image": "Load RAW Image 📷"}
