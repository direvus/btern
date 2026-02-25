#!/usr/bin/env python
# coding=utf-8
import numbers

import trit
import integer


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

    def get_trits(self):
        """Return the contents of this Register as a Trits object."""
        return trit.Trits(self)


class Instruction(object):
    """A single instruction that is executable by a Processor.

    Each Instruction has:
      * an opcode; a sequence of trits to identify the instruction,
      * a size; the number of trits in the instruction including the opcode,
      * a function; a callable taking two arguments, being the Processor
        executing the instruction, and the entire instruction including the
        opcode and any operands,
      * optionally a name; a human-readable label for the instruction.
    """
    def __init__(self, opcode, size, function, name=None):
        if size < len(opcode):
            raise ValueError(
                    "Invalid Instruction size {}; must be at least the "
                    "length of the opcode ({}).".format(size, len(opcode)))
        self.opcode = opcode
        self.size = size
        self.function = function
        self.name = name

    def __str__(self):
        if self.name is None:
            return str(self.opcode)
        return self.name

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
        self.stop = False

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
        """Continue the instruction cycle, until the stop flag is set."""
        self.stop = False
        while not self.stop:
            self.fetch()
            self.increment()
            self.execute()

    def halt(self, *args):
        """Cause the processor to cease running."""
        self.stop = True


