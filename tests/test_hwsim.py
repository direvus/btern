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
def test_hwsim_mux_2way(inputs, expected):
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
    (out,) = comp.get_outputs((inp, load))
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
    comp.set_inputs((inp, load))
    comp.update()
    (out,) = comp.get_outputs((inp, load))
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
    comp.set_inputs((inp, load))
    out = comp.update()
    assert out == expected


@pytest.mark.parametrize(
        "inputs,expected",
        list(zip(TRINARY, (
                Z, Z, Z,
                N, Z, P,
                N, N, N,
                Z, Z, Z,
                N, Z, P,
                Z, Z, Z,
                Z, Z, Z,
                N, Z, P,
                P, P, P,
                ))))
def test_hwsim_register(inputs, expected):
    comp = memory.Register()
    inp, load, state = inputs
    comp.components['DFF'].state = state
    (out,) = comp.get_outputs((inp, load))
    # The value of the register should continue to reflect the current state
    # until the next clock cycle.
    assert out == state

    comp.tick()
    (out,) = comp.get_outputs((inp, load))
    assert out == expected


def test_hwsim_register_updates():
    comp = memory.Register()
    (out,) = comp.get_outputs('++')
    # The value of the register should continue to reflect the initial state
    # until the next clock cycle.
    assert out == ZERO

    comp.tick()
    # Tell the register to retain its value for the next cycle, and check that
    # the positive value was loaded correctly from the previous cycle.
    (out,) = comp.get_outputs('00')
    assert out == POS

    comp.tick()
    # Tell the register to reset to zero for the next cycle. The current value
    # should still be positive, as we sent a retain signal last time.
    (out,) = comp.get_outputs('0-')
    assert out == POS

    comp.tick()
    # The output should now be zero after the reset.
    (out,) = comp.get_outputs('0-')
    assert out == ZERO


@pytest.mark.parametrize(
        "inputs,expected",
        list(zip(
            (
                '0-+-+---0+++-',
                '0-+-+---0+++0',
                '0-+-+---0++++',
                ),
            (
                '000000000000',
                '000000000000',
                '0-+-+---0+++',
                ))))
def test_hwsim_register12(inputs, expected):
    comp = memory.Register12()
    out = comp.get_outputs(inputs)
    assert out == tuple('000000000000')
    comp.tick()
    out = comp.get_outputs(inputs)
    assert out == tuple(expected)


def test_hwsim_register12_updates():
    comp = memory.Register12()
    v = '0-+-+---0+++'
    z = '000000000000'

    out = comp.get_outputs(v + '+')
    # The value of the register should continue to reflect the initial state
    # until the next clock cycle.
    assert out == tuple(z)

    comp.tick()
    # Tell the register to retain its value for the next cycle, and check that
    # the positive value was loaded correctly from the previous cycle.
    out = comp.get_outputs(z + '0')
    assert out == tuple(v)

    comp.tick()
    # Tell the register to reset to zero for the next cycle. The current value
    # should still be positive, as we sent a retain signal last time.
    out = comp.get_outputs(z + '-')
    assert out == tuple(v)

    comp.tick()
    # The output should now be zero after the reset.
    out = comp.get_outputs(z + '0')
    assert out == tuple(z)


@pytest.mark.parametrize(
        "inputs,expected",
        list(zip(
            (
                '0-+-+---0+++--',
                '0-+-+---0+++-0',
                '0-+-+---0+++-+',
                '0-+-+---0+++0-',
                '0-+-+---0+++00',
                '0-+-+---0+++0+',
                '0-+-+---0++++-',
                '0-+-+---0++++0',
                '0-+-+---0+++++',
                ),
            (
                '000000000000',
                '000000000000',
                '000000000000',
                '000000000000',
                '000000000000',
                '000000000000',
                '0-+-+---0+++',
                '0-+-+---0+++',
                '0-+-+---0+++',
                ))))
def test_hwsim_ram3(inputs, expected):
    comp = memory.RAM3()
    out = comp.get_outputs(inputs)
    assert out == tuple('000000000000')
    comp.tick()
    out = comp.get_outputs(inputs)
    assert out == tuple(expected)


def test_hwsim_ram3_updates():
    ram = memory.RAM3()
    z = '000000000000'
    v = '0-+-+---0+++'

    # Address the first register and tell it to load the test value. It
    # shouldn't be visible in the outputs from the RAM module until after the
    # next clock tick.
    out = ram.get_outputs(v + '+-')
    assert out == tuple(z)

    # Send a clock tick, and continue to address the first register but switch
    # off the 'load' signal. Check that the value loaded in the previous clock
    # cycle is now visible on the output.
    ram.tick()
    out = ram.get_outputs(z + '0-')
    assert out == tuple(v)

    # Address the third register and load the test value into it.
    ram.tick()
    out = ram.get_outputs(v + '++')
    assert out == tuple(z)

    # Send a clock tick, tell the third register to reset, and check the value
    # was loaded correctly from the previous cycle.
    ram.tick()
    out = ram.get_outputs(z + '-+')
    assert out == tuple(v)

    # Send a clock tick, keep the third register active, and check that it was
    # reset correctly by the previous cycle.
    ram.tick()
    out = ram.get_outputs(z + '0+')
    assert out == tuple(z)

    # Send a clock tick, activate the first register again, and check that it
    # still has the value loaded in the first cycle.
    ram.tick()
    out = ram.get_outputs(z + '0-')
    assert out == tuple(v)


