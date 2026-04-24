#!/usr/bin/env python
"""VM translator: translates VM code into assembly"""
import argparse
import io
import os
import sys
from collections.abc import Iterable
from traceback import print_exc

from ternary.trit import NEG, POS
from ternary.hardware.util import (
        input_stream, output_stream, int_to_trits,
        MIN_ADDR, MAX_ADDR, MIN_INT, MAX_INT)


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
        'sub': (
            'MOV sp A',
            'DEC M M',
            'CPY M A',
            'CPY M D',
            'DEC A A',
            'ADD M -D M',
            ),
        'and': (
            'MOV sp A',
            'DEC M M',
            'CPY M A',
            'CPY M D',
            'DEC A A',
            'AND M D M',
            ),
        'or': (
            'MOV sp A',
            'DEC M M',
            'CPY M A',
            'CPY M D',
            'DEC A A',
            'AND -M -D M',
            'CPY -M M',
            ),
        'not': (
            'MOV sp A',
            'DEC M A',
            'CPY -M M',
            ),
        'shiftl': (
            'MOV sp A',
            'DEC M A',
            'SHL M M',
            ),
        'shiftr': (
            'MOV sp A',
            'DEC M A',
            'SHR M M',
            ),
        'inc': (
            'MOV sp A',
            'DEC M A',
            'INC M M',
            ),
        'dec': (
            'MOV sp A',
            'DEC M A',
            'DEC M M',
            ),
        'lt': (
            'MOV sp A',
            'DEC M M',
            'CPY M A',
            'CPY M D',
            'DEC A A',
            'SUB D M M',
            ),
        'gt': (
            'MOV sp A',
            'DEC M M',
            'CPY M A',
            'CPY M D',
            'DEC A A',
            'SUB M D M',
            ),
        'eq': (
            'MOV sp A',
            'DEC M M',
            'CPY M A',
            'CPY M D',
            'DEC A A',
            'SUB D M D',
            'ISZ D M',
            ),
        'ne': (
            'MOV sp A',
            'DEC M M',
            'CPY M A',
            'CPY M D',
            'DEC A A',
            'SUB D M D',
            'ISZ D D',
            'CPY -D M',
            ),
        }


class Translator:
    def __init__(self):
        self.program = []
        self.module = ''
        self.linenum = 0

    def read(self, stream: io.TextIOBase, filename: str):
        self.linenum = 1
        self.module = filename
        self.program.append(f"### Module: {filename}")
        for line in stream:
            line = line.strip()
            if not line:
                continue
            try:
                code = self.translate(line)
            except ValueError as e:
                raise ValueError(
                        f"{e} at {self.module} line {self.linenum}")
            self.program.extend(code)
            self.linenum += 1

    def write(self, stream: io.TextIOBase):
        for line in self.program:
            stream.write(f'{line}\n')

    def translate(self, line: str) -> Iterable[str]:
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

        if name == 'pop':
            return self.translate_pop(*args)

        if name == 'label':
            return (f'{self.module}.{args[0]}:',)

        if name == 'goto':
            label = f'{self.module}.{args[0]}'
            return (
                    f'MOV {label} A  # goto {args[0]}',
                    'NOP JMP',
                    )

        raise ValueError(f"Invalid operation '{name}'")

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
        offset = int(offset)
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
            code = []
            if offset < MIN_INT or offset > MAX_INT:
                raise ValueError(
                        f"Invalid constant value {offset}: cannot be "
                        "represented within 12 trits.")
            if offset < MIN_ADDR or offset > MAX_ADDR:
                # This constant value needs 12 trits to represent, so we're
                # going to MOV the most significant 11 trits in first, shift
                # them left and then use INC or DEC as needed to populate the
                # least significant trit.
                trits = int_to_trits(offset, 12)
                code.extend((
                        f'MOV {trits[:-1]} D  # push constant {offset}',
                        'SHL D D',
                        ))
                if trits[-1] == POS:
                    code.append('INC D D')
                if trits[-1] == NEG:
                    code.append('DEC D D')
            else:
                # Constant value fits within 11 trits, so just use a literal
                # MOV.
                code.append(f'MOV {offset} D  # push constant {offset}')

            code.extend((
                    'MOV sp A',
                    'INC M M',
                    'DEC M A',
                    'CPY D M',
                    ))
            return code

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
        filename = 'stdin'
        if stream != sys.stdin:
            filename = input_path
        translator.read(stream, filename)

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
