# Index

- Ternary logic system
- [Fundamental components](/doc/hwsim/fundamental.md)
- [Composite logic gates](/doc/hwsim/gates.md)
- [Computer architecture and machine language specification](/doc/hwsim/arch.md)
- [Assembly language](/doc/hwsim/assembly.md)

# Ternary logic system

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

The `0` value represents an unknown value that could be either `−` or `+`, but
we don't know which one. Otherwise, logical operations follow the same rules as
normal two-valued Boolean logic systems.

So, for example, a logical operation like `0 AND +` would yield `0`, because
the left-hand operand could be either `−` or `+`, and therefore the result of
the `AND` cannot be decided.

On the other hand, the operation `0 AND −` is definitively false, because the
result cannot ever be true, regardless of whether the left-hand operand is true
or false.

Many of the familiar formulas from two-valued logic continue to hold in this
three-valued system, for example ternary `x AND +` is equal to `x` in the same
way that `x AND true` is equal to `x` in binary.

De Morgan's Theorem applies exactly the same way in both systems:

```
NOT (NOT x AND NOT y) == x OR y

NOT (NOT x OR NOT Y) == x AND y
```
