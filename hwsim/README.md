# Balanced Ternary Hardware Simulator

The `hwsim` package is a series of hardware designs and simulation tools for a
hypothetical balanced ternary computer.

## Ternary logic system

Every connection or "wire" in the computer is deemed to carry one of three
possible signal states: negative, zero or positive, for which we use the
symbols `−`, `0` and `+`.

Logic gates operate on the Kleene three-valued logic system, where signals
are interpreted as follows:

| signal | meaning |
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

|     |     |  b  |     |
|  a  | `−` | `0` | `+` |
|-----|-----|-----|-----|
| `−` | `+` | `+` | `+` |
| `0` | `+` | `0` | `0` |
| `+` | `+` | `0` | `−` |

### Inverted logical disjunction (NOR)

![NOR gate](/doc/hwsim/nor.png)

Outputs the inverse of the logical OR of its two inputs:

a NOR b == NOT (a OR b)

|     |     |  b  |     |
|  a  | `−` | `0` | `+` |
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

|     |     |  b  |     |
|  a  | `−` | `0` | `+` |
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

|     |     |  b  |     |
|  a  | `−` | `0` | `+` |
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

|     |     |     | curr|     |
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
