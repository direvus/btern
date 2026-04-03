from hwsim.component import (
        ZERO, NEG, NAnd, NAny, NCons, NOr, Not, PNot, Component, Trits)
from hwsim.arithmetic import Add12, Inc12, Dec12, Comparator12
from hwsim.logic import (
        And12, IsZero, Not12, Mux2Way, Mux12, Mux2Way12,
        ShiftLeft12, ShiftRight12)
from hwsim.memory import Register12, ProgramCounter11


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
    instead used to select the function to apply to 'x': if 'py' is negative,
    the output is x - 1, and if it is positive, the output is x + 1.

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

    It takes as inputs the address of the current instruction, a candidate jump
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
        super().__init__(
                ('current[11]', 'target[11]', 'cmp', 'j1', 'j2'),
                ('out[11]',),
                {
                    'Inc': Inc12,
                    'MuxA': Mux2Way12,
                    'MuxB': Mux12,
                    'MuxC': Mux2Way12,
                    'MuxOut': Mux12,
                    'NAnyA': NAny,
                    'NAnyC': NAny,
                    'NotJ2': Not,
                    },
                {
                    'out': 'MuxOut.out[0..10]',
                    'MuxOut.a': 'MuxA.out',
                    'MuxOut.b': 'MuxB.out',
                    'MuxOut.c': 'MuxC.out',
                    'MuxOut.s': 'j1',
                    'MuxA.a[0..10]': 'target',
                    'MuxA.a[11]': ZERO,
                    'MuxA.b': 'Inc.out',
                    'MuxA.s': 'NAnyA.out',
                    'MuxB.a': NEG,
                    'MuxB.b': 'Inc.out',
                    'MuxB.c[0..10]': 'target',
                    'MuxB.c[11]': ZERO,
                    'MuxB.s': 'j2',
                    'MuxC.a': 'Inc.out',
                    'MuxC.b[0..10]': 'target',
                    'MuxC.b[11]': ZERO,
                    'MuxC.s': 'NAnyC.out',
                    'NAnyA.a': 'NotJ2.out',
                    'NAnyA.b': 'cmp',
                    'NAnyC.a': 'j2',
                    'NAnyC.b': 'cmp',
                    'NotJ2.in': 'j2',
                    'Inc.in[0..10]': 'current',
                    'Inc.in[11]': ZERO,
                    })


class Loader(Component):
    """The Loader calculates how data should be loaded into memory.

    Its inputs are single-trit signals 'reset', 'mode' and 'target', and it has
    three outputs 'a', 'm' and 'd'.

    The 'a' output gives the loading signal for the A register, the 'd' output
    gives the loading signal for the D register, and the 'm' output gives the
    loading signal for the active register in RAM.

    When the 'reset' signal is non-zero, the outputs are always '-', '0', '-'
    irrespective of the other inputs.


    |       | target |  -  |  0  |  +  |
    | reset |  mode  |     |     |     |
    |=======|========|=====|=====|=====|
    |   -   |    -   | -0- | -0- | -0- |
    |   -   |    0   | -0- | -0- | -0- |
    |   -   |    +   | -0- | -0- | -0- |
    |   0   |    -   | +00 | +00 | +00 |
    |   0   |    0   | +00 | 0+0 | 00+ |
    |   0   |    +   | 00+ | 00+ | 00+ |
    |   +   |    -   | -0- | -0- | -0- |
    |   +   |    0   | -0- | -0- | -0- |
    |   +   |    +   | -0- | -0- | -0- |
    """
    def __init__(self):
        super().__init__(
                ('reset', 'mode', 'target'),
                ('a', 'm', 'd'),
                {
                    'NOrA': NOr,
                    'NAndA': NAnd,
                    'NotA': Not,
                    'NConsA': NCons,
                    'NAnyM1': NAny,
                    'NAnyM2': NAny,
                    'NConsM': NCons,
                    'NConsD': NCons,
                    'NAndD': NAnd,
                    'NAnyD': NAny,
                    'MuxA': Mux2Way,
                    'MuxM': Mux2Way,
                    'MuxD': Mux2Way,
                    'PNotMode': PNot,
                    'PNotTarget': PNot,
                    },
                {
                    'a': 'MuxA.out',
                    'm': 'MuxM.out',
                    'd': 'MuxD.out',

                    'MuxA.a': 'NConsA.out',
                    'MuxA.b': NEG,
                    'MuxA.s': 'reset',

                    'MuxM.a': 'NConsM.out',
                    'MuxM.b': ZERO,
                    'MuxM.s': 'reset',

                    'MuxD.a': 'NAndD.out',
                    'MuxD.b': NEG,
                    'MuxD.s': 'reset',

                    'NConsA.a': 'NOrA.out',
                    'NConsA.b': 'NotA.out',
                    'NotA.in': 'NAndA.out',
                    'NOrA.a': 'PNotMode.out',
                    'NOrA.b': 'target',
                    'NAndA.a': 'mode',
                    'NAndA.b': 'target',

                    'NConsM.a': 'NAnyM1.out',
                    'NConsM.b': 'NAnyM2.out',
                    'NAnyM1.a': 'PNotMode.out',
                    'NAnyM1.b': 'target',
                    'NAnyM2.a': 'mode',
                    'NAnyM2.b': 'PNotTarget.out',

                    'NAndD.a': 'NConsD.out',
                    'NAndD.b': 'NAnyD.out',
                    'NConsD.a': 'mode',
                    'NConsD.b': 'PNotTarget.out',
                    'NAnyD.a': 'mode',
                    'NAnyD.b': 'target',

                    'PNotMode.in': 'mode',
                    'PNotTarget.in': 'target',
                    })


