# Index

- [Ternary logic system](/doc/hardware/logic.md)
- Fundamental components
- [Composite logic gates](/doc/hardware/gates.md)
- [Computer architecture and machine language specification](/doc/hardware/arch.md)
- [Assembly language](/doc/hardware/assembly.md)

# Fundamental components

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

## Inverter (NOT)

![NOT gate](/doc/hardware/not.png)

Logically inverts its input:

|  in | out |
|-----|-----|
| `−` | `+` |
| `0` | `0` |
| `+` | `−` |

## Positively-biased inverter (PNOT)

![PNOT gate](/doc/hardware/pnot.png)

Logically inverts its input, but a zero input is biased to a positive output:

|  in | out |
|-----|-----|
| `−` | `+` |
| `0` | `+` |
| `+` | `−` |

## Negatively-biased inverter (NNOT)

![NNOT gate](/doc/hardware/nnot.png)

Logically inverts its input, but a zero input is biased to a negative output:

|  in | out |
|-----|-----|
| `−` | `+` |
| `0` | `−` |
| `+` | `−` |

## Inverted logical conjunction (NAND)

![NAND gate](/doc/hardware/nand.png)

Outputs the inverse of the logical AND of its two inputs:

a NAND b == NOT (a AND b)

| a/b | `−` | `0` | `+` |
|-----|-----|-----|-----|
| `−` | `+` | `+` | `+` |
| `0` | `+` | `0` | `0` |
| `+` | `+` | `0` | `−` |

## Inverted logical disjunction (NOR)

![NOR gate](/doc/hardware/nor.png)

Outputs the inverse of the logical OR of its two inputs:

a NOR b == NOT (a OR b)

| a/b | `−` | `0` | `+` |
|-----|-----|-----|-----|
| `−` | `+` | `0` | `−` |
| `0` | `0` | `0` | `−` |
| `+` | `−` | `−` | `−` |

## Inverted overall bias (NANY)

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

## Inverted consensus (NCONS)

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

## Clock

The clock delivers a signal that oscillates on some regular interval. Unlike
the other fundamental components, we do not simulate the physical connections
of the clock component itself, rather it is abstracted by the `tick()` method
on components.

When the `tick()` method is invoked on a component, that component executes any
behaviour that is triggered on a clock signal, and propagates the clock signal
recursively down to all of its subcomponents.

## Data flip flop (DFF) 

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

