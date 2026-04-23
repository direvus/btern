from collections.abc import Iterable
from io import BytesIO, StringIO

import pytest

from ternary.hardware.assembler import Assembler
from ternary.hardware.translator import Translator
from ternary.hardware.simulator import Simulator
from ternary.hardware.emulator import Emulator


def emulate(program: Iterable[str]) -> Emulator:
    """Translate, assemble and emulate a VM program.

    This function translates a VM source program into assembly, hands the
    assembly off to the Assembler to process into machine code, and finally
    hands the machine code off to the Emulator to execute, and returns the
    Emulator instance.
    """
    tr = Translator()
    ass = Assembler()
    emu = Emulator()

    assembly = StringIO()
    machine = BytesIO()

    tr.read(StringIO('\n'.join(program)), 'test')
    tr.write(assembly)

    assembly.seek(0)
    ass.read(assembly)
    ass.write(machine)

    machine.seek(0)
    emu.load(machine)
    emu.execute()
    return emu


@pytest.mark.parametrize(
        "a,b,expected",
        [
            (0, 0, 0),
            (0, 1, 1),
            (1, 0, 1),
            (1, 1, 2),
            (-87, 2, -85),
            (-7, -422, -429),
            ])
def test_hardware_translator_add(a, b, expected):
    emu = emulate((
            f'push constant {a}',
            f'push constant {b}',
            'add'))
    out = emu.get_ram_contents(0)
    assert out == expected


@pytest.mark.parametrize(
        "a,b,expected",
        [
            (0, 0, 0),
            (0, 1, -1),
            (1, 0, 1),
            (1, 1, 0),
            (-87, 2, -89),
            (-7, -422, 415),
            ])
def test_hardware_translator_sub(a, b, expected):
    emu = emulate((
            f'push constant {a}',
            f'push constant {b}',
            'sub'))
    out = emu.get_ram_contents(0)
    assert out == expected


@pytest.mark.parametrize(
        "a,b,expected",
        [
            (0, 0, 1),
            (0, 1, -1),
            (1, 0, -1),
            (1, 1, 1),
            (-87, 2, -1),
            (-7, -422, -1),
            ])
def test_hardware_translator_eq(a, b, expected):
    emu = emulate((
            f'push constant {a}',
            f'push constant {b}',
            'eq'))
    out = emu.get_ram_contents(0)
    assert out == expected


@pytest.mark.parametrize(
        "a,b,expected",
        [
            (0, 0, -1),
            (0, 1, 1),
            (1, 0, 1),
            (1, 1, -1),
            (-87, 2, 1),
            (-7, -422, 1),
            ])
def test_hardware_translator_ne(a, b, expected):
    emu = emulate((
            f'push constant {a}',
            f'push constant {b}',
            'ne'))
    out = emu.get_ram_contents(0)
    assert out == expected
