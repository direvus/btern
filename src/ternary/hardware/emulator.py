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
from collections.abc import Callable
from traceback import print_exc

from PIL import Image, ImageDraw, ImagePalette

from ternary import binary
from ternary.hardware.util import (
        int_to_trits, trits_to_int, input_stream, output_stream,
        MIN_ADDR, MIN_INT, INT_RANGE, COLOURS_3T, Trit)


SCREEN_WIDTH = 320
SCREEN_HEIGHT = 200
SCREEN_END_ADDR = MIN_ADDR + (SCREEN_WIDTH * SCREEN_HEIGHT / 4)


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
    def __init__(self, screen_scale: int = 1):
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
        self.screen_scale = screen_scale
        self.palette = None
        self.palette_map = {}
        self.screen_image = self.make_image()
        self.memory_callback = None

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

    def set_memory_callback(self, callback: Callable) -> None:
        self.memory_callback = callback

    def get_ram(self, address: int) -> int:
        return self.ram.get(address, 0)

    def set_ram(self, address: int, value: int) -> None:
        self.ram[address] = value
        self.update_image(address, value)
        if self.memory_callback:
            self.memory_callback(address, value)

    def get_m(self) -> int:
        return self.get_ram(self.a)

    def set_speed(self, speed: int) -> None:
        self.speed = int(speed)
        self.cycle_time = 1.0 / self.speed

    def set_rate_limit(self, value: bool) -> None:
        self.rate_limit = bool(value)

    def reset(self):
        self.a = 0
        self.d = 0
        self.pc = MIN_ADDR
        self.ticks = 0
        self.make_image()

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
        mode = instruction[0]

        if mode == '0':
            jump = instruction[10:]
            tgt, sy, sx, py, px, f, shift = instruction[1:8]

            x = self.a if sx == '-' else (m if sx == '0' else self.d)
            y = self.a if sy == '-' else (m if sy == '0' else self.d)
            result = compute(x, y, px, py, f)

            if shift == '-':
                # Shift right
                trits = '0' + int_to_trits(result, 12)[:11]
                result = trits_to_int(trits)
            elif shift == '+':
                # Shift left
                trits = int_to_trits(result, 12)[1:] + '0'
                result = trits_to_int(trits)

            nxt = add(self.pc, 1)
            if jump == '--':
                nxt = self.a if result < 0 else nxt
            elif jump == '0-':
                nxt = self.a if result == 0 else nxt
            elif jump == '+-':
                nxt = self.a if result > 0 else nxt
            elif jump == '-0':
                nxt = MIN_ADDR
            elif jump == '+0':
                nxt = self.a
            elif jump == '-+':
                nxt = self.a if result <= 0 else nxt
            elif jump == '0+':
                nxt = self.a if result != 0 else nxt
            elif jump == '++':
                nxt = self.a if result >= 0 else nxt

            self.pc = nxt

            if tgt == '-':
                self.a = result
            elif tgt == '0':
                self.set_ram(self.a, result)
            else:
                self.d = result
        else:
            # MOV
            value = trits_to_int(instruction[1:])
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

    def get_palette(self) -> ImagePalette.ImagePalette:
        if self.palette is not None:
            return self.palette

        self.palette_map = {}
        seq = []
        count = 0
        for key, colour in COLOURS_3T.items():
            r = int(colour[:2], 16)
            g = int(colour[2:4], 16)
            b = int(colour[4:], 16)
            self.palette_map[key] = count
            seq.extend((r, g, b))
            count += 1

        self.palette = ImagePalette.ImagePalette('RGB', seq)
        return self.palette

    def make_image(self) -> None:
        width = SCREEN_WIDTH * self.screen_scale
        height = SCREEN_HEIGHT * self.screen_scale
        self.screen_image = Image.new('P', (width, height))
        self.screen_image.putpalette(self.get_palette())
        self.screen_draw = ImageDraw.Draw(self.screen_image)
        bg = self.palette_map['000']
        self.screen_draw.rectangle((0, 0, width, height), fill=bg, width=0)

    def update_image(self, addr: int, value: int) -> None:
        """Update the screen render image after a memory update.

        Given a memory address, and the value held in that address, refresh the
        pixels covered by that address, by drawing new rectangles on the
        existing screen render.

        Do nothing if the given address is not in the screen memory region, or
        if the screen image has not been initialised.
        """
        if self.screen_image is None or addr >= SCREEN_END_ADDR:
            return

        row, col = divmod(addr - MIN_ADDR, SCREEN_WIDTH / 4)
        x0 = col * 4 * self.screen_scale
        y0 = row * self.screen_scale
        y1 = y0 + self.screen_scale - 1
        trits = int_to_trits(value, 12)
        for i in range(0, 12, 3):
            key = trits[i:i+3]
            colour_index = self.palette_map[key]
            x1 = x0 + self.screen_scale - 1
            bounds = (x0, y0, x1, y1)
            self.screen_draw.rectangle(bounds, fill=colour_index, width=0)
            x0 += self.screen_scale

    def render(self) -> Image:
        if self.screen_image is None:
            self.make_image()
        addr = MIN_ADDR
        for y in range(SCREEN_HEIGHT):
            x = 0
            while x < SCREEN_WIDTH:
                value = int_to_trits(self.get_ram(addr), 12)
                for i in range(0, 12, 3):
                    key = value[i:i+3]
                    colour_index = self.palette_map[key]
                    x0 = x * self.screen_scale
                    y0 = y * self.screen_scale
                    x1 = x0 + self.screen_scale - 1
                    y1 = y0 + self.screen_scale - 1
                    self.screen_draw.rectangle(
                            [(x0, y0), (x1, y1)],
                            fill=colour_index,
                            width=0)
                    x += 1
                addr += 1
        return self.screen_image

    def get_image(self) -> Image:
        return self.screen_image


def main(
        input_path: str = '-',
        select: list[int] | None = None,
        render_path: str = '',
        screen_scale: int = 1):
    emu = Emulator(screen_scale)
    with input_stream(input_path) as stream:
        emu.load(stream)

    emu.execute()

    if render_path:
        im = emu.render()
        with output_stream(render_path, binary=True) as stream:
            im.save(stream, format='PNG')

    if select:
        for index in select:
            value = emu.get_ram_contents(index)
            print(value)

    return True


def cli():
    parser = argparse.ArgumentParser()
    parser.add_argument('input_path', nargs='?', default='-')
    parser.add_argument('-s', '--select', type=int, action='append')
    parser.add_argument('-r', '--render-path', type=str)
    parser.add_argument('-x', '--screen-scale', type=int, default=1)

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
