# Index

- [Ternary logic system](/doc/hardware/logic.md)
- [Fundamental components](/doc/hardware/fundamental.md)
- Composite logic gates
- [Computer architecture and machine language specification](/doc/hardware/arch.md)
- [Assembly language](/doc/hardware/assembly.md)

# Composite logic gates

Composite gates are made up of connections between some set of the [fundamental
components](/doc/hardware/fundamental.md) NAND, NOR, NANY, NCONS, NOT, PNOT and
NNOT.

## AND / OR

To take one of the simplest examples, an AND gate is composed of two
fundamental components: a NAND and a NOT, connected together like so:

![AND gate diagram](/doc/hardware/and.png)

The OR and ANY gates follow the same pattern, but with NOR and NANY in place of
the NAND respectively.

## XOR

The XOR (exclusive OR) gate is composed of a NAND, a NOT and two NORS:

![XOR gate diagram](/doc/hardware/xor.png)

## ISZ (is zero)

The ISZ gate takes a single input, and its output is positive if the input is
zero, and negative otherwise. It is composed of a PNOT, NOT and NAND:

![ISZ gate diagram](/doc/hardware/iszero.png)

## 2-way ISZ

The 2-way ISZ gate takes two inputs, and its output is positive only if both
inputs are zero, and negative otherwise.

![ISZ2 gate diagram](/doc/hardware/iszero2.png)

## 12-way ISZ

The 12-way ISZ gate takes a 12-trit input bus. Its output is positive only if
all 12 inputs are zero, and negative otherwise.

![ISZ12 gate diagram](/doc/hardware/iszero12.png)

## CLU (cycle up) and CLD (cycle down)

The cycle up gate takes a single input, and outputs the value of its input
bumped up one step, so a negative becomes a zero, a zero becomes a positive,
and a positive wraps around to become negative.

![CLU gate diagram](/doc/hardware/clu.png)

Cycle down works the same way, but in the opposite direction.

![CLD gate diagram](/doc/hardware/cld.png)

## 3-way Multiplexer

The 3-way multiplexer (MUX) is an essential logic gate that many of the more complex
components are built around. It takes three data inputs 'a', 'b' and 'c', and a
selector 's'. The output is selected from one of the three data inputs, based
on the value of the selector: when the selector is negative, the output is 'a'.
When the selector is zero, the output is 'b', and when the selector is
positive, the output is 'c'.

![Multiplexer gate diagram](/doc/hardware/mux.png)
