# Index

- [Ternary logic system](/doc/hwsim/logic.md)
- [Fundamental components](/doc/hwsim/fundamental.md)
- [Composite logic gates](/doc/hwsim/gates.md)
- Computer architecture and machine language specification
- [Assembly language](/doc/hwsim/assembly.md)

# Computer Architecture

The computer uses a word size of 12 trits. It has a RAM module and a program
ROM module, each of which is addressed using 11 trits, for a total addressable
space of 177,147 words, or 2,125,764 trits.

## CPU

![CPU architecture](/doc/hwsim/cpu.png)

The Central Processing Unit (CPU) accepts a 12-trit machine language
instruction, a 12-trit value from the currently active RAM register, and a
reset signal. It produces the result of executing the instruction, a new RAM
address to activate, a signal indicating whether to load, retain or reset the
contents of that RAM address, and the address of the next instruction to
execute from the program ROM.

The CPU contains two main registers, the `A` ("Address") register and the `D`
("Data") register.

The `A` register has two special functions:

- Selects the active register in RAM for the next clock cycle. Thus, in any
  given clock cycle, `M` is the value in the register with the address that was
  held in `A` in the previous cycle.
- Selects the target address in program ROM for a successful jump condition.

The `D` register is a general purpose data register with no special functions.

The mnemonic `M` refers to the value from the active RAM register that was
supplied to the CPU in the current cycle.

`A`, `M` and `D` are all eligible for selection as inputs to the Arithmetic
Logic Unit (ALU), and are all eligible as targets to receive the result of a
computation.

## Arithmetic Logic Unit (ALU)

![ALU architecture](/doc/hwsim/alu.png)

The ALU accepts two 12-trit inputs, 'x' and 'y', and three control signals
'px', 'py' and 'f'.

The 'px' and 'py' signals instruct the ALU whether to perform a transform on
the 'x' and 'y' inputs respectively, before passing them on to the main
function.

If the 'px' or 'py' is negative, that input is negated. If the 'px' or 'py' is
zero, that input is passed through as-is. If the 'px' or 'py' is positive, that
input is replaced with zero.

The 'f' signal instructs the ALU which function to perform on the inputs. When
'f' is negative, the function is a logical tritwise AND. When 'f' is positive,
the function is arithmetic addition. When 'f' is zero, we ignore the 'y' input
and apply a unary function to 'x'. Because 'y' is ignored, we re-use the 'py'
signal to select either increment of x (when 'py' is positive) or decrement of
x (when 'py' is negative).

# Machine Language Specification

Each machine language instruction is 12 trits long, and it makes sense to look
at them from most to least significant trit:

| Index | Meaning                         |
|-------|---------------------------------|
|  11   | Instruction mode (move/compute) |
|  10   | Computation target (A/M/D)      |
|   9   | Y-input select (A/M/D)          |
|   8   | X-input select (A/M/D)          |
|   7   | Y-input transform (-Y/Y/0)      |
|   6   | X-input transform (-X/X/0)      |
|   5   | ALU function select (&/-1/+1/+) |
|   4   | Shift (right/none/left)         |
|   3   | Reserved                        |
|   2   | Reserved                        |
|   1   | Jump control 2                  |
|   0   | Jump control 1                  |

## Instruction mode (index 11)

The most significant trit, at index 11, controls the overall instruction mode.
When it is zero, the instruction is in compute (normal) mode.

When it is non-zero, the instruction is in move mode. It treats the remaining
11 trits as a literal data value, and loads that value directly into either the
`A` or the `D` register. The high trit of the target register will be set to
zero.

To load a literal value with 12 significant trits into a register, it's
recommended to first load in the 11 high trits using a Move instruction, then
shift it left, then use an increment or decrement instruction to set the low
trit.

| Code | Mode                                 |
|------|--------------------------------------|
|  `−` | Move literal value directly into `A` |
|  `0` | Compute                              |
|  `+` | Move literal value directly into `D` |

## Target select (index 10)

The trit at index 10 selects where the result of computation should be written:

| Code | Target |
|------|--------|
|  `−` |   `A`  |
|  `0` |   `M`  |
|  `+` |   `D`  |

## X and Y input select (indexes 8-9)

The trits at indexes 8 and 9 select which inputs should be sent to the ALU for
computation. The ALU has two inputs, named `X` and `Y`. The `X` input is
selected by index 8 and the `Y` input is selected by index 9, as follows:

| Code | Input |
|------|-------|
|  `−` |  `A`  |
|  `0` |  `M`  |
|  `+` |  `D`  |

## X and Y input transforms (indexes 6-7)

The two trits at indexes 6 and 7 indicate whether to apply a transform
operation to each of the selected X and Y inputs before sending it to the ALU;
index 6 controls the X input, and index 7 controls the Y. Each input will
either be replaced with all zeroes, passed through as-is, or negated.

Note that in balanced ternary, a tritwise logical negation and an arithmetic
negation are the same thing.

| Code | Operation    |
|------|--------------|
|  `−` | Negate       |
|  `0` | Pass through |
|  `+` | Zero out     |

## ALU function select (index 5)

The trit at index 5 controls which function the ALU will apply to its inputs.

| Code | Operation  | Detail                          |
|------|------------|---------------------------------|
|  `−` | X AND Y    | Tritwise logical AND of X and Y |
|  `0` | X+1 or X-1 | Increase or decrease X by 1     |
|  `+` | X + Y      | Arithmetic sum of X and Y       |

When the code at index 5 is zero, the Y input is disregarded, so the Y-input
transform trit at index 7 has no effect on the computation. So instead the ALU
uses the trit at index 7 to select a unary operation to apply to X:

| [5] | [7] | Operation | Detail            |
|-----|-----|-----------|-------------------|
| `0` | `−` | X-1       | Subtract 1 from X |
| `0` | `0` | Reserved  |                   |
| `0` | `+` | X+1       | Add 1 to X        |

## Trit shifting (index 4)

The trit at index 4 selects whether to shift the trits of the output from the
ALU.

In a shift operation, all the trits of a value are shifted one place to the
left or right. Here, "left" and "right" are with respect to the trits laid out
in arithmetic order, with index 11 on the left, through to index 0 on the right.

"Shift left" means the trit at index 0 is moved to index 1, index 1 is moved to
2, and so on until the trit at index 10 is moved to 11, and the trit at 11 is
discarded. The empty place at index 0 is filled with a zero.

"Shift right" is the same but in the opposite direction.

| Code | Operation   |
|------|-------------|
|  `−` | Shift right |
|  `0` | No shift    |
|  `+` | Shift left  |

## Jump controls (indexes 0-1)

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

