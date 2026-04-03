import pytest

from hwsim import cpu
from tests.util import seq_matches, Z, P, TRINARY, QUATERNARY


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
            '-0-', '-0-', '-0-',
            '-0-', '-0-', '-0-',
            '-0-', '-0-', '-0-',
            '+00', '+00', '+00',
            '+00', '0+0', '00+',
            '00+', '00+', '00+',
            '-0-', '-0-', '-0-',
            '-0-', '-0-', '-0-',
            '-0-', '-0-', '-0-',
            ))))
def test_hwsim_loader(inputs, expected):
    comp = cpu.Loader()
    out = comp.get_outputs(inputs)
    assert out == tuple(expected)


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


def test_hwsim_cpu_reset():
    comp = cpu.CPU()
    # Send a reset signal with random junk in 'inM' and 'inst'. Expect that the
    # loadM output should be 0, and addrP will be all negative.
    inputs = ('--0++-000+-+' '0++0+-+-0000' '+')
    out = comp.get_outputs(inputs)
    loadm = out[23]
    addrp = out[24:35]
    assert loadm == Z
    assert addrp == tuple('-----------')

    # Advance to the next clock cycle and confirm that registers A and D have
    # both been reset to zero.
    comp.tick()
    assert comp.get_a() == '000000000000'
    assert comp.get_d() == '000000000000'


def test_hwsim_cpu_load_a():
    comp = cpu.CPU()
    comp.reset()
    assert comp.get_a() == '000000000000'
    assert comp.get_d() == '000000000000'

    # Tell the CPU to load a literal value into register A
    inputs = ('000000000000' '+-+-+-+-+-+-' '0')
    out = comp.get_outputs(inputs)
    loadm = out[23]
    addrp = out[24:35]
    assert loadm == Z
    assert addrp == tuple('0----------')

    # Advance to the next clock cycle and confirm that the register contains
    # the 11 literal trits from the instruction, with the high trit set to
    # zero.
    comp.tick()
    assert comp.get_a() == '+-+-+-+-+-+0'
    assert comp.get_d() == '000000000000'


def test_hwsim_cpu_load_d():
    comp = cpu.CPU()
    comp.reset()
    assert comp.get_a() == '000000000000'
    assert comp.get_d() == '000000000000'

    # Tell the CPU to load a literal value into register D
    inputs = ('000000000000' '+-+-+-+-+-++' '0')
    out = comp.get_outputs(inputs)
    loadm = out[23]
    addrp = out[24:35]
    assert loadm == Z
    assert addrp == tuple('0----------')

    # Advance to the next clock cycle and confirm that the register contains
    # the 11 literal trits from the instruction, with the high trit set to
    # zero.
    comp.tick()
    assert comp.get_a() == '000000000000'
    assert comp.get_d() == '+-+-+-+-+-+0'


def test_hwsim_cpu_add():
    comp = cpu.CPU()
    comp.reset()

    # Load literal value -28 into register A
    inputs = ('000000000000' '-00-0000000-' '0')
    out = comp.get_outputs(inputs)
    loadm = out[23]
    addrp = out[24:35]
    assert loadm == Z
    assert addrp == tuple('0----------')

    comp.tick()
    assert comp.get_a() == '-00-00000000'
    assert comp.get_d() == '000000000000'

    # Load literal value 30 into register D
    inputs = ('000000000000' '0+0+0000000+' '0')
    out = comp.get_outputs(inputs)
    loadm = out[23]
    addrp = out[24:35]
    assert loadm == Z
    assert addrp == tuple('+----------')

    comp.tick()
    assert comp.get_a() == '-00-00000000'
    assert comp.get_d() == '0+0+00000000'

    # Add together A and D, store the result in D
    inputs = ('000000000000' '00000+00-++0' '0')
    out = comp.get_outputs(inputs)
    loadm = out[23]
    addrp = out[24:35]
    assert loadm == Z
    assert addrp == tuple('-0---------')

    # The contents of D should now be 2, and A should be unchanged.
    comp.tick()
    assert comp.get_a() == '-00-00000000'
    assert comp.get_d() == '-+0000000000'


def test_hwsim_cpu_and():
    comp = cpu.CPU()
    comp.reset()

    # Load literal value into register A
    inputs = ('000000000000' '---000+++00-' '0')
    out = comp.get_outputs(inputs)
    loadm = out[23]
    addrp = out[24:35]
    assert loadm == Z
    assert addrp == tuple('0----------')
    comp.tick()

    # Load literal value into register D
    inputs = ('000000000000' '-0+-0+-0+00+' '0')
    out = comp.get_outputs(inputs)
    loadm = out[23]
    addrp = out[24:35]
    assert loadm == Z
    assert addrp == tuple('+----------')
    comp.tick()

    assert comp.get_a() == '---000+++000'
    assert comp.get_d() == '-0+-0+-0+000'

    # Compute the logical AND of A and D, store the result in D
    inputs = ('000000000000' '00000-00-++0' '0')
    out = comp.get_outputs(inputs)
    loadm = out[23]
    addrp = out[24:35]
    assert loadm == Z
    assert addrp == tuple('-0---------')
    comp.tick()

    # The contents of D should now be the result of AND, A should be unchanged.
    assert comp.get_a() == '---000+++000'
    assert comp.get_d() == '----00-0+000'


