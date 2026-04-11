import tkinter as tk
from tkinter import filedialog, messagebox
import sys

import customtkinter as ctk
from ternary.hardware.emulator import Emulator
from ternary.hardware.util import int_to_trits, MIN_ADDR, input_stream

LOAD_BUTTON_LABEL = "📂 Load"
RESET_BUTTON_LABEL = "↺ Reset"
STEP_BUTTON_LABEL = "⏭ Step"
RUN_BUTTON_LABEL = "▶ Run"
PAUSE_BUTTON_LABEL = "⏸ Pause"
CONTROL_BUTTON_WIDTH = 120
SPEED_MIN_HZ = 1
SPEED_MAX_HZ = 1_000_000


def format_frequency_hz(hz):
    """Convert Hz to human-readable format (Hz, kHz, or MHz)."""
    if hz >= 1_000_000:
        return f"{hz / 1_000_000:.0f} MHz"
    elif hz >= 1_000:
        return f"{hz / 1_000:.0f} kHz"
    else:
        return f"{hz} Hz"


class EmulatorGUI:
    def __init__(self, input_path=None):
        ctk.set_appearance_mode("system")
        ctk.set_default_color_theme("blue")

        self.root = ctk.CTk()
        self.root.title("Ternary Computer Emulator")
        self.root.geometry("1100x700")

        self.emulator = Emulator()
        self.program_rows = []
        self.running = False
        self.after_id = None
        self.speed_hz = 1000
        self.mono_font = ("Courier New", 11)

        self.create_layout()
        self.update_tray()

        if input_path:
            self.root.after(100, lambda: self.load_program_from_path(input_path))

    def create_layout(self):
        main_frame = ctk.CTkFrame(self.root)
        main_frame.pack(fill="both", expand=True, padx=10, pady=10)
        main_frame.grid_rowconfigure(0, weight=1)
        main_frame.grid_rowconfigure(1, weight=0)
        main_frame.grid_columnconfigure(1, weight=1)

        left_frame = ctk.CTkFrame(main_frame, width=288)
        left_frame.grid(row=0, column=0, sticky="ns", padx=5, pady=5)
        left_frame.grid_rowconfigure(0, weight=1)

        self.program_frame = ctk.CTkScrollableFrame(left_frame, width=364, height=600)
        self.program_frame.grid(row=0, column=0, padx=10, pady=10, sticky="nsew")
        self.program_frame.grid_columnconfigure(1, weight=1)

        canvas_frame = ctk.CTkFrame(main_frame)
        canvas_frame.grid(row=0, column=1, sticky="nsew", padx=5, pady=5)
        canvas_frame.grid_rowconfigure(0, weight=1)
        canvas_frame.grid_columnconfigure(0, weight=1)

        self.canvas = tk.Canvas(
            canvas_frame,
            width=640,
            height=400,
            bg="black",
            highlightthickness=1,
            highlightbackground="#777",
        )
        self.canvas.grid(row=0, column=0, sticky="", padx=10, pady=10)

        self.system_tray_frame = ctk.CTkFrame(main_frame, height=80)
        self.system_tray_frame.grid(row=1, column=0, columnspan=2, sticky="nsew", padx=5, pady=5)
        self.system_tray_frame.grid_columnconfigure(0, weight=1)
        self.system_tray_frame.grid_columnconfigure(1, weight=1)

        control_frame = ctk.CTkFrame(self.system_tray_frame)
        control_frame.grid(row=0, column=0, columnspan=2, sticky="ew", padx=10, pady=(10, 5))
        control_frame.grid_columnconfigure((0, 1, 2, 3, 4), weight=1)

        self.load_button = ctk.CTkButton(control_frame, text=LOAD_BUTTON_LABEL, command=self.load_program, width=CONTROL_BUTTON_WIDTH)
        self.load_button.grid(row=0, column=0, padx=5, pady=5, sticky="ew")

        self.reset_button = ctk.CTkButton(control_frame, text=RESET_BUTTON_LABEL, command=self.reset_emulator, state="disabled", width=CONTROL_BUTTON_WIDTH)
        self.reset_button.grid(row=0, column=1, padx=5, pady=5, sticky="ew")

        self.step_button = ctk.CTkButton(control_frame, text=STEP_BUTTON_LABEL, command=self.step_emulator, state="disabled", width=CONTROL_BUTTON_WIDTH)
        self.step_button.grid(row=0, column=2, padx=5, pady=5, sticky="ew")

        self.run_button = ctk.CTkButton(control_frame, text=RUN_BUTTON_LABEL, command=self.toggle_running, state="disabled", width=CONTROL_BUTTON_WIDTH)
        self.run_button.grid(row=0, column=3, padx=5, pady=5, sticky="ew")

        self.speed_button = ctk.CTkButton(control_frame, text=self.get_speed_button_text(), command=self.open_speed_dialog, width=CONTROL_BUTTON_WIDTH)
        self.speed_button.grid(row=0, column=4, padx=5, pady=5, sticky="ew")

        tray_items_frame = ctk.CTkFrame(self.system_tray_frame)
        tray_items_frame.grid(row=1, column=0, columnspan=2, sticky="nsew", padx=10, pady=(5, 10))
        tray_items_frame.grid_columnconfigure((0, 1, 2, 3, 4), weight=1)

        def create_register_item(parent, label_text):
            item_frame = ctk.CTkFrame(parent, fg_color="transparent")
            item_frame.grid_columnconfigure(0, weight=0)
            item_frame.grid_columnconfigure(1, weight=0)
            
            label = ctk.CTkLabel(item_frame, text=label_text, fg_color="#404040", text_color="#a0a0a0", 
                                corner_radius=4, padx=6, pady=2, font=self.mono_font)
            label.grid(row=0, column=0, padx=(0, 4), sticky="w")
            
            value = ctk.CTkLabel(item_frame, text="0", fg_color="transparent", text_color="white",
                                anchor="w", font=self.mono_font)
            value.grid(row=0, column=1, sticky="w")
            
            return item_frame, value

        self.item_a, self.label_a = create_register_item(tray_items_frame, "A")
        self.item_a.grid(row=0, column=0, padx=5, sticky="nsew")

        self.item_d, self.label_d = create_register_item(tray_items_frame, "D")
        self.item_d.grid(row=0, column=1, padx=5, sticky="nsew")

        self.item_m, self.label_m = create_register_item(tray_items_frame, "M")
        self.item_m.grid(row=0, column=2, padx=5, sticky="nsew")

        self.item_pc, self.label_pc = create_register_item(tray_items_frame, "PC")
        self.item_pc.grid(row=0, column=3, padx=5, sticky="nsew")

        self.item_ticks, self.label_ticks = create_register_item(tray_items_frame, "Ticks")
        self.item_ticks.grid(row=0, column=4, padx=5, sticky="nsew")

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
        self.update_tray()
        self.reset_button.configure(state="normal")
        self.step_button.configure(state="normal")
        self.run_button.configure(state="normal", text=RUN_BUTTON_LABEL)

    def get_speed_button_text(self):
        return f"⚙ Speed: {format_frequency_hz(self.speed_hz)}"

    def open_speed_dialog(self):
        dialog = ctk.CTkToplevel(self.root)
        dialog.title("Adjust Speed")
        dialog.geometry("480x150")
        dialog.grab_set()
        dialog.transient(self.root)
        dialog.grid_columnconfigure(0, weight=1)
        dialog.grid_columnconfigure(1, weight=0)

        label = ctk.CTkLabel(dialog, text=f"Set execution speed ({format_frequency_hz(SPEED_MIN_HZ)} to {format_frequency_hz(SPEED_MAX_HZ)}):", anchor="w")
        label.grid(row=0, column=0, columnspan=2, padx=16, pady=(16, 8), sticky="ew")

        speed_var = tk.StringVar(value=str(self.speed_hz))

        def update_entry(value):
            speed_var.set(str(int(float(value))))

        slider = ctk.CTkSlider(dialog, from_=SPEED_MIN_HZ, to=SPEED_MAX_HZ, command=update_entry)
        slider.set(self.speed_hz)
        slider.grid(row=1, column=0, padx=16, pady=(0, 8), sticky="ew")

        input_frame = ctk.CTkFrame(dialog)
        input_frame.grid(row=1, column=1, padx=(8, 16), pady=(0, 8), sticky="ew")
        input_frame.grid_columnconfigure(0, weight=1)

        speed_entry = ctk.CTkEntry(input_frame, textvariable=speed_var, width=80)
        speed_entry.grid(row=0, column=0, padx=(0, 4), pady=5, sticky="ew")

        hz_label = ctk.CTkLabel(input_frame, text="Hz", anchor="w")
        hz_label.grid(row=0, column=1, padx=(0, 0), pady=5, sticky="w")

        def validate_speed(value_str):
            try:
                value = int(value_str)
            except ValueError:
                raise ValueError("Enter an integer value for Hz.")
            if value < SPEED_MIN_HZ or value > SPEED_MAX_HZ:
                raise ValueError(f"Speed must be between {SPEED_MIN_HZ} and {SPEED_MAX_HZ} Hz.")
            return value

        def apply_speed():
            try:
                speed_value = validate_speed(speed_var.get())
            except ValueError as exc:
                messagebox.showerror("Invalid speed", str(exc), parent=dialog)
                return
            self.speed_hz = speed_value
            self.speed_button.configure(text=self.get_speed_button_text())
            dialog.destroy()

        def on_entry_return(event):
            try:
                speed_value = validate_speed(speed_var.get())
            except ValueError:
                return
            slider.set(speed_value)

        speed_entry.bind("<Return>", on_entry_return)
        speed_entry.bind("<FocusOut>", lambda event: on_entry_return(event))

        button_frame = ctk.CTkFrame(dialog)
        button_frame.grid(row=2, column=0, columnspan=2, padx=16, pady=(0, 16), sticky="ew")
        button_frame.grid_columnconfigure((0, 1), weight=1)

        cancel_button = ctk.CTkButton(button_frame, text="Cancel", command=dialog.destroy)
        cancel_button.grid(row=0, column=0, padx=5, sticky="ew")

        ok_button = ctk.CTkButton(button_frame, text="OK", command=apply_speed)
        ok_button.grid(row=0, column=1, padx=5, sticky="ew")

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
        self.update_tray()
        self.reset_button.configure(state="normal")
        self.step_button.configure(state="normal")
        self.run_button.configure(state="normal", text=RUN_BUTTON_LABEL)

    def refresh_program_list(self):
        for inst_label, comment_label in self.program_rows:
            inst_label.destroy()
            comment_label.destroy()
        self.program_rows.clear()

        for index, instruction in enumerate(self.emulator.program):
            inst_label = ctk.CTkLabel(
                self.program_frame,
                text=f"{index:04d}: {instruction}",
                anchor="w",
                fg_color="transparent",
                corner_radius=8,
                font=self.mono_font,
            )
            inst_label.grid(row=index, column=0, sticky="ew", padx=(0, 8), pady=2)

            comment_text = self.emulator.comments.get(index, "")
            comment_label = None
            if comment_text:
                comment_label = ctk.CTkLabel(
                    self.program_frame,
                    text=comment_text,
                    anchor="w",
                    text_color="#888888",
                    fg_color="transparent",
                    font=self.mono_font,
                )
                comment_label.grid(row=index, column=1, sticky="w", pady=2)

            self.program_rows.append((inst_label, comment_label))

        self.highlight_current_instruction()

    def highlight_current_instruction(self):
        index = self.emulator.pc - MIN_ADDR
        for idx, (inst_label, _) in enumerate(self.program_rows):
            if idx == index:
                inst_label.configure(fg_color="#2f95ff", text_color="white")
            else:
                inst_label.configure(fg_color="transparent", text_color="white")

    def update_tray(self):
        a_trits = int_to_trits(self.emulator.a, 12)
        d_trits = int_to_trits(self.emulator.d, 12)
        m_value = self.emulator.get_m()
        m_trits = int_to_trits(m_value, 12)
        pc_trits = int_to_trits(self.emulator.pc, 11)

        self.label_a.configure(text=f"{self.emulator.a} ({a_trits})")
        self.label_d.configure(text=f"{self.emulator.d} ({d_trits})")
        self.label_m.configure(text=f"{m_value} ({m_trits})")
        self.label_pc.configure(text=f"{self.emulator.pc} ({pc_trits})")
        self.label_ticks.configure(text=f"{self.emulator.ticks}")
        self.highlight_current_instruction()

    def reset_emulator(self):
        self.emulator.reset()
        self.running = False
        if self.after_id is not None:
            self.root.after_cancel(self.after_id)
            self.after_id = None
        self.update_tray()
        self.run_button.configure(state="normal", text=RUN_BUTTON_LABEL)

    def step_emulator(self):
        if not self.emulator.program:
            return

        index = self.emulator.pc - MIN_ADDR
        if not (0 <= index < len(self.emulator.program)):
            return

        self.emulator.step()
        self.update_tray()

    def toggle_running(self):
        if self.running:
            self.pause_running()
        else:
            self.start_running()

    def start_running(self):
        if not self.emulator.program or self.running:
            return

        self.running = True
        self.run_button.configure(text=PAUSE_BUTTON_LABEL)
        self.schedule_step()

    def pause_running(self):
        if self.after_id is not None:
            self.root.after_cancel(self.after_id)
            self.after_id = None
        self.running = False
        self.run_button.configure(state="normal", text=RUN_BUTTON_LABEL)

    def schedule_step(self):
        if not self.running:
            return

        index = self.emulator.pc - MIN_ADDR
        if not (0 <= index < len(self.emulator.program)):
            self.pause_running()
            return

        self.emulator.step()
        self.update_tray()

        speed = self.speed_hz
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
