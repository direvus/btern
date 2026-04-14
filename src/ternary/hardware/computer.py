from ternary.hardware.component import Component, Trits
from ternary.hardware.cpu import CPU
from ternary.hardware.memory import RAM177KMock, ROM177KMock
from ternary.trit import ZERO, POS


class Computer(Component):
    """The Computer connects a CPU with a RAM module and a program ROM.

    It takes a single input signal 'reset', and has no outputs.

    The CPU receives its instruction to execute from the currently addressed
    register in the program ROM. It also receives the contents of the currently
    addressed register in RAM as its 'inM' input.

    The 'addrM', 'outM' and 'loadM' outputs from the CPU are passed to the RAM
    module, and they control which register in RAM is active, what value to
    provide it, and what loading behaviour to apply.

    The 'addrP' output from CPU selects the address in ROM of the next
    instruction to execute.

    The 'reset' signal is passed through directly to the CPU. When it is set to
    a non-zero value, the CPU will clear its internal registers and set 'addrP'
    to point at the first register of the program ROM.

    The typical way to operate the Computer is to load the ROM with a program,
    then set the 'reset' signal, tick the clock, and then leave the reset
    signal at zero and continue to tick the clock while the computer runs the
    program.

    The Computer expects to receive trit sequences in arithmetic order (most
    significant to least) and outputs trit sequences in arithmetic order, but
    internally within the hardware simulation, the order is reversed so that
    the least significant trit has index zero.
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

    def load_program(self, data: Trits) -> None:
        """Write data to the program ROM."""
        self.components['ROM'].load(data)

    def set_ram_contents(self, address: Trits, value: Trits) -> None:
        addr = address[::-1]
        value = value[::-1]
        return self.components['RAM'].set_contents(addr, value)

    def get_ram_contents(self, address: Trits) -> Trits:
        addr = address[::-1]
        return self.components['RAM'].get_contents(addr)[::-1]

    def get_a(self) -> Trits:
        return self.components['CPU'].get_a()[::-1]

    def get_d(self) -> Trits:
        return self.components['CPU'].get_d()[::-1]

    def get_program_address(self) -> Trits:
        return self.components['CPU'].get_pc()[::-1]
