"""
Bitwise solution for simplified Tetris engine.

Grid and pieces are represented with bitmasks: each row is an int with bits
for columns (1 = filled, 0 = empty).
"""
import fileinput
from math import inf

WIDTH = 10

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

# Convert to int bitmasks for the grid: column bitmasks (bottom bit = row 0).
SHAPE_MASKS = {k: [int(''.join(x), 2) for x in zip(*v)] for k, v in SHAPES.items()}
# First filled row (from bottom) for each column mask, used to align pieces.
FIRST_NONZERO_ROWS = {k: [(x & -x).bit_length() - 1 for x in v] for k, v in SHAPE_MASKS.items()}

def place_piece(piece, grid_columns):
    shape = SHAPES[piece[0]]
    x0 = int(piece.strip()[1:])
    piece_height = len(shape)
    piece_width = len(shape[0])

    # construct column bitmasks
    column_masks = SHAPE_MASKS[piece[0]]
    first_one_rows = FIRST_NONZERO_ROWS[piece[0]]
    cols_at_piece = grid_columns[x0: x0+piece_width]
    col_bit_lengths = [c.bit_length() for c in cols_at_piece]
    # Compute landing height by aligning the first filled cell of each column
    # to sit on top of the existing stack heights in that column.
    # Why this always yields a valid y0:
    # - For each piece column i, r_i is the row index of its lowest filled cell.
    # - The piece is validly placed when all columns are at or above their current
    #   stack heights, and at least one column's lowest filled cell touches the
    #   top of the stack (so it is not floating).
    # - The candidate y0 = y - r_i (where y is the current stack height in col i)
    #   represents exactly that "touching" placement for column i. We take the
    #   minimum such y0 that also satisfies the height constraints for all columns.
    y0 = inf
    for i, col in enumerate(cols_at_piece):
        r_i = first_one_rows[i]
        y = col.bit_length()
        valid = all(y + r - r_i >= n for r, n in zip(first_one_rows, col_bit_lengths))
        if valid and y >= r_i:
            y0 = min(y0, y - r_i)

    for i, col_mask in enumerate(column_masks):
        # no need to check for index out of bound because assuming the input piece is always valid
        grid_columns[x0 + i] |= col_mask << y0

    # Check for full rows: bit = 1 means the row is full across all columns.
    full_row_mask = grid_columns[0]
    for col in grid_columns:
        full_row_mask &= col

    if not full_row_mask:
        return

    # Only rows touched by the new piece can become full.
    full_rows = [idx for idx in range(y0, y0 + piece_height) if full_row_mask & (1 << idx)]

    # Clear full rows by compacting segments between cleared rows.
    for i, col in enumerate(grid_columns):
        new_col = 0
        higher_bits = col
        for shift, r in enumerate(full_rows):
            higher_bits, lower_bits = divmod(higher_bits, 1 << r)  # divide higher_bits by 2**r
            # Remove the r-th bit and keep higher bits aligned to original indices.
            higher_bits = (higher_bits >> 1) << (r + 1)
            new_col |= lower_bits >> shift

        new_col |= higher_bits >> len(full_rows)
        grid_columns[i] = new_col


def process_line(line):
    """Process one input line: place each piece in order, then return final height."""
    grid_columns = [0] * WIDTH
    pieces = (x.strip() for x in line.strip().split(",") if x.strip())
    for piece in pieces:
        place_piece(piece, grid_columns)
    return max(grid_columns).bit_length()


def main():
    """Read lines from stdin, print one height per line."""
    for line in fileinput.input():
        line = line.strip()
        if not line:
            continue
        print(process_line(line))


if __name__ == "__main__":
    main()
