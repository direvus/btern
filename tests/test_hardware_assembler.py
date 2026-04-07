from io import StringIO

import pytest

from ternary.hardware.assembler import Assembler
from tests.util import seq_matches


@pytest.mark.parametrize(
        "inputs,expected",
        list(zip(
            (
                'MOV -84383 A',
                'MOV +0-+-++0--- A',
                'MOV 0 D',
                'MOV 88073 D',
                'MOV -00++-+++++ D',
                'LABEL:\nMOV LABEL A',
                ),
            (
                '+0-+-++0----',
                '+0-+-++0----',
                '00000000000+',
                '-00++-++++++',
                '-00++-++++++',
                '------------',
                ))))
def test_hardware_assembler_mov(inputs, expected):
    ass = Assembler()

    assembly = StringIO(inputs)
    machine = StringIO()
    assembly.seek(0)

    ass.read(assembly)
    ass.write(machine)

    machine.seek(0)
    out = machine.read()

    assert seq_matches(out[:12], expected)


@pytest.mark.parametrize(
        "inputs,expected",
        list(zip(
            (
                'ADD M D D',
                'ADD 0 0 D',
                'ADD D -M M',
                ),
            (
                '00000+000++0',
                '00000++++++0',
                '00000+0-+000',
                ))))
def test_hardware_assembler_add(inputs, expected):
    ass = Assembler()

    assembly = StringIO(inputs)
    machine = StringIO()
    assembly.seek(0)

    ass.read(assembly)
    ass.write(machine)

    machine.seek(0)
    out = machine.read()

    assert seq_matches(out[:12], expected)


@pytest.mark.parametrize(
        "inputs,expected",
        list(zip(
            (
                'SUB M D D',
                'SUB 0 0 D',
                'SUB D -M M',
                ),
            (
                '00000+0-0++0',
                '00000++++++0',
                '00000+00+000',
                ))))
def test_hardware_assembler_sub(inputs, expected):
    ass = Assembler()

    assembly = StringIO(inputs)
    machine = StringIO()
    assembly.seek(0)

    ass.read(assembly)
    ass.write(machine)

    machine.seek(0)
    out = machine.read()

    assert seq_matches(out[:12], expected)


@pytest.mark.parametrize(
        "inputs,expected",
        list(zip(
            (
                'CHK A',
                'CHK D',
                'CHK M',
                ),
            (
                '00000++0+--0',
                '00000++0+++0',
                '00000++0+000',
                ))))
def test_hardware_assembler_chk(inputs, expected):
    ass = Assembler()

    assembly = StringIO(inputs)
    machine = StringIO()
    assembly.seek(0)

    ass.read(assembly)
    ass.write(machine)

    machine.seek(0)
    out = machine.read()

    assert seq_matches(out[:12], expected)


@pytest.mark.parametrize(
        "inputs,expected",
        list(zip(
            (
                'CLR A',
                'CLR D',
                'CLR M',
                ),
            (
                '00000-++++-0',
                '00000-+++++0',
                '00000-++++00',
                ))))
def test_hardware_assembler_clr(inputs, expected):
    ass = Assembler()

    assembly = StringIO(inputs)
    machine = StringIO()
    assembly.seek(0)

    ass.read(assembly)
    ass.write(machine)

    machine.seek(0)
    out = machine.read()

    assert seq_matches(out[:12], expected)


@pytest.mark.parametrize(
        "inputs,expected",
        list(zip(
            (
                'CPY M D',
                'CPY M A',
                'CPY D M',
                'CPY -D M',
                ),
            (
                '00000++0+0+0',
                '00000++0+0-0',
                '00000++0++00',
                '00000++-++00',
                ))))
def test_hardware_assembler_cpy(inputs, expected):
    ass = Assembler()

    assembly = StringIO(inputs)
    machine = StringIO()
    assembly.seek(0)

    ass.read(assembly)
    ass.write(machine)

    machine.seek(0)
    out = machine.read()

    assert seq_matches(out[:12], expected)


