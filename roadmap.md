# Roadmap: ComfyUI-RAWpy

This document outlines the planned features and improvements for the `ComfyUI-RAWpy` extension, sorted by priority.

## ✅ Phase 0: Modernization (Completed)
- [x] **V3 API Migration**: Full adoption of `io.ComfyNode` and `define_schema`.
- [x] **Standardization**: Added help documentation, workflow templates, and i18n structure.

---

## ✅ Priority 1: Image Quality & Core Essentials (Completed)
*Focus: Maximizing the fidelity of the output image and providing basic photographic control.*

- [x] **16-bit Pipeline**: Support `output_bps=16` in `postprocess` to provide higher dynamic range directly to ComfyUI's float32 tensors, avoiding 8-bit quantization artifacts.
- [x] **White Balance Controls**:
  - [x] `use_camera_wb`: Use the white balance stored in the image metadata.
  - [x] `use_auto_wb`: Calculate white balance automatically from image content.
  - [x] `user_wb`: Custom RGBG multipliers for precise manual control.
- [x] **Demosaicing Algorithm Selection**: Expose algorithms (AHD, VNG, PPG, DCB, etc.) to allow users to choose between speed and artifact reduction.
- [x] **Manual Orientation**: Support `user_flip` for cases where the camera's orientation sensor was incorrect.

## ✅ Priority 2: Color Science & Exposure (Completed)
*Focus: Professional color management and linear workflow integration.*

- [x] **Output Color Spaces**: Support selecting specific color spaces (sRGB, Adobe RGB, Wide Gamut, ProPhoto, etc.).
- [x] **Gamma Control**: Allow custom gamma curves (power and slope) for linear or specialized workflows.
- [x] **Exposure Fine-tuning**:
  - [x] `exp_shift`: Linear exposure shift.
  - [x] `exp_preserve_highlights`: Control highlight detail preservation during exposure shifts.
- [x] **Chromatic Aberration Correction**: Add inputs for red/blue scale coefficients to fix fringing.

## 🧹 Priority 3: Artifact Reduction & Pre-processing
*Focus: Cleaning up raw data before it enters the AI/Latent pipeline.*

- [ ] **Wavelet Denoising**: Implement `noise_thr` for effective pre-demosaic noise reduction.
- [ ] **Impulse Noise Reduction**: Add `fbdd_noise_reduction` (Fix Bad Data Demosaicing).
- [ ] **Median Filter Passes**: Post-demosaic filtering to reduce color moiré and artifacts.
- [ ] **Dark Frame Subtraction**: Support loading an external dark frame to remove sensor noise patterns.
- [ ] **Bad Pixel Correction**: Support external map files for sensor defect correction.

## 📂 Priority 4: Workflow & Metadata
*Focus: Integration, efficiency, and data-driven workflows.*

- [ ] **Metadata Extraction**: Provide a dictionary of Exif and camera-specific metadata (ISO, Shutter, Aperture, Focal Length).
- [ ] **Lens Profiles**: Output EXIF data specifically for lens-specific adjustments.
- [ ] **XMP Sidecar Support**: Read `.xmp` files to apply WB and exposure from Lightroom/Darktable.
- [x] **Embedded Preview Output**: Fast "instant-load" of the embedded JPEG preview for rapid prototyping.
- [ ] **Lazy Loading / Draft Mode**: Option for fast loading by skipping interpolation for quick previews (e.g. half-size).

## 📽️ Priority 5: Advanced & Scientific Features
*Focus: Deep sensor access and unconventional creative control.*

- [ ] **Raw Bayer Output**: Provide undecoded sensor data as a 1-channel tensor. 
- [ ] **RGGB 4-Channel Node**: Output RAW data as a 4-channel image (separated R, G1, G2, B).
- [ ] **Custom Linear Pipeline**: Skip all `rawpy` processing for custom demosaicing in Torch.
- [ ] **Sub-image Selection**: Support for RAW files with multiple exposures or layers.

## 🚂 Priority 6: Performance & Optimization
- [ ] **GPU Post-processing**: Investigate Torch-based demosaicing to offload CPU work.
- [ ] **Streaming Load**: Optimize memory usage for high-resolution 100MP+ images.

---
*Suggestions or contributions are welcome! Please open an issue or PR on the GitHub repository.*
