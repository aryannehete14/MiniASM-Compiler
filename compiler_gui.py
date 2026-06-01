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
# 1. Lexical Analysis
# ------------------------------
def lexical_analysis(code):
    tokens = []
    errors = []
    literals = []
    lines = code.split('\n')

    for line_num, line_content in enumerate(lines, 1):
        position = 0

        while position < len(line_content):
            char = line_content[position]

            if char.isspace():
                position += 1
                continue

            match = re.match(
                r'[A-Za-z_][A-Za-z0-9_]*|\d+|==|!=|>=|<=|\|\||&&|[=;()><+\-*/]',
                line_content[position:]
            )

            if match:
                word = match.group()

                if word in KEYWORDS:
                    tokens.append(("KEYWORD", word, line_num))

                elif word in [
                    "=", ">", "<", ">=", "<=",
                    "==", "!=", "+", "-", "*",
                    "/", "&&", "||"
                ]:
                    tokens.append(("OPERATOR", word, line_num))

                elif word in [";", "(", ")"]:
                    tokens.append(("DELIMITER", word, line_num))

                elif word.isdigit():
                    tokens.append(("NUMBER", word, line_num))

                    if ("int", word) not in literals:
                        literals.append(("int", word))

                elif word.isidentifier():
                    tokens.append(("IDENTIFIER", word, line_num))

                position += len(word)

            else:
                errors.append(
                    f"Line {line_num}: Lexical Error: Invalid token '{char}'"
                )
                position += 1

    return tokens, errors, literals

# ------------------------------
# 2. Syntax Analysis
# ------------------------------
def syntax_analysis(tokens):
    errors = []

    if len(tokens) == 0:
        return "Empty program", ["Line 1: Empty program"]

    has_start = any(t[1] == "START" for t in tokens)
    has_end = any(t[1] == "END" for t in tokens)

    if has_start and not has_end:
        errors.append("If START is used, END must also be present")

    if has_end and not has_start:
        errors.append("If END is used, START must also be present")

    if has_start and has_end:

        if tokens[0][1] != "START":
            errors.append(
                f"Line {tokens[0][2]}: START must be the first keyword"
            )

        if tokens[-1][1] != "END":
            errors.append(
                f"Line {tokens[-1][2]}: END must be the last keyword"
            )

    if errors:
        return "Syntax errors found", errors

    return "Syntax is correct (START/END optional)", []

# ------------------------------
# 3. Semantic Analysis
# ------------------------------
def semantic_analysis(tokens):

    symbol_table = {}
    initialized = set()
    semantic_errors = []
    variables_used = set()

    i = 0

    while i < len(tokens):

        token_type, value, line = tokens[i]

        # ----------------------
        # Assignment Checking
        # ----------------------
        if token_type == "IDENTIFIER":

            var_name = value

            variables_used.add(var_name)

            # Auto declare variable
            if var_name not in symbol_table:

                symbol_table[var_name] = "int"

            # Assignment
            if i + 1 < len(tokens) and tokens[i + 1][1] == "=":

                if i + 2 >= len(tokens):

                    semantic_errors.append(
                        f"Line {line}: Missing assignment value"
                    )

                    break

                rhs = tokens[i + 2]

                # ----------------------
                # Datatype Checking
                # ----------------------
                if rhs[0] == "NUMBER":

                    pass

                elif rhs[0] == "IDENTIFIER":

                    rhs_var = rhs[1]

                    variables_used.add(rhs_var)

                    # Auto declare RHS variable
                    if rhs_var not in symbol_table:

                        symbol_table[rhs_var] = "int"

                    # Initialization Check
                    if rhs_var not in initialized:

                        semantic_errors.append(
                            f"Line {line}: Variable '{rhs_var}' used before initialization"
                        )

                else:

                    semantic_errors.append(
                        f"Line {line}: Type mismatch in assignment"
                    )

                initialized.add(var_name)

        # ----------------------
        # PRINT Checking
        # ----------------------
        if value == "PRINT":

            if i + 1 < len(tokens):

                var = tokens[i + 1][1]

                variables_used.add(var)

                if var not in symbol_table:

                    symbol_table[var] = "int"

                if var not in initialized:

                    semantic_errors.append(
                        f"Line {line}: Variable '{var}' used before initialization"
                    )

        # ----------------------
        # IF Condition Checking
        # ----------------------
        if value == "IF":

            j = i + 1

            while j < len(tokens) and tokens[j][1] != "THEN":

                t_type, t_value, t_line = tokens[j]

                if t_type == "IDENTIFIER":

                    variables_used.add(t_value)

                    if t_value not in symbol_table:

                        symbol_table[t_value] = "int"

                    if t_value not in initialized:

                        semantic_errors.append(
                            f"Line {t_line}: Variable '{t_value}' used before initialization"
                        )

                j += 1

        i += 1

    semantic_output = (
        f"Variables used: "
        f"{', '.join(sorted(variables_used)) if variables_used else 'None'}"
    )

    if semantic_errors:

        semantic_output += (
            "\n\n[SEMANTIC ERRORS]\n"
            + "\n".join(semantic_errors)
        )

    return semantic_output, symbol_table
