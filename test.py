#!/usr/bin/env python
# coding=utf-8
import unittest
import string

import trit
import integer
import character
from trit import Trit, Trits, NEG, ZERO, POS, TRITS
from character import UTF6t


class TestTrit(unittest.TestCase):
    def setUp(self):
        self.unary = [TRITS[x] for x in trit.GLYPHS]
        self.binary = [(x, y) for x in self.unary for y in self.unary]

    def test_init(self):
        assert len(TRITS) == 3
        assert len(trit.INTEGERS) == 3

    def test_make(self):
        trits = [Trit.make(x) for x in trit.INPUTS]
        with self.assertRaises(ValueError):
            Trit.make('$')

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
        # Set up all possible 3-trit sequences for unary operations.
        glyphs = trit.GLYPHS
        self.length = 3
        self.unary = [Trits(x + y + z)
                for x in glyphs
                for y in glyphs
                for z in glyphs]
        # Set up a selection of various sequences for binary operations.
        seqs = (
                Trits('-'),
                Trits('0'),
                Trits('+'),
                Trits('--0+-'),
                Trits('++', 6),
                )
        self.binary = [(x, y) for x in seqs for y in seqs]

    def test_init(self):
        with self.assertRaises(ValueError):
            trits = Trits('0', -1)
        assert len(self.unary) == 3 ** self.length
        assert len(Trits('')) == 0
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

    def test_and(self):
        assert [str(x & y) for (x, y) in self.binary] == [
                '-',      '-',      '-',      '--00-',  '00000-',
                '-',      '0',      '0',      '--00-',  '000000',
                '-',      '0',      '+',      '--00-',  '00000+',
                '--00-',  '--00-',  '--00-',  '--0+-',  '0--0+-',
                '00000-', '000000', '00000+', '0--0+-', '0000++']

    def test_or(self):
        assert [str(x | y) for (x, y) in self.binary] == [
                '-',      '0',      '+',      '000+-',  '0000++',
                '0',      '0',      '+',      '000+0',  '0000++',
                '+',      '+',      '+',      '000++',  '0000++',
                '000+-',  '000+0',  '000++',  '--0+-',  '0000++',
                '0000++', '0000++', '0000++', '0000++', '0000++']

    def test_xor(self):
        assert [str(x ^ y) for (x, y) in self.binary] == [
                '-',      '0',      '+',      '0000-',  '00000+',
                '0',      '0',      '0',      '00000',  '000000',
                '+',      '0',      '-',      '0000+',  '00000-',
                '0000-',  '00000',  '0000+',  '--0--',  '0000-+',
                '00000+', '000000', '00000-', '0000-+', '0000--']

    def test_concat(self):
        # Trits + Trits concatenation
        assert [str(x + y) for (x, y) in self.binary] == [
                '--',      '-0',      '-+',      '---0+-',      '-0000++',
                '0-',      '00',      '0+',      '0--0+-',      '00000++',
                '+-',      '+0',      '++',      '+--0+-',      '+0000++',
                '--0+--',  '--0+-0',  '--0+-+',  '--0+---0+-',  '--0+-0000++',
                '0000++-', '0000++0', '0000+++', '0000++--0+-', '0000++0000++']
        # Trits + Trit concatenation
        assert [str(x + TRITS[POS]) for x in self.unary] == [
                '---+', '--0+', '--++',
                '-0-+', '-00+', '-0++',
                '-+-+', '-+0+', '-+++',
                '0--+', '0-0+', '0-++',
                '00-+', '000+', '00++',
                '0+-+', '0+0+', '0+++',
                '+--+', '+-0+', '+-++',
                '+0-+', '+00+', '+0++',
                '++-+', '++0+', '++++']
        # Trits + str concatenation
        assert [str(x + '-0+') for x in self.unary] == [
                '----0+', '--0-0+', '--+-0+',
                '-0--0+', '-00-0+', '-0+-0+',
                '-+--0+', '-+0-0+', '-++-0+',
                '0---0+', '0-0-0+', '0-+-0+',
                '00--0+', '000-0+', '00+-0+',
                '0+--0+', '0+0-0+', '0++-0+',
                '+---0+', '+-0-0+', '+-+-0+',
                '+0--0+', '+00-0+', '+0+-0+',
                '++--0+', '++0-0+', '+++-0+']
        # Bogus operand concatentation
        with self.assertRaises(TypeError):
            self.unary[0] + 1

    def test_repeat(self):
        assert [str(x * 3) for x in self.unary] == [
                '---------', '--0--0--0', '--+--+--+',
                '-0--0--0-', '-00-00-00', '-0+-0+-0+',
                '-+--+--+-', '-+0-+0-+0', '-++-++-++',
                '0--0--0--', '0-00-00-0', '0-+0-+0-+',
                '00-00-00-', '000000000', '00+00+00+',
                '0+-0+-0+-', '0+00+00+0', '0++0++0++',
                '+--+--+--', '+-0+-0+-0', '+-++-++-+',
                '+0-+0-+0-', '+00+00+00', '+0++0++0+',
                '++-++-++-', '++0++0++0', '+++++++++']

    def test_lt(self):
        assert [x < y for x, y in self.binary] == [
                False, True,  True,  False, True,
                False, False, True,  False, True,
                False, False, False, False, True,
                True,  True,  True,  False, True,
                False, False, False, False, False]

    def test_le(self):
        assert [x <= y for x, y in self.binary] == [
                True,  True,  True,  False, True,
                False, True,  True,  False, True,
                False, False, True,  False, True,
                True,  True,  True,  True,  True,
                False, False, False, False, True]

    def test_eq(self):
        assert [x == y for x, y in self.binary] == [
                True,  False, False, False, False,
                False, True,  False, False, False,
                False, False, True,  False, False,
                False, False, False, True,  False,
                False, False, False, False, True]

    def test_ne(self):
        assert [x != y for x, y in self.binary] == [
                False, True,  True,  True,  True,
                True,  False, True,  True,  True,
                True,  True,  False, True,  True,
                True,  True,  True,  False, True,
                True,  True,  True,  True,  False]

    def test_gt(self):
        assert [x > y for x, y in self.binary] == [
                False, False, False, True,  False,
                True,  False, False, True,  False,
                True,  True,  False, True,  False,
                False, False, False, False, False,
                True,  True,  True,  True,  False]

    def test_ge(self):
        assert [x >= y for x, y in self.binary] == [
                True,  False, False, True,  False,
                True,  True,  False, True,  False,
                True,  True,  True,  True,  False,
                False, False, False, True,  False,
                True,  True,  True,  True,  True]


