import pytest

from hwsim import component

from trit import ZERO, POS, NEG

TRITS = (NEG, ZERO, POS)
PAIRS = tuple((a, b) for a in TRITS for b in TRITS)


@pytest.mark.parametrize(
        "inputs,expected",
        list(zip(PAIRS, (POS, POS, POS, POS, ZERO, ZERO, POS, ZERO, NEG))))
def test_hwsim_nand(inputs, expected):
    comp = component.Nand()

    (out,) = comp.evaluate(inputs)
    assert out == expected


@pytest.mark.parametrize(
        "inputs,expected",
        list(zip(((NEG,), (ZERO,), (POS,)), (POS, ZERO, NEG))))
def test_hwsim_not(inputs, expected):
    comp = component.not_gate()

    (out,) = comp.evaluate(inputs)
    assert out == expected


@pytest.mark.parametrize(
        "inputs,expected",
        list(zip(PAIRS, (NEG, NEG, NEG, NEG, ZERO, ZERO, NEG, ZERO, POS))))
def test_hwsim_and(inputs, expected):
    comp = component.and_gate()

    (out,) = comp.evaluate(inputs)
    assert out == expected


@pytest.mark.parametrize(
        "inputs,expected",
        list(zip(PAIRS, (NEG, ZERO, POS, ZERO, ZERO, POS, POS, POS, POS))))
def test_hwsim_or(inputs, expected):
    comp = component.or_gate()

    (out,) = comp.evaluate(inputs)
    assert out == expected


@pytest.mark.parametrize(
        "inputs,expected",
        list(zip(PAIRS, (NEG, ZERO, POS, ZERO, ZERO, ZERO, POS, ZERO, NEG))))
def test_hwsim_xor(inputs, expected):
    comp = component.xor_gate()

    (out,) = comp.evaluate(inputs)
    assert out == expected