# ------------------------------
# Parse Tree Generation
# ------------------------------
def generate_parse_tree(tokens):
    tree = ["Program"]

    has_start = any(t[1] == "START" for t in tokens)

    i = 0

    if has_start and tokens[i][1] == "START":
        tree.append("├─ START")
        i = 1

    while i < len(tokens):

        token_type, value, line = tokens[i]

        if value == "END":
            tree.append("└─ END")
            break

        if (
            token_type == "IDENTIFIER"
            and i + 1 < len(tokens)
            and tokens[i + 1][1] == "="
        ):

            tree.append("├─ Assignment")
            tree.append("│  ├─ Identifier: " + value)
            tree.append("│  ├─ Operator: =")

            if i + 2 < len(tokens):
                tree.append("│  ├─ Value: " + tokens[i + 2][1])

            if i + 3 < len(tokens) and tokens[i + 3][1] == ";":
                tree.append("│  └─ Delimiter: ;")

            i += 4

        elif value == "PRINT":

            tree.append("├─ Print Statement")
            tree.append("│  ├─ Keyword: PRINT")

            if i + 1 < len(tokens):
                tree.append("│  ├─ Variable: " + tokens[i + 1][1])

            if i + 2 < len(tokens) and tokens[i + 2][1] == ";":
                tree.append("│  └─ Delimiter: ;")

            i += 3

        elif value == "IF":

            tree.append("├─ If Statement")
            tree.append("│  ├─ Keyword: IF")
            tree.append("│  ├─ Condition")

            j = i + 1

            while j < len(tokens) and tokens[j][1] != "THEN":

                if tokens[j][1] == "(":
                    tree.append("│  │  ├─ (")

                elif tokens[j][1] == ")":
                    tree.append("│  │  └─ )")

                elif tokens[j][0] == "IDENTIFIER":
                    tree.append("│  │  ├─ Variable: " + tokens[j][1])

                elif tokens[j][0] == "OPERATOR":
                    tree.append("│  │  ├─ Operator: " + tokens[j][1])

                elif tokens[j][0] == "NUMBER":
                    tree.append("│  │  ├─ Number: " + tokens[j][1])

                j += 1

            if j < len(tokens) and tokens[j][1] == "THEN":
                tree.append("│  ├─ Keyword: THEN")
                j += 1

            if j < len(tokens) and tokens[j][1] == "PRINT":

                tree.append("│  ├─ Print Statement")
                tree.append("│  │  ├─ Keyword: PRINT")

                if j + 1 < len(tokens):
                    tree.append("│  │  ├─ Variable: " + tokens[j + 1][1])

                if j + 2 < len(tokens) and tokens[j + 2][1] == ";":
                    tree.append("│  │  └─ Delimiter: ;")

            i = j + 3

        else:
            i += 1

    return "\n".join(tree)

