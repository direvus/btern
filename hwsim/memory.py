from collections.abc import Iterable

from hwsim.component import Component, Trit, Trits
from hwsim.logic import Mux, Mux12, Demux, Mux9Way12, Demux9Way
from hwsim.util import trits_to_int
from trit import NEG, ZERO, POS


class DataFlipFlop(Component):
    """The data flip flop has a single trit internal state value.

    It takes two inputs, 'in' and 'load', and has one output 'out'. The output
    produces the current internal state of the flip flop, without any inputs
    required.

    When the flip flop receives a clock pulse, it updates its internal value
    according to the 'in' and 'load' signals. When 'load' is zero, the internal
    value is retained and the value of 'in' is disregarded. When 'load' is
    non-zero, the internal state is set to the value of 'in'.

    The update() method returns True when the load signal is non-zero,
    regardless of whether the actual state value has changed.
    """
    state: Trit = ZERO

    def __init__(self):
        super().__init__(('in', 'load'), ('out',))

    def update(self) -> bool:
        load = self.get_value('load')
        if load == ZERO:
            return False

        self.state = self.get_value('in')
        return True

    def get_value(self, name: str) -> Trit:
        if name == 'out':
            return self.state
        return super().get_value(name)

    def get_contents(self) -> Trit:
        return self.state


class Register(Component):
    """A single-trit data register.

    The Register is a persisent memory cell for a single trit value. It takes
    two inputs, 'in' and 'load', and has one output 'out'.

    When the Register receives a clock pulse, it updates its internal memory
    according to the 'load' and 'in' signals. When 'load' is zero, the internal
    state is retained and the value of 'in' is disregarded. When 'load' is
    negative, the internal state is reset to zero and the value of 'in' is
    disregarded. When 'load' is positive, the internal state is replaced with
    the value of 'in'.

    The Register is clocked so that changes to the internal state will not be
    visible in the output until the next clock cycle.

    The output value after the next clock tick is determined as follows:

    | current   | - | 0 | + |
    | in | load |   |   |   |
    |====|======|===|===|===|
    | -  |  -   | 0 | 0 | 0 |
    | -  |  0   | - | 0 | + |
    | -  |  +   | - | - | - |
    | 0  |  -   | 0 | 0 | 0 |
    | 0  |  0   | - | 0 | + |
    | 0  |  +   | 0 | 0 | 0 |
    | +  |  -   | 0 | 0 | 0 |
    | +  |  0   | - | 0 | + |
    | +  |  +   | + | + | + |

    """
    def __init__(self):
        super().__init__(
                ('in', 'load'),
                ('out',),
                {
                    'DFF': DataFlipFlop,
                    'Mux': Mux,
                    },
                {
                    'out': 'DFF.out',
                    'DFF.load': 'load',
                    'DFF.in': 'Mux.out',
                    'Mux.a': ZERO,
                    'Mux.b': 'DFF.out',
                    'Mux.c': 'in',
                    'Mux.s': 'load',
                    })

    def get_contents(self) -> Trit:
        return self.components['DFF'].get_contents()


