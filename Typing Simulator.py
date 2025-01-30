import tkinter as tk
from tkinter import ttk
import pyautogui
import keyboard
import time
import random
import threading

class TypingSimulatorApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Typing Simulator")

        # Text input
        self.text_label = tk.Label(root, text="Enter text to type:")
        self.text_label.pack(pady=5)
        self.text_input = tk.Text(root, height=10, width=50)
        self.text_input.pack(pady=5)

        # Hotkey input
        self.hotkey_label = tk.Label(root, text="Set hotkey (e.g., ctrl+shift+t):")
        self.hotkey_label.pack(pady=5)
        self.hotkey_entry = tk.Entry(root, width=20)
        self.hotkey_entry.pack(pady=5)
        self.hotkey_entry.insert(0, "ctrl+shift+t")  # Default hotkey

        # Speed selection
        self.speed_label = tk.Label(root, text="Select typing speed (WPM):")
        self.speed_label.pack(pady=5)
        self.speed_var = tk.StringVar(value="30")  # Default speed
        self.speed_options = ttk.Combobox(root, textvariable=self.speed_var, values=["10", "20", "30", "40", "50", "60"])
        self.speed_options.pack(pady=5)

        # Start button
        self.start_button = tk.Button(root, text="Set Hotkey and Start Listening", command=self.start_listening)
        self.start_button.pack(pady=10)

        # Status label
        self.status_label = tk.Label(root, text="Status: Not listening")
        self.status_label.pack(pady=5)

        # Variables
        self.hotkey = None
        self.text_to_type = ""
        self.typing_speed = 30  # Default speed in WPM
        self.is_typing = False  # Flag to track if typing is active
        self.stop_typing = False  # Flag to stop typing

    def start_listening(self):
        # Get the hotkey, text, and speed from the GUI
        self.hotkey = self.hotkey_entry.get().strip()
        self.text_to_type = self.text_input.get("1.0", tk.END).strip()
        self.typing_speed = int(self.speed_var.get())  # Get selected speed

        if not self.hotkey:
            self.status_label.config(text="Error: Please enter a hotkey.")
            return
        if not self.text_to_type:
            self.status_label.config(text="Error: Please enter some text to type.")
            return

        # Set the hotkey
        try:
            keyboard.remove_hotkey(self.hotkey)  # Remove previous hotkey if any
        except:
            pass
        keyboard.add_hotkey(self.hotkey, self.toggle_typing)

        # Update status
        self.status_label.config(text=f"Status: Listening for hotkey ({self.hotkey}) at {self.typing_speed} WPM. Press {self.hotkey} to start/stop typing.")

    def toggle_typing(self):
        """
        Toggles typing on/off when the hotkey is pressed.
        """
        if self.is_typing:
            self.stop_typing = True  # Stop typing
            self.is_typing = False
            self.status_label.config(text=f"Status: Typing stopped. Press {self.hotkey} to resume.")
        else:
            self.stop_typing = False  # Start typing
            self.is_typing = True
            self.status_label.config(text=f"Status: Typing in progress. Press {self.hotkey} to stop.")
            threading.Thread(target=self.type_text, daemon=True).start()  # Run typing in a separate thread

    def type_text(self):
        """
        Simulates typing the text into the currently focused text box with natural variations.
        """
        time.sleep(1)  # Give the user 1 second to focus on the text box

        # Base delay based on typing speed (WPM)
        base_delay = 60 / (self.typing_speed * 5)

        for char in self.text_to_type:
            if self.stop_typing:  # Stop typing if the flag is set
                break

            # Add small random variation to the delay
            delay = base_delay * random.uniform(0.8, 1.2)  # Vary delay by ±20%
            time.sleep(delay)

            # Simulate a miss-click with 5% probability
            if random.random() < 0.05:  # 5% chance of a miss-click
                wrong_char = random.choice("abcdefghijklmnopqrstuvwxyz")  # Random wrong character
                pyautogui.write(wrong_char)
                time.sleep(random.uniform(0.1, 0.3))  # Pause before deleting
                pyautogui.press("backspace")  # Delete the wrong character
                time.sleep(random.uniform(0.1, 0.3))  # Pause before typing the correct character

            # Type the correct character
            pyautogui.write(char)

        # Reset flags after typing is done or stopped
        self.is_typing = False
        self.stop_typing = False
        self.status_label.config(text=f"Status: Typing finished. Press {self.hotkey} to start again.")

if __name__ == "__main__":
    root = tk.Tk()
    app = TypingSimulatorApp(root)
    root.mainloop()