# ------------------------------
# 4. Intermediate Code Generation
# ------------------------------
def intermediate_code(tokens):

    code = []
    stream = list(tokens)

    def peek():
        return stream[0][1] if stream else None

    def consume():
        return stream.pop(0)

    while stream:

        token_type, value, line = consume()

        # Ignore START and END
        if value in ["START", "END"]:
            continue

        # ----------------------
        # ASSIGNMENT
        # ----------------------
        if token_type == "IDENTIFIER":

            var = value

            if not stream:
                raise Exception(
                    f"Line {line}: Incomplete assignment statement"
                )

            if peek() != "=":

                if peek() == ";":
                    raise Exception(
                        f"Line {line}: Standalone identifier '{var}' is invalid"
                    )

                raise Exception(
                    f"Line {line}: Missing '=' in assignment"
                )

            consume()  # '='

            if not stream:
                raise Exception(
                    f"Line {line}: Missing value in assignment"
                )

            # First operand
            if stream[0][0] not in ["NUMBER", "IDENTIFIER"]:
                raise Exception(
                    f"Line {line}: Invalid assignment value"
                )

            left = consume()[1]

            # ----------------------
            # Arithmetic Expression
            # ----------------------
            if stream and peek() in ["+", "-", "*", "/"]:

                operator = consume()[1]

                if not stream:
                    raise Exception(
                        f"Line {line}: Missing second operand"
                    )

                if stream[0][0] not in ["NUMBER", "IDENTIFIER"]:
                    raise Exception(
                        f"Line {line}: Invalid arithmetic operand"
                    )

                right = consume()[1]

                if not stream or peek() != ";":
                    raise Exception(
                        f"Line {line}: Missing ';' after assignment"
                    )

                consume()  # ';'

                code.append(
                    f"LOAD {var}, {left} {operator} {right}"
                )

            # ----------------------
            # Normal Assignment
            # ----------------------
            else:

                if not stream or peek() != ";":
                    raise Exception(
                        f"Line {line}: Missing ';' after assignment"
                    )

                consume()  # ';'

                code.append(f"LOAD {var}, {left}")

        # ----------------------
        # PRINT
        # ----------------------
        elif value == "PRINT":

            if not stream:
                raise Exception(
                    f"Line {line}: Missing variable after PRINT"
                )

            if stream[0][1] == ";":
                raise Exception(
                    f"Line {line}: Missing variable after PRINT"
                )

            if stream[0][0] != "IDENTIFIER":
                raise Exception(
                    f"Line {line}: PRINT expects a variable"
                )

            var = consume()[1]

            if not stream or peek() != ";":
                raise Exception(
                    f"Line {line}: Missing ';' after PRINT"
                )

            consume()  # ';'

            code.append(f"PRINT {var}")

        # ----------------------
        # IF CONDITION
        # ----------------------
        elif value == "IF":

            if not stream or peek() != "(":
                raise Exception(
                    f"Line {line}: Missing '(' after IF"
                )

            consume()  # '('

            if len(stream) < 3:
                raise Exception(
                    f"Line {line}: Incomplete IF condition"
                )

            if stream[0][0] != "IDENTIFIER":
                raise Exception(
                    f"Line {line}: Invalid variable in IF condition"
                )

            v1 = consume()[1]

            if peek() not in [">", "<", ">=", "<=", "==", "!="]:
                raise Exception(
                    f"Line {line}: Invalid comparison operator"
                )

            op1 = consume()[1]

            if stream[0][0] not in ["NUMBER", "IDENTIFIER"]:
                raise Exception(
                    f"Line {line}: Invalid comparison value"
                )

            n1 = consume()[1]

            # Logical condition
            if stream and peek() in ["&&", "||"]:

                logic_op = consume()[1]

                if len(stream) < 3:
                    raise Exception(
                        f"Line {line}: Incomplete logical condition"
                    )

                if stream[0][0] != "IDENTIFIER":
                    raise Exception(
                        f"Line {line}: Invalid variable in logical condition"
                    )

                v2 = consume()[1]

                if peek() not in [">", "<", ">=", "<=", "==", "!="]:
                    raise Exception(
                        f"Line {line}: Invalid comparison operator"
                    )

                op2 = consume()[1]

                if stream[0][0] not in ["NUMBER", "IDENTIFIER"]:
                    raise Exception(
                        f"Line {line}: Invalid comparison value"
                    )

                n2 = consume()[1]

                if not stream or peek() != ")":
                    raise Exception(
                        f"Line {line}: Missing ')' in IF condition"
                    )

                consume()

                if not stream or peek() != "THEN":
                    raise Exception(
                        f"Line {line}: Missing THEN"
                    )

                consume()

                if not stream or peek() != "PRINT":
                    raise Exception(
                        f"Line {line}: Expected PRINT after THEN"
                    )

                consume()

                if not stream:
                    raise Exception(
                        f"Line {line}: Missing variable after PRINT"
                    )

                prnt_var = consume()[1]

                if not stream or peek() != ";":
                    raise Exception(
                        f"Line {line}: Missing ';' after PRINT"
                    )

                consume()

                code.append(
                    f"IF {v1} {op1} {n1} {logic_op} {v2} {op2} {n2}"
                )

                code.append(f"PRINT {prnt_var}")

            else:

                if not stream or peek() != ")":
                    raise Exception(
                        f"Line {line}: Missing ')' in IF condition"
                    )

                consume()

                if not stream or peek() != "THEN":
                    raise Exception(
                        f"Line {line}: Missing THEN"
                    )

                consume()

                if not stream or peek() != "PRINT":
                    raise Exception(
                        f"Line {line}: Expected PRINT after THEN"
                    )

                consume()

                if not stream:
                    raise Exception(
                        f"Line {line}: Missing variable after PRINT"
                    )

                prnt_var = consume()[1]

                if not stream or peek() != ";":
                    raise Exception(
                        f"Line {line}: Missing ';' after PRINT"
                    )

                consume()

                code.append(f"IF {v1} {op1} {n1}")
                code.append(f"PRINT {prnt_var}")

        else:
            raise Exception(
                f"Line {line}: Invalid statement '{value}'"
            )

    return code