class Register12(Component):
    """A 12-trit data register.

    This is a series of persisent memory cells for 12 trit values. It takes a
    12-trit input bus 'in', and a single-trit 'load' signal. It has one 12-trit
    output bus 'out'.

    When the register receives a clock pulse, it updates its internal memory
    according to the 'load' and 'in' signals. When 'load' is zero, the internal
    state is retained and the value of 'in' is disregarded. When 'load' is
    negative, the internal state is reset to zero and the value of 'in' is
    disregarded. When 'load' is positive, the internal state is replaced with
    the value of 'in'.
    """
    deferred = True

    def __init__(self):
        super().__init__(
                ('in[12]', 'load'),
                ('out[12]',),
                {
                    'T0': Register,
                    'T1': Register,
                    'T2': Register,
                    'T3': Register,
                    'T4': Register,
                    'T5': Register,
                    'T6': Register,
                    'T7': Register,
                    'T8': Register,
                    'T9': Register,
                    'T10': Register,
                    'T11': Register,
                    },
                {
                    'out[0]': 'T0.out',
                    'out[1]': 'T1.out',
                    'out[2]': 'T2.out',
                    'out[3]': 'T3.out',
                    'out[4]': 'T4.out',
                    'out[5]': 'T5.out',
                    'out[6]': 'T6.out',
                    'out[7]': 'T7.out',
                    'out[8]': 'T8.out',
                    'out[9]': 'T9.out',
                    'out[10]': 'T10.out',
                    'out[11]': 'T11.out',
                    'T0.in': 'in[0]',
                    'T1.in': 'in[1]',
                    'T2.in': 'in[2]',
                    'T3.in': 'in[3]',
                    'T4.in': 'in[4]',
                    'T5.in': 'in[5]',
                    'T6.in': 'in[6]',
                    'T7.in': 'in[7]',
                    'T8.in': 'in[8]',
                    'T9.in': 'in[9]',
                    'T10.in': 'in[10]',
                    'T11.in': 'in[11]',
                    'T0.load': 'load',
                    'T1.load': 'load',
                    'T2.load': 'load',
                    'T3.load': 'load',
                    'T4.load': 'load',
                    'T5.load': 'load',
                    'T6.load': 'load',
                    'T7.load': 'load',
                    'T8.load': 'load',
                    'T9.load': 'load',
                    'T10.load': 'load',
                    'T11.load': 'load',
                    })

    def get_contents(self) -> Trits:
        return ''.join(
                self.components[f'T{i}'].get_contents()
                for i in range(12))


class RAM3(Component):
    """A 3 register RAM module.

    The module takes a 12-trit input bus named 'in', a single trit 'load'
    signal and a single trit 'addr' signal.

    The 'addr' signal selects which of the three registers is active:

    | addr | active register |
    |======|=================|
    |  -   | first           |
    |  0   | second          |
    |  +   | third           |

    The 12-trit ouput bus always contains the current value of the active
    register. Changes to register contents will take effect on the next time
    tick.
    """
    def __init__(self):
        super().__init__(
                ('in[12]', 'load', 'addr'),
                ('out[12]',),
                {
                    'Demux': Demux,
                    'R1': Register12,
                    'R2': Register12,
                    'R3': Register12,
                    'Mux': Mux12,
                    },
                {
                    'out': 'Mux.out',
                    'Mux.a': 'R1.out',
                    'Mux.b': 'R2.out',
                    'Mux.c': 'R3.out',
                    'Mux.s': 'addr',
                    'R1.in': 'in',
                    'R1.load': 'Demux.a',
                    'R2.in': 'in',
                    'R2.load': 'Demux.b',
                    'R3.in': 'in',
                    'R3.load': 'Demux.c',
                    'Demux.in': 'load',
                    'Demux.s': 'addr',
                    })


