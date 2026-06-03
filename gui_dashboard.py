import customtkinter as ctk
import subprocess
import threading
import sys
import os

ctk.set_appearance_mode("dark")
ctk.set_default_color_theme("blue")

class StickmanDashboard:
    def __init__(self):
        self.app = ctk.CTk()
        self.app.geometry("850x600")
        self.app.title("🤖 AI Stickman Dashboard v2.0")
        
        # Subprocess tracking
        self.process = None
        self.log_thread = None
        
        # UI color scheme (Catppuccin Mocha inspired)
        self.bg_color = "#1E1E2E"
        self.sidebar_bg = "#11111B"
        self.card_bg = "#181825"
        self.accent_color = "#89B4FA"  # Light Blue
        self.stop_color = "#F38BA8"    # Pastel Red
        self.green_color = "#A6E3A1"   # Pastel Green
        self.yellow_color = "#F9E2AF"  # Pastel Yellow

        # Set main app background
        self.app.configure(fg_color=self.bg_color)
        
        # Configure Grid Layout
        self.app.grid_columnconfigure(1, weight=1)
        self.app.grid_rowconfigure(0, weight=1)

        # ----------------------------------------------------
        # SIDEBAR PANEL
        # ----------------------------------------------------
        self.sidebar = ctk.CTkFrame(self.app, width=200, corner_radius=0, fg_color=self.sidebar_bg)
        self.sidebar.grid(row=0, column=0, sticky="nsew")
        self.sidebar.grid_rowconfigure(4, weight=1) # push bottom elements
        
        # Sidebar Logo / Title
        self.logo_label = ctk.CTkLabel(self.sidebar, text="STICKMAN AI", font=("Arial", 22, "bold"), text_color=self.accent_color)
        self.logo_label.pack(pady=(30, 5))
        self.sub_label = ctk.CTkLabel(self.sidebar, text="Console Dashboard v2.0", font=("Arial", 12, "italic"), text_color="#A6ADC8")
        self.sub_label.pack(pady=(0, 25))
        
        # Sidebar navigation buttons
        self.btn_dashboard = ctk.CTkButton(self.sidebar, text="📺 Dashboard", font=("Arial", 14, "bold"), 
                                           fg_color="transparent", text_color="#CDD6F4", hover_color="#313244", 
                                           anchor="w", height=40, command=self.show_dashboard)
        self.btn_dashboard.pack(fill="x", padx=15, pady=5)
        
        self.btn_settings = ctk.CTkButton(self.sidebar, text="⚙ Settings & Config", font=("Arial", 14, "bold"), 
                                          fg_color="transparent", text_color="#CDD6F4", hover_color="#313244", 
                                          anchor="w", height=40, command=self.show_settings)
        self.btn_settings.pack(fill="x", padx=15, pady=5)
        
        self.btn_help = ctk.CTkButton(self.sidebar, text="ℹ Guide & Info", font=("Arial", 14, "bold"), 
                                      fg_color="transparent", text_color="#CDD6F4", hover_color="#313244", 
                                      anchor="w", height=40, command=self.show_help)
        self.btn_help.pack(fill="x", padx=15, pady=5)

        # Version stamp
        self.version_stamp = ctk.CTkLabel(self.sidebar, text="FPS Optimized Edition\nMulti-Threaded HUD", font=("Arial", 11), text_color="#585B70")
        self.version_stamp.pack(side="bottom", pady=20)

        # ----------------------------------------------------
        # CONTENT FRAMES
        # ----------------------------------------------------
        # Container for screens
        self.container = ctk.CTkFrame(self.app, fg_color="transparent")
        self.container.grid(row=0, column=1, sticky="nsew", padx=20, pady=20)
        self.container.grid_columnconfigure(0, weight=1)
        self.container.grid_rowconfigure(0, weight=1)
        
        self.setup_dashboard_frame()
        self.setup_settings_frame()
        self.setup_help_frame()
        
        # Show Dashboard initially
        self.show_dashboard()

        # Handle clean exit
        self.app.protocol("WM_DELETE_WINDOW", self.on_closing)

    # ----------------------------------------------------
    # TAB 1: DASHBOARD VIEW
    # ----------------------------------------------------
    def setup_dashboard_frame(self):
        self.frame_dashboard = ctk.CTkFrame(self.container, fg_color="transparent")
        self.frame_dashboard.grid(row=0, column=0, sticky="nsew")
        self.frame_dashboard.grid_columnconfigure(0, weight=3)
        self.frame_dashboard.grid_columnconfigure(1, weight=2)
        self.frame_dashboard.grid_rowconfigure(1, weight=1)

        # Header Title
        title = ctk.CTkLabel(self.frame_dashboard, text="Live Control Console", font=("Arial", 26, "bold"), text_color="#CDD6F4")
        title.grid(row=0, column=0, columnspan=2, sticky="w", pady=(0, 15))

        # LEFT COLUMN - Control and Inputs
        left_col = ctk.CTkFrame(self.frame_dashboard, fg_color="transparent")
        left_col.grid(row=1, column=0, sticky="nsew", padx=(0, 10))
        
        # Card 1: Console State Status
        status_card = ctk.CTkFrame(left_col, fg_color=self.card_bg, corner_radius=12)
        status_card.pack(fill="x", pady=(0, 15), ipady=10)
        
        status_header = ctk.CTkLabel(status_card, text="Console Telemetry Status", font=("Arial", 14, "bold"), text_color="#BAC2DE")
        status_header.pack(anchor="w", padx=15, pady=(10, 5))
        
        status_row = ctk.CTkFrame(status_card, fg_color="transparent")
        status_row.pack(fill="x", padx=15, pady=5)
        
        self.status_indicator = ctk.CTkFrame(status_row, width=15, height=15, corner_radius=7.5, fg_color=self.stop_color)
        self.status_indicator.pack(side="left", padx=(0, 10))
        
        self.status_label = ctk.CTkLabel(status_row, text="Status: OFFLINE", font=("Arial", 15, "bold"), text_color="#CDD6F4")
        self.status_label.pack(side="left")
        
        # Telemetry detail stats
        stats_frame = ctk.CTkFrame(status_card, fg_color="transparent")
        stats_frame.pack(fill="x", padx=15, pady=(5, 5))
        
        self.lbl_init_mood = ctk.CTkLabel(stats_frame, text="Initial Mood: --", font=("Arial", 12), text_color="#A6ADC8")
        self.lbl_init_mood.pack(anchor="w")
        self.lbl_curr_mood = ctk.CTkLabel(stats_frame, text="Active Sentiment Mood: --", font=("Arial", 12), text_color="#A6ADC8")
        self.lbl_curr_mood.pack(anchor="w")
        self.lbl_pid = ctk.CTkLabel(stats_frame, text="Process ID (PID): None", font=("Arial", 12), text_color="#A6ADC8")
        self.lbl_pid.pack(anchor="w")

        # Card 2: Interactive Controls
        ctrl_card = ctk.CTkFrame(left_col, fg_color=self.card_bg, corner_radius=12)
        ctrl_card.pack(fill="x", pady=0, ipady=10)
        
        ctrl_header = ctk.CTkLabel(ctrl_card, text="NLP Mood Controller", font=("Arial", 14, "bold"), text_color="#BAC2DE")
        ctrl_header.pack(anchor="w", padx=15, pady=(10, 5))
        
        # Text input field
        self.mood_entry = ctk.CTkEntry(ctrl_card, placeholder_text="Enter how you are feeling (e.g., 'I am so happy!' or 'sad day')", 
                                       font=("Arial", 13), fg_color="#1E1E2E", border_color="#313244", height=40)
        self.mood_entry.pack(fill="x", padx=15, pady=10)
        self.mood_entry.bind("<Return>", lambda event: self.send_mood_update())
        
        # Start/Stop Action Buttons
        btn_row = ctk.CTkFrame(ctrl_card, fg_color="transparent")
        btn_row.pack(fill="x", padx=15, pady=5)
        
        self.btn_start = ctk.CTkButton(btn_row, text="▶ Start Stickman", font=("Arial", 13, "bold"),
                                       fg_color=self.accent_color, hover_color="#5795F7", text_color="#11111B",
                                       height=40, command=self.start_stickman, corner_radius=8)
        self.btn_start.pack(side="left", fill="x", expand=True, padx=(0, 5))
        
        self.btn_stop = ctk.CTkButton(btn_row, text="■ Stop Console", font=("Arial", 13, "bold"),
                                      fg_color="#313244", hover_color=self.stop_color, text_color="#CDD6F4",
                                      height=40, command=self.stop_stickman, corner_radius=8, state="disabled")
        self.btn_stop.pack(side="left", fill="x", expand=True, padx=(5, 0))
        
        # Update mood button
        self.btn_update = ctk.CTkButton(ctrl_card, text="⚡ Dynamic Sentiment Injector", font=("Arial", 13, "bold"),
                                        fg_color="#313244", hover_color=self.accent_color, text_color="#CDD6F4",
                                        height=36, command=self.send_mood_update, corner_radius=8, state="disabled")
        self.btn_update.pack(fill="x", padx=15, pady=10)

        # RIGHT COLUMN - Subprocess Live Term Logs
        right_col = ctk.CTkFrame(self.frame_dashboard, fg_color=self.card_bg, corner_radius=12)
        right_col.grid(row=1, column=1, sticky="nsew", padx=(10, 0))
        right_col.grid_rowconfigure(1, weight=1)
        
        log_header = ctk.CTkLabel(right_col, text="System Log Monitor", font=("Arial", 14, "bold"), text_color="#BAC2DE")
        log_header.pack(anchor="w", padx=15, pady=(10, 5))
        
        # Scrollable Textbox for logs
        self.log_box = ctk.CTkTextbox(right_col, font=("Consolas", 11), fg_color="#11111B", border_color="#313244", corner_radius=8)
        self.log_box.pack(fill="both", expand=True, padx=15, pady=(5, 15))
        self.log_box.configure(state="disabled")
        
        self.append_log_system("System Dashboard Initialized. Ready to launch Stickman Console.")

    # ----------------------------------------------------
    # TAB 2: SETTINGS & CONFIG SLIDERS
    # ----------------------------------------------------
    def setup_settings_frame(self):
        self.frame_settings = ctk.CTkFrame(self.container, fg_color="transparent")
        
        # Header Title
        title = ctk.CTkLabel(self.frame_settings, text="Stickman Parameter Calibration", font=("Arial", 26, "bold"), text_color="#CDD6F4")
        title.pack(anchor="w", pady=(0, 15))
        
        card = ctk.CTkFrame(self.frame_settings, fg_color=self.card_bg, corner_radius=12)
        card.pack(fill="both", expand=True, ipady=10, ipadx=10)
        
        desc = ctk.CTkLabel(card, text="Adjust these properties to modify the stickman's dimensions in real-time.", 
                            font=("Arial", 13), text_color="#A6ADC8")
        desc.pack(anchor="w", padx=20, pady=(15, 10))
        
        # Helper function to generate a slider row
        def create_slider(parent, label_text, param_name, min_val, max_val, default_val):
            row = ctk.CTkFrame(parent, fg_color="transparent")
            row.pack(fill="x", padx=20, pady=10)
            
            lbl_name = ctk.CTkLabel(row, text=label_text, font=("Arial", 13, "bold"), width=150, anchor="w", text_color="#CDD6F4")
            lbl_name.pack(side="left")
            
            lbl_val = ctk.CTkLabel(row, text=str(default_val), font=("Consolas", 13), width=50, text_color=self.accent_color)
            
            def slider_callback(val):
                val_int = int(val)
                lbl_val.configure(text=str(val_int))
                self.send_config_update(param_name, val_int)
                
            slider = ctk.CTkSlider(row, from_=min_val, to=max_val, number_of_steps=max_val-min_val, height=16,
                                   fg_color="#313244", progress_color=self.accent_color, button_color=self.accent_color,
                                   command=slider_callback)
            slider.set(default_val)
            slider.pack(side="left", fill="x", expand=True, padx=10)
            lbl_val.pack(side="right")
            return slider

        # Generate structural sliders
        self.slider_thick = create_slider(card, "Neon Outline Thickness", "thickness", 2, 15, 4)
        self.slider_head  = create_slider(card, "Head Radius Size", "head_radius", 15, 65, 35)
        self.slider_body  = create_slider(card, "Body Spacing Length", "body_length", 40, 160, 90)
        self.slider_arm   = create_slider(card, "Arm Reach Length", "arm_length", 25, 120, 65)
        self.slider_leg   = create_slider(card, "Leg Stride Length", "leg_length", 30, 130, 75)

        # Reset button
        self.btn_reset = ctk.CTkButton(card, text="Reset Defaults", font=("Arial", 13, "bold"),
                                       fg_color="#313244", hover_color="#45475A", text_color="#CDD6F4",
                                       height=35, command=self.reset_sliders, width=150, corner_radius=8)
        self.btn_reset.pack(anchor="e", padx=20, pady=20)

    # ----------------------------------------------------
    # TAB 3: HELP & INSTRUCTIONS
    # ----------------------------------------------------
    def setup_help_frame(self):
        self.frame_help = ctk.CTkFrame(self.container, fg_color="transparent")
        
        # Header Title
        title = ctk.CTkLabel(self.frame_help, text="Console Operation Guide", font=("Arial", 26, "bold"), text_color="#CDD6F4")
        title.pack(anchor="w", pady=(0, 15))
        
        card = ctk.CTkScrollableFrame(self.frame_help, fg_color=self.card_bg, corner_radius=12)
        card.pack(fill="both", expand=True)
        
        instructions = (
            "🤖 AI STICKMAN GESTURE GAME INSTRUCTIONS\n"
            "==========================================================\n\n"
            "This application uses state-of-the-art Natural Language Processing (NLP) "
            "to understand your emotional sentiment and MediaPipe computer vision "
            "to track your hand movements through the webcam.\n\n"
            "1. HOW TO LAUNCH THE APP:\n"
            "   - Enter an emotional text or mood in the input field.\n"
            "   - Click the 'Start Stickman' button to activate your webcam and start rendering.\n"
            "   - Type a new text description and hit 'Enter' or click the 'Dynamic Sentiment Injector' "
            "     to instantly change the stickman's behavior live.\n\n"
            "2. WEBCAM HAND GESTURES CONTROL:\n"
            "   - 🖐 SHOW 1 FINGER:\n"
            "     The stickman enters an IDLE state, breathing gently in place. "
            "     Its neon outlines will glow in bright CYAN-TEAL.\n\n"
            "   - ✌ SHOW 2 FINGERS:\n"
            "     The stickman walks smoothly to the right, looping around the screen limits. "
            "     Its outlines will flash in glowing VIOLET-PINK.\n\n"
            "   - ✊ GESTURE OUTSIDE TARGETS (No hand detected or show other numbers of fingers):\n"
            "     The stickman performs its specific mood-sensitive dance style:\n"
            "     * HAPPY TEXT (e.g. 'I feel good'): Glows EMERALD-GREEN, smiles, and waves arms jumping!\n"
            "     * SAD TEXT (e.g. 'I am depressed'): Glows OCEAN-BLUE, slumps head, frowns and cries!\n"
            "     * NEUTRAL TEXT (e.g. 'It is a table'): Glows CYAN, stands in relaxed idle posture.\n\n"
            "3. PERFORMANCE OPTIMIZATIONS:\n"
            "   - MediaPipe hand calculations are offloaded to an asynchronous background worker thread. "
            "     This keeps the camera window running at a solid, stutter-free frame rate (up to 60 FPS).\n"
            "   - To exit the camera console, press the 'q' key on the OpenCV window or click 'Stop Console' here."
        )
        
        lbl_info = ctk.CTkLabel(card, text=instructions, font=("Consolas", 12), justify="left", text_color="#CDD6F4")
        lbl_info.pack(anchor="w", padx=20, pady=20)

    # ----------------------------------------------------
    # CONTROLLER BUSINESS LOGIC
    # ----------------------------------------------------
    def start_stickman(self):
        if self.process is not None:
            return
            
        mood = self.mood_entry.get().strip()
        if mood == "":
            self.append_log_system("Error: Please enter a mood text in the input box before starting.")
            self.status_label.configure(text="Status: Enter Mood Text", text_color=self.yellow_color)
            return

        self.append_log_system(f"Launching Stickman Console with initial mood: '{mood}'...")
        self.status_label.configure(text="Status: LAUNCHING...", text_color=self.yellow_color)
        
        self.btn_start.configure(state="disabled")
        self.btn_stop.configure(state="normal", fg_color=self.stop_color)
        self.btn_update.configure(state="normal")
        
        # Spawn main.py process
        try:
            self.process = subprocess.Popen(
                [sys.executable, "main.py"],
                stdin=subprocess.PIPE,
                stdout=subprocess.PIPE,
                stderr=subprocess.STDOUT,
                bufsize=1,
                universal_newlines=True
            )
            
            # Send initial mood
            self.process.stdin.write(mood + "\n")
            self.process.stdin.flush()
            
            self.lbl_pid.configure(text=f"Process ID (PID): {self.process.pid}")
            
            # Start background stdout logging thread
            self.log_thread = threading.Thread(target=self.log_reader_worker, daemon=True)
            self.log_thread.start()
            
            # Send current slider values to initialize stickman config parameters
            self.app.after(500, self.send_all_slider_values)
            
        except Exception as e:
            self.append_log_system(f"Launch Failed: {str(e)}")
            self.stop_stickman()

    def log_reader_worker(self):
        """Monitor stdout of subprocess line by line and forward to Tkinter main thread."""
        proc = self.process
        while proc and proc.poll() is None:
            line = proc.stdout.readline()
            if not line:
                break
            text = line.strip()
            if text:
                self.app.after(10, self.handle_process_log, text)
        
        # Process ended
        self.app.after(10, self.handle_process_termination)

    def handle_process_log(self, text):
        """Update GUI elements based on stdout flags from the console."""
        # Insert log into UI terminal monitor
        self.log_box.configure(state="normal")
        self.log_box.insert("end", text + "\n")
        self.log_box.see("end")
        self.log_box.configure(state="disabled")
        
        # Read process headers
        if text.startswith("SYS_START:"):
            self.status_indicator.configure(fg_color=self.green_color)
            self.status_label.configure(text="Status: ACTIVE", text_color=self.green_color)
        elif text.startswith("MOOD_INITIAL:"):
            mood = text.split(":")[1]
            self.lbl_init_mood.configure(text=f"Initial Mood: {mood}")
            self.lbl_curr_mood.configure(text=f"Active Sentiment Mood: {mood}")
        elif text.startswith("MOOD_UPDATE:"):
            mood = text.split(":")[1]
            self.lbl_curr_mood.configure(text=f"Active Sentiment Mood: {mood}")
        elif text.startswith("SYS_CONFIG:"):
            pass

    def handle_process_termination(self):
        """Restore interface states when subprocess exits."""
        self.append_log_system("Stickman Console process terminated.")
        self.status_indicator.configure(fg_color=self.stop_color)
        self.status_label.configure(text="Status: OFFLINE", text_color="#CDD6F4")
        
        self.lbl_init_mood.configure(text="Initial Mood: --")
        self.lbl_curr_mood.configure(text="Active Sentiment Mood: --")
        self.lbl_pid.configure(text="Process ID (PID): None")
        
        self.process = None
        self.btn_start.configure(state="normal")
        self.btn_stop.configure(state="disabled", fg_color="#313244")
        self.btn_update.configure(state="disabled")

    def send_mood_update(self):
        if self.process is None:
            return
        mood = self.mood_entry.get().strip()
        if mood != "":
            try:
                self.process.stdin.write(mood + "\n")
                self.process.stdin.flush()
                self.append_log_system(f"Sent mood update command: '{mood}'")
            except Exception as e:
                self.append_log_system(f"Failed to communicate update: {str(e)}")

    def send_config_update(self, param, val):
        if self.process is None:
            return
        try:
            cmd = f"CFG:{param}:{val}\n"
            self.process.stdin.write(cmd)
            self.process.stdin.flush()
        except Exception:
            pass

    def send_all_slider_values(self):
        """Transmit initial values of sliders to matching config slots in the process."""
        self.send_config_update("thickness", int(self.slider_thick.get()))
        self.send_config_update("head_radius", int(self.slider_head.get()))
        self.send_config_update("body_length", int(self.slider_body.get()))
        self.send_config_update("arm_length", int(self.slider_arm.get()))
        self.send_config_update("leg_length", int(self.slider_leg.get()))
        self.append_log_system("Uploaded parameter calibrations to stickman model.")

    def stop_stickman(self):
        if self.process is not None:
            try:
                # Force close stdout/stdin to prevent blocking issues
                self.process.stdin.close()
                self.process.stdout.close()
                self.process.terminate()
                self.process.wait(timeout=1.0)
            except Exception:
                try:
                    self.process.kill()
                except Exception:
                    pass
            self.process = None
        self.handle_process_termination()

    def reset_sliders(self):
        self.slider_thick.set(4)
        self.slider_head.set(35)
        self.slider_body.set(90)
        self.slider_arm.set(65)
        self.slider_leg.set(75)
        
        # update values labels
        self.slider_thick._command(4)
        self.slider_head._command(35)
        self.slider_body._command(90)
        self.slider_arm._command(65)
        self.slider_leg._command(75)
        
        self.append_log_system("Reset stickman configuration sliders to factory defaults.")

    def append_log_system(self, text):
        """Append local dashboard messages to the log box."""
        self.log_box.configure(state="normal")
        self.log_box.insert("end", f"[DASHBOARD] {text}\n")
        self.log_box.see("end")
        self.log_box.configure(state="disabled")

    # ----------------------------------------------------
    # TAB TRANSITION NAVIGATION
    # ----------------------------------------------------
    def show_dashboard(self):
        self.frame_settings.pack_forget()
        self.frame_help.pack_forget()
        self.frame_dashboard.pack(fill="both", expand=True)
        
        # Adjust sidebar button colors
        self.btn_dashboard.configure(fg_color="#313244", text_color=self.accent_color)
        self.btn_settings.configure(fg_color="transparent", text_color="#CDD6F4")
        self.btn_help.configure(fg_color="transparent", text_color="#CDD6F4")

    def show_settings(self):
        self.frame_dashboard.pack_forget()
        self.frame_help.pack_forget()
        self.frame_settings.pack(fill="both", expand=True)
        
        self.btn_dashboard.configure(fg_color="transparent", text_color="#CDD6F4")
        self.btn_settings.configure(fg_color="#313244", text_color=self.accent_color)
        self.btn_help.configure(fg_color="transparent", text_color="#CDD6F4")

    def show_help(self):
        self.frame_dashboard.pack_forget()
        self.frame_settings.pack_forget()
        self.frame_help.pack(fill="both", expand=True)
        
        self.btn_dashboard.configure(fg_color="transparent", text_color="#CDD6F4")
        self.btn_settings.configure(fg_color="transparent", text_color="#CDD6F4")
        self.btn_help.configure(fg_color="#313244", text_color=self.accent_color)

    def on_closing(self):
        self.stop_stickman()
        self.app.destroy()

if __name__ == "__main__":
    app_instance = StickmanDashboard()
    app_instance.app.mainloop()