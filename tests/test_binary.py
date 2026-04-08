import pytest

from ternary import binary
from ternary.trit import Trits


@pytest.mark.parametrize(
        "inputs,expected",
        [
            ('', b'\xf3'),
            ('-', b'\xf7\x00'),
            ('-0', b'\xf6\x01'),
            ('--+', b'\xf5\x02'),
            ('---+', b'\xf4\x02'),
            ('-----', b'\xf3\x00'),
            ('00000', b'\xf3\x79'),
            ('+++++', b'\xf3\xf2'),
            ('-0++-', b'\xf3\x33'),
            ('-0++--0++-', b'\xf3\x33\x33'),
            ('-0++-0', b'\xf7\x00\x9a'),
            (
                '-0-0+0-0-0++-0-+---0-+-0-0-+-+-0-+0',
                b'\xf3\x20\x5b\xdb\xa3\x39\x65\x22'),
            ])
def test_binary_encode(inputs, expected):
    assert binary.encode(inputs) == expected


@pytest.mark.parametrize(
        "inputs,expected",
        [
            (b'', ''),
            (b'\xf3', ''),
            (b'\x00', '-----'),
            (b'\xf3\x00', '-----'),
            (b'\x79', '00000'),
            (b'\xf2', '+++++'),
            (b'\x33', '-0++-'),
            (b'\x33\x33', '-0++--0++-'),
            (b'\x33\x01', '-0++-----0'),
            (b'\xf7\x00\x9a', '-0++-0'),
            ])
def test_binary_decode(inputs, expected):
    assert binary.decode(inputs) == Trits(expected)


@pytest.mark.parametrize("inputs", [b'\xf8', b'\xf9', b'\xfa', b'\xfb',
                                    b'\xfc', b'\xfd', b'\xfe', b'\xff'])
def test_binary_decode_err(inputs):
    with pytest.raises(ValueError):
        binary.decode(inputs)
