# ParseCraft – Compiler Grammar Analysis & LL(1) Parsing Studio

**ParseCraft** is a web-based compiler grammar analysis and predictive parsing studio built using Python and Flask. It provides an interactive environment for analyzing Context-Free Grammars (CFGs), transforming grammars into a suitable form for predictive parsing, calculating FIRST and FOLLOW sets, generating LL(1) parsing tables, and simulating input-string parsing step by step.

The platform combines core compiler design algorithms with an interactive IDE-inspired interface to make grammar analysis easier to understand, execute, and visualize.

**Live Demo:** https://parsecraft.vercel.app

**GitHub Repository:** https://github.com/Aditya-Vardh/ParseCraft

---

## Features

### 1. Grammar Input & Analysis
- Enter Context-Free Grammar productions directly into the grammar editor.
- Support for multiple production alternatives using `|`.
- Support for epsilon (ε) productions.
- Includes predefined sample grammars for quick testing.

### 2. Grammar Transformation
- Immediate left-recursion elimination.
- Left factoring using common-prefix detection.
- Displays the transformed grammar for inspection.

### 3. FIRST & FOLLOW Computation
- Calculates FIRST sets for all non-terminals.
- Calculates FOLLOW sets for all non-terminals.
- Handles epsilon productions and nullable symbols.
- Uses the `$` end-of-input marker for the start symbol.

### 4. LL(1) Parsing Table Generation
- Automatically constructs the predictive parsing table.
- Identifies conflicting table entries.
- Determines whether the transformed grammar satisfies the LL(1) table-conflict condition.
- Displays parsing-table entries in an organized format.

### 5. Predictive Parsing Simulation
- Tests input strings against the transformed grammar.
- Performs stack-based LL(1) predictive parsing.
- Displays parsing steps, stack contents, remaining input, and parser actions.
- Reports accepted and rejected input strings with parsing errors.

### 6. Parse Tree Visualization
- Generates a parse tree for the tested input.
- Displays the hierarchical structure of grammar derivations.

### 7. Interactive Compiler IDE
- Professional IDE-inspired interface.
- Sample grammar selection.
- Dark/light theme toggle.
- Compiler statistics and grammar insights.
- Downloadable PDF analysis report.
- Responsive interface with interactive controls.

---

## Technology Stack

| Component | Technology |
|---|---|
| Programming Language | Python |
| Backend Framework | Flask |
| Frontend | HTML5 |
| Styling | CSS3 |
| Client-side Interactions | JavaScript |
| Templating Engine | Jinja2 |
| Parsing Algorithm | LL(1) Predictive Parsing |
| Deployment | Vercel and Render |
| Version Control | Git and GitHub |

---

## System Architecture

ParseCraft follows a modular architecture that separates the user interface, Flask application, and compiler algorithms.

```text
                 USER
                   |
                   v
          HTML / CSS / JavaScript
                   |
                   v
              Flask App
                app.py
                   |
                   v
          Compiler Processing
                   |
        +----------+----------+
        |          |          |
        v          v          v
     Grammar    FIRST &    LL(1)
   Processing   FOLLOW     Parser
        |          |          |
        v          v          v
  Left Recursion  Set       Parsing
  Elimination   Computation  Table
        |
        v
   Left Factoring
        |
        v
    Analysis Results
        |
        v
  Dashboard / Parse Tree /
  Parsing Simulation / PDF
```

### Project Structure

```text
ParseCraft/
│
├── compiler/
│   ├── __init__.py
│   ├── grammar.py
│   ├── first_follow.py
│   └── ll1.py
│
├── public/
│   ├── style.css
│   └── script.js
│
├── static/
│   ├── style.css
│   └── script.js
│
├── templates/
│   └── index.html
│
├── app.py
├── requirements.txt
└── README.md
```

### Module Description

