import pytest
from pathlib import Path
from PIL import Image

from post_generator.config import Config
from post_generator.app import _build_image, generate_post
from post_generator.services.transform import VALID_POSITIONS


@pytest.fixture
def temp_photo_path(tmp_path):
    """Fixture to create a temporary test image and return its path as a string."""
    img_path = tmp_path / "test_bg.png"
    # Create a simple red 800x600 landscape image
    img = Image.new("RGB", (800, 600), (255, 0, 0))
    img.save(img_path)
    return str(img_path)


def test_build_image_pipeline(temp_photo_path):
    """
    Test that the full _build_image pipeline runs end-to-end,
    correctly cropping, overlaying mask, and rendering text.
    """
    config = Config(
        photo=temp_photo_path,
        position="top-right",
        text="Testing Integration Pipeline",
        x=10,
        y=-10,
        font=None,
        text_color="yellow",
        stroke_color="black"
    )

    image, resolved_position = _build_image(config)

    # Assert correct type, size, and mode
    assert isinstance(image, Image.Image)
    assert image.size == (1080, 1350)
    assert image.mode == "RGBA"
    assert resolved_position == "top-right"


def test_build_image_pipeline_random_position(temp_photo_path):
    """
    Test that the pipeline works with position='random' and correctly resolves it.
    """
    config = Config(
        photo=temp_photo_path,
        position="random",
        text="Random Position Test",
        x=0,
        y=0
    )

    image, resolved_position = _build_image(config)
    assert resolved_position in VALID_POSITIONS
    assert image.size == (1080, 1350)


def test_generate_post_writes_file_to_disk(temp_photo_path, tmp_path):
    """
    Test that generate_post runs the full flow and writes the output file to disk.
    """
    output_dir = tmp_path / "output_dir"
    output_dir.mkdir()
    
    config = Config(
        photo=temp_photo_path,
        position="bottom-left",
        text="Saved Post Test",
        x=0,
        y=0,
        output_path=str(output_dir),
        output_name="my_instagram_post.png",
        preview=False
    )

    generate_post(config)

    expected_file = output_dir / "my_instagram_post.png"
    assert expected_file.exists()
    assert expected_file.is_file()

    # Load and verify the generated image properties
    img = Image.open(expected_file)
    assert img.size == (1080, 1350)
