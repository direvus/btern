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
|   −    | False   |
|   0    | Unknown |
|   +    | True    |

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
|  −  |  +  |
|  0  |  0  |
|  +  |  −  |

### Positively-biased inverter (PNOT)

![PNOT gate](/doc/hwsim/pnot.png)

Logically inverts its input, but a zero input is biased to a positive output:

|  in | out |
|-----|-----|
|  −  |  +  |
|  0  |  +  |
|  +  |  −  |

### Negatively-biased inverter (NNOT)

![NNOT gate](/doc/hwsim/nnot.png)

Logically inverts its input, but a zero input is biased to a negative output:

|  in | out |
|-----|-----|
|  −  |  +  |
|  0  |  −  |
|  +  |  −  |

### Inverted logical conjunction (NAND)

### Inverted logical disjunction (NOR)

### Inverted overall bias (NANY)

### Inverted consensus (NCONS)

### Clock

### Data flip flop (DFF) 
