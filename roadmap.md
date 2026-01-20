# Roadmap: ComfyUI-RAWpy

This document outlines the planned features and improvements for the `ComfyUI-RAWpy` extension.

---

## ✅ Phase 0: Core RAW Processing (Completed)
- [x] **V3 API Migration**: Full adoption of `io.ComfyNode` and `define_schema`.
- [x] **16-bit Pipeline**: Support `output_bps=16` for higher dynamic range.
- [x] **White Balance Controls**: Camera WB, Auto WB, Custom RGBG multipliers.
- [x] **Demosaicing Algorithms**: AHD, VNG, PPG, DCB, AMAZE, LINEAR, DHT.
- [x] **Color Science**: sRGB, Adobe RGB, ProPhoto, Wide Gamut, XYZ, ACES, Rec2020.
- [x] **Gamma & Exposure**: Custom gamma curves, exposure shift, highlight preservation.
- [x] **Chromatic Aberration Correction**: Red/Blue scale coefficients.
- [x] **Embedded Previews**: Extract embedded JPEG/Bitmap thumbnails.

---

## ✅ Phase 1: ExifTool Integration (Completed)
- [x] **Multi-Thumbnail Support**: 3 outputs (IMAGE, preview, thumbnail).
- [x] **ExifTool-based Extraction**: Target specific embedded images:
  - `ThumbnailImage` (small ~4KB)
  - `PreviewImage` (medium ~150KB)
  - `JpgFromRaw` (full-size JPEG)
- [x] **Graceful Fallback**: Works without ExifTool (returns 1x1 placeholder).

---

## 🚀 Phase 2: Camera & Capture Metadata Nodes
*Focus: Extract and expose critical shooting parameters.*

- [ ] **Metadata Extraction Node**: Return camera-specific MakerNotes as dictionary.
  - Sony: Focus mode, Picture Profile
  - Canon: Picture Style, Lens ID
  - Nikon: Active D-Lighting settings
- [ ] **Lens Data Output**: Exact lens model, serial number, distortion profiles.
- [ ] **GPS Coordinates**: Geolocation for location-based workflows.
- [ ] **Copyright & IPTC**: Creator info, keywords, descriptions.

---

## 🔀 Phase 3: Smart Workflow Routing
*Focus: Route images through different pipelines based on metadata.*

- [ ] **ISO-Based Routing**: Apply stronger denoise for high-ISO shots (>3200).
- [ ] **Focal Length Router**: Different sharpening for wide-angle vs telephoto.
- [ ] **Flash Detection**: Auto-correct flash white balance.
- [ ] **Scene Mode Detection**: Identify portrait/night/HDR mode from MakerNotes.

---

## 📁 Phase 4: Batch Organization & Management
*Focus: Organize thousands of RAW files intelligently.*

- [ ] **Time-Based Grouping**: Burst sequences, bracketed exposures, time-lapses.
- [ ] **Camera Body Sorting**: Multi-camera shoots automatically separated.
- [ ] **Lens-Specific Processing**: Apply lens correction profiles per manufacturer.
- [ ] **Rating/Color Labels**: Import star ratings and color flags from Adobe/Capture One.

---

## 📝 Phase 5: Metadata Writing & Preservation
*Focus: Write processing history back to XMP sidecar files.*

- [ ] **XMP Sidecar Writing**: Track ComfyUI workflow IDs and parameters.
- [ ] **AI Model Metadata**: Record which models were used for upscaling/enhancement.
- [ ] **Cross-Platform Compatibility**: Export settings for Lightroom/Capture One.

---

## 🔬 Phase 6: Advanced Camera Features
*Focus: Deep sensor access and unconventional creative control.*

- [ ] **Dual-Native ISO Detection**: Sony/Panasonic base ISO optimization.
- [ ] **Focus Stacking Metadata**: Extract focus distance for intelligent merging.
- [ ] **Color Profile Switching**: Manufacturer-specific color science (Sony HLG, Canon Log).
- [ ] **Raw Bayer Output**: Undecoded sensor data as 1-channel tensor.
- [ ] **RGGB 4-Channel Node**: Separated R, G1, G2, B for custom demosaicing.

---

## 🚂 Phase 7: Performance & Optimization
- [ ] **GPU Post-processing**: Torch-based demosaicing to offload CPU work.
- [ ] **Streaming Load**: Optimize memory for 100MP+ images.
- [ ] **Caching**: JSON metadata dumps to avoid repeated ExifTool calls.

---

## Strategic Benefits

**Professional Workflow Tool**: This roadmap transforms ComfyUI-RAWpy from a simple RAW loader into a complete photographic workflow system.

**Dataset Creation**: Photographers training AI models need accurate metadata for conditional training (e.g., teaching models about different lenses, cameras, lighting conditions).

**Differentiation**: No other ComfyUI extension provides comprehensive camera metadata access.

---

*Suggestions or contributions are welcome! Please open an issue or PR on the GitHub repository.*
