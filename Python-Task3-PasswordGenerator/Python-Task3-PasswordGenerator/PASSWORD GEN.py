import math
import secrets
import string
import tkinter as tk


class AnimatedToggle(tk.Canvas):
    """Futuristic toggle switch with smooth sliding animation."""

    def __init__(self, parent, variable, active_color="#ff5400", command=None):
        super().__init__(parent, width=44, height=22, bg="#000000", highlightthickness=0, cursor="hand2")
        self.variable = variable
        self.active_color = active_color
        self.inactive_color = "#1f1f1f"
        self.command = command

        self.bind("<Button-1>", self.toggle)
        self.variable.trace_add("write", lambda *args: self.animate_switch())

        self.current_x = 24.0 if self.variable.get() else 4.0
        self.draw(self.current_x)

    def toggle(self, event=None):
        self.variable.set(not self.variable.get())
        if self.command:
            self.command()

    def animate_switch(self):
        target_x = 24.0 if self.variable.get() else 4.0
        self.tween_knob(target_x)

    def tween_knob(self, target_x):
        diff = target_x - self.current_x
        if abs(diff) > 0.5:
            self.current_x += diff * 0.4
            self.draw(self.current_x)
            self.after(15, lambda: self.tween_knob(target_x))
        else:
            self.current_x = target_x
            self.draw(self.current_x)

    def draw(self, knob_x):
        self.delete("all")
        is_on = self.variable.get()
        color = self.active_color if is_on else self.inactive_color

        self.create_rectangle(1, 1, 43, 21, fill="#0b0b0b", outline=color, width=1)
        if is_on:
            self.create_rectangle(3, 3, 41, 19, fill="#1f1f1f", outline="")

        self.create_oval(knob_x, 3, knob_x + 16, 19, fill=color, outline="")


