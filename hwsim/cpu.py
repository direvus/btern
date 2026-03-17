from hwsim.component import ZERO, Component
from hwsim.logic import And12, Not12, Mux12
from hwsim.arithmetic import Add12, Inc12, Dec12


class ALU(Component):
    """A 12-trit Arithmetic Logic Unit (ALU)

    The logic unit takes two 12-trit input buses, named 'x' and 'y', and
    performs various functions on the inputs, based on the single-trit control
    signals 'px', 'py' and 'f'. 'px' and 'py' select a transformation to apply
    to the 'x' or 'y' input, and 'f' specifies a function that combines the two
    inputs to produce the result.

    When 'px' or 'py' is negative, the input is logically inverted. When 'px'
    or 'py' is positive, the input is replaced with all zeroes. When 'px' or
    'py' is zero, the input is passed through without any transformation.

    When 'f' is negative, the output is the logical AND of the two inputs. When
    'f' is positive, the output is the arithmetic sum of the two inputs. When
    'f' is zero, the 'y' input is ignored, and the value of the 'py' signal is
    instead used to select the function: if 'py' is negative, the output is x -
    1, and if it is positive, the output is x + 1.

    The behaviour when 'f' and 'py' are both zero is reserved for future
    expansion.

    | p | transform         |    | f | function   |
    |===|===================|    |===|============|
    | - | invert            |    | - | x & y      |
    | 0 | none              |    | 0 | x++ or x-- |
    | + | replace with zero |    | + | x + y      |

    | px  | py  | f |   out   |  equiv. |
    |=====|=====|===|=========|=========|
    |  -  |  -  | - | -x & -y | x NOR y |
    |  -  |  -  | 0 | -x - 1  |         |
    |  -  |  -  | + | -x + -y | -x - y  |
    |  -  |  0  | - | -x & y  |         |
    |  -  |  0  | 0 |         |         |
    |  -  |  0  | + | -x + y  | y - x   |
    |  -  |  +  | - | -x & 0  |         |
    |  -  |  +  | 0 | -x + 1  |         |
    |  -  |  +  | + | -x + 0  | -x      |
    |  0  |  -  | - | x & -y  |         |
    |  0  |  -  | 0 | x - 1   |         |
    |  0  |  -  | + | x + -y  | x - y   |
    |  0  |  0  | - | x & y   |         |
    |  0  |  0  | 0 |         |         |
    |  0  |  0  | + | x + y   |         |
    |  0  |  +  | - | x & 0   |         |
    |  0  |  +  | 0 | x + 1   |         |
    |  0  |  +  | + | x + 0   | x       |
    |  +  |  -  | - | 0 & -y  |         |
    |  +  |  -  | 0 | 0 - 1   | -1      |
    |  +  |  -  | + | 0 + -y  | -y      |
    |  +  |  0  | - | 0 & y   |         |
    |  +  |  0  | 0 |         |         |
    |  +  |  0  | + | 0 + y   | y       |
    |  +  |  +  | - | 0 & 0   | 0       |
    |  +  |  +  | 0 | 0 + 1   | 1       |
    |  +  |  +  | + | 0 + 0   | 0       |
    """
    def __init__(self):
        super().__init__(
                ('x[12]', 'y[12]', 'px', 'py', 'f'),
                ('out[12]',),
                {
                    'PreX': Mux12,
                    'PreY': Mux12,
                    'NotX': Not12,
                    'NotY': Not12,
                    'UnaryX': Mux12,
                    'MuxOut': Mux12,
                    'Add': Add12,
                    'Inc': Inc12,
                    'Dec': Dec12,
                    'And': And12,
                    },
                {
                    'out': 'MuxOut.out',
                    'MuxOut.a': 'And.out',
                    'MuxOut.b': 'UnaryX.out',
                    'MuxOut.c': 'Add.out',
                    'MuxOut.s': 'f',
                    'UnaryX.a': 'Dec.out',
                    'UnaryX.b': ZERO,
                    'UnaryX.c': 'Inc.out',
                    'UnaryX.s': 'py',
                    'Add.a': 'PreX.out',
                    'Add.b': 'PreY.out',
                    'And.a': 'PreX.out',
                    'And.b': 'PreY.out',
                    'Inc.in': 'PreX.out',
                    'Dec.in': 'PreX.out',
                    'PreX.a': 'NotX.out',
                    'PreX.b': 'x',
                    'PreX.c': ZERO,
                    'PreX.s': 'px',
                    'PreY.a': 'NotY.out',
                    'PreY.b': 'y',
                    'PreY.c': ZERO,
                    'PreY.s': 'py',
                    'NotX.in': 'x',
                    'NotY.in': 'y',
                })
