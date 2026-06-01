import tkinter as tk
from tkinter import messagebox
from tkinter import ttk
import re

# ------------------------------
# Language Definitions
# ------------------------------
KEYWORDS = {"START", "END", "IF", "THEN", "PRINT"}

# ------------------------------
# Syntax Highlighting Colors
# ------------------------------
SYNTAX_COLORS = {
    "KEYWORD": "#c678dd",
    "OPERATOR": "#56b6c2",
    "NUMBER": "#d19a66",
    "IDENTIFIER": "#61afef",
    "DELIMITER": "#abb2bf",
}

# ------------------------------
# 1. Lexical Analysis (UPDATED)
# ------------------------------
def lexical_analysis(code):
    tokens, errors = [], []
    literal_table = {}
    lit_id = 1

    lines = code.split('\n')
    for line_num, line_content in enumerate(lines, 1):
        pos = 0
        while pos < len(line_content):
            char = line_content[pos]

            if char.isspace():
                pos += 1
                continue

            match = re.match(r'[A-Za-z]+|\d+|==|!=|>=|<=|\|\||&&|[=;()><+\-*/]', line_content[pos:])
            if match:
                word = match.group()

                if word in KEYWORDS:
                    tokens.append(("KEYWORD", word, line_num))

                elif word in ["=", ">", "<", ">=", "<=", "==", "!=", "+", "-", "*", "/", "&&", "||"]:
                    tokens.append(("OPERATOR", word, line_num))

                elif word in [";", "(", ")"]:
                    tokens.append(("DELIMITER", word, line_num))

                elif word.isdigit():
                    tokens.append(("NUMBER", word, line_num))
                    if word not in literal_table:
                        literal_table[word] = f"L{lit_id}"
                        lit_id += 1

                elif word.isidentifier():
                    tokens.append(("IDENTIFIER", word, line_num))

                pos += len(word)
            else:
                errors.append(f"Line {line_num}: Lexical Error: Invalid token '{char}'")
                pos += 1

    return tokens, errors, literal_table


# ------------------------------
# Parse Tree
# ------------------------------
class Node:
    def __init__(self, val):
        self.val = val
        self.children = []

    def add(self, child):
        self.children.append(child)

def print_tree(node, level=0):
    s = "  " * level + node.val + "\n"
    for c in node.children:
        s += print_tree(c, level+1)
    return s


# ------------------------------
# 2. Recursive Descent Parser
# ------------------------------
class Parser:
    def __init__(self, tokens):
        self.tokens = tokens
        self.pos = 0
        self.errors = []
        self.root = Node("Program")

    def current(self):
        return self.tokens[self.pos] if self.pos < len(self.tokens) else None

    def consume(self):
        tok = self.current()
        self.pos += 1
        return tok

    def match(self, val):
        tok = self.current()
        if tok and tok[1] == val:
            return self.consume()
        else:
            line = tok[2] if tok else "EOF"
            self.errors.append(f"Line {line}: Expected '{val}'")
            return None

    def program(self):
        if not self.match("START"): return
        stmt_list = Node("StmtList")
        self.root.add(stmt_list)

        while self.current() and self.current()[1] != "END":
            stmt = self.statement()
            if stmt:
                stmt_list.add(stmt)
            else:
                self.recover()

        self.match("END")

    def recover(self):
        while self.current() and self.current()[1] != ";":
            self.consume()
        if self.current():
            self.consume()

    def statement(self):
        tok = self.current()
        if not tok: return None

        if tok[0] == "IDENTIFIER":
            return self.assignment()
        elif tok[1] == "PRINT":
            return self.print_stmt()
        elif tok[1] == "IF":
            return self.if_stmt()
        else:
            self.errors.append(f"Line {tok[2]}: Invalid statement")
            return None

    def assignment(self):
        node = Node("Assign")
        var = self.consume()
        node.add(Node(var[1]))
        self.match("=")

        val = self.consume()
        node.add(Node(val[1]))

        self.match(";")
        return node

    def print_stmt(self):
        node = Node("Print")
        self.match("PRINT")
        var = self.consume()
        node.add(Node(var[1]))
        self.match(";")
        return node

    def if_stmt(self):
        node = Node("If")
        self.match("IF")
        self.match("(")

        v1 = self.consume()
        op = self.consume()
        n1 = self.consume()

        cond = Node("Cond")
        cond.add(Node(v1[1]))
        cond.add(Node(op[1]))
        cond.add(Node(n1[1]))

        if self.current() and self.current()[1] in ["&&", "||"]:
            logic = self.consume()
            v2 = self.consume()
            op2 = self.consume()
            n2 = self.consume()

            cond.add(Node(logic[1]))
            cond.add(Node(v2[1]))
            cond.add(Node(op2[1]))
            cond.add(Node(n2[1]))

        node.add(cond)

        self.match(")")
        self.match("THEN")

        stmt = self.print_stmt()
        node.add(stmt)

        return node


# ------------------------------
# 3. Semantic Analysis (IMPROVED)
# ------------------------------
def semantic_analysis(tokens):
    assigned = set()
    errors = []
    warnings = []
    symbol_table = {}

    for i, t in enumerate(tokens):
        if t[0] == "IDENTIFIER":
            if t[1] not in assigned:
                warnings.append(f"Line {t[2]}: '{t[1]}' used before assignment")
            symbol_table[t[1]] = "int"

        if t[1] == "=":
            var = tokens[i-1][1]
            if var in assigned:
                warnings.append(f"Line {t[2]}: Duplicate assignment '{var}'")
            assigned.add(var)

    return errors, warnings, symbol_table


