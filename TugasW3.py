import tkinter as tk
from tkinter import ttk
import math

# =========================
# FSM DEFINITION
# L = { x in (0+1)+ | last char = 1 AND no substring "00" }
# States: S (start), A (saw 0), B (saw 1, accept), C (dead/trap)
# =========================
STATES = ["S", "A", "B", "C"]
START_STATE = "S"
ACCEPT_STATES = {"B"}
ALPHABET = {"0", "1"}

TRANSITIONS = {
    ("S", "0"): "A",
    ("S", "1"): "B",
    ("A", "0"): "C",
    ("A", "1"): "B",
    ("B", "0"): "A",
    ("B", "1"): "B",
    ("C", "0"): "C",
    ("C", "1"): "C",
}

STATE_DESCRIPTIONS = {
    "S": "Start — belum membaca input",
    "A": "Baru membaca '0', menunggu '1'",
    "B": "Baru membaca '1' — DITERIMA",
    "C": "Dead state — ditemukan '00'",
}

# =========================
# FSM SIMULATION
# =========================
def simulate_fsm(input_string):
    """Returns (accepted, steps_list)"""
    if not input_string:
        return False, [], "String kosong — harus minimal 1 karakter"

    for ch in input_string:
        if ch not in ALPHABET:
            return False, [], f"Karakter '{ch}' tidak valid. Hanya '0' dan '1' yang diperbolehkan."

    current = START_STATE
    steps = [("—", current, STATE_DESCRIPTIONS[current])]

    for char in input_string:
        next_state = TRANSITIONS[(current, char)]
        steps.append((char, next_state, STATE_DESCRIPTIONS[next_state]))
        current = next_state

    accepted = current in ACCEPT_STATES
    reason = ""
    if not accepted:
        if current == "C":
            reason = "DITOLAK — String mengandung substring '00'"
        elif current == "S":
            reason = "DITOLAK — String kosong"
        else:
            reason = "DITOLAK — Karakter terakhir bukan '1'"
    else:
        reason = "DITERIMA — Berakhir '1' dan tidak mengandung '00'"

    return accepted, steps, reason


