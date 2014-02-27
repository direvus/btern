#!/usr/bin/env python
# coding=utf-8


import unittest
import btern
from btern import Trit, NEG, ZERO, POS


class TestTrit(unittest.TestCase):
    def setUp(self):
        self.unary = [btern.TRITS[x] for x in btern.GLYPHS]
        self.binary = [(x, y) for x in self.unary for y in self.unary]

    def test_init(self):
        assert len(btern.TRITS) == 3
        assert len(btern.INTEGERS) == 3

    def test_make(self):
        trits = [Trit.make(x) for x in btern.INPUTS]
        with self.assertRaises(ValueError):
            trit = Trit.make('$')

    def test_str(self):
        assert [str(x) for x in self.unary] == [NEG, ZERO, POS]

    def test_int(self):
        assert [int(x) for x in self.unary] == [-1, 0, 1]

    def test_bool(self):
        assert [bool(x) for x in self.unary] == [False, False, True]

    def test_negate(self):
        assert [str(-x) for x in self.unary] == [POS, ZERO, NEG]

    def test_abs(self):
        assert [str(abs(x)) for x in self.unary] == [POS, ZERO, POS]

    def test_lt(self):
        assert [x < y for (x, y) in self.binary] == [
            False, True,  True,
            False, False, True,
            False, False, False]

    def test_le(self):
        assert [x <= y for (x, y) in self.binary] == [
            True,  True,  True,
            False, True,  True,
            False, False, True]

    def test_eq(self):
        assert [x == y for (x, y) in self.binary] == [
            True,  False, False,
            False, True,  False,
            False, False, True]

    def test_ne(self):
        assert [x != y for (x, y) in self.binary] == [
            False, True,  True,
            True,  False, True,
            True,  True, False]

    def test_gt(self):
        assert [x > y for (x, y) in self.binary] == [
            False, False, False,
            True,  False, False,
            True,  True,  False]

    def test_ge(self):
        assert [x >= y for (x, y) in self.binary] == [
            True,  False, False,
            True,  True,  False,
            True,  True,  True]

    def test_and(self):
        assert [str(x & y) for (x, y) in self.binary] == [
            NEG,  NEG,  NEG,
            NEG,  ZERO, ZERO,
            NEG,  ZERO, POS]

    def test_or(self):
        assert [str(x | y) for (x, y) in self.binary] == [
            NEG,  ZERO, POS,
            ZERO, ZERO, POS,
            POS,  POS,  POS]

    def test_xor(self):
        assert [str(x ^ y) for (x, y) in self.binary] == [
            NEG,  ZERO, POS,
            ZERO, ZERO, ZERO,
            POS,  ZERO, NEG]

    def test_add(self):
        assert [list(map(str, x.add(y))) for (x, y) in self.binary] == [
            [POS,  NEG ], [NEG,  ZERO], [ZERO, ZERO],
            [NEG,  ZERO], [ZERO, ZERO], [POS,  ZERO],
            [ZERO, ZERO], [POS,  ZERO], [NEG,  POS ]]
