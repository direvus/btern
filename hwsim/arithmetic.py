from hwsim.component import Component, NANY, NCONS, NOT, PNOT, nxor_gate


def sum_gate():
    """The sum gate adds two trits together.

    If either input is zero, then the output is the other value. If the inputs
    are positive and negative, then the output is zero. If the inputs are the
    same, then the output is the inverse of the value.

    | a | b | out |
    |===|===|=====|
    | - | - |  +  |
    | - | 0 |  -  |
    | - | + |  0  |
    | 0 | - |  -  |
    | 0 | 0 |  0  |
    | 0 | + |  +  |
    | + | - |  0  |
    | + | 0 |  +  |
    | + | + |  -  |
    """
    return Component(
            ('a', 'b'),
            ('out',),
            {
                'NAny': NANY,
                'NXor': nxor_gate,
                'Not': NOT,
                'PNot': PNOT,
                'NXorOut': nxor_gate,
                },
            {
                'out': 'NXorOut.out',
                'NXorOut.a': 'Not.out',
                'NXorOut.b': 'PNot.out',
                'Not.in': 'NAny.out',
                'PNot.in': 'NXor.out',
                'NAny.a': 'a',
                'NAny.b': 'b',
                'NXor.a': 'a',
                'NXor.b': 'b',
                })


def half_adder():
    """The half adder performs basic single trit addition.

    It takes two inputs 'a' and 'b', and produces two outputs 'sum' and
    'carry'.

    The 'sum' output is the value of 'a' when 'b' is zero, the value of 'b'
    when 'a' is zero, if both inputs are the same, then the negation of that
    value, otherwise zero.

    The 'carry' output is zero, except when both inputs are the same, then it
    takes the value of the inputs.

    | a | b |  sum  | carry |
    |===|===|=======|=======|
    | - | - |   +   |   -   |
    | - | 0 |   -   |   0   |
    | - | + |   0   |   0   |
    | 0 | - |   -   |   0   |
    | 0 | 0 |   0   |   0   |
    | 0 | + |   +   |   0   |
    | + | - |   0   |   0   |
    | + | 0 |   +   |   0   |
    | + | + |   -   |   +   |
    """
    return Component(
            ('a', 'b'),
            ('sum', 'carry'),
            {
                'Sum': sum_gate,
                'NCons': NCONS,
                'Not': NOT,
                },
            {
                'sum': 'Sum.out',
                'carry': 'Not.out',
                'Sum.a': 'a',
                'Sum.b': 'b',
                'Not.in': 'NCons.out',
                'NCons.a': 'a',
                'NCons.b': 'b',
                })