class TestInt(unittest.TestCase):
    def setUp(self):
        self.ints = [
                0,
                1,
                -1,
                -7,
                500077,
                -2**32]

    def test_init(self):
        assert [str(integer.Int(x)) for x in self.ints] == [
                '0',
                '+',
                '-',
                '-+-',
                '+0-+++-00-+0+',
                '--+0-+-00+-+00+++++--']
        assert False not in [int(integer.Int(x)) == x for x in self.ints]


class TestUInt(unittest.TestCase):
    def setUp(self):
        self.ints = [
                0,
                1,
                500077,
                2**32]

    def test_init(self):
        assert [str(integer.UInt(x)) for x in self.ints] == [
                '-',
                '0',
                '++00-0+++0-0',
                '0-+--+-+++-0++0000+00']
        assert False not in [int(integer.UInt(x)) == x for x in self.ints]
        with self.assertRaises(ValueError):
            integer.UInt(-7)

    def test_length(self):
        assert [str(integer.UInt(x, 6)) for x in self.ints] == [
                '------',
                '-----0',
                '+++0-0',
                '000+00']


class TestUTF6t(unittest.TestCase):
    def setUp(self):
        self.strings = [
                '',
                '0',
                '~',
                string.lowercase,
                u'\u2713 \u2717',
                ]

    def test_encode(self):
        assert [str(UTF6t.encode(x)) for x in self.strings] == [
                '',
                '--0+0-',
                '-00+--',
                '-0-0+0-0-0++-0-+---0-+-0-0-+-+-0-+0-'
                '-0-+00-0-+0+-0-++--0-++0-0-+++-00---'
                '-00--0-00--+-00-0--00-00-00-0+-00-+-'
                '-00-+0-00-++-000---000-0-000-+-0000-'
                '-00000-0000+',
                '+-000+--0000--0-0++-000+--00++',
                ]

    def test_decode(self):
        assert self.strings == [
                UTF6t.decode(str(UTF6t.encode(x))) for x in self.strings]
        # Bad length
        with self.assertRaises(ValueError):
            UTF6t.decode('0000')
        # Initial at end of stream
        with self.assertRaises(ValueError):
            UTF6t.decode('+00000')
        # Continuation at beginning
        with self.assertRaises(ValueError):
            UTF6t.decode('0-----')
        # Initial without final
        with self.assertRaises(ValueError):
            UTF6t.decode('+-----+-----')
        # Continuation without initial
        with self.assertRaises(ValueError):
            UTF6t.decode('-+++++0-----')

