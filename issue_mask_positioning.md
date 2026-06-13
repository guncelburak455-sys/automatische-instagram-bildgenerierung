# Issue: Test Mask Positioning Logic

## User Story
As a developer, I want to test the mask positioning logic so that the mask can be placed correctly in all four corners.

## Acceptance Criteria
- [x] The top-left position is tested.
- [x] The top-right position is tested.
- [x] The bottom-left position is tested.
- [x] The bottom-right position is tested.
- [x] Random positioning only returns valid positions.
- [x] The test run can be executed with pytest.

## Tasks
- [x] Create a new test file `tests/test_mask_positioning.py`.
- [x] Test `choose_position` for:
  - Exact positions ("top-left", "top-right", "bottom-left", "bottom-right").
  - "random" option (making sure it returns one of the valid positions using a mock or a seeded random generator).
  - `None` value (which defaults to random behavior).
- [x] Test `transform_for_position` for all four corners:
  - Verify mirroring behavior for top-left (no change).
  - Verify mirroring behavior for top-right (horizontal mirror).
  - Verify mirroring behavior for bottom-left (vertical mirror).
  - Verify mirroring behavior for bottom-right (horizontal + vertical mirror).
- [x] Test `anchor_offset` for all four corners:
  - Verify top-left offset is `(0, 0)`.
  - Verify top-right offset is `(INSTAGRAM_WIDTH - shape_w, 0)`.
  - Verify bottom-left offset is `(0, INSTAGRAM_HEIGHT - shape_h)`.
  - Verify bottom-right offset is `(INSTAGRAM_WIDTH - shape_w, INSTAGRAM_HEIGHT - shape_h)`.
- [x] Run pytest to ensure all test cases pass.
