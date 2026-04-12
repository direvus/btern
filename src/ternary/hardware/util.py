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
COLOURS_3T = {
    '---': '000000',
    '--0': '00007F',
    '--+': '0000FF',
    '-0-': '007F00',
    '-00': '007F7F',
    '-0+': '007FFF',
    '-+-': '00FF00',
    '-+0': '00FF7F',
    '-++': '00FFFF',
    '0--': '7F0000',
    '0-0': '7F007F',
    '0-+': '7F00FF',
    '00-': '7F7F00',
    '000': '7F7F7F',
    '00+': '7F7FFF',
    '0+-': '7FFF00',
    '0+0': '7FFF7F',
    '0++': '7FFFFF',
    '+--': 'FF0000',
    '+-0': 'FF007F',
    '+-+': 'FF00FF',
    '+0-': 'FF7F00',
    '+00': 'FF7F7F',
    '+0+': 'FF7FFF',
    '++-': 'FFFF00',
    '++0': 'FFFF7F',
    '+++': 'FFFFFF',
}

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


def trits_to_colour(t: Trits) -> str:
    """Map a 3-trit sequence to a colour.
    
    Each 3-trit sequence maps to a colour in a 27-colour RGB space. The first trit controls the red quantity, the second trit controls the green and the third trits controls the blue. A negative trit means none of that colour value, a zero trit means 50% and a positive trit means 100%.
    
    If the supplied trit sequence is longer than 3 trits, only the first 3 trits are used and any excess is ignored.

    If the suppled trit sequence is shorter than 3 trits, a ValueError is raised.

    The colour is returned as a six-character hexadecimal string, for example:
    
    >>> trits_to_colour('-0+')
    '007FFF' 
    """
    try:
        return COLOURS_3T[t[:3]]
    except KeyError:
        raise ValueError(f"Invalid colour sequence '{t}'")