# ------------------------------
# 5. Optimization & 6. Target Code
# ------------------------------
def optimize(code):
    optimized = []
    seen = set()

    for line in code:

        if line.startswith("LOAD"):

            if line not in seen:
                optimized.append(line)
                seen.add(line)

        else:
            optimized.append(line)

    return optimized

def target_code(code):
    return [f"ASM -> {line}" for line in code]

# ------------------------------
# EXECUTION
# ------------------------------
def evaluate_condition(memory, var, op, val):

    x = memory.get(var, 0)
    val = int(val)

    ops = {
        ">": x > val,
        "<": x < val,
        ">=": x >= val,
        "<=": x <= val,
        "==": x == val,
        "!=": x != val
    }

    return ops.get(op, False)

def execute_code(code):

    memory = {}
    output = []
    skip_next = False

    for line in code:

        parts = line.split()

        # ----------------------
        # LOAD
        # ----------------------
        if parts[0] == "LOAD":

            var = parts[1].strip(",")

            # Arithmetic expression
            if len(parts) == 5:

                left = parts[2]
                op = parts[3]
                right = parts[4]

                left_val = (
                    memory[left]
                    if left in memory
                    else int(left)
                )

                right_val = (
                    memory[right]
                    if right in memory
                    else int(right)
                )

                if op == "+":
                    result = left_val + right_val

                elif op == "-":
                    result = left_val - right_val

                elif op == "*":
                    result = left_val * right_val

                elif op == "/":
                    result = left_val // right_val

                memory[var] = result

            # Normal assignment
            else:

                value = parts[2]

                memory[var] = (
                    memory[value]
                    if value in memory
                    else int(value)
                )

        # ----------------------
        # IF
        # ----------------------
        elif parts[0] == "IF":

            if any(op in parts for op in ["&&", "||"]):

                res1 = evaluate_condition(
                    memory,
                    parts[1],
                    parts[2],
                    parts[3]
                )

                res2 = evaluate_condition(
                    memory,
                    parts[5],
                    parts[6],
                    parts[7]
                )

                if parts[4] == "&&":
                    skip_next = not (res1 and res2)
                else:
                    skip_next = not (res1 or res2)

            else:

                skip_next = not evaluate_condition(
                    memory,
                    parts[1],
                    parts[2],
                    parts[3]
                )

        # ----------------------
        # PRINT
        # ----------------------
        elif parts[0] == "PRINT":

            if not skip_next:
                output.append(str(memory.get(parts[1], 0)))

            skip_next = False

    return "\n".join(output)

