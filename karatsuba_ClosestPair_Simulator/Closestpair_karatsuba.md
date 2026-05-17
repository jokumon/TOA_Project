# Closest Pair & Karatsuba Multiplication visualizer

A step-by-step animated visualizer for two classic divide-and-conquer algorithms

---

## Setup & Run

```bash
pip install -r requirements.txt
python main.py
```

Make sure `test_cases/` and `karatsuba_answers/` folders exist, or just hit **Generate input files** in the app, it creates them automatically.

---

## Project Structure

```
.
├── main.py
├── requirements.txt
├── test_cases/              # Auto-created, holds input .txt files
└── karatsuba_answers/       # Auto-created, holds answer output files
```

---

## Input File Formats

### Closest Pair: `closest_input_N.txt`

- Line 1: integer N (number of points)
- Lines 2 to N+1: `x y` coordinates (integers or floats, space-separated)

```
5
10 20
300 150
45 90
200 400
80 60
```

### Karatsuba: `karatsuba_input_N.txt`

- Line 1: big integer A
- Line 2: big integer B
- No commas, no spaces, digits only

```
38472918374619283746
92837461928374619283
```
---
## Buttons

Both tabs share the same button layout:

| Button | Action |
|--------|--------|
| **Generate input files** | Creates 10 random input files in `test_cases/`. Asks for confirmation before overwriting. |
| **Run (choose 1-10)** | Prompts for a number 1-10, loads that generated file, runs algorithm, starts animation at step 1. If files aren't generated yet, prompts you to generate or pick manually. |
| **Select file manually** | Opens file dialog. Shows expected format reminder first. Runs algorithm on chosen file. |
| **Next step** | Advances animation by one step. |
| **Play / Pause** | Auto-plays through all steps at current speed. Click again to pause. |
| **Speed (Closest Pair)** | Cycles through 4 speeds: Turtle Paced → Leisurely Innit? → Zooomy → Vrroooom (600ms → 200ms → 50ms → 1ms per step) |
| **Speed (Karatsuba)** | Cycles through 4 speeds: Grandpa → Normal innit? → F1 Max Verstappen → Blitz (600ms → 200ms → 50ms → 1ms per step) |
| **Reset animation** | Resets to step 1 (keeps loaded data). |

---

## How It Works

### Closest Pair (Divide & Conquer)
1. Sorts points by X and Y
2. Recursively splits into left/right halves
3. Finds closest pair in each half
4. Checks the strip region around the dividing line
5. Returns the global minimum distance pair

**Recorded step types for animation:**

| Step | What it shows |
|------|--------------|
| `start` | All points plotted |
| `divide` | Vertical dividing line drawn |
| `base_case` | ≤3 points, brute-forced |
| `combine_sides` | Best pair from left+right halves |
| `strip` | Points within δ of dividing line highlighted |
| `strip_check` | Each strip pair comparison drawn |
| `result_level` | Best pair at this recursion level |
| `final` | Global best pair highlighted |

---

### Karatsuba Multiplication
Recursively multiplies two large integers using the formula:
```
xy = z2·10^2m + (z1-z2-z0)·10^m + z0
where z0=xl·yl, z2=xh·yh, z1=(xl+xh)·(yl+yh)
```
Base case: either number < 10.

Visualizes the **recursion tree**, each node shows the two numbers being multiplied and depth. The current active node is highlighted larger.

---

## Output

### Closest Pair
Result panel shows:
- Source (generated or manual)
- Filename
- Number of points
- Minimum distance
- Closest pair coordinates
- Execution time (ms)

### Karatsuba
Result panel shows:
- Source and filename
- Digit counts of A and B
- A, B, and Product in scientific notation
- Execution time (ms)
- Answer saved to `karatsuba_answers/<filename>_ans.txt`
