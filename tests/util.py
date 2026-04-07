from collections.abc import Iterable

from ternary.trit import ZERO, POS, NEG


N = NEG
Z = ZERO
P = POS
# Assemble standard input lists for chips with 1, 2, 3 or 4 inputs.
TRITS = (NEG, ZERO, POS)
UNARY = tuple((a,) for a in TRITS)
BINARY = tuple((a, b) for a in TRITS for b in TRITS)
TRINARY = tuple((a, b, c) for a in TRITS for b in TRITS for c in TRITS)
QUATERNARY = tuple((a, b, c, d)
                   for a in TRITS
                   for b in TRITS
                   for c in TRITS
                   for d in TRITS)


def seq_matches(a: Iterable, b: Iterable) -> bool:
    return len(a) == len(b) and all(x == y for x, y in zip(a, b))
