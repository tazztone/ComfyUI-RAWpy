# ComfyUI RAW Image Loader

![V3 Compatible](https://img.shields.io/badge/ComfyUI-V3%20API-green)
![License](https://img.shields.io/github/license/dimtion/comfyui-raw-image)

A custom node extension for [ComfyUI](https://github.com/comfyanonymous/ComfyUI) that enables high-quality loading and processing of RAW image files directly into your workflows.
A [ComfyUI](https://github.com/comfyanonymous/ComfyUI) custom node for loading and processing RAW image files using `rawpy` (LibRaw).

![Screenshot of the tool](.github/img/node-screenshot.png)

## Features

- **Standard & Advanced Nodes**:
  - `Load RAW Image (Simple)`: Quick loading with essential settings.
  - `Load RAW Image (Advanced)`: Full professional control over the development pipeline.
- **High Quality Pipeline**:
  - **16-bit Output**: Process in high bit-depth to preserve dynamic range.
  - **Demosaicing Control**: Select algorithms from AHD (default) to AMAZE (high quality) or LINEAR (fast).
  - **Color Science**: Select output colorspace (sRGB, Adobe RGB, ProPhoto, Rec2020) and custom gamma curves.
- **Exposure & Correction**:
  - **Exposure Shift**: Linear exposure adjustment with highlight preservation.
  - **White Balance**: Camera, Auto, Daylight, or Custom RGB multipliers.
  - **Optical Correction**: Chromatic aberration correction and manual orientation override.
- **V3 API**: Built on the modern ComfyUI `io.ComfyNode` schema.

## Installation

### Prerequisites

- ComfyUI installed and working
- Python 3.8+ environment

### Install Steps

1. Clone this repository into your ComfyUI custom nodes directory:

```bash
cd ComfyUI/custom_nodes/
git clone https://github.com/your-repo/ComfyUI-RAWpy.git
```

2. Install the required dependencies:

```bash
pip install -r requirements.txt
```

3. Restart ComfyUI

## Development & Testing

This repository includes a `pytest` suite with mocked `rawpy` interactions.

1. Install test dependencies:
   ```bash
   pip install -e ".[dev]"
   ```
2. Run tests:
   ```bash
   pytest
   ```

## Nodes

### Load RAW Image (Simple)
- **Image**: Select RAW file.
- **Output 16-bit**: Enable for higher quality float32 tensors.
- **White Balance**: Camera / Auto / Daylight.
- **Highlight Mode**: Clip / Ignore / Blend / Reconstruct.

### Load RAW Image (Advanced)
Exposes all parameters including:
- Custom White Balance multipliers
- Demosaicing Algorithm (AHD, VNG, PPG, DCB, AMAZE, etc.)
- Output Color Space & Gamma
- Exposure Shift & Highlight Preservation
- Chromatic Aberration Correction

## Usage

1. Place your RAW image files in your ComfyUI input directory
2. In the ComfyUI interface, add the "Load RAW image" node to your workflow
3. Select your RAW file from the dropdown
4. Configure the processing options:
   - **use_auto_bright**: Enable/disable automatic brightness adjustment
   - **bright_adjustment**: Fine-tune brightness (0.1-3.0)
   - **highlight_mode**: Choose how to handle highlights in the image
     - clip: Clip highlights to maximum value
     - ignore: Preserve highlight values
     - blend: Blend highlight areas
     - reconstruct: Attempt to reconstruct highlight details

## Supported File Formats

Supports all RAW formats handled by the [rawpy library](https://www.libraw.org/supported-cameras), including:
- Canon (CR2, CR3)
- Nikon (NEF)
- Sony (ARW)
- Fujifilm (RAF)
- And many more

## License

[MIT License](LICENSE)

## Acknowledgements

- [rawpy](https://github.com/letmaik/rawpy) for RAW image processing
