#!/usr/bin/env python
"""VM translator: translates VM code into assembly"""
import argparse
import os
import sys
from collections.abc import Iterable
from traceback import print_exc

from ternary.hardware.util import input_stream, output_stream


SEGMENTS = {'local', 'args', 'this', 'that'}
# Codes that always produce the same static assembly output and require no
# substitutions.
STATIC_CODES = {
        'add': (
            'MOV sp A',
            'DEC M M',
            'CPY M A',
            'CPY M D',
            'DEC A A',
            'ADD M D M',
            ),
        }


class Translator:
    def __init__(self):
        self.program = []

    def read(self, stream):
        n = 1
        for line in stream:
            line = line.strip()
            if not line:
                continue
            code = self.translate(line, n)
            self.program.extend(code)
            n += 1

    def write(self, stream):
        for line in self.program:
            stream.write(f'{line}\n')

    def translate(self, line: str, num: int) -> Iterable[str]:
        tokens = line.split()
        name = tokens[0]
        args = tokens[1:]

        if name in STATIC_CODES:
            # Append a comment to the first line of the static assembly code,
            # otherwise return it as-is.
            code = list(STATIC_CODES[name])
            code[0] = f'{code[0]}  # {line}'
            return code

        if name == 'push':
            return self.translate_push(*args)
        elif name == 'pop':
            return self.translate_pop(*args)

        raise ValueError(f"Invalid operation '{name}' at line {num}")

    def translate_push(self, segment: str, offset: int) -> Iterable[str]:
        """Translate a `push` instruction into assembly.

        A push instruction takes a single value and adds it to the top of the
        stack. In normal operation, the arguments to 'push' are the name of a
        memory segment, and an offset into that segment. We find the base
        memory address of the memory segment, add the offset to it, take the
        value held in the register at that address, write it into the register
        currently pointed to by the stack pointer SP, and then advance SP to
        point at the next register.

        In assembly pseudo-code:

        1. addr = segment + offset
        2. *SP = *addr
        3. SP++

        If the segment name is 'constant' then we treat the offset argument as
        a literal value to add to the stack instead.

        Return an iterable of assembly code instructions as strings.
        """
        if segment in SEGMENTS:
            code = [f'MOV {segment} A  # push {segment} {offset}']
            # Skip adding the offset if it's zero
            if offset != 0:
                code.extend((
                        f'MOV {offset} D',
                        'ADD A D A',
                        ))
            code.extend((
                    'CPY M D',
                    'MOV sp A',
                    'INC M M',
                    'DEC M A',
                    'CPY D M',
                    ))
            return code
        elif segment == 'constant':
            return (
                    f'MOV {offset} D  # push constant {offset}',
                    'MOV sp A',
                    'INC M M',
                    'DEC M A',
                    'CPY D M',
                    )

        raise ValueError(f"Invalid segment name '{segment}'.")

    def translate_pop(self, segment: str, offset: int) -> Iterable[str]:
        """Translate a `pop` instruction into assembly.

        A pop instruction removes the value from the top of the stack, and
        writes it to some memory location. In normal operation, the arguments
        to 'pop' are the name of a memory segment, and an offset into that
        segment. We find the base memory address of the segment, add the offset
        to it, write the value from the top of the stack there, and substract
        one from the stack pointer.

        In assembly pseudo-code:

        1. addr = segment + offset
        2. SP--
        3. *addr = *SP

        Return an iterable of assembly code instructions as strings.
        """
        if segment in SEGMENTS:
            code = [f'MOV {segment} A  # pop {segment} {offset}']
            # Skip adding the offset if it's zero
            if offset != 0:
                code.extend((
                        f'MOV {offset} D',
                        'ADD A D D',
                        ))
            code.extend((
                    'MOV addr A',
                    'CPY D M',
                    'MOV sp A',
                    'DEC M M',
                    'CPY M A',
                    'CPY M D',
                    'MOV addr A',
                    'CPY M A',
                    'CPY D M',
                    ))
            return code
        elif segment == 'constant':
            raise ValueError("Pop to constant is not valid.")

        raise ValueError(f"Invalid segment name '{segment}'.")


def main(input_path: str = '-'):
    if input_path == '-':
        output_path = '-'
    else:
        dirname = os.path.dirname(input_path)
        base = os.path.basename(input_path)
        root, ext = os.path.splitext(base)
        output_path = os.path.join(dirname, f'{root}.asm')

    translator = Translator()
    with input_stream(input_path) as stream:
        translator.read(stream)

    with output_stream(output_path) as stream:
        translator.write(stream)

    return True


def cli():
    parser = argparse.ArgumentParser()
    parser.add_argument('input_path', nargs='?', default='-')
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
