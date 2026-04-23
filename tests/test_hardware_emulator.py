from io import BytesIO
import pytest

from ternary.hardware import emulator
from ternary.hardware.util import trits_to_int


@pytest.mark.parametrize(
        "inputs,expected",
        list(zip((
                ('------------', '++++++++++++'),
                ('000000000000', '++++++++++++'),
                ('++++++++++++', '++++++++++++'),
                ),
            (
                '------------',
                '000000000000',
                '++++++++++++',
                ))))
def test_hardware_emulator_and(inputs, expected):
    out = emulator.do_and(*map(trits_to_int, inputs))
    assert out == trits_to_int(expected)


@pytest.mark.parametrize(
        "inputs,expected",
        list(zip((
                (0, 0),
                (1, 0),
                (0, 1),
                (1, 1),
                (1, -1),
                (-2, -5),
                (265720, 1),
                (-265720, -1),
                ),
            (
                0,
                1,
                1,
                2,
                0,
                -7,
                -265720,
                265720,
                ))))
def test_hardware_emulator_add(inputs, expected):
    out = emulator.add(*inputs)
    assert out == expected


def test_hardware_emulator_mul():
    program = (
            '-000000000+0',  # 07. MOV 3 A
            '00++++-00000',  # 08. CLR M
            '-0000000000+',  # 09. MOV 1 A
            '0+0+0++00000',  # 10. CPY M D
            '-000000000+-',  # 11. MOV 2 A
            '00++0++00000',  # 12. CPY D M
            '-00000000000',  # 13. LOOP: MOV 0 A
            '0+0+0++00000',  # 14. CPY M D
            '-000000000+0',  # 15. MOV 3 A
            '000+00+00000',  # 16. ADD D M M
            '-000000000+-',  # 17. MOV 2 A
            '0+00-0000000',  # 18. DEC M D
            '00++0++00000',  # 19. CPY D M
            '----------+-',  # 20. MOV LOOP A
            '0+++0++000+-',  # 21. CHK D JGT
            )
    emu = emulator.Emulator()
    emu.load_text(program)

    emu.set_ram(0, 77)
    emu.set_ram(1, 2)

    emu.execute()
    assert emu.get_ram(3) == 154


def test_hardware_emulator_load_binary():
    program = BytesIO(
            b'\xf6\x01yy\xcap\xe6\xd6xyy\xe5y\x94\xe9y(y\xcb\xebxyy\xd4\x9d'
            b'vy{\x85\xe5pyy\xd4\xca^y\x94\x95y(y\xb2^y\x9e\xcaQ\x00q\xe9{'
            )
    emu = emulator.Emulator()
    emu.load(program)
    emu.execute()
    assert emu.get_ram(3) == -231
