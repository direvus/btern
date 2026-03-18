from hwsim.component import ZERO, NEG, NANY, NOT, Component
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


class Jumper(Component):
    """The Jumper calculates the address of the next instruction to execute.

    It takes as inputs the address of the current instruction, a possible jump
    target address, the result of running the Comparator against the test
    value, and two control signals j1 and j2.

    The output will be calculated according to the control signals as follows:

    | j1 | j2 | name | out                           |
    |====|====|======|===============================|
    | -  | -  | JLT  | Jump if test is <0            |
    | -  | 0  | JEZ  | Jump if test is =0            |
    | -  | +  | JGT  | Jump if test is >0            |
    | 0  | -  | RST  | Jump to start unconditionally |
    | 0  | 0  | NOJ  | Do not jump                   |
    | 0  | +  | JMP  | Jump unconditionally          |
    | +  | -  | JLE  | Jump if test is <=0           |
    | +  | 0  | JNZ  | Jump if test is !=0           |
    | +  | +  | JGE  | Jump if test is >=0           |

    If the logic indicates no jump (a jump criterion is not met, or the control
    code is 00 NOJ) the output is the current instruction address + 1.
    """
    def __init__(self):
        # Note: lazily using 3-way multiplexers for the 'A' and 'C' branch,
        # even though there are only two possible outcomes on those branches --
        # the jump target, or current+1. As a future optimisation, we may be
        # able to swap these out for 2-way multiplexers. Each 3-way mux has 78
        # primitives, whereas I think a 2-way mux could be 51. So it's a pretty
        # significant difference, though granted we only need one Jumper chip
        # in the entire computer.
        super().__init__(
                ('current[12]', 'target[12]', 'cmp', 'j1', 'j2'),
                ('out[12]',),
                {
                    'Inc': Inc12,
                    'MuxA': Mux12,
                    'MuxB': Mux12,
                    'MuxC': Mux12,
                    'MuxOut': Mux12,
                    'NAnyA': NANY,
                    'NAnyC': NANY,
                    'NotJ2': NOT,
                    },
                {
                    'out': 'MuxOut.out',
                    'MuxOut.a': 'MuxA.out',
                    'MuxOut.b': 'MuxB.out',
                    'MuxOut.c': 'MuxC.out',
                    'MuxOut.s': 'j1',
                    'MuxA.a': 'Inc.out',
                    'MuxA.b': 'target',
                    'MuxA.c': 'Inc.out',
                    'MuxA.s': 'NAnyA.out',
                    'MuxB.a': NEG,
                    'MuxB.b': 'Inc.out',
                    'MuxB.c': 'target',
                    'MuxB.s': 'j2',
                    'MuxC.a': 'target',
                    'MuxC.b': 'Inc.out',
                    'MuxC.c': 'target',
                    'MuxC.s': 'NAnyC.out',
                    'NAnyA.a': 'NotJ2.out',
                    'NAnyA.b': 'cmp',
                    'NAnyC.a': 'j2',
                    'NAnyC.b': 'cmp',
                    'NotJ2.in': 'j2',
                    'Inc.in': 'current',
                    })