class JumpController(Component):
    """The Jump Controller modifies the jump control signals if needed.

    It takes as inputs the two jump control signals 'j1' and 'j2', and the
    'mode' and 'reset' signals.

    When the 'mode' signal in a CPU instruction is non-zero, the jump1 and
    jump2 signals are not controls at all, they are literal trit values to be
    loaded into a register, so we need to override them both to zero to ensure
    no jump occurs.

    When the 'reset' signal to the CPU is non-zero, irrespective of the
    CPU instruction, we need to override the jump signals to force a jump to
    the start of the program address space, so jump1 needs to be zero and jump2
    needs to be negative.

    When both 'mode' and 'signal' are both zero, then the jump signals are
    passed through to the outputs as-is.
    """
    def __init__(self):
        super().__init__(
                ('j1', 'j2', 'mode', 'reset'),
                ('out1', 'out2'),
                {
                    'NotMode': Not,
                    'NotReset': Not,
                    'Not2': Not,
                    'IsResetZero': IsZero,
                    'NCons1R': NCons,
                    'NCons1M': NCons,
                    'NCons2M': NCons,
                    'NAny1RA': NAny,
                    'NAny1RB': NAny,
                    'NAny1MA': NAny,
                    'NAny1MB': NAny,
                    'NAny2MA': NAny,
                    'NAny2MB': NAny,
                    'NAnd2R': NAnd,
                    },
                {
                    'out1': 'NCons1R.out',
                    'NCons1R.a': 'NAny1RA.out',
                    'NCons1R.b': 'NAny1RB.out',
                    'NAny1RA.a': 'NotReset.out',
                    'NAny1RA.b': 'NCons1M.out',
                    'NAny1RB.a': 'reset',
                    'NAny1RB.b': 'NCons1M.out',

                    'NCons1M.a': 'NAny1MA.out',
                    'NCons1M.b': 'NAny1MB.out',
                    'NAny1MA.a': 'NotMode.out',
                    'NAny1MA.b': 'j1',
                    'NAny1MB.a': 'mode',
                    'NAny1MB.b': 'j1',

                    'out2': 'Not2.out',
                    'Not2.in': 'NAnd2R.out',
                    'NAnd2R.a': 'IsResetZero.out',
                    'NAnd2R.b': 'NCons2M.out',

                    'NCons2M.a': 'NAny2MA.out',
                    'NCons2M.b': 'NAny2MB.out',
                    'NAny2MA.a': 'NotMode.out',
                    'NAny2MA.b': 'j2',
                    'NAny2MB.a': 'mode',
                    'NAny2MB.b': 'j2',

                    'NotMode.in': 'mode',
                    'NotReset.in': 'reset',
                    'IsResetZero.in': 'reset',
                    })


