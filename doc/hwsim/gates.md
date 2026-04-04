# Index

- [Ternary logic system](/doc/hwsim/logic.md)
- [Fundamental components](/doc/hwsim/fundamental.md)
- Composite logic gates
- [Computer architecture and machine language specification](/doc/hwsim/arch.md)
- [Assembly language](/doc/hwsim/assembly.md)

# Composite logic gates

Composite gates are made up of connections between some set of the [fundamental
components](/doc/hwsim/fundamental.md) NAND, NOR, NANY, NCONS, NOT, PNOT and
NNOT.

## AND / OR

To take one of the simplest examples, an AND gate is composed of two
fundamental components: a NAND and a NOT, connected together like so:

![AND gate diagram](/doc/hwsim/and.png)

The OR and ANY gates follow the same pattern, but with NOR and NANY in place of
the NAND respectively.

## XOR

The XOR (exclusive OR) gate is composed of a NAND, a NOT and two NORS:

![XOR gate diagram](/doc/hwsim/xor.png)

## ISZ (is zero)

The ISZ gate takes a single input, and its output is positive if the input is
zero, and negative otherwise. It is composed of a PNOT, NOT and NAND:

![ISZ gate diagram](/doc/hwsim/iszero.png)

## CLU (cycle up) and CLD (cycle down)

The cycle up gate takes a single input, and outputs the value of its input
bumped up one step, so a negative becomes a zero, a zero becomes a positive,
and a positive wraps around to become negative.

Cycle down works the same way, but in the opposite direction.

![CLU gate diagram](/doc/hwsim/clu.png)

![CLD gate diagram](/doc/hwsim/cld.png)

## 3-way Multiplexer

The 3-way multiplexer (MUX) is an essential logic gate that many of the more complex
components are built around. It takes three data inputs 'a', 'b' and 'c', and a
selector 's'. The output is selected from one of the three data inputs, based
on the value of the selector: when the selector is negative, the output is 'a'.
When the selector is zero, the output is 'b', and when the selector is
positive, the output is 'c'.

![Multiplexer gate diagram](/doc/hwsim/mux.png)
