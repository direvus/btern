from hwsim.component import Component, Trits, NOT
from hwsim.logic import Mux
from trit import ZERO


class DataFlipFlop(Component):
    """The data flip flop has a single trit internal state value.

    It takes two inputs, 'in' and 'load', and has one output 'out'. The output
    always produces the current internal state of the flip flop.

    When the flip flop receives a clock pulse, it updates its internal value
    according to the 'in' and 'load' signals. When 'load' is zero, the internal
    value is retained and the value of 'in' is disregarded. When 'load' is
    non-zero, the internal state is set to the value of 'in'.

    The update() method returns True when the load signal is non-zero,
    regardless of whether the actual state value has changed.
    """
    state = ZERO

    def __init__(self):
        super().__init__(('load', 'in'), ('out',))

    def update(self) -> bool:
        load = self.cache['load']
        if load == ZERO:
            return False

        self.state = self.cache['in']
        return True

    def get_outputs(self, inputs: Trits | None = None) -> Trits:
        if inputs is not None:
            self.set_inputs(inputs)
        return (self.state,)


class Register(Component):
    """A single-trit data register.

    The Register is a persisent memory cell for a single trit value. It takes
    two inputs, 'load' and 'in', and has one output 'out'.

    When the Register receives a clock pulse, it updates its internal memory
    according to the 'load' and 'in' signals. When 'load' is zero, the internal
    state is retained and the value of 'in' is disregarded. When 'load' is
    negative, the internal state is inverted and the value of 'in' is
    disregarded. When 'load' is positive, the internal state is replaced with
    the value of 'in'.
    """
    def __init__(self):
        super().__init__(
                ('load', 'in'),
                ('out',),
                {
                    'DFF': DataFlipFlop,
                    'Mux': Mux,
                    'Not': NOT,
                    },
                {
                    'out': 'DFF.out',
                    'DFF.load': 'load',
                    'DFF.in': 'Mux.out',
                    'Mux.a': 'Not.out',
                    'Mux.b': 'DFF.out',
                    'Mux.c': 'in',
                    'Mux.s': 'load',
                    'Not.in': 'DFF.out',
                    })
        self.prepare_cache()

    def prepare_cache(self):
        # Seed the cache for the feedbacks from the DFF's output to the Mux, or
        # else we will go into an infinite recursion trying to resolve the
        # inputs for the DFF.
        (value,) = self.components['DFF'].get_outputs()
        self.cache['Not.in'] = value
        self.cache['Mux.b'] = value

    def update_subcomponents(self):
        changed = super().update_subcomponents()
        if changed:
            self.prepare_cache()
        return changed


class RAM3(Component):
    """A 3 register RAM module.

    The module takes a 12-trit input bus named 'in', a single 'address' signal
    and a single trit 'load' signal.

    The address signal selects which of the three registers is to be read from
    and written to.
    """
