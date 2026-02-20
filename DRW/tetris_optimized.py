import sys

WIDTH = 10
FULL_ROW = (1 << WIDTH) - 1

# Each shape is stored as a list of row bitmasks (bottom-up).
PIECES = {
    "Q": [0b11, 0b11],
    "I": [0b1111],
    "Z": [0b110, 0b011],
    "S": [0b011, 0b110],
    "T": [0b010, 0b111],
    "L": [0b011, 0b001, 0b001],
    "J": [0b011, 0b010, 0b010],
}


def collides(rows, shape_rows, x0, y_base):
    for i, mask in enumerate(shape_rows):
        y = y_base + i
        if y < 0:
            return True
        shifted = mask << x0
        if y < len(rows) and (rows[y] & shifted):
            return True
    return False


def place_piece(rows, shape_rows, x0):
    y_base = len(rows) + 4
    while True:
        if collides(rows, shape_rows, x0, y_base - 1):
            break
        y_base -= 1

    required_rows = y_base + len(shape_rows)
    while len(rows) < required_rows:
        rows.append(0)

    for i, mask in enumerate(shape_rows):
        rows[y_base + i] |= mask << x0

    rows[:] = [row for row in rows if row != FULL_ROW]


def process_line(line):
    rows = []
    tokens = [t.strip() for t in line.strip().split(",") if t.strip()]
    for token in tokens:
        shape_rows = PIECES[token[0]]
        x0 = int(token[1:])
        place_piece(rows, shape_rows, x0)
    return str(len(rows))


def main():
    outputs = []
    for raw in sys.stdin:
        if raw.strip() == "":
            continue
        outputs.append(process_line(raw))
    sys.stdout.write("\n".join(outputs))


if __name__ == "__main__":
    main()
