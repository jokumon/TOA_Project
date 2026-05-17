import tkinter as tk
import random
import os
import time
import math
from tkinter import ttk, messagebox, filedialog, simpledialog
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
from matplotlib.figure import Figure

#---------------------OOP-------------------------------------------------------------------------

def custom_popup_cnclmangen(root):
    popup = tk.Toplevel(root)
    popup.title("Input files Error")
    popup.geometry("380x200")
    popup.resizable(False, False)
    popup.grab_set()
    label = ttk.Label(
        popup, 
        text="\nInput files have not been generated, or a file hasn't been chosen.\nChoose an option:", 
        justify="center",
        wraplength=320,
        font=("TkDefaultFont", 12, "normal")
    )
    label.pack(pady=15)
    result = {"choice": "cancel"}

    def choose(option):
        result["choice"] = option
        popup.destroy()

    btn_frame = ttk.Frame(popup)
    btn_frame.pack(pady=10)

    ttk.Button(btn_frame, text="Generate the files", width=18,
               command=lambda: choose("generate")).grid(row=0, column=0, padx=5)

    ttk.Button(btn_frame, text="Select custom file", width=18,
               command=lambda: choose("manual")).grid(row=0, column=1, padx=5)

    ttk.Button(btn_frame, text="Cancel", width=18,
               command=lambda: choose("cancel")).grid(row=1, column=0, columnspan=2, pady=10)

    root.wait_window(popup)
    return result["choice"]

#---------------------------------------------------------------------------------------------

def distance(p1, p2):
    return math.hypot(p1[0] - p2[0], p1[1] - p2[1])

def scientific_notationizer(n, lennum=4):
    s = str(abs(n))
    if len(s) <= lennum:
        return s
    return f"{s[:lennum]} x10^{len(s) - lennum}"

# ------------------------------------------------------------------------------------------------

def closest_pair_minpoints(points):
    n = len(points)
    if n < 2:
        return float("inf"), None, None
    min_dist = float("inf")
    best_p1 = best_p2 = None
    for i in range(n):
        for j in range(i + 1, n):
            d = distance(points[i], points[j])
            if d < min_dist:
                min_dist = d
                best_p1, best_p2 = points[i], points[j]
    return min_dist, best_p1, best_p2

def logstepsforclosestpair(px, py, steps, depth=0):
    n = len(px)
    if n <= 3:
        d, p1, p2 = closest_pair_minpoints(px)
        steps.append({
            "type": "base_case",
            "depth": depth,
            "points": px[:],
            "pair": (p1, p2),
            "dist": d
        })
        return d, p1, p2

    mid = n // 2
    Qx = px[:mid]
    Rx = px[mid:]
    mid_x = Qx[-1][0]
    steps.append({
        "type": "divide",
        "depth": depth,
        "mid_x": mid_x
    })
    Qx_set = set(Qx)
    Qy, Ry = [], []
    for p in py:
        if p in Qx_set:
            Qy.append(p)
        else:
            Ry.append(p)

    d_left, p1_left, p2_left = logstepsforclosestpair(Qx, Qy, steps, depth + 1)
    d_right, p1_right, p2_right = logstepsforclosestpair(Rx, Ry, steps, depth + 1)

    if d_left < d_right:
        d_min = d_left
        best_pair = (p1_left, p2_left)
    else:
        d_min = d_right
        best_pair = (p1_right, p2_right)

    steps.append({
        "type": "combine_sides",
        "depth": depth,
        "d_min": d_min,
        "pair": best_pair
    })
    strip = [p for p in py if abs(p[0] - mid_x) < d_min]

    steps.append({
        "type": "strip",
        "depth": depth,
        "mid_x": mid_x,
        "strip": strip[:],
        "d_min_before": d_min
    })

    strip_len = len(strip)
    for i in range(strip_len):
        for j in range(i + 1, min(i + 8, strip_len)):
            p, q = strip[i], strip[j]
            d = distance(p, q)
            steps.append({
                "type": "strip_check",
                "depth": depth,
                "p": p,
                "q": q,
                "d": d
            })
            if d < d_min:
                d_min = d
                best_pair = (p, q)

    steps.append({
        "type": "result_level",
        "depth": depth,
        "pair": best_pair,
        "dist": d_min
    })

    return d_min, best_pair[0], best_pair[1]

