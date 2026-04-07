import pytest

from ternary.hardware import util


@pytest.mark.parametrize(
        "inputs,expected",
        list(zip(
            (
                '-',
                '0',
                '+',
                '--',
                '-0',
                '-+',
                '-++',
                '---+',
                ),
            (
                -1,
                0,
                1,
                -4,
                -1,
                2,
                11,
                14,
                ))))
def test_hardware_trits_to_int(inputs, expected):
    out = util.trits_to_int(inputs)
    assert out == expected


@pytest.mark.parametrize(
        "inputs,expected",
        list(zip(
            (
                (-1, 1),
                (0, 1),
                (1, 1),
                (-4, 2),
                (-1, 2),
                (2, 2),
                (11, 3),
                (14, 4),
                ),
            (
                '-',
                '0',
                '+',
                '--',
                '-0',
                '-+',
                '-++',
                '---+',
                ))))
def test_hardware_int_to_trits(inputs, expected):
    out = util.int_to_trits(*inputs)
    assert out == expected


@pytest.mark.parametrize(
        "inputs",
        [
            (1, 0),
            (1, -1),
            (2, 1),
            (1e8, 12),
            ])
def test_hardware_int_to_trits_err(inputs):
    with pytest.raises(ValueError):
        util.int_to_trits(*inputs)
