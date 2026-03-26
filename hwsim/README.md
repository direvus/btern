# Balanced Ternary Hardware Simulator

The `hwsim` package is a series of hardware designs and simulation tools for a
hypothetical balanced ternary computer.

## Ternary logic system

Every connection or "wire" in the computer is deemed to carry one of three
possible signal states: negative, zero or positive, for which we use the
symbols `−`, `0` and `+`.

Logic gates operate on the Kleene three-valued logic system, where signals
are interpreted as follows:

| Signal | Meaning |
|--------|---------|
|  `−`   | False   |
|  `0`   | Unknown |
|  `+`   | True    |

The `0` value means a value that could be either `−` or `+`, but we don't know
which one. Otherwise, logical operations follow the same rules as normal
two-valued Boolean logic systems.

So, for example, a logical operation like `0 AND +` would yield `0`, because
the left-hand operand could be either `−` or `+`, and therefore the result of
the `AND` cannot be decided.

On the other hand, the operation `0 AND −` is definitively false, because the
result cannot ever be true, regardless of whether the left-hand operand is true
or false.

## Fundamental components

This is *not* an electrical engineering project, so we begin by assuming
several fundamental components, and build up the rest of the computer by making
connections between these fundamental components.

These fundamental components are:

- Inverter (NOT)
- Positively-biased inverter (PNOT)
- Negatively-biased inverter (NNOT)
- Inverted conjunction (NAND)
- Inverted disjunction (NOR)
- Inverted overall bias (NANY)
- Inverted consensus (NCONS)
- Clock
- Data flip flop (DFF) 

### Inverter (NOT)

![NOT gate](/doc/hwsim/not.png)

Logically inverts its input:

|  in | out |
|-----|-----|
| `−` | `+` |
| `0` | `0` |
| `+` | `−` |

### Positively-biased inverter (PNOT)

![PNOT gate](/doc/hwsim/pnot.png)

Logically inverts its input, but a zero input is biased to a positive output:

|  in | out |
|-----|-----|
| `−` | `+` |
| `0` | `+` |
| `+` | `−` |

### Negatively-biased inverter (NNOT)

![NNOT gate](/doc/hwsim/nnot.png)

Logically inverts its input, but a zero input is biased to a negative output:

|  in | out |
|-----|-----|
| `−` | `+` |
| `0` | `−` |
| `+` | `−` |

### Inverted logical conjunction (NAND)

![NAND gate](/doc/hwsim/nand.png)

Outputs the inverse of the logical AND of its two inputs:

a NAND b == NOT (a AND b)

| a/b | `−` | `0` | `+` |
|-----|-----|-----|-----|
| `−` | `+` | `+` | `+` |
| `0` | `+` | `0` | `0` |
| `+` | `+` | `0` | `−` |

### Inverted logical disjunction (NOR)

![NOR gate](/doc/hwsim/nor.png)

Outputs the inverse of the logical OR of its two inputs:

a NOR b == NOT (a OR b)

| a/b | `−` | `0` | `+` |
|-----|-----|-----|-----|
| `−` | `+` | `0` | `−` |
| `0` | `0` | `0` | `−` |
| `+` | `−` | `−` | `−` |

### Inverted overall bias (NANY)

Outputs the inverse of the logical ANY of its two inputs.

There is no direct analogue for ANY in two-valued Boolean logic. It outputs
zero when one input is negative and the other is positive, the non-zero value
when one of the inputs is zero and the other is non-zero, and the same value as
the input when both inputs are equal. It can be conceptualised as the overall
charge bias of the inputs when taken together.

a NANY b == NOT (a ANY b)

| a/b | `−` | `0` | `+` |
|-----|-----|-----|-----|
| `−` | `+` | `+` | `0` |
| `0` | `+` | `0` | `−` |
| `+` | `0` | `−` | `−` |

### Inverted consensus (NCONS)

Outputs the inverse of the logical CONS of its two inputs.

