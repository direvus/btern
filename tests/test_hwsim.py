import pytest

from hwsim import component, arithmetic, logic, cpu, memory
from trit import ZERO, POS, NEG


N = NEG
Z = ZERO
P = POS
TRITS = (NEG, ZERO, POS)
UNARY = tuple((a,) for a in TRITS)
BINARY = tuple((a, b) for a in TRITS for b in TRITS)
TRINARY = tuple((a, b, c) for a in TRITS for b in TRITS for c in TRITS)
QUATERNARY = tuple((a, b, c, d)
                   for a in TRITS
                   for b in TRITS
                   for c in TRITS
                   for d in TRITS)


@pytest.mark.parametrize(
        "inputs,expected",
        list(zip(BINARY, (POS, POS, POS, POS, ZERO, ZERO, POS, ZERO, NEG))))
def test_hwsim_nand(inputs, expected):
    comp = component.NAnd()

    (out,) = comp.get_outputs(inputs)
    assert out == expected


@pytest.mark.parametrize(
        "inputs,expected",
        list(zip(UNARY, (POS, POS, NEG))))
def test_hwsim_pnot(inputs, expected):
    comp = component.PNot()

    (out,) = comp.get_outputs(inputs)
    assert out == expected


@pytest.mark.parametrize(
        "inputs,expected",
        list(zip(UNARY, (POS, NEG, NEG))))
def test_hwsim_nnot(inputs, expected):
    comp = component.NNot()

    (out,) = comp.get_outputs(inputs)
    assert out == expected


@pytest.mark.parametrize(
        "inputs,expected",
        list(zip(BINARY, (POS, POS, ZERO, POS, ZERO, NEG, ZERO, NEG, NEG))))
def test_hwsim_nany(inputs, expected):
    comp = component.NAny()

    (out,) = comp.get_outputs(inputs)
    assert out == expected


@pytest.mark.parametrize(
        "inputs,expected",
        list(zip(BINARY, (
            POS, ZERO, ZERO, ZERO, ZERO, ZERO, ZERO, ZERO, NEG))))
def test_hwsim_ncons(inputs, expected):
    comp = component.NCons()

    (out,) = comp.get_outputs(inputs)
    assert out == expected


@pytest.mark.parametrize(
        "inputs,expected",
        list(zip(UNARY, (POS, ZERO, NEG))))
def test_hwsim_not(inputs, expected):
    comp = component.Not()

    (out,) = comp.get_outputs(inputs)
    assert out == expected


@pytest.mark.parametrize(
        "inputs,expected",
        list(zip(BINARY, (NEG, NEG, NEG, NEG, ZERO, ZERO, NEG, ZERO, POS))))
def test_hwsim_and(inputs, expected):
    comp = logic.And()

    (out,) = comp.get_outputs(inputs)
    assert out == expected


@pytest.mark.parametrize(
        "inputs,expected",
        list(zip(BINARY, (NEG, ZERO, POS, ZERO, ZERO, POS, POS, POS, POS))))
def test_hwsim_or(inputs, expected):
    comp = logic.Or()

    (out,) = comp.get_outputs(inputs)
    assert out == expected


@pytest.mark.parametrize(
        "inputs,expected",
        list(zip(BINARY, (NEG, NEG, ZERO, NEG, ZERO, POS, ZERO, POS, POS))))
def test_hwsim_any(inputs, expected):
    comp = logic.Any()

    (out,) = comp.get_outputs(inputs)
    assert out == expected


@pytest.mark.parametrize(
        "inputs,expected",
        list(zip(BINARY, (NEG, ZERO, POS, ZERO, ZERO, ZERO, POS, ZERO, NEG))))
def test_hwsim_xor(inputs, expected):
    comp = logic.Xor()

    (out,) = comp.get_outputs(inputs)
    assert out == expected


@pytest.mark.parametrize(
        "inputs,expected",
        list(zip(BINARY, (POS, ZERO, NEG, ZERO, ZERO, ZERO, NEG, ZERO, POS))))
