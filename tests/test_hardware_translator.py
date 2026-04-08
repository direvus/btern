from io import BytesIO, StringIO

from ternary.hardware.assembler import Assembler
from ternary.hardware.translator import Translator
from ternary.hardware.simulator import Simulator


def test_hardware_translator_sim():
    # This is an end-to-end integration test that translates a VM source
    # program into assembly, hands the assembly off to the Assembler to process
    # into machine code, and finally hands the machine code off to the
    # Simulator to execute, and then checks the final values in memory.
    program = (
            "push constant -7\n"
            "push constant 25\n"
            "add"
            )
    tr = Translator()
    ass = Assembler()
    sim = Simulator()

    assembly = StringIO()
    machine = BytesIO()

    tr.read(StringIO(program), 'test')
    tr.write(assembly)

    assembly.seek(0)
    ass.read(assembly)
    ass.write(machine)

    machine.seek(0)
    sim.load(machine)
    sim.execute()

    index = 0  # Stack should contain only the final result
    out = sim.get_ram_contents(index)
    assert out == (-7 + 25)
