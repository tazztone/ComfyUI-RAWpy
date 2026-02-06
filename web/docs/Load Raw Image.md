# Load RAW Image 📷

Only available in **ComfyUI-RAWpy**.

## Description
Loads a RAW image file (CR2, NEF, ARW, RAF, etc.) and processes it using LibRaw/rawpy into a standard image for ComfyUI. This extension uses a modern V3 API architecture and provides high-fidelity 16-bit processing.

## Nodes

### Load RAW Image (Simple)
Essential settings for daily use. Optimized for speed and ease of use.

#### Inputs
- **image**: Select the RAW file from your input directory.
- **output_16bit**: (Boolean) Keeps the full dynamic range of the RAW file (float32). Default: `True`.
- **white_balance**:
    - `camera`: Use the settings shot with the photo.
    - `auto`: Calculate WB from the image data.
    - `daylight`: Standard daylight preset (~5500K).
- **highlight_mode**:
    - `clip`: Standard, clips white to max.
    - `blend`: Blends clipped channels (fixes pink highlights).
    - `reconstruct`: Estimates missing data (slower but best results).
- **half_size**: (Boolean) Develop at half resolution (4x faster). Great for quick drafts.

### Load RAW Image (Advanced)
Full professional control over the development pipeline, including denoising and color science.

#### Inputs
- **White Balance**: Custom RGBG multipliers support when set to `custom`.
- **Demosaicing**: Choice of algorithms (AHD, AMAZE, PPG, VNG, etc.).
- **Exposure & Color**: Manual exposure shift, highlight preservation, and custom color space/gamma curves.
- **Denoising**: Wavelet denoising (`noise_thr`) and impulse noise reduction (`fbdd`).
- **Correction**: Chromatic aberration correction and manual orientation override.

## Outputs
- **IMAGE**: The main developed RGB image (processed via rawpy).
- **preview**: High-resolution embedded JPEG/Bitmap extracted directly from the RAW file for fast visualization.
- **thumbnail**: Tiny, highly-optimized thumbnail extracted via **ExifTool** (if available) for efficient gallery browsing.

## 📁 Example Workflows
This extension includes built-in templates to help you get started:
1. Open the **Workflow Templates** menu in ComfyUI.
2. Look for the **ComfyUI-RAWpy** category.
3. Select **basic_raw_load** to load a pre-configured graph.