# ------------------------------
# GUI & Logic
# ------------------------------
def highlight_syntax(event=None):

    for tag in text_input.tag_names():

        if tag not in ["sel", "error"]:
            text_input.tag_remove(tag, "1.0", tk.END)

    code = text_input.get("1.0", tk.END)

    for match in re.finditer(
        r'[A-Za-z_][A-Za-z0-9_]*|\d+|==|!=|>=|<=|\|\||&&|[=;()><+\-*/]',
        code
    ):

        word = match.group()

        s_idx = f"1.0+{match.start()}c"
        e_idx = f"1.0+{match.end()}c"

        if word in KEYWORDS:
            text_input.tag_add("KEYWORD", s_idx, e_idx)

        elif word in [
            "=", ">", "<", ">=", "<=",
            "==", "!=", "+", "-", "*",
            "/", "&&", "||"
        ]:
            text_input.tag_add("OPERATOR", s_idx, e_idx)

        elif word in [";", "(", ")"]:
            text_input.tag_add("DELIMITER", s_idx, e_idx)

        elif word.isdigit():
            text_input.tag_add("NUMBER", s_idx, e_idx)

        elif word.isidentifier():
            text_input.tag_add("IDENTIFIER", s_idx, e_idx)

    for tag, color in SYNTAX_COLORS.items():

        text_input.tag_config(
            tag,
            foreground=color,
            font=(
                "Consolas",
                11,
                "bold" if tag == "KEYWORD" else "normal"
            )
        )

def update_line_numbers(event=None):

    line_numbers.config(state="normal")
    line_numbers.delete("1.0", tk.END)

    line_count = int(
        text_input.index('end-1c').split('.')[0]
    )

    line_numbers.insert(
        "1.0",
        "\n".join(str(i) for i in range(1, line_count + 1))
    )

    line_numbers.config(state="disabled")

    line_numbers.yview_moveto(text_input.yview()[0])

def on_text_scroll(*args):

    line_numbers.yview_moveto(text_input.yview()[0])
    text_input_scroll.set(*args)

