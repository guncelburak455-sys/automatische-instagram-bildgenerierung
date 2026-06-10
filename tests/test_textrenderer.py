import pytest
from unittest.mock import patch, MagicMock
from PIL import ImageFont
from post_generator.services.textrenderer import TextRenderer

@pytest.fixture
def renderer():
    return TextRenderer()

@pytest.fixture
def default_grid():
    # 2x2 grid, each cell 100x100
    # Coordinates: X: 0-199, Y: 0-199
    # Center: (100, 100)
    return [(0, 0), (0, 1), (1, 0), (1, 1)]

def test_fits_in_cells_small_fits(renderer, default_grid):
    """
    Test _fits_in_cells() with a small width/height that completely fits 
    within the provided filled grid cells (should return True).
    """
    # w=50, h=50 at cx=100, cy=100 with 0 padding
    # Bounds: x in 75..125, y in 75..125
    # Grid cells needed: (0,0), (0,1), (1,0), (1,1)
    result = renderer._fits_in_cells(
        w=50, h=50, cx=100, cy=100, 
        cells=default_grid, cell_size=100, offset=(0, 0), padding=0
    )
    assert result is True

def test_fits_in_cells_large_extends_beyond(renderer, default_grid):
    """
    Test _fits_in_cells() with a large width/height that extends beyond 
    the filled grid cells (should return False).
    """
    # w=250, h=250 at cx=100, cy=100 with 0 padding
    # Bounds: x in -25..225, y in -25..225
    # Grid cells needed: -1 to 2, which don't exist in default_grid
    result = renderer._fits_in_cells(
        w=250, h=250, cx=100, cy=100, 
        cells=default_grid, cell_size=100, offset=(0, 0), padding=0
    )
    assert result is False

def test_fits_in_cells_padding_reduces_space(renderer, default_grid):
    """
    Test that the padding parameter correctly reduces the available space, 
    forcing _fits_in_cells to return False if the text is too close to the edge.
    """
    # w=190, h=190 at cx=100, cy=100
    
    # Without padding, bounds are x in 5..195, y in 5..195
    # This fits perfectly in grid cells (0,0) to (1,1)
    result_no_padding = renderer._fits_in_cells(
        w=190, h=190, cx=100, cy=100, 
        cells=default_grid, cell_size=100, offset=(0, 0), padding=0
    )
    assert result_no_padding is True
    
    # With padding of 20, bounds are x in -15..215, y in -15..215
    # This extends outside the 0..199 grid limits
    result_with_padding = renderer._fits_in_cells(
        w=190, h=190, cx=100, cy=100, 
        cells=default_grid, cell_size=100, offset=(0, 0), padding=20
    )
    assert result_with_padding is False

def test_fits_in_cells_overlapping_empty_cell(renderer):
    """
    Overlapping into an empty grid cell returns False.
    """
    # Grid with a hole: missing (1, 1) cell
    grid_with_hole = [(0, 0), (1, 0), (0, 1)]
    
    # w=150, h=150 at cx=100, cy=100 padding 0
    # Bounds: 25..175 -> needs grids (0,0), (0,1), (1,0), (1,1).
    # Missing (1,1) should cause a False return
    result = renderer._fits_in_cells(
        w=150, h=150, cx=100, cy=100, 
        cells=grid_with_hole, cell_size=100, offset=(0, 0), padding=0
    )
    assert result is False

@patch("post_generator.services.textrenderer.ImageFont.truetype")
def test_load_font_valid_custom_path(mock_truetype, renderer):
    """
    Test load_font() with a mock valid font path to ensure it loads the TrueType font correctly.
    """
    mock_font = MagicMock(spec=ImageFont.FreeTypeFont)
    mock_truetype.return_value = mock_font
    
    font = renderer.load_font("custom_font.ttf", 20)
    
    mock_truetype.assert_called_once_with("custom_font.ttf", 20)
    assert font == mock_font

