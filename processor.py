#!/usr/bin/env python
# coding=utf-8
import numbers

from . import trit
from . import integer


class Register(trit.Trits):
    """A fixed-length, mutable, ordered sequence of trits.

    A Register's length is set when it is created, and is fixed for the
    lifetime of the Register.  The contents of the Register within that length
    may be modified freely.
    """
    __hash__ = None

    def __init__(self, trits, length):
        if not isinstance(length, numbers.Integral):
            raise TypeError(
                    "Invalid length argument {!r}; "
                    "length must be a positive integer.".format(length))
        if length <= 0:
            raise ValueError(
                    "Invalid length argument {}; "
                    "length must be positive.".format(length))
        super(Register, self).__init__(trits, length)
        self.trits = list(self.trits)
        self.length = length

    def __str__(self):
        return ''.join([str(x) for x in self.trits])

    def __len__(self):
        return self.length

    def __setitem__(self, key, value):
        if isinstance(key, slice):
            length = len(range(*key.indices(self.length)))
            if length != len(value):
                raise ValueError(
                        "Invalid slice assignment of {} items to {} indices; "
                        "would modify the length of the Register.".format(
                            len(value), length))
            self.trits[key] = [trit.Trit.make(x) for x in value]
        else:
            self.trits[key] = trit.Trit.make(value)

    def put(self, trits):
        self[:] = trit.Trits(trits, self.length)

    def clear(self):
        self.put([])


class Instruction(object):
    """A single instruction that is executable by a Processor.

    Each Instruction has:
      * an opcode; a sequence of trits to identify the instruction, 
      * a size; the number of trits in the instruction including the opcode,
      * a function; a callable taking two arguments, being the Processor
        executing the instruction, and the entire instruction including the
        opcode and any operands.
    """
    def __init__(self, opcode, size, function):
        if size < len(opcode):
            raise ValueError(
                    "Invalid Instruction size {}; must be at least the "
                    "length of the opcode ({}).".format(size, len(opcode)))
        self.opcode = opcode
        self.size = size
        self.function = function

    def execute(self, processor, data):
        self.function(processor, data)


class Processor(object):
    """Abstract base class for a simple fetch-increment-execute processor.

    This class emulates a basic fetch-increment-execute processor cycle.  The
    size of instructions, how instructions are to be loaded, the number and
    size of registers available, and the size of the program register, are all
    left to inheriting classes to determine.
    """
    def __init__(self, instructions):
        self.instructions = {}
        for ins in instructions:
            self.instructions[ins.opcode] = ins
        self.halt = False

    def fetch(self):
        """Retrieve the next instruction from the program."""
        raise NotImplementedError

    def increment(self):
        """Increment the instruction pointer."""
        raise NotImplementedError

    def execute(self):
        """Execute the most recently fetched instruction."""
        raise NotImplementedError

    def run(self):
        """Continue the instruction cycle, until the halt flag is set."""
        while not self.halt:
            self.fetch()
            self.increment()
            self.execute()

    def halt(self, *args):
        """Cause the processor to cease running."""
        self.halt = True


class T3(Processor):
    """A trivial 3-trit single-operand processor.

    Instructions have a fixed size of 6, comprising a 3-trit opcode and
    3-trit operand.

    There are 27 registers, each 6 trits in size, identified using 3-trit
    addresses.  The register 000 is the default register.  Instructions that
    produce a result store it in the default register.  The other 26 registers
    --- through 00-, and 00+ through +++, are general use registers.

    The program memory likewise consists of 27 instruction registers of 6 trits
    each.
    """
    OPCODE_SIZE = 3
    ADDRESS_SIZE = 3
    INSTRUCTION_SIZE = 6
    REGISTER_COUNT = 27
    REGISTER_SIZE = 6
    PROGRAM_SIZE = 162
    INSTRUCTIONS = (
            ('000', Processor.halt),
            )
    ADDRESS_MIN = trit.Trits('---')
    ADDRESS_MAX = trit.Trits('+++')

    def __init__(self):
        super(T3, self).__init__((
            Instruction(trit.Trits(a), self.INSTRUCTION_SIZE, b)
                for a, b in self.INSTRUCTIONS))
        self.ip = Register([], self.ADDRESS_SIZE)
        self.ir = Register([], self.INSTRUCTION_SIZE)
        self.registers = {
                trit.Trits([x, y, z]): Register([], self.REGISTER_SIZE)
                    for x in trit.GLYPHS
                    for y in trit.GLYPHS
                    for z in trit.GLYPHS}
        self.program = {
                trit.Trits([x, y, z]): Register([], self.INSTRUCTION_SIZE)
                    for x in trit.GLYPHS
                    for y in trit.GLYPHS
                    for z in trit.GLYPHS}
        self.dr = self.registers['000']
        self.reset()

    def reset(self):
        self.ip[:] = self.ADDRESS_MIN
        self.ir.clear()
        for address in self.registers:
            self.registers[address].clear()

    def get_ip_address(self):
        return trit.Trits(self.ip)

    def fetch(self):
        self.ir.put(self.program[self.get_ip_address()])

    def increment(self):
        if self.get_ip_address() == self.ADDRESS_MAX:
            value = self.ADDRESS_MIN
        else:
            value = integer.Int(self.ip) + integer.Int('+')
        self.ip.put(value)

    def execute(self):
        opcode = self.ir[:self.OPCODE_SIZE]
        operand = self.ir[self.OPCODE_SIZE:]
        self.instructions[opcode].execute(self, operand)