def closest_pair_with_steps(points):
    if len(points) < 2:
        return float("inf"), None, None, []

    px = sorted(points, key=lambda p: p[0])
    py = sorted(points, key=lambda p: p[1])

    steps = []
    steps.append({
        "type": "start",
        "points": px[:]
    })

    d_min, p1, p2 = logstepsforclosestpair(px, py, steps, depth=0)

    steps.append({
        "type": "final",
        "pair": (p1, p2),
        "dist": d_min
    })

    return d_min, p1, p2, steps

# --------------------------------------------------------------------------------------------------

def karatrecursion(x, y, steps, depth=0, parent_id=None):
    step = {
        "type": "call",
        "depth": depth,
        "x": x,
        "y": y,
        "parent": parent_id,
    }
    steps.append(step)
    my_id = len(steps) - 1

    if x < 10 or y < 10:
        prod = x * y
        step["base"] = True
        step["result"] = prod
        return prod

    sx, sy = str(x), str(y)
    n = max(len(sx), len(sy))
    step["n"] = n
    m = n // 2
    power10_m = 10 ** m
    x_high = x // power10_m
    x_low = x % power10_m
    y_high = y // power10_m
    y_low = y % power10_m

    z0 = karatrecursion(x_low, y_low, steps, depth + 1, my_id)
    z2 = karatrecursion(x_high, y_high, steps, depth + 1, my_id)
    z1 = karatrecursion(x_low + x_high, y_low + y_high, steps, depth + 1, my_id)

    prod = (z2 * (10 ** (2 * m))) + ((z1 - z2 - z0) * (10 ** m)) + z0
    step["result"] = prod
    return prod

def startkaratsuba(x, y):
    steps = []
    result = karatrecursion(x, y, steps, depth=0, parent_id=None)
    return result, steps

# --------------------------------------------------------------------------------------------------

def check_if_generated67(
    base_name="closest_input_",
    expected_count=10):

    for idx in range(1, expected_count + 1):
        filename = os.path.join("test_cases", f"{base_name}{idx}.txt")
        if not os.path.exists(filename):
            return False   

        try:
            with open(filename, "r") as f:
                first = f.readline()
                if not first:
                    return False
                try:
                    n = int(first.strip())
                except ValueError:
                    return False

                points = []
                for line in f:
                    line = line.strip()
                    if not line:
                        continue
                    parts = line.split()
                    if len(parts) != 2:
                        return False
                    float(parts[0])   
                    float(parts[1])   
                    points.append((parts[0], parts[1]))

                if len(points) != n:
                    return False
        except Exception:
            return False
    return True

def read_coordinates_file(path):
    with open(path, "r") as f:
        first = f.readline()
        if not first:
            raise ValueError("File is empty.")
        try:
            n = int(first.strip())
        except ValueError:
            raise ValueError("First line must be an integer number of points.")

        points = []
        for line in f:
            line = line.strip()
            if not line:
                continue
            parts = line.split()
            if len(parts) != 2:
                raise ValueError("Each point line must have exactly two numbers: x y.")
            try:
                x = float(parts[0])
                y = float(parts[1])
            except ValueError:
                raise ValueError("Point coordinates must be numbers.")
            points.append((x, y))

    if len(points) != n:
        raise ValueError(f"Expected {n} points but found {len(points)}.")
    return points

def generate_closest_input_files(
    num_files=10,
    base_name="closest_input_",
    min_n=100,
    max_n=150,
    coord_min=0,
    coord_max=500):
    for idx in range(1, num_files + 1):
        n = random.randint(min_n, max_n)
        filename = os.path.join("test_cases", f"{base_name}{idx}.txt")
        with open(filename, "w") as f:
            f.write(str(n) + "\n")
            for _ in range(n):
                x = random.randint(coord_min, coord_max)
                y = random.randint(coord_min, coord_max)
                f.write(f"{x} {y}\n")

def generate_karatsuba_input_files(
    num_files=10,
    base_name="karatsuba_input_",
    min_digits=100,
    max_digits=110):

    def random_big_int(num_digits):
        first = str(random.randint(1, 9))
        rest = "".join(str(random.randint(0, 9)) for _ in range(num_digits - 1))
        return first + rest

    for idx in range(1, num_files + 1):
        d1 = random.randint(min_digits, max_digits)
        d2 = random.randint(min_digits, max_digits)
        a = random_big_int(d1)
        b = random_big_int(d2)

        filename = os.path.join("test_cases", f"{base_name}{idx}.txt")
        with open(filename, "w") as f:
            f.write(a + "\n")
            f.write(b + "\n")

