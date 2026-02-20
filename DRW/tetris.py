"""
Bitwise solution for simplified Tetris engine.

Grid and pieces are represented with bitmasks: each row is an int with bits
for columns (1 = filled, 0 = empty). Row index 0 is the bottom of the grid.
"""
import fileinput
import sys

WIDTH = 10
FULL_ROW = (1 << WIDTH) - 1  # All 10 columns set; used to detect a completed row

# Each shape is stored as a list of row strings (top row first in the list).
# '1' = block, '0' = empty; string form matches the visual shape and is easy to reverse.
SHAPES = {
    "Q": ["11", "11"],
    "I": ["1111"],
    "Z": ["110", "011"],
    "S": ["011", "110"],
    "T": ["111", "010"],
    "L": ["10", "10", "11"],
    "J": ["01", "01", "11"],
}

# Convert to int bitmasks for the grid: v[::-1] = rows bottom-up (row 0 = bottom of piece),
# x[::-1] = bits reversed so column 0 of the piece is the LSB (so "shift by x0" aligns correctly).
SHAPE_MASKS = {k: [int(x[::-1], 2) for x in v[::-1]] for k, v in SHAPES.items()}


def place_piece(piece, grid_rows):
    """
    Places one piece into the grid

    :param piece: str, contains the shape and location information from the input
    :param grid_rows: list of int, each number whose binary is the bitmask of the row
    :return: grid_rows after the piece placed
    """
    shape_masks = SHAPE_MASKS[piece[0]]
    x0 = int(piece[1:])

    # Simulate drop: start with piece one row above the top of the stack and move down
    # until any part would overlap existing blocks or the floor (y0 = 0).
    y0 = len(grid_rows) + 1
    overlap = False
    while not overlap:
        y0 -= 1
        if y0 == 0:
            break
        # Check overlap if the piece were placed one row lower (at y0-1); if so, it rests at y0.
        for i, row_mask in enumerate(shape_masks):
            y = y0 - 1 + i  # Grid row index for this piece row when placed at y0-1
            if y >= len(grid_rows):
                break
            if grid_rows[y] & (row_mask << x0):
                overlap = True
                break

    # Write the piece into the grid: OR each piece row into the corresponding grid row.
    # Append new rows if the piece extends above the current top.
    for i, row_mask in enumerate(shape_masks):
        if y0 + i >= len(grid_rows):
            grid_rows.append(0)
        grid_rows[y0 + i] |= row_mask << x0

    # Clear any completed rows (they disappear; rows above effectively “drop” by removal).
    return [r for r in grid_rows if r != FULL_ROW]


def process_line(line):
    """Process one input line: place each piece in order, then return final height."""
    grid_rows = []
    pieces = (x.strip() for x in line.strip().split(",") if x.strip())
    for piece in pieces:
        grid_rows = place_piece(piece, grid_rows)
    return len(grid_rows)


def main():
    """Read lines from stdin, print one height per line."""
    outputs = []
    for line in fileinput.input():
        line = line.strip()
        if not line:
            continue
        print(process_line(line))
        # outputs.append(str(process_line(line)))
    # print(outputs)
    # sys.stdout.write("\n".join(outputs))


if __name__ == "__main__":
    main()
