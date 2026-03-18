from hwsim.component import (
        Component, NAND, NCONS, NOR, NANY, NOT, PNOT, NNOT)


class And(Component):
    """The AND gate performs logical conjunction of the inputs.

    The output is true if and only if both inputs are true.

    (a AND b) == NOT (a NAND b)
    """
    def __init__(self):
        super().__init__(
                ('a', 'b'),
                ('out',),
                {'Nand': NAND, 'Not': NOT},
                {
                    'out': 'Not.out',
                    'Not.in': 'Nand.out',
                    'Nand.a': 'a',
                    'Nand.b': 'b',
                    })


class Or(Component):
    """The OR gate performs logical disjunction of the inputs.

    The output is true if either (or both) of the inputs are true.

    (a OR b) == NOT (a NOR b)
    """
    def __init__(self):
        super().__init__(
                ('a', 'b'),
                ('out',),
                {'Nor': NOR, 'Not': NOT},
                {
                    'out': 'Not.out',
                    'Not.in': 'Nor.out',
                    'Nor.a': 'a',
                    'Nor.b': 'b',
                    })


class Any(Component):
    """The ANY gate detects an overall bias of the inputs.

    The output is zero if the inputs are positive and negative, or both zero.
    Otherwise, the output is positive if there is any positive signal in the
    inputs, or negative if there is any negative signal.

    (a ANY b) == NOT (a NANY b)
    """
    def __init__(self):
        super().__init__(
                ('a', 'b'),
                ('out',),
                {'NAny': NANY, 'Not': NOT},
                {
                    'out': 'Not.out',
                    'Not.in': 'NAny.out',
                    'NAny.a': 'a',
                    'NAny.b': 'b',
                    })


class Xor(Component):
    """The XOR gate performs logical exclusive disjunction of the inputs.

    The output is true if either one of the inputs is true, but not both.

    It consists of four primitive gates: a NAND, a NOT and two NORS. Both
    inputs are separately passed to a NAND gate and a NOR gate, the result of
    the NAND is inverted, and those two results are passed to a NOR gate to
    produce the final output.

    (a XOR b) == (NOT (a NAND b)) NOR (a NOR b)
    """
    def __init__(self):
        super().__init__(
                ('a', 'b'),
                ('out',),
                {'Nand': NAND, 'NorAB': NOR, 'Not': NOT, 'NorOut': NOR},
                {
                    'out': 'NorOut.out',
                    'NorOut.a': 'Not.out',
                    'NorOut.b': 'NorAB.out',
                    'Not.in': 'Nand.out',
                    'Nand.a': 'a',
                    'Nand.b': 'b',
                    'NorAB.a': 'a',
                    'NorAB.b': 'b',
                    })


class NXor(Component):
    """The NXOR gate performs negative exclusive disjunction of the inputs.

    The output is positive if the inputs are either both positive, or both
    negative.

    It consists of four primitive gates: two NANDs, a NOR and a NOT. Both
    inputs are separately passed to a NAND gate and a NOR gate, the result of
    the NOR is inverted, and those two results are passed to a NAND gate to
    produce the final output.

    (a NXOR b) == (NOT (a NOR b)) NAND (a NAND b)
    """
    def __init__(self):
        super().__init__(
                ('a', 'b'),
                ('out',),
                {'NandAB': NAND, 'NandOut': NAND, 'Nor': NOR, 'Not': NOT},
                {
                    'out': 'NandOut.out',
                    'NandOut.a': 'Not.out',
                    'NandOut.b': 'NandAB.out',
                    'Not.in': 'Nor.out',
                    'Nor.a': 'a',
                    'Nor.b': 'b',
                    'NandAB.a': 'a',
                    'NandAB.b': 'b',
                    })


class IsZero(Component):
    """The ISZ gate tests whether the input is zero.

    The output is positive if the input value is zero, and negative otherwise.

    | in  | out |
    |=====|=====|
    |  -  |  -  |
    |  0  |  +  |
    |  +  |  -  |

    ISZ(a) == PNOT(NAND(¬in, in))
    """
    def __init__(self):
        super().__init__(
                ('in',),
                ('out',),
                {
                    'PNot': PNOT,
                    'Not': NOT,
                    'NAnd': NAND,
                    },
                {
                    'out': 'PNot.out',
                    'PNot.in': 'NAnd.out',
                    'NAnd.a': 'in',
                    'NAnd.b': 'Not.out',
                    'Not.in': 'in',
                    })