def compile_code():

    code = text_input.get("1.0", tk.END)

    text_input.tag_remove("error", "1.0", tk.END)

    for tab in tabs.values():

        if isinstance(tab, tk.Text):
            tab.delete("1.0", tk.END)

    for item in literal_tree.get_children():
        literal_tree.delete(item)

    try:

        tokens, lex_errors, literals = lexical_analysis(code)

        syntax_msg, syn_errors = syntax_analysis(tokens)

        all_errors = lex_errors + syn_errors

        if all_errors:

            tabs["Syntax"].insert(
                tk.END,
                "[COMPILATION ERRORS]\n\n" + "\n".join(all_errors)
            )

            status.config(
                text=f"❌ Found {len(all_errors)} Errors",
                fg="#ef4444"
            )

            for err in all_errors:

                match = re.search(r'Line (\d+)', err)

                if match:
                    line_num = match.group(1)

                    text_input.tag_add(
                        "error",
                        f"{line_num}.0",
                        f"{line_num}.end"
                    )

            text_input.tag_config(
                "error",
                background="#450a0a",
                foreground="#f87171"
            )

            notebook.select(1)
            return

        semantic, symbol_table = semantic_analysis(tokens)

        parse_tree_output = generate_parse_tree(tokens)

        ic = intermediate_code(tokens)

        opt = optimize(ic)

        target = target_code(opt)

        execution_output = execute_code(opt)

        tabs["Tokens"].insert(
            tk.END,
            "[TOKENS]\n\n" + "\n".join(
                [f"{t[0]} → {t[1]}" for t in tokens]
            )
        )

        tabs["Syntax"].insert(
            tk.END,
            "[SYNTAX ANALYSIS]\n\n" + syntax_msg
        )

        tabs["ParseTree"].insert(
            tk.END,
            "[PARSE TREE]\n\n" + parse_tree_output
        )

        tabs["Semantic"].insert(
            tk.END,
            "[SEMANTIC ANALYSIS]\n\n" + semantic
        )

        for item in symbol_tree.get_children():
            symbol_tree.delete(item)

        for k, v in symbol_table.items():
            symbol_tree.insert("", "end", values=(k, v))

        for idx, (lit_type, lit_val) in enumerate(literals, 1):
            literal_tree.insert(
                "",
                "end",
                values=(idx, lit_val, lit_type)
            )

        tabs["Intermediate"].insert(
            tk.END,
            "[INTERMEDIATE CODE]\n\n" + "\n".join(ic)
        )

        tabs["Optimized"].insert(
            tk.END,
            "[OPTIMIZED CODE]\n\n" + "\n".join(opt)
        )

        tabs["Target"].insert(
            tk.END,
            "[TARGET CODE]\n\n" + "\n".join(target)
        )

        tabs["Execution"].insert(
            tk.END,
            "[PROGRAM OUTPUT]\n\n" +
            (execution_output or "No Output")
        )

        tabs["Flow"].insert(
    tk.END,
    "SOURCE PROGRAM\n"
    "        ↓\n"
    "1. LEXICAL ANALYSIS\n"
    "   - Token Generation\n"
    "   - Literal Detection\n"
    "        ↓\n"
    "2. SYNTAX ANALYSIS\n"
    "   - Grammar Validation\n"
    "   - Statement Checking\n"
    "        ↓\n"
    "3. PARSE TREE GENERATION\n"
    "   - Program Structure\n"
    "        ↓\n"
    "4. SEMANTIC ANALYSIS\n"
    "   - Variable Identification\n"
    "   - Symbol Table Creation\n"
    "        ↓\n"
    "5. INTERMEDIATE CODE GENERATION\n"
    "   - LOAD / IF / PRINT Instructions\n"
    "        ↓\n"
    "6. CODE OPTIMIZATION\n"
    "   - Remove Redundant LOAD Instructions\n"
    "        ↓\n"
    "7. TARGET CODE GENERATION\n"
    "   - ASM Representation\n"
    "        ↓\n"
    "8. EXECUTION PHASE\n"
    "   - Final Output Display"
)

        status.config(
            text="✔ Compilation Successful",
            fg="#22c55e"
        )

    except Exception as e:

        error_msg = str(e)

        status.config(
            text=f"❌ Error: {error_msg}",
            fg="#ef4444"
        )

        match = re.search(r'Line (\d+)', error_msg)

        if match:

            line_num = match.group(1)

            text_input.tag_add(
                "error",
                f"{line_num}.0",
                f"{line_num}.end"
            )

            text_input.tag_config(
                "error",
                background="#450a0a",
                foreground="#f87171"
            )

        messagebox.showerror("Compiler Error", error_msg)

root = tk.Tk()

root.title("MiniLang Compiler IDE")
root.geometry("1200x750")
root.configure(bg="#0f172a")

