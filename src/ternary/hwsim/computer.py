from collections.abc import Iterable

from ternary.hwsim.component import Component, Trits
from ternary.hwsim.cpu import CPU
from ternary.hwsim.memory import RAM177KMock, ROM177KMock
from ternary.trit import ZERO, POS


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

    def reset(self) -> None:
        """Signal a reset and advance to the next clock cycle."""
        self.set_inputs(POS)
        self.tick()

    def step(self) -> None:
        """Execute one normal clock cycle."""
        self.set_inputs(ZERO)
        self.tick()

    def load_program(self, data: Iterable[Trits]) -> None:
        """Write data to the program ROM."""
        self.components['ROM'].load(data)

    def set_ram_contents(self, address: Trits, value: Trits) -> None:
        return self.components['RAM'].set_contents(address, value)

    def get_ram_contents(self, address: Trits) -> Trits:
        return self.components['RAM'].get_contents(address)

    def get_a(self) -> Trits:
        return self.components['CPU'].get_a()

    def get_d(self) -> Trits:
        return self.components['CPU'].get_d()

    def get_program_address(self) -> Trits:
        return self.components['CPU'].get_pc()
