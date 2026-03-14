from hwsim.component import Component, Trits
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

    def get_outputs(self, inputs: Trits) -> Trits:
        self.set_inputs(inputs)
        return (self.state,)
