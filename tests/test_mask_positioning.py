import random
import pytest

from post_generator.services.transform import (
    choose_position,
    transform_for_position,
    anchor_offset,
    VALID_POSITIONS,
    INSTAGRAM_WIDTH,
    INSTAGRAM_HEIGHT,
)


def test_choose_position_fixed():
    """
    Verify that choose_position returns the input position if it is a specific, valid corner position.
    """
    rng = random.Random(42)
    for pos in VALID_POSITIONS:
        assert choose_position(pos, rng) == pos


def test_choose_position_random():
    """
    Verify that choose_position returns one of the VALID_POSITIONS when "random" is passed.
    """
    rng = random.Random(12345)
    for _ in range(100):
        pos = choose_position("random", rng)
        assert pos in VALID_POSITIONS


def test_choose_position_none():
    """
    Verify that choose_position defaults to random behavior and returns a valid position when None is passed.
    """
    rng = random.Random(6789)
    for _ in range(100):
        pos = choose_position(None, rng)
        assert pos in VALID_POSITIONS


def test_transform_for_position_top_left():
    """
    Verify transform_for_position with "top-left" does not modify/mirror the cells.
    """
    cells = [(0, 0), (1, 0), (0, 1)]
    result = transform_for_position(cells, 3, 3, "top-left")
    assert result == cells


def test_transform_for_position_top_right():
    """
    Verify transform_for_position with "top-right" horizontally mirrors the cells.
    """
    cells = [(0, 0), (1, 0), (0, 1)]
    # Grid width = 3, so x -> 3 - 1 - x
    # (0, 0) -> (2, 0)
    # (1, 0) -> (1, 0)
    # (0, 1) -> (2, 1)
    expected = [(2, 0), (1, 0), (2, 1)]
    result = transform_for_position(cells, 3, 3, "top-right")
    assert result == expected


def test_transform_for_position_bottom_left():
    """
    Verify transform_for_position with "bottom-left" vertically mirrors the cells.
    """
    cells = [(0, 0), (1, 0), (0, 1)]
    # Grid height = 3, so y -> 3 - 1 - y
    # (0, 0) -> (0, 2)
    # (1, 0) -> (1, 2)
    # (0, 1) -> (0, 1)
    expected = [(0, 2), (1, 2), (0, 1)]
    result = transform_for_position(cells, 3, 3, "bottom-left")
    assert result == expected


def test_transform_for_position_bottom_right():
    """
    Verify transform_for_position with "bottom-right" both horizontally and vertically mirrors the cells.
    """
    cells = [(0, 0), (1, 0), (0, 1)]
    # Grid width = 3, height = 3
    # (0, 0) -> (2, 2)
    # (1, 0) -> (1, 2)
    # (0, 1) -> (2, 1)
    expected = [(2, 2), (1, 2), (2, 1)]
    result = transform_for_position(cells, 3, 3, "bottom-right")
    assert result == expected


def test_anchor_offset_top_left():
    """
    Verify anchor_offset for "top-left" position is always (0, 0).
    """
    offset = anchor_offset(template_w=4, template_h=5, cell=100, position="top-left")
    assert offset == (0, 0)


def test_anchor_offset_top_right():
    """
    Verify anchor_offset for "top-right" position.
    Expected: (INSTAGRAM_WIDTH - shape_w, 0)
    """
    # shape_w = 4 * 100 = 400
    # expected x = 1080 - 400 = 680
    offset = anchor_offset(template_w=4, template_h=5, cell=100, position="top-right")
    assert offset == (680, 0)


def test_anchor_offset_bottom_left():
    """
    Verify anchor_offset for "bottom-left" position.
    Expected: (0, INSTAGRAM_HEIGHT - shape_h)
    """
    # shape_h = 5 * 100 = 500
    # expected y = 1350 - 500 = 850
    offset = anchor_offset(template_w=4, template_h=5, cell=100, position="bottom-left")
    assert offset == (0, 850)


def test_anchor_offset_bottom_right():
    """
    Verify anchor_offset for "bottom-right" position.
    Expected: (INSTAGRAM_WIDTH - shape_w, INSTAGRAM_HEIGHT - shape_h)
    """
    # shape_w = 400, shape_h = 500
    # expected = (680, 850)
    offset = anchor_offset(template_w=4, template_h=5, cell=100, position="bottom-right")
    assert offset == (680, 850)