class InfernoBlizzardPocketNexus:

    def __init__(self, root):
        self.root = root
        self.root.title("INFERNO-BLIZZARD [Pocket]")
        self.root.geometry("360x540")
        self.root.minsize(320, 480)
        self.root.resizable(True, True)

        self.colors = {
            "bg": "#000000",
            "panel": "#0f0f0f",
            "surface": "#161616",
            "accent": "#ff5400",
            "accent_dim": "#b33600",
            "matrix": "#38bdf8",
            "warning": "#f59e0b",
            "danger": "#ef4444",
            "text": "#ffffff",
            "muted": "#a3a3a3",
            "border": "#333333"
        }

        self.root.configure(bg=self.colors["bg"])

        self.mode_var = tk.StringVar(value="quantum")
        self.length_var = tk.IntVar(value=16)
        self.word_count_var = tk.IntVar(value=4)
        self.use_upper = tk.BooleanVar(value=True)
        self.use_lower = tk.BooleanVar(value=True)
        self.use_digits = tk.BooleanVar(value=True)
        self.use_symbols = tk.BooleanVar(value=True)
        self.no_ambiguous = tk.BooleanVar(value=True)
        self.custom_exclude_var = tk.StringVar(value="")
        self.history = []

        # 3D Particle Animation Layers (Embers + Snow + Subtle Ambient Colored Dust)
        self.particles = []
        for _ in range(15):
            self.particles.append({
                "type": "ember",
                "x": secrets.randbelow(360),
                "y": secrets.randbelow(540),
                "z": 0.5 + (secrets.randbelow(150) / 100.0),
                "speed": 0.8 + (secrets.randbelow(140) / 100.0),
                "size": secrets.choice([1, 2, 3]),
                "color": secrets.choice(["#ff5400", "#ffb703", "#d62828"])
            })
        for _ in range(20):
            self.particles.append({
                "type": "snow",
                "x": secrets.randbelow(360),
                "y": secrets.randbelow(540),
                "z": 0.5 + (secrets.randbelow(150) / 100.0),
                "speed": 0.4 + (secrets.randbelow(100) / 100.0),
                "size": secrets.choice([1, 2]),
                "color": secrets.choice(["#ffffff", "#38bdf8", "#93c5fd"])
            })
        for _ in range(8):  # Subtle ambient colorful dust floating across main interface
            self.particles.append({
                "type": "ambient_dust",
                "x": secrets.randbelow(360),
                "y": secrets.randbelow(540),
                "vx": (secrets.randbelow(10) - 5) * 0.1,
                "vy": (secrets.randbelow(10) - 5) * 0.1,
                "size": 2,
                "color": secrets.choice(["#ff5400", "#38bdf8", "#ec4899", "#10b981", "#f59e0b"])
            })

        self._build_responsive_grid()
        self._build_ui()

        self.output_entry.insert(0, "PRESS [GENERATE KEY] TO INITIATE")
        self.strength_lbl.config(text="STANDBY [--]", fg=self.colors["muted"])
        self.crack_time_lbl.config(text="Crack: --")

        self.animate_particles()

    def _build_responsive_grid(self):
        self.root.rowconfigure(0, weight=1)
        self.root.columnconfigure(0, weight=1)

    def _build_ui(self):
        self.anim_canvas = tk.Canvas(self.root, bg=self.colors["bg"], highlightthickness=0)
        self.anim_canvas.grid(row=0, column=0, sticky="nsew")

        self.main_container = tk.Frame(self.root, bg=self.colors["bg"])
        self.main_container.grid(row=0, column=0, sticky="nsew", padx=10, pady=10)

        self.main_container.columnconfigure(0, weight=1)
        self.main_container.rowconfigure(4, weight=1)

        # --- 1. HUD Telemetry Header ---
        header_frame = tk.Frame(self.main_container, bg=self.colors["bg"])
        header_frame.grid(row=0, column=0, sticky="ew", pady=(0, 6))
        header_frame.columnconfigure(1, weight=1)

        tk.Label(
            header_frame, text="INFERNO-BLIZZARD // POCKET",
            font=("Consolas", 9, "bold"), fg=self.colors["accent"], bg=self.colors["bg"]
        ).grid(row=0, column=0, sticky="w")

        tk.Label(
            header_frame, text="DUST-PHYSICS ACTIVE",
            font=("Consolas", 8, "bold"), fg=self.colors["matrix"], bg=self.colors["bg"]
        ).grid(row=0, column=1, sticky="e")

        # --- 2. Mode Selector Matrix ---
        mode_frame = tk.Frame(self.main_container, bg=self.colors["panel"], highlightbackground=self.colors["border"],
                              highlightthickness=1)
        mode_frame.grid(row=1, column=0, sticky="ew", pady=(0, 6))
        mode_frame.columnconfigure((0, 1), weight=1)

        self.btn_quantum = tk.Button(
            mode_frame, text="RANDOM", font=("Consolas", 9, "bold"),
            bg=self.colors["accent"], fg="#ffffff", activebackground=self.colors["accent_dim"],
            bd=0, pady=6, cursor="hand2", command=lambda: self.switch_mode("quantum")
        )
        self.btn_quantum.grid(row=0, column=0, sticky="nsew", padx=1, pady=1)

        self.btn_neural = tk.Button(
            mode_frame, text="PASSPHRASE", font=("Consolas", 9, "bold"),
            bg=self.colors["panel"], fg=self.colors["muted"], activebackground=self.colors["panel"],
            bd=0, pady=6, cursor="hand2", command=lambda: self.switch_mode("neural")
        )
        self.btn_neural.grid(row=0, column=1, sticky="nsew", padx=1, pady=1)

        # --- 3. Output Telemetry Display ---
        output_card = tk.Frame(
            self.main_container, bg=self.colors["surface"],
            highlightbackground=self.colors["border"], highlightthickness=1, padx=8, pady=8
        )
        output_card.grid(row=2, column=0, sticky="ew", pady=(0, 6))
        output_card.columnconfigure(0, weight=1)

        entry_box_frame = tk.Frame(output_card, bg=self.colors["panel"], padx=6, pady=6)
        entry_box_frame.grid(row=0, column=0, sticky="ew")
        entry_box_frame.columnconfigure(0, weight=1)

        self.output_entry = tk.Entry(
            entry_box_frame, font=("Consolas", 11, "bold"),
            bg=self.colors["panel"], fg=self.colors["accent"],
            insertbackground=self.colors["accent"], bd=0, readonlybackground=self.colors["panel"]
        )
        self.output_entry.grid(row=0, column=0, sticky="ew")

        self.copy_btn = tk.Button(
            output_card, text="COPY", font=("Consolas", 9, "bold"),
            bg=self.colors["accent"], fg="#ffffff", activebackground=self.colors["accent_dim"],
            bd=0, padx=12, pady=6, cursor="hand2", command=self.copy_to_clipboard
        )
        self.copy_btn.grid(row=0, column=1, padx=(6, 0), sticky="ns")

        self.meter_canvas = tk.Canvas(output_card, height=5, bg=self.colors["panel"], highlightthickness=0)
        self.meter_canvas.grid(row=1, column=0, columnspan=2, sticky="ew", pady=(6, 2))

        meta_subrow = tk.Frame(output_card, bg=self.colors["surface"])
        meta_subrow.grid(row=2, column=0, columnspan=2, sticky="ew")
        meta_subrow.columnconfigure(1, weight=1)

        self.strength_lbl = tk.Label(meta_subrow, text="--", font=("Consolas", 9, "bold"), fg=self.colors["text"],
                                     bg=self.colors["surface"])
        self.strength_lbl.grid(row=0, column=0, sticky="w")

        self.crack_time_lbl = tk.Label(meta_subrow, text="--", font=("Consolas", 8, "bold"), fg=self.colors["muted"],
                                       bg=self.colors["surface"])
        self.crack_time_lbl.grid(row=0, column=1, sticky="e")

        # --- 4. Dynamic Parameter Panel ---
        self.settings_card = tk.Frame(
            self.main_container, bg=self.colors["surface"],
            highlightbackground=self.colors["border"], highlightthickness=1, padx=10, pady=8
        )
        self.settings_card.grid(row=3, column=0, sticky="nsew", pady=(0, 6))
        self.settings_card.columnconfigure(0, weight=1)

        self.build_settings_content()

        # --- 5. Action Execution Matrix ---
        self.gen_btn = tk.Button(
            self.main_container, text="🔥❄ GENERATE KEY ❄🔥", font=("Consolas", 10, "bold"),
            bg=self.colors["accent"], fg="#ffffff", activebackground=self.colors["accent_dim"],
            bd=0, pady=9, cursor="hand2", command=self.generate
        )
        self.gen_btn.grid(row=5, column=0, sticky="ew", pady=(0, 6))

        # --- 6. Vault Session History Matrix ---
        history_frame = tk.Frame(self.main_container, bg=self.colors["bg"])
        history_frame.grid(row=4, column=0, sticky="nsew", pady=(0, 2))
        history_frame.columnconfigure(0, weight=1)
        history_frame.rowconfigure(1, weight=1)

        hist_header_sub = tk.Frame(history_frame, bg=self.colors["bg"])
        hist_header_sub.grid(row=0, column=0, sticky="ew")
        hist_header_sub.columnconfigure(1, weight=1)

        tk.Label(hist_header_sub, text="SESSION HISTORY (LAST 5)", font=("Consolas", 8, "bold"), fg=self.colors["text"],
                 bg=self.colors["bg"]).grid(row=0, column=0, sticky="w")

        clear_log_btn = tk.Label(hist_header_sub, text="[PURGE]", font=("Consolas", 8, "bold"),
                                 fg=self.colors["danger"], bg=self.colors["bg"], cursor="hand2")
        clear_log_btn.grid(row=0, column=1, sticky="e")
        clear_log_btn.bind("<Button-1>", self.clear_history)

        self.history_box = tk.Listbox(
            history_frame, height=3, font=("Consolas", 9, "bold"),
            bg=self.colors["surface"], fg=self.colors["matrix"],
            selectbackground=self.colors["panel"], selectforeground=self.colors["text"],
            bd=0, highlightbackground=self.colors["border"], highlightthickness=1, activestyle="none"
        )
        self.history_box.grid(row=1, column=0, sticky="nsew", pady=(2, 0))
        self.history_box.bind("<<ListboxSelect>>", self.on_history_select)

    def trigger_slider_dust(self, event):
        """Spawns vibrant 3D colorful dust particles on slider motion."""
        for _ in range(3):
            self.particles.append({
                "type": "dust",
                "x": event.x_root - self.root.winfo_rootx(),
                "y": event.y_root - self.root.winfo_rooty(),
                "vx": (secrets.randbelow(20) - 10) * 0.3,
                "vy": (secrets.randbelow(20) - 10) * 0.3,
                "life": 25,
                "size": secrets.choice([2, 3, 4]),
                "color": secrets.choice(["#ff5400", "#38bdf8", "#f59e0b", "#ec4899", "#10b981"])
            })

    def animate_particles(self):
        self.anim_canvas.delete("particle")
        w = self.anim_canvas.winfo_width()
        h = self.anim_canvas.winfo_height()
        if w < 50: w = 360
        if h < 50: h = 540

        active_particles = []
        for p in self.particles:
            ptype = p.get("type")
            if ptype == "dust":
                p["x"] += p["vx"]
                p["y"] += p["vy"]
                p["life"] -= 1
                if p["life"] > 0:
                    active_particles.append(p)
                    size = p["size"]
                    self.anim_canvas.create_oval(p["x"], p["y"], p["x"] + size, p["y"] + size, fill=p["color"],
                                                 outline="", tags="particle")
            elif ptype == "ambient_dust":
                p["x"] += p["vx"]
                p["y"] += p["vy"]
                if p["x"] < 0: p["x"] = w
                if p["x"] > w: p["x"] = 0
                if p["y"] < 0: p["y"] = h
                if p["y"] > h: p["y"] = 0
                active_particles.append(p)
                size = p["size"]
                self.anim_canvas.create_oval(p["x"], p["y"], p["x"] + size, p["y"] + size, fill=p["color"], outline="",
                                             tags="particle")
            else:
                if p["type"] == "ember":
                    p["y"] -= p["speed"] * p["z"]
                    p["x"] += math.sin(p["y"] / 25.0) * 0.6
                    if p["y"] < 0:
                        p["y"] = h + 10
                        p["x"] = secrets.randbelow(w + 1)
                else:
                    p["y"] += p["speed"] * p["z"]
                    p["x"] += math.cos(p["y"] / 30.0) * 0.4
                    if p["y"] > h:
                        p["y"] = -10
                        p["x"] = secrets.randbelow(w + 1)

                size = max(1, int(p["size"] * p["z"]))
                self.anim_canvas.create_oval(p["x"], p["y"], p["x"] + size, p["y"] + size, fill=p["color"], outline="",
                                             tags="particle")
                active_particles.append(p)

        self.particles = active_particles
        self.root.after(25, self.animate_particles)

    def switch_mode(self, mode):
        self.mode_var.set(mode)
        if mode == "quantum":
            self.btn_quantum.config(bg=self.colors["accent"], fg="#ffffff")
            self.btn_neural.config(bg=self.colors["panel"], fg=self.colors["muted"])
        else:
            self.btn_neural.config(bg=self.colors["accent"], fg="#ffffff")
            self.btn_quantum.config(bg=self.colors["panel"], fg=self.colors["muted"])
        self.build_settings_content()

    def build_settings_content(self):
        for widget in self.settings_card.winfo_children():
            widget.destroy()

        mode = self.mode_var.get()
        self.settings_card.columnconfigure(0, weight=1)

        if mode == "quantum":
            len_row = tk.Frame(self.settings_card, bg=self.colors["surface"])
            len_row.grid(row=0, column=0, sticky="ew", pady=(0, 4))
            len_row.columnconfigure(0, weight=1)

            tk.Label(len_row, text="LENGTH:", font=("Consolas", 8, "bold"), fg=self.colors["text"],
                     bg=self.colors["surface"]).pack(side="left")
            tk.Label(len_row, textvariable=self.length_var, font=("Consolas", 10, "bold"), fg=self.colors["accent"],
                     bg=self.colors["surface"]).pack(side="right")

            slider = tk.Scale(
                self.settings_card, from_=8, to=64, orient="horizontal", variable=self.length_var,
                showvalue=0, bg=self.colors["accent"], fg=self.colors["text"], troughcolor="#1a1a1a",
                activebackground=self.colors["matrix"], highlightthickness=0, bd=0, sliderrelief="raised",
                cursor="hand2"
            )
            slider.grid(row=1, column=0, sticky="ew", pady=(0, 6))
            slider.bind("<B1-Motion>", self.trigger_slider_dust)

            options = [
                ("Uppercase (A-Z)", self.use_upper),
                ("Lowercase (a-z)", self.use_lower),
                ("Numbers (0-9)", self.use_digits),
                ("Symbols (!@#$)", self.use_symbols),
                ("No Ambiguous", self.no_ambiguous),
            ]
            for idx, (text, var) in enumerate(options, start=2):
                row = tk.Frame(self.settings_card, bg=self.colors["surface"])
                row.grid(row=idx, column=0, sticky="ew", pady=2)
                row.columnconfigure(0, weight=1)

                tk.Label(row, text=text, font=("Consolas", 9, "bold"), fg=self.colors["text"],
                         bg=self.colors["surface"]).pack(side="left")
                AnimatedToggle(row, variable=var, active_color=self.colors["accent"]).pack(side="right")

            excl_row = tk.Frame(self.settings_card, bg=self.colors["surface"])
            excl_row.grid(row=7, column=0, sticky="ew", pady=(4, 0))
            excl_row.columnconfigure(0, weight=1)
            tk.Label(excl_row, text="Exclude:", font=("Consolas", 8, "bold"), fg=self.colors["muted"],
                     bg=self.colors["surface"]).pack(anchor="w")
            tk.Entry(
                excl_row, textvariable=self.custom_exclude_var, font=("Consolas", 9, "bold"),
                bg=self.colors["panel"], fg=self.colors["text"], bd=0, insertbackground=self.colors["accent"]
            ).pack(fill="x", pady=(1, 0))

        else:
            word_row = tk.Frame(self.settings_card, bg=self.colors["surface"])
            word_row.grid(row=0, column=0, sticky="ew", pady=(0, 4))
            word_row.columnconfigure(0, weight=1)

            tk.Label(word_row, text="WORD COUNT:", font=("Consolas", 8, "bold"), fg=self.colors["text"],
                     bg=self.colors["surface"]).pack(side="left")
            tk.Label(word_row, textvariable=self.word_count_var, font=("Consolas", 10, "bold"),
                     fg=self.colors["accent"], bg=self.colors["surface"]).pack(side="right")

            slider = tk.Scale(
                self.settings_card, from_=3, to=6, orient="horizontal", variable=self.word_count_var,
                showvalue=0, bg=self.colors["accent"], fg=self.colors["text"], troughcolor="#1a1a1a",
                activebackground=self.colors["matrix"], highlightthickness=0, bd=0, sliderrelief="raised",
                cursor="hand2"
            )
            slider.grid(row=1, column=0, sticky="ew", pady=(0, 8))
            slider.bind("<B1-Motion>", self.trigger_slider_dust)

            tk.Label(
                self.settings_card,
                text="Diceware lexicons with random connectors for high memorability.",
                font=("Consolas", 8), fg=self.colors["muted"], bg=self.colors["surface"], wraplength=280, justify="left"
            ).grid(row=2, column=0, sticky="ew", pady=4)

    def generate(self):
        mode = self.mode_var.get()
        if mode == "quantum":
            sets = []
            ambiguous = "0Ol1I|" if self.no_ambiguous.get() else ""
            custom_excl = self.custom_exclude_var.get()

            def clean(chars):
                return "".join(c for c in chars if c not in ambiguous and c not in custom_excl)

            if self.use_upper.get(): sets.append(clean(string.ascii_uppercase))
            if self.use_lower.get(): sets.append(clean(string.ascii_lowercase))
            if self.use_digits.get(): sets.append(clean(string.digits))
            if self.use_symbols.get(): sets.append(clean("!@#$%^&*()_+-=[]{}|;:,.<>?"))

            sets = [s for s in sets if s]
            if not sets:
                self.strength_lbl.config(text="ERROR: SELECT SETS", fg=self.colors["danger"])
                return

            length = self.length_var.get()
            if length < len(sets):
                length = len(sets)
                self.length_var.set(length)

            password = [secrets.choice(s) for s in sets]
            full_pool = "".join(sets)
            password += [secrets.choice(full_pool) for _ in range(length - len(sets))]

            for i in range(len(password) - 1, 0, -1):
                j = secrets.randbelow(i + 1)
                password[i], password[j] = password[j], password[i]

            password = "".join(password)
            pool_size = len(full_pool)
        else:
            lexicon = [
                "quantum", "nexus", "matrix", "vector", "cyber", "pulse", "beacon",
                "orbit", "titan", "stellar", "plasma", "vortex", "helix", "cipher",
                "photon", "spectrum", "kinetic", "gravity", "nebula", "zenith"
            ]
            count = self.word_count_var.get()
            chosen_words = [secrets.choice(lexicon) for _ in range(count)]
            separator = secrets.choice(["-", "_", ".", "#", "@"])
            password = separator.join(chosen_words)
            pool_size = len(lexicon) ** count

        self.output_entry.delete(0, tk.END)
        self.output_entry.insert(0, password)

        self.evaluate_security(password, pool_size)
        self.add_to_history(password)

    def evaluate_security(self, pw, pool_size):
        self.meter_canvas.delete("all")
        if not pw:
            return

        entropy = len(pw) * math.log2(max(pool_size, 2))

        if entropy < 45:
            label, color, pct = "WEAK", self.colors["danger"], 0.25
        elif entropy < 75:
            label, color, pct = "GOOD", self.colors["warning"], 0.55
        elif entropy < 115:
            label, color, pct = "STRONG", self.colors["matrix"], 0.8
        else:
            label, color, pct = "ULTRA", self.colors["accent"], 1.0

        seconds = (2 ** entropy) / 5e10
        if seconds < 60:
            time_str = "<1m"
        elif seconds < 3600:
            time_str = f"{int(seconds / 60)}m"
        elif seconds < 86400:
            time_str = f"{int(seconds / 3600)}h"
        elif seconds < 31536000:
            time_str = f"{int(seconds / 86400)}d"
        else:
            time_str = "CENTURIES+"

        self.strength_lbl.config(text=f"{label} [{int(entropy)}b]", fg=color)
        self.crack_time_lbl.config(text=f"Crack: {time_str}")

        self.root.update_idletasks()
        bar_width = self.meter_canvas.winfo_width()
        if bar_width <= 1:
            bar_width = 300
        self.meter_canvas.create_rectangle(0, 0, int(bar_width * pct), 5, fill=color, outline="")

    def add_to_history(self, pw):
        if pw in self.history:
            return
        self.history.insert(0, pw)
        if len(self.history) > 5:
            self.history.pop()

        self.history_box.delete(0, tk.END)
        for idx, item in enumerate(self.history, 1):
            self.history_box.insert(tk.END, f"[{idx}] {item}")

    def clear_history(self, event=None):
        self.history.clear()
        self.history_box.delete(0, tk.END)

    def copy_to_clipboard(self):
        pw = self.output_entry.get()
        if pw and pw != "PRESS [GENERATE KEY] TO INITIATE":
            self.root.clipboard_clear()
            self.root.clipboard_append(pw)
            self.copy_btn.config(text="OK", bg=self.colors["matrix"])
            self.root.after(1200, lambda: self.copy_btn.config(text="COPY", bg=self.colors["accent"]))

    def on_history_select(self, event):
        sel = self.history_box.curselection()
        if not sel:
            return
        selected_pw = self.history[sel[0]]
        self.output_entry.delete(0, tk.END)
        self.output_entry.insert(0, selected_pw)
        self.evaluate_security(selected_pw, 62)


if __name__ == "__main__":
    root = tk.Tk()
    app = InfernoBlizzardPocketNexus(root)
    root.mainloop()
