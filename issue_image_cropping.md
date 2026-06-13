# Issue: Expand Test Coverage for Image Cropping Functionality

## Description
One of the key components of our Instagram post generator is the `crop_to_4_5` function, which crops and resizes input images to fit the standard Instagram format (4:5 aspect ratio, 1080x1350 resolution).

The existing tests (in `tests/test_composition.py`) cover basic cropping scenarios. However, to guarantee the robustness and stability of the application, we need to test the following edge cases:
1. **Different Color Modes:** Verify that images with different PIL modes—such as RGBA (with transparency), L (grayscale), CMYK, and Palette (P)—are cropped and resized correctly, and their modes and transparency channels are preserved.
2. **Tiny Images:** Ensure that images much smaller than the target resolution (e.g., 10x10 or 5x20) are scaled up to 1080x1350 without failing or losing color information.
3. **Odd Dimensions & Symmetry:** Verify that images with odd dimensions (where division by 2 results in fractional pixels) are handled correctly and centered as symmetrically as possible without rounding errors or crashes.
4. **Invalid Inputs:** Test the error-handling behavior when the function is called with invalid arguments (e.g., `None`, strings, or integers) instead of a PIL Image object.

## Acceptance Criteria
- Images with different color modes (RGB, RGBA, L, CMYK) must be successfully cropped and resized, and their original modes must be preserved.
- Tiny images must be upscaled to exactly 1080x1350 without causing errors.
- Images with odd dimensions must be processed without offset calculation crashes.
- Proper exceptions (`TypeError` or `AttributeError`) must be raised when invalid inputs are provided.
- All newly written tests must pass successfully using `pytest`.

## Tasks
- [x] Create the `tests/test_image_cropping.py` test suite.
- [x] Implement the following test cases:
  - `test_crop_image_modes`: Verifies preservation of PIL modes (RGBA, L, CMYK) after crop and resize.
  - `test_crop_tiny_images`: Verifies correct behavior when upscaling extremely small images.
  - `test_crop_odd_dimensions`: Verifies coordinates rounding for images with odd width/height.
  - `test_crop_invalid_input`: Verifies exception raising for non-Image inputs.
- [x] Run and verify that all tests pass.
