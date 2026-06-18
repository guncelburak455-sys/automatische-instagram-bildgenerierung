import pytest
from PIL import Image

from post_generator.services.post_generator import (
    crop_to_4_5,
    INSTAGRAM_WIDTH,
    INSTAGRAM_HEIGHT,
)


def test_crop_image_modes():
    """
    Test that crop_to_4_5 preserves the color modes of input images.
    Modes to test: RGBA (transparency), L (grayscale), CMYK.
    """
    modes = ["RGBA", "L", "CMYK"]
    for mode in modes:
        # Create a landscape image of 200x100 in the given mode
        # Fill it with a non-zero color appropriate for the mode
        if mode == "RGBA":
            color = (255, 0, 0, 128)
        elif mode == "L":
            color = 128
        elif mode == "CMYK":
            color = (255, 255, 0, 0)
        else:
            color = 0

        img = Image.new(mode, (200, 100), color)
        result = crop_to_4_5(img)
        
        # Verify the dimensions are correct
        assert result.size == (INSTAGRAM_WIDTH, INSTAGRAM_HEIGHT)
        # Verify the mode is preserved
        assert result.mode == mode


def test_crop_tiny_images():
    """
    Test that extremely small images are correctly cropped to 4:5 and scaled up to 1080x1350.
    """
    # 10x10 square image
    img = Image.new("RGB", (10, 10), (0, 255, 0))
    result = crop_to_4_5(img)
    assert result.size == (INSTAGRAM_WIDTH, INSTAGRAM_HEIGHT)
    
    # 5x20 tall image (ratio 0.25, which is smaller than 0.8)
    img_tall = Image.new("RGB", (5, 20), (0, 0, 255))
    result_tall = crop_to_4_5(img_tall)
    assert result_tall.size == (INSTAGRAM_WIDTH, INSTAGRAM_HEIGHT)


def test_crop_odd_dimensions():
    """
    Test cropping images with odd pixel dimensions to verify that integer division
    and rounding do not cause any offset errors or crashes.
    """
    # 1001 x 1001 image (odd width and height)
    img = Image.new("RGB", (1001, 1001), (255, 255, 255))
    result = crop_to_4_5(img)
    assert result.size == (INSTAGRAM_WIDTH, INSTAGRAM_HEIGHT)


def test_crop_invalid_input():
    """
    Test that crop_to_4_5 raises an appropriate exception when passed invalid inputs
    (e.g., None, string, integer) instead of an Image object.
    """
    with pytest.raises((AttributeError, TypeError)):
        crop_to_4_5(None)  # type: ignore

    with pytest.raises((AttributeError, TypeError)):
        crop_to_4_5("not an image")  # type: ignore

    with pytest.raises((AttributeError, TypeError)):
        crop_to_4_5(12345)  # type: ignore
