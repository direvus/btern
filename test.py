#!/usr/bin/env python
# coding=utf-8


import unittest
import btern
from btern import Trit, Trits, NEG, ZERO, POS, TRITS


class TestTrit(unittest.TestCase):
    def setUp(self):
        self.unary = [TRITS[x] for x in btern.GLYPHS]
        self.binary = [(x, y) for x in self.unary for y in self.unary]

    def test_init(self):
        assert len(TRITS) == 3
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


class TestTrits(unittest.TestCase):
    def setUp(self):
        # Set up all possible 3-trit sequences:
        glyphs = btern.GLYPHS
        self.length = 3
        self.unary = [Trits(x + y + z)
                for x in glyphs
                for y in glyphs
                for z in glyphs]

    def test_init(self):
        with self.assertRaises(ValueError):
            trits = Trits('')
        with self.assertRaises(ValueError):
            trits = Trits('0', 0)
        assert len(self.unary) == 3 ** self.length
        assert str(Trits('', 4)) == '0000'
        assert str(Trits('+', 4)) == '000+'
        assert str(Trits('---0', 2)) == '-0'
        assert [i for i in range(-100, 100) if int(Trits(i)) != i] == []

    def test_str(self):
        assert [str(x) for x in self.unary] == [
                '---', '--0', '--+', '-0-', '-00', '-0+', '-+-', '-+0', '-++',
                '0--', '0-0', '0-+', '00-', '000', '00+', '0+-', '0+0', '0++',
                '+--', '+-0', '+-+', '+0-', '+00', '+0+', '++-', '++0', '+++']

    def test_len(self):
        assert [len(x) for x in self.unary] == [3] * len(self.unary)
        assert len(Trits('', 8)) == 8
        assert len(Trits('----', 1)) == 1

    def test_index(self):
        assert [str(x[0]) for x in self.unary] == [
                '-', '-', '-', '-', '-', '-', '-', '-', '-',
                '0', '0', '0', '0', '0', '0', '0', '0', '0',
                '+', '+', '+', '+', '+', '+', '+', '+', '+']
        assert [str(x[-1]) for x in self.unary] == [
                '-', '0', '+', '-', '0', '+', '-', '0', '+',
                '-', '0', '+', '-', '0', '+', '-', '0', '+',
                '-', '0', '+', '-', '0', '+', '-', '0', '+']
        with self.assertRaises(IndexError):
            self.unary[0][3]
        with self.assertRaises(TypeError):
            self.unary[0]['a']

    def test_slice(self):
        assert [str(x[:2]) for x in self.unary] == [
                '--', '--', '--', '-0', '-0', '-0', '-+', '-+', '-+',
                '0-', '0-', '0-', '00', '00', '00', '0+', '0+', '0+',
                '+-', '+-', '+-', '+0', '+0', '+0', '++', '++', '++']
        assert [str(x[1:]) for x in self.unary] == [
                '--', '-0', '-+', '0-', '00', '0+', '+-', '+0', '++',
                '--', '-0', '-+', '0-', '00', '0+', '+-', '+0', '++',
                '--', '-0', '-+', '0-', '00', '0+', '+-', '+0', '++']
        assert [str(x[0:3:2]) for x in self.unary] == [
                '--', '-0', '-+', '--', '-0', '-+', '--', '-0', '-+',
                '0-', '00', '0+', '0-', '00', '0+', '0-', '00', '0+',
                '+-', '+0', '++', '+-', '+0', '++', '+-', '+0', '++']

    def test_contains(self):
        assert [('-' in x) for x in self.unary] == [
                True, True, True, True, True,  True,  True, True,  True,
                True, True, True, True, False, False, True, False, False,
                True, True, True, True, False, False, True, False, False]
        assert [(TRITS[POS] in x) for x in self.unary] == [
                False, False, True,  False, False, True, True, True, True,
                False, False, True,  False, False, True, True, True, True,
                True,  True,  True,  True,  True,  True, True, True, True]

    def test_iteration(self):
        assert [x for x in self.unary[5]] == [
                TRITS[NEG], TRITS[ZERO], TRITS[POS]]

    def test_immutability(self):
        with self.assertRaises(TypeError):
            self.unary[0][0] = TRITS[POS]

    def test_int(self):
        assert [int(x) for x in self.unary] == list(range(-13, 14))

    def test_neg(self):
        assert [str(-x) for x in self.unary] == [
                '+++', '++0', '++-', '+0+', '+00', '+0-', '+-+', '+-0', '+--',
                '0++', '0+0', '0+-', '00+', '000', '00-', '0-+', '0-0', '0--',
                '-++', '-+0', '-+-', '-0+', '-00', '-0-', '--+', '--0', '---']

    def test_pos(self):
        assert [str(+x) for x in self.unary] == [
                '---', '--0', '--+', '-0-', '-00', '-0+', '-+-', '-+0', '-++',
                '0--', '0-0', '0-+', '00-', '000', '00+', '0+-', '0+0', '0++',
                '+--', '+-0', '+-+', '+0-', '+00', '+0+', '++-', '++0', '+++']

    def test_abs(self):
        assert [str(abs(x)) for x in self.unary] == [
                '+++', '++0', '++-', '+0+', '+00', '+0-', '+-+', '+-0', '+--',
                '0++', '0+0', '0+-', '00+', '000', '00+', '0+-', '0+0', '0++',
                '+--', '+-0', '+-+', '+0-', '+00', '+0+', '++-', '++0', '+++']

