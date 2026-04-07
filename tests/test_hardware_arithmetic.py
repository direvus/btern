import pytest

from ternary.hardware import arithmetic
from tests.util import N, Z, P, UNARY, BINARY, TRINARY


@pytest.mark.parametrize(
        "inputs,expected",
        list(zip(BINARY, (P, N, Z, N, Z, P, Z, P, N))))
def test_hardware_sum(inputs, expected):
    comp = arithmetic.Sum()

    out, = comp.get_outputs(inputs)
    assert out == expected


@pytest.mark.parametrize(
        "inputs,expected",
        list(zip(BINARY, (
            (P, N),
            (N, Z),
            (Z, Z),
            (N, Z),
            (Z, Z),
            (P, Z),
            (Z, Z),
            (P, Z),
            (N, P),
            ))))
def test_hardware_half_add(inputs, expected):
    comp = arithmetic.HalfAdd()

    out = comp.get_outputs(inputs)
    assert out == expected


@pytest.mark.parametrize(
        "inputs,expected",
        list(zip(TRINARY, (
            (Z, N), (P, N), (N, Z),
            (P, N), (N, Z), (Z, Z),
            (N, Z), (Z, Z), (P, Z),
            (P, N), (N, Z), (Z, Z),
            (N, Z), (Z, Z), (P, Z),
            (Z, Z), (P, Z), (N, P),
            (N, Z), (Z, Z), (P, Z),
            (Z, Z), (P, Z), (N, P),
            (P, Z), (N, P), (Z, P),
            ))))
def test_hardware_full_add(inputs, expected):
    comp = arithmetic.FullAdd()

    out = comp.get_outputs(inputs)
    assert out == expected


@pytest.mark.parametrize(
        "inputs,expected",
        list(zip(UNARY, ((Z, Z), (P, Z), (N, P)))))
def test_hardware_inc(inputs, expected):
    comp = arithmetic.Inc()

    out = comp.get_outputs(inputs)
    assert out == expected


@pytest.mark.parametrize(
        "inputs,expected",
        list(zip(UNARY, ((P, N), (N, Z), (Z, Z)))))
def test_hardware_dec(inputs, expected):
    comp = arithmetic.Dec()

    out = comp.get_outputs(inputs)
    assert out == expected


@pytest.mark.parametrize(
        "inputs,expected",
        list(zip(
            (
                '000000000000',
                '------------',
                '++++++++++++',
                ),
            (
                tuple('+00000000000'),
                tuple('0-----------'),
                tuple('------------'),
                ))))
def test_hardware_inc12(inputs, expected):
    comp = arithmetic.Inc12()

    out = comp.get_outputs(inputs)
    assert out == expected


@pytest.mark.parametrize(
        "inputs,expected",
        list(zip(
            (
                '000000000000',
                '-00000000000',
                '+00000000000',
                '--0000000000',
                '------------',
                '++++++++++++',
                ),
            (
                tuple('-00000000000'),
                tuple('+-0000000000'),
                tuple('000000000000'),
                tuple('++-000000000'),
                tuple('++++++++++++'),
                tuple('0+++++++++++'),
                ))))
def test_hardware_dec12(inputs, expected):
    comp = arithmetic.Dec12()

    out = comp.get_outputs(inputs)
    assert out == expected


@pytest.mark.parametrize(
        "inputs,expected",
        list(zip(
            (
                ('000000000000' '000000000000'),
                ('-00000000000' '+00000000000'),
                ('+00000000000' '+00000000000'),
                ('------------' '++++++++++++'),
                ),
            (
                tuple('000000000000'),
                tuple('000000000000'),
                tuple('-+0000000000'),
                tuple('000000000000'),
                ))))
def test_hardware_add12(inputs, expected):
    comp = arithmetic.Add12()

    out = comp.get_outputs(inputs)
    assert out == expected


@pytest.mark.parametrize(
        "inputs,expected",
        list(zip(BINARY, (N, N, N, N, Z, P, P, P, P))))
def test_hardware_comparator(inputs, expected):
    comp = arithmetic.Comparator()

    (out,) = comp.get_outputs(inputs)
    assert out == expected


@pytest.mark.parametrize(
        "inputs,expected",
        list(zip(
            (
                '000000000000',
                '-00000000000',
                '+00000000000',
                '00000000000-',
                '00000000000+',
                '00000-000000',
                '00000000+000',
                '+++++++++++-',
                '-----------+',
                ),
            (
                '0',
                '-',
                '+',
                '-',
                '+',
                '-',
                '+',
                '-',
                '+',
                ))))
def test_hardware_comparator12(inputs, expected):
    comp = arithmetic.Comparator12()

    (out,) = comp.get_outputs(inputs)
    assert out == expected