def test_hwsim_nxor(inputs, expected):
    comp = logic.NXor()

    (out,) = comp.get_outputs(inputs)
    assert out == expected


@pytest.mark.parametrize(
        "inputs,expected",
        list(zip(UNARY, (NEG, POS, NEG))))
def test_hwsim_isz(inputs, expected):
    comp = logic.IsZero()

    (out,) = comp.get_outputs(inputs)
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
def test_hwsim_mux(inputs, expected):
    comp = logic.Mux()

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
def test_hwsim_demux(inputs, expected):
    comp = logic.Demux()

    out = comp.get_outputs(inputs)
    assert out == expected


@pytest.mark.parametrize(
        "inputs,expected",
        list(zip(BINARY, (POS, NEG, ZERO, NEG, ZERO, POS, ZERO, POS, NEG))))
def test_hwsim_sum(inputs, expected):
    comp = arithmetic.Sum()

    out, = comp.get_outputs(inputs)
    assert out == expected


@pytest.mark.parametrize(
        "inputs,expected",
        list(zip(BINARY, (
            (POS, NEG),
            (NEG, ZERO),
            (ZERO, ZERO),
            (NEG, ZERO),
            (ZERO, ZERO),
            (POS, ZERO),
            (ZERO, ZERO),
            (POS, ZERO),
            (NEG, POS),
            ))))
def test_hwsim_half_add(inputs, expected):
    comp = arithmetic.HalfAdd()

    out = comp.get_outputs(inputs)
    assert out == expected


@pytest.mark.parametrize(
        "inputs,expected",
        list(zip(TRINARY, (
            (ZERO, NEG), (POS, NEG), (NEG, ZERO),
            (POS, NEG), (NEG, ZERO), (ZERO, ZERO),
            (NEG, ZERO), (ZERO, ZERO), (POS, ZERO),
            (POS, NEG), (NEG, ZERO), (ZERO, ZERO),
            (NEG, ZERO), (ZERO, ZERO), (POS, ZERO),
            (ZERO, ZERO), (POS, ZERO), (NEG, POS),
            (NEG, ZERO), (ZERO, ZERO), (POS, ZERO),
            (ZERO, ZERO), (POS, ZERO), (NEG, POS),
            (POS, ZERO), (NEG, POS), (ZERO, POS),
            ))))
def test_hwsim_full_add(inputs, expected):
    comp = arithmetic.FullAdd()

    out = comp.get_outputs(inputs)
    assert out == expected


@pytest.mark.parametrize(
        "inputs,expected",
        list(zip(UNARY, ((ZERO, ZERO), (POS, ZERO), (NEG, POS)))))
def test_hwsim_inc(inputs, expected):
    comp = arithmetic.Inc()

    out = comp.get_outputs(inputs)
    assert out == expected


@pytest.mark.parametrize(
        "inputs,expected",
        list(zip(UNARY, ((POS, NEG), (NEG, ZERO), (ZERO, ZERO)))))
def test_hwsim_dec(inputs, expected):
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
                '000---0+-00-',
                ),
            (
                tuple('000000000000'),
                tuple('++++++++++++'),
                tuple('------------'),
                tuple('000+++0-+00+'),
                ))))
def test_hwsim_not12(inputs, expected):
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
def test_hwsim_and12(inputs, expected):
    comp = logic.And12()

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
def test_hwsim_inc12(inputs, expected):
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
def test_hwsim_dec12(inputs, expected):
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
def test_hwsim_add12(inputs, expected):
    comp = arithmetic.Add12()

    out = comp.get_outputs(inputs)
    assert out == expected


@pytest.mark.parametrize(
        "inputs,expected",
        list(zip(BINARY, (NEG, NEG, NEG, NEG, ZERO, POS, POS, POS, POS))))
def test_hwsim_comparator(inputs, expected):
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
def test_hwsim_comparator12(inputs, expected):
    comp = arithmetic.Comparator12()

    (out,) = comp.get_outputs(inputs)
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
def test_hwsim_mux12(inputs, expected):
    comp = logic.Mux12()

    out = comp.get_outputs(inputs)
    assert out == expected