class Mux(Component):
    """The MUX gate is a single trit, 3-way multiplexer.

    It selects one of its three data inputs, based on the value of a fourth
    'selector' input, and produces the selected input signal on its output.

    The three data inputs are named 'a', 'b' and 'c', and the selector input is
    named 's'. The input value is selected as follows:

    |  s  | out |
    |=====|=====|
    |  -  |  a  |
    |  0  |  b  |
    |  +  |  c  |

    The complete truth table for all four inputs is:

    |   | c | - | - | - | 0 | 0 | 0 | + | + | + |
    |   | s | - | 0 | + | - | 0 | + | - | 0 | + |
    | a | b |   |   |   |   |   |   |   |   |   |
    |===|===|===|===|===|===|===|===|===|===|===|
    | - | - | - | - | - | - | - | 0 | - | - | + |
    | - | 0 | - | 0 | - | - | 0 | 0 | - | 0 | + |
    | - | + | - | + | - | - | + | 0 | - | + | + |
    | 0 | - | 0 | - | - | 0 | - | 0 | 0 | - | + |
    | 0 | 0 | 0 | 0 | - | 0 | 0 | 0 | 0 | 0 | + |
    | 0 | + | 0 | + | - | 0 | + | 0 | 0 | + | + |
    | + | - | + | - | - | + | - | 0 | + | - | + |
    | + | 0 | + | 0 | - | + | 0 | 0 | + | 0 | + |
    | + | + | + | + | - | + | + | 0 | + | + | + |
    """
    def __init__(self):
        super().__init__(
                ('a', 'b', 'c', 's'),
                ('out',),
                {
                    'NandABC': NAND,
                    'NandAB': NAND,
                    'NandA': NAND,
                    'NandB': NAND,
                    'NandC': NAND,
                    'NotAB': NOT,
                    'NNot': NNOT,
                    'ISZ': IsZero,
                    'PNot1': PNOT,
                    'PNot2': PNOT,
                    },
                {
                    'out': 'NandABC.out',
                    'NandABC.a': 'NotAB.out',
                    'NandABC.b': 'NandC.out',
                    'NotAB.in': 'NandAB.out',
                    'NandAB.a': 'NandA.out',
                    'NandAB.b': 'NandB.out',
                    'NandA.a': 'a',
                    'NandA.b': 'NNot.out',
                    'NNot.in': 's',
                    'NandB.a': 'b',
                    'NandB.b': 'ISZ.out',
                    'ISZ.in': 's',
                    'NandC.a': 'c',
                    'NandC.b': 'PNot2.out',
                    'PNot2.in': 'PNot1.out',
                    'PNot1.in': 's',
                    })


class Not12(Component):
    def __init__(self):
        super().__init__(
                ('in[12]',),
                ('out[12]',),
                {
                    'Not0': NOT,
                    'Not1': NOT,
                    'Not2': NOT,
                    'Not3': NOT,
                    'Not4': NOT,
                    'Not5': NOT,
                    'Not6': NOT,
                    'Not7': NOT,
                    'Not8': NOT,
                    'Not9': NOT,
                    'Not10': NOT,
                    'Not11': NOT,
                    },
                {
                    'out[0]': 'Not0.out',
                    'out[1]': 'Not1.out',
                    'out[2]': 'Not2.out',
                    'out[3]': 'Not3.out',
                    'out[4]': 'Not4.out',
                    'out[5]': 'Not5.out',
                    'out[6]': 'Not6.out',
                    'out[7]': 'Not7.out',
                    'out[8]': 'Not8.out',
                    'out[9]': 'Not9.out',
                    'out[10]': 'Not10.out',
                    'out[11]': 'Not11.out',
                    'Not0.in': 'in[0]',
                    'Not1.in': 'in[1]',
                    'Not2.in': 'in[2]',
                    'Not3.in': 'in[3]',
                    'Not4.in': 'in[4]',
                    'Not5.in': 'in[5]',
                    'Not6.in': 'in[6]',
                    'Not7.in': 'in[7]',
                    'Not8.in': 'in[8]',
                    'Not9.in': 'in[9]',
                    'Not10.in': 'in[10]',
                    'Not11.in': 'in[11]',
                    })


