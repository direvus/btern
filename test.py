#!/usr/bin/env python
# coding=utf-8
import unittest
import string

from . import trit, integer, character
from .trit import Trit, Trits, GLYPHS, NEG, ZERO, POS
from .trit import TRITS, TRIT_NEG, TRIT_ZERO, TRIT_POS
from .integer import Int, UInt
from .character import UTF6t
from .processor import Register


# The set of all possible 3-trit sequences
TRIPLETS = [Trits([x, y, z]) for x in GLYPHS for y in GLYPHS for z in GLYPHS]


class TestTrit(unittest.TestCase):
    def setUp(self):
        self.unary = [TRITS[x] for x in trit.GLYPHS]
        self.binary = [(x, y) for x in self.unary for y in self.unary]
        self.ternary = [(x, y, z) for x, y in self.binary for z in self.unary]

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
        assert [tuple(map(str, x.add(y, z))) for x, y, z in self.ternary] == [
            ('0', '-'), ('+', '-'), ('-', '0'),
            ('+', '-'), ('-', '0'), ('0', '0'),
            ('-', '0'), ('0', '0'), ('+', '0'),
            ('+', '-'), ('-', '0'), ('0', '0'),
            ('-', '0'), ('0', '0'), ('+', '0'),
            ('0', '0'), ('+', '0'), ('-', '+'),
            ('-', '0'), ('0', '0'), ('+', '0'),
            ('0', '0'), ('+', '0'), ('-', '+'),
            ('+', '0'), ('-', '+'), ('0', '+')]

    def test_mul(self):
        assert [str(x * y) for x, y in self.binary] == [
                POS,  ZERO, NEG,
                ZERO, ZERO, ZERO,
                NEG,  ZERO, POS]


class TestTrits(unittest.TestCase):
    def setUp(self):
        # Set up all possible 3-trit sequences for unary operations.
        self.length = 3
        self.unary = TRIPLETS
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
        assert [(TRIT_POS in x) for x in self.unary] == [
                False, False, True,  False, False, True, True, True, True,
                False, False, True,  False, False, True, True, True, True,
                True,  True,  True,  True,  True,  True, True, True, True]

    def test_iteration(self):
        assert [x for x in self.unary[5]] == [TRIT_NEG, TRIT_ZERO, TRIT_POS]

    def test_immutability(self):
        with self.assertRaises(TypeError):
            self.unary[0][0] = TRIT_POS

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

    def test_trim(self):
        assert [str(x.trim()) for x in self.unary] == [
                '---', '--0', '--+', '-0-', '-00', '-0+', '-+-', '-+0', '-++',
                '--',   '-0',  '-+',   '-',    '',   '+',  '+-',  '+0',  '++',
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
        assert [str(x + TRIT_POS) for x in self.unary] == [
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
        self.unary = [
                0,
                1,
                -1,
                -7,
                500077,
                -2**32]
        self.binary = [(x, y) for x in self.unary for y in self.unary]

    def test_init(self):
        assert [str(Int(x)) for x in self.unary] == [
                '0',
                '+',
                '-',
                '-+-',
                '+0-+++-00-+0+',
                '--+0-+-00+-+00+++++--']
        assert False not in [int(Int(x)) == x for x in self.unary]

    def test_int(self):
        assert [int(Int(x)) for x in TRIPLETS] == list(range(-13, 14))
        assert False not in [
                int(Int(x)) == x for x in range(-100, 100)]

    def test_abs(self):
        assert [str(abs(Int(x))) for x in TRIPLETS] == [
                '+++', '++0', '++-', '+0+', '+00', '+0-', '+-+', '+-0', '+--',
                '0++', '0+0', '0+-', '00+', '000', '00+', '0+-', '0+0', '0++',
                '+--', '+-0', '+-+', '+0-', '+00', '+0+', '++-', '++0', '+++']

    def test_add(self):
        assert [int(Int(x) + Int(y)) for x, y in self.binary] == [
                x + y for x, y in self.binary]

    def test_sub(self):
        assert [int(Int(x) - Int(y)) for x, y in self.binary] == [
                x - y for x, y in self.binary]

    def test_mul(self):
        assert [int(Int(x) * Int(y)) for x, y in self.binary] == [
                x * y for x, y in self.binary]

    def test_div(self):
        with self.assertRaises(ZeroDivisionError):
            Int(1) // Int(0)
        ints = range(-5, 6)
        ops = [(x, y) for x in ints for y in ints if y != 0]
        quotients = [Int(int(x.__truediv__(y))) for x, y in ops]
        remains = [Int(x - (y * int(x.__truediv__(y)))) for x, y in ops]
        divmods = list(zip(quotients, remains))
        assert [Int(x) // Int(y) for x, y in ops] == quotients
        assert [Int(x) % Int(y) for x, y in ops] == remains
        assert [divmod(Int(x), Int(y)) for x, y in ops] == divmods


class TestUInt(unittest.TestCase):
    def setUp(self):
        self.ints = [
                0,
                1,
                500077,
                2**32]

    def test_init(self):
        assert [str(UInt(x)) for x in self.ints] == [
                '-',
                '0',
                '++00-0+++0-0',
                '0-+--+-+++-0++0000+00']
        assert False not in [int(UInt(x)) == x for x in self.ints]
        with self.assertRaises(ValueError):
            UInt(-7)

    def test_length(self):
        assert [str(UInt(x, 6)) for x in self.ints] == [
                '------',
                '-----0',
                '+++0-0',
                '000+00']

    def test_int(self):
        assert [int(UInt(x)) for x in TRIPLETS] == list(range(27))

    def test_abs(self):
        assert [abs(UInt(x)) for x in TRIPLETS] == [UInt(x) for x in TRIPLETS]


class TestUTF6t(unittest.TestCase):
    def setUp(self):
        self.strings = [
                '',
                '0',
                '~',
                string.ascii_lowercase,
                u'\u2713 \u2717',
                ]

    def test_encode(self):
        assert [str(Trits(UTF6t.encode(x))) for x in self.strings] == [
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
        # Bogus element type
        with self.assertRaises(TypeError):
            UTF6t.encode([None])
        with self.assertRaises(TypeError):
            UTF6t.encode([3.14159])

    def test_decode(self):
        assert self.strings == [
                UTF6t.decode(UTF6t.encode(x)) for x in self.strings]
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


class TestRegister(unittest.TestCase):
    def setUp(self):
        self.unary = [Register(x, 3) for x in TRIPLETS]

    def test_init(self):
        with self.assertRaises(TypeError):
            Register([], None)
        with self.assertRaises(ValueError):
            Register([], 0)
        assert len(str(Register([], 6))) == 6

    def test_set(self):
        r = Register([], 6)
        # Assignment to out-of-range index
        with self.assertRaises(IndexError):
            r[6] = TRIT_POS
        # Slice assignment that would alter the sequence length
        with self.assertRaises(ValueError):
            r[:] = [TRIT_POS]

        r[0] = TRIT_POS; assert str(r) == '+00000'
        r[-1] = TRIT_NEG; assert str(r) == '+0000-'
        r[-2:] = '-0'; assert str(r) == '+000-0'
        r[:3] = '-+-'; assert str(r) == '-+-0-0'
        r[:] = '000+++'; assert str(r) == '000+++'
        r[2:4] = '--'; assert str(r) == '00--++'
