# CFG & PDA Visualizer

## Working:

```bash
pip install -r requirements.txt
python main.py
```

### Tabs
| Tab | Function |
|-----|----------|
| CFG Mode | Enter/load CFG rules, run or step derivation |
| PDA Mode | Enter/load PDA JSON, run or step simulation |

### Buttons
| Button | Action |
|--------|--------|
| Load | Opens file dialog, pastes into text box |
| Run | Full simulation → shows diagram on canvas |
| Step | Shows derivation steps / trace as text on canvas |
| Reset | Clears inputs and canvas |

### Visualization Panel
- Scrollable (horizontal + vertical scrollbars)
- Draggable — click and drag to pan
- Full image resolution preserved (no thumbnail downscale)

### Save Function
After a successful Run:
1. Diagram is always rendered to a temp path first
2. Popup asks **"Do you want to save this image?"**
3. If yes → file dialog to pick save location
4. If no → image still displays in canvas, temp file deleted
5. Preserves metadata

CFG temp path: `saved_results/cfg_tree_tmp.png`  
PDA temp path: `saved_results/pda_diagram.png`

## CFG Input format:
#### General Format:  
NON_TERMINAL -> production1 | production2 | production3  

**Example:**  
S -> a S b | ε  
can be without spaces:  
S -> ab  
#### Rules
- One rule per line
- `->` separates LHS from RHS
- `|` separates alternatives
- Use `ε` for empty production
- Symbols separated by spaces are treated as separate tokens; unseparated chars are split individually (e.g. `ab` → `['a','b']`)
- Genrally:
  - Uppercase symbols are usually treated as non-terminals.
  - Lowercase symbols are usually terminals.
- Recursive grammars may become computationally expensive.

## PDA Input Format (Plaintext)
#### Required Sections:
- states:
- input_symbols:
- stack_symbols:
- start_state:
- accept_states:
- start_stack:
- Transition Format: current_state, input_symbol, stack_top -> next_state, push_string  
#### Rules
- Separate values using commas.
- Use ε for epsilon transitions.
- Push strings are pushed character-by-character.
- Avoid adding extra commas in transitions.
- Every transition right-hand side must contain exactly:
  - next state
  - push string
- Push strings are reversed internally before pushing onto the stack.
- Acceptance occurs when:
  - input is consumed
  - PDA reaches an accept state
    
**Example:**  
  
states: q0, q1, q2  
input_symbols: a, b  
stack_symbols: A, Z  
start_state: q0  
accept_states: q2  
start_stack: Z  
q0, a, Z -> q0, AZ  
q0, b, A -> q1, ε  
q1, ε, Z -> q2, Z  

## PDA Input Format (JSON)
The simulator also supports PDA definitions in JSON.  
  
#### General Structure:  

```json
{
  "states": [],
  "input_symbols": [],
  "stack_symbols": [],
  "start_state": "",
  "accept_states": [],
  "start_stack": "",
  "transitions": {}
}
```
#### Transition Structure:
Transitions follow this structure:  

```json
"current_state": {
  "input_symbol": {
    "stack_top": [["next_state", "push_string"]]
  }
}
```
**Example:**
```json
{
  "states": ["q0", "q1", "q2"],
  "input_symbols": ["a", "b"],
  "stack_symbols": ["A", "Z"],
  "start_state": "q0",
  "accept_states": ["q2"],
  "start_stack": "Z",
  "transitions": {
    "q0": {
      "a": {
        "Z": ["q1", "AZ"]
      },
      "ε": {
        "Z": ["q2", "Z"]
      }
    }
  }
}
```
**Transition value formats:**
- Single: `["next_state", "push_string"]`
- Multiple: `[["q1", "AZ"], ["q2", "Z"]]`
- Empty push (pop only): `["q1", "ε"]`
- Epsilon input: key `"ε"`, `"epsilon"`, `"eps"`, or `""`

---

## Working:
Three cooperating modules:

| File | Role |
|------|------|
| `cfg_parser.py` | Parses CFG rules, derives strings, returns steps |
| `visualizer.py` | Draws derivation trees and PDA diagrams via Graphviz |
| `main.py` | Tkinter GUI, runs the project (ofc) |

---

## cfg_parser.py

### `parse_cfg(cfg_text: str) -> dict`
Parses plaintext CFG rules into a dictionary.
**Returns:** `{ 'S': [['a','S','b'], []], ... }`

---

### `CFG(cfg_text)`
Wrapper class.

```python
cfg = CFG("S -> a S b | ε")
result = cfg.derive("aabb")
```

**`derive(target_string)` returns:**
```python
{
  "accepted": True/False,
  "derivation": ["S", "a S b", "a a S b b", "a a b b"],  # sentential forms
  "tree": [...]   # same as derivation, used for tree rendering
}
```

---

### `derive_string` — How it works
Recursive leftmost derivation with pruning:

- Expands leftmost non-terminal first
- **Prunes if:** terminal count exceeds target length
- **Prunes if:** terminal prefix doesn't match target prefix
- **Prunes if:** depth exceeds `2 * len(target)` (loop guard)

---

## visualizer.py

### `draw_cfg_tree(steps, output_file='cfg_tree') -> str`
Builds a parse tree PNG from derivation steps.

**Input:** list of sentential form strings, e.g.:
```python
["S", "a S b", "a a S b b", "a a b b"]
```

**Output:** saves `<output_file>.png`, returns path.

**Note:** Assumes **leftmost derivation** — tree building logic only handles one expansion per step. Complex/ambiguous grammars may render incorrectly.

---

### `draw_pda_states(pda, output_file='pda_diagram') -> str`
Renders PDA state diagram.

**Input:** parsed PDA dict (from `pda_simulator.parse_pda`)

**Output:** saves `<output_file>.png`, returns path.

- Accept states → double circle
- Start state → arrow from invisible node
- Edge labels: `(input, stack_top → push)`

---

## main.py (GUI)
- Uses tkinter and canvases
- runs the entire program
---

## Dependencies

- pillow
- Graphviz

binaries must also be installed on the system and available in PATH.
