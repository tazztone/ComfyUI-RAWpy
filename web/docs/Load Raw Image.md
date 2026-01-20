# Load RAW Image 📷

Only available in **ComfyUI-RAWpy**.

## Description
Loads a RAW image file (CR2, NEF, ARW, RAF, etc.) and processes it using LibRaw/rawpy into a standard image for ComfyUI.

## Inputs
- **image**: Select the RAW file from your input directory.
- **use_auto_bright**: (Boolean) Automatically adjust brightness using LibRaw's auto-scale. Default: `True`.
- **bright_adjustment**: (Float) Manually scale brightness. 1.0 is default.
- **highlight_mode**: How to handle highlights.
    - `clip`: Clip values (standard).
    - `ignore`: Do nothing.
    - `blend`: Blend highlights.
    - `reconstruct`: Attempt recovery.

## Outputs
- **IMAGE**: The processed RGB image.

## 📁 Example Workflows
This extension includes built-in templates to help you get started:
1. Open the **Workflow Templates** menu in ComfyUI.
2. Look for the **ComfyUI-RAWpy** category.
3. Select **basic_raw_load** to load a pre-configured graph.
