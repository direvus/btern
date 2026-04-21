#!/usr/bin/env python
import logging

from iconipy import IconFactory
from PySide6 import QtCore, QtGui, QtWidgets

from ternary.hardware.emulator import Emulator, SCREEN_END_ADDR
from ternary.hardware.util import MIN_ADDR, int_to_trits, input_stream

SPEED_MIN_HZ = 1
SPEED_MAX_HZ = 1_000_000
SCREEN_WIDTH = 320
SCREEN_HEIGHT = 200
SCREEN_SCALE = 4

FONT_MONO = QtGui.QFont("Fira Code")
FONT_MONO.setStyleHint(QtGui.QFont.StyleHint.Monospace)

FONT_MONO_ITALIC = QtGui.QFont(FONT_MONO)
FONT_MONO_ITALIC.setItalic(True)

COLOUR_DIM_TEXT = QtGui.QColor("#666666")

ICON_FACTORY = IconFactory(
    icon_set="lucide",
    icon_size=16,
)


def format_clock_speed(hz):
    """Convert Hz to human-readable format (Hz, kHz, or MHz)."""
    if hz >= 1_000_000:
        return f"{hz / 1_000_000:.0f} MHz"
    elif hz >= 1_000:
        return f"{hz / 1_000:.0f} kHz"
    else:
        return f"{hz} Hz"


def format_trits(value: int):
    trits = int_to_trits(value, 12)
    return ' '.join((trits[:6], trits[6:]))


class Worker(QtCore.QRunnable):
    def __init__(self, fn):
        super().__init__()
        self.fn = fn

    @QtCore.Slot()
    def run(self):
        self.fn()


class TrayItem(QtWidgets.QWidget):
    def __init__(self, name: str, primary: str = "", secondary: str = ""):
        super().__init__()
        self.name = QtWidgets.QLabel(name)
        self.primary = QtWidgets.QLineEdit(primary)
        self.primary.setFont(FONT_MONO)
        self.primary.setReadOnly(True)
        self.secondary = QtWidgets.QLineEdit(secondary)
        self.secondary.setFont(FONT_MONO)
        self.secondary.setReadOnly(True)

        layout = QtWidgets.QHBoxLayout()
        layout.addWidget(self.name)
        layout.addWidget(self.primary)
        layout.addWidget(self.secondary)
        self.setLayout(layout)

    def set_primary_text(self, text: str):
        self.primary.setText(text)

    def set_secondary_text(self, text: str):
        self.secondary.setText(text)


