#!/usr/bin/env python
# coding=utf-8
"""
Balanced ternary binary encoding
============

Tools for encoding balanced ternary data into binary formats and back again.

The encoding scheme used here uses 8-bit segments to represent 5-trit segments.
Each 5-trit segment is mapped to an 8-bit binary value which corresponds to its
value as an unsigned integer.

So, for example, consider the trit sequence:

    0-00+

This sequence interpreted as a signed number is decimal -70, and as an unsigned
number decimal 51.  We encode it using the byte value 51, or hex 0x33, which
gives:

    0011 0011

If a trit sequence is not evenly divisible into 5-trit segments, the final
segment is padded to 5 trits by adding '-' trits to the left.
"""
import integer
import trit


def encode(source):
    result = bytearray()
    for i in range(0, len(source), 5):
        value = integer.UInt(source[i:i+5], 5)
        result.append(int(value))
    return bytes(result)


def decode(source):
    result = trit.Trits('')
    binary = bytearray(source)
    for i in range(len(binary)):
        value = binary[i]
        if value > 242:
            raise ValueError(
                    "Invalid byte at position {}: {:#02x}".format(i, value))
        result += integer.UInt(value, 5)
    return result