def test_hwsim_ram9():
    ram = memory.RAM9()
    z = '000000000000'
    v = '0-+-+---0+++'

    # Instruct the first register to load the test value. It won't be visible
    # in the outputs from the RAM module until after the next clock tick.
    out = ram.get_outputs(v + '+--')
    assert out == tuple(z)

    # Send a clock tick, and continue to address the first register but switch
    # off the 'load' signal. Afterwards, check that the value loaded in the
    # previous clock cycle is now visible on the output.
    ram.tick()
    out = ram.get_outputs(z + '0--')
    assert out == tuple(v)

    # Address the eighth register and load the test value into it.
    ram.tick()
    out = ram.get_outputs(v + '++0')
    assert out == tuple(z)

    ram.tick()
    out = ram.get_outputs(z + '0+0')
    assert out == tuple(v)


def test_hwsim_ram81():
    ram = memory.RAM81()
    addr = '+0-+'
    value = '+--0+---00--'
    zero = tuple(ZERO * 12)

    # Load the test value into the register. It won't be visible in the outputs
    # from the RAM module until after the next clock tick.
    out = ram.get_outputs(value + '+' + addr)
    assert out == zero

    # Send a clock tick, and continue to address the same register but switch
    # the 'load' signal to retain. Afterwards, check that the value loaded in
    # the previous clock cycle is now visible on the output.
    ram.tick()
    out = ram.get_outputs(value + '0' + addr)
    assert out == tuple(value)

    # Send a clock tick, and continue to address the same register but switch
    # the 'load' signal to reset. Afterwards, check that the value loaded in
    # the previous clock cycle was correctly retained by the previous
    # instruction.
    ram.tick()
    out = ram.get_outputs(value + '-' + addr)
    assert out == tuple(value)

    # Send another tick, and check that the register was correctly cleared by
    # the previous instruction.
    ram.tick()
    out = ram.get_outputs(value + '0' + addr)
    assert out == zero


def test_hwsim_ram177ksim():
    ram = memory.RAM177KSim()
    addr = '+0-+00+---0'
    value = '+--0+---00--'
    zero = tuple(ZERO * 12)

    # Load the test value into the register. It won't be visible in the outputs
    # from the RAM module until after the next clock tick.
    out = ram.get_outputs(value + '+' + addr)
    assert out == zero

    # Send a clock tick, and continue to address the same register but switch
    # the 'load' signal to retain. Afterwards, check that the value loaded in
    # the previous clock cycle is now visible on the output.
    ram.tick()
    out = ram.get_outputs(value + '0' + addr)
    assert out == tuple(value)

    # Send a clock tick, and continue to address the same register but switch
    # the 'load' signal to reset. Afterwards, check that the value loaded in
    # the previous clock cycle was correctly retained by the previous
    # instruction.
    ram.tick()
    out = ram.get_outputs(value + '-' + addr)
    assert out == tuple(value)

    # Send another tick, and check that the register was correctly cleared by
    # the previous instruction.
    ram.tick()
    out = ram.get_outputs(value + '0' + addr)
    assert out == zero


def test_hwsim_program_counter11():
    comp = memory.ProgramCounter11()
    v = '0-+-+---0++'
    z = '00000000000'
    n = '-----------'

    out = comp.get_outputs(v)
    # The value of the register should continue to reflect the initial state
    # until the next clock cycle.
    assert out == tuple(z)

    comp.tick()
    # Check that the current value was loaded correctly from the previous
    # cycle, and set the next value to all negative.
    out = comp.get_outputs(n)
    assert out == tuple(v)

    comp.tick()
    out = comp.get_outputs(z)
    assert out == tuple(n)


@pytest.mark.parametrize(
        "inputs,expected",
        list(zip(TRINARY, (
            Z, Z, Z,  # a = -, b = -
            Z, Z, Z,  # a = -, b = 0
            Z, Z, Z,  # a = -, b = +
            Z, Z, Z,  # a = 0, b = -
            Z, Z, P,  # a = 0, b = 0
            Z, Z, Z,  # a = 0, b = +
            Z, Z, Z,  # a = +, b = -
            Z, Z, Z,  # a = +, b = 0
            Z, Z, Z,  # a = +, b = +
            ))))