class MainWindow(QtWidgets.QMainWindow):
    def __init__(self, input_path=None, breaks=None):
        super().__init__()
        self.setWindowTitle("T-12 Ternary Computer Emulator")
        self.emulator = Emulator()
        self.program = []
        self.program_length = 0
        self.breaks = set(breaks) if breaks is not None else set()
        self.running = False
        self.count = 0

        self.threadpool = QtCore.QThreadPool()
        self.create_layout()

        if input_path:
            self.load_program(input_path)

    def create_layout(self):
        self.root = QtWidgets.QWidget()
        main_layout = QtWidgets.QVBoxLayout()
        main_panel = QtWidgets.QHBoxLayout()
        controls = QtWidgets.QHBoxLayout()
        info_tray = QtWidgets.QHBoxLayout()

        width = SCREEN_WIDTH * SCREEN_SCALE
        height = SCREEN_HEIGHT * SCREEN_SCALE

        self.program_list = QtWidgets.QTreeWidget()
        self.program_list.setColumnCount(3)
        self.program_list.setMinimumWidth(280)
        self.program_list.header().hide()
        font = QtGui.QFont(FONT_MONO)
        font.setPointSize(8)
        self.program_list.setFont(font)

        self.screen = QtWidgets.QLabel()
        self.pix = QtGui.QPixmap(width, height)
        self.screen.setMinimumSize(width, height)
        self.screen.setPixmap(self.pix)
        self.painter = QtGui.QPainter()
        self.pen = QtGui.QPen()
        self.pen.setWidth(SCREEN_SCALE)

        self.a = TrayItem("A", "000000 000000")
        self.d = TrayItem("D", "000000 000000")
        self.m = TrayItem("M", "000000 000000")
        self.pc = TrayItem("PC", "000000 000000")
        self.ticks = TrayItem("Ticks", "0")

        info_tray.addWidget(self.a)
        info_tray.addWidget(self.d)
        info_tray.addWidget(self.m)
        info_tray.addWidget(self.pc)
        info_tray.addWidget(self.ticks)

        # Add a space at the start of the text labels as a cheap way to get
        # some spacing between the text and the icon.
        self.load_button = QtWidgets.QPushButton(
                ICON_FACTORY.asQPixmap("hard-drive-upload"),
                " Load")
        self.reset_button = QtWidgets.QPushButton(
                ICON_FACTORY.asQPixmap("power"),
                " Reset")
        self.step_button = QtWidgets.QPushButton(
                ICON_FACTORY.asQPixmap("step-forward"),
                " Step")
        self.run_button = QtWidgets.QPushButton(
                ICON_FACTORY.asQPixmap("play"),
                " Run")

        self.reset_button.pressed.connect(self.reset)
        self.step_button.pressed.connect(self.schedule_step)

        controls.addWidget(self.load_button)
        controls.addWidget(self.reset_button)
        controls.addWidget(self.step_button)
        controls.addWidget(self.run_button)

        main_panel.addWidget(self.program_list)
        main_panel.addWidget(self.screen)
        main_layout.addLayout(main_panel)
        main_layout.addLayout(info_tray)
        main_layout.addLayout(controls)
        self.root.setLayout(main_layout)
        self.setCentralWidget(self.root)

    def stop(self):
        self.running = False
        # TODO update buttons

    def schedule_step(self):
        worker = Worker(self.step)
        self.threadpool.start(worker)

    def step(self):
        self.emulator.step()
        self.count += 1
        self.update_tray()

        if self.running:
            self.schedule_step()

    def start(self):
        self.running = True
        # TODO update buttons
        self.schedule_step()

    def reset(self):
        self.running = False
        self.emulator.reset()
        self.count = 0
        self.update_tray()
        self.stop()

    def load_program(self, path: str):
        try:
            with input_stream(path) as stream:
                self.emulator.load(stream)
                self.program_length = len(self.emulator.program)
        except Exception as e:
            self.show_error_dialog(
                "Program Load Error",
                f"Failed to load program from {path}:\n\n{str(e)}",
            )
            return

        self.reset()
        self.program_list.clear()

        for i, line in enumerate(self.emulator.program):
            comment = self.emulator.comments.get(i, "")
            item = QtWidgets.QTreeWidgetItem(self.program_list)
            item.setText(0, str(i + 1))
            item.setText(1, line)
            item.setText(2, comment)
            item.setTextAlignment(1, QtCore.Qt.AlignCenter)
            item.setTextAlignment(0, QtCore.Qt.AlignRight)
            item.setFont(2, FONT_MONO_ITALIC)
            item.setFont(2, FONT_MONO_ITALIC)
            item.setForeground(0, COLOUR_DIM_TEXT)
            item.setForeground(2, COLOUR_DIM_TEXT)

        self.program_list.resizeColumnToContents(0)
        self.update_tray()

    def update_tray(self):
        # TODO
        a = self.emulator.a
        self.a.set_primary_text(format_trits(a))
        self.a.set_secondary_text(str(a))

        d = self.emulator.d
        self.d.set_primary_text(format_trits(d))
        self.d.set_secondary_text(str(d))

        m = self.emulator.get_ram(a)
        self.m.set_primary_text(format_trits(m))
        self.m.set_secondary_text(str(m))

        pc = self.emulator.pc
        self.pc.set_primary_text(format_trits(pc))
        self.pc.set_secondary_text(str(pc))

        self.ticks.set_primary_text(str(self.count))


def cli():
    import argparse

    logging.basicConfig(level=logging.INFO)
    parser = argparse.ArgumentParser(
        description="Ternary Computer Emulator GUI"
    )
    parser.add_argument(
        "program",
        nargs="?",
        default=None,
        help="Path to the ternary program file to load",
    )
    parser.add_argument(
        "-b",
        "--breakpoint",
        type=int,
        action="append",
        help="Automatically pause when reaching this line number",
    )
    args = parser.parse_args()

    app = QtWidgets.QApplication()
    window = MainWindow(input_path=args.program, breaks=args.breakpoint)
    window.show()
    app.exec()


if __name__ == "__main__":
    cli()
