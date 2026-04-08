#!/usr/bin/env python
import argparse
import io
import sys
from traceback import print_exc

from ternary import binary
from ternary.hardware.computer import Computer
from ternary.hardware.util import int_to_trits, trits_to_int, input_stream


MIN_ADDR = -(3 ** 11 // 2)


class Simulator:
    def __init__(self):
        self.sources = []
        self.computer = Computer()
        self.program_length = 0

    def load_binary(self, stream) -> None:
        """Load a program encoded in binary format."""
        program = str(binary.decode(stream.read()))
        length = len(program)
        if length % 12 != 0:
            raise ValueError(
                    "Invalid length for binary-encoded program: "
                    f"expected a multiple of 12 but got {length}")
        self.computer.load_program(program)
        self.program_length = length // 12

    def load_text(self, stream: io.TextIOBase) -> None:
        """Load a program encoded in text format."""
        codes = []
        for line in stream:
            line = line.strip()
            if not line:
                continue
            self.sources.append(line)
            code = line[:12]
            if any(c not in '-0+' for c in code):
                raise ValueError(
                        f"Invalid characters in '{line}': expected only "
                        "-, 0 and + in the first 12 characters of each line")
            codes.append(code)
        program = ''.join(codes)
        self.computer.load_program(program)
        self.program_length = len(codes)

    def load(self, stream) -> None:
        """Load a program encoded in either text or binary format.

        This method will try to auto-detect which format the stream is in, and
        call load_text() or load_binary() as appropriate.
        """
        if isinstance(stream, io.TextIOBase):
            self.load_text(stream)
        else:
            self.load_binary(stream)

    def execute(self):
        """Run the loaded program.

        The simulator will continue to cycle the computer until it tries to
        access a program address beyond the end of the program, at which point
        we will terminate.
        """
        exit_address = MIN_ADDR + self.program_length
        self.computer.reset()
        pc = trits_to_int(self.computer.get_program_address())
        while pc < exit_address:
            self.computer.step()
            pc = trits_to_int(self.computer.get_program_address())

    def get_ram_contents(self, index: int) -> int:
        addr = int_to_trits(index, 11)
        value = self.computer.get_ram_contents(addr)
        return trits_to_int(value)


def main(
        input_path: str = '-',
        select: list[int] | None = None):
    sim = Simulator()
    with input_stream(input_path) as stream:
        sim.load(stream)

    sim.execute()
    if select:
        for index in select:
            value = sim.get_ram_contents(index)
            print(value)

    return True


def cli():
    parser = argparse.ArgumentParser()
    parser.add_argument('input_path', nargs='?', default='-')
    parser.add_argument(
            '-s', '--select', type=int, action='append')

    args = parser.parse_args()
    success = False
    try:
        success = main(**vars(args))
    except Exception:
        print_exc()
        sys.exit(1)
    sys.exit(0 if success else 1)


if __name__ == '__main__':
    cli()
