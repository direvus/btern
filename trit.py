#!/usr/bin/env python
# coding=utf-8
"""
Trits and sequences of trits
============================

This module defines the Trit and Trits (Trit sequence) classes and provides for
various basic operations on these types.

A Trit is always one of the three possible basic units in balanced ternary,
-1, 0, or 1.

When performing logical operations with balanced ternary values, we use the
Kleene ternary propositional logic system, where - represents False, +
represents True, and 0 represents an indeterminate value, which is either True
or False (analogous to NULL in SQL).
"""
import numbers


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
    """A ternary digit (trit) is the basic unit of information in ternary.

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
        elif isinstance(value, numbers.Real):
            if value == 0:
                return TRIT_ZERO
            elif value > 0:
                return TRIT_POS
            else:
                return TRIT_NEG
        elif value is None:
            return TRIT_ZERO

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
        return 'Trit({!s})'.format(self)

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
            return TRIT_POS
        elif self.value == POS:
            return TRIT_NEG
        else:
            return TRIT_ZERO

    def __pos__(self):
        """Unary plus is an identity function: return the trit."""
        return self

    def __abs__(self):
        """Return the absolute value (value without any sign) of this trit.
        
        The negative trit yields the positive trit, while the positive and zero
        trits yield themselves.
        """
        if self.value == NEG:
            return TRIT_POS
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
            return TRIT_NEG
        elif self.value == POS and other.value == POS:
            return TRIT_POS
        else:
            return TRIT_ZERO

    def __or__(self, other):
        """Return the tritwise OR of two trits.
        
        The result is positive if either input is positive, negative if both
        inputs are negative, otherwise zero.
        """
        if POS in (self.value, other.value):
            return TRIT_POS
        elif self.value == NEG and other.value == NEG:
            return TRIT_NEG
        else:
            return TRIT_ZERO

    def __xor__(self, other):
        """Return the tritwise XOR (exclusive-OR) of two trits.

        The result is zero if either input is zero, positive if one input is
        positive and the other negative, and negative otherwise.
        """
        if ZERO in (self.value, other.value):
            return TRIT_ZERO
        elif self.value != other.value:
            return TRIT_POS
        else:
            return TRIT_NEG

    def add(self, other, carry=None):
        """Add two Trit objects with an optional carry-in Trit.
        
        Return a 2-tuple of Trit objects (sum, carry-out).

        This method isn't named __add__ because, having three inputs and two
        outputs, it is not appropriate for doing the work of the + operator.
        """
        if carry is None:
            carry = TRIT_ZERO
        if carry == TRIT_ZERO:
            if self.value == ZERO:
                return (other, TRIT_ZERO)
            elif other.value == ZERO:
                return (self, TRIT_ZERO)
            elif self != other:
                return (TRIT_ZERO, TRIT_ZERO)
            else:
                return (-self, self)
        elif other.value == ZERO:
            return self.add(carry)
        elif self.value == ZERO:
            return other.add(carry)
        elif self != other:
            return (carry, TRIT_ZERO)
        elif self != carry:
            return (other, TRIT_ZERO)
        else:
            return (TRIT_ZERO, self)

    def __mul__(self, other):
        """Multiply two Trit objects and return the product as a Trit.
        
        Has the opposite set of outcomes as XOR, that is:
        (a * b) == ~(a ^ b)
        """
        if self.value == ZERO or other.value == ZERO:
            return TRIT_ZERO
        elif self.value == other.value:
            return TRIT_POS
        else:
            return TRIT_NEG


TRITS = {x: Trit(x) for x in (NEG, ZERO, POS)}
TRIT_NEG  = TRITS[NEG]
TRIT_ZERO = TRITS[ZERO]
TRIT_POS  = TRITS[POS]


class Trits(object):
    """An immutable, ordered sequence of trits.
    
    The 'trits' argument must be an iterable of values which can be parsed into
    Trit objects.  'trits' may also be None, or an empty iterable, if an empty
    Trits object is desired.

    If the optional 'length' argument is given, the Trits sequence will be
    forced to have exactly 'length' trits, by either adding zero trits or
    removing trits on the left as required.

    Unless otherwise noted, binary operations on Trits objects of unequal
    length will extend the shorter operand by adding zero trits on the left to
    match the length of the longer operand.
    """
    def __init__(self, trits, length=None):
        self.trits = []
        if trits is not None:
            self.trits = [Trit.make(x) for x in trits]
        if length is not None:
            if length < 0:
                raise ValueError(
                        "Invalid length argument '{!r}'.".format(length))
            if len(self.trits) < length:
                pad = [TRIT_ZERO] * (length - len(self.trits))
                self.trits = pad + self.trits
            elif len(self.trits) > length:
                self.trits = self.trits[-length:]
        self.string = ''.join([str(x) for x in self.trits])

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

    def __neg__(self):
        return Trits([-x for x in self.trits])

    def __invert__(self):
        return -self

    def __pos__(self):
        return self

    def __abs__(self):
        """Return the numeric absolute value.
        
        This operation is on the whole Trits sequence, not on each trit
        individually, thus:

        >>> abs(Trits('+-')) # == 2
        Trits('+-')
        >>> abs(Trits('-+')) # == -2
        Trits('+-')
        """
        for t in self.trits:
            if t == TRIT_NEG:
                return -self
            elif t == TRIT_POS:
                return self
        return self

    @classmethod
    def match_length(cls, a, b):
        """Return a 2-tuple of Trits a and b each having the same length.
        
        If the two operands are of unequal length, the shorter operand is
        padded with zero trits on the left to make it the same length as the
        other.
        """
        if len(a) == len(b):
            return (a, b)
        elif len(a) < len(b):
            return (cls(a, len(b)), b)
        else:
            return (a, cls(b, len(a)))

    def __and__(self, other):
        """Return the tritwise AND of two trit sequences."""
        a, b = Trits.match_length(self, other)
        return Trits([x & y for x, y in zip(a, b)])

    def __or__(self, other):
        """Return the tritwise OR of two trit sequences."""
        a, b = Trits.match_length(self, other)
        return Trits([x | y for x, y in zip(a, b)])

    def __xor__(self, other):
        """Return the tritwise XOR of two trit sequences."""
        a, b = Trits.match_length(self, other)
        return Trits([x ^ y for x, y in zip(a, b)])

    def __add__(self, other):
        """Return the concatenation of a Trits with an iterable or Trit."""
        if isinstance(other, Trit):
            lst = [other]
        else:
            lst = list(other)
        return Trits(self.trits + lst)

    def __radd__(self, other):
        return self.__add__(other)

    def __mul__(self, other):
        """Return 'self' repeated 'other' times."""
        return Trits(self.trits * other)

    def cmp(self, other):
        a, b = Trits.match_length(self, other)
        for x, y in zip(a, b):
            if x < y:
                return -1
            elif x > y:
                return 1
        return 0

    def __lt__(self, other):
        return (self.cmp(other) < 0)

    def __le__(self, other):
        return (self.cmp(other) <= 0)

    def __eq__(self, other):
        return (self.cmp(other) == 0)

    def __ne__(self, other):
        return (self.cmp(other) != 0)

    def __gt__(self, other):
        return (self.cmp(other) > 0)

    def __ge__(self, other):
        return (self.cmp(other) >= 0)
