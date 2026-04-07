import pytest

from ternary.hardware import component, logic
from tests.util import seq_matches, N, Z, P, UNARY, BINARY, TRINARY, QUATERNARY


@pytest.mark.parametrize(
        "inputs,expected",
        list(zip(BINARY, (P, P, P, P, Z, Z, P, Z, N))))
def test_hardware_nand(inputs, expected):
    comp = component.NAnd()

    (out,) = comp.get_outputs(inputs)
    assert out == expected


@pytest.mark.parametrize(
        "inputs,expected",
        list(zip(UNARY, (P, P, N))))
def test_hardware_pnot(inputs, expected):
    comp = component.PNot()

    (out,) = comp.get_outputs(inputs)
    assert out == expected


@pytest.mark.parametrize(
        "inputs,expected",
        list(zip(UNARY, (P, N, N))))
def test_hardware_nnot(inputs, expected):
    comp = component.NNot()

    (out,) = comp.get_outputs(inputs)
    assert out == expected


@pytest.mark.parametrize(
        "inputs,expected",
        list(zip(BINARY, (P, Z, N, Z, Z, N, N, N, N))))
def test_hardware_nor(inputs, expected):
    comp = component.NOr()
    (out,) = comp.get_outputs(inputs)
    assert out == expected


@pytest.mark.parametrize(
        "inputs,expected",
        list(zip(BINARY, (P, P, Z, P, Z, N, Z, N, N))))
def test_hardware_nany(inputs, expected):
    comp = component.NAny()

    (out,) = comp.get_outputs(inputs)
    assert out == expected


@pytest.mark.parametrize(
        "inputs,expected",
        list(zip(BINARY, (
            P, Z, Z, Z, Z, Z, Z, Z, N))))
def test_hardware_ncons(inputs, expected):
    comp = component.NCons()

    (out,) = comp.get_outputs(inputs)
    assert out == expected


@pytest.mark.parametrize(
        "inputs,expected",
        list(zip(UNARY, (P, Z, N))))
def test_hardware_not(inputs, expected):
    comp = component.Not()

    (out,) = comp.get_outputs(inputs)
    assert out == expected


@pytest.mark.parametrize(
        "inputs,expected",
        list(zip(BINARY, (N, N, N, N, Z, Z, N, Z, P))))
def test_hardware_and(inputs, expected):
    comp = logic.And()

    (out,) = comp.get_outputs(inputs)
    assert out == expected


@pytest.mark.parametrize(
        "inputs,expected",
        list(zip(BINARY, (N, Z, P, Z, Z, P, P, P, P))))
def test_hardware_or(inputs, expected):
    comp = logic.Or()

    (out,) = comp.get_outputs(inputs)
    assert out == expected


@pytest.mark.parametrize(
        "inputs,expected",
        list(zip(BINARY, (N, N, Z, N, Z, P, Z, P, P))))
def test_hardware_any(inputs, expected):
    comp = logic.Any()

    (out,) = comp.get_outputs(inputs)
    assert out == expected


@pytest.mark.parametrize(
        "inputs,expected",
        list(zip(BINARY, (N, Z, P, Z, Z, Z, P, Z, N))))
def test_hardware_xor(inputs, expected):
    comp = logic.Xor()

    (out,) = comp.get_outputs(inputs)
    assert out == expected


@pytest.mark.parametrize(
        "inputs,expected",
        list(zip(BINARY, (P, Z, N, Z, Z, Z, N, Z, P))))
def test_hardware_nxor(inputs, expected):
    comp = logic.NXor()

    (out,) = comp.get_outputs(inputs)
    assert out == expected


@pytest.mark.parametrize(
        "inputs,expected",
        list(zip(UNARY, (N, P, N))))
def test_hardware_isz(inputs, expected):
    comp = logic.IsZero()

    (out,) = comp.get_outputs(inputs)
    assert out == expected


@pytest.mark.parametrize(
        "inputs,expected",
        list(zip(UNARY, (P, N, Z))))
def test_hardware_cld(inputs, expected):
    comp = logic.CycleDown()
    (out,) = comp.get_outputs(inputs)
    assert out == expected


@pytest.mark.parametrize(
        "inputs,expected",
        list(zip(UNARY, (Z, P, N))))
def test_hardware_clu(inputs, expected):
    comp = logic.CycleUp()
    (out,) = comp.get_outputs(inputs)
    assert out == expected


@pytest.mark.parametrize(
        "inputs,expected",
        list(zip(
            (
                '000000000000',
                '------------',
                '++++++++++++',
                '000---0+-00-',
                ),
            (
                tuple('000000000000'),
                tuple('++++++++++++'),
                tuple('------------'),
                tuple('000+++0-+00+'),
                ))))
def test_hardware_not12(inputs, expected):
    comp = logic.Not12()

    out = comp.get_outputs(inputs)
    assert out == expected


