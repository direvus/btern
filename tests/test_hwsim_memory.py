import pytest

from ternary.hwsim import memory
from tests.util import N, Z, P, TRINARY


@pytest.mark.parametrize(
        "inputs,expected",
        list(zip(TRINARY, (
                N, Z, P,
                N, Z, P,
                N, Z, P,
                N, Z, P,
                N, Z, P,
                N, Z, P,
                N, Z, P,
                N, Z, P,
                N, Z, P,
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
                N, N, N,
                Z, Z, Z,
                P, P, P,
                N, Z, P,
                N, Z, P,
                N, Z, P,
                N, N, N,
                Z, Z, Z,
                P, P, P,
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
    assert out == Z

    comp.tick()
    # Tell the register to retain its value for the next cycle, and check that
    # the positive value was loaded correctly from the previous cycle.
    (out,) = comp.get_outputs('00')
    assert out == P

    comp.tick()
    # Tell the register to reset to zero for the next cycle. The current value
    # should still be positive, as we sent a retain signal last time.
    (out,) = comp.get_outputs('0-')
    assert out == P

    comp.tick()
    # The output should now be zero after the previous reset signal.
    (out,) = comp.get_outputs('0-')
    assert out == Z


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
    zero = tuple(Z * 12)

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


def test_hwsim_ram177k_mock():
    ram = memory.RAM177KMock()
    addr = '+0-+00+---0'
    value = '+--0+---00--'
    zero = tuple(Z * 12)

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
