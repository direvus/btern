import sys
from collections.abc import Iterable
from contextlib import contextmanager
from typing import Literal

from ternary.trit import ZERO, POS, NEG


Trit = Literal[NEG, ZERO, POS]
Trits = Iterable[Trit]

WORD_SIZE = 12
ADDR_SIZE = 11
MAX_ADDR = (3 ** ADDR_SIZE) // 2
MIN_ADDR = -MAX_ADDR
MAX_INT = (3 ** WORD_SIZE) // 2
MIN_INT = -MAX_INT
INT_RANGE = 3 ** 12


@contextmanager
def input_stream(path):
    if path == '-':
        yield sys.stdin
    else:
        fp = open(path, 'r')
        try:
            yield fp
        finally:
            fp.close()


@contextmanager
def output_stream(path):
    if path == '-':
        yield sys.stdout
    else:
        fp = open(path, 'w')
        try:
            yield fp
        finally:
            fp.close()


def trits_to_int(trits: Trits) -> int:
    """Convert a sequence of trits into a Python integer.

    The trits are interpreted from least signficant at index 0, to most
    significant at the end of the sequence.
    """
    result = 0
    scale = 1
    for t in trits:
        if t != ZERO:
            value = 1 if t == POS else -1
            result += value * scale
        scale *= 3
    return result


def int_to_trits(n: int, size: int) -> Trits:
    """Convert a Python decimal integer into a fixed-length sequence of trits.

    The trits are organised from least significant at index 0, to most
    significant at the end of the sequence.

    Raises an error if the given integer cannot be represented in the given
    number of trits.
    """
    if size <= 0:
        raise ValueError(f"Invalid trit size {size}")
    trit_map = '-0+'
    m = (3 ** size) // 2
    if n < -m or n > m:
        raise ValueError(f"Integer {n} cannot be represented in {size} trits")

    # Shift to an unsigned equivalent
    x = n + m
    result = []
    for _ in range(size):
        x, rem = divmod(x, 3)
        result.append(trit_map[rem])
    return ''.join(result)
