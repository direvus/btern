from ternary.hardware import computer, util
from tests.util import seq_matches, N


def test_hardware_computer_mov_a():
    comp = computer.Computer()
    program = (
        '--0++-00+---'  # MOV A
        )
    comp.load_program(program)
    comp.reset()
    comp.step()
    assert seq_matches(comp.get_a(), '0-0++-00+---')
    assert seq_matches(comp.get_d(), '000000000000')


def test_hardware_computer_mov_d():
    comp = computer.Computer()
    program = (
        '+-0++-00+--+'  # MOV D
        )
    comp.load_program(program)
    comp.reset()
    comp.step()
    assert seq_matches(comp.get_a(), '000000000000')
    assert seq_matches(comp.get_d(), '0-0++-00+--+')


def test_hardware_computer_mov_a2():
    comp = computer.Computer()
    program = (
        '0+++++-00000'  # CLR D
        '--0++-00+---'  # MOV A
        )
    comp.load_program(program)
    comp.reset()
    comp.step()
    assert seq_matches(comp.get_a(), '000000000000')
    assert seq_matches(comp.get_d(), '000000000000')

    comp.step()
    assert seq_matches(comp.get_a(), '0-0++-00+---')
    assert seq_matches(comp.get_d(), '000000000000')


def test_hardware_computer_write_m():
    # Put a random literal value into D, then select a random memory address,
    # and copy the value from D into memory.
    comp = computer.Computer()
    program = (
        '--0++-00+---'  # MOV A
        '++-0+-+-00-+'  # MOV D
        '00+00++00000'  # ADD 0 D M
        )
    comp.load_program(program)
    comp.reset()

    comp.step()
    assert seq_matches(comp.get_a(), '0-0++-00+---')
    assert seq_matches(comp.get_d(), '000000000000')

    comp.step()
    assert seq_matches(comp.get_a(), '0-0++-00+---')
    assert seq_matches(comp.get_d(), '0+-0+-+-00-+')

    comp.step()
    assert seq_matches(comp.get_a(), '0-0++-00+---')
    assert seq_matches(comp.get_d(), '0+-0+-+-00-+')
    assert seq_matches(comp.get_ram_contents('-0++-00+---'), '0+-0+-+-00-+')


def test_hardware_computer_read_m():
    # Store a random literal value into RAM[1] before starting the program. The
    # program will select address 1, then copy M into D.
    comp = computer.Computer()
    addr1 = util.int_to_trits(1, 11)
    value = '++-0+-+-00-+'
    comp.set_ram_contents(addr1, value)

    program = (
        '-0000000000+'  # MOV 1 A
        '0+0+0++00000'  # CPY M D
        )
    comp.load_program(program)
    comp.reset()
    for _ in range(len(program)):
        comp.step()
    assert seq_matches(comp.get_a(), '00000000000+')
    assert seq_matches(comp.get_d(), value)


def test_hardware_computer_loop():
    # Test basic loop operation. Load a target address into A, and a loop
    # counter value into D. Decrement the counter and loop on that instruction
    # until the counter reaches zero.
    comp = computer.Computer()
    program = (
        '+000000000+0'  # 1. MOV 3 D
        '-----------+'  # 2. MOV ----------+ A
        '0+0+-00000+-'  # 3. DEC D D JGT
        )
    comp.load_program(program)
    comp.reset()
    assert seq_matches(comp.get_program_address(), '-----------')

    comp.step()
    assert seq_matches(comp.get_d(), '0000000000+0')
    assert seq_matches(comp.get_program_address(), '----------0')

    comp.step()
    assert seq_matches(comp.get_a(), '0----------+')
    assert seq_matches(comp.get_d(), '0000000000+0')
    assert seq_matches(comp.get_program_address(), '----------+')

    comp.step()
    assert seq_matches(comp.get_a(), '0----------+')
    assert seq_matches(comp.get_d(), '0000000000+-')
    assert seq_matches(comp.get_program_address(), '----------+')

    comp.step()
    assert seq_matches(comp.get_a(), '0----------+')
    assert seq_matches(comp.get_d(), '00000000000+')
    assert seq_matches(comp.get_program_address(), '----------+')

    comp.step()
    assert seq_matches(comp.get_a(), '0----------+')
    assert seq_matches(comp.get_d(), '000000000000')
    assert seq_matches(comp.get_program_address(), '---------0-')


def test_hardware_computer_mul():
    # Test a simple multiplication routine. This code should multiply the value
    # in RAM[0] by the value in RAM[1], and store the result in RAM[3].
    comp = computer.Computer()
    program = (
            '-00000000000'  # 01. MOV 0 A
            '+000000-00++'  # 02. MOV -77 D
            '00++0++00000'  # 03. CPY D M
            '-0000000000+'  # 04. MOV 1 A
            '+000000000+0'  # 05. MOV 3 D
            '00++0++00000'  # 06. CPY D M
            '-000000000+0'  # 07. MOV 3 A
            '00++++-00000'  # 08. CLR M
            '-0000000000+'  # 09. MOV 1 A
            '0+0+0++00000'  # 10. CPY M D
            '-000000000+-'  # 11. MOV 2 A
            '00++0++00000'  # 12. CPY D M
            '-00000000000'  # 13. LOOP: MOV 0 A
            '0+0+0++00000'  # 14. CPY M D
            '-000000000+0'  # 15. MOV 3 A
            '000+00+00000'  # 16. ADD D M M
            '-000000000+-'  # 17. MOV 2 A
            '0+00-0000000'  # 18. DEC M D
            '00++0++00000'  # 19. CPY D M
            '---------00-'  # 20. MOV LOOP A
            '0+++0++000+-'  # 21. CHK D JGT
            )
    comp.load_program(program)
    comp.reset()
    addr3 = util.int_to_trits(3, 11)

    start = util.MIN_ADDR
    exit_addr = start + len(program)

    pc = util.trits_to_int(comp.get_program_address())
    while pc < exit_addr:
        comp.step()
        pc = util.trits_to_int(comp.get_program_address())

    result = util.trits_to_int(comp.get_ram_contents(addr3))
    assert result == -77 * 3
