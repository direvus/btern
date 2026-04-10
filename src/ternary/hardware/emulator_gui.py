import tkinter as tk
from tkinter import filedialog

import customtkinter as ctk
from ternary.hardware.emulator import Emulator
from ternary.hardware.util import int_to_trits, MIN_ADDR


class EmulatorGUI:
    def __init__(self):
        ctk.set_appearance_mode("system")
        ctk.set_default_color_theme("blue")

        self.root = ctk.CTk()
        self.root.title("Ternary Computer Emulator")
        self.root.geometry("1000x700")

        self.emulator = Emulator()
        self.program_labels = []
        self.running = False
        self.after_id = None

        self.create_layout()
        self.update_debug()

    def create_layout(self):
        main_frame = ctk.CTkFrame(self.root)
        main_frame.pack(fill="both", expand=True, padx=10, pady=10)
        main_frame.grid_rowconfigure(0, weight=1)
        main_frame.grid_columnconfigure(1, weight=1)

        left_frame = ctk.CTkFrame(main_frame, width=240)
        left_frame.grid(row=0, column=0, sticky="ns", padx=5, pady=5)
        left_frame.grid_rowconfigure(1, weight=1)

        program_title = ctk.CTkLabel(
            left_frame,
            text="Loaded Program",
            anchor="w",
            font=(None, 16, "bold"),
        )
        program_title.grid(row=0, column=0, padx=10, pady=(10, 5), sticky="ew")

        self.program_frame = ctk.CTkScrollableFrame(left_frame, width=220, height=560)
        self.program_frame.grid(row=1, column=0, padx=10, pady=5, sticky="nsew")
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

        self.reset_button = ctk.CTkButton(control_frame, text="Reset", command=self.reset_emulator)
        self.reset_button.grid(row=0, column=1, padx=5, pady=5, sticky="ew")

        self.step_button = ctk.CTkButton(control_frame, text="Step", command=self.step_emulator)
        self.step_button.grid(row=0, column=2, padx=5, pady=5, sticky="ew")

        self.run_button = ctk.CTkButton(control_frame, text="Run", command=self.start_running)
        self.run_button.grid(row=0, column=3, padx=5, pady=5, sticky="ew")

        pause_frame = ctk.CTkFrame(self.debug_frame)
        pause_frame.grid(row=1, column=0, sticky="ew", padx=10, pady=5)
        pause_frame.grid_columnconfigure(1, weight=1)

        self.pause_button = ctk.CTkButton(pause_frame, text="Pause", command=self.pause_running, state="disabled")
        self.pause_button.grid(row=0, column=0, padx=(0, 5), pady=5, sticky="ew")

        self.speed_slider = ctk.CTkSlider(pause_frame, from_=100, to=5000, number_of_steps=49)
        self.speed_slider.set(1000)
        self.speed_slider.grid(row=0, column=1, padx=(5, 0), pady=5, sticky="ew")

        speed_label = ctk.CTkLabel(pause_frame, text="Speed")
        speed_label.grid(row=0, column=2, padx=5, pady=5, sticky="w")

        info_frame = ctk.CTkFrame(self.debug_frame)
        info_frame.grid(row=1, column=1, sticky="nsew", padx=10, pady=5)
        info_frame.grid_columnconfigure(0, weight=1)

        self.label_status = ctk.CTkLabel(info_frame, text="Program: none", anchor="w")
        self.label_status.grid(row=0, column=0, padx=10, pady=(10, 3), sticky="ew")

        self.label_a = ctk.CTkLabel(info_frame, text="A: 0 (000000000000)", anchor="w")
        self.label_a.grid(row=1, column=0, padx=10, pady=3, sticky="ew")

        self.label_d = ctk.CTkLabel(info_frame, text="D: 0 (000000000000)", anchor="w")
        self.label_d.grid(row=2, column=0, padx=10, pady=3, sticky="ew")

        self.label_pc = ctk.CTkLabel(info_frame, text="PC: 0", anchor="w")
        self.label_pc.grid(row=3, column=0, padx=10, pady=3, sticky="ew")

        self.label_ticks = ctk.CTkLabel(info_frame, text="Ticks: 0", anchor="w")
        self.label_ticks.grid(row=4, column=0, padx=10, pady=3, sticky="ew")

        self.label_instruction = ctk.CTkLabel(info_frame, text="Instruction: —", anchor="w")
        self.label_instruction.grid(row=5, column=0, padx=10, pady=(3, 10), sticky="ew")

    def load_program(self):
        path = filedialog.askopenfilename(
            title="Select Ternary Program",
            filetypes=[("Ternary text", "*.txt"), ("Binary program", "*.bin"), ("All files", "*")],
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
        self.pause_button.configure(state="disabled")
        self.run_button.configure(state="normal")

    def refresh_program_list(self):
        for label in self.program_labels:
            label.destroy()
        self.program_labels.clear()

        for index, instruction in enumerate(self.emulator.program):
            label = ctk.CTkLabel(
                self.program_frame,
                text=f"{index:04d}: {instruction}",
                anchor="w",
                width=220,
                fg_color="transparent",
                corner_radius=8,
            )
            label.grid(row=index, column=0, padx=5, pady=2, sticky="ew")
            self.program_labels.append(label)

        self.highlight_current_instruction()
        self.label_status.configure(text=f"Program: {len(self.emulator.program)} instructions")

    def highlight_current_instruction(self):
        index = self.emulator.pc - MIN_ADDR
        for idx, label in enumerate(self.program_labels):
            if idx == index:
                label.configure(fg_color="#2f95ff", text_color="white")
            else:
                label.configure(fg_color="transparent", text_color="white")

    def update_debug(self):
        a_trits = int_to_trits(self.emulator.a, 12)
        d_trits = int_to_trits(self.emulator.d, 12)
        index = self.emulator.pc - MIN_ADDR
        current_instruction = "—"
        if 0 <= index < len(self.emulator.program):
            current_instruction = self.emulator.program[index]

        self.label_a.configure(text=f"A: {self.emulator.a} ({a_trits})")
        self.label_d.configure(text=f"D: {self.emulator.d} ({d_trits})")
        self.label_pc.configure(text=f"PC: {self.emulator.pc} (idx {index})")
        self.label_ticks.configure(text=f"Ticks: {self.emulator.ticks}")
        self.label_instruction.configure(text=f"Instruction: {current_instruction}")
        self.highlight_current_instruction()

    def reset_emulator(self):
        self.emulator.reset()
        self.running = False
        if self.after_id is not None:
            self.root.after_cancel(self.after_id)
            self.after_id = None
        self.update_debug()
        self.pause_button.configure(state="disabled")
        self.run_button.configure(state="normal")

    def step_emulator(self):
        if not self.emulator.program:
            return

        index = self.emulator.pc - MIN_ADDR
        if not (0 <= index < len(self.emulator.program)):
            return

        self.emulator.step()
        self.update_debug()

    def start_running(self):
        if not self.emulator.program or self.running:
            return

        self.running = True
        self.pause_button.configure(state="normal")
        self.run_button.configure(state="disabled")
        self.schedule_step()

    def pause_running(self):
        if self.after_id is not None:
            self.root.after_cancel(self.after_id)
            self.after_id = None
        self.running = False
        self.run_button.configure(state="normal")
        self.pause_button.configure(state="disabled")

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
    gui = EmulatorGUI()
    gui.run()
