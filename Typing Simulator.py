import tkinter as tk
from tkinter import ttk
import pyautogui
import keyboard
import time
import random
import threading

class CustomButton(tk.Canvas):
    def __init__(self, parent, text, command=None, width=200, height=40, bg="#4a90e2", fg="#FFFFFF", 
                 hover_bg="#357abd", hover_fg="#FFFFFF", corner_radius=10):
        super().__init__(parent, width=width, height=height, bg=parent["bg"], 
                        highlightthickness=0, relief='ridge')
        
        self.command = command
        self.bg = bg
        self.fg = fg
        self.hover_bg = hover_bg
        self.hover_fg = hover_fg
        self.corner_radius = corner_radius
        self.text = text
        
        # Draw initial button
        self.draw_button(self.bg, self.fg)
        
        # Bind events
        self.bind("<Enter>", self.on_enter)
        self.bind("<Leave>", self.on_leave)
        self.bind("<Button-1>", self.on_click)
        
    def draw_button(self, bg, fg):
        self.delete("all")
        # Draw rounded rectangle
        self.create_rounded_rect(0, 0, self.winfo_reqwidth(), self.winfo_reqheight(), 
                               self.corner_radius, fill=bg)
        # Draw text centered
        font_size = 16 if len(self.text) <= 2 else 10  # Larger font for emojis
        self.create_text(self.winfo_reqwidth()/2, self.winfo_reqheight()/2, 
                        text=self.text, fill=fg, 
                        font=("Segoe UI Emoji", font_size),  # Changed font to better support emojis
                        anchor="center", justify="center")  # Ensure center alignment
    
    def create_rounded_rect(self, x1, y1, x2, y2, radius, **kwargs):
        points = [
            x1 + radius, y1,
            x2 - radius, y1,
            x2, y1,
            x2, y1 + radius,
            x2, y2 - radius,
            x2, y2,
            x2 - radius, y2,
            x1 + radius, y2,
            x1, y2,
            x1, y2 - radius,
            x1, y1 + radius,
            x1, y1
        ]
        return self.create_polygon(points, smooth=True, **kwargs)
    
    def on_enter(self, e):
        self.draw_button(self.hover_bg, self.hover_fg)
        
    def on_leave(self, e):
        self.draw_button(self.bg, self.fg)
        
    def on_click(self, e):
        if self.command:
            self.command()

class CustomTextBox(tk.Canvas):
    def __init__(self, parent, width=300, height=150, bg="#FFFFFF", fg="#000000", 
                 corner_radius=10, padding=10):
        super().__init__(parent, width=width, height=height, bg=parent["bg"], 
                        highlightthickness=0, relief='ridge')
        
        self.bg = bg
        self.fg = fg
        self.corner_radius = corner_radius
        self.padding = padding
        
        # Create text widget
        self.text = tk.Text(self, wrap=tk.WORD, bg=bg, fg=fg, 
                           insertbackground=fg, selectbackground="#4a90e2",
                           selectforeground="#FFFFFF", relief='flat', 
                           font=("Helvetica", 10),
                           width=1, height=1)
        
        # Draw the background
        self.draw_background()
        
        # Place the text widget
        self.text.place(x=padding, y=padding, 
                       width=width-2*padding, 
                       height=height-2*padding)
    
    def draw_background(self):
        self.delete("background")
        self.create_rounded_rect(0, 0, self.winfo_width(), self.winfo_height(), 
                               self.corner_radius, fill=self.bg, tags="background")
    
    def create_rounded_rect(self, x1, y1, x2, y2, radius, **kwargs):
        points = [
            x1 + radius, y1,
            x2 - radius, y1,
            x2, y1,
            x2, y1 + radius,
            x2, y2 - radius,
            x2, y2,
            x2 - radius, y2,
            x1 + radius, y2,
            x1, y2,
            x1, y2 - radius,
            x1, y1 + radius,
            x1, y1
        ]
        return self.create_polygon(points, smooth=True, **kwargs)

    def get(self, *args):
        return self.text.get(*args)

    def insert(self, *args):
        return self.text.insert(*args)

class TypingSimulatorApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Typing Simulator")
        
        # Dark mode state
        self.dark_mode = False
        self.light_theme = {
            "bg": "#f0f0f0",
            "fg": "#333333",
            "button_bg": "#4a90e2",
            "button_fg": "#FFFFFF",
            "entry_bg": "#FFFFFF",
            "status_fg": "#666666",
            "icon_color": "#666666"  # Grey color for moon in light mode
        }
        self.dark_theme = {
            "bg": "#1e1e1e",
            "fg": "#FFFFFF",
            "button_bg": "#404040",
            "button_fg": "#FFFFFF",
            "entry_bg": "#2d2d2d",
            "status_fg": "#a0a0a0",
            "icon_color": "#FFFFFF"  # Changed to white for sun in dark mode
        }
        self.current_theme = self.light_theme
        
        self.root.configure(bg=self.current_theme["bg"])

        # Main container
        main_frame = tk.Frame(root, bg=self.current_theme["bg"], padx=20, pady=20)
        main_frame.pack(expand=True, fill='both')

        # Dark mode toggle icon in top right
        self.theme_icon = tk.Label(
            main_frame, 
            text="🌙",
            font=("Segoe UI Emoji", 16),
            bg=self.current_theme["bg"],
            fg=self.current_theme["icon_color"],
            cursor="hand2"  # Change cursor to hand when hovering
        )
        self.theme_icon.pack(anchor='ne', padx=5, pady=5)
        self.theme_icon.bind("<Button-1>", lambda e: self.toggle_theme())

        # Text input
        self.text_label = tk.Label(main_frame, text="Enter text to type:", 
                                 font=("Helvetica", 12, "bold"),
                                 bg=self.current_theme["bg"], 
                                 fg=self.current_theme["fg"])
        self.text_label.pack(pady=5)
        
        self.text_input = CustomTextBox(main_frame, width=600, height=300,
                                      bg=self.current_theme["entry_bg"],
                                      fg=self.current_theme["fg"])
        self.text_input.pack(pady=10)

        # Hotkey input
        hotkey_frame = tk.Frame(main_frame, bg=self.current_theme["bg"])
        hotkey_frame.pack(fill='x', pady=10)
        
        self.hotkey_label = tk.Label(hotkey_frame, text="Set hotkey:", 
                                   font=("Helvetica", 12, "bold"),
                                   bg=self.current_theme["bg"], 
                                   fg=self.current_theme["fg"])
        self.hotkey_label.pack(side='left', padx=5)
        
        self.hotkey_entry = tk.Entry(hotkey_frame, width=15, 
                                   font=("Helvetica", 10),
                                   relief='flat',
                                   bg=self.current_theme["entry_bg"],
                                   fg=self.current_theme["fg"],
                                   highlightthickness=1,
                                   highlightbackground=self.current_theme["button_bg"])
        self.hotkey_entry.pack(side='left', padx=5)
        self.hotkey_entry.insert(0, "ctrl+q")

        # Pause hotkey input
        pause_frame = tk.Frame(main_frame, bg=self.current_theme["bg"])
        pause_frame.pack(fill='x', pady=10)

        self.pause_hotkey_label = tk.Label(pause_frame, text="Pause/Resume hotkey:", 
                                          font=("Helvetica", 12, "bold"),
                                          bg=self.current_theme["bg"], 
                                          fg=self.current_theme["fg"])
        self.pause_hotkey_label.pack(side='left', padx=5)

        self.pause_hotkey_entry = tk.Entry(pause_frame, width=15, 
                                          font=("Helvetica", 10),
                                          relief='flat',
                                          bg=self.current_theme["entry_bg"],
                                          fg=self.current_theme["fg"],
                                          highlightthickness=1,
                                          highlightbackground=self.current_theme["button_bg"])
        self.pause_hotkey_entry.pack(side='left', padx=5)
        self.pause_hotkey_entry.insert(0, "ctrl+p")

        # Speed selection
        speed_frame = tk.Frame(main_frame, bg=self.current_theme["bg"])
        speed_frame.pack(fill='x', pady=10)
        
        self.speed_label = tk.Label(speed_frame, text="Typing speed (WPM):", 
                                  font=("Helvetica", 12, "bold"),
                                  bg=self.current_theme["bg"], 
                                  fg=self.current_theme["fg"])
        self.speed_label.pack(side='left', padx=5)
        
        self.speed_var = tk.StringVar(value="30")
        self.speed_options = ttk.Combobox(speed_frame, textvariable=self.speed_var,
                                        values=["10", "20", "30", "40", "50", "60", "70", "80", 
                                               "90", "100", "120", "140", "160", "180", "200"],
                                        width=10, font=("Helvetica", 10))
        self.speed_options.pack(side='left', padx=5)

        # Start button
        self.start_button = CustomButton(main_frame, text="Start Listening",
                                       width=250, height=40,
                                       bg=self.current_theme["button_bg"],
                                       fg=self.current_theme["button_fg"],
                                       command=self.start_listening)
        self.start_button.pack(pady=20)

        # Status label
        self.status_label = tk.Label(main_frame, text="Status: Not listening",
                                   font=("Helvetica", 10),
                                   bg=self.current_theme["bg"], 
                                   fg=self.current_theme["status_fg"])
        self.status_label.pack(pady=5)

        # Variables
        self.hotkey = None
        self.pause_hotkey = None
        self.text_to_type = ""
        self.typing_speed = 30
        self.is_typing = False
        self.stop_typing = False
        self.paused = False

        # Style the window
        self.root.geometry("750x800")
        self.root.resizable(False, False)

    def toggle_theme(self):
        """Toggle between light and dark mode"""
        self.dark_mode = not self.dark_mode
        self.current_theme = self.dark_theme if self.dark_mode else self.light_theme
        
        # Update icon and its color
        self.theme_icon.configure(
            text="☀️" if self.dark_mode else "🌙",
            bg=self.current_theme["bg"],
            fg=self.current_theme["icon_color"]
        )
        
        # Update window background
        self.root.configure(bg=self.current_theme["bg"])
        
        # Update all frames
        for widget in self.root.winfo_children():
            if isinstance(widget, tk.Frame):
                widget.configure(bg=self.current_theme["bg"])
                for child in widget.winfo_children():
                    if isinstance(child, tk.Frame):
                        child.configure(bg=self.current_theme["bg"])
        
        # Update labels
        self.text_label.configure(bg=self.current_theme["bg"], 
                                fg=self.current_theme["fg"])
        self.hotkey_label.configure(bg=self.current_theme["bg"], 
                                  fg=self.current_theme["fg"])
        self.pause_hotkey_label.configure(bg=self.current_theme["bg"], 
                                        fg=self.current_theme["fg"])
        self.speed_label.configure(bg=self.current_theme["bg"], 
                                 fg=self.current_theme["fg"])
        self.status_label.configure(bg=self.current_theme["bg"], 
                                  fg=self.current_theme["status_fg"])
        
        # Update entry fields
        self.hotkey_entry.configure(bg=self.current_theme["entry_bg"],
                                  fg=self.current_theme["fg"],
                                  highlightbackground=self.current_theme["button_bg"])
        self.pause_hotkey_entry.configure(bg=self.current_theme["entry_bg"],
                                        fg=self.current_theme["fg"],
                                        highlightbackground=self.current_theme["button_bg"])
        
        # Update text box
        self.text_input.bg = self.current_theme["entry_bg"]
        self.text_input.fg = self.current_theme["fg"]
        self.text_input.text.configure(
            bg=self.current_theme["entry_bg"],
            fg=self.current_theme["fg"],
            insertbackground=self.current_theme["fg"]  # Update cursor color to match text
        )
        self.text_input.draw_background()
        
        # Update buttons
        self.start_button.bg = self.current_theme["button_bg"]
        self.start_button.fg = self.current_theme["button_fg"]
        self.start_button.draw_button(self.current_theme["button_bg"], 
                                    self.current_theme["button_fg"])

    def start_listening(self):
        """Start listening for the hotkey"""
        try:
            # Unregister previous hotkey if it exists
            if self.hotkey:
                keyboard.remove_hotkey(self.hotkey)
            if self.pause_hotkey:
                keyboard.remove_hotkey(self.pause_hotkey)
            
            # Get the new hotkey
            hotkey = self.hotkey_entry.get().strip()
            if not hotkey:
                return
            
            # Register new hotkey
            self.hotkey = keyboard.add_hotkey(hotkey, self.start_typing)
            
            # Update status
            self.status_label.config(text=f"Status: Listening for '{hotkey}'")
            
            # Get typing speed
            self.typing_speed = int(self.speed_var.get())
            
            # Get text to type
            self.text_to_type = self.text_input.get("1.0", tk.END).strip()

            # Register pause/resume hotkey
            pause_hotkey_value = self.pause_hotkey_entry.get().strip()
            if pause_hotkey_value:
                self.pause_hotkey = keyboard.add_hotkey(pause_hotkey_value, self.toggle_pause)
            
        except Exception as e:
            self.status_label.config(text=f"Error: {str(e)}")

    def start_typing(self):
        """Start typing the text"""
        if self.is_typing or not self.text_to_type:
            return
        
        def type_text():
            self.is_typing = True
            time.sleep(0.5)
            self.stop_typing = False
            self.paused = False
            
            try:
                # Calculate delay between characters based on WPM
                delay = 60 / (self.typing_speed * 5)  # Average word length is 5 characters
                
                for char in self.text_to_type:
                    if self.stop_typing:
                        break
                    # If paused, wait until resumed or stopped
                    while self.paused and not self.stop_typing:
                        time.sleep(0.1)
                    
                    # 5% chance to make a typo
                    if random.random() < 0.05:
                        # Get a "nearby" key on the keyboard
                        nearby_keys = {
                            'a': 'sq', 'b': 'vn', 'c': 'xv', 'd': 'sf', 'e': 'wr', 'f': 'dg', 
                            'g': 'fh', 'h': 'gj', 'i': 'uo', 'j': 'hk', 'k': 'jl', 'l': 'k;',
                            'm': 'n,', 'n': 'bm', 'o': 'ip', 'p': 'o[', 'q': 'wa', 'r': 'et',
                            's': 'ad', 't': 'ry', 'u': 'yi', 'v': 'cb', 'w': 'qe', 'x': 'zc',
                            'y': 'tu', 'z': 'xs'
                        }
                        
                        if char.lower() in nearby_keys:
                            # Type wrong character
                            wrong_char = random.choice(nearby_keys[char.lower()])
                            if char.isupper():
                                wrong_char = wrong_char.upper()
                            pyautogui.write(wrong_char)
                            
                            # Wait a bit before correcting
                            time.sleep(delay * random.uniform(1.0, 1.5))
                            
                            # Delete the mistake
                            pyautogui.press('backspace')
                            
                            # Wait a bit before typing correct character
                            time.sleep(delay * random.uniform(0.8, 1.2))
                    
                    # Type the correct character
                    pyautogui.write(char)
                    
                    # Add random variation to timing
                    time.sleep(delay * random.uniform(0.8, 1.2))
                    
            except Exception as e:
                self.status_label.config(text=f"Error: {str(e)}")
            
            finally:
                self.is_typing = False
        
        # Start typing in a separate thread
        threading.Thread(target=type_text, daemon=True).start()

    def stop_typing_text(self):
        """Stop the typing process"""
        self.stop_typing = True
        self.paused = False

    def toggle_pause(self):
        """Toggle pause/resume while typing"""
        if not self.is_typing:
            return
        self.paused = not self.paused
        if self.paused:
            self.status_label.config(text="Status: Paused")
        else:
            self.status_label.config(text="Status: Typing...")

if __name__ == "__main__":
    root = tk.Tk()
    app = TypingSimulatorApp(root)
    root.mainloop()