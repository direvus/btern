#!/usr/bin/env python
import argparse
import math
import os
import re
import sys
from traceback import print_exc

from ternary.hardware.util import int_to_trits, input_stream, output_stream


INT_RE = re.compile(r'^[+-]?\d+$')
LABEL_RE = re.compile(r'^([^\s]+)\s*:$')
SYMBOL_RE = re.compile(r'^[^\W_\d]\w*$')
DEST_MAP = {
        'A': '-',
        'M': '0',
        'D': '+',
        }
INPUT_MAP = {
        'A': '0-',
        'M': '00',
        'D': '0+',
        '-A': '--',
        '-M': '-0',
        '-D': '-+',
        '0': '++',
        }
JUMP_MAP = {
        'JLT': '--',
        'JEZ': '-0',
        'JGT': '-+',
        'RST': '0-',
        'NOJ': '00',
        'JMP': '0+',
        'JLE': '+-',
        'JNZ': '+0',
        'JGE': '++',
        }
SHIFT_MAP = {
        '>>': '-',
        '<<': '+',
        }
PREDEF_VARS = {
        'sp': 0,
        'local': 1,
        'args': 2,
        }
MIN_ADDR = -(3 ** 11 // 2)
VAR_ADDR = -13


def parse_input(text: str) -> str:
    try:
        return INPUT_MAP[text]
    except KeyError:
        keys = ', '.join(INPUT_MAP.keys())
        raise ValueError(
                f"Invalid destination {text}, expected one of: {keys}")


def parse_dest(text: str) -> str:
    try:
        return DEST_MAP[text]
    except KeyError:
        keys = ', '.join(DEST_MAP.keys())
        raise ValueError(
                f"Invalid destination {text}, expected one of: {keys}")


def parse_optional(args) -> tuple[str, str]:
    shift = None
    jump = None
    for arg in args:
        if arg in SHIFT_MAP:
            if shift is not None:
                raise ValueError(
                    "Multiple shift specifiers found in an instruction")
            shift = SHIFT_MAP[arg]
        elif arg in JUMP_MAP:
            if jump is not None:
                raise ValueError(
                    "Multiple jump specifiers found in an instruction")
            jump = JUMP_MAP[arg]
        else:
            raise ValueError(
                    f"Expected a shift or jump specifier, but got {arg}")
    return (
            jump or '00',
            shift or '0')


class Assembler:
    def __init__(self):
        self.labels = {}
        self.variables = PREDEF_VARS.copy()
        self.instructions = []
        self.sources = []
        self.errors = []

    def read(self, stream):
        n = 0
        lines = []
        # First pass: pull out the labels and assign them to line numbers, and
        # store the actual instruction lines in a list for the second pass
        for line in stream:
            # Strip comments
            if '#' in line:
                line = line[:line.index('#')]
            if ';' in line:
                line = line[:line.index(';')]
            # Remove leading and trailing whitespace
            line = line.strip()
            if not line:
                continue

            m = LABEL_RE.match(line)
            if m:
                label = m.group(1)
                if label in self.labels:
                    raise ValueError(
                            f"Invalid label name {label}: label has "
                            "been defined previously in this program")
                self.labels[label] = n
                continue

            lines.append((n, line))
            n += 1

        # Second pass: parse the instructions into machine code
        for num, line in lines:
            self.read_line(num, line)

    def read_line(self, num: int, line: str):
        tokens = line.split()
        op = tokens[0].upper()
        args = list(tokens[1:])

        if op == 'NOP':
            self.parse_add(num, line, ('0', 'D', 'D'))
        elif op == 'ADD':
            self.parse_add(num, line, args)
        elif op == 'SUB':
            # SUB is just ADD with the second input inverted
            b = args[1]
            b = b[1:] if b.startswith('-') else '-' + b
            args[1] = b
            self.parse_add(num, line, args)
        elif op == 'CHK':
            # CHK is just ADD 0 with the same source and dest
            args.insert(0, args[0])
            args.insert(0, '0')
            self.parse_add(num, line, args)
        elif op == 'CLR':
            # CLR is just AND 0 0
            args.insert(0, '0')
            args.insert(0, '0')
            self.parse_and(num, line, args)
        elif op == 'CPY':
            # CPY is just ADD with one input zeroed
            args.insert(0, '0')
            self.parse_add(num, line, args)
        elif op == 'SHL':
            # SHL is just ADD 0 with a left shift
            args.insert(0, '0')
            args.append('<<')
            self.parse_add(num, line, args)
        elif op == 'SHR':
            # SHR is just ADD 0 with a right shift
            args.insert(0, '0')
            args.append('>>')
            self.parse_add(num, line, args)
        elif op == 'AND':
            self.parse_and(num, line, args)
        elif op == 'INC':
            self.parse_inc(num, line, args)
        elif op == 'DEC':
            self.parse_dec(num, line, args)
        elif op == 'MOV':
            self.parse_mov(num, line, args)
        else:
            self.errors.append(f"{num+1}: Unrecognised operation {op}")

    def parse_add(self, num: int, source: str, args):
        try:
            length = len(args)
            if length < 3 or length > 5:
                raise ValueError(f"expected 3-5 arguments, got {length}")
            px, x = parse_input(args[0])
            py, y = parse_input(args[1])
            dest = parse_dest(args[2])
            jump, shift = parse_optional(args[3:])

            inst = ''.join((jump, '00', shift, '+', px, py, x, y, dest, '0'))
            self.instructions.append(inst)
            self.sources.append(source)
        except Exception as e:
            self.errors.append(f"{num+1}. {source}: {e}")

    def parse_and(self, num: int, source: str, args):
        try:
            length = len(args)
            if length < 3 or length > 5:
                raise ValueError(f"expected 3-5 arguments, got {length}")
            px, x = parse_input(args[0])
            py, y = parse_input(args[1])
            dest = parse_dest(args[2])
            jump, shift = parse_optional(args[3:])

            inst = ''.join((jump, '00', shift, '-', px, py, x, y, dest, '0'))
            self.instructions.append(inst)
            self.sources.append(source)
        except Exception as e:
            self.errors.append(f"{num+1}. {source}: {e}")

    def parse_inc(self, num: int, source: str, args):
        try:
            length = len(args)
            if length < 2 or length > 4:
                raise ValueError(f"expected 2-4 arguments, got {length}")
            px, x = parse_input(args[0])
            py, y = '+0'
            dest = parse_dest(args[1])
            jump, shift = parse_optional(args[2:])

            inst = ''.join((jump, '00', shift, '0', px, py, x, y, dest, '0'))
            self.instructions.append(inst)
            self.sources.append(source)
        except Exception as e:
            self.errors.append(f"{num+1}. {source}: {e}")

    def parse_dec(self, num: int, source: str, args):
        try:
            length = len(args)
            if length < 2 or length > 4:
                raise ValueError(f"expected 2-4 arguments, got {length}")
            px, x = parse_input(args[0])
            py, y = '-0'
            dest = parse_dest(args[1])
            jump, shift = parse_optional(args[2:])

            inst = ''.join((jump, '00', shift, '0', px, py, x, y, dest, '0'))
            self.instructions.append(inst)
            self.sources.append(source)
        except Exception as e:
            self.errors.append(f"{num+1}. {source}: {e}")

    def parse_mov(self, num: int, source: str, args):
        try:
            length = len(args)
            if length != 2:
                raise ValueError(f"expected exactly 2 arguments, got {length}")

            if args[1] == 'A':
                dest = '-'
            elif args[1] == 'D':
                dest = '+'
            else:
                raise ValueError(
                        f"invalid MOV target '{args[1]}', expected A or D")

            int_match = INT_RE.match(args[0])
            symbol_match = SYMBOL_RE.match(args[0])
            if args[0] in self.labels:
                index = self.labels[args[0]]
                value = int_to_trits(MIN_ADDR + index, 11)
            elif args[0] in self.variables:
                index = self.variables[args[0]]
                value = int_to_trits(VAR_ADDR + index, 11)
            elif int_match:
                dec = int(args[0])
                value = int_to_trits(dec, 11)
            elif symbol_match:
                # New variable, allocate it a register relative to VAR_ADDR
                index = len(self.variables)
                self.variables[args[0]] = index
                value = int_to_trits(VAR_ADDR + index, 11)
            elif len(args[0]) == 11 and all(c in '-0+' for c in args[0]):
                value = args[0]
            else:
                raise ValueError(
                        f"invalid MOV value '{args[0]}', expected a symbol "
                        "name, decimal integer, or 11-trit sequence")

            self.instructions.append(value + dest)
            self.sources.append(source)
        except Exception as e:
            self.errors.append(f"{num+1}. {source}: {e}")

    def write(self, stream):
        if not self.instructions:
            return

        width = max(1, int(math.log(len(self.instructions), 10)) + 1)
        for i, inst in enumerate(self.instructions):
            labels = (k for k, v in self.labels.items() if v == i)
            source = ''.join(f'{x}: ' for x in labels) + self.sources[i]
            linenum = f'{i + 1:0{width}d}'
            stream.write(f'{inst}  # {linenum}. {source}\n')


def main(input_path: str = '-'):
    if input_path == '-':
        output_path = '-'
    else:
        dirname = os.path.dirname(input_path)
        base = os.path.basename(input_path)
        root, ext = os.path.splitext(base)
        output_path = os.path.join(dirname, f'{root}.t12')

    assembler = Assembler()
    with input_stream(input_path) as stream:
        assembler.read(stream)

    if assembler.errors:
        print("Errors encountered during parsing:", file=sys.stderr)
        for e in assembler.errors:
            print(e, file=sys.stderr)
        return False

    with output_stream(output_path) as stream:
        assembler.write(stream)
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
