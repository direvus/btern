import pytest

from hwsim import computer, cpu, util
from trit import ZERO, POS, NEG
from tests.util import seq_matches


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
def test_hwsim_trits_to_int(inputs, expected):
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
def test_hwsim_int_to_trits(inputs, expected):
    out = util.int_to_trits(*inputs)
    assert out == expected


def test_hwsim_computer():
    # Put a random literal value into D, then select a random memory address,
    # and write the value from D into memory.
    comp = computer.Computer()
    program = (
        '--0++-00+---',  # MOV A
        '++-0+-+-00-+',  # MOV D
        '00000++00+00',  # ADD 0 D M
        )
    comp.load_program(program)
    comp.reset()
    for _ in range(len(program)):
        comp.get_outputs(ZERO)
        comp.tick()

    assert seq_matches(comp.get_ram_contents('--0++-00+--'), '++-0+-+-00-0')


def test_hwsim_computer_read_m():
    # Store a random literal value into RAM[1] before starting the program. The
    # program will select address 1, then copy M into D.
    comp = computer.Computer()
    addr1 = util.int_to_trits(1, 11)
    value = '++-0+-+-00-+'
    comp.set_ram_contents(addr1, value)

    program = (
        '+0000000000-',  # MOV 1 A
        '00000++0+0+0',  # ADD 0 M D
        )
    comp.load_program(program)
    comp.reset()
    count = 1
    for _ in range(len(program)):
        print(f"Starting tick {count}")
        comp.get_outputs(ZERO)
        comp.tick()
        print(f"Finished tick {count}")
        count += 1

    assert seq_matches(comp.get_d(), value)


def test_hwsim_computer_loop():
    # Test basic loop operation. Load a target address into A, and a loop
    # counter value into D. Decrement the counter and loop on that instruction
    # until the counter reaches zero.
    comp = computer.Computer()
    program = (
        '0+000000000+',  # MOV 3 D
        '+-----------',  # MOV +---------- A
        '-+00000-+0+0',  # DEC D D JGT
        )
    comp.load_program(program)
    comp.reset()
    assert seq_matches(comp.get_program_address(), '-----------')

    comp.step()
    assert seq_matches(comp.get_d(), '0+0000000000')
    assert seq_matches(comp.get_program_address(), '0----------')

    comp.step()
    assert seq_matches(comp.get_a(), '+----------0')
    assert seq_matches(comp.get_d(), '0+0000000000')
    assert seq_matches(comp.get_program_address(), '+----------')

    comp.step()
    assert seq_matches(comp.get_a(), '+----------0')
    assert seq_matches(comp.get_d(), '-+0000000000')
    assert seq_matches(comp.get_program_address(), '+----------')

    comp.step()
    assert seq_matches(comp.get_a(), '+----------0')
    assert seq_matches(comp.get_d(), '+00000000000')
    assert seq_matches(comp.get_program_address(), '+----------')

    comp.step()
    assert seq_matches(comp.get_a(), '+----------0')
    assert seq_matches(comp.get_d(), '000000000000')
    assert seq_matches(comp.get_program_address(), '-0---------')


def test_hwsim_computer_mul():
    # Test a simple multiplication routine. This code should multiply the value
    # in RAM[0] by the value in RAM[1], and store the result in RAM[3].
    comp = computer.Computer()
    program = (
            '0+000000000-',  # 1. MOV 3 A
            '00000-++++00',  # 2. CLR M
            '+0000000000-',  # 3. MOV 1 A
            '00000++0+0+0',  # 4. CPY M D
            '-+000000000-',  # 5. MOV 2 A
            '00000++0++00',  # 6. CPY D M
            '00000000000-',  # 7. LOOP: MOV 0 A
            '00000++0+0+0',  # 8. CPY M D
            '0+000000000-',  # 9. MOV 3 A
            '00000+00+000',  # 10. ADD D M M
            '-+000000000-',  # 11. MOV 2 A
            '0000000-00+0',  # 12. DEC M D
            '00000++0++00',  # 13. CPY D M
            '-+----------',  # 14. MOV LOOP A
            '-+000++0+++0',  # 15. CHK D JGT
            )
    comp.load_program(program)
    comp.reset()
    addr0 = util.int_to_trits(0, 11)
    addr1 = util.int_to_trits(1, 11)
    addr2 = util.int_to_trits(2, 11)
    addr3 = util.int_to_trits(3, 11)

    a = util.int_to_trits(-13, 12)
    b = util.int_to_trits(5, 12)

    comp.set_ram_contents(addr0, a)
    comp.set_ram_contents(addr1, b)

    start = util.trits_to_int(NEG * 11)
    exit_addr = start + len(program)

    pc = util.trits_to_int(comp.get_program_address())
    while pc < exit_addr:
        comp.step()
        ra = util.trits_to_int(comp.get_a())
        rd = util.trits_to_int(comp.get_d())
        m0 = util.trits_to_int(comp.get_ram_contents(addr0))
        m1 = util.trits_to_int(comp.get_ram_contents(addr1))
        m2 = util.trits_to_int(comp.get_ram_contents(addr2))
        m3 = util.trits_to_int(comp.get_ram_contents(addr3))
        print(
                f"A = {ra} D = {rd} "
                f"M[0] = {m0} M[1] = {m1} M[2] = {m2} M[3] = {m3}")
        print()
        pc = util.trits_to_int(comp.get_program_address())

    result = util.trits_to_int(comp.get_ram_contents(addr3))
    assert result == -13 * 5