There is no direct analogue for CONS in two-valued Boolean logic. When both
inputs are equal (they are in "consensus"), it outputs the input value. In all
other cases, it outputs zero.

a NCONS b == NOT (a CONS b)

| a/b | `−` | `0` | `+` |
|-----|-----|-----|-----|
| `−` | `+` | `0` | `0` |
| `0` | `0` | `0` | `0` |
| `+` | `0` | `0` | `−` |

### Clock

The clock delivers a signal that oscillates on some regular interval. Unlike
the other fundamental components, we do not simulate the physical connections
of the clock component itself, rather it is abstracted by the `tick()` method
on components.

When the `tick()` method is invoked on a component, that component executes any
behaviour that is triggered on a clock signal, and propagates the clock signal
recursively down to its subcomponents.

### Data flip flop (DFF) 

The data flip flop is the fundamental component of data memory. It is capable
of storing a single trit of data, and either retains or replaces that value
when it receives a clock tick, depending on how its input signals are set at
the time of the tick.

It takes two inputs, 'in' and 'load'. The 'load' signal governs the behaviour
of the DFF when it receives a clock tick. If 'load' is zero, then the current
stored value is retained as-is. If 'load' is negative, then the stored value is
reset to zero. Finally, if 'load' is positive, then the stored value is
replaced by the value of the 'in' signal.

The following table shows what the next stored value of the DFF will be, after
a clock tick, given the current stored value and the values of the 'load' and
'in' inputs.

| load|  in | `−` | `0` | `+` |
|-----|-----|-----|-----|-----|
| `−` | `−` | `0` | `0` | `0` |
| `−` | `0` | `0` | `0` | `0` |
| `−` | `+` | `0` | `0` | `0` |
| `0` | `−` | `−` | `0` | `+` |
| `0` | `0` | `−` | `0` | `+` |
| `0` | `+` | `−` | `0` | `+` |
| `+` | `−` | `−` | `−` | `−` |
| `+` | `0` | `0` | `0` | `0` |
| `+` | `+` | `+` | `+` | `+` |

## Computer Architecture

The computer uses a word size of 12 trits. It has a RAM module and a program
ROM module, each of which can be addressed using 11 trits, for a total
addressable space of 177,147 words, or 2,125,764 trits.

The Central Processing Unit (CPU) accepts a 12-trit machine language
instruction, and a 12-trit value from the currently active RAM register. It
produces the result of executing the instruction, a new RAM address to
activate, a signal indicating whether to load, retain or reset the contents of
that RAM address, and the address of the next instruction to execute from the
program ROM.

The CPU contains two main registers, named `A` and `D`. These registers,
together with the value from the active RAM register (named `M`), can be taken
as inputs to the Arithmetic Logic Unit (ALU).

The `A` register has two additional special functions:

- Selects the active register in RAM for the next clock cycle. Thus, in any
  given clock cycle, `M` is the value in the register with the address that was
  held in `A` in the previous cycle.
- Selects the target address in program ROM for a successful jump condition.

## Machine Language Specification

Each machine language instruction is 12 trits long, and it makes sense to look
at them from most to least significant trit:

| Index | Meaning                         |
|-------|---------------------------------|
|  11   | Instruction mode (move/compute) |
|  10   | Computation target (A/M/D)      |
|   9   | ALU input select (M+D/A+D/A+M)  |
|   8   | Y-input transform (-Y/Y/0)      |
|   7   | X-input transform (-X/X/0)      |
|   6   | ALU function select (&/-1/+1/+) |
|   5   | Shift (right/none/left)         |
|   4   | Reserved                        |
|   3   | Reserved                        |
|   2   | Reserved                        |
|   1   | Jump control 2                  |
|   0   | Jump control 1                  |

### Instruction mode (index 11)

The most significant trit at index 11 controls the overall instruction mode.
When it is zero, the instruction is in compute (normal) mode.