# =========================
# GUI APPLICATION
# =========================
class FSMApp:
    # Color palette
    BG = "#1a1a2e"
    BG2 = "#16213e"
    ACCENT = "#0f3460"
    HIGHLIGHT = "#e94560"
    GREEN = "#00b894"
    TEXT = "#eaeaea"
    TEXT_DIM = "#8a8a9a"
    GOLD = "#f9ca24"
    ORANGE = "#e17055"
    BLUE = "#74b9ff"
    PURPLE = "#a29bfe"

    STATE_COLORS = {
        "S": "#74b9ff",
        "A": "#ffeaa7",
        "B": "#00b894",
        "C": "#e94560",
    }

    def __init__(self, root):
        self.root = root
        self.root.title("FSM Simulator — Tugas Praktikum #2 Otomata")
        self.root.geometry("1050x750")
        self.root.configure(bg=self.BG)
        self.root.resizable(True, True)

        self.animation_step = -1
        self.current_steps = []
        self.animation_id = None

        self._build_ui()
        self._draw_fsm_diagram()

    def _build_ui(self):
        # --- Title ---
        title_frame = tk.Frame(self.root, bg=self.BG)
        title_frame.pack(fill="x", padx=20, pady=(15, 5))

        tk.Label(title_frame, text="⚙  FSM Simulator", font=("Segoe UI", 22, "bold"),
                 fg=self.HIGHLIGHT, bg=self.BG).pack(side="left")

        tk.Label(title_frame, text="Teori Bahasa & Automata", font=("Segoe UI", 11),
                 fg=self.TEXT_DIM, bg=self.BG).pack(side="right", pady=8)

        # --- Language description ---
        lang_frame = tk.Frame(self.root, bg=self.ACCENT, highlightbackground=self.HIGHLIGHT,
                              highlightthickness=1)
        lang_frame.pack(fill="x", padx=20, pady=(5, 10))

        tk.Label(lang_frame, text="L = { x ∈ (0+1)⁺ | karakter terakhir x = 1  ∧  x tidak memiliki substring 00 }",
                 font=("Consolas", 12, "bold"), fg=self.GOLD, bg=self.ACCENT,
                 padx=15, pady=8).pack()

        # --- Main content ---
        content = tk.Frame(self.root, bg=self.BG)
        content.pack(fill="both", expand=True, padx=20)

        # Left panel: FSM diagram
        left = tk.LabelFrame(content, text=" Diagram FSM ", font=("Segoe UI", 11, "bold"),
                             fg=self.BLUE, bg=self.BG2, labelanchor="n",
                             highlightbackground="#333", highlightthickness=1)
        left.pack(side="left", fill="both", expand=True, padx=(0, 10))

        self.canvas = tk.Canvas(left, bg=self.BG2, highlightthickness=0, width=460, height=340)
        self.canvas.pack(fill="both", expand=True, padx=5, pady=5)

        # Right panel: input/output
        right = tk.Frame(content, bg=self.BG)
        right.pack(side="right", fill="both", expand=True)

        # Input section
        input_frame = tk.LabelFrame(right, text=" Input String ", font=("Segoe UI", 11, "bold"),
                                    fg=self.BLUE, bg=self.BG2, labelanchor="n",
                                    highlightbackground="#333", highlightthickness=1)
        input_frame.pack(fill="x", pady=(0, 10))

        entry_row = tk.Frame(input_frame, bg=self.BG2)
        entry_row.pack(fill="x", padx=15, pady=10)

        self.entry = tk.Entry(entry_row, font=("Consolas", 16), bg="#0d1b2a", fg=self.TEXT,
                              insertbackground=self.TEXT, relief="flat", justify="center")
        self.entry.pack(side="left", fill="x", expand=True, ipady=6)
        self.entry.bind("<Return>", lambda e: self.run_fsm())

        btn_frame = tk.Frame(input_frame, bg=self.BG2)
        btn_frame.pack(pady=(0, 10))

        self.btn_run = tk.Button(btn_frame, text="▶  Analyze", font=("Segoe UI", 11, "bold"),
                                 bg=self.GREEN, fg="white", relief="flat", padx=20, pady=4,
                                 cursor="hand2", command=self.run_fsm)
        self.btn_run.pack(side="left", padx=5)

        self.btn_animate = tk.Button(btn_frame, text="⏵  Step-by-Step", font=("Segoe UI", 11, "bold"),
                                     bg=self.PURPLE, fg="white", relief="flat", padx=20, pady=4,
                                     cursor="hand2", command=self.start_animation)
        self.btn_animate.pack(side="left", padx=5)

        self.btn_clear = tk.Button(btn_frame, text="✕  Clear", font=("Segoe UI", 11, "bold"),
                                   bg=self.HIGHLIGHT, fg="white", relief="flat", padx=20, pady=4,
                                   cursor="hand2", command=self.clear_all)
        self.btn_clear.pack(side="left", padx=5)

        # Result label
        self.result_var = tk.StringVar(value="Masukkan string biner lalu klik Analyze")
        self.result_label = tk.Label(right, textvariable=self.result_var,
                                     font=("Segoe UI", 13, "bold"), bg=self.BG,
                                     fg=self.TEXT_DIM, wraplength=450, pady=5)
        self.result_label.pack(fill="x")

        # Transition table
        table_frame = tk.LabelFrame(right, text=" Tabel Transisi ", font=("Segoe UI", 11, "bold"),
                                    fg=self.BLUE, bg=self.BG2, labelanchor="n",
                                    highlightbackground="#333", highlightthickness=1)
        table_frame.pack(fill="both", expand=True)

        cols = ("Step", "Input", "State", "Keterangan")
        self.tree = ttk.Treeview(table_frame, columns=cols, show="headings", height=8)

        style = ttk.Style()
        style.theme_use("clam")
        style.configure("Treeview", background="#0d1b2a", foreground=self.TEXT,
                         fieldbackground="#0d1b2a", font=("Consolas", 10), rowheight=26)
        style.configure("Treeview.Heading", background=self.ACCENT, foreground=self.GOLD,
                         font=("Segoe UI", 10, "bold"))
        style.map("Treeview", background=[("selected", self.ACCENT)])

        self.tree.heading("Step", text="#")
        self.tree.heading("Input", text="Input")
        self.tree.heading("State", text="State")
        self.tree.heading("Keterangan", text="Keterangan")
        self.tree.column("Step", width=40, anchor="center")
        self.tree.column("Input", width=60, anchor="center")
        self.tree.column("State", width=60, anchor="center")
        self.tree.column("Keterangan", width=260, anchor="w")

        scrollbar = ttk.Scrollbar(table_frame, orient="vertical", command=self.tree.yview)
        self.tree.configure(yscrollcommand=scrollbar.set)
        self.tree.pack(side="left", fill="both", expand=True, padx=(5, 0), pady=5)
        scrollbar.pack(side="right", fill="y", pady=5)

        # Quick test buttons
        quick_frame = tk.LabelFrame(self.root, text=" Quick Test ", font=("Segoe UI", 10, "bold"),
                                    fg=self.BLUE, bg=self.BG2, labelanchor="n",
                                    highlightbackground="#333", highlightthickness=1)
        quick_frame.pack(fill="x", padx=20, pady=(5, 15))

        examples = [("1", True), ("01", True), ("101", True), ("0101", True),
                    ("0", False), ("00", False), ("100", False), ("010010", False)]

        for i, (s, exp) in enumerate(examples):
            color = self.GREEN if exp else self.HIGHLIGHT
            tag = "✓" if exp else "✗"
            btn = tk.Button(quick_frame, text=f"{tag} {s}", font=("Consolas", 10, "bold"),
                            bg=color, fg="white", relief="flat", padx=8, pady=2, cursor="hand2",
                            command=lambda x=s: self._quick_test(x))
            btn.pack(side="left", padx=4, pady=6)

    # =========================
    # FSM DIAGRAM DRAWING
    # =========================
    def _draw_fsm_diagram(self, highlight_state=None):
        c = self.canvas
        c.delete("all")

        w, h = 460, 340
        positions = {
            "S": (80, h // 2),
            "A": (220, h // 2 - 80),
            "B": (220, h // 2 + 80),
            "C": (380, h // 2 - 80),
        }
        R = 30

        # Draw start arrow
        sx, sy = positions["S"]
        c.create_line(10, sy, sx - R, sy, arrow=tk.LAST, fill=self.BLUE,
                      width=2, arrowshape=(10, 12, 5))
        c.create_text(10, sy - 15, text="start", font=("Segoe UI", 9), fill=self.TEXT_DIM, anchor="w")

        # Draw transitions (arrows)
        self._draw_transitions(c, positions, R, highlight_state)

        # Draw states (circles)
        for state, (x, y) in positions.items():
            is_accept = state in ACCEPT_STATES
            is_highlight = (state == highlight_state)

            fill = self.STATE_COLORS.get(state, "#555")
            outline = "white"
            lw = 2

            if is_highlight:
                fill = "#ffffff"
                outline = self.GOLD
                lw = 4
                c.create_oval(x - R - 8, y - R - 8, x + R + 8, y + R + 8,
                              outline=self.GOLD, width=2, dash=(4, 4))

            c.create_oval(x - R, y - R, x + R, y + R, fill=fill, outline=outline, width=lw)

            if is_accept:
                c.create_oval(x - R + 5, y - R + 5, x + R - 5, y + R - 5,
                              outline=outline, width=2)

            text_color = self.BG if not is_highlight else self.BG
            c.create_text(x, y, text=state, font=("Segoe UI", 16, "bold"), fill=text_color)

        # Legend
        c.create_text(w // 2, h - 15, text="◎ = Accept State  |  ◉ = Dead State",
                      font=("Segoe UI", 9), fill=self.TEXT_DIM)

    def _draw_transitions(self, c, pos, R, hl):
        """Draw all transition arrows."""
        def arrow_between(p1, p2, label, curve=0):
            x1, y1 = p1
            x2, y2 = p2
            dx, dy = x2 - x1, y2 - y1
            dist = math.sqrt(dx * dx + dy * dy)
            if dist == 0:
                return

            ux, uy = dx / dist, dy / dist
            sx, sy = x1 + ux * R, y1 + uy * R
            ex, ey = x2 - ux * R, y2 - uy * R

            if curve != 0:
                mx = (sx + ex) / 2 - uy * curve
                my = (sy + ey) / 2 + ux * curve
                c.create_line(sx, sy, mx, my, ex, ey, smooth=True, arrow=tk.LAST,
                              fill=self.TEXT_DIM, width=2, arrowshape=(8, 10, 4))
                c.create_text(mx, my - 12 * (1 if curve > 0 else -1), text=label,
                              font=("Consolas", 11, "bold"), fill=self.GOLD)
            else:
                c.create_line(sx, sy, ex, ey, arrow=tk.LAST, fill=self.TEXT_DIM,
                              width=2, arrowshape=(8, 10, 4))
                mx, my = (sx + ex) / 2, (sy + ey) / 2
                offset_x = -uy * 14
                offset_y = ux * 14
                c.create_text(mx + offset_x, my + offset_y, text=label,
                              font=("Consolas", 11, "bold"), fill=self.GOLD)

        def self_loop(px, py, label, angle=90):
            rad = math.radians(angle)
            cx = px + math.cos(rad) * 50
            cy = py - math.sin(rad) * 50
            lr = 18
            c.create_oval(cx - lr, cy - lr, cx + lr, cy + lr, outline=self.TEXT_DIM, width=2)
            c.create_text(cx, cy - lr - 10, text=label,
                          font=("Consolas", 11, "bold"), fill=self.GOLD)

        S, A, B, C = pos["S"], pos["A"], pos["B"], pos["C"]

        arrow_between(S, A, "0", curve=0)
        arrow_between(S, B, "1", curve=0)
        arrow_between(A, B, "1", curve=0)
        arrow_between(A, C, "0", curve=0)
        arrow_between(B, A, "0", curve=0)
        self_loop(B[0], B[1], "1", angle=-90)
        self_loop(C[0], C[1], "0,1", angle=90)

    # =========================
    # FSM LOGIC
    # =========================
    def run_fsm(self):
        self._stop_animation()
        input_str = self.entry.get().strip()
        accepted, steps, reason = simulate_fsm(input_str)

        self.current_steps = steps

        # Update result
        if not steps and not accepted:
            self.result_var.set(reason)
            self.result_label.config(fg=self.ORANGE)
            self._draw_fsm_diagram()
            return

        self.result_var.set(reason)
        self.result_label.config(fg=self.GREEN if accepted else self.HIGHLIGHT)

        # Update table
        for item in self.tree.get_children():
            self.tree.delete(item)

        for i, (inp, state, desc) in enumerate(steps):
            self.tree.insert("", "end", values=(i, inp, state, desc))

        # Highlight final state
        if steps:
            self._draw_fsm_diagram(highlight_state=steps[-1][1])

    def start_animation(self):
        self._stop_animation()
        input_str = self.entry.get().strip()
        accepted, steps, reason = simulate_fsm(input_str)

        if not steps:
            self.result_var.set(reason)
            self.result_label.config(fg=self.ORANGE)
            return

        self.current_steps = steps
        self.animation_step = 0
        self.anim_accepted = accepted
        self.anim_reason = reason

        for item in self.tree.get_children():
            self.tree.delete(item)

        self.result_var.set("Animasi berjalan...")
        self.result_label.config(fg=self.PURPLE)
        self._animate_next()

    def _animate_next(self):
        if self.animation_step >= len(self.current_steps):
            self.result_var.set(self.anim_reason)
            self.result_label.config(fg=self.GREEN if self.anim_accepted else self.HIGHLIGHT)
            self.animation_step = -1
            return

        i = self.animation_step
        inp, state, desc = self.current_steps[i]
        self.tree.insert("", "end", values=(i, inp, state, desc))
        self._draw_fsm_diagram(highlight_state=state)

        self.animation_step += 1
        self.animation_id = self.root.after(600, self._animate_next)

    def _stop_animation(self):
        if self.animation_id:
            self.root.after_cancel(self.animation_id)
            self.animation_id = None
        self.animation_step = -1

    def clear_all(self):
        self._stop_animation()
        self.entry.delete(0, tk.END)
        for item in self.tree.get_children():
            self.tree.delete(item)
        self.result_var.set("Masukkan string biner lalu klik Analyze")
        self.result_label.config(fg=self.TEXT_DIM)
        self._draw_fsm_diagram()

    def _quick_test(self, s):
        self.entry.delete(0, tk.END)
        self.entry.insert(0, s)
        self.run_fsm()


# =========================
# MAIN
# =========================
if __name__ == "__main__":
    root = tk.Tk()
    app = FSMApp(root)
    root.mainloop()