@pytest.mark.parametrize(
        "inputs,expected",
        list(zip(
            (
                'AND D M D',
                'AND A M M',
                'AND -D A A',
                ),
            (
                '00000-00+0+0',
                '00000-00-000',
                '00000--0+--0',
                ))))
def test_hardware_assembler_and(inputs, expected):
    ass = Assembler()

    assembly = StringIO(inputs)
    machine = StringIO()
    assembly.seek(0)

    ass.read(assembly)
    ass.write(machine)

    machine.seek(0)
    out = machine.read()

    assert seq_matches(out[:12], expected)


@pytest.mark.parametrize(
        "inputs,expected",
        list(zip(
            (
                'INC D D',
                'INC A M',
                'INC 0 D',
                ),
            (
                '0000000++0+0',
                '0000000+-000',
                '000000+++0+0',
                ))))
def test_hardware_assembler_inc(inputs, expected):
    ass = Assembler()

    assembly = StringIO(inputs)
    machine = StringIO()
    assembly.seek(0)

    ass.read(assembly)
    ass.write(machine)

    machine.seek(0)
    out = machine.read()

    assert seq_matches(out[:12], expected)


@pytest.mark.parametrize(
        "inputs,expected",
        list(zip(
            (
                'DEC D D',
                'DEC A M',
                'DEC 0 D',
                ),
            (
                '0000000-+0+0',
                '0000000--000',
                '000000+-+0+0',
                ))))
def test_hardware_assembler_dec(inputs, expected):
    ass = Assembler()

    assembly = StringIO(inputs)
    machine = StringIO()
    assembly.seek(0)

    ass.read(assembly)
    ass.write(machine)

    machine.seek(0)
    out = machine.read()

    assert seq_matches(out[:12], expected)


@pytest.mark.parametrize(
        "inputs,expected",
        list(zip(
            (
                'SHL D D',
                'SHL A M',
                'SHL M A',
                ),
            (
                '0000+++0+++0',
                '0000+++0+-00',
                '0000+++0+0-0',
                ))))
def test_hardware_assembler_shl(inputs, expected):
    ass = Assembler()

    assembly = StringIO(inputs)
    machine = StringIO()
    assembly.seek(0)

    ass.read(assembly)
    ass.write(machine)

    machine.seek(0)
    out = machine.read()

    assert seq_matches(out[:12], expected)


@pytest.mark.parametrize(
        "inputs,expected",
        list(zip(
            (
                'SHR D D',
                'SHR A M',
                'SHR M A',
                ),
            (
                '0000-++0+++0',
                '0000-++0+-00',
                '0000-++0+0-0',
                ))))
def test_hardware_assembler_shr(inputs, expected):
    ass = Assembler()

    assembly = StringIO(inputs)
    machine = StringIO()
    assembly.seek(0)

    ass.read(assembly)
    ass.write(machine)

    machine.seek(0)
    out = machine.read()

    assert seq_matches(out[:12], expected)


def test_hardware_assembler_nop():
    ass = Assembler()

    assembly = StringIO('NOP')
    machine = StringIO()
    assembly.seek(0)

    ass.read(assembly)
    ass.write(machine)

    machine.seek(0)
    out = machine.read()

    assert seq_matches(out[:12], '00000++0+++0')


@pytest.mark.parametrize(
        "inputs,expected",
        list(zip(
            (
                'NOP RST',
                'CHK D JMP',
                'CHK M JGT',
                ),
            (
                '0-000++0+++0',
                '0+000++0+++0',
                '-+000++0+000',
                ))))
def test_hardware_assembler_jump(inputs, expected):
    ass = Assembler()
    assembly = StringIO(inputs)
    machine = StringIO()
    assembly.seek(0)

    ass.read(assembly)
    ass.write(machine)

    machine.seek(0)
    out = machine.read()

    assert seq_matches(out[:12], expected)
