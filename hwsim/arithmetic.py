from hwsim.component import Component, and_gate, any_gate, NCONS, NOT


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


def full_adder():
    """The full adder performs addition over three input trits.

    It takes three inputs 'a', 'b' and 'c', and produces two outputs 'sum' and
    'carry'.
    """
    return Component(
            ('a', 'b', 'c'),
            ('sum', 'carry'),
            {
                'AddAB': half_adder,
                'AddABC': half_adder,
                'Any': any_gate,
                },
            {
                'sum': 'AddABC.sum',
                'carry': 'Any.out',
                'AddABC.a': 'AddAB.sum',
                'AddABC.b': 'c',
                'AddAB.a': 'a',
                'AddAB.b': 'b',
                'Any.a': 'AddAB.carry',
                'Any.b': 'AddABC.carry',
                })


# 12-trit versions of some of the logical gates.


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
            ('out[12]'),
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