class RAM9(Component):
    """A 9 register RAM module.

    The module takes a 12-trit input data bus named 'in', a single trit 'load'
    signal, and a 2-trit 'addr' bus.

    The 'addr' bus selects which of the nine registers to activate:

    | s[1] | s[0] | register |
    |======|======|==========|
    |   -  |   -  |     0    |
    |   -  |   0  |     1    |
    |   -  |   +  |     2    |
    |   0  |   -  |     3    |
    |   0  |   0  |     4    |
    |   0  |   +  |     5    |
    |   +  |   -  |     6    |
    |   +  |   0  |     7    |
    |   +  |   +  |     8    |

    The contents of the 'in' data bus are sent to all registers, but only the
    active register will receive the 'load' signal.

    The 12-trit ouput bus always contains the current value of the active
    register. Changes to register contents will take effect on the next time
    tick.
    """
    def __init__(self):
        super().__init__(
                ('in[12]', 'load', 'addr[2]'),
                ('out[12]',),
                {
                    'Demux': Demux9Way,
                    'R0': Register12,
                    'R1': Register12,
                    'R2': Register12,
                    'R3': Register12,
                    'R4': Register12,
                    'R5': Register12,
                    'R6': Register12,
                    'R7': Register12,
                    'R8': Register12,
                    'Mux': Mux9Way12,
                    },
                {
                    'out': 'Mux.out',
                    'Mux.a': 'R0.out',
                    'Mux.b': 'R1.out',
                    'Mux.c': 'R2.out',
                    'Mux.d': 'R3.out',
                    'Mux.e': 'R4.out',
                    'Mux.f': 'R5.out',
                    'Mux.g': 'R6.out',
                    'Mux.h': 'R7.out',
                    'Mux.i': 'R8.out',
                    'Mux.s': 'addr',
                    'R0.in': 'in',
                    'R0.load': 'Demux.a',
                    'R1.in': 'in',
                    'R1.load': 'Demux.b',
                    'R2.in': 'in',
                    'R2.load': 'Demux.c',
                    'R3.in': 'in',
                    'R3.load': 'Demux.d',
                    'R4.in': 'in',
                    'R4.load': 'Demux.e',
                    'R5.in': 'in',
                    'R5.load': 'Demux.f',
                    'R6.in': 'in',
                    'R6.load': 'Demux.g',
                    'R7.in': 'in',
                    'R7.load': 'Demux.h',
                    'R8.in': 'in',
                    'R8.load': 'Demux.i',
                    'Demux.in': 'load',
                    'Demux.s': 'addr',
                    })


class RAM81(Component):
    """An 81 register RAM module.

    The module takes a 12-trit input data bus named 'in', a single trit 'load'
    signal and a 4-trit 'addr' bus.

    It consists of nine RAM9 submodules.

    The upper two trits of the address bus select which of the nine submodules
    to activate, and the lower two trits of the address are passed down to the
    submodules, to select the active register within that submodule.

    The contents of the 'in' data bus are sent to all registers, but only the
    active register will receive the 'load' signal.

    The 12-trit ouput bus always contains the current value of the active
    register. Changes to register contents will take effect on the next time
    tick.
    """
    def __init__(self):
        super().__init__(
                ('in[12]', 'load', 'addr[4]'),
                ('out[12]',),
                {
                    'Demux': Demux9Way,
                    'R0': RAM9,
                    'R1': RAM9,
                    'R2': RAM9,
                    'R3': RAM9,
                    'R4': RAM9,
                    'R5': RAM9,
                    'R6': RAM9,
                    'R7': RAM9,
                    'R8': RAM9,
                    'Mux': Mux9Way12,
                    },
                {
                    'out': 'Mux.out',
                    'Mux.a': 'R0.out',
                    'Mux.b': 'R1.out',
                    'Mux.c': 'R2.out',
                    'Mux.d': 'R3.out',
                    'Mux.e': 'R4.out',
                    'Mux.f': 'R5.out',
                    'Mux.g': 'R6.out',
                    'Mux.h': 'R7.out',
                    'Mux.i': 'R8.out',
                    'Mux.s': 'addr[2..3]',
                    'R0.in': 'in',
                    'R0.load': 'Demux.a',
                    'R0.addr': 'addr[0..1]',
                    'R1.in': 'in',
                    'R1.load': 'Demux.b',
                    'R1.addr': 'addr[0..1]',
                    'R2.in': 'in',
                    'R2.load': 'Demux.c',
                    'R2.addr': 'addr[0..1]',
                    'R3.in': 'in',
                    'R3.load': 'Demux.d',
                    'R3.addr': 'addr[0..1]',
                    'R4.in': 'in',
                    'R4.load': 'Demux.e',
                    'R4.addr': 'addr[0..1]',
                    'R5.in': 'in',
                    'R5.load': 'Demux.f',
                    'R5.addr': 'addr[0..1]',
                    'R6.in': 'in',
                    'R6.load': 'Demux.g',
                    'R6.addr': 'addr[0..1]',
                    'R7.in': 'in',
                    'R7.load': 'Demux.h',
                    'R7.addr': 'addr[0..1]',
                    'R8.in': 'in',
                    'R8.load': 'Demux.i',
                    'R8.addr': 'addr[0..1]',
                    'Demux.in': 'load',
                    'Demux.s': 'addr[2..3]',
                    })


