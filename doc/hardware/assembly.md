# Index

- [Ternary logic system](/doc/hardware/logic.md)
- [Fundamental components](/doc/hardware/fundamental.md)
- [Composite logic gates](/doc/hardware/gates.md)
- [Computer architecture and machine language specification](/doc/hardware/arch.md)
- Assembly language

# Assembly language

The assembly language for the balanced ternary computer is line oriented.
A newline character (0x10) terminates a line.

Leading and trailing whitespace on a line are ignored. Empty lines are ignored.

A hash (#) or semicolon (;) character begins a comment. All characters from the
start of a comment until the end of the line are ignored.

After removing whitespace and comments, and skipping blank lines, every
remaining line must be either a **label** or an **instruction**.

## Labels

A label definition consists of pretty much any sequence of non-whitespace
characters, followed by a colon (:), for example:

```
LOOP1:
```

Each label defines a reference to the location in program memory of the
instruction that immediately follows it. You can use these label names as
shorthand for their literal values in a MOV instruction.

Each label name can only be used to define one location. It is an error to
specify the same label name in multiple locations.

## Instructions

Each instruction consists of several elements separated by whitespace, for
example:

```
MOV -70 D
CPY D M
DEC D D JGT
```

The first element must always be the operation name, a sequence of three
letters. The remaining elements are the arguments to the operation, and the
requirements for the number of type of these arguments differs depending on the
operation. These are explained in detail below.

## Operations

The first element of each instruction must be one of the following operation
names:

- MOV
- ADD
- SUB
- CHK
- CLR
- CPY
- AND
- INC
- DEC
- SHL
- SHR
- NOP

The MOV operation is a special operation with its own distinct rules. All other
operations are **compute** operations.

## General rules for compute operations

There are some general rules for arguments that apply to all compute
operations, that is, all operations except for MOV.

In compute operations, all **input** arguments must be one of the following:

- The name of a register: `A`, `M` or `D`, or
- The name of a negated register: `-A`, `-M` or `-D`, or
- The literal value zero: `0`.

A **destination** argument must be one of `A`, `M` or `D`.

Every compute operation has two optional arguments that can appear after the
mandatory arguments. They are the **shift** specifier, and the **jump**
specifier. The operation may have a shift only, a jump only, both a shift
and a jump in any order, or neither.

The shift specifier is either `>>` for shift right, or `<<` for shift left. The
result of the computation is shifted before it is sent to the destination
register, and before testing it for a possible jump.

The jump specifier is one of the following jump codes:

- `JLT` -- jump if the result is less than zero
- `JEZ` -- jump if the result is exactly zero
- `JGT` -- jump if the result is greater than zero
- `RST` -- jump to the start of the program
- `NOJ` -- do not jump
- `JMP` -- jump unconditionally
- `JLE` -- jump if the result is greater than or equal to zero
- `JNZ` -- jump if the result is not equal to zero
- `JGE` -- jump if the result is less than or equal to zero

A jump specifier, if present, will test the result of the computation (after
any shift) against the selected criterion, and if it matches, the program will
jump to the address currently held in the `A` register, and execute the
instruction at that address in the next cycle.

The code `NOJ` (no jump) has the same effect as omitting the jump specifier
entirely.

### MOV

The MOV (move) instruction puts a literal value directly into the A or D
register.

It requires exactly two arguments. The first is the literal value, which can be
one of:

- A sequence of 11 trits, using the symbols `-`, `0` and `+`.
- A signed decimal integer, consisting of an optional sign specifier (`-` or
  `+`), followed by a sequence of digits.
- The name of a label defined in the same program.
- The name of a variable.

The second argument is the destination, which must be either `A` or `D`.

For example:

```
MOV -0+-------- A
MOV 10 D
MOV LOOP1 A
MOV pointer A
```

A variable name must consist of a letter, followed by zero or more "word"
characters (letters, digits and underscores). When the first argument to MOV
matches this pattern, and it's not one of the defined labels for the program,
it is taken to be a variable name.

The first time a variable name is encountered in a program, it is assigned its
own register address in memory, and that address is substituted in as the
argument to MOV by the assembler. If that same variable name is encountered in
other parts of the program, the assembler substitutes that same register
address.

There are a few predefined variables:

- `sp` for the stack pointer
- `local` for the current local variable memory segment
- `args` for the current function arguments memory segment

### ADD

The ADD instruction adds the two inputs together and stores in the result in a
register.

It has three mandatory arguments, the two inputs and the destination register.

```
ADD A D M
```

### SUB

The SUB (subtract) instruction subtracts the second input from the first, and
writes the result to a register.

It has three mandatory arguments, the two inputs and the destination register,
for example:

```
SUB M D M
```

SUB is a convenient shorthand for calling ADD with the second input negated.

### CHK

The CHK (check) instruction does not modify any register, but selects a
register as the input of computation, typically so that it can be used as the
test value for a conditional jump.

It has one mandatory argument: the input register.

For example:

```
CHK D
```

CHK is a convenient shorthand for adding zero to the register, and writing the
result back to the same register.

### CLR

The CLR (clear) instruction sets a register to zero.

It has one mandatory argument: the destination register.

For example:

```
CLR M
```
CLR is a convenient shorthand for `AND 0 0 <dest>`

### CPY

The CPY (copy) instruction copies the contents of one register to another.

It has two mandatory arguments, the source register and the destination
register.

CPY is a convenient shorthand for adding zero to the source and writing the
result to the destination.

### AND

The AND instruction performs logical AND on its inputs.

It has three mandatory arguments, the two inputs and the destination register,
for example:

```
AND A D D
```

### INC

The INC (increment) instruction adds one to its input.

It has two mandatory arguments, the input and the destination register,
for example:

```
INC D D
```

### DEC

The DEC (decrement) instruction subtracts one from its input.

It has two mandatory arguments, the input and the destination register,
for example:

```
DEC D D
```

### SHL

The SHL (shift left) instruction shifts the trits in the input one position to
the left.

It has two mandatory arguments, the input and the destination register. For
example:

```
SHL D D
```

SHL is a convenient shorthand for `ADD 0 <in> <dest> <<`

Because SHL applies its own shift argument to the instruction, it is an error
to specify a shift to this operation.

### SHR

The SHR (shift right) instruction shifts the trits in the input one position to
the right.

It has two mandatory arguments, the input and the destination register. For
example:

```
SHR M D
```

SHR is a convenient shorthand for `ADD 0 <in> <dest> >>`

Because SHR applies its own shift argument to the instruction, it is an error
to specify a shift to this operation.

### NOP

The NOP (no operation) instruction doesn't do anything apart from occupy the
computer for one cycle.

It has no mandatory arguments.

NOP is a shorthand for `ADD 0 D D`.

# Example program

The following example program listing performs simple multiplication by
addition:

```
# Multiply the value in RAM address 0 by the value in address 1.
# Store the result in address 3.
# We will use address 2 as a loop counter.

# RAM[3] = 0
MOV 3 A
CLR M

# RAM[2] = RAM[1]
MOV 1 A
CPY M D
MOV 2 A
CPY D M

# while (RAM[2] > 0):
#     RAM[3] += RAM[0]
#     RAM[2] -= 1
LOOP:
MOV 0 A
CPY M D
MOV 3 A
ADD D M M
MOV 2 A
DEC M D
CPY D M
MOV LOOP A
CHK D JGT
```

This assembly code maps to the machine code program:

```
0+000000000-  # 1. MOV 3 A
00000-++++00  # 2. CLR M
+0000000000-  # 3. MOV 1 A
00000++0+0+0  # 4. CPY M D
-+000000000-  # 5. MOV 2 A
00000++0++00  # 6. CPY D M
00000000000-  # 7. LOOP: MOV 0 A
00000++0+0+0  # 8. CPY M D
0+000000000-  # 9. MOV 3 A
00000+00+000  # 10. ADD D M M
-+000000000-  # 11. MOV 2 A
0000000-00+0  # 12. DEC M D
00000++0++00  # 13. CPY D M
-+----------  # 14. MOV LOOP A
-+000++0+++0  # 15. CHK D JGT
```
