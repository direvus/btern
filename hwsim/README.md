# Balanced Ternary Hardware Simulator

The `hwsim` package is a series of hardware designs and simulation tools for a
hypothetical balanced ternary computer.

See the documentation for more detail:

- [Ternary logic system](/doc/hwsim/logic.md)
- [Fundamental components](/doc/hwsim/fundamental.md)
- [Computer architecture and machine language specification](/doc/hwsim/arch.md)

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
