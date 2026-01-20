# Agent Guide: ComfyUI-RAWpy

This document provides a comprehensive overview of the `ComfyUI-RAWpy` repository, designed to assist AI agents in understanding, maintaining, and extending the codebase.

## 🔭 Project Overview

`ComfyUI-RAWpy` is a custom node extension for [ComfyUI](https://github.com/comfyanonymous/ComfyUI) that enables high-quality loading and processing of RAW image files (Canon, Nikon, Sony, Fuji, etc.) directly within workflows using the `rawpy` library (a wrapper for LibRaw).

### Core Functionality
- **RAW Loading**: Supports a wide range of camera-specific RAW formats.
- **Exposure Control**: Toggleable automatic brightness and manual linear gain adjustment.
- **Highlight Recovery**: Multiple modes for handling overexposed regions (Clip, Ignore, Blend, Reconstruct).
- **Standardized Output**: Converts RAW data into the standard ComfyUI `IMAGE` format (Batch, Height, Width, Channels) tensor with values normalized to [0, 1].

## 🏗️ Architecture

The repository follows the standard ComfyUI custom node structure:

- `nodes.py`: Contains the definition and logic for the RAW loading nodes, fully compliant with **V3 API**.
- `__init__.py`: Handles node registration using the `ComfyExtension` class and `comfy_entrypoint`.
- `requirements.txt`: Specifies dependencies (`rawpy`, `numpy`, `Pillow`, `torch`).

## 🧩 Key Components

### `LoadRawImage` Class (in `nodes.py`)

This is the primary (and currently only) node in the extension. It is fully migrated to the **ComfyUI V3 API**.

#### Schema (V3)
- **Inheritance**: `io.ComfyNode`
- **Definition**: Uses `define_schema` to strictly type inputs and outputs.
- **Inputs**:
    - `image` (`io.Combo`): Path to RAW file.
    - `use_auto_bright` (`io.Boolean`): Auto-brightness toggle.
    - `bright_adjustment` (`io.Float`): Manual brightness multiplier.
    - `highlight_mode` (`io.Combo`): Highlight recovery mode.
- **Outputs**:
    - `IMAGE` (`io.Image`): Standard RGB tensor (the developed RAW image).
    - `preview` (`io.Image`): Extracted embedded JPEG/Bitmap preview (or black image if missing).

### `LoadRawImageAdvanced` Class
The advanced node offers professional control, including:
- **Denoising**:
    - `noise_thr`: Wavelet denoising threshold.
    - `fbdd_noise_reduction`: Impulse noise reduction (Off, Light, Full).
    - `median_filter_passes`: Post-demosaic filtering.
- **Performance**:
    - `half_size`: 4x speedup (half resolution) for drafts.

#### Execution Logic (`execute` method)
1. Opens the file using `rawpy.imread`.
2. Calls `raw.postprocess` with the specified parameters.
3. **Note**: Supports full 16-bit high dynamic range (float32) if `output_16bit` is enabled.
4. Extracts embedded thumbnail (JPEG/Bitmap) converting it to a secondary tensor.
5. Returns data wrapped in `io.NodeOutput`.

## 🛠️ Developmental Context

### Common Extension Patterns
- **16-bit Support**: ComfyUI handles float32 tensors. This node fully supports converting 16-bit RAW data into float32 tensors, preserving the dynamic range.
- **Debayering Options**: `rawpy` provides various interpolation methods (`AHD`, `VNG`, `PPG`, etc.). These could be exposed as input parameters.
- **White Balance**: Currently relies on `rawpy` defaults (usually camera WB). Methods like `use_camera_wb`, `user_flip`, and `auto_wb` could be added.

### Environment Setup
1. Dependencies are listed in `requirements.txt`.
2. `folder_paths` is a ComfyUI utility used for resolving file paths within the ecosystem.

## 🤝 Workflow Integration

The node outputs a standard `IMAGE` type, meaning it can be plugged directly into:
- VAE Encoders (for Stable Diffusion workflows).
- Image Previewers.
- Any standard ComfyUI image processing node (Reroute, Upscale, Crop, etc.).

## 🧪 Testing Guide

This repository uses a comprehensive test suite to ensure the stability of the nodes. The tests are designed to run both **standalone** (unit tests) and **integrated** (with a live ComfyUI server).

### 🚀 Quick Start

#### 1. Configure VS Code (Recommended)
This repository includes a `.vscode/settings.json` that pre-configures the correct Python environment and test arguments.

1.  Open this folder in VS Code.
2.  Go to the **Testing** tab (flask icon).
3.  Click "Refresh Tests".
4.  Run any test directly from the UI.

> **Note:** If tests are not found, ensure your Python interpreter is set to the ComfyUI virtual environment: `../../venv/Scripts/python.exe`.

#### 2. Run from Command Line
You can use the provided `run_tests.py` script which handles environment setup automatically.

```powershell
cd custom_nodes\ComfyUI-RAWpy

# Run ALL tests
..\..\venv\Scripts\python run_tests.py

# Run ONLY Unit Tests (Fast, no server needed)
..\..\venv\Scripts\python run_tests.py -m unit

# Run ONLY Integration Tests (Requires ComfyUI running)
..\..\venv\Scripts\python run_tests.py -m integration
```

### 🧪 Test Suite Structure

The tests are split into two categories to ensure fast feedback loops while still verifying full functionality.

#### Unit Tests (`tests/unit/`)
*   **Speed:** Fast (< 1s)
*   **Dependencies:** None (Standalone)
*   **Purpose:** Verify internal logic, math, and syntax without loading ComfyUI.

| File | Description |
| :--- | :--- |
| `test_syntax.py` | Ensures all files are valid Python and follow strict import rules. |
| `test_raw_processing.py` | Validates isolated core logic (`raw_processing.py`) without ComfyUI dependencies. |

#### Integration Tests (`tests/integration/`)
*   **Speed:** Slow (Requires network)
*   **Dependencies:** Running ComfyUI Server (Port 8188)
*   **Purpose:** Verify node registration, API endpoints, and workflow validity.

| Category | Description |
| :--- | :--- |
| **Node Registration** | Checks that nodes are correctly registered with the server. |
| **Server Health** | Verifies the ComfyUI API is reachable and healthy. |
| **Server Startup** | Verifies that ComfyUI starts successfully with the node installed (`test_server_startup.py`). |

### 🛠 Developer Guide

#### Architectural Best Practices (Testing)
The codebase uses a **Dependency Isolation** pattern to enable unit testing.

1.  **Separation of Concerns**:
    - `raw_processing.py`: Pure Python logic. **NO** imports from `comfy` or `folder_paths`.
    - `nodes.py`: ComfyUI adapter. handles Inputs/Outputs and calls `raw_processing`.
2.  **Testing Strategy**:
    - **Unit Tests** import `raw_processing.py` directly. They are fast and stable because they don't trigger ComfyUI's complex import chain.
    - **Do NOT** define core logic inside the `execute` method of `nodes.py`. Always extract it.

#### Writing Unit Tests
- Use existing `mock_rawpy` fixture in `conftest.py` to simulate LibRaw behavior.
- Import functions from `raw_processing.py`, **not** from `nodes.py`.

#### Writing Integration Tests
Integration tests use the `api_client` fixture to talk to the server.
```python
@pytest.mark.integration
def test_my_node_exists(self, api_client):
    assert api_client.node_exists("Load Raw Image")
```

#### Troubleshooting Common Issues
- **`ImportError: attempted relative import...`**:
    - **Cause**: Running `pytest` from the root directory.
    - **Fix**: Always use `python run_tests.py`.
- **`ModuleNotFoundError: No module named 'folder_paths'`**:
    - **Cause**: Your unit test is importing `nodes.py` which depends on ComfyUI.
    - **Fix**: Move the logic you are testing into `raw_processing.py` (or a similar utility file) and test that instead.


## 🎓 Recommended Tasks for Agents

- **Enhancement**: Expose more `rawpy.postprocess` flags (e.g., Gamma, Color Space, White Balance).
- **Optimization**: Support 16-bit processing directly into float32 tensors for better quality.
## ✅ Completed Tasks

- **Modernization**: Full migration to ComfyUI V3 API (`io.ComfyNode`, `ComfyExtension`).
- **Testing**: Established automated testing framework including unit tests and **Server Startup** verification.
- **Standardization**: Added Workflow Templates (`example_workflows/`) and Documentation (`web/docs/`).

## 📚 ComfyUI Documentation Reference

To ensure high-quality and consistent development, agents MUST visit the relevant links from the following list before starting any specific task (e.g., visit the "i18n Support" link before adding translations).

### Core Concepts & Backend
- [Overview](https://docs.comfy.org/custom-nodes/overview.md)
- [Getting Started](https://docs.comfy.org/custom-nodes/walkthrough.md)
- [Lifecycle](https://docs.comfy.org/custom-nodes/backend/lifecycle.md)
- [Datatypes](https://docs.comfy.org/custom-nodes/backend/datatypes.md)
- [Images, Latents, and Masks](https://docs.comfy.org/custom-nodes/backend/images_and_masks.md)
- [Working with torch.Tensor](https://docs.comfy.org/custom-nodes/backend/tensors.md)
- [Data lists](https://docs.comfy.org/custom-nodes/backend/lists.md)
- [Lazy Evaluation](https://docs.comfy.org/custom-nodes/backend/lazy_evaluation.md)
- [Node Expansion](https://docs.comfy.org/custom-nodes/backend/expansion.md)
- [Hidden and Flexible inputs](https://docs.comfy.org/custom-nodes/backend/more_on_inputs.md)
- [Properties](https://docs.comfy.org/custom-nodes/backend/server_overview.md): Properties of a custom node
- [Annotated Examples (Backend)](https://docs.comfy.org/custom-nodes/backend/snippets.md)

### V3 Migration
- [V3 Migration Guide](https://docs.comfy.org/custom-nodes/v3_migration.md): Essential for moving from V1 to the new ComfyNode schema.

### Frontend & UI Extensions
- [Javascript Extensions](https://docs.comfy.org/custom-nodes/js/javascript_overview.md)
- [Comfy Hooks](https://docs.comfy.org/custom-nodes/js/javascript_hooks.md)
- [Comfy Objects](https://docs.comfy.org/custom-nodes/js/javascript_objects_and_hijacking.md)
- [Annotated Examples (JS)](https://docs.comfy.org/custom-nodes/js/javascript_examples.md)
- [Commands and Keybindings](https://docs.comfy.org/custom-nodes/js/javascript_commands_keybindings.md)
- [Context Menu Migration Guide](https://docs.comfy.org/custom-nodes/js/context-menu-migration.md)
- [Selection Toolbox](https://docs.comfy.org/custom-nodes/js/javascript_selection_toolbox.md)
- [Settings](https://docs.comfy.org/custom-nodes/js/javascript_settings.md)
- [Dialog API](https://docs.comfy.org/custom-nodes/js/javascript_dialog.md)
- [Toast API](https://docs.comfy.org/custom-nodes/js/javascript_toast.md)
- [Sidebar Tabs](https://docs.comfy.org/custom-nodes/js/javascript_sidebar_tabs.md)
- [Bottom Panel Tabs](https://docs.comfy.org/custom-nodes/js/javascript_bottom_panel_tabs.md)
- [Topbar Menu](https://docs.comfy.org/custom-nodes/js/javascript_topbar_menu.md)
- [About Panel Badges](https://docs.comfy.org/custom-nodes/js/javascript_about_panel_badges.md)

### Publishing & Internationalization
- [ComfyUI Custom Nodes i18n Support](https://docs.comfy.org/custom-nodes/i18n.md): Multi-language support.
- [Add node docs](https://docs.comfy.org/custom-nodes/help_page.md): Creating rich documentation (markdown).
- [Workflow templates](https://docs.comfy.org/custom-nodes/workflow_templates.md)

### 📸 RAW Processing (rawpy/LibRaw)
- [rawpy API Reference](https://letmaik.github.io/rawpy/api/index.html): Main documentation portal.
- [rawpy.RawPy Class](https://letmaik.github.io/rawpy/api/rawpy.RawPy.html): Methods for reading and post-processing (e.g., `postprocess`).
- [rawpy.Params Class](https://letmaik.github.io/rawpy/api/rawpy.Params.html): Definition of all processing parameters (demosaic, WB, noise reduction, etc.).
- [rawpy Enumerations](https://letmaik.github.io/rawpy/api/enums.html): Supported demosaic algorithms, color spaces, and highlight modes.
- [rawpy Exceptions](https://letmaik.github.io/rawpy/api/exceptions.html): Error handling for unsupported formats or corrupted files.
- [Named Tuples](https://letmaik.github.io/rawpy/api/namedtuples.html): Structure of returned data like `ImageSizes` and `Thumbnail`.