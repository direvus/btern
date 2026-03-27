# Index

- [Ternary logic system](/doc/hwsim/logic.md)
- [Fundamental components](/doc/hwsim/fundamental.md)
- [Computer architecture and machine language specification](/doc/hwsim/arch.md)

# Assembly language

The assembly language for the balanced ternary computer is line oriented.
A newline character (0x10) terminates a line.

Leading and trailing whitespace on a line are ignored. Empty lines are ignored.

A hash (#) or semicolon (;) character begins a comment. All characters from the
start of a comment until the end of the line are ignored.

After removing whitespace and comments, and skipping blank lines, every
remaining line must be either a **label** or an **instruction**.

## Labels

A label consists of an ASCII letter character, followed by any number of "word" characters (letters, digits and underscores), followed by a
colon (:), for example:

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
- CPY
- AND
- INC
- DEC
- NOP

The MOV operation is a special operation with its own distinct rules. All other
operations are **compute** operations.

## General rules for compute operations

There are some general rules for arguments that apply to all compute
operations, that is, all operations except for MOV.

In all other operation, all **input** arguments must be one of the following:

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

The second argument is the destination, which must be either `A` or `D`.

For example:

```
MOV -0+-------- A
MOV 10 D
MOV LOOP1 A
```

### ADD

The CPY (copy) instruction copies the contents of one register to another.

It has two mandatory arguments, the input and the destination register.

```
ADD A D M
```

### SUB

The SUB (subtract) instruction subtracts one input from another, and writes the
result to a register.

It has three mandatory arguments, the two inputs and the destination register,
for example:

```
SUB M D M
```

SUB is a convenient shorthand for calling ADD with the second input negated.

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

### NOP

The NOP (no operation) instruction doesn't do anything apart from occupy the
computer for one cycle.

It has no mandatory arguments.

NOP is a shorthand for ADD 0 0.