class RAM729(Component):
    """A 729 register RAM module.

    The module takes a 12-trit input data bus named 'in', a single trit 'load'
    signal and a 6-trit 'addr' bus.

    It consists of nine RAM81 submodules.

    The upper two trits of the address bus select which of the nine submodules
    to activate, and the lower four trits of the address are passed down to the
    submodules, to select the active register within that submodule.

    The contents of the 'in' data bus are sent to all registers, but only the
    active register will receive the 'load' signal.

    The 12-trit ouput bus always contains the current value of the active
    register. Changes to register contents will take effect on the next time
    tick.
    """
    def __init__(self):
        super().__init__(
                ('in[12]', 'load', 'addr[6]'),
                ('out[12]',),
                {
                    'Demux': Demux9Way,
                    'R0': RAM81,
                    'R1': RAM81,
                    'R2': RAM81,
                    'R3': RAM81,
                    'R4': RAM81,
                    'R5': RAM81,
                    'R6': RAM81,
                    'R7': RAM81,
                    'R8': RAM81,
                    'Mux': Mux9Way12,
                    },
                {
                    'out': 'Mux.out',
                    'Mux.a': 'R0.out',
                    'Mux.b': 'R1.out',
                    'Mux.c': 'R2.out',
                    'Mux.d': 'R3.out',
                    'Mux.e': 'R4.out',
                    'Mux.f': 'R5.out',
                    'Mux.g': 'R6.out',
                    'Mux.h': 'R7.out',
                    'Mux.i': 'R8.out',
                    'Mux.s': 'addr[4..5]',
                    'R0.in': 'in',
                    'R0.load': 'Demux.a',
                    'R0.addr': 'addr[0..3]',
                    'R1.in': 'in',
                    'R1.load': 'Demux.b',
                    'R1.addr': 'addr[0..3]',
                    'R2.in': 'in',
                    'R2.load': 'Demux.c',
                    'R2.addr': 'addr[0..3]',
                    'R3.in': 'in',
                    'R3.load': 'Demux.d',
                    'R3.addr': 'addr[0..3]',
                    'R4.in': 'in',
                    'R4.load': 'Demux.e',
                    'R4.addr': 'addr[0..3]',
                    'R5.in': 'in',
                    'R5.load': 'Demux.f',
                    'R5.addr': 'addr[0..3]',
                    'R6.in': 'in',
                    'R6.load': 'Demux.g',
                    'R6.addr': 'addr[0..3]',
                    'R7.in': 'in',
                    'R7.load': 'Demux.h',
                    'R7.addr': 'addr[0..3]',
                    'R8.in': 'in',
                    'R8.load': 'Demux.i',
                    'R8.addr': 'addr[0..3]',
                    'Demux.in': 'load',
                    'Demux.s': 'addr[4..5]',
                    })


