# ComfyUI RAW Image Loader

![V3 Compatible](https://img.shields.io/badge/ComfyUI-V3%20API-green)
![License](https://img.shields.io/github/license/dimtion/comfyui-raw-image)

A custom node extension for [ComfyUI](https://github.com/comfyanonymous/ComfyUI) that enables high-quality loading and processing of RAW image files directly into your workflows.

![Screenshot of the tool](.github/img/node-screenshot.png)

## Features

- **Standardized V3 Node Architecture**: Fully compliant with the latest ComfyUI standards.
- **Universal RAW Support**: Loads files from almost any camera (Canon, Nikon, Sony, Fuji, etc.) via `LibRaw`.
- **Advanced Processing**: 
    - Automatic or Manual Brightness (Linear Gain).
    - Multiple Highlight Recovery modes (Clip, Blend, Reconstruct).
- **Workflow Templates**: Includes built-in example workflows (access via the "Workflow Templates" menu).

## Installation

### Prerequisites

- ComfyUI installed and working
- Python 3.8+ environment

### Install Steps

1. Clone this repository into your ComfyUI custom nodes directory:

```bash
cd ComfyUI/custom_nodes/
git clone https://github.com/dimtion/comfyui-raw-image.git
```

2. Install the required dependencies:

```bash
pip install -r requirements.txt
```

3. Restart ComfyUI

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
