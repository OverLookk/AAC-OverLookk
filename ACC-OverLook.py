import ctypes
import time
import threading
import tkinter as tk
from tkinter import ttk
from pynput import keyboard

class AutoClicker:
    def __init__(self, root):
        self.root = root
        self.is_running = False
        self.click_interval_ms = 100  # Default interval between clicks in milliseconds
        self.click_duration_secs = 0  # Duration in seconds
        self.thread = None
        self.toggle_key = "f4"  # Default toggle key to F4
        self.click_button = "left"  # Default click button
        self.listener = None

        # Lock window size
        root.resizable(False, False)  # Disable window resizing

        # Validation for numeric input
        vcmd = (root.register(self.validate_entry), '%P')

        # Main frame
        main_frame = ttk.Frame(root, padding="10 10 10 10")
        main_frame.grid(column=0, row=0, sticky=(tk.W, tk.E, tk.N, tk.S))

        # Click Interval Section
        ttk.Label(main_frame, text="Click Interval:").grid(column=1, row=1, sticky=tk.W)

        self.entry_interval_mins = ttk.Entry(main_frame, width=5, validate='key', validatecommand=vcmd)
        self.entry_interval_mins.insert(0, "0")
        self.entry_interval_mins.grid(column=2, row=1, sticky=tk.W)

        ttk.Label(main_frame, text="mins").grid(column=3, row=1, sticky=tk.W)

        self.entry_interval_secs = ttk.Entry(main_frame, width=5, validate='key', validatecommand=vcmd)
        self.entry_interval_secs.insert(0, "0")
        self.entry_interval_secs.grid(column=4, row=1, sticky=tk.W)

        ttk.Label(main_frame, text="secs").grid(column=5, row=1, sticky=tk.W)

        self.entry_interval_ms = ttk.Entry(main_frame, width=5, validate='key', validatecommand=vcmd)
        self.entry_interval_ms.insert(0, "100")
        self.entry_interval_ms.grid(column=6, row=1, sticky=tk.W)

        ttk.Label(main_frame, text="ms").grid(column=7, row=1, sticky=tk.W)

        self.entry_interval_us = ttk.Entry(main_frame, width=5, validate='key', validatecommand=vcmd)
        self.entry_interval_us.insert(0, "0")
        self.entry_interval_us.grid(column=8, row=1, sticky=tk.W)

        ttk.Label(main_frame, text="μs").grid(column=9, row=1, sticky=tk.W)

        # Click Duration Section
        ttk.Label(main_frame, text="Click Duration (seconds):").grid(column=1, row=2, sticky=tk.W, columnspan=2)

        self.entry_duration_secs = ttk.Entry(main_frame, width=10, validate='key', validatecommand=vcmd)
        self.entry_duration_secs.insert(0, "0")
        self.entry_duration_secs.grid(column=4, row=2, sticky=tk.W, columnspan=5)

        # Mouse Button Section
        ttk.Label(main_frame, text="Mouse Button 0 = inf:").grid(column=1, row=3, sticky=tk.W, columnspan=2)

        self.button_option = tk.StringVar(root)
        self.button_option.set("left")  # default value
        self.dropdown_button = ttk.Combobox(main_frame, textvariable=self.button_option, values=["left", "middle", "right"], state="readonly")
        self.dropdown_button.grid(column=4, row=3, sticky=tk.W, columnspan=5)

        # Toggle Key Section
        self.label_toggle_key = ttk.Label(main_frame, text=f"Toggle Key (current: {self.toggle_key.upper()}):")
        self.label_toggle_key.grid(column=1, row=4, sticky=tk.W, columnspan=3)

        self.configure_key_button = ttk.Button(main_frame, text="Change Toggle Key", command=self.configure_toggle_key)
        self.configure_key_button.grid(column=4, row=4, sticky=tk.W, columnspan=3)

        # Start/Stop Button with Countdown Timer in Button Text
        self.toggle_button = ttk.Button(main_frame, text="Start Auto Clicker", command=self.start_with_delay)
        self.toggle_button.grid(column=7, row=4, sticky=tk.W, columnspan=3)

        # Status Label
        self.status_label = ttk.Label(main_frame, text="Status: Stopped")
        self.status_label.grid(column=1, row=5, sticky=tk.W, columnspan=9)

        # Padding between elements
        for child in main_frame.winfo_children():
            child.grid_configure(padx=5, pady=5)

    def validate_entry(self, new_value):
        # Allow empty value (clearing the entry)
        if new_value == "":
            return True
        # Allow only numbers and one period
        try:
            float(new_value)
            if new_value.count('.') > 1:
                return False
            return True
        except ValueError:
            return False

    def start_with_delay(self):
        self.toggle_button.config(state=tk.DISABLED)  # Disable the button
        self.start_countdown(0.7)  # Start the countdown for 0.7 seconds

    def start_countdown(self, time_left):
        if time_left > 0:
            self.toggle_button.config(text=f"Start Auto Clicker ({time_left:.1f})")
            self.root.after(100, self.start_countdown, time_left - 0.1)
        else:
            self.toggle_button.config(state=tk.NORMAL, text="Start Auto Clicker")
            self.toggle_auto_click()  # Proceed with starting the auto clicker

    def fast_click(self):
        # Use Windows API for mouse events
        mouse_event = ctypes.windll.user32.mouse_event
        button_flag_down = {"left": 0x0002, "middle": 0x0020, "right": 0x0008}
        button_flag_up = {"left": 0x0004, "middle": 0x0040, "right": 0x0010}

        end_time = time.time() + self.click_duration_secs if self.click_duration_secs > 0 else float('inf')
        while self.is_running and time.time() < end_time:
            mouse_event(button_flag_down[self.click_button], 0, 0, 0, 0)
            mouse_event(button_flag_up[self.click_button], 0, 0, 0, 0)
            time.sleep(self.click_interval_ms / 1000.0)

    def start_listener(self):
        # Start the keyboard listener for toggling
        def on_press(key):
            try:
                if key.char == self.toggle_key:
                    self.toggle_auto_click()
            except AttributeError:
                if key == keyboard.Key[self.toggle_key]:
                    self.toggle_auto_click()

        self.listener = keyboard.Listener(on_press=on_press)
        self.listener.start()

    def configure_toggle_key(self):
        self.status_label.config(text="Press a key to set as the new toggle key...")

        def on_press(key):
            try:
                self.toggle_key = key.char
            except AttributeError:
                self.toggle_key = key.name
            self.label_toggle_key.config(text=f"Toggle Key (current: {self.toggle_key.upper()}):")
            self.status_label.config(text="Status: Stopped")
            self.listener.stop()

        self.listener = keyboard.Listener(on_press=on_press)
        self.listener.start()

    def calculate_total_time(self, mins, secs, ms, us):
        return (mins * 60) + secs + (ms / 1000) + (us / 1000000)

    def toggle_auto_click(self):
        if self.is_running:
            self.is_running = False
            self.toggle_button.config(text="Start Auto Clicker", state=tk.NORMAL)
            self.status_label.config(text="Status: Stopped")
        else:
            try:
                # Calculate the click interval
                interval_mins = float(self.entry_interval_mins.get())
                interval_secs = float(self.entry_interval_secs.get())
                interval_ms = float(self.entry_interval_ms.get())
                interval_us = float(self.entry_interval_us.get())
                self.click_interval_ms = self.calculate_total_time(interval_mins, interval_secs, interval_ms, interval_us) * 1000

                # Get the duration in seconds
                self.click_duration_secs = float(self.entry_duration_secs.get())

                self.click_button = self.button_option.get().lower()  # Get the mouse button from the dropdown
                self.is_running = True
                self.toggle_button.config(text="Stop Auto Clicker")
                self.status_label.config(text="Status: Running")
                # Start clicking in a separate thread to avoid freezing the UI
                self.thread = threading.Thread(target=self.fast_click)
                self.thread.start()
            except ValueError:
                self.status_label.config(text="Please enter valid numbers for the interval and duration.")

if __name__ == "__main__":
    # Create the main application window
    root = tk.Tk()
    root.title("Advanced Auto Clicker by: @overlookk on github")

    # Lock the window size
    root.resizable(False, False)

   

 # Apply a more modern theme (requires ttkthemes package)
    try:
        import ttkthemes
        root.style = ttkthemes.ThemedStyle(root)
        root.style.set_theme("equilux")  # You can choose different themes
    except ImportError:
        pass  # Continue with default theme if ttkthemes is not installed

    # Create the AutoClicker instance and run the main loop
    app = AutoClicker(root)
    app.start_listener()  # Start listening for the toggle key
    root.mainloop()