class CPU(Component):
    """The CPU executes machine language instructions.

    Its inputs are:

    - inM -- a 12-trit bus holding the current value addressed in RAM
    - inst -- a 12-trit bus holding the machine language instruction to execute
    - reset -- a single trit signal

    Its outputs are:

    - addrM -- an 11-trit address in RAM
    - outM -- the 12-trit value to present to RAM
    - loadM -- a single-trit signal indicating how the addressed RAM register
      should behave
    - addrP -- an 11-trit address in program ROM of the next instruction to
      execute.

    When the reset signal is non-zero, it overrides the instruction and instead
    forces the CPU to unconditionally jump to the start of the program ROM.

    The meaning of each trit in the machine language instruction is as follows:

    | index | meaning                         |
    |-------|---------------------------------|
    |   0   | Jump control 1                  |
    |   1   | Jump control 2                  |
    |   2   | Reserved                        |
    |   3   | Reserved                        |
    |   4   | Shift (right/none/left)         |
    |   5   | ALU function select (&/-1/+1/+) |
    |   6   | X-input transform (-X/X/0)      |
    |   7   | Y-input transform (-Y/Y/0)      |
    |   8   | X-input select (A/M/D)          |
    |   9   | Y-input select (A/M/D)          |
    |  10   | Computation target (A/M/D)      |
    |  11   | Instruction mode (load/compute) |
    """
    def __init__(self):
        super().__init__(
                ('inM[12]', 'inst[12]', 'reset'),
                ('addrM[11]', 'outM[12]', 'loadM', 'addrP[11]'),
                {
                    'ALU': ALU,
                    'Loader': Loader,
                    'Jumper': Jumper,
                    'JumpCtl': JumpController,
                    'Cmp': Comparator12,
                    'A': Register12,
                    'D': Register12,
                    'ProgramCounter': ProgramCounter11,
                    'X': Mux12,
                    'Y': Mux12,
                    'RegIn': Mux2Way12,
                    'ShiftL': ShiftLeft12,
                    'ShiftR': ShiftRight12,
                    'Result': Mux12,
                    },
                {
                    'loadM': 'Loader.m',
                    'Loader.reset': 'reset',
                    'Loader.mode': 'inst[11]',
                    'Loader.target': 'inst[10]',

                    'addrP': 'Jumper.out',
                    'Jumper.j1': 'JumpCtl.out1',
                    'Jumper.j2': 'JumpCtl.out2',
                    'Jumper.cmp': 'Cmp.out',
                    'Jumper.target': 'A.out[0..10]',
                    'Jumper.current': 'ProgramCounter.out',

                    'A.load': 'Loader.a',
                    'D.load': 'Loader.d',
                    'A.in': 'RegIn.out',
                    'D.in': 'RegIn.out',

                    'ALU.f': 'inst[5]',
                    'ALU.px': 'inst[6]',
                    'ALU.py': 'inst[7]',
                    'ALU.x': 'X.out',
                    'ALU.y': 'Y.out',

                    'X.a': 'A.out',
                    'X.b': 'inM',
                    'X.c': 'D.out',
                    'X.s': 'inst[8]',

                    'Y.a': 'A.out',
                    'Y.b': 'inM',
                    'Y.c': 'D.out',
                    'Y.s': 'inst[9]',

                    'RegIn.a': 'Result.out',
                    'RegIn.b[0..10]': 'inst[0..10]',
                    'RegIn.b[11]': ZERO,
                    'RegIn.s': 'inst[11]',

                    'ShiftL.in': 'ALU.out',
                    'ShiftR.in': 'ALU.out',

                    'Result.a': 'ShiftR.out',
                    'Result.b': 'ALU.out',
                    'Result.c': 'ShiftL.out',
                    'Result.s': 'inst[4]',

                    'Cmp.in': 'Result.out',
                    'outM': 'Result.out',

                    'addrM': 'A.out[0..10]',

                    'JumpCtl.j1': 'inst[0]',
                    'JumpCtl.j2': 'inst[1]',
                    'JumpCtl.mode': 'inst[11]',
                    'JumpCtl.reset': 'reset',

                    'ProgramCounter.in': 'Jumper.out',
                    })

    def reset(self) -> None:
        """Reset the CPU.

        Set the 'reset' input to a non-zero value, and then send a clock tick.
        """
        self.get_outputs('000000000000000000000000+')
        self.tick()

    def get_a(self) -> Trits:
        """Get the current contents of the A register."""
        return self.components['A'].get_contents()

    def get_d(self) -> Trits:
        """Get the current contents of the D register."""
        return self.components['D'].get_contents()

    def get_pc(self) -> Trits:
        """Get the current contents of the Program Counter."""
        return self.components['ProgramCounter'].get_contents()
