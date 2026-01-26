import tkinter as tk
from tkinter import filedialog, messagebox
import ttkbootstrap as tb
from ttkbootstrap.constants import *
from ttkbootstrap.scrolled import ScrolledText, ScrolledFrame
from PIL import Image, ImageTk, ImageDraw
import sys
import os
from pathlib import Path
import io

from src.services.exporter import Exporter
from src.core.models import SpriteDefinition, CompilationOptions

VERSION = "v0.2.0-dev"

class FloatingPanel(tb.Frame):
    """
    Base class for in-editor floating panels.
    They are implemented as child frames that can be positioned absolutely.
    """
    def __init__(self, parent, title, width=350, height=400, on_close=None):
        super().__init__(parent, relief=tk.RAISED, borderwidth=1)
        self.on_close = on_close
        self.width = width
        self.height = height
        header = tb.Frame(self, bootstyle="secondary")
        header.pack(fill=tk.X)
        tb.Label(header, text=title, font=("Segoe UI", 10, "bold"), bootstyle="inverse-secondary", padding=(10, 5)).pack(side=tk.LEFT)
        tb.Button(header, text="✕", bootstyle="secondary-link", command=self.hide, padding=(5, 2)).pack(side=tk.RIGHT, padx=5)
        self.content = tb.Frame(self, padding=15)
        self.content.pack(fill=tk.BOTH, expand=True)

    def show(self, x=None, y=None):
        """Displays the panel at the given coordinates within its parent."""
        # Center if no coords provided
        if x is None:
            self.update_idletasks()
            parent_w = self.master.winfo_width()
            parent_h = self.master.winfo_height()
            x = (parent_w - self.width) // 2
            y = (parent_h - self.height) // 2
            
        self.place(x=x, y=y, width=self.width, height=self.height)
        self.tkraise()

    def hide(self):
        """Hides the panel and triggers the on_close callback."""
        self.place_forget()
        if self.on_close: self.on_close()

class AboutPanel(FloatingPanel):
    """
    Informational panel about the compiler version and credits.
    """
    def __init__(self, parent, on_close=None):
        super().__init__(parent, "About PixelRoot32", width=380, height=320, on_close=on_close)
        tb.Label(self.content, text="PixelRoot32 Sprite Compiler", font=("Segoe UI", 12, "bold")).pack(pady=(10, 5))
        tb.Label(self.content, text=VERSION).pack(pady=(0, 15))
        tb.Label(self.content, text="A mechanical sprite sheet compiler for the PixelRoot32 engine.\nConverts PNGs to optimized bitfields for ESP32.", justify=tk.CENTER, wraplength=320).pack(pady=5)
        
        tb.Button(self.content, text="Close", bootstyle="secondary-outline", command=self.hide).pack(side=tk.BOTTOM, pady=10)

