import pytest
from unittest.mock import patch
from PIL import Image

from post_generator.services.post_generator import (
    crop_to_4_5,
    INSTAGRAM_WIDTH,
    INSTAGRAM_HEIGHT,
)
from post_generator.services.composition import compose, save_output, ORANGE

def test_crop_wide_landscape_image():
    """
    Test crop_to_4_5() with a wide (landscape) image and verify it crops from the sides evenly.
    Target ratio is 4:5 (0.8). Wide image: 2000x1000 (ratio 2.0).
    Expected new width: int(1000 * 0.8) = 800
    Expected left crop: (2000 - 800) // 2 = 600
    Expected crop box: (600, 0, 1400, 1000)
    """
    img = Image.new("RGB", (2000, 1000))
    with patch.object(Image.Image, 'crop', wraps=img.crop) as mock_crop:
        result = crop_to_4_5(img)
        
        mock_crop.assert_called_once_with((600, 0, 1400, 1000))
        assert result.size == (INSTAGRAM_WIDTH, INSTAGRAM_HEIGHT)

def test_crop_tall_portrait_image():
    """
    Test crop_to_4_5() with a tall (portrait) image and verify it crops from the top and bottom evenly.
    Target ratio is 4:5 (0.8). Tall image: 1000x2000 (ratio 0.5).
    Expected new height: int(1000 / 0.8) = 1250
    Expected top crop: (2000 - 1250) // 2 = 375
    Expected crop box: (0, 375, 1000, 1625)
    """
    img = Image.new("RGB", (1000, 2000))
    with patch.object(Image.Image, 'crop', wraps=img.crop) as mock_crop:
        result = crop_to_4_5(img)
        
        mock_crop.assert_called_once_with((0, 375, 1000, 1625))
        assert result.size == (INSTAGRAM_WIDTH, INSTAGRAM_HEIGHT)

def test_crop_exact_4_5_ratio():
    """
    Test that an image already at a 4:5 ratio is simply resized without losing any content.
    For an image of 400x500 (0.8 ratio), it should crop with the exact original bounds (0, 0, 400, 500).
    """
    img = Image.new("RGB", (400, 500))
    with patch.object(Image.Image, 'crop', wraps=img.crop) as mock_crop:
        result = crop_to_4_5(img)
        
        mock_crop.assert_called_once_with((0, 0, 400, 500))
        assert result.size == (INSTAGRAM_WIDTH, INSTAGRAM_HEIGHT)

def test_crop_resolution_always_1080_1350():
    """
    Test that the output resolution of crop_to_4_5() is always exactly (1080, 1350)
    for various extreme shapes.
    """
    sizes = [
        (100, 100),       # Square
        (3000, 200),      # Extremely wide
        (200, 3000),      # Extremely tall
        (1080, 1350),     # Exact target
    ]
    
    for w, h in sizes:
        img = Image.new("RGB", (w, h))
        result = crop_to_4_5(img)
        assert result.size == (INSTAGRAM_WIDTH, INSTAGRAM_HEIGHT)

def test_compose_returns_correct_format():
    bg = Image.new("RGBA", (100, 100), (0, 0, 0, 255))
    mask = Image.new("L", (100, 100), 0)
    
    result = compose(bg, mask)
    
    assert result.size == bg.size
    assert result.mode == "RGBA"

def test_compose_fully_white_mask():
    bg = Image.new("RGBA", (10, 10), (0, 0, 0, 255))
    mask = Image.new("L", (10, 10), 255)  # fully white
    
    result = compose(bg, mask)
    
    # all pixels should be ORANGE
    for x in range(10):
        for y in range(10):
            assert result.getpixel((x, y)) == ORANGE

def test_compose_fully_black_mask():
    bg_color = (10, 20, 30, 255)
    bg = Image.new("RGBA", (10, 10), bg_color)
    mask = Image.new("L", (10, 10), 0)  # fully black
    
    result = compose(bg, mask)
    
    # all pixels should remain bg_color
    for x in range(10):
        for y in range(10):
            assert result.getpixel((x, y)) == bg_color

def test_save_output_creates_file(tmp_path):
    img = Image.new("RGBA", (10, 10), (255, 0, 0, 255))
    output_file = tmp_path / "test_output.png"
    
    returned_path = save_output(img, str(output_file))
    
    assert returned_path == output_file
    assert output_file.exists()
    assert output_file.is_file()

def test_save_output_creates_directories(tmp_path):
    img = Image.new("RGBA", (10, 10), (255, 0, 0, 255))
    # deep directory structure
    output_file = tmp_path / "deep" / "nested" / "dir" / "test_output.png"
    
    returned_path = save_output(img, str(output_file))
    
    assert returned_path == output_file
    assert output_file.exists()
    assert output_file.parent.exists()
