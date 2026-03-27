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

This is *not* an electronics engineering project, so we begin by assuming
several fundamental components, and build up the rest of the computer by making
connections between these fundamental components.

The fundamental components are:

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

The ANY operation is particular to ternary logic, and has no direct analogue in
two-valued Boolean logic. It outputs zero when one input is negative and the
other is positive, the non-zero value when one of the inputs is zero and the
other is non-zero, and the same value as the input when both inputs are equal.
It can be conceptualised as the overall charge bias of the inputs when taken
together.

a NANY b == NOT (a ANY b)

| a/b | `−` | `0` | `+` |
|-----|-----|-----|-----|
| `−` | `+` | `+` | `0` |
| `0` | `+` | `0` | `−` |
| `+` | `0` | `−` | `−` |

### Inverted consensus (NCONS)

Outputs the inverse of the logical CONS of its two inputs.

The CONS operation is particular to ternary logic, and has no direct analogue
in two-valued Boolean logic. When both inputs are equal (they are in
"consensus"), it outputs the input value. In all other cases, it outputs zero.

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
recursively down to all of its subcomponents.

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
ROM module, each of which is addressed using 11 trits, for a total addressable
space of 177,147 words, or 2,125,764 trits.

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

## Machine Language Specification

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

### Instruction mode (index 11)

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

### Target select (index 10)

The trit at index 10 selects where the result of computation should be written:

| Code | Target |
|------|--------|
|  `−` |   `A`  |
|  `0` |   `M`  |
|  `+` |   `D`  |

### X and Y input select (indexes 8-9)

The trits at indexes 8 and 9 select which inputs should be sent to the ALU for
computation. The ALU has two inputs, named `X` and `Y`. The `X` input is
selected by index 8 and the `Y` input is selected by index 9, as follows:

| Code | Input |
|------|-------|
|  `−` |  `A`  |
|  `0` |  `M`  |
|  `+` |  `D`  |

### X and Y input transforms (indexes 6-7)

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

### ALU function select (index 5)

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

### Trit shifting (index 4)

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

## Future expansion

There are a few opportunities for future expansion in this design.

- One reserved ALU operation (when both 'f' and 'py' are zero) that could be
  made to do something useful, just not sure what. Could be a tryte swap, or a
  tritwise reverse?
- Two reserved trits in the machine language.
- The 'reset' signal only has two states, zero or non-zero. There is room to
  make neg and pos behave differently, perhaps adding something like a halt?
- Consider ways to terminate the program. Maybe reserve the very last address
  of the program space as a shutdown, so if the CPU ever tries to jump there,
  we stop running? That way a shutdown is just two machine instructions -- move
  11+ into A and then jump.

## Acknowledgements

My approach to hardware simulation, the computer architecture and the machine
language design are all heavily inspired by the course [Nand to
Tetris](https://www.nand2tetris.org/) by Noam Nisan and Shimon Schocken.

The selection of the seven fundamental ternary logic gates (NOT, PNOT, NNOT,
NAND, NOR, NANY and NCONS) is based on the work of [Louis
Duret-Robert](https://louis-dr.github.io/cd4007.html), who demonstrated that
those gates can be feasibly constructed from transistors.
