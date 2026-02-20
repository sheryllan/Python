#!/usr/bin/env python3
import sys

WIDTH = 10
FULL_ROW = (1 << WIDTH) - 1

PIECES = {
    "Q": [(0, 0), (1, 0), (0, 1), (1, 1)],
    "I": [(0, 0), (1, 0), (2, 0), (3, 0)],
    "Z": [(0, 1), (1, 1), (1, 0), (2, 0)],
    "S": [(1, 1), (2, 1), (0, 0), (1, 0)],
    "T": [(0, 1), (1, 1), (2, 1), (1, 0)],
    "L": [(0, 0), (0, 1), (0, 2), (1, 0)],
    "J": [(1, 0), (1, 1), (1, 2), (0, 0)],
    "X": [(0, 0), (0, 1), (1, 1), (2, 1)]
}


def collides(rows, shape, x0, y_base):
    for dx, dy in shape:
        x = x0 + dx
        y = y_base + dy
        if y < 0:
            return True
        if y < len(rows) and (rows[y] >> x) & 1:
            return True
    return False


def place_piece(rows, shape, x0):
    y_base = len(rows) + 4
    while True:
        if collides(rows, shape, x0, y_base - 1):
            break
        y_base -= 1

    for dx, dy in shape:
        x = x0 + dx
        y = y_base + dy
        while y >= len(rows):
            rows.append(0)
        rows[y] |= 1 << x

    rows[:] = [row for row in rows if row != FULL_ROW]


def process_line(line):
    rows = []
    tokens = [t.strip() for t in line.strip().split(",") if t.strip()]
    for token in tokens:
        shape = PIECES[token[0]]
        x0 = int(token[1])
        place_piece(rows, shape, x0)
    return str(len(rows))


def main():
    outputs = []
    for raw in sys.stdin:
        if raw.strip() == "":
            continue
        outputs.append(process_line(raw))
    sys.stdout.write("\n".join(outputs))


if __name__ == "__main__":
    # print(process_line("Z0, S3, Q6, Q8, J2, X0, X5"))
    main()