class And12(Component):
    def __init__(self):
        super().__init__(
                ('a[12]', 'b[12]'),
                ('out[12]',),
                {
                    'And0': And,
                    'And1': And,
                    'And2': And,
                    'And3': And,
                    'And4': And,
                    'And5': And,
                    'And6': And,
                    'And7': And,
                    'And8': And,
                    'And9': And,
                    'And10': And,
                    'And11': And,
                    },
                {
                    'out[0]': 'And0.out',
                    'out[1]': 'And1.out',
                    'out[2]': 'And2.out',
                    'out[3]': 'And3.out',
                    'out[4]': 'And4.out',
                    'out[5]': 'And5.out',
                    'out[6]': 'And6.out',
                    'out[7]': 'And7.out',
                    'out[8]': 'And8.out',
                    'out[9]': 'And9.out',
                    'out[10]': 'And10.out',
                    'out[11]': 'And11.out',
                    'And0.a': 'a[0]',
                    'And0.b': 'b[0]',
                    'And1.a': 'a[1]',
                    'And1.b': 'b[1]',
                    'And2.a': 'a[2]',
                    'And2.b': 'b[2]',
                    'And3.a': 'a[3]',
                    'And3.b': 'b[3]',
                    'And4.a': 'a[4]',
                    'And4.b': 'b[4]',
                    'And5.a': 'a[5]',
                    'And5.b': 'b[5]',
                    'And6.a': 'a[6]',
                    'And6.b': 'b[6]',
                    'And7.a': 'a[7]',
                    'And7.b': 'b[7]',
                    'And8.a': 'a[8]',
                    'And8.b': 'b[8]',
                    'And9.a': 'a[9]',
                    'And9.b': 'b[9]',
                    'And10.a': 'a[10]',
                    'And10.b': 'b[10]',
                    'And11.a': 'a[11]',
                    'And11.b': 'b[11]',
                    })


