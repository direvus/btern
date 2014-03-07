#!/usr/bin/env python
# coding=utf-8
"""
Balanced ternary character strings
============

Strings in balanced ternary are sequences of code points in the Unicode
Character Set (UCS).  This module provides one particular method of mapping
these code points to sequences of balanced ternary digits (trits), called
*Unicode Transformation Format - 6-trit* (UTF-6t).

UTF-6t
------

UTF-6t is based heavily on UTF-8.  It shares most of the features of UTF-8 and
has a very similar structure.

A UTF-6t value is made up of one or more trytes of 6 trits each.  Each tryte
consists of one trit of metadata, followed by five trits of code point data.
Thus, a maximum of four trytes (24 trits with 4 metadata trits and 20 data
trits) are required to represent all 2,147,483,648 code points in the Unicode
Character Set.  A maximum of three trytes are required to represent code points
up to 0x10FFFF (1114111), which is the limit of UTF-16, also enforced for
UTF-8.

The first trit of each tryte indicates whether the tryte is:
  * the final (or only) tryte of a value (-),
  * a continuation tryte in a multi-tryte value (0), or
  * the initial tryte of a multi-tryte value (+).

The remaining five trits of each tryte are data trits which, when taken
together and interpreted as an unsigned integer, encode one Unicode code point.

      Code points       Data trits             Layout
       0 -        243            5                        -xxxxx
     244 -      59049           10                 +xxxxx -xxxxx
   59050 -   14348907           15          +xxxxx 0xxxxx -xxxxx
14348908 - 3486784401           20   +xxxxx 0xxxxx 0xxxxx -xxxxx

As with UTF-8, not all sequences of trits are valid UTF-6t encodings:
  * A final tryte (-) may never be followed directly by a continuation tryte
    (0).  The last tryte in a sequence must always be a final tryte.
  * An initial tryte (+) must always be followed by either a continuation
    tryte (0) or a final tryte (-).
  * A continuation tryte (0) must always be followed by either another
    continuation tryte or a final tryte (-).  It must never be the first tryte
    of a character.

Comparison with UTF-8
---------------------

UTF-6t has most of the features of UTF-8: it uses only one tryte with a leading
negative to represent the whole ASCII character set, and therefore all valid
ASCII sequences using 6 unsigned trits per character are valid UTF-6t sequences
with equivalent meaning.  UTF-6t is self-synchronising, and a tritwise sort
will yield values in their code point order.

The main difference between UTF-6t and UTF-8 is that the first byte of a UTF-8
sequence indicates the number of bytes remaining in the value, allowing a
decoder to know the byte width of the character prior to examining the
continuation bytes.  UTF-6t does not have this (admittedly useful) property,
and consequently there are certain failure modes we cannot detect.  For
example, if an entire continuation tryte were missing from a multi-tryte value,
it would appear to be a correct (but very different) value.  On the other hand,
UTF-8 cannot represent a code point with more than 31 bits, whereas UTF-6t can
be extended indefinitely by simply adding more continuation trytes.
"""
from __future__ import division
import math
import numbers

import trit
import integer


class UTF6t(trit.Trits):
    INITIAL  = trit.POS
    CONTINUE = trit.ZERO
    FINAL    = trit.NEG
    LEAD_SIZE  = 1
    DATA_SIZE  = 5
    TRYTE_SIZE = 6

    @classmethod
    def encode(cls, chars):
        """Return 'chars' encoded as a UTF-6t sequence of trits.

        'chars' must be iterable, and its elements may be standard string
        characters, unicode characters, or integer code points.
        """
        trits = ''
        for char in chars:
            if isinstance(char, numbers.Integral):
                code = char
            elif isinstance(char, basestring):
                code = ord(char)
            else:
                raise ValueError(
                        "Cannot parse {!r} as a unicode character.".format(
                            char))
            uint = str(integer.UInt(code))
            padding = (cls.DATA_SIZE - len(uint)) % cls.DATA_SIZE
            uint = (trit.NEG * padding) + uint
            length = len(uint)
            for i in range(0, length, cls.DATA_SIZE):
                if i == length - cls.DATA_SIZE:
                    lead = cls.FINAL
                elif i == 0:
                    lead = cls.INITIAL
                else:
                    lead = trit.CONTINUE
                trits += lead + uint[i:i + cls.DATA_SIZE]
        return cls(trits)

    @classmethod
    def decode(cls, trits):
        """Return the string value from UTF-6t encoded 'trits'.
        
        'trits' can be a UTF6t instance, or any other iterable of trits.  Each
        element of the iterable must be a Trit instance, or something which is
        coerceable to Trit.

        If 'trits' is not a valid UTF-6t encoded sequence, raise a ValueError.
        """
        result = u''
        if len(trits) == 0:
            return result
        elif len(trits) % cls.TRYTE_SIZE != 0:
            raise ValueError(
                    "Cannot decode sequence of length {} as UTF-6t: "
                    "must be a multiple of {}.".format(
                        len(trits), cls.TRYTE_SIZE))
        code = []
        for i in range(0, len(trits), cls.TRYTE_SIZE):
            t = trits[i]
            if not isinstance(t, trit.Trit):
                t = trit.Trit.make(t)
            lead = str(t)
            data = list(trits[i + cls.LEAD_SIZE:i + cls.TRYTE_SIZE])
            if lead == cls.FINAL:
                result += unichr(int(integer.UInt(code + data)))
                code = []
            else:
                if lead == cls.CONTINUE and len(code) == 0:
                    raise ValueError(
                            "Invalid UTF-6t sequence: unexpected continuation "
                            "tryte at offset {}.".format(i))
                if lead == cls.INITIAL and len(code) != 0:
                    raise ValueError(
                            "Invalid UTF-6t sequence: unexpected initial "
                            "tryte at offset {}.".format(i))
                code += data
        if len(code) != 0:
            raise ValueError(
                    "Invalid UTF-6t sequence: unterminated multi-tryte "
                    "character at end of sequence.".format(i))
        return result
