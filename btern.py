#!/usr/bin/env python
# coding=utf-8
"""
Balanced Ternary
================

This library implements computations over values expressed in Balanced Ternary
form.

Balanced Ternary is a numeral system with three symbols, equating to the
decimal values -1, 0 and +1.  We use the characters -, 0 and + to represent
these values respectively.

When performing logical operations with balanced ternary values, we use the
Kleene ternary propositional logic system, where - represents False, +
represents True, and 0 represents an indeterminate value, which is either True
or False.
"""
import math


NEG  = '-'
ZERO = '0'
POS  = '+'

GLYPHS = (NEG, ZERO, POS)
INTEGERS = {
        NEG: -1,
        ZERO: 0,
        POS:  1}
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


class Trit(object):
    """A ternary bit (trit) is the basic unit of information in ternary.

    In balanced ternary, each trit represents one of the three values:
      * -1 (negative, false, low),
      *  0 (zero, unknown, none), or
      *  1 (positive, true, high).
    """
    def __init__(self, value):
        self.value = value
        self.integer = INTEGERS[self.value]

    @staticmethod
    def make(value):
        """Return a Trit corresponding to 'value'.

        If 'value' is a Trit, we return that Trit unmodified.  If it is an
        integer or a float, we return a Trit according to whether the number is
        negative, zero, or positive.

        Otherwise we treat 'value' and string and try to parse it.  If it
        matches one of the keys in INPUTS then it yields a Trit.  If not,
        the value is not recognised and we raise a ValueError.
        """
        if isinstance(value, Trit):
            return value
        elif isinstance(value, int) or isinstance(value, float):
            if value == 0:
                return TRITS[ZERO]
            elif value > 0:
                return TRITS[POS]
            else:
                return TRITS[NEG]
        elif value is None:
            return TRITS[ZERO]

        text = str(value).strip()
        if text in INPUTS:
            return TRITS[INPUTS[text]]
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
        return self.integer

    def __oct__(self):
        return oct(int(self))

    def __hex__(self):
        return hex(int(self))

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
            return TRITS[POS]
        elif self.value == POS:
            return TRITS[NEG]
        else:
            return TRITS[ZERO]

    def __pos__(self):
        """Unary plus is an identity function: return the trit."""
        return self

    def __abs__(self):
        """Return the absolute value (value without any sign) of this trit.
        
        The negative trit yields the positive trit, while the positive and zero
        trits yield themselves.
        """
        if self.value == NEG:
            return TRITS[POS]
        else:
            return self

    def __invert__(self):
        """Return the inverse of this Trit (same as negation)."""
        return self.__neg__()

    def __lt__(self, other):
        return (int(self) < int(other))

    def __le__(self, other):
        return (int(self) <= int(other))

    def __eq__(self, other):
        return (self.value == other.value)

    def __ne__(self, other):
        return (self.value != other.value)

    def __gt__(self, other):
        return (int(self) > int(other))

    def __ge__(self, other):
        return (int(self) >= int(other))

    def __and__(self, other):
        """Return the tritwise AND of two trits.
        
        The result is negative if either input is negative, positive if both
        inputs are positive, otherwise zero.
        """
        if NEG in (self.value, other.value):
            return TRITS[NEG]
        elif self.value == POS and other.value == POS:
            return TRITS[POS]
        else:
            return TRITS[ZERO]

    def __or__(self, other):
        """Return the tritwise OR of two trits.
        
        The result is positive if either input is positive, negative if both
        inputs are negative, otherwise zero.
        """
        if POS in (self.value, other.value):
            return TRITS[POS]
        elif self.value == NEG and other.value == NEG:
            return TRITS[NEG]
        else:
            return TRITS[ZERO]

    def __xor__(self, other):
        """Return the tritwise XOR (exclusive-OR) of two trits.

        The result is zero if either input is zero, positive if one input is
        positive and the other negative, and negative otherwise.
        """
        if ZERO in (self.value, other.value):
            return TRITS[ZERO]
        elif self.value != other.value:
            return TRITS[POS]
        else:
            return TRITS[NEG]

    def add(self, other):
        """Add two Trits and return a 2-tuple of (result, carry)."""
        carry = TRITS[ZERO]
        if self.value == ZERO:
            return (other, carry)
        elif other.value == ZERO:
            return (self, carry)
        elif self == other:
            return (-self, self)
        else:
            # Values are unequal and neither is zero, must be -1 + 1.
            return (TRITS[ZERO], carry)


class Trits(object):
    """An immutable ordered sequence of one or more trits.
    
    A Trits object may be initialised with an optional 'length' argument, in
    which case the value will be forced to have exactly 'length' trits, by
    either adding zero trits or removing trits on the left as required.  If no
    length is specified, the value will be represented using the minimum number
    of trits.

    Unless otherwise noted, when an operation returns a Trits object, it has
    whatever length is necessary to fully represent the operation's result.

    Every sequence of trits represents an integer, which is the sum of the
    integer equivalent of each trit, times 3 to the power of the trit's index,
    starting from zero in the rightmost position.  E.g.,

    For example, the trit sequence '-++' has the integer equivalent 'i' of:

    i = -1 * (3 ** 2)
      +  1 * (3 ** 1)
      +  1 * (3 ** 0)
      =  (-1 * 9) + (1 * 3) + (1 * 1)
      = -9 + 3 + 1
      = -5
    """
    def __init__(self, trits, length=None):
        if isinstance(trits, int):
            if trits == 0:
                self.trits = [TRITS[ZERO]]
            else:
                integer = trits
                self.trits = []
                power = int_order(integer) - 1
                while power >= 0:
                    if integer == 0 or int_order(integer) <= power:
                        trit = TRITS[ZERO]
                    elif integer < 0:
                        trit = TRITS[NEG]
                    else:
                        trit = TRITS[POS]
                    self.trits.append(trit)
                    integer -= int(trit) * (3 ** power)
                    power -= 1
        else:
            self.trits = [Trit.make(x) for x in trits]
        if length is not None:
            if length <= 0:
                raise ValueError(
                        "Invalid length argument '{!r}'.".format(length))
            if len(self.trits) < length:
                pad = [TRITS[ZERO]] * (length - len(self.trits))
                self.trits = pad + self.trits
            elif len(self.trits) > length:
                self.trits = self.trits[-length:]
        elif len(self.trits) == 0:
            raise ValueError(
                    "Empty trits list is invalid without a length argument.")
        self.string = ''.join([str(x) for x in self.trits])
        self.integer = 0
        for i in range(len(self)):
            if self[i] == TRITS[ZERO]:
                continue
            power = len(self) - 1 - i
            self.integer += int(self[i]) * (3 ** power)

    def __str__(self):
        return self.string

    def __repr__(self):
        return "Trits('{}')".format(self.string)

    def __hash__(self):
        return hash(self.string)

    def __len__(self):
        return len(self.trits)

    def __getitem__(self, key):
        if isinstance(key, slice):
            return Trits(self.trits[key])
        return self.trits[key]

    def __contains__(self, item):
        if isinstance(item, Trit):
            return (item in self.trits)
        else:
            return (str(item) in self.string)

    def __iter__(self):
        return iter(self.trits)

    def __int__(self):
        return self.integer

    def __oct__(self):
        return oct(int(self))

    def __hex__(self):
        return hex(int(self))


TRITS = {x: Trit(x) for x in (NEG, ZERO, POS)}


def int_order(integer):
    """Return the number of trits required to represent 'integer'."""
    return int(math.ceil(math.log(2 * abs(integer), 3)))
