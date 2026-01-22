import sys
from pathlib import Path
import tkinter as tk
from tkinter import filedialog, messagebox, ttk
import threading
import io

from PIL import Image


class SpriteCompilerGUI:
    def __init__(self, root: tk.Tk) -> None:
        self.root = root
        self.root.title("PixelRoot32 Sprite Compiler")

        self.input_path_var = tk.StringVar()
        self.grid_var = tk.StringVar(value="16x16")
        self.sprite_count_var = tk.StringVar()
        self.offset_var = tk.StringVar(value="0,0")
        self.output_path_var = tk.StringVar(value="sprites.h")

        self.sprite_entries = []
        # No longer using subprocess, so no# self._current_process = None

        self._set_window_icon()
        self._build_layout()

    def _set_window_icon(self) -> None:
        """Loads and sets the window icon, handling both dev and frozen environments."""
        try:
            if getattr(sys, "frozen", False):
                base_path = Path(sys._MEIPASS)
            else:
                base_path = Path(__file__).parent
            
            # Look for the icon in assets folder
            icon_path = base_path / "assets" / "pr32_logo.png"
            
            if icon_path.exists():
                icon_img = tk.PhotoImage(file=str(icon_path))
                self.root.iconphoto(False, icon_img)
        except Exception as e:
            print(f"Warning: Could not load icon: {e}")

    def _build_layout(self) -> None:
        main = ttk.Frame(self.root, padding=10)
        main.grid(row=0, column=0, sticky="nsew")

        self.root.columnconfigure(0, weight=1)
        self.root.rowconfigure(0, weight=1)
        main.columnconfigure(1, weight=1)

        ttk.Label(main, text="Input PNG:").grid(row=0, column=0, sticky="w")
        input_frame = ttk.Frame(main)
        input_frame.grid(row=0, column=1, columnspan=2, sticky="ew", pady=2)
        input_frame.columnconfigure(0, weight=1)
        ttk.Entry(input_frame, textvariable=self.input_path_var).grid(
            row=0, column=0, sticky="ew"
        )
        ttk.Button(input_frame, text="Browse...", command=self._browse_input).grid(
            row=0, column=1, padx=5
        )

        ttk.Label(main, text="Grid (WxH):").grid(row=1, column=0, sticky="w")
        ttk.Entry(main, textvariable=self.grid_var, width=10).grid(
            row=1, column=1, sticky="w", pady=2
        )

        ttk.Label(main, text="Sprite count (per row):").grid(row=2, column=0, sticky="w")
        ttk.Entry(main, textvariable=self.sprite_count_var, width=10).grid(
            row=2, column=1, sticky="w", pady=2
        )

        ttk.Label(main, text="Offset (X,Y):").grid(row=3, column=0, sticky="w")
        ttk.Entry(main, textvariable=self.offset_var, width=10).grid(
            row=3, column=1, sticky="w", pady=2
        )

        ttk.Label(main, text="Output .h:").grid(row=4, column=0, sticky="w")
        out_frame = ttk.Frame(main)
        out_frame.grid(row=4, column=1, sticky="ew", pady=2)
        out_frame.columnconfigure(0, weight=1)
        ttk.Entry(out_frame, textvariable=self.output_path_var).grid(
            row=0, column=0, sticky="ew"
        )
        ttk.Button(out_frame, text="Browse...", command=self._browse_output).grid(
            row=0, column=1, padx=5
        )

        options_frame = ttk.Frame(main)
        options_frame.grid(row=5, column=0, columnspan=3, sticky="ew", pady=(5, 0))
        options_frame.columnconfigure(2, weight=1)

        ttk.Label(options_frame, text="Export Mode:").grid(row=0, column=0, sticky="w")
        self.mode_var = tk.StringVar(value="layered")
        mode_combo = ttk.Combobox(
            options_frame, 
            textvariable=self.mode_var, 
            values=["layered", "2bpp", "4bpp"], 
            state="readonly", 
            width=10
        )
        mode_combo.grid(row=0, column=1, sticky="w", padx=5)

        ttk.Button(
            options_frame, text="Auto-detect", command=self._auto_detect_clicked
        ).grid(row=0, column=3, sticky="e")
        
        ttk.Label(options_frame, text="(Experimental)", foreground="gray").grid(
            row=0, column=4, sticky="w", padx=(2, 0)
        )

        ttk.Label(main, text="Sprites (gx, gy, gw, gh):").grid(
            row=6, column=0, columnspan=3, sticky="w", pady=(10, 2)
        )

        sprites_frame = ttk.Frame(main, borderwidth=1, relief="sunken")
        sprites_frame.grid(row=7, column=0, columnspan=3, sticky="nsew")
        main.rowconfigure(7, weight=1)
        sprites_frame.columnconfigure(0, weight=1)

        self.sprites_listbox = tk.Listbox(sprites_frame, height=6)
        self.sprites_listbox.grid(row=0, column=0, rowspan=4, sticky="nsew")
        sprites_frame.rowconfigure(0, weight=1)

        self.sprites_listbox.bind("<<ListboxSelect>>", self._on_sprite_select)

        sprite_form = ttk.Frame(sprites_frame, padding=(8, 0, 0, 0))
        sprite_form.grid(row=0, column=1, sticky="nw")

        ttk.Label(sprite_form, text="gx:").grid(row=0, column=0, sticky="w")
        ttk.Label(sprite_form, text="gy:").grid(row=1, column=0, sticky="w")
        ttk.Label(sprite_form, text="gw:").grid(row=2, column=0, sticky="w")
        ttk.Label(sprite_form, text="gh:").grid(row=3, column=0, sticky="w")

        self.gx_var = tk.StringVar(value="0")
        self.gy_var = tk.StringVar(value="0")
        self.gw_var = tk.StringVar(value="1")
        self.gh_var = tk.StringVar(value="1")

        ttk.Entry(sprite_form, textvariable=self.gx_var, width=5).grid(
            row=0, column=1, sticky="w", pady=1
        )
        ttk.Entry(sprite_form, textvariable=self.gy_var, width=5).grid(
            row=1, column=1, sticky="w", pady=1
        )
        ttk.Entry(sprite_form, textvariable=self.gw_var, width=5).grid(
            row=2, column=1, sticky="w", pady=1
        )
        ttk.Entry(sprite_form, textvariable=self.gh_var, width=5).grid(
            row=3, column=1, sticky="w", pady=1
        )

        buttons_frame = ttk.Frame(sprite_form)
        buttons_frame.grid(row=4, column=0, columnspan=2, pady=(8, 0))

        ttk.Button(buttons_frame, text="Add / Update", command=self._add_or_update_sprite).grid(
            row=0, column=0, padx=2
        )
        ttk.Button(buttons_frame, text="Remove", command=self._remove_sprite).grid(
            row=0, column=1, padx=2
        )
        ttk.Button(buttons_frame, text="Clear", command=self._clear_sprites).grid(
            row=0, column=2, padx=2
        )

        compile_frame = ttk.Frame(main)
        compile_frame.grid(row=8, column=0, columnspan=3, sticky="ew", pady=(10, 4))
        compile_frame.columnconfigure(0, weight=1)
        self.compile_button = ttk.Button(
            compile_frame, text="Compile", command=self._run_compiler
        )
        self.compile_button.grid(row=0, column=0, sticky="e")

        ttk.Label(main, text="Log:").grid(row=9, column=0, columnspan=3, sticky="w")

        log_frame = ttk.Frame(main)
        log_frame.grid(row=10, column=0, columnspan=3, sticky="nsew")
        main.rowconfigure(10, weight=1)

        self.log_text = tk.Text(log_frame, height=10, wrap="word")
        self.log_text.grid(row=0, column=0, sticky="nsew")
        log_frame.rowconfigure(0, weight=1)
        log_frame.columnconfigure(0, weight=1)

        scrollbar = ttk.Scrollbar(log_frame, orient="vertical", command=self.log_text.yview)
        scrollbar.grid(row=0, column=1, sticky="ns")
        self.log_text.configure(yscrollcommand=scrollbar.set)

    def _browse_input(self) -> None:
        path = filedialog.askopenfilename(
            title="Select sprite sheet PNG",
            filetypes=[("PNG images", "*.png"), ("All files", "*.*")],
        )
        if path:
            self.input_path_var.set(path)

    def _auto_detect_clicked(self) -> None:
        path = self.input_path_var.get().strip()
        if not path:
            messagebox.showerror("No input", "Please select an input PNG first.")
            return
        p = Path(path)
        if not p.is_file():
            messagebox.showerror("Invalid input", "Input PNG file does not exist.")
            return
        if p.suffix.lower() != ".png":
            messagebox.showerror("Invalid input", "Input file must be a PNG image.")
            return
        self._auto_fill_from_image(path)

    def _browse_output(self) -> None:
        path = filedialog.asksaveasfilename(
            title="Select output header",
            defaultextension=".h",
            filetypes=[("C header", "*.h"), ("All files", "*.*")],
            initialfile=self.output_path_var.get() or "sprites.h",
        )
        if path:
            self.output_path_var.set(path)

    def _auto_fill_from_image(self, path: str) -> None:
        try:
            img = Image.open(path).convert("RGBA")
        except Exception as exc:
            messagebox.showwarning("Analysis failed", f"Could not analyze image:\n{exc}")
            return

        # Check for color/layer count warning
        pixels = img.load()
        colors = set()
        for y in range(img.height):
            for x in range(img.width):
                r, g, b, a = pixels[x, y]
                if a > 0:
                    colors.add((r, g, b))
        
        if len(colors) > 4:
            messagebox.showwarning(
                "Performance Warning",
                f"Detected {len(colors)} unique colors (layers).\n\n"
                "Using more than 4 layers for main characters may degrade performance on ESP32.\n"
                "Consider using 4bpp packed sprites for higher color counts."
            )

        bbox = img.getbbox()
        if not bbox:
            return

        left, top, right, bottom = bbox
        width, height = img.size

        def divisors(n: int):
            result = set()
            limit = int(n**0.5) + 1
            for d in range(1, limit):
                if n % d == 0:
                    result.add(d)
                    result.add(n // d)
            return sorted(result)

        sprite_count = None
        sprite_count_str = self.sprite_count_var.get().strip()
        if sprite_count_str:
            try:
                sprite_count = int(sprite_count_str)
            except ValueError:
                sprite_count = None

        grid_w = None
        columns = None

        if sprite_count and sprite_count > 0 and width % sprite_count == 0:
            grid_w = width // sprite_count
            columns = sprite_count
        else:
            candidates = [d for d in divisors(width) if 8 <= d <= width]
            preferred = [16, 32, 8, 24, 48, 64]

            for p in preferred:
                if p in candidates:
                    grid_w = p
                    break

            if grid_w is None:
                if candidates:
                    grid_w = max(candidates)
                else:
                    grid_w = width

            columns = max(1, width // grid_w)

        grid_h = grid_w
        rows = max(1, height // grid_h)

        row_occupied = []
        for gy in range(rows):
            y0 = top + gy * grid_h
            y1 = min(y0 + grid_h, bottom)
            occupied = False
            for y in range(y0, y1):
                for x in range(left, right):
                    r, g, b, a = pixels[x, y]
                    if a > 0:
                        occupied = True
                        break
                if occupied:
                    break
            row_occupied.append(occupied)

        max_occ_row = -1
        for i, occ in enumerate(row_occupied):
            if occ:
                max_occ_row = i

        self.grid_var.set(f"{grid_w}x{grid_h}")
        self.offset_var.set(f"{left},{top}")

        self._clear_sprites()

        count = 0

        if max_occ_row != -1 and max_occ_row <= 1:
            max_rows = max_occ_row + 1
            for gx in range(columns):
                x0 = left + gx * grid_w
                col_rows = [False] * max_rows
                for gy in range(max_rows):
                    y0 = top + gy * grid_h
                    y1 = min(y0 + grid_h, bottom)
                    for y in range(y0, y1):
                        for x in range(x0, x0 + grid_w):
                            r, g, b, a = pixels[x, y]
                            if a > 0:
                                col_rows[gy] = True
                                break
                        if col_rows[gy]:
                            break
                gy = 0
                while gy < max_rows:
                    if not col_rows[gy]:
                        gy += 1
                        continue
                    start = gy
                    while gy < max_rows and col_rows[gy]:
                        gy += 1
                    gh = gy - start
                    spec = f"{gx},{start},1,{gh}"
                    self.sprite_entries.append(spec)
                    self.sprites_listbox.insert(tk.END, spec)
                    count += 1
        else:
            for gy in range(rows):
                for gx in range(columns):
                    spec = f"{gx},{gy},1,1"
                    self.sprite_entries.append(spec)
                    self.sprites_listbox.insert(tk.END, spec)
                    count += 1

        self.log_text.insert(
            tk.END,
            f"Auto-detected grid {grid_w}x{grid_h}, offset {left},{top}, {count} sprite(s).\n",
        )
        self.log_text.see(tk.END)

    def _add_or_update_sprite(self) -> None:
        try:
            gx = int(self.gx_var.get())
            gy = int(self.gy_var.get())
            gw = int(self.gw_var.get())
            gh = int(self.gh_var.get())
        except ValueError:
            messagebox.showerror("Invalid sprite", "gx, gy, gw, gh must be integers.")
            return

        if gw <= 0 or gh <= 0:
            messagebox.showerror("Invalid sprite", "gw and gh must be positive.")
            return

        spec = f"{gx},{gy},{gw},{gh}"

        selection = self.sprites_listbox.curselection()
        if selection:
            index = selection[0]
            self.sprite_entries[index] = spec
            self.sprites_listbox.delete(index)
            self.sprites_listbox.insert(index, spec)
        else:
            self.sprite_entries.append(spec)
            self.sprites_listbox.insert(tk.END, spec)

    def _remove_sprite(self) -> None:
        selection = self.sprites_listbox.curselection()
        if not selection:
            return
        index = selection[0]
        del self.sprite_entries[index]
        self.sprites_listbox.delete(index)

    def _clear_sprites(self) -> None:
        self.sprite_entries.clear()
        self.sprites_listbox.delete(0, tk.END)

    def _on_sprite_select(self, event: tk.Event) -> None:
        selection = self.sprites_listbox.curselection()
        if not selection:
            return
        spec = self.sprite_entries[selection[0]]
        gx, gy, gw, gh = spec.split(",")
        self.gx_var.set(gx)
        self.gy_var.set(gy)
        self.gw_var.set(gw)
        self.gh_var.set(gh)

    def _validate_inputs(self) -> bool:
        input_path = Path(self.input_path_var.get())
        if not input_path.is_file():
            messagebox.showerror("Invalid input", "Input PNG file does not exist.")
            return False
        if input_path.suffix.lower() != ".png":
            messagebox.showerror("Invalid input", "Input file must be a PNG image.")
            return False

        grid_value = self.grid_var.get().strip().lower()
        parts = grid_value.split("x")
        if len(parts) != 2:
            messagebox.showerror("Invalid grid", "Grid must be in the form WxH, e.g. 16x16.")
            return False
        try:
            w = int(parts[0])
            h = int(parts[1])
        except ValueError:
            messagebox.showerror("Invalid grid", "Grid values must be integers.")
            return False
        if w <= 0 or h <= 0:
            messagebox.showerror("Invalid grid", "Grid values must be positive.")
            return False

        offset_value = self.offset_var.get().strip()
        if offset_value:
            offset_parts = offset_value.split(",")
            if len(offset_parts) != 2:
                messagebox.showerror(
                    "Invalid offset", "Offset must be in the form X,Y, e.g. 0,10."
                )
                return False
            try:
                int(offset_parts[0])
                int(offset_parts[1])
            except ValueError:
                messagebox.showerror(
                    "Invalid offset", "Offset X and Y must be integers."
                )
                return False

        if not self.sprite_entries:
            messagebox.showerror(
                "No sprites",
                "You must define at least one sprite (gx, gy, gw, gh).",
            )
            return False

        output_path = self.output_path_var.get().strip()
        if not output_path:
            messagebox.showerror(
                "Invalid output", "Please specify an output header file name."
            )
            return False

        return True

    def _run_compiler(self) -> None:
        if not self._validate_inputs():
            return

        # Locate the script, handling PyInstaller frozen state
        if getattr(sys, "frozen", False):
            # If frozen, the script should be in the temp folder (sys._MEIPASS)
            base_path = Path(sys._MEIPASS)
        else:
            # If normal script, look in the same directory
            base_path = Path(__file__).parent

        script_path = base_path / "pr32-sprite-compiler.py"

        if not script_path.is_file():
            messagebox.showerror(
                "Script not found",
                f"Could not find pr32-sprite-compiler.py.\n\nExpected at:\n{script_path}",
            )
            return

        # Build arguments for the script
        # Note: sys.argv[0] will be the script name passed to the executed code
        args = [str(script_path), self.input_path_var.get()]

        args.extend(["--grid", self.grid_var.get().strip()])

        offset_value = self.offset_var.get().strip()
        if offset_value:
            args.extend(["--offset", offset_value])

        for spec in self.sprite_entries:
            args.extend(["--sprite", spec])

        args.extend(["--out", self.output_path_var.get().strip()])

        args.extend(["--mode", self.mode_var.get()])

        self.compile_button.configure(state="disabled")
        self.root.update_idletasks()

        self.log_text.insert(tk.END, "Starting compilation...\n")
        self.log_text.insert(tk.END, "Args: " + " ".join(args) + "\n")
        self.log_text.see(tk.END)

        # Run compilation in a separate thread to avoid freezing GUI
        threading.Thread(
            target=self._execute_script_in_thread, args=(script_path, args), daemon=True
        ).start()

    def _execute_script_in_thread(self, script_path: Path, args: list) -> None:
        output_buffer = io.StringIO()
        
        # Capture stdout/stderr and override argv
        original_stdout = sys.stdout
        original_stderr = sys.stderr
        original_argv = sys.argv
        
        sys.stdout = output_buffer
        sys.stderr = output_buffer
        sys.argv = args

        return_code = 0
        try:
            with open(script_path, "r", encoding="utf-8") as f:
                code = compile(f.read(), str(script_path), "exec")
            
            # Create a clean global context
            global_context = {"__name__": "__main__", "__file__": str(script_path)}
            
            # Execute the script
            exec(code, global_context)
            
        except SystemExit as e:
            # The script called sys.exit()
            if isinstance(e.code, int):
                return_code = e.code
            elif e.code is None:
                return_code = 0
            else:
                return_code = 1
                print(f"Exit: {e.code}") # goes to buffer
        except Exception:
            import traceback
            traceback.print_exc() # goes to buffer
            return_code = 1
        finally:
            # Restore original streams
            sys.stdout = original_stdout
            sys.stderr = original_stderr
            sys.argv = original_argv

        # Update GUI in the main thread
        self.root.after(
            0, self._on_compilation_finished, output_buffer.getvalue(), return_code
        )

    def _on_compilation_finished(self, output: str, return_code: int) -> None:
        self.log_text.insert(tk.END, output)
        self.log_text.see(tk.END)
        
        self.compile_button.configure(state="normal")

        if return_code == 0:
            messagebox.showinfo("Done", "Compilation finished successfully.")
        else:
            messagebox.showerror(
                "Compiler error",
                f"pr32-sprite-compiler exited with code {return_code}.\nSee log for details.",
            )

    # Removed _poll_process_output as we now use threading/exec


def main() -> None:
    root = tk.Tk()
    SpriteCompilerGUI(root)
    root.mainloop()


if __name__ == "__main__":
    main()