When it is non-zero, the instruction treats the remaining 11 trits as a literal
data value, and loads that value directly into either the `A` or the `D`
register. The high bit of the target register will be set to zero.

To load a literal value with 12 significant trits into a register, it's
recommended to first load in the 11 high trits using a Move instruction, then
shift it left, then use an increment or decrement instruction to set the low
trit.

| Code | Mode |
|------|------|
|  `−` | Move literal value directly into `A` |
|  `0` | Compute |
|  `+` | Move literal value directly into `D` |

### Target select (index 10)

The trit at index 10 selects where the result of computation should be written:

| Code | Target |
|------|--------|
|  `−` |   `A`  |
|  `0` |   `M`  |
|  `+` |   `D`  |

### ALU input select (index 9)

The trit at index 9 selects which two inputs should be sent to the ALU for
computation. The ALU has two inputs, named `X` and `Y`, and they are selected
from `A`, `M` and `D` as follows:

| Code |  X  |  Y  |
|------|-----|-----|
|  `−` | `M` | `D` |
|  `0` | `A` | `D` |
|  `+` | `A` | `M` |

### X and Y input transforms (indexes 7-8)

The two trits at indexes 7 and 8 indicate whether to apply a transform
operation to each of the selected X and Y inputs before sending it to the ALU;
index 7 controls the X input, and index 8 controls the Y. Each input will
either be replaced with all zeroes, passed through as-is, or negated.

Note that in balanced ternary, a tritwise logical negation and an arithmetic
negation are the same thing.

| Code | Operation    |
|------|--------------|
|  `−` | Negate       |
|  `0` | Pass through |
|  `+` | Zero out     |

### ALU function select (index 6)

The trit at index 6 controls which function the ALU will apply to its inputs.

| Code | Operation  | Detail                          |
|------|------------|---------------------------------|
|  `−` | X AND Y    | Tritwise logical AND of X and Y |
|  `0` | X+1 or X-1 | Increase or decrease X by 1     |
|  `+` | X + Y      | Arithmetic sum of X and Y       |

When the code is zero, the Y input is disregarded and instead the ALU uses the
trit at index 8 to select a unary operation to apply to X:

|  [8] | Operation | Detail            |
|------|-----------|-------------------|
|  `−` | X-1       | Subtract 1 from X |
|  `0` | Reserved  |                   |
|  `+` | X+1       | Add 1 to X        |

### Trit shifting (index 5)

The trit at index 5 selects whether to shift the trits of the output from the
ALU.

"Shift left" means the trit at index 0 is moved to index 1, and so on until the
trit at index 10 is moved to 11, and the trit at 11 is discarded. The empty
place at index 0 is filled with a zero.

"Shift right" is the same but in the opposite direction.

| Code | Operation   |
|------|-------------|
|  `−` | Shift right |
|  `0` | No shift    |
|  `+` | Shift left  |

### Jump controls (indexes 0-1)

The trits at indexes 0 and 1 control which instruction address will be executed
next. The JLT, JEZ, JGT, JLE, JNZ and JGE settings test the output from the ALU
against the selected criterion, and if it matches, will jump to the address
held in `A`.

The RST setting will unconditionally jump to the first address of the program
ROM. The JMP setting will unconditionally jump to the address in `A`, and the
NOJ setting will not jump, but advance normally to the current instruction
address plus one.

| j1  | j2  | name | Result                        |
|-----|-----|------|-------------------------------|
| `-` | `-` | JLT  | Jump if test is <0            |
| `-` | `0` | JEZ  | Jump if test is =0            |
| `-` | `+` | JGT  | Jump if test is >0            |
| `0` | `-` | RST  | Jump to start unconditionally |
| `0` | `0` | NOJ  | Do not jump                   |
| `0` | `+` | JMP  | Jump unconditionally          |
| `+` | `-` | JLE  | Jump if test is <=0           |
| `+` | `0` | JNZ  | Jump if test is !=0           |
| `+` | `+` | JGE  | Jump if test is >=0           |
