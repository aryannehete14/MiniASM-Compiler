# MiniASM Compiler

A simple Assembly Language Compiler and Interpreter built using Python. This project provides a graphical interface for writing, compiling, and executing MiniASM programs while demonstrating core compiler design concepts such as lexical analysis, parsing, symbol handling, and instruction execution.

---

## Features

* User-friendly GUI built with Python
* Assembly code editor
* Compile MiniASM instructions
* Execute assembly programs
* Error detection and reporting
* Instruction parsing and validation
* Educational implementation of compiler concepts
* Lightweight and easy to run

---

## Project Structure

```text
MiniASM-Compiler/
│
├── compiler_gui.py      # Main GUI application
├── lexer.py             # Lexical analyzer
├── parser.py            # Syntax parser
├── interpreter.py       # Instruction execution engine
├── utils.py             # Helper functions
├── examples/            # Sample MiniASM programs
└── README.md
```

> Note: File names may vary depending on your implementation.

---

## Technologies Used

* Python 3.x
* Tkinter (GUI)
* Compiler Design Concepts
* Assembly Language Simulation

---

## Installation

### Clone the Repository

```bash
git clone https://github.com/aryannehete14/MiniASM-Compiler.git
cd MiniASM-Compiler
```

### Install Dependencies

If any dependencies are required:

```bash
pip install -r requirements.txt
```

---

## Running the Project

Launch the compiler GUI:

```bash
python compiler_gui.py
```

---

## Sample MiniASM Program

```asm
MOV A, 10
MOV B, 20
ADD A, B
PRINT A
HLT
```

### Expected Output

```text
30
```

---

## Compiler Workflow

1. User writes MiniASM code.
2. Lexer tokenizes the input.
3. Parser validates syntax.
4. Instructions are translated into internal representations.
5. Interpreter executes instructions.
6. Output is displayed in the GUI.

---

## Learning Objectives

This project helps in understanding:

* Lexical Analysis
* Syntax Analysis
* Parsing
* Instruction Processing
* Assembly Language Concepts
* Compiler Design Fundamentals
* GUI Application Development in Python

---

## Future Enhancements

* Symbol Table Visualization
* Intermediate Code Generation
* Optimization Module
* Debugging Support
* Memory Register Visualization
* Machine Code Generation
* Enhanced Error Reporting

---

## Screenshots

Add screenshots of your GUI here.

Example:

```markdown
![Compiler GUI](screenshots/gui.png)
```

---

## Author

Aryan Nehete

GitHub: https://github.com/aryannehete14

---

## License

This project is developed for educational and learning purposes.