status_frame = tk.Frame(root, bg="#1e293b", height=35)
status_frame.pack(side="bottom", fill="x")

status = tk.Label(
    status_frame,
    text="Ready to compile",
    bg="#1e293b",
    fg="#64748b",
    font=("Segoe UI", 10),
    anchor="w",
    padx=15,
    pady=5
)

status.pack(side="left")

tk.Label(
    status_frame,
    text="v1.0.0 | Python Tkinter",
    bg="#1e293b",
    fg="#475569",
    font=("Segoe UI", 9),
    anchor="e",
    padx=15
).pack(side="right")

header = tk.Frame(root, bg="#1e293b", height=60)
header.pack(side="top", fill="x")

title_frame = tk.Frame(header, bg="#1e293b")
title_frame.pack(pady=10)

tk.Label(
    title_frame,
    text="⚡ MiniLang",
    font=("Segoe UI", 18, "bold"),
    bg="#1e293b",
    fg="#38bdf8"
).pack(side="left", padx=5)

tk.Label(
    title_frame,
    text="Compiler IDE",
    font=("Segoe UI", 18),
    bg="#1e293b",
    fg="#94a3b8"
).pack(side="left")

button_frame = tk.Frame(root, bg="#0f172a")
button_frame.pack(side="bottom", pady=12)

tk.Button(
    button_frame,
    text="▶ Compile & Run",
    command=compile_code,
    font=("Segoe UI", 11, "bold"),
    bg="#22c55e",
    fg="#0a0f1e",
    relief=tk.FLAT,
    padx=25,
    pady=8,
    cursor="hand2"
).grid(row=0, column=0, padx=8)

tk.Button(
    button_frame,
    text="🗑 Clear All",
    command=lambda: [
        text_input.delete("1.0", tk.END),
        [
            tab.delete("1.0", tk.END)
            for tab in tabs.values()
            if isinstance(tab, tk.Text)
        ],
        [
            symbol_tree.delete(i)
            for i in symbol_tree.get_children()
        ],
        [
            literal_tree.delete(i)
            for i in literal_tree.get_children()
        ],
        update_line_numbers(),
        status.config(text="Ready", fg="#64748b")
    ],
    font=("Segoe UI", 11, "bold"),
    bg="#ef4444",
    fg="white",
    relief=tk.FLAT,
    padx=25,
    pady=8,
    cursor="hand2"
).grid(row=0, column=1, padx=8)

main_frame = tk.Frame(root, bg="#0f172a")
main_frame.pack(fill="both", expand=True, padx=15, pady=10)

main_frame.grid_rowconfigure(0, weight=1)
main_frame.grid_columnconfigure(0, weight=1)
main_frame.grid_columnconfigure(1, weight=1)

input_frame = tk.LabelFrame(
    main_frame,
    text=" 📝 Source Code Editor ",
    font=("Segoe UI", 11, "bold"),
    bg="#1e293b",
    fg="#e2e8f0",
    relief=tk.FLAT,
    borderwidth=2,
    padx=5,
    pady=5
)

input_frame.grid(
    row=0,
    column=0,
    sticky="nsew",
    padx=5,
    pady=5
)

editor_container = tk.Frame(input_frame, bg="#0a0f1e")
editor_container.pack(fill="both", expand=True)

line_numbers = tk.Text(
    editor_container,
    width=4,
    font=("Consolas", 11),
    bg="#0a0f1e",
    fg="#475569",
    bd=0,
    padx=5,
    pady=10,
    state="disabled",
    cursor="arrow",
    takefocus=0
)

line_numbers.pack(side="left", fill="y")

text_input_scroll = tk.Scrollbar(
    editor_container,
    bg="#1e293b"
)

text_input_scroll.pack(side="right", fill="y")