@pytest.mark.parametrize(
        "inputs,expected",
        list(zip(
            (
                ('-0+-0+-0+-0+' '+-0+-0+-0+-0' '0++'),
                ('-0+-0+-0+-0+' '+-0+-0+-0+-0' '+++'),
                ('-0+-0+-0+-0+' '+-0+-0+-0+-0' '++0'),
                ('-0+-0+-0+-0+' '+-0+-0+-0+-0' '+-0'),
                ('-0+-0+-0+-0+' '+-0+-0+-0+-0' '+0+'),
                ('-0+-0+-0+-0+' '+-0+-0+-0+-0' '-++'),
                ('-0+-0+-0+-0+' '+-0+-0+-0+-0' '+-+'),
                ('-0+-0+-0+-0+' '+-0+-0+-0+-0' '00+'),
                ('-0+-0+-0+-0+' '+-0+-0+-0+-0' '--+'),
                ('-0+-0+-0+-0+' '+-0+-0+-0+-0' '00-'),
                ('-0+-0+-0+-0+' '+-0+-0+-0+-0' '---'),
                ),
            (
                tuple('-0+-0+-0+-0+'),  # x
                tuple('000000000000'),  # 0
                tuple('+00000000000'),  # 1
                tuple('-00000000000'),  # -1
                tuple('+-0+-0+-0+-0'),  # y
                tuple('+0-+0-+0-+0-'),  # -x
                tuple('-+0-+0-+0-+0'),  # -y
                tuple('0-+0-+0-+0-+'),  # x + y
                tuple('0+-0+-0+-0+-'),  # -x - y
                tuple('--0--0--0--0'),  # x & y
                tuple('-0--0--0--0-'),  # -x & -y
                ))))
def test_hwsim_alu(inputs, expected):
    comp = cpu.ALU()

    out = comp.get_outputs(inputs)
    assert out == expected


@pytest.mark.parametrize(
        "inputs,expected",
        list(zip(TRINARY, (
                NEG, ZERO, POS,
                NEG, ZERO, POS,
                NEG, ZERO, POS,
                NEG, ZERO, POS,
                NEG, ZERO, POS,
                NEG, ZERO, POS,
                NEG, ZERO, POS,
                NEG, ZERO, POS,
                NEG, ZERO, POS,
                ))))
def test_hwsim_dff_setup(inputs, expected):
    comp = memory.DataFlipFlop()

    load, inp, state = inputs
    comp.state = state
    (out,) = comp.get_outputs((load, inp))
    assert out == expected


@pytest.mark.parametrize(
        "inputs,expected",
        list(zip(TRINARY, (
                NEG, NEG, NEG,
                ZERO, ZERO, ZERO,
                POS, POS, POS,
                NEG, ZERO, POS,
                NEG, ZERO, POS,
                NEG, ZERO, POS,
                NEG, NEG, NEG,
                ZERO, ZERO, ZERO,
                POS, POS, POS,
                ))))
def test_hwsim_dff_update_state(inputs, expected):
    comp = memory.DataFlipFlop()

    load, inp, state = inputs
    comp.state = state
    comp.set_inputs((load, inp))
    comp.update()
    (out,) = comp.get_outputs((load, inp))
    assert out == expected


@pytest.mark.parametrize(
        "inputs,expected",
        list(zip(TRINARY, (
                True, True, True,
                True, True, True,
                True, True, True,
                False, False, False,
                False, False, False,
                False, False, False,
                True, True, True,
                True, True, True,
                True, True, True,
                ))))
def test_hwsim_dff_update_return(inputs, expected):
    comp = memory.DataFlipFlop()

    load, inp, state = inputs
    comp.state = state
    comp.set_inputs((load, inp))
    out = comp.update()
    assert out == expected


@pytest.mark.parametrize(
        "inputs,expected",
        list(zip(BINARY, (
                ZERO, ZERO, ZERO,
                ZERO, ZERO, ZERO,
                NEG, ZERO, POS,
                ))))
