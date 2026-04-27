import re
import tkinter as tk
from tkinter import filedialog
from tkinter.scrolledtext import ScrolledText

# =========================
# TOKEN DATA
# =========================
RESERVED_WORDS = {
    "if", "else", "for", "while", "return",
    "int", "float", "double", "char", "void",
    "break", "continue"
}

SYMBOLS = set("+-*/=(){}[];,<>!&|#")

# =========================
# TOKENIZER
# =========================
def classify_token(token):
    if token in RESERVED_WORDS:
        return "Reserved Word"
    elif re.match(r'^[0-9]+(\.[0-9]+)?$', token):
        return "Math"
    elif token in "+-*/=<>":
        return "Math"
    elif token in SYMBOLS:
        return "Symbol"
    elif re.match(r'^[a-zA-Z_][a-zA-Z0-9_]*$', token):
        return "Variable"
    else:
        return "Unknown"

def tokenize(code):
    return re.findall(r'[a-zA-Z_][a-zA-Z0-9_]*|[0-9]+(?:\.[0-9]+)?|[^\s]', code)

# =========================
# FUNCTION
# =========================
def analyze_code():
    code = input_box.get("1.0", tk.END)
    tokens = tokenize(code)

    output_box.config(state="normal")
    output_box.delete("1.0", tk.END)

    for token in tokens:
        category = classify_token(token)

        # warna berdasarkan kategori
        tag = category
        output_box.insert(tk.END, f"{token:10} -> {category}\n", tag)

    output_box.config(state="disabled")

def load_file():
    file_path = filedialog.askopenfilename()
    if file_path:
        with open(file_path, "r") as f:
            input_box.delete("1.0", tk.END)
            input_box.insert(tk.END, f.read())

def clear_all():
    input_box.delete("1.0", tk.END)
    output_box.config(state="normal")
    output_box.delete("1.0", tk.END)
    output_box.config(state="disabled")

# =========================
# UI SETUP
# =========================
root = tk.Tk()
root.title("Tokenizer Analyzer")
root.geometry("1000x600")
root.configure(bg="#4A90E2")

# ===== HEADER =====
header = tk.Frame(root, bg="#4A90E2")
header.pack(fill="x", padx=10, pady=5)

tk.Label(header, text="Input Program:", fg="white", bg="#4A90E2",
        font=("Arial", 14, "bold")).pack(side="left")

tk.Button(header, text="Load File", command=load_file,
        bg="white").pack(side="left", padx=10)

# ===== MAIN FRAME =====
main_frame = tk.Frame(root, bg="#4A90E2")
main_frame.pack(fill="both", expand=True, padx=10)

# INPUT BOX
input_box = ScrolledText(main_frame, wrap=tk.WORD, height=15)
input_box.pack(fill="both", expand=True, pady=5)

# BUTTONS
btn_frame = tk.Frame(root, bg="#4A90E2")
btn_frame.pack(pady=5)

tk.Button(btn_frame, text="Analyze", width=12,
        command=analyze_code).pack(side="left", padx=10)

tk.Button(btn_frame, text="Clear", width=12,
        command=clear_all).pack(side="left", padx=10)

# OUTPUT LABEL
tk.Label(root, text="Hasil Token:", fg="white", bg="#4A90E2",
        font=("Arial", 14, "bold")).pack(anchor="w", padx=10)

# OUTPUT BOX
output_box = ScrolledText(root, wrap=tk.WORD, height=15, state="disabled")
output_box.pack(fill="both", expand=True, padx=10, pady=5)

output_box.tag_config("Reserved Word", foreground="blue")
output_box.tag_config("Variable", foreground="black")
output_box.tag_config("Symbol", foreground="purple")
output_box.tag_config("Math", foreground="green")
output_box.tag_config("Unknown", foreground="red")

root.mainloop()