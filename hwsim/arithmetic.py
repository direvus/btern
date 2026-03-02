from hwsim.component import Component, any_gate, NCONS, NOT


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
                'Any1': any_gate,
                'Any2': any_gate,
                'Any3': any_gate,
                'NCons': NCONS,
                },
            {
                'out': 'Any3.out',
                'Any3.a': 'NCons.out',
                'Any3.b': 'Any2.out',
                'Any2.a': 'NCons.out',
                'Any2.b': 'Any1.out',
                'Any1.a': 'a',
                'Any1.b': 'b',
                'NCons.a': 'a',
                'NCons.b': 'b',
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