def test_hwsim_loader(inputs, expected):
    comp = cpu.Loader()
    (out,) = comp.get_outputs(inputs)
    assert out == expected


@pytest.mark.parametrize(
        "inputs,expected",
        list(zip(
            (
                # No jump
                ('++00-+++-00' '0-+-+---0++' '-00'),
                ('++00-+++-00' '0-+-+---0++' '000'),
                ('++00-+++-00' '0-+-+---0++' '+00'),
                # Reset
                ('++00-+++-00' '0-+-+---0++' '-0-'),
                ('++00-+++-00' '0-+-+---0++' '00-'),
                ('++00-+++-00' '0-+-+---0++' '+0-'),
                # Jump unconditionally
                ('++00-+++-00' '0-+-+---0++' '-0+'),
                ('++00-+++-00' '0-+-+---0++' '00+'),
                ('++00-+++-00' '0-+-+---0++' '+0+'),
                # Jump if <0
                ('++00-+++-00' '0-+-+---0++' '---'),
                ('++00-+++-00' '0-+-+---0++' '0--'),
                ('++00-+++-00' '0-+-+---0++' '+--'),
                # Jump if ==0
                ('++00-+++-00' '0-+-+---0++' '--0'),
                ('++00-+++-00' '0-+-+---0++' '0-0'),
                ('++00-+++-00' '0-+-+---0++' '+-0'),
                # Jump if >0
                ('++00-+++-00' '0-+-+---0++' '--+'),
                ('++00-+++-00' '0-+-+---0++' '0-+'),
                ('++00-+++-00' '0-+-+---0++' '+-+'),
                # Jump if <=0
                ('++00-+++-00' '0-+-+---0++' '-+-'),
                ('++00-+++-00' '0-+-+---0++' '0+-'),
                ('++00-+++-00' '0-+-+---0++' '++-'),
                # Jump if !=0
                ('++00-+++-00' '0-+-+---0++' '-+0'),
                ('++00-+++-00' '0-+-+---0++' '0+0'),
                ('++00-+++-00' '0-+-+---0++' '++0'),
                # Jump if >=0
                ('++00-+++-00' '0-+-+---0++' '-++'),
                ('++00-+++-00' '0-+-+---0++' '0++'),
                ('++00-+++-00' '0-+-+---0++' '+++'),
                ),
            (
                tuple('--+0-+++-00'),
                tuple('--+0-+++-00'),
                tuple('--+0-+++-00'),

                tuple('-----------'),
                tuple('-----------'),
                tuple('-----------'),

                tuple('0-+-+---0++'),
                tuple('0-+-+---0++'),
                tuple('0-+-+---0++'),

                tuple('0-+-+---0++'),
                tuple('--+0-+++-00'),
                tuple('--+0-+++-00'),

                tuple('--+0-+++-00'),
                tuple('0-+-+---0++'),
                tuple('--+0-+++-00'),

                tuple('--+0-+++-00'),
                tuple('--+0-+++-00'),
                tuple('0-+-+---0++'),

                tuple('0-+-+---0++'),
                tuple('0-+-+---0++'),
                tuple('--+0-+++-00'),

                tuple('0-+-+---0++'),
                tuple('--+0-+++-00'),
                tuple('0-+-+---0++'),

                tuple('--+0-+++-00'),
                tuple('0-+-+---0++'),
                tuple('0-+-+---0++'),
                ))))
def test_hwsim_jumper(inputs, expected):
    comp = cpu.Jumper()
    out = comp.get_outputs(inputs)
    assert out == expected


@pytest.mark.parametrize(
        "inputs,expected",
        list(zip(QUATERNARY, (
            '0-', '00', '0-', '0-', '--', '0-', '0-', '00', '0-',  # j = --
            '0-', '00', '0-', '0-', '-0', '0-', '0-', '00', '0-',  # j = -0
            '0-', '00', '0-', '0-', '-+', '0-', '0-', '00', '0-',  # j = -+
            '0-', '00', '0-', '0-', '0-', '0-', '0-', '00', '0-',  # j = 0-
            '0-', '00', '0-', '0-', '00', '0-', '0-', '00', '0-',  # j = 00
            '0-', '00', '0-', '0-', '0+', '0-', '0-', '00', '0-',  # j = 0+
            '0-', '00', '0-', '0-', '+-', '0-', '0-', '00', '0-',  # j = +-
            '0-', '00', '0-', '0-', '+0', '0-', '0-', '00', '0-',  # j = +0
            '0-', '00', '0-', '0-', '++', '0-', '0-', '00', '0-',  # j = ++
            ))))
def test_hwsim_jump_controller(inputs, expected):
    comp = cpu.JumpController()
    out = comp.get_outputs(inputs)
    assert out == tuple(expected)
