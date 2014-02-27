#!/usr/bin/env python
# coding=utf-8
"""
Balanced Ternary
================

This library implements computations over values expressed in Balanced Ternary
form.

Balanced Ternary is a numeral system with three symbols, equating to the
decimal values -1, 0 and +1.  We use the characters -, 0 and + to represents these
values respectively.

When performing logical operations with balanced ternary values, we use the
Kleene ternary propositional logic system, where - represents False, +
represents True, and 0 represents an indeterminate value, which is either True
or False.
"""


NEG  = '-'
ZERO = '0'
POS  = '+'

ORDERING = (NEG, ZERO, POS)
INPUTS = {
        NEG:  NEG,
        '-1': NEG,
        '✗':  NEG,
        ZERO: ZERO,
        '':   ZERO,
        '=':  ZERO,
        'N':  ZERO,
        'n':  ZERO,
        'Z':  ZERO,
        'z':  ZERO,
        POS:  POS,
        '1':  POS,
        '✓':  POS,
        }
INTEGERS = {
        NEG: -1,
        ZERO: 0,
        POS:  1,
        }


class Trit(object):
    def __init__(self, value):
        if isinstance(value, int) or isinstance(value, float):
            if value == 0:
                self.value = ZERO
            elif value > 0:
                self.value = POS
            else:
                self.value = NEG
        elif isinstance(value, Trit):
            self.value = value.value
        elif value is None:
            self.value = ZERO
        else:
            text = str(value).strip()
            if text in INPUTS:
                self.value = INPUTS[text]
            else:
                raise ValueError(
                        "Failed to parse {0!r} as a trit.".format(value))

    def __unicode__(self):
        return self.value

    def __str__(self):
        return self.value

    def __hash__(self):
        return hash(self.value)

    def __repr__(self):
        return 'Trit({})'.format(int(self))

    def __int__(self):
        return INTEGERS[self.value]

    def __oct__(self):
        return oct(int(self))

    def __hex__(self):
        return hex(int(self))

    def ordinal(self):
        return ORDERING.index(self.value)

    def __bool__(self):
        """Return the boolean truth value of this trit.
        
        Only the positive trit is considered True in the boolean (two-valued
        logic) sense, the other trits are False.
        """
        return (self.value == POS)

    def __nonzero__(self):
        """Return the boolean truth value (Python2 equivalent of __bool__)."""
        return self.__bool__()

    def __neg__(self):
        """Return the negation of this Trit.
        
        The zero Trit negates itself, the positive and negative trits negate
        each other.
        """
        if self.value == NEG:
            return Trit(POS)
        elif self.value == POS:
            return Trit(NEG)
        else:
            return Trit(ZERO)

    def __pos__(self):
        """Return a copy of the trit."""
        return Trit(self)

    def __abs__(self):
        """Return the absolute value (value without any sign) of this trit.
        
        The negative trit yields the positive trit, while the positive and zero
        trits yield themselves.
        """
        if self.value == NEG:
            return Trit(POS)
        else:
            return Trit(self)

    def __invert__(self):
        """Return the inverse of this Trit (same as negation)."""
        return self.__neg__()

    def __lt__(self, other):
        return (self.ordinal() < other.ordinal())

    def __le__(self, other):
        return (self.ordinal() <= other.ordinal())

    def __eq__(self, other):
        return (self.value == other.value)

    def __ne__(self, other):
        return (self.value != other.value)

    def __gt__(self, other):
        return (self.ordinal() > other.ordinal())

    def __ge__(self, other):
        return (self.ordinal() >= other.ordinal())

    def __and__(self, other):
        """Return the tritwise AND of two trits.
        
        The result is negative if either input is negative, positive if both
        inputs are positive, otherwise zero.
        """
        if NEG in (self.value, other.value):
            return Trit(NEG)
        elif self.value == POS and other.value == POS:
            return Trit(POS)
        else:
            return Trit(ZERO)

    def __or__(self, other):
        """Return the tritwise OR of two trits.
        
        The result is positive if either input is positive, negative if both
        inputs are negative, otherwise zero.
        """
        if POS in (self.value, other.value):
            return Trit(POS)
        elif self.value == NEG and other.value == NEG:
            return Trit(NEG)
        else:
            return Trit(ZERO)

    def __xor__(self, other):
        """Return the tritwise XOR (exclusive-OR) of two trits.

        The result is zero if either input is zero, positive if one input is
        positive and the other negative, and negative otherwise.
        """
        if ZERO in (self.value, other.value):
            return Trit(ZERO)
        elif self.value != other.value:
            return Trit(POS)
        else:
            return Trit(NEG)

    def add(self, other):
        """Add two Trits and return a 2-tuple of (result, carry)."""
        carry = Trit(ZERO)
        if self.value == ZERO:
            return (other, carry)
        elif other.value == ZERO:
            return (self, carry)
        elif self == other:
            return (-self, Trit(self))
        else:
            # Values are unequal and neither is zero, must be -1 + 1.
            return (Trit(ZERO), carry)
        