# ------------------------------
# 4. Intermediate Code (same)
# ------------------------------
def intermediate_code(tokens):
    code = []
    for i in range(len(tokens)):
        if tokens[i][0] == "IDENTIFIER" and i+2 < len(tokens):
            if tokens[i+1][1] == "=":
                code.append(f"LOAD {tokens[i][1]}, {tokens[i+2][1]}")
        if tokens[i][1] == "PRINT":
            code.append(f"PRINT {tokens[i+1][1]}")
    return code


# ------------------------------
# 5. Optimization (Enhanced)
# ------------------------------
def optimize(code):
    seen = set()
    opt = []
    for line in code:
        if line not in seen:
            opt.append(line)
            seen.add(line)
    return opt


# ------------------------------
# 6. Target Code
# ------------------------------
def target_code(code):
    return [f"ASM -> {c}" for c in code]


# ------------------------------
# EXECUTION
# ------------------------------
def execute_code(code):
    mem = {}
    out = []
    for line in code:
        p = line.split()
        if p[0] == "LOAD":
            mem[p[1].strip(",")] = int(p[2])
        elif p[0] == "PRINT":
            out.append(str(mem.get(p[1], 0)))
    return "\n".join(out)


# ------------------------------
# COMPILE (UPDATED ONLY BACKEND)
# ------------------------------
def compile_code():
    code = text_input.get("1.0", tk.END)
    text_input.tag_remove("error", "1.0", tk.END)

    for tab in tabs.values():
        if isinstance(tab, tk.Text):
            tab.delete("1.0", tk.END)

    try:
        tokens, lex_errors, literal_table = lexical_analysis(code)

        parser = Parser(tokens)
        parser.program()

        errors = lex_errors + parser.errors
        if errors:
            tabs["Syntax"].insert(tk.END, "\n".join(errors))
            for err in errors:
                m = re.search(r'Line (\d+)', err)
                if m:
                    text_input.tag_add("error", f"{m.group(1)}.0", f"{m.group(1)}.end")
            text_input.tag_config("error", background="#450a0a", foreground="#f87171")
            return

        sem_err, warnings, sym = semantic_analysis(tokens)

        ic = intermediate_code(tokens)
        opt = optimize(ic)
        tgt = target_code(opt)
        out = execute_code(opt)

        tabs["Tokens"].insert(tk.END, "\n".join([str(t) for t in tokens]))
        tabs["Syntax"].insert(tk.END, "✔ Syntax Correct")
        tabs["Semantic"].insert(tk.END, "\n".join(warnings) or "No Issues")

        for i in symbol_tree.get_children():
            symbol_tree.delete(i)
        for k, v in sym.items():
            symbol_tree.insert("", "end", values=(k, v))

        tabs["Intermediate"].insert(tk.END, "\n".join(ic))
        tabs["Optimized"].insert(tk.END, "\n".join(opt))
        tabs["Target"].insert(tk.END, "\n".join(tgt))
        tabs["Execution"].insert(tk.END, out or "No Output")

        tabs["Parse Tree"].insert(tk.END, print_tree(parser.root))
        tabs["LiteralTable"].insert(tk.END,
            "\n".join([f"{k} → {v}" for k,v in literal_table.items()]))

        status.config(text="✔ Compilation Successful", fg="#22c55e")

    except Exception as e:
        messagebox.showerror("Compiler Error", str(e))


# ------------------------------
# GUI (UNCHANGED FROM YOUR CODE)
# ------------------------------
# ⚠️ ONLY CHANGE: added 2 tab names

root = tk.Tk()
root.title("MiniLang Compiler IDE")
root.geometry("1200x750")
root.configure(bg="#0f172a")

status_frame = tk.Frame(root, bg="#1e293b", height=35)
status_frame.pack(side="bottom", fill="x")
status = tk.Label(status_frame, text="Ready to compile", bg="#1e293b", fg="#64748b", font=("Segoe UI", 10), anchor="w", padx=15, pady=5)
status.pack(side="left")

header = tk.Frame(root, bg="#1e293b", height=60)
header.pack(side="top", fill="x")

button_frame = tk.Frame(root, bg="#0f172a")
button_frame.pack(side="bottom", pady=12)

tk.Button(button_frame, text="▶ Compile & Run", command=compile_code,
          bg="#22c55e").grid(row=0, column=0)

main_frame = tk.Frame(root)
main_frame.pack(fill="both", expand=True)

text_input = tk.Text(main_frame)
text_input.pack(side="left", fill="both", expand=True)

notebook = ttk.Notebook(main_frame)
notebook.pack(side="right", fill="both", expand=True)

tabs = {}
for name in ["Tokens","Syntax","Semantic","Intermediate","Optimized","Target","Execution","Flow","Parse Tree","LiteralTable"]:
    f = tk.Frame(notebook)
    t = tk.Text(f)
    t.pack(fill="both", expand=True)
    notebook.add(f, text=name)
    tabs[name] = t

symbol_tree = ttk.Treeview(root, columns=("Variable","Type"), show="headings")
symbol_tree.heading("Variable", text="Variable Name")
symbol_tree.heading("Type", text="Data Type")
symbol_tree.pack()

root.mainloop()