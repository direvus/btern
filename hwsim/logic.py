from hwsim.component import (
        Component, NAND, NOR, NANY, NOT, PNOT, NNOT)


def and_gate():
    """The AND gate performs logical conjunction of the inputs.

    The output is true if and only if both inputs are true.

    (a AND b) == NOT (a NAND b)
    """
    return Component(
            ('a', 'b'),
            ('out',),
            {'Nand': NAND, 'Not': NOT},
            {
                    'out': 'Not.out',
                    'Not.in': 'Nand.out',
                    'Nand.a': 'a',
                    'Nand.b': 'b',
                    })


def or_gate():
    """The OR gate performs logical disjunction of the inputs.

    The output is true if either (or both) of the inputs are true.

    (a OR b) == NOT (a NOR b)
    """
    return Component(
            ('a', 'b'),
            ('out',),
            {'Nor': NOR, 'Not': NOT},
            {
                    'out': 'Not.out',
                    'Not.in': 'Nor.out',
                    'Nor.a': 'a',
                    'Nor.b': 'b',
                    })


def any_gate():
    """The ANY gate detects an overall bias of the inputs.

    The output is zero if the inputs are positive and negative, or both zero.
    Otherwise, the output is positive if there is any positive signal in the
    inputs, or negative if there is any negative signal.

    (a ANY b) == NOT (a NANY b)
    """
    return Component(
            ('a', 'b'),
            ('out',),
            {'NAny': NANY, 'Not': NOT},
            {
                    'out': 'Not.out',
                    'Not.in': 'NAny.out',
                    'NAny.a': 'a',
                    'NAny.b': 'b',
                    })


def xor_gate():
    """The XOR gate performs logical exclusive disjunction of the inputs.

    The output is true if either one of the inputs is true, but not both.

    It consists of four primitive gates: a NAND, a NOT and two NORS. Both
    inputs are separately passed to a NAND gate and a NOR gate, the result of
    the NAND is inverted, and those two results are passed to a NOR gate to
    produce the final output.

    (a XOR b) == (NOT (a NAND b)) NOR (a NOR b)
    """
    return Component(
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


def nxor_gate():
    """The NXOR gate performs negative exclusive disjunction of the inputs.

    The output is positive if the inputs are either both positive, or both
    negative.

    It consists of four primitive gates: two NANDs, a NOR and a NOT. Both
    inputs are separately passed to a NAND gate and a NOR gate, the result of
    the NOR is inverted, and those two results are passed to a NAND gate to
    produce the final output.

    (a NXOR b) == (NOT (a NOR b)) NAND (a NAND b)
    """
    return Component(
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


def isz_gate():
    """The ISZ gate tests whether the input is zero.

    The output is positive if the input value is zero, and negative otherwise.

    | in  | out |
    |=====|=====|
    |  -  |  -  |
    |  0  |  +  |
    |  +  |  -  |

    It consists of two NNOTs, one PNOT, and one AND gate, for a total of
    4 primitive gates.

    ISZ a == (PNOT a) AND (NOT NNOT a)
    """
    return Component(
            ('in',),
            ('out',),
            {
                'PNot': PNOT,
                'NNot': NNOT,
                'Not': NNOT,
                'And': and_gate,
            },
            {
                'out': 'And.out',
                'And.a': 'PNot.out',
                'And.b': 'Not.out',
                'PNot.in': 'in',
                'Not.in': 'NNot.out',
                'NNot.in': 'in',
                })


def mux_gate():
    """The MUX gate is a 3-way multiplexer.

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
    return Component(
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
                'ISZ': isz_gate,
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


def not12():
    return Component(
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


def and12():
    return Component(
            ('a[12]', 'b[12]'),
            ('out[12]',),
            {
                'And0': and_gate,
                'And1': and_gate,
                'And2': and_gate,
                'And3': and_gate,
                'And4': and_gate,
                'And5': and_gate,
                'And6': and_gate,
                'And7': and_gate,
                'And8': and_gate,
                'And9': and_gate,
                'And10': and_gate,
                'And11': and_gate,
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