| File | Responsibility |
|---|---|
| `app.py` | Flask application, routing, and integration of compiler modules |
| `compiler/grammar.py` | Grammar parsing, symbol tokenization, left-recursion elimination, and left factoring |
| `compiler/first_follow.py` | FIRST and FOLLOW set computation |
| `compiler/ll1.py` | LL(1) parsing-table construction, conflict detection, predictive parsing, and parse-tree generation |
| `templates/index.html` | Main application interface and dynamic result rendering |
| `static/style.css` | Original frontend styling |
| `static/script.js` | Frontend interactions, theme controls, and PDF report functionality |
| `public/` | Static asset directory used by the Vercel deployment |
| `requirements.txt` | Python dependencies |

---

## Installation & Local Setup

### Prerequisites

- Python 3.10 or later
- Git
- pip (Python package manager)

### Step 1: Clone the Repository

```bash
git clone https://github.com/Aditya-Vardh/ParseCraft.git
```

### Step 2: Navigate to the Project

```bash
cd ParseCraft
```

### Step 3: Create a Virtual Environment

**Windows:**

```bash
python -m venv .venv
```

Activate it:

```bash
.venv\Scripts\activate
```

**Linux / macOS:**

```bash
python3 -m venv .venv
source .venv/bin/activate
```

### Step 4: Install Dependencies

```bash
pip install -r requirements.txt
```

### Step 5: Run the Application

```bash
python app.py
```

### Step 6: Open in Browser

Visit:

```text
http://127.0.0.1:5000
```

The ParseCraft workspace will be available locally.

---

## How to Use ParseCraft

1. Open the ParseCraft application.
2. Enter a Context-Free Grammar in the grammar editor or select a predefined sample.
3. Enter the input string to be tested.
4. Click **Analyze Grammar**.
5. Inspect the original grammar and transformed grammar.
6. Review the FIRST and FOLLOW sets.
7. Examine the generated LL(1) parsing table and any conflicts.
8. Follow the predictive parsing simulation.
9. Inspect the generated parse tree.
10. Download the analysis report if required.

### Example Grammar

```text
E->TE'
E'->+TE'|epsilon
T->FT'
T'->*FT'|epsilon
F->(E)|id
```

### Example Input String

```text
id+id*id
```

This example demonstrates an arithmetic-expression grammar with operator precedence represented through the grammar structure.

---

## Core Compiler Design Concepts

ParseCraft implements the following compiler design concepts:

- Context-Free Grammars (CFG)
- Terminals and Non-terminals
- Epsilon Productions
- Immediate Left Recursion Elimination
- Left Factoring
- FIRST Set Computation
- FOLLOW Set Computation
- LL(1) Predictive Parsing
- Parsing Table Construction
- Parsing Conflict Detection
- Stack-Based Parsing Simulation
- Parse Tree Generation

**Note:** The current grammar transformation implementation handles immediate left recursion, not general indirect left recursion. LL(1) suitability is assessed through parsing-table conflicts after transformation.

---

## Deployment

ParseCraft is configured for deployment on two platforms.

### Vercel
- Connected directly to the GitHub repository.
- Uses the Flask application preset.
- Serves static frontend assets through the `public/` directory.
- Supports automatic deployments when changes are pushed to the `main` branch.

### Render
- Deployed as a Python web service.
- Installs dependencies using `requirements.txt`.
- Runs the Flask application using Gunicorn.

**Build Command:**

```bash
pip install -r requirements.txt
```

**Start Command:**

```bash
gunicorn app:app
```

---

## Future Enhancements

Potential improvements include:

- Indirect left-recursion elimination.
- More comprehensive grammar validation.
- Enhanced syntax-error recovery.
- Interactive step-by-step parse-tree construction.
- Additional parsing algorithms such as LR(0), SLR(1), and CLR(1).
- Grammar import and export functionality.
- Expanded compiler analysis and visualization tools.

---

## Project Information

**Project Name:** ParseCraft – Compiler Grammar Analysis & LL(1) Parsing Studio

**Project Domain:** Compiler Design

**Project Type:** Web-Based Compiler Analysis Tool

**Team:** PLUTONIUM

**Repository:** https://github.com/Aditya-Vardh/ParseCraft

**Live Application:** https://parsecraft.vercel.app

---

*ParseCraft – Transforming Grammar Theory into an Interactive Compiler Experience.*