def test_hwsim_register(inputs, expected):
    comp = memory.Register()

    load, inp = inputs
    (out,) = comp.get_outputs((load, inp))
    # The value of a register should always be zero before any clock ticks
    assert out == ZERO

    comp.tick()
    (out,) = comp.get_outputs((load, inp))
    assert out == expected


@pytest.mark.parametrize(
        "inputs,expected",
        list(zip(
            (
                # No jump
                ('++00-+++-00-' '0-+-+---0+++' '-00'),
                ('++00-+++-00-' '0-+-+---0+++' '000'),
                ('++00-+++-00-' '0-+-+---0+++' '+00'),
                # Reset
                ('++00-+++-00-' '0-+-+---0+++' '-0-'),
                ('++00-+++-00-' '0-+-+---0+++' '00-'),
                ('++00-+++-00-' '0-+-+---0+++' '+0-'),
                # Jump unconditionally
                ('++00-+++-00-' '0-+-+---0+++' '-0+'),
                ('++00-+++-00-' '0-+-+---0+++' '00+'),
                ('++00-+++-00-' '0-+-+---0+++' '+0+'),
                # Jump if <0
                ('++00-+++-00-' '0-+-+---0+++' '---'),
                ('++00-+++-00-' '0-+-+---0+++' '0--'),
                ('++00-+++-00-' '0-+-+---0+++' '+--'),
                # Jump if ==0
                ('++00-+++-00-' '0-+-+---0+++' '--0'),
                ('++00-+++-00-' '0-+-+---0+++' '0-0'),
                ('++00-+++-00-' '0-+-+---0+++' '+-0'),
                # Jump if >0
                ('++00-+++-00-' '0-+-+---0+++' '--+'),
                ('++00-+++-00-' '0-+-+---0+++' '0-+'),
                ('++00-+++-00-' '0-+-+---0+++' '+-+'),
                # Jump if <=0
                ('++00-+++-00-' '0-+-+---0+++' '-+-'),
                ('++00-+++-00-' '0-+-+---0+++' '0+-'),
                ('++00-+++-00-' '0-+-+---0+++' '++-'),
                # Jump if !=0
                ('++00-+++-00-' '0-+-+---0+++' '-+0'),
                ('++00-+++-00-' '0-+-+---0+++' '0+0'),
                ('++00-+++-00-' '0-+-+---0+++' '++0'),
                # Jump if >=0
                ('++00-+++-00-' '0-+-+---0+++' '-++'),
                ('++00-+++-00-' '0-+-+---0+++' '0++'),
                ('++00-+++-00-' '0-+-+---0+++' '+++'),
                ),
            (
                tuple('--+0-+++-00-'),
                tuple('--+0-+++-00-'),
                tuple('--+0-+++-00-'),

                tuple('------------'),
                tuple('------------'),
                tuple('------------'),

                tuple('0-+-+---0+++'),
                tuple('0-+-+---0+++'),
                tuple('0-+-+---0+++'),

                tuple('0-+-+---0+++'),
                tuple('--+0-+++-00-'),
                tuple('--+0-+++-00-'),

                tuple('--+0-+++-00-'),
                tuple('0-+-+---0+++'),
                tuple('--+0-+++-00-'),

                tuple('--+0-+++-00-'),
                tuple('--+0-+++-00-'),
                tuple('0-+-+---0+++'),

                tuple('0-+-+---0+++'),
                tuple('0-+-+---0+++'),
                tuple('--+0-+++-00-'),

                tuple('0-+-+---0+++'),
                tuple('--+0-+++-00-'),
                tuple('0-+-+---0+++'),

                tuple('--+0-+++-00-'),
                tuple('0-+-+---0+++'),
                tuple('0-+-+---0+++'),
                ))))
def test_hwsim_jumper(inputs, expected):
    comp = cpu.Jumper()

    out = comp.get_outputs(inputs)
    assert out == expected