class RAM6K(Component):
    """A 6,561 register RAM module.

    The module takes a 12-trit input data bus named 'in', a single trit 'load'
    signal and an 8-trit 'addr' bus.

    It consists of nine RAM729 submodules.

    The upper two trits of the address bus select which of the nine submodules
    to activate, and the lower six trits of the address are passed down to the
    submodules, to select the active register within that submodule.

    The contents of the 'in' data bus are sent to all registers, but only the
    active register will receive the 'load' signal.

    The 12-trit ouput bus always contains the current value of the active
    register. Changes to register contents will take effect on the next time
    tick.
    """
    def __init__(self):
        super().__init__(
                ('in[12]', 'load', 'addr[8]'),
                ('out[12]',),
                {
                    'Demux': Demux9Way,
                    'R0': RAM729,
                    'R1': RAM729,
                    'R2': RAM729,
                    'R3': RAM729,
                    'R4': RAM729,
                    'R5': RAM729,
                    'R6': RAM729,
                    'R7': RAM729,
                    'R8': RAM729,
                    'Mux': Mux9Way12,
                    },
                {
                    'out': 'Mux.out',
                    'Mux.a': 'R0.out',
                    'Mux.b': 'R1.out',
                    'Mux.c': 'R2.out',
                    'Mux.d': 'R3.out',
                    'Mux.e': 'R4.out',
                    'Mux.f': 'R5.out',
                    'Mux.g': 'R6.out',
                    'Mux.h': 'R7.out',
                    'Mux.i': 'R8.out',
                    'Mux.s': 'addr[6..7]',
                    'R0.in': 'in',
                    'R0.load': 'Demux.a',
                    'R0.addr': 'addr[0..5]',
                    'R1.in': 'in',
                    'R1.load': 'Demux.b',
                    'R1.addr': 'addr[0..5]',
                    'R2.in': 'in',
                    'R2.load': 'Demux.c',
                    'R2.addr': 'addr[0..5]',
                    'R3.in': 'in',
                    'R3.load': 'Demux.d',
                    'R3.addr': 'addr[0..5]',
                    'R4.in': 'in',
                    'R4.load': 'Demux.e',
                    'R4.addr': 'addr[0..5]',
                    'R5.in': 'in',
                    'R5.load': 'Demux.f',
                    'R5.addr': 'addr[0..5]',
                    'R6.in': 'in',
                    'R6.load': 'Demux.g',
                    'R6.addr': 'addr[0..5]',
                    'R7.in': 'in',
                    'R7.load': 'Demux.h',
                    'R7.addr': 'addr[0..5]',
                    'R8.in': 'in',
                    'R8.load': 'Demux.i',
                    'R8.addr': 'addr[0..5]',
                    'Demux.in': 'load',
                    'Demux.s': 'addr[6..7]',
                    })


class RAM59K(Component):
    """A 59,049 register RAM module.

    The module takes a 12-trit input data bus named 'in', a single trit 'load'
    signal and a 10-trit 'addr' bus.

    It consists of nine RAM6K submodules.

    The upper two trits of the address bus select which of the nine submodules
    to activate, and the lower eight trits of the address are passed down to
    the submodules, to select the active register within that submodule.

    The contents of the 'in' data bus are sent to all registers, but only the
    active register will receive the 'load' signal.

    The 12-trit ouput bus always contains the current value of the active
    register. Changes to register contents will take effect on the next time
    tick.
    """
    def __init__(self):
        super().__init__(
                ('in[12]', 'load', 'addr[10]'),
                ('out[12]',),
                {
                    'Demux': Demux9Way,
                    'R0': RAM6K,
                    'R1': RAM6K,
                    'R2': RAM6K,
                    'R3': RAM6K,
                    'R4': RAM6K,
                    'R5': RAM6K,
                    'R6': RAM6K,
                    'R7': RAM6K,
                    'R8': RAM6K,
                    'Mux': Mux9Way12,
                    },
                {
                    'out': 'Mux.out',
                    'Mux.a': 'R0.out',
                    'Mux.b': 'R1.out',
                    'Mux.c': 'R2.out',
                    'Mux.d': 'R3.out',
                    'Mux.e': 'R4.out',
                    'Mux.f': 'R5.out',
                    'Mux.g': 'R6.out',
                    'Mux.h': 'R7.out',
                    'Mux.i': 'R8.out',
                    'Mux.s': 'addr[8..9]',
                    'R0.in': 'in',
                    'R0.load': 'Demux.a',
                    'R0.addr': 'addr[0..7]',
                    'R1.in': 'in',
                    'R1.load': 'Demux.b',
                    'R1.addr': 'addr[0..7]',
                    'R2.in': 'in',
                    'R2.load': 'Demux.c',
                    'R2.addr': 'addr[0..7]',
                    'R3.in': 'in',
                    'R3.load': 'Demux.d',
                    'R3.addr': 'addr[0..7]',
                    'R4.in': 'in',
                    'R4.load': 'Demux.e',
                    'R4.addr': 'addr[0..7]',
                    'R5.in': 'in',
                    'R5.load': 'Demux.f',
                    'R5.addr': 'addr[0..7]',
                    'R6.in': 'in',
                    'R6.load': 'Demux.g',
                    'R6.addr': 'addr[0..7]',
                    'R7.in': 'in',
                    'R7.load': 'Demux.h',
                    'R7.addr': 'addr[0..7]',
                    'R8.in': 'in',
                    'R8.load': 'Demux.i',
                    'R8.addr': 'addr[0..7]',
                    'Demux.in': 'load',
                    'Demux.s': 'addr[8..9]',
                    })


