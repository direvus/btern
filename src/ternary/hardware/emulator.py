#!/usr/bin/env python
"""emulator.py -- Emulate the ternary computer in software

This script runs ternary machine code programs, by emulating the behaviour of
the computer design entirely in software, as opposed to simulator.py which
simulates all of the electronic connections between logic gates.

The simulator is useful for validating the hardware designs, but it is too
resource intensive to be practical for running and testing higher-level
programs. That's where the emulator comes in.
"""
import argparse
import io
import sys
import time
from traceback import print_exc

from ternary import binary
from ternary.hardware.util import (
        int_to_trits, trits_to_int, input_stream, MIN_ADDR, MIN_INT,
        INT_RANGE, Trit)


def do_and(a: int, b: int) -> int:
    ta = int_to_trits(a, 12)
    tb = int_to_trits(b, 12)

    result = []
    for x, y in zip(ta, tb):
        t = '+' if x == '+' and y == '+' else '-' if '-' in (x, y) else '0'
        result.append(t)
    return trits_to_int(result)


def add(a: int, b: int) -> int:
    mod = (a + b - MIN_INT) % INT_RANGE
    return MIN_INT + mod


def compute(x: int, y: int, px: Trit, py: Trit, f: Trit) -> int:
    """Perform a computation.

    This function emulates the behaviour of the ALU.
    """
    x = -x if px == '-' else (x if px == '0' else 0)
    y = -y if py == '-' else (y if py == '0' else 0)

    if f == '-':
        # AND
        return do_and(x, y)
    elif f == '+':
        # ADD
        return add(x, y)
    else:
        # Unary on X
        if py == '-':
            # Decrement X
            return add(x, -1)
        elif py == '0':
            # X == 0?
            return 1 if x == 0 else -1
        else:
            # Increment X
            return add(x, 1)


class Emulator:
    def __init__(self):
        self.a = 0
        self.d = 0
        self.pc = 0
        self.ram = {}
        self.program = []
        self.comments = {}
        self.ticks = 0
        self.speed = 1000  # 1 kHz
        self.cycle_time = 1.0 / self.speed
        self.rate_limit = False

    def load_binary(self, stream) -> None:
        """Load a program encoded in binary format."""
        program = str(binary.decode(stream.read()))
        length = len(program)
        if length % 12 != 0:
            raise ValueError(
                    "Invalid length for binary-encoded program: "
                    f"expected a multiple of 12 but got {length}")
        self.program = []
        self.comments = {}
        for i in range(0, length, 12):
            self.program.append(program[i:i+12])

    def load_text(self, stream: io.TextIOBase) -> None:
        """Load a program encoded in text format."""
        codes = []
        comments = {}
        i = 0
        for line in stream:
            line = line.strip()
            if not line:
                continue
            code = line[:12]
            comment = line[12:].strip() if len(line) > 12 else ""

            if any(c not in '-0+' for c in code):
                raise ValueError(
                        f"Invalid characters in '{line}': expected only "
                        "-, 0 and + in the first 12 characters of each line")
            codes.append(code)
            comments[i] = comment
            i += 1
        self.program = codes
        self.comments = comments

    def load(self, stream) -> None:
        """Load a program encoded in either text or binary format.

        This method will try to auto-detect which format the stream is in, and
        call load_text() or load_binary() as appropriate.
        """
        if isinstance(stream, io.TextIOBase):
            self.load_text(stream)
        else:
            self.load_binary(stream)

    def get_ram(self, address: int) -> int:
        return self.ram.get(address, 0)

    def set_ram(self, address: int, value: int) -> None:
        self.ram[address] = value

    def get_m(self) -> int:
        return self.get_ram(self.a)

    def reset(self):
        self.a = 0
        self.d = 0
        self.pc = MIN_ADDR
        self.ticks = 0

    def execute(self):
        """Run the loaded program.

        The emulator will continue to cycle until it arrives at a program
        address beyond the end of the program, at which point we will
        terminate.
        """
        exit_address = MIN_ADDR + len(self.program)
        self.reset()
        while self.pc < exit_address:
            self.step()

    def step(self):
        """Execute one computer cycle."""
        start = time.perf_counter()

        index = self.pc - MIN_ADDR
        m = self.ram.get(self.a, 0)

        instruction = self.program[index]
        mode = instruction[11]

        if mode == '0':
            jump = instruction[:2]
            shift, f, px, py, sx, sy, t = instruction[4:11]

            x = self.a if sx == '-' else (m if sx == '0' else self.d)
            y = self.a if sy == '-' else (m if sy == '0' else self.d)
            result = compute(x, y, px, py, f)
            if shift == '-':
                trits = int_to_trits(result, 12)[1:] + '0'
                result = trits_to_int(trits)
            elif shift == '+':
                trits = '0' + int_to_trits(result, 12)[:11]
                result = trits_to_int(trits)

            nxt = add(self.pc, 1)
            if jump == '--':
                nxt = self.a if result < 0 else nxt
            elif jump == '-0':
                nxt = self.a if result == 0 else nxt
            elif jump == '-+':
                nxt = self.a if result > 0 else nxt
            elif jump == '0-':
                nxt = MIN_ADDR
            elif jump == '0+':
                nxt = self.a
            elif jump == '+-':
                nxt = self.a if result <= 0 else nxt
            elif jump == '+0':
                nxt = self.a if result != 0 else nxt
            elif jump == '++':
                nxt = self.a if result >= 0 else nxt

            self.pc = nxt

            if t == '-':
                self.a = result
            elif t == '0':
                self.ram[self.a] = result
            else:
                self.d = result
        else:
            # MOV
            value = trits_to_int(instruction[:11])
            if mode == '-':
                self.a = value
            else:
                self.d = value

            self.pc = add(self.pc, 1)

        if self.rate_limit:
            dur = time.perf_counter() - start
            if self.cycle_time > dur:
                time.sleep(self.cycle_time - dur)
        self.ticks += 1

    def get_ram_contents(self, index: int) -> int:
        return self.ram.get(index, 0)


def main(
        input_path: str = '-',
        select: list[int] | None = None):
    emu = Emulator()
    with input_stream(input_path) as stream:
        emu.load(stream)

    emu.execute()
    if select:
        for index in select:
            value = emu.get_ram_contents(index)
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