def read_integers_from_file(path):
    with open(path, "r") as f:
        lines = [line.strip() for line in f if line.strip()]

    if len(lines) < 2:
        raise ValueError("File must contain at least two non-empty lines with integers.")

    try:
        a = int(lines[0])
        b = int(lines[1])
    except ValueError:
        raise ValueError("Lines must contain valid integers only.")

    return a, b

def check_k_generated(
    base_name="karatsuba_input_",expected_count=10):
    for idx in range(1, expected_count + 1):
        filename = os.path.join("test_cases", f"{base_name}{idx}.txt")
        if not os.path.exists(filename):
            return False
        try:
            read_integers_from_file(filename)
        except Exception:
            return False
    return True

# --------------------------------------LOL-------------------------------------------------------------------------------------

class ClosestPairGUI:
    def __init__(self, parent, root2):
        self.root = root2
        self.root.title("DAA Project - 23k0790,23k0712,23k0628")
        self.root.geometry("1200x750")
        self.root.minsize(900, 600)

        self.inputs_generated = check_if_generated67()

        self.points = []
        self.steps = []
        self.current_step_index = -1
        self.playing = False

        self.speed_levels = [600, 200, 50, 1]
        self.speed_labels = ["Speed: Turtle Paced", "Speed: Leisurely Innit?", "Speed: Zooomy", "Speed: Vrroooom"]
        self.speed_index = 1 
        self.speed_ms = self.speed_levels[self.speed_index]


        main_frame = ttk.Frame(parent, padding=10)
        main_frame.pack(fill=tk.BOTH, expand=True)
        left_frame = ttk.Frame(main_frame, width=300)
        left_frame.pack(side=tk.LEFT, fill=tk.Y)
        left_frame.pack_propagate(False)
        # left_frame.grid_rowconfigure(0, weight=1)
        # left_frame.grid_rowconfigure(2, weight=1)
        # left_frame.grid_columnconfigure(0, weight=1)    
        # top_spacer = ttk.Frame(left_frame)
        # top_spacer.pack(side="top", expand=True, fill="both")
        # center_wrapper = ttk.Frame(left_frame)
        # center_wrapper.pack(side="top", anchor="center")
        # center_wrapper.pack(expand=True, fill=tk.BOTH, padx=10, pady=20)
        stuff_box1 = ttk.Frame(left_frame)
        # stuff_box1 = ttk.Frame()
        # stuff_box1.pack(expand=True) 
        stuff_box1.pack(expand=True, fill=tk.BOTH, padx=10, pady=20)
        # stuff_box1.pack()
        # bottom_spacer = ttk.Frame(left_frame)
        # bottom_spacer.pack(side="top", expand=True, fill="both")
        right_frame = ttk.Frame(main_frame)
        right_frame.pack(side=tk.RIGHT, fill=tk.BOTH, expand=True)
        right_frame.pack_propagate(True)


        self.btn_generate = ttk.Button(stuff_box1, text="Generate input files", command=self.on_generate)
        self.btn_generate.pack(fill=tk.X, pady=5)

        self.btn_run = ttk.Button(stuff_box1, text="Run (choose 1-10)", command=self.on_run)
        self.btn_run.pack(fill=tk.X, pady=5)

        self.btn_select = ttk.Button(stuff_box1, text="Select file manually", command=self.on_select_file)
        self.btn_select.pack(fill=tk.X, pady=5)

        self.btn_next = ttk.Button(stuff_box1, text="Next step", command=self.on_next_step)
        self.btn_next.pack(fill=tk.X, pady=(15, 5))

        self.btn_play = ttk.Button(stuff_box1, text="Play", command=self.on_play)
        self.btn_play.pack(fill=tk.X, pady=5)

        self.btn_speed = ttk.Button(stuff_box1, text=self.speed_labels[self.speed_index], command=self.on_change_speed)
        self.btn_speed.pack(fill=tk.X, pady=5)

        self.btn_reset_anim = ttk.Button(stuff_box1, text="Reset animation", command=self.on_reset_animation)
        self.btn_reset_anim.pack(fill=tk.X, pady=5)

        textforstatuslabel = ("Input files: generated" if self.inputs_generated else "Input files: not generated yet")

        self.status_label = ttk.Label(
            stuff_box1,
            text=textforstatuslabel,
            wraplength=220,
            justify="center",
            font=("TkDefaultFont", 10, "bold")
        )
        self.status_label.pack(pady=(15, 5), anchor="center")

        ttk.Label(stuff_box1, text="Final answer:", justify="center").pack(anchor="center")
        self.result_label = ttk.Label(
            stuff_box1,
            text="-",
            justify=tk.CENTER,
            wraplength=220,
            font=("TkDefaultFont", 10, "bold")
        )
        self.result_label.pack(pady=(5, 5), anchor="center")

        self.step_info_label = ttk.Label(
            stuff_box1,
            text="Step: -/ -\nDescription: -",
            justify=tk.CENTER,
            wraplength=220,
            font=("TkDefaultFont", 10, "bold")
        )
        self.step_info_label.pack(pady=(15, 5), anchor="center")


        self.fig = Figure(figsize=(6, 5))
        self.ax = self.fig.add_subplot(111)
        self.ax.set_title("Closest Pair - Animation")
        self.ax.set_xlabel("X")
        self.ax.set_ylabel("Y")
        self.ax.set_aspect("equal", "box")
        self.canvas = FigureCanvasTkAgg(self.fig, master=right_frame)
        canvas_widget = self.canvas.get_tk_widget()
        # canvas_widget.config(width=850, height=700)
        canvas_widget.pack(fill=tk.BOTH, expand=True)
        self.ax.set_xlim(0, 500)
        self.ax.set_ylim(0, 500)
        self.fig.tight_layout()
        self.canvas.draw()

    def set_result(self, text):
        self.result_label.configure(text=text)

    def reset_view(self):
        self.steps = []
        self.current_step_index = -1
        self.points = []
        self.playing = False
        self.ax.clear()
        self.ax.set_title("Closest Pair an Animation")
        self.ax.set_xlabel("X")
        self.ax.set_ylabel("Y")
        self.ax.set_aspect("equal", "box")
        self.ax.set_xlim(0, 500)
        self.ax.set_ylim(0, 500)
        self.fig.tight_layout()
        self.canvas.draw()
        self.step_info_label.configure(text="Step: -/ -\nDescription: -")

    def draw_current_step(self):
        if not self.steps or self.current_step_index < 0:
            return

        step = self.steps[self.current_step_index]

        self.ax.clear()

        if self.points:
            xs = [p[0] for p in self.points]
            ys = [p[1] for p in self.points]
            self.ax.scatter(xs, ys, s=35)

        division_lines = [
            st["mid_x"] for st in self.steps[:self.current_step_index + 1]
            if st["type"] == "divide"
        ]
        for mid_x in division_lines:
            self.ax.axvline(mid_x, linestyle="--")

        desc = f"Type: {step['type']}"

        if step["type"] == "start":
            desc = "Starting with all points."

        elif step["type"] == "divide":
            mid_x = step["mid_x"]
            self.ax.axvline(mid_x, linestyle="--")
            desc = f"Divide at x = {round(mid_x)}"

        elif step["type"] == "base_case":
            pts = step["points"]
            px = [p[0] for p in pts]
            py = [p[1] for p in pts]
            self.ax.scatter(px, py, s=45)

            p1, p2 = step["pair"]
            if p1 is not None and p2 is not None:
                self.ax.scatter([p1[0], p2[0]], [p1[1], p2[1]], s=80)
                self.ax.plot([p1[0], p2[0]], [p1[1], p2[1]])
                desc = f"Base case best pair {p1} - {p2}, dist={round(step['dist'])}"

        elif step["type"] == "combine_sides":
            p1, p2 = step["pair"]
            if p1 is not None and p2 is not None:
                self.ax.scatter([p1[0], p2[0]], [p1[1], p2[1]], s=80)
                self.ax.plot([p1[0], p2[0]], [p1[1], p2[1]])
                desc = f"Best from halves: {p1} - {p2}, dist={round(step['d_min'])}"

        elif step["type"] == "strip":
            strip = step["strip"]
            sx = [p[0] for p in strip]
            sy = [p[1] for p in strip]
            self.ax.scatter(sx, sy, s=50)
            desc = f"Strip around mid, {len(strip)} points."

        elif step["type"] == "strip_check":
            p = step["p"]
            q = step["q"]
            self.ax.scatter([p[0], q[0]], [p[1], q[1]], s=80)
            self.ax.plot([p[0], q[0]], [p[1], q[1]])
            desc = f"Checking strip pair {p} - {q}, dist={round(step['d'])}"

        elif step["type"] == "result_level":
            p1, p2 = step["pair"]
            if p1 is not None and p2 is not None:
                self.ax.scatter([p1[0], p2[0]], [p1[1], p2[1]], s=90)
                self.ax.plot([p1[0], p2[0]], [p1[1], p2[1]])
                desc = f"Level result: {p1} - {p2}, dist={round(step['dist'])}"

        elif step["type"] == "final":
            p1, p2 = step["pair"]
            if p1 is not None and p2 is not None:
                self.ax.scatter([p1[0], p2[0]], [p1[1], p2[1]], s=100)
                self.ax.plot([p1[0], p2[0]], [p1[1], p2[1]])
                desc = f"Final best pair {p1} - {p2}, dist={round(step['dist'])}"

        self.ax.set_aspect("equal", "box")
        self.ax.set_xlim(0, 500)
        self.ax.set_ylim(0, 500)

        self.ax.set_title("Closest Pair - Animation")
        self.ax.set_xlabel("X")
        self.ax.set_ylabel("Y")
        self.fig.tight_layout()
        self.canvas.draw()

        total_steps = len(self.steps)
        self.step_info_label.configure(
            text=f"Step: {self.current_step_index + 1}/{total_steps}\nDescription: {desc}"
        )