class MainWindow(tb.Window):
    def __init__(self):
        super().__init__(title="PixelRoot32 Sprite Compiler", themename="darkly", resizable=(True, True))
        self.geometry("650x900")
        
        self.input_path_var = tk.StringVar()
        self.grid_var = tk.StringVar(value="16x16")
        self.sprite_count_var = tk.StringVar()
        self.offset_var = tk.StringVar(value="0,0")
        self.output_path_var = tk.StringVar(value="sprites.h")
        self.mode_var = tk.StringVar(value="layered")
        self.prefix_var = tk.StringVar(value="")

        # Manual Sprite Entry Vars
        self.manual_gx = tk.StringVar(value="0")
        self.manual_gy = tk.StringVar(value="0")
        self.manual_gw = tk.StringVar(value="1")
        self.manual_gh = tk.StringVar(value="1")
        
        self.sprites_list = [] # List of SpriteDefinition

        self._setup_assets()
        self._build_layout()
        
    def _setup_assets(self):
        base_path = Path(__file__).parent.parent
        
        # Window icon
        logo_path = base_path / "assets" / "pr32_logo.png"
        if logo_path.exists():
            img = Image.open(logo_path)
            self.icon_img = ImageTk.PhotoImage(img)
            self.iconphoto(False, self.icon_img)

    def _create_card(self, parent, title, number=None):
        card = tb.Frame(parent, bootstyle="secondary")
        card.pack(fill=X, pady=2, padx=2)
        
        inner = tb.Frame(card, padding=(15, 10))
        inner.pack(fill=X)
        
        header_text = f"{number}. {title}" if number else title
        title_lbl = tb.Label(inner, text=header_text, font=("Segoe UI", 10, "bold"))
        title_lbl.pack(anchor=W)
        
        sep = tb.Separator(inner, bootstyle="secondary")
        sep.pack(fill=X, pady=(2, 8))
        
        return inner

    def _build_layout(self):
        # Status Bar at the very bottom (outside scroll)
        status_bar = tb.Frame(self)
        status_bar.pack(side=BOTTOM, fill=X)
        
        self.status_label = tb.Label(status_bar, text="Ready", bootstyle="secondary", padding=5)
        self.status_label.pack(side=LEFT)
        
        # Help/About button
        tb.Button(status_bar, text="?", bootstyle="secondary-link", 
                  command=self._show_about, padding=5).pack(side=RIGHT)

        version_label = tb.Label(status_bar, text=VERSION, bootstyle="secondary", padding=5)
        version_label.pack(side=RIGHT)

        # Use a scrolled frame for the rest of the content
        scroll_container = ScrolledFrame(self, autohide=True)
        scroll_container.pack(fill=BOTH, expand=YES, padx=10, pady=5)
        
        main_container = scroll_container

        # --- Paso 1: Input Image ---
        card1 = self._create_card(main_container, "Input Image", 1)
        
        file_row = tb.Frame(card1)
        file_row.pack(fill=X)
        
        tb.Label(file_row, text="Input PNG:", width=12).pack(side=LEFT)
        tb.Entry(file_row, textvariable=self.input_path_var).pack(side=LEFT, fill=X, expand=YES, padx=5)
        tb.Button(file_row, text="Browse...", bootstyle="secondary-outline", command=self._browse_input).pack(side=LEFT)

        # --- Paso 2: Grid Settings ---
        card2 = self._create_card(main_container, "Grid Settings", 2)
        
        grid_row = tb.Frame(card2)
        grid_row.pack(fill=X)
        
        tb.Label(grid_row, text="Grid (WxH):", width=15).pack(side=LEFT)
        tb.Entry(grid_row, textvariable=self.grid_var, width=15).pack(side=LEFT, padx=5)
        
        tb.Label(grid_row, text="Offset (X,Y):", width=15, padding=(20, 0, 0, 0)).pack(side=LEFT)
        tb.Entry(grid_row, textvariable=self.offset_var, width=15).pack(side=LEFT, padx=5)

        row2 = tb.Frame(card2)
        row2.pack(fill=X, pady=(10, 0))
        tb.Label(row2, text="Sprite count (per row):", width=20).pack(side=LEFT)
        tb.Entry(row2, textvariable=self.sprite_count_var, width=15).pack(side=LEFT, padx=5)
        
        tb.Button(row2, text="Auto-detect", bootstyle="secondary-outline", command=self._on_auto_detect_click).pack(side=LEFT, padx=5)
        tb.Label(row2, text="(Experimental)", bootstyle="secondary").pack(side=LEFT)

        # --- Paso 3: Sprite Selection ---
        card3 = self._create_card(main_container, "Sprite Selection", 3)
        
        sprite_editor_frame = tb.Frame(card3)
        sprite_editor_frame.pack(fill=BOTH, expand=YES)

        # Left: Listbox
        list_container = tb.Frame(sprite_editor_frame)
        list_container.pack(side=LEFT, fill=BOTH, expand=YES)

        self.sprite_listbox = tk.Listbox(list_container, height=5, bg="#2b2b2b", fg="white", 
                                       selectbackground="#007acc", borderwidth=1, relief="solid")
        self.sprite_listbox.pack(side=LEFT, fill=BOTH, expand=YES)
        self.sprite_listbox.bind('<<ListboxSelect>>', self._on_listbox_select)
        
        scrollbar = tb.Scrollbar(list_container, orient=VERTICAL, command=self.sprite_listbox.yview)
        scrollbar.pack(side=RIGHT, fill=Y)
        self.sprite_listbox.config(yscrollcommand=scrollbar.set)

        # Right: Manual Controls
        controls_frame = tb.Frame(sprite_editor_frame, padding=(15, 0, 0, 0))
        controls_frame.pack(side=RIGHT, fill=Y)

        entry_grid = tb.Frame(controls_frame)
        entry_grid.pack(fill=X)

        for i, (label, var) in enumerate([("gx:", self.manual_gx), ("gy:", self.manual_gy), 
                                         ("gw:", self.manual_gw), ("gh:", self.manual_gh)]):
            tb.Label(entry_grid, text=label).grid(row=i, column=0, sticky=W, pady=2, padx=(0, 20))
            tb.Entry(entry_grid, textvariable=var, width=10).grid(row=i, column=1, sticky=EW, pady=2)

        btn_row = tb.Frame(controls_frame)
        btn_row.pack(fill=X, pady=(15, 0))
        
        tb.Button(btn_row, text="Add / Update", bootstyle="primary", command=self._on_add_sprite).pack(fill=X, pady=2)
        tb.Button(btn_row, text="Remove", bootstyle="secondary-outline", command=self._on_remove_sprite).pack(fill=X, pady=2)
        tb.Button(btn_row, text="Clear", bootstyle="secondary-outline", command=self._on_clear_sprites).pack(fill=X, pady=2)

        # --- Paso 4: Export ---
        card4 = self._create_card(main_container, "Export", 4)
        
        row_export = tb.Frame(card4)
        row_export.pack(fill=X)
        
        tb.Label(row_export, text="Export Mode:", width=12).pack(side=LEFT)
        tb.Combobox(row_export, textvariable=self.mode_var, values=["layered", "2bpp", "4bpp"], state="readonly", width=12).pack(side=LEFT, padx=5)
        
        tb.Label(row_export, text="Prefix:", width=10, padding=(15, 0, 0, 0)).pack(side=LEFT)
        tb.Entry(row_export, textvariable=self.prefix_var, width=15).pack(side=LEFT, padx=5)

        row_output = tb.Frame(card4)
        row_output.pack(fill=X, pady=(10, 0))
        tb.Label(row_output, text="Output .h:", width=12).pack(side=LEFT)
        tb.Entry(row_output, textvariable=self.output_path_var).pack(side=LEFT, fill=X, expand=YES, padx=5)
        tb.Button(row_output, text="Browse...", bootstyle="secondary-outline", command=self._browse_output).pack(side=LEFT)

        tb.Button(card4, text="Export Sprites", bootstyle="info", 
                  command=self._on_compile, padding=(20, 10)).pack(anchor=W, pady=(20, 0))

        # --- Paso 5: Log ---
        card5 = self._create_card(main_container, "Log")
        
        self.log_area = ScrolledText(card5, height=8, autohide=True, bootstyle="dark")
        self.log_area.pack(fill=BOTH, expand=YES)
        self.log("Ready...")

    # --- UI Logic ---

    def _show_about(self):
        about = AboutPanel(self)
        about.show()

    def log(self, message, style=None):
        if style == "warning":
            self.log_area.insert(END, message + "\n", "warning")
            self.log_area.tag_configure("warning", foreground="orange")
        elif style == "error":
            self.log_area.insert(END, message + "\n", "error")
            self.log_area.tag_configure("error", foreground="red")
        elif style == "success":
            self.log_area.insert(END, message + "\n", "success")
            self.log_area.tag_configure("success", foreground="lightgreen")
        else:
            self.log_area.insert(END, message + "\n")
        self.log_area.see(END)

    def _browse_input(self):
        path = filedialog.askopenfilename(filetypes=[("PNG images", "*.png")])
        if path:
            self.input_path_var.set(path)
            self.log(f"Selected input: {path}")

    def _browse_output(self):
        path = filedialog.asksaveasfilename(defaultextension=".h", filetypes=[("C Header", "*.h")])
        if path:
            self.output_path_var.set(path)
            self.log(f"Selected output: {path}")

    def _on_add_sprite(self):
        try:
            gx, gy = int(self.manual_gx.get()), int(self.manual_gy.get())
            gw, gh = int(self.manual_gw.get()), int(self.manual_gh.get())
            
            # Check if updating existing
            selection = self.sprite_listbox.curselection()
            if selection:
                idx = selection[0]
                self.sprites_list[idx] = SpriteDefinition(gx, gy, gw, gh, idx)
                self.sprite_listbox.delete(idx)
                self.sprite_listbox.insert(idx, f"Sprite {idx}: {gx},{gy} ({gw}x{gh})")
                self.sprite_listbox.select_set(idx)
            else:
                idx = len(self.sprites_list)
                self.sprites_list.append(SpriteDefinition(gx, gy, gw, gh, idx))
                self.sprite_listbox.insert(END, f"Sprite {idx}: {gx},{gy} ({gw}x{gh})")
        except ValueError:
            messagebox.showerror("Error", "Please enter valid numeric values for sprite dimensions.")

    def _on_remove_sprite(self):
        selection = self.sprite_listbox.curselection()
        if selection:
            idx = selection[0]
            self.sprite_listbox.delete(idx)
            self.sprites_list.pop(idx)
            # Re-index
            self._refresh_listbox()

    def _on_clear_sprites(self):
        self.sprite_listbox.delete(0, END)
        self.sprites_list = []

    def _refresh_listbox(self):
        self.sprite_listbox.delete(0, END)
        for i, s in enumerate(self.sprites_list):
            s.index = i
            self.sprite_listbox.insert(END, f"Sprite {i}: {s.gx},{s.gy} ({s.gw}x{s.gh})")

    def _on_listbox_select(self, event):
        selection = self.sprite_listbox.curselection()
        if selection:
            s = self.sprites_list[selection[0]]
            self.manual_gx.set(str(s.gx))
            self.manual_gy.set(str(s.gy))
            self.manual_gw.set(str(s.gw))
            self.manual_gh.set(str(s.gh))

    def _on_auto_detect_click(self):
        input_path = self.input_path_var.get()
        if not input_path or not os.path.exists(input_path):
            messagebox.showerror("Error", "Please select a valid input PNG first.")
            return
        
        try:
            img = Image.open(input_path)
            w, h = img.size
            
            # Parse grid
            try:
                gw, gh = map(int, self.grid_var.get().lower().split('x'))
            except:
                gw, gh = 16, 16
                self.grid_var.set("16x16")

            cols = w // gw
            rows = h // gh
            
            # Respect sprite count if provided
            try:
                max_cols = int(self.sprite_count_var.get())
                if max_cols > 0: cols = min(cols, max_cols)
            except: pass

            self._on_clear_sprites()
            idx = 0
            for gy in range(rows):
                for gx in range(cols):
                    self.sprites_list.append(SpriteDefinition(gx, gy, 1, 1, idx))
                    self.sprite_listbox.insert(END, f"Sprite {idx}: {gx},{gy} (1x1)")
                    idx += 1
            
            self.log(f"Auto-detected {idx} sprites ({cols}x{rows} grid).")
            
        except Exception as e:
            messagebox.showerror("Error", f"Auto-detect failed: {e}")

    def _on_compile(self):
        input_path = self.input_path_var.get()
        if not input_path or not os.path.exists(input_path):
            messagebox.showerror("Error", "Please select a valid input PNG file.")
            return

        if not self.sprites_list:
            if messagebox.askyesno("No Sprites", "No sprites defined in list. Auto-detect now?"):
                self._on_auto_detect_click()
                if not self.sprites_list: return
            else:
                return

        try:
            # Parse settings
            gw, gh = map(int, self.grid_var.get().lower().split('x'))
            ox, oy = map(int, self.offset_var.get().split(','))
            
            img = Image.open(input_path).convert("RGBA")
            
            options = CompilationOptions(
                grid_w=gw, grid_h=gh, 
                offset_x=ox, offset_y=oy,
                mode=self.mode_var.get(),
                output_path=self.output_path_var.get(),
                name_prefix=self.prefix_var.get()
            )

            self.status_label.config(text="Compiling...", bootstyle="info")
            self.log("Starting compilation...")
            self.update_idletasks()

            # Redirect stdout to capture compiler messages if needed, 
            # but for now we'll just call the service.
            if Exporter.export(img, self.sprites_list, options):
                self.status_label.config(text="Success!", bootstyle="success")
                self.log(f"OK: Generated {options.output_path}")
                messagebox.showinfo("Success", f"Compiled {len(self.sprites_list)} sprites to {options.output_path}")
            else:
                self.status_label.config(text="Failed", bootstyle="danger")
                self.log("ERROR: Export failed.")
        
        except Exception as e:
            self.status_label.config(text="Error", bootstyle="danger")
            self.log(f"CRITICAL ERROR: {str(e)}")
            messagebox.showerror("Error", f"Compilation failed: {str(e)}")
