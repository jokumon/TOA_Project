from cfg_parser import CFG
from visualizer import draw_cfg_tree, draw_pda_states
import os
import json
import tkinter as tk
from tkinter import ttk, messagebox, filedialog
from PIL import Image, ImageTk
from pda_simulator import parse_pda, simulate_pda
from PIL import Image

class VisualizerApp:
    def __init__(self, root):
        self.root = root
        self.root.title("PDA / CFG Visualizer Tool")
        self.root.geometry("1000x700")

        self.notebook = ttk.Notebook(root)
        self.cfg_tab = ttk.Frame(self.notebook)
        self.pda_tab = ttk.Frame(self.notebook)
        self.notebook.add(self.cfg_tab, text='CFG Mode')
        self.notebook.add(self.pda_tab, text='PDA Mode')
        self.notebook.pack(expand=1, fill='both')

        self.create_cfg_ui()
        self.create_pda_ui()

    def create_cfg_ui(self):
        ttk.Label(self.cfg_tab, text="Enter CFG Rules:").pack(anchor='w', padx=10, pady=(10, 0))
        self.cfg_text = tk.Text(self.cfg_tab, height=10)
        self.cfg_text.pack(fill='x', padx=10)

        ttk.Label(self.cfg_tab, text="Input String:").pack(anchor='w', padx=10, pady=(10, 0))
        self.cfg_input_entry = tk.Entry(self.cfg_tab)
        self.cfg_input_entry.pack(fill='x', padx=10)

        cfg_button_frame = ttk.Frame(self.cfg_tab)
        cfg_button_frame.pack(pady=10)
        ttk.Button(cfg_button_frame, text="Load CFG", command=self.load_cfg).pack(side='left', padx=5)
        ttk.Button(cfg_button_frame, text="Run", command=self.run_cfg).pack(side='left', padx=5)
        ttk.Button(cfg_button_frame, text="Step", command=self.step_cfg).pack(side='left', padx=5)
        ttk.Button(cfg_button_frame, text="Reset", command=self.reset_cfg).pack(side='left', padx=5)

        self.cfg_visual_output = ttk.Label(self.cfg_tab, text="CFG Parse Tree or Derivation will appear here", background="white", relief='sunken')
        self.cfg_visual_output.pack(fill='both', expand=True, padx=10, pady=10)

    def create_pda_ui(self):
        ttk.Label(self.pda_tab, text="Enter PDA Definition:").pack(anchor='w', padx=10, pady=(10, 0))
        self.pda_text = tk.Text(self.pda_tab, height=10)
        self.pda_text.pack(fill='x', padx=10)

        ttk.Label(self.pda_tab, text="Input String:").pack(anchor='w', padx=10, pady=(10, 0))
        self.pda_input_entry = tk.Entry(self.pda_tab)
        self.pda_input_entry.pack(fill='x', padx=10)

        pda_button_frame = ttk.Frame(self.pda_tab)
        pda_button_frame.pack(pady=10)
        ttk.Button(pda_button_frame, text="Load PDA", command=self.load_pda).pack(side='left', padx=5)
        ttk.Button(pda_button_frame, text="Run", command=self.run_pda).pack(side='left', padx=5)
        ttk.Button(pda_button_frame, text="Step", command=self.step_pda).pack(side='left', padx=5)
        ttk.Button(pda_button_frame, text="Reset", command=self.reset_pda).pack(side='left', padx=5)

        self.pda_visual_output = ttk.Label(self.pda_tab, text="PDA Simulation or Graph will appear here", background="white", relief='sunken')
        self.pda_visual_output.pack(fill='both', expand=True, padx=10, pady=10)

    def load_cfg(self):
        file_path = filedialog.askopenfilename(title="Select CFG Definition File", filetypes=[("Text files", "*.txt"), ("All files", "*.*")])
        if file_path:
            try:
                with open(file_path, "r") as file:
                    content = file.read()
                    self.cfg_text.delete("1.0", tk.END)
                    self.cfg_text.insert(tk.END, content)
                    messagebox.showinfo("Loaded", f"CFG rules loaded from:\n{os.path.basename(file_path)}")
            except Exception as e:
                messagebox.showerror("Error", f"Failed to read file:\n{e}")

    def run_cfg(self):
        rules_text = self.cfg_text.get("1.0", tk.END).strip()
        input_str = self.cfg_input_entry.get().strip()

        if not rules_text or not input_str:
            messagebox.showwarning("Warning", "Please enter both CFG rules and an input string.")
            return

        cfg = CFG(rules_text)
        result = cfg.derive(input_str)

        if result["accepted"]:
            messagebox.showinfo("CFG Result", "String accepted by CFG!")
            output_path = draw_cfg_tree(result["tree"], output_file="cfg_tree")
            img = Image.open(output_path)
            draw_cfg_tree(result["tree"], output_file=output_path)
            try:
                img = Image.open(output_path)
                img.thumbnail((800, 500))
                photo = ImageTk.PhotoImage(img)
                self.cfg_visual_output.config(image=photo, text="")
                self.cfg_visual_output.image = photo
            except Exception as e:
                messagebox.showerror("Error", f"Failed to load image: {e}")
        else:
            messagebox.showerror("CFG Result", "String rejected by CFG.")
            self.cfg_visual_output.config(text="CFG Parse Tree or Derivation will appear here", image='')

    def step_cfg(self):
        rules_text = self.cfg_text.get("1.0", tk.END).strip()
        input_str = self.cfg_input_entry.get().strip()

        if not rules_text or not input_str:
            messagebox.showwarning("Warning", "Please enter CFG rules and an input string.")
            return

        cfg = CFG(rules_text)
        result = cfg.derive(input_str)

        if result["accepted"]:
            derivation_steps = result["derivation"]
            step_text = " → ".join(derivation_steps)
            self.cfg_visual_output.config(text=step_text, image='')
        else:
            messagebox.showerror("CFG Result", "String rejected by CFG.")
            self.cfg_visual_output.config(text="CFG Parse Tree or Derivation will appear here", image='')

    def reset_cfg(self):
        self.cfg_text.delete("1.0", tk.END)
        self.cfg_input_entry.delete(0, tk.END)
        self.cfg_visual_output.config(text="CFG Parse Tree or Derivation will appear here")

    def load_pda(self):
        file_path = filedialog.askopenfilename(title="Select PDA Definition File", filetypes=[("JSON files", "*.json"), ("Text files", "*.txt"), ("All files", "*.*")])
        if file_path:
            try:
                with open(file_path, "r") as file:
                    content = file.read()
                    self.pda_text.delete("1.0", tk.END)
                    self.pda_text.insert(tk.END, content)
                    messagebox.showinfo("Loaded", f"PDA definition loaded from:\n{os.path.basename(file_path)}")
            except Exception as e:
                messagebox.showerror("Error", f"Failed to read file:\n{e}")

    def run_pda(self):
        # 1) Read from the text widget
        raw = self.pda_text.get("1.0", tk.END).strip()
        inp = self.pda_input_entry.get().strip()

        if not raw or not inp:
            messagebox.showwarning("Warning", "Please enter PDA definition and input string.")
            return

        # --- DEBUG #1: show exactly what text we're parsing
        print("\n=== RAW PDA TEXT ===")
        print(raw)
        print("====================\n")

        try:
            # 2) Always parse through parse_pda
            pda = parse_pda(raw)

            # --- DEBUG #2: dump the transitions we got back
            print("\n=== PARSED TRANSITIONS ===")
            for key, actions in pda['transitions'].items():
                print(key, "→", actions)
            print("==========================\n")

            # 3) Run the simulation
            accepted, trace = simulate_pda(pda, inp)

            if accepted:
                messagebox.showinfo("PDA Result", "String accepted by PDA!")
                img_path = draw_pda_states(pda, 'pda_diagram')
                image = Image.open(img_path)
                image = image.resize((800, 300), Image.Resampling.LANCZOS)
                photo = ImageTk.PhotoImage(image)
                self.pda_visual_output.config(image=photo, text="")
                self.pda_visual_output.image = photo
            else:
                messagebox.showerror("PDA Result", "String rejected by PDA.")
                self.pda_visual_output.config(text="PDA Simulation or Graph will appear here", image='')

        except Exception as e:
            messagebox.showerror("Error", f"Failed to simulate PDA:\n{e}")



    def step_pda(self):
        pda_def = self.pda_text.get("1.0", tk.END).strip()
        input_str = self.pda_input_entry.get().strip()

        if not pda_def or not input_str:
            messagebox.showwarning("Warning", "Please enter PDA definition and input string.")
            return

        try:
            pda_dict = json.loads(pda_def)
            pda = parse_pda(pda_def)
            accepted, trace = simulate_pda(pda, input_str)
            
            if accepted:
                trace_text = "\n".join(f"State: {step['state']}, Input: {step['input']}, Stack: {step['stack']}" for step in trace)
                self.pda_visual_output.config(text=trace_text, image='')
            else:
                messagebox.showerror("PDA Result", "String rejected by PDA.")
                self.pda_visual_output.config(text="PDA Simulation or Graph will appear here", image='')

        except Exception as e:
            messagebox.showerror("Error", f"Failed to step through PDA:\n{e}")

    def reset_pda(self):
        self.pda_text.delete("1.0", tk.END)
        self.pda_input_entry.delete(0, tk.END)
        self.pda_visual_output.config(text="PDA Simulation or Graph will appear here")

if __name__ == "__main__":
    root = tk.Tk()
    app = VisualizerApp(root)
    root.mainloop()
