# Balanced Ternary Hardware Simulator

The `hardware` subpackage is a series of hardware designs and simulation tools
for a hypothetical 12-trit balanced ternary computer.

See the documentation for more detail:

- [Ternary logic system](/doc/hardware/logic.md)
- [Fundamental components](/doc/hardware/fundamental.md)
- [Composite logic gates](/doc/hardware/gates.md)
- [Computer architecture and machine language specification](/doc/hardware/arch.md)
- [Assembly language](/doc/hardware/assembly.md)

## Future expansion

There are a few opportunities for future expansion in this design.

- Two reserved trits in the machine language.
- The 'reset' signal only has two states, zero or non-zero. There is room to
  make neg and pos behave differently, perhaps adding something like a halt?

## Acknowledgements

My approach to hardware simulation, the computer architecture and the machine
language design are all heavily inspired by the course [Nand to
Tetris](https://www.nand2tetris.org/) by Noam Nisan and Shimon Schocken.

The selection of the seven fundamental ternary logic gates (NOT, PNOT, NNOT,
NAND, NOR, NANY and NCONS) is based on the work of [Louis
Duret-Robert](https://louis-dr.github.io/cd4007.html), who demonstrated that
those gates can be feasibly constructed from transistors.
