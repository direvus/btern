from collections.abc import Iterable
from typing import Literal

from trit import ZERO, POS, NEG


Trit = Literal[NEG, ZERO, POS]
Trits = Iterable[Trit]


def trits_to_int(trits: Trits) -> Trits:
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