# ----------------- Buttons! hehehe! Get it? -----------------------------------------------------------------------------------

    def on_change_speed(self):
        self.speed_index = (self.speed_index + 1) % len(self.speed_levels)
        self.speed_ms = self.speed_levels[self.speed_index]
        self.btn_speed.configure(text=self.speed_labels[self.speed_index])

    def on_generate(self):
        answer = messagebox.askyesno(
            "Generate files",
            "This will create/overwrite closest_input_1.txt to closest_input_10.txt in the test cases folder. Continue?"
        )
        if not answer:
            return
        try:
            generate_closest_input_files()
            self.inputs_generated = True
            self.status_label.configure(
                text="Input files: generated closest_input_1.txt to closest_input_10.txt, yay!"
            )
        except Exception as e:
            messagebox.showerror("Error", f"Could not generate files: {e}")

    def run_on_file(self, path, source_label):
        try:
            points = read_coordinates_file(path)
        except Exception as e:
            messagebox.showerror(
                "Invalid file",
                f"Error reading file:\n{e}\n\nExpected format:\n"
                "First line: integer N\nNext N lines: x y coordinates.(Just values, seperated by space)"
            )
            return

        self.reset_view()
        self.points = points

        start = time.perf_counter()
        min_dist, p1, p2, steps = closest_pair_with_steps(points)
        end = time.perf_counter()
        elapsed_ms = (end - start) * 1000.0

        self.steps = steps
        self.current_step_index = 0
        self.draw_current_step()

        dist_round = round(min_dist)
        time_round = round(elapsed_ms)

        self.set_result(
            f"Source: {source_label}\n"
            f"File: {os.path.basename(path)}\n"
            f"Points: {len(points)}\n"
            f"Min distance: {dist_round}\n"
            f"Closest pair: {p1} and {p2}\n"
            f"Time: {time_round} ms"
        )

    def on_run(self):
        if not self.inputs_generated:
            choice = custom_popup_cnclmangen(self.root)
            if choice == "cancel":
                return
            if choice == "generate":
                self.on_generate()
                if not self.inputs_generated:
                    return
            if choice == "manual":
                self.on_select_file()
                return

        idx = simpledialog.askinteger(
            "Select input",
            "Enter an input file number (1-10):",
            parent=self.root,
            minvalue=1,
            maxvalue=10
        )
        if idx is None:
            return
        filename = os.path.join("test_cases", f"closest_input_{idx}.txt")
        if not os.path.exists(filename):
            messagebox.showerror(
                "File missing",
                f"{filename} does not exist. Please generate inputs or choose another file."
            )
            return

        self.run_on_file(filename, f"auto generated file #{idx}")

    def on_select_file(self):
        messagebox.showinfo(
            "Input format",
            "Please choose a .txt file with this format:\n"
            "First line: integer N (number of points, at least 2)\n"
            "Next N lines: x y coordinates (just numbers separated by a space)."
        )
        path = filedialog.askopenfilename(
            title="Select input file",
            filetypes=[("Text files", "*.txt"), ("All files", "*.*")]
        )
        if not path:
            return

        self.run_on_file(path, "manual selection")

    def on_next_step(self):
        if not self.steps:
            messagebox.showinfo("No animation", "Run an input file first to generate steps.")
            return
        if self.current_step_index + 1 >= len(self.steps):
            messagebox.showinfo("End", "Animation finished. You are at the last step.")
            return
        self.current_step_index += 1
        self.draw_current_step()

    def on_reset_animation(self):
        if not self.steps:
            self.reset_view()
            return
        self.playing = False
        self.btn_play.configure(text="Play")
        self.current_step_index = 0
        self.draw_current_step()

    def on_play(self):
        if not self.steps:
            messagebox.showinfo("No animation", "Broski, generate files or select one")
            return
        if self.playing:
            self.playing = False
            self.btn_play.configure(text="Play")
            return
        self.playing = True
        self.btn_play.configure(text="Pause")
        self.play_next_step()

    def play_next_step(self):
        if not self.playing:
            return
        if not self.steps:
            return
        if self.current_step_index + 1 >= len(self.steps):
            self.playing = False
            self.btn_play.configure(text="Play")
            return
        self.current_step_index += 1
        self.draw_current_step()
        self.root.after(self.speed_ms, self.play_next_step)

