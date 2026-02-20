"""
Bitwise solution for simplified Tetris engine.

Grid and pieces are represented with bitmasks: each row is an int with bits
for columns (1 = filled, 0 = empty).
"""
import fileinput

WIDTH = 10
FULL_ROW = (1 << WIDTH) - 1  # All 10 columns set; used to detect a completed row
MAX_ROWS = 100

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

# Convert to int bitmasks for the grid: column bitmasks
SHAPE_MASKS = {k: [int(''.join(x), 2) for x in zip(*v)] for k, v in SHAPES.items()}

def lowest_set_bit_index(value):
    """Return index of lowest 1 bit; -1 if value is 0."""
    if value == 0:
        return -1
    return (value & -value).bit_length() - 1

def place_piece(piece, grid_columns):
    shape = SHAPES[piece[0]]
    x0 = int(piece.strip()[1:])
    piece_height = len(shape)
    piece_width = len(shape[0])

    # construct column bitmasks
    column_masks = SHAPE_MASKS[piece[0]]
    y0 = max(grid_columns[x0: x0+piece_width]).bit_length()
    while y0 > 0:
        y = y0 - 1
        overlap = any(grid_mask & col_mask << y for col_mask, grid_mask
                      in zip(column_masks, grid_columns[x0: x0 + piece_width]))
        if overlap:
            break

        y0 = y

    for i, col_mask in enumerate(column_masks):
        # no need to check for index out of bound because assuming the input piece is always valid
        grid_columns[x0 + i] |= col_mask << y0

    # check for full rows, bits equal to 1 is where the rows are full
    full_row_mask = grid_columns[0]
    for col in grid_columns:
        full_row_mask &= col

    if not full_row_mask:
        return

    # only rows touched by the new piece can become full
    full_rows = [idx for idx in range(y0, y0 + piece_height) if full_row_mask & (1 << idx)]

    # clear the full row bits in the grid_columns by compacting segments
    for i, col in enumerate(grid_columns):
        new_col = 0
        prev = -1
        bit_len = col.bit_length()
        full_rows.append(bit_len)
        for shift, curr in enumerate(full_rows):
            interval = curr - prev - 1
            if interval > 0:
                value = col & (((1 << interval) - 1) << (prev + 1))
                new_col |= value >> shift
            prev = curr

        grid_columns[i] = new_col
        full_rows.pop()


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
