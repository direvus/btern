#!/usr/bin/env python
# coding=utf-8


import unittest
import btern


class TestTrit(unittest.TestCase):
    def setUp(self):
        self.unary = [btern.Trit(x) for x in btern.ORDERING]
        self.binary = [(x, y) for x in self.unary for y in self.unary]

    def test_init(self):
        trits = [btern.Trit(x) for x in btern.INPUTS]
        with self.assertRaises(ValueError):
            trit = btern.Trit('$')

    def test_str(self):
        assert [str(x) for x in self.unary] == list(btern.ORDERING)

    def test_int(self):
        assert [int(x) for x in self.unary] == [-1, 0, 1]

    def test_bool(self):
        assert [bool(x) for x in self.unary] == [False, False, True]

    def test_negate(self):
        assert [int(-x) for x in self.unary] == [1, 0, -1]

    def test_abs(self):
        assert [int(abs(x)) for x in self.unary] == [1, 0, 1]

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
        assert [int(x & y) for (x, y) in self.binary] == [
            -1, -1, -1,
            -1,  0,  0,
            -1,  0,  1]

    def test_or(self):
        assert [int(x | y) for (x, y) in self.binary] == [
            -1,  0,  1,
             0,  0,  1,
             1,  1,  1]

    def test_xor(self):
        assert [int(x ^ y) for (x, y) in self.binary] == [
            -1,  0,  1,
             0,  0,  0,
             1,  0, -1]

    def test_add(self):
        assert [map(int, x.add(y)) for (x, y) in self.binary] == [
            [ 1, -1], [-1,  0], [ 0,  0],
            [-1,  0], [ 0,  0], [ 1,  0],
            [ 0,  0], [ 1,  0], [-1,  1]]