# ---------------------I didnt expect ot to be this long -----------------------------------------------------------------------------------

class KaratsubaGUI:
    def __init__(self, parent, root2):
        self.parent = parent
        self.root = root2

        self.inputs_generated = check_k_generated()

        self.steps = []
        self.current_step_index = -1
        self.playing = False

        self.speed_levels = [600, 200, 50, 1]
        self.speed_labels = ["Speed: Grandpa", "Speed: Normal innit?", "Speed: F1, Max Verstappen", "Speed: Blitz"]
        self.speed_index = 1
        self.speed_ms = self.speed_levels[self.speed_index]


        main_frame = ttk.Frame(parent, padding=10)
        main_frame.pack(fill=tk.BOTH, expand=True)

        left_frame = ttk.Frame(main_frame, width=300)
        left_frame.pack(side=tk.LEFT, fill=tk.Y)
        left_frame.pack_propagate(False)

        controls_box = ttk.Frame(left_frame)
        controls_box.pack(expand=True, fill=tk.BOTH, padx=10, pady=20)

        right_frame = ttk.Frame(main_frame)
        right_frame.pack(side=tk.RIGHT, fill=tk.BOTH, expand=True)

        self.btn_generate = ttk.Button(
            controls_box,
            text="Generate Karatsuba files",
            command=self.on_generate
        )
        self.btn_generate.pack(fill=tk.X, pady=5)

        self.btn_run = ttk.Button(
            controls_box,
            text="Run (choose 1-10)",
            command=self.on_run
        )
        self.btn_run.pack(fill=tk.X, pady=5)

        self.btn_select = ttk.Button(
            controls_box,
            text="Select file manually",
            command=self.on_select_file
        )
        self.btn_select.pack(fill=tk.X, pady=5)

        self.btn_next = ttk.Button(
            controls_box,
            text="Next step",
            command=self.on_next_step
        )
        self.btn_next.pack(fill=tk.X, pady=(15, 5))

        self.btn_play = ttk.Button(
            controls_box,
            text="Play",
            command=self.on_play
        )
        self.btn_play.pack(fill=tk.X, pady=5)

        self.btn_speed = ttk.Button(
            controls_box,
            text=self.speed_labels[self.speed_index],
            command=self.on_change_speed
        )
        self.btn_speed.pack(fill=tk.X, pady=5)

        self.btn_reset_anim = ttk.Button(
            controls_box,
            text="Reset animation",
            command=self.on_reset_animation
        )
        self.btn_reset_anim.pack(fill=tk.X, pady=5)

        status_text = (
            "Input files: generated"
            if self.inputs_generated
            else "Input files: not generated yet"
        )

        self.status_label = ttk.Label(
            controls_box,
            text=status_text,
            wraplength=220,
            justify="center",
            font=("TkDefaultFont", 10, "bold")
        )
        self.status_label.pack(pady=(15, 5), anchor="center")

        ttk.Label(
            controls_box,
            text="Final answer:",
            justify="center",
            font=("TkDefaultFont", 10, "bold")
        ).pack(anchor="center")

        self.result_label = ttk.Label(
            controls_box,
            text="-",
            justify=tk.CENTER,
            wraplength=230,
            font=("TkDefaultFont", 10, "bold")
        )
        self.result_label.pack(pady=(5, 5), anchor="center")

        self.step_info_label = ttk.Label(
            controls_box,
            text="Step: -/ -\nDescription: -",
            justify=tk.CENTER,
            wraplength=230,
            font=("TkDefaultFont", 10, "bold")
        )
        self.step_info_label.pack(pady=(15, 5), anchor="center")


        self.fig = Figure(figsize=(6, 5))
        self.ax = self.fig.add_subplot(111)
        self.ax.set_title("Karatsuba recursion tree (it'll try its best)")
        self.ax.set_xlabel("calls")
        self.ax.set_ylabel("depth")
        self.canvas = FigureCanvasTkAgg(self.fig, master=right_frame)
        canvas_widget = self.canvas.get_tk_widget()
        # canvas_widget.config(width=850, height=700)
        canvas_widget.pack(fill=tk.BOTH, expand=True)
        self.fig.tight_layout()
        self.canvas.draw()

    def set_result(self, text):
        self.result_label.configure(text=text)

    def reset_view(self):
        self.steps = []
        self.current_step_index = -1
        self.playing = False
        self.ax.clear()
        self.ax.set_title("Karatsuba recursion tree - it'll try its best")
        self.ax.set_xlabel("call index (auto layout)")
        self.ax.set_ylabel("depth")
        self.fig.tight_layout()
        self.canvas.draw()
        self.step_info_label.configure(text="Step: -/ -\nDescription: -")

    def draw_current_step(self):
        if not self.steps or self.current_step_index < 0:
            return

        self.ax.clear()
        active_steps = [
            (idx, st)
            for idx, st in enumerate(self.steps[: self.current_step_index + 1])
            if st.get("type") == "call"
        ]
        if not active_steps:
            self.canvas.draw()
            return

        depth_nodes = {}
        for idx, st in active_steps:
            d = st["depth"]
            depth_nodes.setdefault(d, []).append(idx)
        positions = {}  
        max_depth = max(depth_nodes.keys())
        for depth, ids in depth_nodes.items():
            k = len(ids)
            for i, node_id in enumerate(ids):
                x = (i + 1) / (k + 1) 
                y = -depth 
                positions[node_id] = (x, y)

        for idx, st in active_steps:
            parent = st.get("parent")
            if parent is not None and parent in positions and idx in positions:
                x1, y1 = positions[parent]
                x2, y2 = positions[idx]
                self.ax.plot([x1, x2], [y1, y2], linewidth=1)

        for idx, st in active_steps:
            x_pos, y_pos = positions[idx]
            is_current = (idx == self.current_step_index)

            size = 80 if is_current else 40
            self.ax.scatter([x_pos], [y_pos], s=size)

            x_val = st["x"]
            y_val = st["y"]
            label_x = scientific_notationizer(x_val, lennum=5)
            label_y = scientific_notationizer(y_val, lennum=5)
            n_digits = st.get("n", max(len(str(x_val)), len(str(y_val))))

            text = f"{label_x}\n{label_y}\n(n={n_digits})"
            self.ax.text(
                x_pos,
                y_pos,
                text,
                ha="center",
                va="center",
                fontsize=7
            )

        self.ax.set_xlim(0, 1)
        self.ax.set_ylim(-max_depth - 1, 1)
        self.ax.set_yticks([-d for d in range(0, max_depth + 1)])
        self.ax.set_yticklabels([str(d) for d in range(0, max_depth + 1)])
        self.ax.set_title("Karatsuba recursion tree - it's trying its best")
        self.ax.set_xlabel("horizontal layout within each depth")
        self.ax.set_ylabel("recursion depth")
        self.fig.tight_layout()
        self.canvas.draw()

        st = self.steps[self.current_step_index]
        label = (
            f"Karatsuba call at depth {st['depth']}\n"
            f"X ~ {scientific_notationizer(st['x'])}\n"
            f"Y ~ {scientific_notationizer(st['y'])}"
        )
        total_steps = len(self.steps)
        self.step_info_label.configure(
            text=f"Step: {self.current_step_index + 1}/{total_steps}\n{label}"
        )

