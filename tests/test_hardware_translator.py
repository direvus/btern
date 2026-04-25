from collections.abc import Iterable
from io import BytesIO, StringIO

import pytest

from ternary.hardware.assembler import Assembler, PREDEF_VARS, VAR_ADDR
from ternary.hardware.translator import Translator
from ternary.hardware.emulator import Emulator
from ternary.hardware.util import MIN_ADDR, MAX_INT


def emulate(program: Iterable[str]) -> Emulator:
    """Translate, assemble and emulate a VM program.

    This function translates a VM source program into assembly, hands the
    assembly off to the Assembler to process into machine code, and finally
    loads the machine code in to an Emulator, and returns the Emulator
    instance.
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
    return emu


def execute(program: Iterable[str]) -> Emulator:
    emu = emulate(program)
    emu.execute()
    return emu


def get_pointer(emulator: Emulator, name: str) -> int:
    addr = PREDEF_VARS[name] + VAR_ADDR
    return emulator.get_ram(addr)


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
    emu = execute((
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
    emu = execute((
            f'push constant {a}',
            f'push constant {b}',
            'sub'))
    out = emu.get_ram_contents(0)
    assert out == expected


@pytest.mark.parametrize(
        "a,b,expected",
        [
            (0, 0, 0),
            (0, 1, 0),
            (1, 0, 0),
            (1, 1, 1),
            (-255541, -163520, -262669),
            ])
def test_hardware_translator_and(a, b, expected):
    emu = execute((
            f'push constant {a}',
            f'push constant {b}',
            'and'))
    out = emu.get_ram_contents(0)
    assert out == expected


@pytest.mark.parametrize(
        "a,b,expected",
        [
            (0, 0, 0),
            (0, 1, 1),
            (1, 0, 1),
            (1, 1, 1),
            (-255541, -163520, -156392),
            ])
def test_hardware_translator_or(a, b, expected):
    emu = execute((
            f'push constant {a}',
            f'push constant {b}',
            'or'))
    out = emu.get_ram_contents(0)
    assert out == expected


@pytest.mark.parametrize(
        "inp,expected",
        [
            (0, 0),
            (1, -1),
            (-1, 1),
            (-87, 87),
            (422, -422),
            ])
def test_hardware_translator_not(inp, expected):
    emu = execute((
            f'push constant {inp}',
            'not'))
    out = emu.get_ram_contents(0)
    assert out == expected


@pytest.mark.parametrize(
        "inp,expected",
        [
            (0, 0),
            (1, 3),
            (-1, -3),
            (-87, -261),
            (422, 1266),
            ])
def test_hardware_translator_shiftl(inp, expected):
    emu = execute((
            f'push constant {inp}',
            'shiftl'))
    out = emu.get_ram_contents(0)
    assert out == expected


@pytest.mark.parametrize(
        "inp,expected",
        [
            (0, 0),
            (1, 0),
            (-1, 0),
            (-87, -29),
            (422, 141),
            ])
def test_hardware_translator_shiftr(inp, expected):
    emu = execute((
            f'push constant {inp}',
            'shiftr'))
    out = emu.get_ram_contents(0)
    assert out == expected


@pytest.mark.parametrize(
        "inp,expected",
        [
            (0, 1),
            (1, 2),
            (-1, 0),
            (-87, -86),
            (422, 423),
            ])
def test_hardware_translator_inc(inp, expected):
    emu = execute((
            f'push constant {inp}',
            'inc'))
    out = emu.get_ram_contents(0)
    assert out == expected


@pytest.mark.parametrize(
        "inp,expected",
        [
            (0, -1),
            (1, 0),
            (-1, -2),
            (-87, -88),
            (422, 421),
            ])
def test_hardware_translator_dec(inp, expected):
    emu = execute((
            f'push constant {inp}',
            'dec'))
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
    emu = execute((
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
    emu = execute((
            f'push constant {a}',
            f'push constant {b}',
            'ne'))
    out = emu.get_ram_contents(0)
    assert out == expected


@pytest.mark.parametrize(
        "a,b,expected",
        [
            (0, 0, False),
            (0, 1, True),
            (1, 0, False),
            (1, 1, False),
            (-87, 2, True),
            (-7, -422, False),
            ])
def test_hardware_translator_lt(a, b, expected):
    emu = execute((
            f'push constant {a}',
            f'push constant {b}',
            'lt'))
    out = emu.get_ram_contents(0)
    assert (out > 0) == expected


@pytest.mark.parametrize(
        "a,b,expected",
        [
            (0, 0, False),
            (0, 1, False),
            (1, 0, True),
            (1, 1, False),
            (-87, 2, False),
            (-7, -422, True),
            ])
def test_hardware_translator_gt(a, b, expected):
    emu = execute((
            f'push constant {a}',
            f'push constant {b}',
            'gt'))
    out = emu.get_ram_contents(0)
    assert (out > 0) == expected


def test_hardware_translator_label_goto():
    emu = emulate((
            'push constant 0',
            'label line1',
            'goto line1',
            ))
    length = len(emu.program)
    emu.reset()
    for _ in range(length):
        emu.step()
    out = emu.pc - MIN_ADDR
    assert out < length


@pytest.mark.parametrize(
        "inp,jumped",
        [
            (0, False),
            (1, True),
            (-1, False),
            (-87, False),
            (422, True),
            ])
def test_hardware_translator_if_goto(inp, jumped):
    emu = execute((
            f'push constant {inp}',
            'if-goto exit',
            f'push constant {MAX_INT}',
            'label exit',
            ))
    out = emu.get_ram_contents(0)
    assert (out == MAX_INT) != jumped


def test_hardware_translator_push_pop():
    emu = execute((
            'push constant 87',
            'pop local 1',
            ))
    local = get_pointer(emu, 'local')
    assert emu.get_ram(local + 1) == 87


def test_hardware_translator_push_invalid():
    tr = Translator()
    value = MAX_INT + 1
    with pytest.raises(ValueError):
        tr.translate(f'push constant {value}')


def test_hardware_translator_function():
    emu = execute((
            'function test_func 0',
            ))
    # With zero locals, the stack pointer and the local pointer should still be
    # equal to each other at their initial value.
    sp = get_pointer(emu, 'sp')
    local = get_pointer(emu, 'local')
    assert sp == 0
    assert sp == local


def test_hardware_translator_function_locals():
    emu = execute((
            'function test_func 3',
            ))
    # With three locals, the stack pointer should be at local + 3
    sp = get_pointer(emu, 'sp')
    local = get_pointer(emu, 'local')
    assert local == 0
    assert sp == (local + 3)