class T3(Processor):
    """A trivial 3-trit single-operand processor.

    Instructions have a fixed size of 6, comprising a 3-trit opcode and
    3-trit operand.

    There are 27 registers, each 6 trits in size, identified using 3-trit
    addresses.  The register 000 is the default register.  Instructions that
    produce a result store it in the default register.  The other 26 registers
    --- through 00-, and 00+ through +++, are general use registers.

    The program memory likewise consists of 27 instructions of 6 trits each,
    addressed --- through +++.
    """
    OPCODE_SIZE = 3
    ADDRESS_SIZE = 3
    INSTRUCTION_SIZE = 6
    REGISTER_SIZE = 6
    PROGRAM_SIZE = 27 * 6
    ADDRESS_MIN = trit.Trits('---')
    ADDRESS_MAX = trit.Trits('+++')
    INSTRUCTIONS = (
            ('--+', 'notR', 'log_not'),
            ('-+-', 'or R', 'log_or'),
            ('-+0', 'shfR', 'shift_right'),
            ('-++', 'putL', 'put_low'),
            ('0--', 'clrR', 'clear'),
            ('0-0', 'jmpN', 'jump_nonzero'),
            ('0-+', 'subR', 'sub'),
            ('00-', 'lodR', 'load'),
            ('000', 'halt', 'halt'),
            ('00+', 'savR', 'save'),
            ('0+-', 'addR', 'add'),
            ('0+0', 'jmp0', 'jump_zero'),
            ('0++', 'outR', 'output'),
            ('+--', 'putH', 'put_high'),
            ('+-0', 'shfL', 'shift_left'),
            ('+-+', 'andR', 'log_and'),
            ('++-', 'xorR', 'log_xor'),
            )

    def __init__(self, verbose=False):
        instructions = ((Instruction(
                trit.Trits(code),
                self.INSTRUCTION_SIZE,
                getattr(T3, func),
                name)
            for code, name, func in self.INSTRUCTIONS))
        super(T3, self).__init__(instructions)
        self.verbose = verbose
        self.ip = Register([], self.ADDRESS_SIZE)
        self.ir = Register([], self.INSTRUCTION_SIZE)
        self.registers = {
                trit.Trits([x, y, z]): Register([], self.REGISTER_SIZE)
                    for x in trit.GLYPHS
                    for y in trit.GLYPHS
                    for z in trit.GLYPHS}
        self.dr = self.registers[trit.Trits('000')]
        self.program = Register([], self.PROGRAM_SIZE)
        self.outputs = []
        self.reset()

    def reset(self):
        self.ip.put(self.ADDRESS_MIN)
        self.ir.clear()
        self.outputs = []
        for address in self.registers:
            self.registers[address].clear()

    def fetch(self):
        address = int(integer.UInt(self.ip)) * self.INSTRUCTION_SIZE
        instruction = self.program[address:address+self.INSTRUCTION_SIZE]
        self.ir.put(instruction)

    def increment(self):
        self.ip.put(integer.Int(self.ip) + integer.Int('+'))

    def execute(self):
        opcode = self.ir[:self.OPCODE_SIZE]
        if opcode not in self.instructions:
            raise ValueError(
                    "Invalid instruction {!r}: "
                    "unrecognised opcode.".format(str(self.ir)))
        instruction = self.instructions[opcode]
        if self.verbose:
            print('{} {} {}'.format(
                    self.ir, instruction, self.get_operand(self.ir)))
        self.instructions[opcode].execute(self, self.ir)

    def set_program(self, program):
        """Write instructions to the program memory.

        Clear the entire program memory, then write the given program code to
        the program register in order, beginning at ---.
        """
        if len(program) > self.PROGRAM_SIZE:
            raise ValueError(
                    "Invalid program: "
                    "length {} exceeds total program memory {}.".format(
                        len(program), self.PROGRAM_SIZE))
        self.program.clear()
        self.program[:len(program)] = program

    def get_operand(self, data):
        """Return the remainder of an instruction after the opcode."""
        return trit.Trits(data[self.OPCODE_SIZE:])

    def get_register(self, address):
        """Return the contents of the register at 'address'."""
        return self.registers[address].get_trits()

    def load(self, data):
        """Copy the contents of a register into the default register.

        'Load 000' is a no-op.
        """
        address = self.get_operand(data)
        content = self.get_register(address)
        self.dr.put(content)

    def save(self, data):
        """Copy the contents of the default register into a register.

        'Save 000' is a no-op.
        """
        content = self.dr.get_trits()
        address = self.get_operand(data)
        self.registers[address].put(content)

    def add(self, data):
        """Add the contents of a register to the default register."""
        a = integer.Int(self.dr)
        b = integer.Int(self.get_register(self.get_operand(data)))
        self.dr.put(a + b)

    def sub(self, data):
        """Subtract the contents of a register from the default register."""
        a = integer.Int(self.dr)
        b = integer.Int(self.get_register(self.get_operand(data)))
        self.dr.put(a - b)

    def jump_zero(self, data):
        """Jump to a program address, if the default register is zero."""
        if self.dr.is_zero():
            address = self.get_operand(data)
            self.ip.put(address)

    def jump_nonzero(self, data):
        """Jump to a program address, if the default register is not zero."""
        if not self.dr.is_zero():
            address = self.get_operand(data)
            self.ip.put(address)

    def clear(self, data):
        """Set all the trits of a register to zero."""
        self.registers[self.get_operand(data)].clear()

    def output(self, data):
        """Output the contents of a register.

        The contents are printed to stdout and also appended as a string to the
        'outputs' list.
        """
        content = str(self.get_register(self.get_operand(data)))
        self.outputs.append(content)
        print(content)

    def put_low(self, data):
        """Write the operand to the lower trits of the default register."""
        operand = self.get_operand(data)
        self.dr[-len(operand):] = operand

    def put_high(self, data):
        """Write the operand to the higher trits of the default register."""
        operand = self.get_operand(data)
        self.dr[:len(operand)] = operand

    def shift_left(self, data):
        """Shift the contents of a register one place to the left.

        Write the result to the default register.
        """
        address = self.get_operand(data)
        content = self.get_register(address)
        self.dr.put(content << 1)

    def shift_right(self, data):
        """Shift the contents of a register one place to the right.

        Write the result to the default register.
        """
        address = self.get_operand(data)
        content = self.get_register(address)
        self.dr.put(content >> 1)

    def log_and(self, data):
        """Tritwise logical AND operation.

        Compute the tritwise logical AND of the default register and the
        register addressed by the operand, and write the result to the default
        register.
        """
        self.dr.put(self.dr & self.get_register(self.get_operand(data)))

    def log_or(self, data):
        """Tritwise logical OR operation.

        Compute the tritwise logical OR of the default register and the
        register addressed by the operand, and write the result to the default
        register.
        """
        self.dr.put(self.dr | self.get_register(self.get_operand(data)))

    def log_xor(self, data):
        """Tritwise logical XOR operation.

        Compute the tritwise logical XOR (exclusive OR) of the default register
        and the register addressed by the operand, and write the result to the
        default register.
        """
        self.dr.put(self.dr ^ self.get_register(self.get_operand(data)))

    def log_not(self, data):
        """Tritwise logical NOT operation.

        Compute the tritwise logical NOT of the register addressed by the
        operand, and write the result to the default register.
        """
        self.dr.put(~self.get_register(self.get_operand(data)))