# -------------- Karatsuba whatever buttons---------------------------------------------------------------

    def on_change_speed(self):
        self.speed_index = (self.speed_index + 1) % len(self.speed_levels)
        self.speed_ms = self.speed_levels[self.speed_index]
        self.btn_speed.configure(text=self.speed_labels[self.speed_index])

    def on_generate(self):
        answer = messagebox.askyesno(
            "Generate Karatsuba files",
            "This will create or overwrite karatsuba_input_1.txt to karatsuba_input_10.txt in test_cases folder. Continue?"
        )
        if not answer:
            return
        try:
            generate_karatsuba_input_files()
            self.inputs_generated = True
            self.status_label.configure(
                text="Input files: generated karatsuba_input_1.txt to karatsuba_input_10.txt"
            )
        except Exception as e:
            messagebox.showerror("Error", f"Could not generate files: {e}")

    def run_on_file(self, path, source_label):
        try:
            a, b = read_integers_from_file(path)
        except Exception as e:
            messagebox.showerror(
                "Invalid file",
                f"Error reading file:\n{e}\n\nExpected format:\n"
                "Line 1: big integer A\nLine 2: big integer B"
            )
            return

        self.reset_view()

        start = time.perf_counter()
        product, steps = startkaratsuba(a, b)
        end = time.perf_counter()
        elapsed_ms = (end - start) * 1000.0

        self.steps = steps
        self.current_step_index = 0
        self.draw_current_step()

        base_name = os.path.splitext(os.path.basename(path))[0]
        # os.makedirs("karatsuba_answers", exist_ok=True)
        ans_filename = f"{base_name}_ans.txt"
        ans_fullpath = os.path.join("karatsuba_answers", ans_filename)
        try:
            with open(ans_fullpath, "w") as f:
                f.write(str(product) + "\n")
        except Exception as e:
            messagebox.showerror(
                "Error saving answer",
                f"Could not write answer file:\n{e}"
            )
            ans_info = "Answer file could not be saved."
        else:
            ans_info = f"Answer saved in file: {ans_filename}"
        
        time_round = round(elapsed_ms)
        text = (
            f"Source: {source_label}\n"
            f"File: {os.path.basename(path)}\n"
            f"Digits A: {len(str(a))}, Digits B: {len(str(b))}\n"
            f"A ~ {scientific_notationizer(a)}\n"
            f"B ~ {scientific_notationizer(b)}\n"
            f"Product ~ {scientific_notationizer(product)}\n"
            f"Time: {time_round} ms\n"
            f"{ans_info}"
        )
        self.set_result(text)

    def on_run(self):
        if not self.inputs_generated:
            # simple popup, reusing your style
            choice = messagebox.askyesno(
                "Input files",
                "Karatsuba input files are not detected. Generate them now?"
            )
            if not choice:
                return
            self.on_generate()
            if not self.inputs_generated:
                return

        idx = simpledialog.askinteger(
            "Select input",
            "Enter an input file number (1-10):",
            parent=self.root,
            minvalue=1,
            maxvalue=10
        )
        if idx is None:
            return

        filename = os.path.join("test_cases", f"karatsuba_input_{idx}.txt")
        if not os.path.exists(filename):
            messagebox.showerror(
                "File missing",
                f"{filename} does not exist. Please generate inputs or choose another file."
            )
            return

        self.run_on_file(filename, f"auto generated Karatsuba file #{idx}")

    def on_select_file(self):
        messagebox.showinfo(
            "Input format",
            "Please choose a .txt file with this format:\n"
            "Line 1: big integer A (at least 100 digits)\n"
            "Line 2: big integer B (at least 100 digits)."
        )
        path = filedialog.askopenfilename(
            title="Select input file",
            filetypes=[("Text files", "*.txt"), ("All files", "*.*")]
        )
        if not path:
            return

        self.run_on_file(path, "manual selection")

    def on_next_step(self):
        if not self.steps:
            messagebox.showinfo("No animation", "Run an input file first to generate steps.")
            return
        if self.current_step_index + 1 >= len(self.steps):
            messagebox.showinfo("End", "Animation finished. You are at the last step.")
            return
        self.current_step_index += 1
        self.draw_current_step()

    def on_reset_animation(self):
        if not self.steps:
            self.reset_view()
            return
        self.playing = False
        self.btn_play.configure(text="Play")
        self.current_step_index = 0
        self.draw_current_step()

    def on_play(self):
        if not self.steps:
            messagebox.showinfo("No animation", "Run an input file first to generate steps.")
            return
        if self.playing:
            self.playing = False
            self.btn_play.configure(text="Play")
            return
        self.playing = True
        self.btn_play.configure(text="Pause")
        self.play_next_step()

    def play_next_step(self):
        if not self.playing:
            return
        if not self.steps:
            return
        if self.current_step_index + 1 >= len(self.steps):
            self.playing = False
            self.btn_play.configure(text="Play")
            return
        self.current_step_index += 1
        self.draw_current_step()
        self.root.after(self.speed_ms, self.play_next_step)

# -------------------- I am tired ---------------------------------------------------------------------------------------------------

if __name__ == "__main__":
    root = tk.Tk()
    root.title("DAA Project - 23k0790,23k0712,23k0628")

    notebook = ttk.Notebook(root)
    notebook.pack(fill=tk.BOTH, expand=True)

    tab1 = ttk.Frame(notebook)
    tab2 = ttk.Frame(notebook)

    notebook.add(tab1, text="Closest Pair")
    notebook.add(tab2, text="Integer Multiplication(Karatsuba)")

    closest_gui = ClosestPairGUI(tab1, root)
    karatsuba_gui = KaratsubaGUI(tab2, root)

    root.mainloop()

