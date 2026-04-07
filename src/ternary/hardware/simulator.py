#!/usr/bin/env python
import argparse
import sys
from traceback import print_exc

from ternary.hardware.computer import Computer
from ternary.hardware.util import trits_to_int, input_stream


MIN_ADDR = -(3 ** 11 // 2)


class Simulator:
    def __init__(self):
        self.sources = []
        self.computer = Computer()
        self.program_length = 0

    def load(self, stream):
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
        self.computer.load_program(codes)
        self.program_length = len(codes)

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
            a = trits_to_int(self.computer.get_a())
            d = trits_to_int(self.computer.get_d())
            pc = trits_to_int(self.computer.get_program_address())

            print(f"{a} {d} {pc}")


def main(input_path: str = '-', watch: list[str] | None = None):
    sim = Simulator()
    with input_stream(input_path) as stream:
        sim.load(stream)

    sim.execute()
    return True


def cli():
    parser = argparse.ArgumentParser()
    parser.add_argument('input_path', nargs='?', default='-')
    parser.add_argument('-w', '--watch', nargs='*', action='append')

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
