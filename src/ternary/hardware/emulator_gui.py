import tkinter as tk
from tkinter import filedialog, messagebox
import sys

import customtkinter as ctk
from ternary.hardware.emulator import Emulator
from ternary.hardware.util import int_to_trits, MIN_ADDR, input_stream


class EmulatorGUI:
    def __init__(self, input_path=None):
        ctk.set_appearance_mode("system")
        ctk.set_default_color_theme("blue")

        self.root = ctk.CTk()
        self.root.title("Ternary Computer Emulator")
        self.root.geometry("1000x700")

        self.emulator = Emulator()
        self.program_rows = []
        self.running = False
        self.after_id = None
        self.mono_font = ("Courier New", 10)
        self.mono_comment_font = ("Courier New", 9)

        self.create_layout()
        self.update_debug()

        if input_path:
            self.root.after(100, lambda: self.load_program_from_path(input_path))

    def create_layout(self):
        main_frame = ctk.CTkFrame(self.root)
        main_frame.pack(fill="both", expand=True, padx=10, pady=10)
        main_frame.grid_rowconfigure(0, weight=1)
        main_frame.grid_columnconfigure(1, weight=1)

        left_frame = ctk.CTkFrame(main_frame, width=288)
        left_frame.grid(row=0, column=0, sticky="ns", padx=5, pady=5)
        left_frame.grid_rowconfigure(0, weight=1)

        self.program_frame = ctk.CTkScrollableFrame(left_frame, width=264, height=600)
        self.program_frame.grid(row=0, column=0, padx=10, pady=10, sticky="nsew")
        self.program_frame.grid_columnconfigure(0, weight=1)

        canvas_frame = ctk.CTkFrame(main_frame)
        canvas_frame.grid(row=0, column=1, sticky="nsew", padx=5, pady=5)
        canvas_frame.grid_rowconfigure(0, weight=1)
        canvas_frame.grid_columnconfigure(0, weight=1)

        self.canvas = tk.Canvas(
            canvas_frame,
            width=640,
            height=400,
            bg="white",
            highlightthickness=1,
            highlightbackground="#777",
        )
        self.canvas.grid(row=0, column=0, sticky="nsew", padx=10, pady=10)

        self.debug_frame = ctk.CTkFrame(main_frame, height=140)
        self.debug_frame.grid(row=1, column=0, columnspan=2, sticky="ew", padx=5, pady=5)
        self.debug_frame.grid_columnconfigure((0, 1), weight=1)

        control_frame = ctk.CTkFrame(self.debug_frame)
        control_frame.grid(row=0, column=0, columnspan=2, sticky="ew", padx=10, pady=(10, 5))
        control_frame.grid_columnconfigure((0, 1, 2, 3), weight=1)

        self.load_button = ctk.CTkButton(control_frame, text="Load Program", command=self.load_program)
        self.load_button.grid(row=0, column=0, padx=5, pady=5, sticky="ew")

        self.reset_button = ctk.CTkButton(control_frame, text="Reset", command=self.reset_emulator, state="disabled")
        self.reset_button.grid(row=0, column=1, padx=5, pady=5, sticky="ew")

        self.step_button = ctk.CTkButton(control_frame, text="Step", command=self.step_emulator, state="disabled")
        self.step_button.grid(row=0, column=2, padx=5, pady=5, sticky="ew")

        self.run_button = ctk.CTkButton(control_frame, text="Run", command=self.toggle_running, state="disabled")
        self.run_button.grid(row=0, column=3, padx=5, pady=5, sticky="ew")

        pause_frame = ctk.CTkFrame(self.debug_frame)
        pause_frame.grid(row=1, column=0, sticky="ew", padx=10, pady=5)
        pause_frame.grid_columnconfigure(0, weight=1)

        self.speed_slider = ctk.CTkSlider(pause_frame, from_=100, to=5000, number_of_steps=49)
        self.speed_slider.set(1000)
        self.speed_slider.grid(row=0, column=0, padx=(5, 0), pady=5, sticky="ew")

        speed_label = ctk.CTkLabel(pause_frame, text="Speed")
        speed_label.grid(row=0, column=1, padx=5, pady=5, sticky="w")

        info_frame = ctk.CTkFrame(self.debug_frame)
        info_frame.grid(row=1, column=1, sticky="nsew", padx=10, pady=5)
        info_frame.grid_columnconfigure(0, weight=1)

        self.label_a = ctk.CTkLabel(info_frame, text="A: 0 (000000000000)", anchor="w", font=self.mono_font)
        self.label_a.grid(row=0, column=0, padx=10, pady=(10, 3), sticky="ew")

        self.label_d = ctk.CTkLabel(info_frame, text="D: 0 (000000000000)", anchor="w", font=self.mono_font)
        self.label_d.grid(row=2, column=0, padx=10, pady=3, sticky="ew")

        self.label_m = ctk.CTkLabel(info_frame, text="M: 0 (000000000000)", anchor="w", font=self.mono_font)
        self.label_m.grid(row=3, column=0, padx=10, pady=3, sticky="ew")

        self.label_pc = ctk.CTkLabel(info_frame, text="PC: 0", anchor="w")
        self.label_pc.grid(row=4, column=0, padx=10, pady=3, sticky="ew")

        self.label_ticks = ctk.CTkLabel(info_frame, text="Ticks: 0", anchor="w")
        self.label_ticks.grid(row=5, column=0, padx=10, pady=(3, 10), sticky="ew")

    def load_program_from_path(self, path):
        try:
            with input_stream(path) as stream:
                self.emulator.load(stream)
        except Exception as e:
            self.show_error_dialog("Program Load Error", f"Failed to load program from {path}:\n\n{str(e)}")
            return

        self.emulator.reset()
        self.running = False
        if self.after_id is not None:
            self.root.after_cancel(self.after_id)
            self.after_id = None

        self.refresh_program_list()
        self.update_debug()
        self.reset_button.configure(state="normal")
        self.step_button.configure(state="normal")
        self.run_button.configure(state="normal", text="Run")

    def show_error_dialog(self, title, message):
        messagebox.showerror(title, message)

    def load_program(self):
        path = filedialog.askopenfilename(
            title="Select Ternary Program",
            filetypes=[("Ternary text", ["*.t12", "*.txt"]),  ("Binary program", "*.bin"), ("All files", "*")],
        )
        if not path:
            return

        try:
            with open(path, "r", encoding="utf-8") as stream:
                self.emulator.load(stream)
        except (ValueError, UnicodeDecodeError):
            with open(path, "rb") as stream:
                self.emulator.load(stream)

        self.emulator.reset()
        self.running = False
        if self.after_id is not None:
            self.root.after_cancel(self.after_id)
            self.after_id = None

        self.refresh_program_list()
        self.update_debug()
        self.reset_button.configure(state="normal")
        self.step_button.configure(state="normal")
        self.run_button.configure(state="normal", text="Run")

    def refresh_program_list(self):
        for row, inst_label, comment_label in self.program_rows:
            row.destroy()
        self.program_rows.clear()

        for index, instruction in enumerate(self.emulator.program):
            row = ctk.CTkFrame(self.program_frame, fg_color="transparent")
            row.grid(row=index, column=0, padx=5, pady=(2, 0), sticky="ew")
            row.grid_columnconfigure(0, weight=1)
            row.grid_columnconfigure(1, weight=1)

            inst_label = ctk.CTkLabel(
                row,
                text=f"{index:04d}: {instruction}",
                anchor="w",
                fg_color="transparent",
                corner_radius=8,
                font=self.mono_font,
            )
            inst_label.grid(row=0, column=0, sticky="ew", padx=(0, 8), pady=2)

            comment_text = self.emulator.comments.get(index, "")
            comment_label = None
            if comment_text:
                comment_label = ctk.CTkLabel(
                    row,
                    text=comment_text,
                    anchor="w",
                    text_color="#888888",
                    fg_color="transparent",
                    font=self.mono_comment_font,
                )
                comment_label.grid(row=0, column=1, sticky="ew", pady=2)

            self.program_rows.append((row, inst_label, comment_label))

        self.highlight_current_instruction()

    def highlight_current_instruction(self):
        index = self.emulator.pc - MIN_ADDR
        for idx, (_, inst_label, _) in enumerate(self.program_rows):
            if idx == index:
                inst_label.configure(fg_color="#2f95ff", text_color="white")
            else:
                inst_label.configure(fg_color="transparent", text_color="white")

    def update_debug(self):
        a_trits = int_to_trits(self.emulator.a, 12)
        d_trits = int_to_trits(self.emulator.d, 12)
        m_value = self.emulator.get_m()
        m_trits = int_to_trits(m_value, 12)
        index = self.emulator.pc - MIN_ADDR

        self.label_a.configure(text=f"A: {self.emulator.a} ({a_trits})")
        self.label_d.configure(text=f"D: {self.emulator.d} ({d_trits})")
        self.label_m.configure(text=f"M: {m_value} ({m_trits})")
        self.label_pc.configure(text=f"PC: {self.emulator.pc} (idx {index})")
        self.label_ticks.configure(text=f"Ticks: {self.emulator.ticks}")
        self.highlight_current_instruction()

    def reset_emulator(self):
        self.emulator.reset()
        self.running = False
        if self.after_id is not None:
            self.root.after_cancel(self.after_id)
            self.after_id = None
        self.update_debug()
        self.run_button.configure(state="normal", text="Run")

    def step_emulator(self):
        if not self.emulator.program:
            return

        index = self.emulator.pc - MIN_ADDR
        if not (0 <= index < len(self.emulator.program)):
            return

        self.emulator.step()
        self.update_debug()

    def toggle_running(self):
        if self.running:
            self.pause_running()
        else:
            self.start_running()

    def start_running(self):
        if not self.emulator.program or self.running:
            return

        self.running = True
        self.run_button.configure(text="Pause")
        self.schedule_step()

    def pause_running(self):
        if self.after_id is not None:
            self.root.after_cancel(self.after_id)
            self.after_id = None
        self.running = False
        self.run_button.configure(state="normal", text="Run")

    def schedule_step(self):
        if not self.running:
            return

        index = self.emulator.pc - MIN_ADDR
        if not (0 <= index < len(self.emulator.program)):
            self.pause_running()
            return

        self.emulator.step()
        self.update_debug()

        speed = self.speed_slider.get()
        delay = max(1, int(1000 / speed))
        self.after_id = self.root.after(delay, self.schedule_step)

    def run(self):
        self.root.mainloop()


if __name__ == "__main__":
    import argparse
    parser = argparse.ArgumentParser(description="Ternary Computer Emulator GUI")
    parser.add_argument("program", nargs="?", default=None, help="Path to the ternary program file to load")
    args = parser.parse_args()

    gui = EmulatorGUI(input_path=args.program)
    gui.run()
