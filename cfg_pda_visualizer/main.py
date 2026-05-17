from cfg_parser import CFG
from visualizer import draw_cfg_tree, draw_pda_states
import os
import json
import tkinter as tk
from tkinter import ttk, messagebox, filedialog
from PIL import Image, ImageTk
from pda_simulator import parse_pda, simulate_pda


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

    def _make_canvas(self, parent):
        """Creates a scrollable, draggable canvas panel."""
        frame = ttk.Frame(parent, relief='sunken', borderwidth=1)
        frame.pack(fill='both', expand=True, padx=10, pady=10)

        hbar = ttk.Scrollbar(frame, orient='horizontal')
        vbar = ttk.Scrollbar(frame, orient='vertical')
        canvas = tk.Canvas(frame, background='white',
                           xscrollcommand=hbar.set, yscrollcommand=vbar.set)

        hbar.config(command=canvas.xview)
        vbar.config(command=canvas.yview)

        hbar.pack(side='bottom', fill='x')
        vbar.pack(side='right', fill='y')
        canvas.pack(side='left', fill='both', expand=True)

        # Drag to pan
        canvas.bind('<ButtonPress-1>', lambda e: canvas.scan_mark(e.x, e.y))
        canvas.bind('<B1-Motion>', lambda e: canvas.scan_dragto(e.x, e.y, gain=1))

        return canvas

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

        self.cfg_canvas = self._make_canvas(self.cfg_tab)

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

        self.pda_canvas = self._make_canvas(self.pda_tab)

    def _show_image_on_canvas(self, canvas, img_path):
        img = Image.open(img_path)
        photo = ImageTk.PhotoImage(img)
        canvas.delete('all')
        canvas.create_image(0, 0, anchor='nw', image=photo)
        canvas.image = photo  # prevent GC
        canvas.config(scrollregion=(0, 0, img.width, img.height))

    def _show_text_on_canvas(self, canvas, text):
        canvas.delete('all')
        canvas.create_text(10, 10, anchor='nw', text=text, font=('Courier', 10), fill='black')
        canvas.config(scrollregion=canvas.bbox('all'))

    def _ask_save(self, src_path, default_name):
        """Popup: ask user if they want to save. Returns chosen path or None."""
        answer = messagebox.askyesno("Save Image", "Do you want to save this image?")
        if answer:
            dest = filedialog.asksaveasfilename(
                defaultextension=".png",
                initialfile=default_name,
                filetypes=[("PNG files", "*.png"), ("All files", "*.*")]
            )
            if dest:
                import shutil
                shutil.copy2(src_path, dest)
                if os.path.exists(src_path):
                    os.remove(src_path)
                return dest
        if os.path.exists(src_path):
            os.remove(src_path) 
        return None

    def load_cfg(self):
        file_path = filedialog.askopenfilename(title="Select CFG Definition File",
                                               filetypes=[("Text files", "*.txt"), ("All files", "*.*")])
        if file_path:
            try:
                with open(file_path, "r") as f:
                    self.cfg_text.delete("1.0", tk.END)
                    self.cfg_text.insert(tk.END, f.read())
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
            # Render to a temp path first
            tmp_path = "saved_results/cfg_tree_tmp.png"
            os.makedirs("saved_results", exist_ok=True)
            draw_cfg_tree(result["tree"], output_file=tmp_path.replace(".png", ""))
            self._show_image_on_canvas(self.cfg_canvas, tmp_path)
            self._ask_save(tmp_path, "cfg_tree.png")
        else:
            messagebox.showerror("CFG Result", "String rejected by CFG.")
            self._show_text_on_canvas(self.cfg_canvas, "String rejected — no parse tree.")

    def step_cfg(self):
        rules_text = self.cfg_text.get("1.0", tk.END).strip()
        input_str = self.cfg_input_entry.get().strip()

        if not rules_text or not input_str:
            messagebox.showwarning("Warning", "Please enter CFG rules and an input string.")
            return

        cfg = CFG(rules_text)
        result = cfg.derive(input_str)

        if result["accepted"]:
            step_text = " → ".join(result["derivation"])
            self._show_text_on_canvas(self.cfg_canvas, step_text)
        else:
            messagebox.showerror("CFG Result", "String rejected by CFG.")
            self._show_text_on_canvas(self.cfg_canvas, "String rejected — no derivation.")

    def reset_cfg(self):
        self.cfg_text.delete("1.0", tk.END)
        self.cfg_input_entry.delete(0, tk.END)
        self._show_text_on_canvas(self.cfg_canvas, "CFG Parse Tree or Derivation will appear here")

    def load_pda(self):
        file_path = filedialog.askopenfilename(title="Select PDA Definition File",
                                               filetypes=[("JSON files", "*.json"), ("Text files", "*.txt"), ("All files", "*.*")])
        if file_path:
            try:
                with open(file_path, "r") as f:
                    self.pda_text.delete("1.0", tk.END)
                    self.pda_text.insert(tk.END, f.read())
                messagebox.showinfo("Loaded", f"PDA definition loaded from:\n{os.path.basename(file_path)}")
            except Exception as e:
                messagebox.showerror("Error", f"Failed to read file:\n{e}")

    def run_pda(self):
        raw = self.pda_text.get("1.0", tk.END).strip()
        inp = self.pda_input_entry.get().strip()

        if not raw or not inp:
            messagebox.showwarning("Warning", "Please enter PDA definition and input string.")
            return

        try:
            pda = parse_pda(raw)
            accepted, trace = simulate_pda(pda, inp)

            if accepted:
                messagebox.showinfo("PDA Result", "String accepted by PDA!")
                tmp_path = "saved_results/pda_diagram.png"
                draw_pda_states(pda, 'pda_diagram')
                self._show_image_on_canvas(self.pda_canvas, tmp_path)
                self._ask_save(tmp_path, "pda_diagram.png")
            else:
                messagebox.showerror("PDA Result", "String rejected by PDA.")
                self._show_text_on_canvas(self.pda_canvas, "String rejected — no diagram.")

        except Exception as e:
            messagebox.showerror("Error", f"Failed to simulate PDA:\n{e}")

    def step_pda(self):
        pda_def = self.pda_text.get("1.0", tk.END).strip()
        input_str = self.pda_input_entry.get().strip()

        if not pda_def or not input_str:
            messagebox.showwarning("Warning", "Please enter PDA definition and input string.")
            return

        try:
            pda = parse_pda(pda_def)
            accepted, trace = simulate_pda(pda, input_str)

            if accepted:
                trace_text = "\n".join(
                    f"State: {s['state']}, Input: {s['input']}, Stack: {s['stack']}" for s in trace
                )
                self._show_text_on_canvas(self.pda_canvas, trace_text)
            else:
                messagebox.showerror("PDA Result", "String rejected by PDA.")
                self._show_text_on_canvas(self.pda_canvas, "String rejected — no trace.")

        except Exception as e:
            messagebox.showerror("Error", f"Failed to step through PDA:\n{e}")

    def reset_pda(self):
        self.pda_text.delete("1.0", tk.END)
        self.pda_input_entry.delete(0, tk.END)
        self._show_text_on_canvas(self.pda_canvas, "PDA Simulation or Graph will appear here")


if __name__ == "__main__":
    root = tk.Tk()
    app = VisualizerApp(root)
    root.mainloop()