@patch("post_generator.services.textrenderer.ImageFont.truetype")
def test_load_font_invalid_custom_path_fallback(mock_truetype, renderer):
    """
    Test load_font() with a non-existent font path to ensure it catches the OSError and falls back.
    """
    # First call with custom font raises OSError, second call with default font succeeds
    mock_default_font = MagicMock(spec=ImageFont.FreeTypeFont)
    mock_truetype.side_effect = [OSError("Not found"), mock_default_font]
    
    with patch("post_generator.services.textrenderer.Path.exists", return_value=True):
        font = renderer.load_font("invalid_font.ttf", 20)
        
    assert mock_truetype.call_count == 2
    # Ensure the first call was the invalid font
    assert mock_truetype.call_args_list[0][0] == ("invalid_font.ttf", 20)
    # Ensure it returned the mock default font (from the fallback loop)
    assert font == mock_default_font

@patch("post_generator.services.textrenderer.ImageFont.truetype")
@patch("post_generator.services.textrenderer.ImageFont.load_default")
def test_load_font_ultimate_fallback(mock_load_default, mock_truetype, renderer):
    """
    Test the ultimate fallback scenario where no TrueType fonts are found, 
    ensuring it successfully returns ImageFont.load_default().
    """
    # All TrueType loads fail
    mock_truetype.side_effect = OSError("Not found")
    
    mock_default_bitmap = MagicMock()
    mock_load_default.return_value = mock_default_bitmap
    
    font = renderer.load_font("invalid_font.ttf", 20)
    
    # load_default should have been called as the last resort
    mock_load_default.assert_called_once()
    assert font == mock_default_bitmap


@pytest.fixture
def default_font():
    return ImageFont.load_default()

def test_wrap_text_short_single_word(renderer, default_font):
    """
    Test format_text (wrap_text) keeps a short single word on one line (no newline added)
    """
    text = "Hello"
    result = renderer.wrap_text(text, default_font, max_width=1000)
    assert result == "Hello"
    assert "\n" not in result

def test_wrap_text_exceeds_threshold(renderer, default_font):
    """
    Test that text exceeding the wrap threshold gets split across multiple lines
    """
    text = "This is a long sentence that should wrap"
    result = renderer.wrap_text(text, default_font, max_width=50)
    assert "\n" in result
    lines = result.split("\n")
    assert len(lines) > 1

@patch("PIL.ImageDraw.ImageDraw.textbbox")
def test_wrap_text_known_multi_word_output(mock_textbbox, renderer, default_font):
    """
    Test that the number of output lines is correct for a known multi-word input.
    A known input produces the exact expected wrapped output.
    """
    # Predictable lengths: string length * 10
    mock_textbbox.side_effect = lambda *args, **kwargs: (0, 0, len(args[1]) * 10, 10)
    
    text = "One Two Three Four"
    # "One" = 30
    # "One Two" = 70
    # "One Two Three" = 130 > 85. So wraps before "Three".
    # "Three" = 50
    # "Three Four" = 100 > 85. Wraps before "Four".
    result = renderer.wrap_text(text, default_font, max_width=85)
    
    expected = "One Two\nThree\nFour"
    assert result == expected
    assert len(result.split("\n")) == 3

@patch("PIL.ImageDraw.ImageDraw.textbbox")
def test_wrap_text_single_word_longer_than_threshold(mock_textbbox, renderer, default_font):
    """
    Test that a single word longer than the threshold is not broken mid-word.
    """
    mock_textbbox.side_effect = lambda *args, **kwargs: (0, 0, len(args[1]) * 10, 10)
    
    text = "Supercalifragilisticexpialidocious"
    # length is 34 -> width is 340. 340 > 50 (max_width)
    result = renderer.wrap_text(text, default_font, max_width=50)
    
    # It shouldn't break the word itself
    assert result == "Supercalifragilisticexpialidocious"
    assert "\n" not in result