text_input = tk.Text(
    editor_container,
    font=("Consolas", 11),
    bg="#0a0f1e",
    fg="#e2e8f0",
    insertbackground="#38bdf8",
    selectbackground="#334155",
    selectforeground="#e2e8f0",
    yscrollcommand=on_text_scroll,
    bd=0,
    padx=10,
    pady=10,
    wrap="none",
    undo=True
)

text_input.pack(side="left", fill="both", expand=True)

text_input_scroll.config(
    command=lambda *args: (
        text_input.yview(*args),
        line_numbers.yview(*args)
    )
)

text_input.bind(
    "<KeyRelease>",
    lambda e: (
        update_line_numbers(),
        highlight_syntax()
    )
)

# ------------------------------
# OUTPUT NOTEBOOK
# ------------------------------
output_frame = tk.LabelFrame(
    main_frame,
    text=" 📊 Compilation Output ",
    font=("Segoe UI", 11, "bold"),
    bg="#1e293b",
    fg="#e2e8f0",
    relief=tk.FLAT,
    borderwidth=2,
    padx=5,
    pady=5
)

output_frame.grid(
    row=0,
    column=1,
    sticky="nsew",
    padx=5,
    pady=5
)

notebook = ttk.Notebook(output_frame)
notebook.pack(fill="both", expand=True, padx=2, pady=2)

# Better tab styling
style = ttk.Style()

style.configure(
    "TNotebook.Tab",
    padding=[6, 3],
    font=("Segoe UI", 8, "bold")
)

tabs = {}

# ------------------------------
# Compiler Phase Tabs
# ------------------------------
tab_order = [
    ("Tokens", "Lexical"),
    ("Syntax", "Syntax"),
    ("ParseTree", "Parse Tree"),
    ("Semantic", "Semantic"),
    ("Intermediate", "Intermediate"),
    ("Optimized", "Optimization"),
    ("Target", "Target Code"),
    ("Execution", "Execution"),
    ("Flow", "Compiler Flow")
]

for key, title in tab_order:

    frame = tk.Frame(notebook, bg="#0a0f1e")

    tab_scroll = tk.Scrollbar(frame)
    tab_scroll.pack(side="right", fill="y")

    text = tk.Text(
        frame,
        font=("Consolas", 10),
        bg="#0a0f1e",
        fg="#22c55e",
        padx=10,
        pady=10,
        yscrollcommand=tab_scroll.set,
        wrap="word"
    )

    text.pack(fill="both", expand=True)

    tab_scroll.config(command=text.yview)

    notebook.add(frame, text=title)

    tabs[key] = text

# ------------------------------
# SYMBOL TABLE TAB
# ------------------------------
symbol_frame = tk.Frame(notebook, bg="#0a0f1e")

symbol_tree = ttk.Treeview(
    symbol_frame,
    columns=("Variable", "Type"),
    show="headings"
)

symbol_tree.heading("Variable", text="Variable Name")
symbol_tree.heading("Type", text="Data Type")

symbol_tree.column(
    "Variable",
    width=150,
    anchor="center"
)

symbol_tree.column(
    "Type",
    width=120,
    anchor="center"
)

symbol_tree.pack(fill="both", expand=True)

notebook.add(symbol_frame, text="Symbol Table")

# ------------------------------
# LITERAL TABLE TAB
# ------------------------------
literal_frame = tk.Frame(notebook, bg="#0a0f1e")

literal_tree = ttk.Treeview(
    literal_frame,
    columns=("Index", "Value", "Type"),
    show="headings"
)

literal_tree.heading("Index", text="Index")
literal_tree.heading("Value", text="Literal Value")
literal_tree.heading("Type", text="Literal Type")

literal_tree.column(
    "Index",
    width=80,
    anchor="center"
)

literal_tree.column(
    "Value",
    width=120,
    anchor="center"
)

literal_tree.column(
    "Type",
    width=120,
    anchor="center"
)

literal_tree.pack(fill="both", expand=True)

notebook.add(literal_frame, text="Literal Table")

update_line_numbers()
highlight_syntax()

root.mainloop()