@pytest.mark.parametrize(
        "inputs,expected",
        list(zip(
            (
                '000000000000000000000000',
                '------------------------',
                '++++++++++++++++++++++++',
                '---000+++-0+-0+-0+-0+-0+',
                ),
            (
                tuple('000000000000'),
                tuple('------------'),
                tuple('++++++++++++'),
                tuple('----00-0+-0+'),
                ))))
def test_hardware_and12(inputs, expected):
    comp = logic.And12()

    out = comp.get_outputs(inputs)
    assert out == expected


@pytest.mark.parametrize(
        "inputs,expected",
        list(zip(QUATERNARY, (
            N, N, N, N, N, Z, N, N, P,  # a = -, b = -
            N, Z, N, N, Z, Z, N, Z, P,  # a = -, b = 0
            N, P, N, N, P, Z, N, P, P,  # a = -, b = +
            Z, N, N, Z, N, Z, Z, N, P,  # a = 0, b = -
            Z, Z, N, Z, Z, Z, Z, Z, P,  # a = 0, b = 0
            Z, P, N, Z, P, Z, Z, P, P,  # a = 0, b = +
            P, N, N, P, N, Z, P, N, P,  # a = +, b = -
            P, Z, N, P, Z, Z, P, Z, P,  # a = +, b = 0
            P, P, N, P, P, Z, P, P, P,  # a = +, b = +
            ))))
def test_hardware_mux(inputs, expected):
    comp = logic.Mux()

    (out,) = comp.get_outputs(inputs)
    assert out == expected


@pytest.mark.parametrize(
        "inputs,expected",
        list(zip(TRINARY, (
            N, N, N,  # a = -, b = -
            Z, N, Z,  # a = -, b = 0
            P, N, P,  # a = -, b = +
            N, Z, N,  # a = 0, b = -
            Z, Z, Z,  # a = 0, b = 0
            P, Z, P,  # a = 0, b = +
            N, P, N,  # a = +, b = -
            Z, P, Z,  # a = +, b = 0
            P, P, P,  # a = +, b = +
            ))))
def test_hardware_mux_2way(inputs, expected):
    comp = logic.Mux2Way()
    (out,) = comp.get_outputs(inputs)
    assert out == expected


@pytest.mark.parametrize(
        "inputs,expected",
        list(zip(BINARY, (
            (N, Z, Z),
            (Z, N, Z),
            (Z, Z, N),
            (Z, Z, Z),
            (Z, Z, Z),
            (Z, Z, Z),
            (P, Z, Z),
            (Z, P, Z),
            (Z, Z, P),
            ))))
def test_hardware_demux(inputs, expected):
    comp = logic.Demux()

    out = comp.get_outputs(inputs)
    assert out == expected


@pytest.mark.parametrize(
        "inputs,expected",
        list(zip(
            (
                ('-0+-0+-0+-0+' '+-0+-0+-0+-0' '0-+0-+0-+0-+' '-'),
                ('-0+-0+-0+-0+' '+-0+-0+-0+-0' '0-+0-+0-+0-+' '0'),
                ('-0+-0+-0+-0+' '+-0+-0+-0+-0' '0-+0-+0-+0-+' '+'),
                ),
            (
                tuple('-0+-0+-0+-0+'),
                tuple('+-0+-0+-0+-0'),
                tuple('0-+0-+0-+0-+'),
                ))))
def test_hardware_mux12(inputs, expected):
    comp = logic.Mux12()
    out = comp.get_outputs(inputs)
    assert out == expected


@pytest.mark.parametrize(
        "inputs,expected",
        list(zip(
            (
                ('-0+-0+-0+-0+' '+-0+-0+-0+-0' '-'),
                ('-0+-0+-0+-0+' '+-0+-0+-0+-0' '0'),
                ('-0+-0+-0+-0+' '+-0+-0+-0+-0' '+'),
                ),
            (
                tuple('+-0+-0+-0+-0'),
                tuple('-0+-0+-0+-0+'),
                tuple('+-0+-0+-0+-0'),
                ))))
def test_hardware_mux2way12(inputs, expected):
    comp = logic.Mux2Way12()
    out = comp.get_outputs(inputs)
    assert out == expected


@pytest.mark.parametrize(
        "inputs,expected",
        list(zip(
            (
                '------------',
                '000000000000',
                '++++++++++++',
                '---0++00-+--',
                ),
            (
                '0-----------',
                '000000000000',
                '0+++++++++++',
                '0---0++00-+-',
                ))))
def test_hardware_shift_left12(inputs, expected):
    comp = logic.ShiftLeft12()
    out = comp.get_outputs(inputs)
    assert seq_matches(out, expected)


@pytest.mark.parametrize(
        "inputs,expected",
        list(zip(
            (
                '------------',
                '000000000000',
                '++++++++++++',
                '---0++00-+--',
                ),
            (
                '-----------0',
                '000000000000',
                '+++++++++++0',
                '--0++00-+--0',
                ))))
def test_hardware_shift_right12(inputs, expected):
    comp = logic.ShiftRight12()
    out = comp.get_outputs(inputs)
    assert seq_matches(out, expected)
