#!/usr/bin/env python
import logging
import time

from iconipy import IconFactory
from PySide6 import QtCore, QtGui, QtWidgets

from ternary.hardware.emulator import Emulator, SCREEN_END_ADDR
from ternary.hardware.util import (
        MIN_ADDR, int_to_trits, input_stream, trits_to_colour)

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


class WorkerSignals(QtCore.QObject):
    finished = QtCore.Signal(str, int)


class Worker(QtCore.QRunnable):
    def __init__(self, fn):
        super().__init__()
        self.fn = fn
        self.signals = WorkerSignals()

    @QtCore.Slot()
    def run(self):
        timer = time.perf_counter_ns()
        target = self.fn()
        duration = time.perf_counter_ns() - timer
        self.signals.finished.emit(target, duration)


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
        self.threadpool.setMaxThreadCount(1)
        self.create_layout()
        self.clear_screen()

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
        self.run_button.pressed.connect(self.start)

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

    def update_buttons(self):
        index = self.get_program_index()
        in_bounds = 0 <= index < self.program_length

        self.load_button.setEnabled(not self.running)
        self.reset_button.setEnabled(not self.running)
        self.step_button.setEnabled(not self.running and in_bounds)
        self.run_button.setEnabled(in_bounds)
        self.run_button.setChecked(self.running)

        icon = 'pause' if self.running else 'play'
        text = ' Pause' if self.running else ' Run'
        self.run_button.setIcon(ICON_FACTORY.asQPixmap(icon))
        self.run_button.setText(text)

    def update_tray(self):
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

    def update_program_list(self):
        index = self.get_program_index()
        item = self.program_list.topLevelItem(index)
        self.program_list.setCurrentItem(item)

    def update_screen(self, address: int, value: int):
        row, col = divmod(address - MIN_ADDR, SCREEN_WIDTH / 4)
        offset = SCREEN_SCALE // 2
        x = col * SCREEN_SCALE * 4 + offset
        y = row * SCREEN_SCALE + offset
        trits = int_to_trits(value, 12)
        painter = QtGui.QPainter(self.pix)
        for i in range(0, 12, 3):
            colour = '#' + trits_to_colour(trits[i:i+3])
            self.pen.setColor(colour)
            painter.setPen(self.pen)
            painter.drawPoint(x, y)
            x += SCREEN_SCALE
        painter.end()
        self.screen.setPixmap(self.pix)

    def clear_screen(self):
        painter = QtGui.QPainter(self.pix)
        colour = '#' + trits_to_colour('000')
        w = SCREEN_WIDTH * SCREEN_SCALE
        h = SCREEN_HEIGHT * SCREEN_SCALE
        painter.fillRect(0, 0, w, h, QtGui.QColor(colour))
        painter.end()
        self.screen.setPixmap(self.pix)

    def get_program_index(self):
        return self.emulator.pc - MIN_ADDR

    def stop(self):
        self.running = False
        self.update_buttons()

    def schedule_step(self):
        worker = Worker(self.step)
        worker.signals.finished.connect(self.step_completed)
        self.threadpool.start(worker)

    def step(self) -> str:
        return self.emulator.step()

    def step_completed(self, target: str, duration: int):
        self.count += 1
        self.update_tray()
        self.update_program_list()
        self.update_buttons()

        if target == 'M':
            a = self.emulator.a
            if a < SCREEN_END_ADDR:
                self.update_screen(a, self.emulator.get_ram(a))

        index = self.get_program_index()
        if index >= self.program_length or index < 0:
            self.stop()
            return

        if self.running:
            # TODO: delay according to target clock speed
            self.schedule_step()

    def start(self):
        """Called when the run/pause button is pressed.

        If the emulator is stopped, start running it. If the emulator is
        running, stop it.
        """
        if self.running:
            self.stop()
            return
        self.running = True
        self.update_buttons()
        self.schedule_step()

    def reset(self):
        self.running = False
        self.emulator.reset()
        self.count = 0
        self.update_tray()
        self.update_program_list()
        self.update_buttons()
        self.clear_screen()
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
        self.update_program_list()
        self.update_buttons()


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