class Mux12(Component):
    """A 12 trit, 3-way multiplexer.

    It selects one of its three data input buses, based on the value of a
    fourth 'selector' input, and produces the selected input bus values on its
    output bus.

    The three data input buses are named 'a', 'b' and 'c', and the selector
    input is named 's'. The output value is determined as follows:

    |  s  | out |
    |=====|=====|
    |  -  |  a  |
    |  0  |  b  |
    |  +  |  c  |
    """
    def __init__(self):
        super().__init__(
                ('a[12]', 'b[12]', 'c[12]', 's'),
                ('out[12]',),
                {
                    'NNotS': NNOT,
                    'ISZ': IsZero,
                    'PNotS': PNOT,
                    'PNotPNotS': PNOT,
                    'NAnd0ABC': NAND,
                    'NAnd0AB': NAND,
                    'NAnd0A': NAND,
                    'NAnd0B': NAND,
                    'NAnd0C': NAND,
                    'Not0AB': NOT,
                    'NAnd1ABC': NAND,
                    'NAnd1AB': NAND,
                    'NAnd1A': NAND,
                    'NAnd1B': NAND,
                    'NAnd1C': NAND,
                    'Not1AB': NOT,
                    'NAnd2ABC': NAND,
                    'NAnd2AB': NAND,
                    'NAnd2A': NAND,
                    'NAnd2B': NAND,
                    'NAnd2C': NAND,
                    'Not2AB': NOT,
                    'NAnd3ABC': NAND,
                    'NAnd3AB': NAND,
                    'NAnd3A': NAND,
                    'NAnd3B': NAND,
                    'NAnd3C': NAND,
                    'Not3AB': NOT,
                    'NAnd4ABC': NAND,
                    'NAnd4AB': NAND,
                    'NAnd4A': NAND,
                    'NAnd4B': NAND,
                    'NAnd4C': NAND,
                    'Not4AB': NOT,
                    'NAnd5ABC': NAND,
                    'NAnd5AB': NAND,
                    'NAnd5A': NAND,
                    'NAnd5B': NAND,
                    'NAnd5C': NAND,
                    'Not5AB': NOT,
                    'NAnd6ABC': NAND,
                    'NAnd6AB': NAND,
                    'NAnd6A': NAND,
                    'NAnd6B': NAND,
                    'NAnd6C': NAND,
                    'Not6AB': NOT,
                    'NAnd7ABC': NAND,
                    'NAnd7AB': NAND,
                    'NAnd7A': NAND,
                    'NAnd7B': NAND,
                    'NAnd7C': NAND,
                    'Not7AB': NOT,
                    'NAnd8ABC': NAND,
                    'NAnd8AB': NAND,
                    'NAnd8A': NAND,
                    'NAnd8B': NAND,
                    'NAnd8C': NAND,
                    'Not8AB': NOT,
                    'NAnd9ABC': NAND,
                    'NAnd9AB': NAND,
                    'NAnd9A': NAND,
                    'NAnd9B': NAND,
                    'NAnd9C': NAND,
                    'Not9AB': NOT,
                    'NAnd10ABC': NAND,
                    'NAnd10AB': NAND,
                    'NAnd10A': NAND,
                    'NAnd10B': NAND,
                    'NAnd10C': NAND,
                    'Not10AB': NOT,
                    'NAnd11ABC': NAND,
                    'NAnd11AB': NAND,
                    'NAnd11A': NAND,
                    'NAnd11B': NAND,
                    'NAnd11C': NAND,
                    'Not11AB': NOT,
                    },
                {
                    'NNotS.in': 's',
                    'ISZ.in': 's',
                    'PNotPNotS.in': 'PNotS.out',
                    'PNotS.in': 's',
                    'out[0]': 'NAnd0ABC.out',
                    'NAnd0ABC.a': 'Not0AB.out',
                    'NAnd0ABC.b': 'NAnd0C.out',
                    'Not0AB.in': 'NAnd0AB.out',
                    'NAnd0AB.a': 'NAnd0A.out',
                    'NAnd0AB.b': 'NAnd0B.out',
                    'NAnd0A.a': 'a[0]',
                    'NAnd0A.b': 'NNotS.out',
                    'NAnd0B.a': 'b[0]',
                    'NAnd0B.b': 'ISZ.out',
                    'NAnd0C.a': 'c[0]',
                    'NAnd0C.b': 'PNotPNotS.out',
                    'out[1]': 'NAnd1ABC.out',
                    'NAnd1ABC.a': 'Not1AB.out',
                    'NAnd1ABC.b': 'NAnd1C.out',
                    'Not1AB.in': 'NAnd1AB.out',
                    'NAnd1AB.a': 'NAnd1A.out',
                    'NAnd1AB.b': 'NAnd1B.out',
                    'NAnd1A.a': 'a[1]',
                    'NAnd1A.b': 'NNotS.out',
                    'NAnd1B.a': 'b[1]',
                    'NAnd1B.b': 'ISZ.out',
                    'NAnd1C.a': 'c[1]',
                    'NAnd1C.b': 'PNotPNotS.out',
                    'out[2]': 'NAnd2ABC.out',
                    'NAnd2ABC.a': 'Not2AB.out',
                    'NAnd2ABC.b': 'NAnd2C.out',
                    'Not2AB.in': 'NAnd2AB.out',
                    'NAnd2AB.a': 'NAnd2A.out',
                    'NAnd2AB.b': 'NAnd2B.out',
                    'NAnd2A.a': 'a[2]',
                    'NAnd2A.b': 'NNotS.out',
                    'NAnd2B.a': 'b[2]',
                    'NAnd2B.b': 'ISZ.out',
                    'NAnd2C.a': 'c[2]',
                    'NAnd2C.b': 'PNotPNotS.out',
                    'out[3]': 'NAnd3ABC.out',
                    'NAnd3ABC.a': 'Not3AB.out',
                    'NAnd3ABC.b': 'NAnd3C.out',
                    'Not3AB.in': 'NAnd3AB.out',
                    'NAnd3AB.a': 'NAnd3A.out',
                    'NAnd3AB.b': 'NAnd3B.out',
                    'NAnd3A.a': 'a[3]',
                    'NAnd3A.b': 'NNotS.out',
                    'NAnd3B.a': 'b[3]',
                    'NAnd3B.b': 'ISZ.out',
                    'NAnd3C.a': 'c[3]',
                    'NAnd3C.b': 'PNotPNotS.out',
                    'out[4]': 'NAnd4ABC.out',
                    'NAnd4ABC.a': 'Not4AB.out',
                    'NAnd4ABC.b': 'NAnd4C.out',
                    'Not4AB.in': 'NAnd4AB.out',
                    'NAnd4AB.a': 'NAnd4A.out',
                    'NAnd4AB.b': 'NAnd4B.out',
                    'NAnd4A.a': 'a[4]',
                    'NAnd4A.b': 'NNotS.out',
                    'NAnd4B.a': 'b[4]',
                    'NAnd4B.b': 'ISZ.out',
                    'NAnd4C.a': 'c[4]',
                    'NAnd4C.b': 'PNotPNotS.out',
                    'out[5]': 'NAnd5ABC.out',
                    'NAnd5ABC.a': 'Not5AB.out',
                    'NAnd5ABC.b': 'NAnd5C.out',
                    'Not5AB.in': 'NAnd5AB.out',
                    'NAnd5AB.a': 'NAnd5A.out',
                    'NAnd5AB.b': 'NAnd5B.out',
                    'NAnd5A.a': 'a[5]',
                    'NAnd5A.b': 'NNotS.out',
                    'NAnd5B.a': 'b[5]',
                    'NAnd5B.b': 'ISZ.out',
                    'NAnd5C.a': 'c[5]',
                    'NAnd5C.b': 'PNotPNotS.out',
                    'out[6]': 'NAnd6ABC.out',
                    'NAnd6ABC.a': 'Not6AB.out',
                    'NAnd6ABC.b': 'NAnd6C.out',
                    'Not6AB.in': 'NAnd6AB.out',
                    'NAnd6AB.a': 'NAnd6A.out',
                    'NAnd6AB.b': 'NAnd6B.out',
                    'NAnd6A.a': 'a[6]',
                    'NAnd6A.b': 'NNotS.out',
                    'NAnd6B.a': 'b[6]',
                    'NAnd6B.b': 'ISZ.out',
                    'NAnd6C.a': 'c[6]',
                    'NAnd6C.b': 'PNotPNotS.out',
                    'out[7]': 'NAnd7ABC.out',
                    'NAnd7ABC.a': 'Not7AB.out',
                    'NAnd7ABC.b': 'NAnd7C.out',
                    'Not7AB.in': 'NAnd7AB.out',
                    'NAnd7AB.a': 'NAnd7A.out',
                    'NAnd7AB.b': 'NAnd7B.out',
                    'NAnd7A.a': 'a[7]',
                    'NAnd7A.b': 'NNotS.out',
                    'NAnd7B.a': 'b[7]',
                    'NAnd7B.b': 'ISZ.out',
                    'NAnd7C.a': 'c[7]',
                    'NAnd7C.b': 'PNotPNotS.out',
                    'out[8]': 'NAnd8ABC.out',
                    'NAnd8ABC.a': 'Not8AB.out',
                    'NAnd8ABC.b': 'NAnd8C.out',
                    'Not8AB.in': 'NAnd8AB.out',
                    'NAnd8AB.a': 'NAnd8A.out',
                    'NAnd8AB.b': 'NAnd8B.out',
                    'NAnd8A.a': 'a[8]',
                    'NAnd8A.b': 'NNotS.out',
                    'NAnd8B.a': 'b[8]',
                    'NAnd8B.b': 'ISZ.out',
                    'NAnd8C.a': 'c[8]',
                    'NAnd8C.b': 'PNotPNotS.out',
                    'out[9]': 'NAnd9ABC.out',
                    'NAnd9ABC.a': 'Not9AB.out',
                    'NAnd9ABC.b': 'NAnd9C.out',
                    'Not9AB.in': 'NAnd9AB.out',
                    'NAnd9AB.a': 'NAnd9A.out',
                    'NAnd9AB.b': 'NAnd9B.out',
                    'NAnd9A.a': 'a[9]',
                    'NAnd9A.b': 'NNotS.out',
                    'NAnd9B.a': 'b[9]',
                    'NAnd9B.b': 'ISZ.out',
                    'NAnd9C.a': 'c[9]',
                    'NAnd9C.b': 'PNotPNotS.out',
                    'out[10]': 'NAnd10ABC.out',
                    'NAnd10ABC.a': 'Not10AB.out',
                    'NAnd10ABC.b': 'NAnd10C.out',
                    'Not10AB.in': 'NAnd10AB.out',
                    'NAnd10AB.a': 'NAnd10A.out',
                    'NAnd10AB.b': 'NAnd10B.out',
                    'NAnd10A.a': 'a[10]',
                    'NAnd10A.b': 'NNotS.out',
                    'NAnd10B.a': 'b[10]',
                    'NAnd10B.b': 'ISZ.out',
                    'NAnd10C.a': 'c[10]',
                    'NAnd10C.b': 'PNotPNotS.out',
                    'out[11]': 'NAnd11ABC.out',
                    'NAnd11ABC.a': 'Not11AB.out',
                    'NAnd11ABC.b': 'NAnd11C.out',
                    'Not11AB.in': 'NAnd11AB.out',
                    'NAnd11AB.a': 'NAnd11A.out',
                    'NAnd11AB.b': 'NAnd11B.out',
                    'NAnd11A.a': 'a[11]',
                    'NAnd11A.b': 'NNotS.out',
                    'NAnd11B.a': 'b[11]',
                    'NAnd11B.b': 'ISZ.out',
                    'NAnd11C.a': 'c[11]',
                    'NAnd11C.b': 'PNotPNotS.out',
                    })


