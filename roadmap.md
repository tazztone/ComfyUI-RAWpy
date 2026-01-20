# Roadmap: ComfyUI-RAWpy

This document outlines the planned features and improvements for the `ComfyUI-RAWpy` extension. The goal is to bring the full power of `LibRaw` (via `rawpy`) to the ComfyUI ecosystem.

## ✅ Phase 0: Modernization (Completed)
- [x] **V3 API Migration**: Full adoption of `io.ComfyNode` and `define_schema`.
- [x] **Standardization**: Added help documentation, workflow templates, and i18n structure.

## 🚀 Phase 1: Core Quality & Bit-Depth (High Priority)
*Focus: Improving the fundamental quality of the output image.*

- [ ] **16-bit Pipeline**: Support `output_bps=16` in `postprocess` to provide higher dynamic range directly to ComfyUI's float32 tensors, avoiding 8-bit quantization artifacts.
- [ ] **White Balance Controls**:
  - [ ] `use_camera_wb`: Use the white balance stored in the image metadata.
  - [ ] `use_auto_wb`: Calculate white balance automatically from image content.
  - [ ] `user_wb`: Custom RGBG multipliers for precise manual control.
- [ ] **Demosaicing Algorithm Selection**: Expose the underlying algorithms (AHD, VNG, PPG, DCB, etc.) to allow users to choose between speed and artifact reduction.

## 🎨 Phase 2: Color & Correction (Medium Priority)
*Focus: Professional color management and lens correction.*

- [ ] **Output Color Spaces**: Support selecting specific color spaces (sRGB, Adobe RGB, Wide Gamut, ProPhoto, etc.).
- [ ] **Gamma Control**: Allow custom gamma curves (power and slope) for linear or specialized workflows.
- [ ] **Chromatic Aberration Correction**: Add inputs for red/blue scale coefficients to fix fringing.
- [ ] **Exposure Fine-tuning**:
  - [ ] `exp_shift`: Linear exposure shift.
  - [ ] `exp_preserve_highlights`: Control how much highlight detail to preserve during exposure shifts.

## 🧹 Phase 3: Noise Reduction & Artifacts
*Focus: Cleaning up raw data before it hits the AI pipeline.*

- [ ] **Wavelet Denoising**: Implement `noise_thr` for effective pre-demosaic noise reduction.
- [ ] **Impulse Noise Reduction**: Add `fbdd_noise_reduction`.
- [ ] **Median Filter Passes**: Post-demosaic filtering to reduce color moiré and artifacts.

## 📂 Phase 4: Workflow & Metadata
*Focus: Integration and utility.*

- [ ] **Metadata Extraction**: A new output for the `Load RAW Image` node that provides a dictionary of Exif and camera-specific metadata (ISO, Shutter Speed, Aperture, Focal Length, etc.).
- [ ] **Thumbnail Extraction Node**: A specialized node to "instant-load" the embedded JPEG preview from a RAW file for fast workflow prototyping.
- [ ] **Manual Orientation**: Support `user_flip` for cases where the camera's orientation sensor was incorrect.
## 🛠️ Phase 5: Advanced Options
- [ ] **Dark Frame Substraction**: Support loading an external dark frame to remove sensor noise patterns.
- [ ] **Bad Pixel Correction**: Support external map files for sensor defect correction.
- [ ] **Half-Size Loading**: Option for extremely fast loading by skipping interpolation (useful for quick previews or low-memory environments).

## 📽️ Phase 6: Creative Bayer Data (Advanced)
*Focus: Accessing the "soul" of the sensor for custom processing.*

- [ ] **Raw Bayer Output**: A node that provides the undecoded, unprocessed sensor data as a 1-channel tensor. 
- [ ] **RGGB 4-Channel Node**: Output the RAW data as a half-resolution 4-channel image (separated R, G1, G2, B channels). This is ideal for training neural networks or high-precision custom workflows.
- [ ] **Custom Linear Pipeline**: Skip all `rawpy` processing to get the true linear values for custom demosaicing in Torch.

## 🧪 Phase 7: Scientific & Advanced Metadata
*Focus: Precision and data-driven workflows.*

- [ ] **Extended Metadata Output**: Provide specialized camera data (e.g., specific black/white levels, sensor pattern description, color matrix).
- [ ] **Lens Profiles**: Output EXIF data for lens-specific adjustments (Focal length, Aperture, Focus distance).
- [ ] **XMP Sidecar Support**: Read `.xmp` files to automatically apply white balance and exposure offsets from Lightroom/Darktable.
- [ ] **Sub-image Selection**: Support for RAW files containing multiple exposures or preview layers.

## 🚂 Future & Performance
- [ ] **GPU Post-processing**: Investigate custom Torch-based demosaicing to offload work from the CPU.
- [ ] **Streaming Load**: Optimize memory usage for high-resolution 100MP+ medium format RAWs.

---
*Suggestions or contributions are welcome! Please open an issue or PR on the GitHub repository.*