class RAM177K(Component):
    """A 177,147 register RAM module.

    The module takes a 12-trit input data bus named 'in', a single trit 'load'
    signal and an 11-trit 'addr' bus.

    It consists of three RAM59K submodules.

    The high trit of the address bus selects which of the three submodules
    to activate, and the lower ten trits of the address are passed down to
    the submodules, to select the active register within that submodule.

    The contents of the 'in' data bus are sent to all registers, but only the
    active register will receive the 'load' signal.

    The 12-trit ouput bus always contains the current value of the active
    register. Changes to register contents will take effect on the next time
    tick.
    """
    def __init__(self):
        super().__init__(
                ('in[12]', 'load', 'addr[11]'),
                ('out[12]',),
                {
                    'Demux': Demux,
                    'R0': RAM59K,
                    'R1': RAM59K,
                    'R2': RAM59K,
                    'Mux': Mux12,
                    },
                {
                    'out': 'Mux.out',
                    'Mux.a': 'R0.out',
                    'Mux.b': 'R1.out',
                    'Mux.c': 'R2.out',
                    'Mux.s': 'addr[10]',
                    'R0.in': 'in',
                    'R0.load': 'Demux.a',
                    'R0.addr': 'addr[0..9]',
                    'R1.in': 'in',
                    'R1.load': 'Demux.b',
                    'R1.addr': 'addr[0..9]',
                    'R2.in': 'in',
                    'R2.load': 'Demux.c',
                    'R2.addr': 'addr[0..9]',
                    'Demux.in': 'load',
                    'Demux.s': 'addr[10]',
                    })


class RAM177KMock(Component):
    """A mocked 177,147 register RAM module.

    The module takes a 12-trit input data bus named 'in', a single trit 'load'
    signal and an 11-trit 'addr' bus.

    The 12-trit ouput bus always contains the current value of the active
    register. Changes to register contents will take effect on the next time
    tick.

    This class imitates the overall behaviour of a memory module, without
    instantiating all of the subcomponents and tracking all of the connection
    state between that many registers, because that is not very practical.
    """
    def __init__(self):
        super().__init__(
                ('in[12]', 'load', 'addr[11]'),
                ('out[12]',))
        self.registers = {}
        self.addr = ''
        self.default_value = tuple(ZERO * 12)

    def get_address(self) -> Trits:
        return ''.join(self.get_value(f'addr[{i}]') for i in range(11))

    def update(self) -> bool:
        load = self.get_value('load')
        addr = self.get_address()
        if load == ZERO and self.addr == addr:
            return False

        self.addr = addr
        if load == NEG:
            self.registers[addr] = self.default_value
        else:
            value = tuple(self.cache[f'in[{i}]'] for i in range(12))
            self.registers[addr] = value
        return True

    def get_value(self, name: str) -> Trit:
        if name in self.outputs:
            index = self.outputs.index(name)
            addr = self.get_address()
            contents = self.registers.get(addr, self.default_value)
            return contents[index]
        return super().get_value(name)

    def get_outputs(self, inputs: Trits | None = None) -> Trits:
        if inputs is not None:
            self.set_inputs(inputs)
        addr = self.get_address()
        return self.registers.get(addr, self.default_value)

    def set_contents(self, addr: Trits, value: Trits) -> None:
        addr = ''.join(addr)
        self.registers[addr] = value

    def get_contents(self, addr: Trits) -> Trits:
        addr = ''.join(addr)
        return self.registers.get(addr, self.default_value)


