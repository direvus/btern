from io import StringIO

import pytest

from ternary.hardware import emulator
from ternary.hardware.util import trits_to_int
from tests.util import BINARY, N, Z, P


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
    emu = emulator.Emulator()
    emu.load_text(program)

    emu.set_ram(0, 77)
    emu.set_ram(1, 2)

    emu.execute()
    assert emu.get_ram(3) == 154