def test_hwsim_cpu_read_m():
    comp = cpu.CPU()
    comp.reset()

    # Load literal address value into register A
    inputs = ('000000000000' '--0++-000+--' '0')
    out = comp.get_outputs(inputs)
    loadm = out[23]
    addrp = out[24:35]
    assert loadm == Z
    assert addrp == tuple('0----------')
    comp.tick()

    # Copy the (hypothetical) addressed value from M into D
    inputs = ('--+000000000' '00000++0+0+0' '0')
    out = comp.get_outputs(inputs)
    loadm = out[23]
    addrp = out[24:35]
    assert loadm == Z
    assert addrp == tuple('+----------')
    comp.tick()
    assert seq_matches(comp.get_d(), '--+000000000')


def test_hwsim_cpu_write_m():
    comp = cpu.CPU()
    comp.reset()

    # Load literal address value into register A
    inputs = ('000000000000' '--0++-000+--' '0')
    out = comp.get_outputs(inputs)
    loadm = out[23]
    addrp = out[24:35]
    assert loadm == Z
    assert addrp == tuple('0----------')
    comp.tick()

    # Load a literal value into register D
    inputs = ('000000000000' '-0+-0+-0+00+' '0')
    out = comp.get_outputs(inputs)
    loadm = out[23]
    addrp = out[24:35]
    assert loadm == Z
    assert addrp == tuple('+----------')
    comp.tick()

    # Compute the value of 0+D, store the result in M
    inputs = ('000000000000' '00000++00+00' '0')
    out = comp.get_outputs(inputs)
    addrm = out[:11]
    outm = out[11:23]
    loadm = out[23]
    addrp = out[24:35]
    assert addrm == tuple('--0++-000+-')
    assert outm == tuple('-0+-0+-0+000')
    assert loadm == P
    assert addrp == tuple('-0---------')


def test_hwsim_cpu_inc_m():
    comp = cpu.CPU()
    comp.reset()

    # Increment the value of M and load it back into M
    inputs = ('+--000+++00-' '0000000+0000' '0')
    out = comp.get_outputs(inputs)
    outm = out[11:23]
    loadm = out[23]
    addrp = out[24:35]
    assert outm == tuple('-0-000+++00-')
    assert loadm == P
    assert addrp == tuple('0----------')


def test_hwsim_cpu_a_m():
    comp = cpu.CPU()
    comp.reset()

    # Load a literal value into register A
    inputs = ('000000000000' '--0++-000+--' '0')
    out = comp.get_outputs(inputs)
    loadm = out[23]
    addrp = out[24:35]
    assert loadm == Z
    assert addrp == tuple('0----------')
    comp.tick()

    # Compute A+M and load the result back into A
    inputs = ('+--000+++00-' '00000+00-0-0' '0')
    out = comp.get_outputs(inputs)
    loadm = out[23]
    addrp = out[24:35]
    assert loadm == Z
    assert addrp == tuple('+----------')
    comp.tick()

    assert comp.get_a() == '0++0+-++++--'


def test_hwsim_cpu_shift_left():
    comp = cpu.CPU()
    comp.reset()

    # Load a literal value into register D
    inputs = ('000000000000' '--0++-000+-+' '0')
    out = comp.get_outputs(inputs)
    loadm = out[23]
    addrp = out[24:35]
    assert loadm == Z
    assert addrp == tuple('0----------')
    comp.tick()
    assert comp.get_d() == '--0++-000+-0'

    # Shift the value left and load it back into D
    inputs = ('000000000000' '0000+++00++0' '0')
    out = comp.get_outputs(inputs)
    loadm = out[23]
    addrp = out[24:35]
    assert loadm == Z
    assert addrp == tuple('+----------')
    comp.tick()
    assert comp.get_d() == '0--0++-000+-'


def test_hwsim_cpu_shift_right():
    comp = cpu.CPU()
    comp.reset()

    # Load a literal value into register D
    inputs = ('000000000000' '--0++-000+-+' '0')
    out = comp.get_outputs(inputs)
    loadm = out[23]
    addrp = out[24:35]
    assert loadm == Z
    assert addrp == tuple('0----------')
    comp.tick()
    assert comp.get_d() == '--0++-000+-0'

    # Shift the value right and load it back into D
    inputs = ('000000000000' '0000-++00++0' '0')
    out = comp.get_outputs(inputs)
    loadm = out[23]
    addrp = out[24:35]
    assert loadm == Z
    assert addrp == tuple('+----------')
    comp.tick()
    assert comp.get_d() == '-0++-000+-00'
