#!/usr/bin/env python
# coding=utf-8
"""
Balanced ternary binary encoding
============

Tools for encoding balanced ternary data into binary formats and back again.

This encoding scheme has a one byte header, followed by zero or more data
bytes. Each data byte encodes the value of a 5-trit ternary segment, by taking
its value as an unsigned integer.

So, for example, consider the trit sequence:

    0-00+

This sequence interpreted as a signed number is decimal -70, and as an unsigned
number decimal 51.  We encode it using the byte value 51, or hex 0x33, which
gives:

    0011 0011

If the trit sequence being encoded is not evenly divisible into 5-trit
segments, the sequence is padded to by adding '-' trits to the start. The
header byte is equal to the number of padding trits that were added, plus 243:

| header | hex    | padding |
| ----   | ----   | ----    |
|    243 | `0xf3` |       0 |
|    244 | `0xf4` |       1 |
|    245 | `0xf5` |       2 |
|    246 | `0xf6` |       3 |
|    247 | `0xf7` |       4 |

"""
from ternary import integer, trit


def encode(source) -> bytes:
    mod = len(source) % 5
    padding = 5 - mod if mod else 0
    header = 243 + padding
    result = bytearray((header,))
    data = '-' * padding + source
    for i in range(0, len(data), 5):
        value = integer.UInt(data[i:i+5])
        result.append(int(value))
    return bytes(result)


def decode(source) -> trit.Trits:
    result = []
    binary = bytearray(source)

    length = 5
    for i in range(len(binary)):
        value = binary[i]
        if value > 247:
            raise ValueError(
                    "Invalid byte at position {}: {:#02x}".format(i, value))

        if value > 242:
            # Header byte, remove padding from next byte
            length = 5 - (value - 243)
            continue

        result.extend(integer.UInt(value, length))
        # Reset the length
        length = 5
    return trit.Trits(result)
