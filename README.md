# ComfyUI RAW Image Loader

A custom node extension for [ComfyUI](https://github.com/comfyanonymous/ComfyUI) improved upon fork from [dimtion/comfyui-raw-image](https://github.com/dimtion/comfyui-raw-image) that enables high-quality loading and processing of RAW image files directly into your workflows using `rawpy` (LibRaw) and `ExifTool`.

![Screenshot of the tool](.github/img/node-screenshot.png)

## Features

- **Standard & Advanced Nodes**:
  - `Load RAW Image (Simple)`: Quick loading with essential settings and fast draft mode.
  - `Load RAW Image (Advanced)`: Full professional control over the development pipeline.
- **Modern V3 API Architecture**: Built from the ground up on the modern ComfyUI `io.ComfyNode` schema, ensuring long-term compatibility and better UI integration.
- **Triple-Output System**:
  - **IMAGE**: The developed RAW image (processed via rawpy).
  - **preview**: High-resolution embedded JPEG/Bitmap (fast loading via LibRaw).
  - **thumbnail**: Tiny embedded thumbnail, highly optimized via **ExifTool** for superior performance in file browsers.
- **High Quality Pipeline**:
  - **16-bit Output**: Process in high bit-depth to preserve dynamic range (float32 tensors).
  - **Demosaicing Control**: Select algorithms from AHD (default) to AMAZE (high quality) or LINEAR (fast).
  - **Color Science**: Select output colorspace (sRGB, Adobe RGB, ProPhoto, Rec2020) and custom gamma curves.
- **Exposure & Correction**:
  - **Exposure Shift**: Linear exposure adjustment with highlight preservation.
  - **White Balance**: Camera, Auto, Daylight, or Custom RGB multipliers.
  - **Optical Correction**: Chromatic aberration correction and manual orientation override.

## Performance & Optimization

- **ExifTool Integration**: By leveraging ExifTool for thumbnail extraction, we bypass heavy image decoding for simple previews, making gallery browsing significantly faster.
- **Half-Size Development**: Enable `half_size` to develop images at 1/4 resolution for 4x faster processing during the experimentation phase.
- **Isolated Core Logic**: The RAW processing engine is decoupled from ComfyUI dependencies, allowing for high-performance execution and reliable unit testing.

## Installation

### Prerequisites

- ComfyUI installed and working
- Python 3.8+ environment
- **ExifTool (Highly Recommended)**: Required for high-speed small thumbnail extraction.
  - **Windows**: Download `exiftool.exe` from [exiftool.org](https://exiftool.org/) and place it in your system PATH.
  - **Linux**: `sudo apt install exiftool`
  - **macOS**: `brew install exiftool`

### Install Steps

1. Clone this repository into your ComfyUI custom nodes directory:

```bash
cd ComfyUI/custom_nodes/
git clone https://github.com/tazztone/ComfyUI-RAWpy.git
```

2. Install the required dependencies:

```bash
pip install -r requirements.txt
```

3. Restart ComfyUI

## Nodes

### Load RAW Image (Simple) 📷
Essential settings for daily use.
- **image**: Select RAW file.
- **output_16bit**: Enable for higher quality float32 tensors.
- **white_balance**: Camera / Auto / Daylight.
- **highlight_mode**: Clip / Blend / Reconstruct.
- **half_size**: Develop at half resolution (4x faster).
- **Outputs**: `IMAGE`, `preview`, `thumbnail`.

### Load RAW Image (Advanced) 📷
Full professional controls for fine-tuning.
- **White Balance**: Custom RGB multipliers (R, G1, B, G2).
- **Demosaicing**: AHD, VNG, PPG, DCB, AMAZE, LINEAR, DHT.
- **Orientation**: Auto or manual flip degrees.
- **Color Science**: Custom Output Colorspace and Gamma Corection.
- **Exposure**: Shift (EV) and Highlight Preservation.
- **Preprocessing**: Chromatic Aberration, Wavelet Denoise (noise_thr), FBDD Noise Reduction.
- **Outputs**: `IMAGE`, `preview`, `thumbnail`.

## Roadmap

This project is evolving into a professional metadata-driven workflow tool. Check [roadmap.md](roadmap.md) for details on:
- **Phase 2**: Camera MakerNotes & Lens Metadata extraction.
- **Phase 3**: Smart logic based on ISO/Focal Length.
- **Phase 5**: XMP sidecar support for Lightroom/Capture One compatibility.

## Supported File Formats

Supports all RAW formats handled by the [rawpy library](https://www.libraw.org/supported-cameras), including:
- Canon (CR2, CR3)
- Nikon (NEF)
- Sony (ARW)
- Fujifilm (RAF)
- DNG (Digital Negative)

## Quality & Testing

This project maintains a high standard of quality through an extensive test suite:
- **Unit Tests**: Verify core RAW processing logic in isolation.
- **Integration Tests**: Ensure seamless registration and execution within the ComfyUI server.
- **Dependency Mocking**: Tests are designed to run efficiently by mocking complex dependencies like LibRaw.

To run the tests:
```bash
python run_tests.py
```

## License

[MIT License](LICENSE)

## Acknowledgements

- [rawpy](https://github.com/letmaik/rawpy) for RAW image processing.
- [ExifTool](https://exiftool.org/) for superior metadata and thumbnail handling.
