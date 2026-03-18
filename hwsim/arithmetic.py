from hwsim.component import (
        Component, NCONS, NAND, NOR, NANY, NOT, PNOT, NNOT)
from hwsim.logic import Any


class Sum(Component):
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
    def __init__(self):
        super().__init__(
                ('a', 'b'),
                ('out',),
                {
                    'Any1': Any,
                    'Any2': Any,
                    'Any3': Any,
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


class HalfAdd(Component):
    """The half add gate performs basic single trit addition.

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
    def __init__(self):
        super().__init__(
                ('a', 'b'),
                ('sum', 'carry'),
                {
                    'Sum': Sum,
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


class FullAdd(Component):
    """The full add gate performs addition over three input trits.

    It takes three inputs 'a', 'b' and 'c', and produces two outputs 'sum' and
    'carry'.
    """
    def __init__(self):
        super().__init__(
                ('a', 'b', 'c'),
                ('sum', 'carry'),
                {
                    'AddAB': HalfAdd,
                    'AddABC': HalfAdd,
                    'Any': Any,
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


class Inc(Component):
    """A single-trit incrementer.

    It takes one input 'in', and produces two outputs 'sum' and 'carry'.

    The 'sum' output is equal to the value of 'in' plus one, with a positive
    input wrapping around to a negative output.

    The 'carry' output is positive when the input is positive, and otherwise it
    is zero.

    | in  | sum | carry |
    |=====|=====|=======|
    |  -  |  0  |   0   |
    |  0  |  +  |   0   |
    |  +  |  -  |   +   |
    """
    def __init__(self):
        super().__init__(
                ('in',),
                ('sum', 'carry'),
                {
                    'Not': NOT,
                    'PNot': PNOT,
                    'NNot': NNOT,
                    'NAnd': NAND,
                    'NOr': NOR,
                    'NCons': NCONS,
                    'NAny': NANY,
                    },
                {
                    'sum': 'NAny.out',
                    'carry': 'NCons.out',
                    'NAny.a': 'NNot.out',
                    'NAny.b': 'NAnd.out',
                    'NNot.in': 'Not.out',
                    'Not.in': 'in',
                    'PNot.in': 'in',
                    'NAnd.a': 'PNot.out',
                    'NAnd.b': 'in',
                    'NCons.a': 'Not.out',
                    'NCons.b': 'NOr.out',
                    'NOr.a': 'in',
                    'NOr.b': 'PNot.out',
                    })


class Dec(Component):
    """A single-trit decrementer.

    It takes one input 'in', and produces two outputs 'sum' and 'carry'.

    The 'sum' output is equal to the value of 'in' minus one, with a negative
    input wrapping around to a positive output.

    The 'carry' output is negative when the input is negative, and otherwise it
    is zero.

    | in  | sum | carry |
    |=====|=====|=======|
    |  -  |  +  |   -   |
    |  0  |  -  |   0   |
    |  +  |  0  |   0   |
    """
    def __init__(self):
        super().__init__(
                ('in',),
                ('sum', 'carry'),
                {
                    'Not': NOT,
                    'PNot': PNOT,
                    'NNot': NNOT,
                    'NAnd': NAND,
                    'NOr': NOR,
                    'NAnySum': NANY,
                    'NAnyCar': NANY,
                    },
                {
                    'sum': 'NAnySum.out',
                    'carry': 'NAnyCar.out',
                    'NAnySum.a': 'NOr.out',
                    'NAnySum.b': 'PNot.out',
                    'NAnyCar.a': 'NAnd.out',
                    'NAnyCar.b': 'Not.out',
                    'NOr.a': 'in',
                    'NOr.b': 'NNot.out',
                    'NNot.in': 'in',
                    'Not.in': 'in',
                    'PNot.in': 'Not.out',
                    'NAnd.a': 'Not.out',
                    'NAnd.b': 'in',
                    })


class Inc12(Component):
    """A 12-trit incrementer.

    It takes a 12-trit input bus 'in', and produces a 12-trit output bus 'out'.

    The output is equal to the input plus one. Overflow wraps around to the
    lowest negative value.

    For example:

    |       in      |       out     |
    |===============|===============|
    | ------ ------ | ------ -----0 |
    | 000000 000000 | 000000 00000+ |
    | ++++++ ++++++ | ------ ------ |
    | 000000 000+++ | 000000 00+--- |
    """
    def __init__(self):
        super().__init__(
                ('in[12]',),
                ('out[12]',),
                {
                    'Inc': Inc,
                    'Add1': HalfAdd,
                    'Add2': HalfAdd,
                    'Add3': HalfAdd,
                    'Add4': HalfAdd,
                    'Add5': HalfAdd,
                    'Add6': HalfAdd,
                    'Add7': HalfAdd,
                    'Add8': HalfAdd,
                    'Add9': HalfAdd,
                    'Add10': HalfAdd,
                    'Add11': Sum,
                    },
                {
                    'out[0]': 'Inc.sum',
                    'Inc.in': 'in[0]',
                    'out[1]': 'Add1.sum',
                    'Add1.a': 'Inc.carry',
                    'Add1.b': 'in[1]',
                    'out[2]': 'Add2.sum',
                    'Add2.a': 'Add1.carry',
                    'Add2.b': 'in[2]',
                    'out[3]': 'Add3.sum',
                    'Add3.a': 'Add2.carry',
                    'Add3.b': 'in[3]',
                    'out[4]': 'Add4.sum',
                    'Add4.a': 'Add3.carry',
                    'Add4.b': 'in[4]',
                    'out[5]': 'Add5.sum',
                    'Add5.a': 'Add4.carry',
                    'Add5.b': 'in[5]',
                    'out[6]': 'Add6.sum',
                    'Add6.a': 'Add5.carry',
                    'Add6.b': 'in[6]',
                    'out[7]': 'Add7.sum',
                    'Add7.a': 'Add6.carry',
                    'Add7.b': 'in[7]',
                    'out[8]': 'Add8.sum',
                    'Add8.a': 'Add7.carry',
                    'Add8.b': 'in[8]',
                    'out[9]': 'Add9.sum',
                    'Add9.a': 'Add8.carry',
                    'Add9.b': 'in[9]',
                    'out[10]': 'Add10.sum',
                    'Add10.a': 'Add9.carry',
                    'Add10.b': 'in[10]',
                    'out[11]': 'Add11.out',
                    'Add11.a': 'Add10.carry',
                    'Add11.b': 'in[11]',
                    })


class Dec12(Component):
    """A 12-trit decrementer.

    It takes a 12-trit input bus 'in', and produces a 12-trit output bus 'out'.

    The output is equal to the input minus one. Overflow wraps around to the
    highest positive value.

    For example:

    |       in      |       out     |
    |===============|===============|
    | ++++++ ++++++ | ++++++ +++++0 |
    | 000000 000000 | 000000 00000- |
    | ------ ------ | ++++++ ++++++ |
    | 000000 000+++ | 000000 000++0 |
    """
    def __init__(self):
        super().__init__(
                ('in[12]',),
                ('out[12]',),
                {
                    'Dec': Dec,
                    'Add1': HalfAdd,
                    'Add2': HalfAdd,
                    'Add3': HalfAdd,
                    'Add4': HalfAdd,
                    'Add5': HalfAdd,
                    'Add6': HalfAdd,
                    'Add7': HalfAdd,
                    'Add8': HalfAdd,
                    'Add9': HalfAdd,
                    'Add10': HalfAdd,
                    'Add11': Sum,
                    },
                {
                    'out[0]': 'Dec.sum',
                    'Dec.in': 'in[0]',
                    'out[1]': 'Add1.sum',
                    'Add1.a': 'in[1]',
                    'Add1.b': 'Dec.carry',
                    'out[2]': 'Add2.sum',
                    'Add2.a': 'in[2]',
                    'Add2.b': 'Add1.carry',
                    'out[3]': 'Add3.sum',
                    'Add3.a': 'in[3]',
                    'Add3.b': 'Add2.carry',
                    'out[4]': 'Add4.sum',
                    'Add4.a': 'in[4]',
                    'Add4.b': 'Add3.carry',
                    'out[5]': 'Add5.sum',
                    'Add5.a': 'in[5]',
                    'Add5.b': 'Add4.carry',
                    'out[6]': 'Add6.sum',
                    'Add6.a': 'in[6]',
                    'Add6.b': 'Add5.carry',
                    'out[7]': 'Add7.sum',
                    'Add7.a': 'in[7]',
                    'Add7.b': 'Add6.carry',
                    'out[8]': 'Add8.sum',
                    'Add8.a': 'in[8]',
                    'Add8.b': 'Add7.carry',
                    'out[9]': 'Add9.sum',
                    'Add9.a': 'in[9]',
                    'Add9.b': 'Add8.carry',
                    'out[10]': 'Add10.sum',
                    'Add10.a': 'in[10]',
                    'Add10.b': 'Add9.carry',
                    'out[11]': 'Add11.out',
                    'Add11.a': 'in[11]',
                    'Add11.b': 'Add10.carry',
                    })


class Add12(Component):
    """A 12-trit addition chip.

    It takes two 12-trit input buses 'a' and 'b', and produces the sum of those
    two inputs on a 12-trit output bus 'out'.

    For example:

    |       a       |       b       |       out     |
    |===============|===============|===============|
    | 000000 00000- | 000000 00000+ | 000000 000000 |
    | 000000 00000+ | 000000 00000+ | 000000 0000+- |
    | ++++++ ++++++ | ------ ------ | 000000 000000 |
    """
    def __init__(self):
        super().__init__(
                ('a[12]', 'b[12]'),
                ('out[12]',),
                {
                    'Add0': HalfAdd,
                    'Add1': FullAdd,
                    'Add2': FullAdd,
                    'Add3': FullAdd,
                    'Add4': FullAdd,
                    'Add5': FullAdd,
                    'Add6': FullAdd,
                    'Add7': FullAdd,
                    'Add8': FullAdd,
                    'Add9': FullAdd,
                    'Add10': FullAdd,
                    'Add11': FullAdd,
                    },
                {
                    'out[0]': 'Add0.sum',
                    'Add0.a': 'a[0]',
                    'Add0.b': 'b[0]',
                    'out[1]': 'Add1.sum',
                    'Add1.a': 'a[1]',
                    'Add1.b': 'b[1]',
                    'Add1.c': 'Add0.carry',
                    'out[2]': 'Add2.sum',
                    'Add2.a': 'a[2]',
                    'Add2.b': 'b[2]',
                    'Add2.c': 'Add1.carry',
                    'out[3]': 'Add3.sum',
                    'Add3.a': 'a[3]',
                    'Add3.b': 'b[3]',
                    'Add3.c': 'Add2.carry',
                    'out[4]': 'Add4.sum',
                    'Add4.a': 'a[4]',
                    'Add4.b': 'b[4]',
                    'Add4.c': 'Add3.carry',
                    'out[5]': 'Add5.sum',
                    'Add5.a': 'a[5]',
                    'Add5.b': 'b[5]',
                    'Add5.c': 'Add4.carry',
                    'out[6]': 'Add6.sum',
                    'Add6.a': 'a[6]',
                    'Add6.b': 'b[6]',
                    'Add6.c': 'Add5.carry',
                    'out[7]': 'Add7.sum',
                    'Add7.a': 'a[7]',
                    'Add7.b': 'b[7]',
                    'Add7.c': 'Add6.carry',
                    'out[8]': 'Add8.sum',
                    'Add8.a': 'a[8]',
                    'Add8.b': 'b[8]',
                    'Add8.c': 'Add7.carry',
                    'out[9]': 'Add9.sum',
                    'Add9.a': 'a[9]',
                    'Add9.b': 'b[9]',
                    'Add9.c': 'Add8.carry',
                    'out[10]': 'Add10.sum',
                    'Add10.a': 'a[10]',
                    'Add10.b': 'b[10]',
                    'Add10.c': 'Add9.carry',
                    'out[11]': 'Add11.sum',
                    'Add11.a': 'a[11]',
                    'Add11.b': 'b[11]',
                    'Add11.c': 'Add10.carry',
                    })


class Comparator(Component):
    """The Comparator signals whether a number is negative, zero or positive.

    It takes 2 input trits, 'a' and 'b', and produces a single trit output
    'out'.

    Treating the inputs together as representing a 2-trit ternary number, with
    'a' being the most significant, output negative if the number is negative
    overall, positive if the number is positive overall, and zero if the number
    is exactly zero.
    """
    def __init__(self):
        super().__init__(
                ('a', 'b'),
                ('out',),
                {
                    'NAnyOut': NANY,
                    'NAny': NANY,
                    'NCons': NCONS,
                    'NotB': NOT,
                    },
                {
                    'out': 'NAnyOut.out',
                    'NAnyOut.a': 'NAny.out',
                    'NAnyOut.b': 'NCons.out',
                    'NAny.a': 'a',
                    'NAny.b': 'b',
                    'NCons.a': 'a',
                    'NCons.b': 'NotB.out',
                    'NotB.in': 'b',
                    })


class Comparator12(Component):
    """The Comparator signals whether a number is negative, zero or positive.

    It takes a 12-trit input bus 'in', and outputs a single trit signal
    indicating whether the input represents a negative, zero or positive
    number.

    A number is only zero when all of its trits are zero. It is negative
    overall when the most significant trit is negative, and positive overall
    when the most significant trit is positive.
    """
    def __init__(self):
        super().__init__(
                ('in[12]',),
                ('out',),
                {
                    'Cmp0': Comparator,
                    'Cmp1': Comparator,
                    'Cmp2': Comparator,
                    'Cmp3': Comparator,
                    'Cmp4': Comparator,
                    'Cmp5': Comparator,
                    'Cmp6': Comparator,
                    'Cmp7': Comparator,
                    'Cmp8': Comparator,
                    'Cmp9': Comparator,
                    'Cmp10': Comparator,
                    },
                {
                    'out': 'Cmp0.out',
                    'Cmp0.a': 'Cmp1.out',
                    'Cmp0.b': 'in[0]',
                    'Cmp1.a': 'Cmp2.out',
                    'Cmp1.b': 'in[1]',
                    'Cmp2.a': 'Cmp3.out',
                    'Cmp2.b': 'in[2]',
                    'Cmp3.a': 'Cmp4.out',
                    'Cmp3.b': 'in[3]',
                    'Cmp4.a': 'Cmp5.out',
                    'Cmp4.b': 'in[4]',
                    'Cmp5.a': 'Cmp6.out',
                    'Cmp5.b': 'in[5]',
                    'Cmp6.a': 'Cmp7.out',
                    'Cmp6.b': 'in[6]',
                    'Cmp7.a': 'Cmp8.out',
                    'Cmp7.b': 'in[7]',
                    'Cmp8.a': 'Cmp9.out',
                    'Cmp8.b': 'in[8]',
                    'Cmp9.a': 'Cmp10.out',
                    'Cmp9.b': 'in[9]',
                    'Cmp10.a': 'in[11]',
                    'Cmp10.b': 'in[10]',
                    })
