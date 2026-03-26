from collections.abc import Iterable

from hwsim.component import Component, Trits
from hwsim.cpu import CPU
from hwsim.memory import RAM177KMock, ROM177KMock
from trit import ZERO, POS


class Computer(Component):
    """The Computer links together a CPU with a RAM module and a program ROM.

    It takes a single input signal 'reset', and has no outputs.

    The CPU receives its instruction to execute from the currently addressed
    register in the program ROM. It also receives the contents of the currently
    addressed register in RAM as its 'inM' input.

    The 'addrM' output from the CPU selects the active register in RAM, while
    'outM' and 'loadM' give the result of the ALU instruction, and whether it
    should be committed to RAM, respectively.

    The 'addrP' output from CPU selects the address in ROM of the next
    instruction to execute.

    The 'reset' signal is passed through directly to the CPU. When it is set to
    a non-zero value, the CPU will clear its registers and set 'addrP' to point
    at the first register of the program ROM.

    The normal way to operate the Computer is to load the ROM with a program,
    then set the 'reset' signal, tick the clock, and then leave the reset
    signal at zero and continue to tick the clock while the computer runs the
    program.
    """
    def __init__(self):
        super().__init__(
                ('reset',),
                tuple(),
                {
                    'CPU': CPU,
                    'RAM': RAM177KMock,
                    'ROM': ROM177KMock,
                    },
                {
                    'CPU.inM': 'RAM.out',
                    'CPU.inst': 'ROM.out',
                    'CPU.reset': 'reset',
                    'RAM.addr': 'CPU.addrM',
                    'RAM.in': 'CPU.outM',
                    'RAM.load': 'CPU.loadM',
                    'ROM.addr': 'CPU.addrP',
                    })

    def get_outputs(self, inputs: Trits | None = None) -> Trits:
        """Process the connections in the Computer.

        Technically we don't have any outputs from this component, but this is
        the method that is usually responsible for triggering a recursive
        evaluation of subcomponents. So we do that here, in spite of the lack
        of any real outputs.
        """
        self.set_inputs(inputs)
        for name in self.components:
            self.evaluate_subcomponent(name)
        return tuple()

    def reset(self) -> None:
        """Reset the computer and advance to the next clock cycle."""
        self.cache['RAM.out'] = ZERO * 12
        self.cache['ROM.out'] = ZERO * 12
        self.get_outputs(POS)
        self.tick()

    def step(self) -> None:
        """Execute one normal clock cycle."""
        self.get_outputs(ZERO)
        self.tick()

    def load_program(self, data: Iterable[Trits]) -> None:
        """Write data to the program ROM."""
        self.components['ROM'].load(data)

    def get_ram_contents(self, address: Trits) -> Trits:
        return self.components['RAM'].get_contents(address)

    def get_a(self) -> Trits:
        return self.components['CPU'].get_a()

    def get_d(self) -> Trits:
        return self.components['CPU'].get_d()

    def get_program_address(self) -> Trits:
        return self.components['CPU'].get_pc()
