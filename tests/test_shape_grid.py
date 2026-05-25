from post_generator.services.post_generator import template_to_grid, grid_to_cells

def test_template_to_grid_preserves_dimensions():
    template = ["110", "011"]
    grid = template_to_grid(template)
    assert len(grid) == 2               # two rows
    assert len(grid[0]) == 3            # three columns
    assert grid[0] == ["1", "1", "0"]

def test_grid_to_cells_returns_only_filled():
    grid = template_to_grid(["10", "01"])
    cells = grid_to_cells(grid)
    # (x, y): "1" at (0,0) and (1,1)
    assert cells == [(0, 0), (1, 1)]

def test_grid_to_cells_known_template():
    grid = template_to_grid(["111", "000", "101"])
    cells = grid_to_cells(grid)
    assert (0, 0) in cells
    assert (2, 2) in cells
    assert (0, 1) not in cells  # middle row is all zeros
    assert (len(cells)) == 5

def test_grid_to_cells_empty_when_all_zero():
    grid = template_to_grid(["000", "000"])
    assert grid_to_cells(grid) == []