class ROM177KMock(Component):
    """A mocked 177,147 register read-only memory module.

    The module takes an 11-trit input address bus 'addr', and has a 12-trit
    output bus 'out'.

    The 12-trit ouput bus always contains the current value of the addressed
    register.

    This class imitates the overall behaviour of a ROM module, but without
    simulating all of the subcomponents and connections between them, because
    that is not very practical for unit testing.
    """
    deferred = True
    index = 0

    def __init__(self):
        super().__init__(
                ('addr[11]',),
                ('out[12]',))
        self.index = 0
        self.registers = []
        self.min_address = trits_to_int(NEG * 11)
        self.default_value = tuple(ZERO * 12)

    def get_outputs(self, inputs: Trits | None = None) -> Trits:
        if inputs is not None:
            self.set_inputs(inputs)
        return self.registers[self.index]

    def update(self) -> bool:
        addr = tuple(self.cache.get(f'addr[{i}]', '0') for i in range(11))
        index = trits_to_int(addr) - self.min_address
        if index != self.index and index >= 0 and index < len(self.registers):
            self.index = index
            return True
        return False

    def get_value(self, name: str) -> Trit:
        if name in self.outputs:
            index = self.outputs.index(name)
            return self.registers[self.index][index]
        return super().get_value(name)

    def load(self, values: Iterable[Trits]):
        """Write data to the ROM.

        Starting from the lowest possible register address in the ROM
        (-----------), the values will be written sequentially into the ROM.

        Each member of the `values` argument should be exactly 12 trits long.
        If a value is longer than 12 trits, it will be truncated, and shorter
        values will be padded on the right with zeroes.
        """
        self.registers = []
        for value in values:
            length = len(value)
            if length > 12:
                value = value[:12]
            elif length < 12:
                pad = tuple(ZERO) * (length - 12)
                value = tuple(value) + pad
            self.registers.append(tuple(value))


class ProgramCounter11(Component):
    """An 11-trit program counter register.

    This is effectively a register that is always in 'write' mode. It takes an
    11-trit input bus 'in', and has an 11-trit output bus 'out'.

    The output bus always yields the current value of the register. When the
    register receives a clock pulse, it updates its internal memory to match
    the 'in' bus, and the new value will be available to read on the output bus
    on the following clock cycle.
    """
    deferred = True

    def __init__(self):
        super().__init__(
                ('in[11]',),
                ('out[11]',),
                {
                    'T0': Register,
                    'T1': Register,
                    'T2': Register,
                    'T3': Register,
                    'T4': Register,
                    'T5': Register,
                    'T6': Register,
                    'T7': Register,
                    'T8': Register,
                    'T9': Register,
                    'T10': Register,
                    },
                {
                    'out[0]': 'T0.out',
                    'out[1]': 'T1.out',
                    'out[2]': 'T2.out',
                    'out[3]': 'T3.out',
                    'out[4]': 'T4.out',
                    'out[5]': 'T5.out',
                    'out[6]': 'T6.out',
                    'out[7]': 'T7.out',
                    'out[8]': 'T8.out',
                    'out[9]': 'T9.out',
                    'out[10]': 'T10.out',
                    'T0.in': 'in[0]',
                    'T1.in': 'in[1]',
                    'T2.in': 'in[2]',
                    'T3.in': 'in[3]',
                    'T4.in': 'in[4]',
                    'T5.in': 'in[5]',
                    'T6.in': 'in[6]',
                    'T7.in': 'in[7]',
                    'T8.in': 'in[8]',
                    'T9.in': 'in[9]',
                    'T10.in': 'in[10]',
                    'T0.load': POS,
                    'T1.load': POS,
                    'T2.load': POS,
                    'T3.load': POS,
                    'T4.load': POS,
                    'T5.load': POS,
                    'T6.load': POS,
                    'T7.load': POS,
                    'T8.load': POS,
                    'T9.load': POS,
                    'T10.load': POS,
                    'T11.load': POS,
                    })

    def get_contents(self) -> Trits:
        return ''.join(
                self.components[f'T{i}'].get_contents()
                for i in range(11))