class Demux(Component):
    """A single trit, 3-way demultiplexer.

    The demultiplexer takes two inputs, 'in' and 's'. It has three outputs,
    'a', 'b' and 'c'.

    The input value will be produced on one of the three outputs, selected
    according to the value of 's':

    | s | out |
    |===|=====|
    | - |  a  |
    | 0 |  b  |
    | + |  c  |

    The two outputs that are not selected will always have the value zero.
    Therefore, the complete truth table is as follows:

    | in | s | a | b | c |
    |====|===|===|===|===|
    | -  | - | - | 0 | 0 |
    | -  | 0 | 0 | - | 0 |
    | -  | + | 0 | 0 | - |
    | 0  | - | 0 | 0 | 0 |
    | 0  | 0 | 0 | 0 | 0 |
    | 0  | + | 0 | 0 | 0 |
    | +  | - | + | 0 | 0 |
    | +  | 0 | 0 | + | 0 |
    | +  | + | 0 | 0 | + |
    """
    def __init__(self):
        super().__init__(
                ('in', 's'),
                ('a', 'b', 'c'),
                {
                    'NotS': NOT,
                    'NConsA': NCONS,
                    'NConsB': NCONS,
                    'NConsC': NCONS,
                    'NOrA': NOR,
                    'NOrC': NOR,
                    'NAndA': NAND,
                    'NAndC': NAND,
                    'NAnyB1': NANY,
                    'NAnyB2': NANY,
                    },
                {
                    'a': 'NConsA.out',
                    'b': 'NConsB.out',
                    'c': 'NConsC.out',
                    'NotS.in': 's',
                    'NConsA.a': 'NOrA.out',
                    'NConsA.b': 'NAndA.out',
                    'NConsB.a': 'NAnyB1.out',
                    'NConsB.b': 'NAnyB2.out',
                    'NConsC.a': 'NAndC.out',
                    'NConsC.b': 'NOrC.out',
                    'NOrA.a': 'in',
                    'NOrA.b': 's',
                    'NAndA.a': 'in',
                    'NAndA.b': 'NotS.out',
                    'NAnyB1.a': 'in',
                    'NAnyB1.b': 's',
                    'NAnyB2.a': 'in',
                    'NAnyB2.b': 'NotS.out',
                    'NAndC.a': 'in',
                    'NAndC.b': 's',
                    'NOrC.a': 'in',
                    'NOrC.b': 'NotS.out',
                    })
