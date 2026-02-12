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

def resource_path(relative_path):
    """ Get absolute path to resource, works for dev and for PyInstaller """
    try:
        # PyInstaller creates a temp folder and stores path in _MEIPASS
        base_path = sys._MEIPASS
    except Exception:
        # In development, use the project root
        # This assumes the script is in src/gui/
        base_path = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))

    return os.path.join(base_path, relative_path)

from pr32_sprite_compiler.core.exporter import Exporter
from pr32_sprite_compiler.core.models import SpriteDefinition, CompilationOptions

VERSION = "v0.3.0-dev"

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
        self.geometry("1100x850") # Wider for two-column layout
        
        self.input_path_var = tk.StringVar()
        
        # Grid & Offset Split Vars
        self.grid_w_var = tk.StringVar(value="16")
        self.grid_h_var = tk.StringVar(value="16")
        self.offset_x_var = tk.StringVar(value="0")
        self.offset_y_var = tk.StringVar(value="0")

        self.sprite_count_var = tk.StringVar()
        self.output_path_var = tk.StringVar(value="sprites.h")
        self.mode_var = tk.StringVar(value="layered")
        self.prefix_var = tk.StringVar(value="")

        # Manual Sprite Entry Vars
        self.manual_gx = tk.StringVar(value="0")
        self.manual_gy = tk.StringVar(value="0")
        self.manual_gw = tk.StringVar(value="1")
        self.manual_gh = tk.StringVar(value="1")
        
        self.sprites_list = [] # List of SpriteDefinition

        self.zoom_level = 1.0
        self.raw_image = None
        self.tk_image = None
        
        # Panning & Interaction state
        self.is_panning = False
        self.last_mouse_x = 0
        self.last_mouse_y = 0
        self.space_pressed = False

        self._setup_assets()
        self._build_layout()
        
        # Trace variables for auto-preview
        self.input_path_var.trace_add("write", lambda *args: self._update_preview())
        self.grid_w_var.trace_add("write", lambda *args: self._update_preview())
        self.grid_h_var.trace_add("write", lambda *args: self._update_preview())
        self.offset_x_var.trace_add("write", lambda *args: self._update_preview())
        self.offset_y_var.trace_add("write", lambda *args: self._update_preview())
        
    def _setup_assets(self):
        # Window icon
        logo_path = resource_path(os.path.join("assets", "pr32_logo.png"))
        if os.path.exists(logo_path):
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
        # Status Bar at the very bottom
        status_bar = tb.Frame(self)
        status_bar.pack(side=BOTTOM, fill=X)
        
        self.status_label = tb.Label(status_bar, text="Ready", bootstyle="secondary", padding=5)
        self.status_label.pack(side=LEFT)
        
        tb.Button(status_bar, text="?", bootstyle="secondary-link", 
                  command=self._show_about, padding=5).pack(side=RIGHT)

        version_label = tb.Label(status_bar, text=VERSION, bootstyle="secondary", padding=5)
        version_label.pack(side=RIGHT)

        # Main Container with two columns
        main_content = tb.Frame(self, padding=10)
        main_content.pack(fill=BOTH, expand=YES)

        # --- Sidebar (Left) ---
        sidebar = ScrolledFrame(main_content, autohide=True, width=350)
        sidebar.pack(side=LEFT, fill=Y, padx=(0, 10))

        # 1. Input Image
        card1 = self._create_card(sidebar, "Input Image")
        file_row = tb.Frame(card1)
        file_row.pack(fill=X)
        tb.Entry(file_row, textvariable=self.input_path_var).pack(side=LEFT, fill=X, expand=YES, padx=(0, 5))
        tb.Button(file_row, text="...", width=3, bootstyle="secondary-outline", command=self._browse_input).pack(side=LEFT)

        # 2. Tile Settings (Matching user image)
        card2 = self._create_card(sidebar, "Tile Settings")
        
        settings_grid = tb.Frame(card2)
        settings_grid.pack(fill=X)

        for i, (label, var) in enumerate([
            ("Tile width", self.grid_w_var),
            ("Tile height", self.grid_h_var),
            ("Tile offset X", self.offset_x_var),
            ("Tile offset Y", self.offset_y_var)
        ]):
            tb.Label(settings_grid, text=label).grid(row=i, column=0, sticky=W, pady=5, padx=(0, 10))
            tb.Spinbox(settings_grid, textvariable=var, from_=0, to=999, width=8).grid(row=i, column=1, sticky=E, pady=5)

        row_auto = tb.Frame(card2)
        row_auto.pack(fill=X, pady=(10, 0))
        tb.Label(row_auto, text="Count (per row):").pack(side=LEFT)
        tb.Entry(row_auto, textvariable=self.sprite_count_var, width=5).pack(side=LEFT, padx=5)
        tb.Button(row_auto, text="Auto-detect", bootstyle="secondary-outline", command=self._on_auto_detect_click).pack(side=RIGHT)

        # 3. Sprite Selection
        card3 = self._create_card(sidebar, "Sprite Selection")
        
        self.sprite_listbox = tk.Listbox(card3, height=6, bg="#2b2b2b", fg="white", 
                                       selectbackground="#007acc", borderwidth=1, relief="solid")
        self.sprite_listbox.pack(fill=X, pady=(0, 5))
        self.sprite_listbox.bind('<<ListboxSelect>>', self._on_listbox_select)

        manual_grid = tb.Frame(card3)
        manual_grid.pack(fill=X, pady=5)
        for i, (l, v) in enumerate([("gx:", self.manual_gx), ("gy:", self.manual_gy), ("gw:", self.manual_gw), ("gh:", self.manual_gh)]):
            tb.Label(manual_grid, text=l).grid(row=i//2, column=(i%2)*2, sticky=W, padx=(5 if i%2 else 0, 2))
            tb.Entry(manual_grid, textvariable=v, width=5).grid(row=i//2, column=(i%2)*2+1, sticky=EW, pady=2)

        btn_row = tb.Frame(card3)
        btn_row.pack(fill=X, pady=5)
        tb.Button(btn_row, text="Add/Update", bootstyle="primary", command=self._on_add_sprite, width=12).pack(side=LEFT, expand=YES, padx=2)
        tb.Button(btn_row, text="Remove", bootstyle="secondary-outline", command=self._on_remove_sprite).pack(side=LEFT, padx=2)
        tb.Button(btn_row, text="Clear", bootstyle="secondary-outline", command=self._on_clear_sprites).pack(side=LEFT, padx=2)

        # --- Main Area (Right) ---
        right_area = tb.Frame(main_content)
        right_area.pack(side=LEFT, fill=BOTH, expand=YES)

        # Preview
        self.preview_card = self._create_card(right_area, "Sprite Sheet Preview")
        
        preview_controls = tb.Frame(self.preview_card)
        preview_controls.pack(fill=X, pady=(0, 10))
        
        tb.Button(preview_controls, text="🔍+", width=3, bootstyle="secondary-outline", 
                  command=lambda: self._adjust_zoom(0.2)).pack(side=LEFT, padx=2)
        tb.Button(preview_controls, text="🔍-", width=3, bootstyle="secondary-outline", 
                  command=lambda: self._adjust_zoom(-0.2)).pack(side=LEFT, padx=2)
        
        self.zoom_label = tb.Label(preview_controls, text="100%", bootstyle="secondary", padding=(10, 0))
        self.zoom_label.pack(side=LEFT)

        canvas_container = tb.Frame(self.preview_card)
        canvas_container.pack(fill=BOTH, expand=YES)
        
        self.preview_canvas = tk.Canvas(canvas_container, bg="#454545",
                                      highlightthickness=0, borderwidth=0)
        self.preview_canvas.pack(side=LEFT, fill=BOTH, expand=YES)

        # Canvas Interaction Binds
        self.preview_canvas.bind("<MouseWheel>", self._on_mouse_zoom)
        self.preview_canvas.bind("<ButtonPress-1>", self._on_pan_start)
        self.preview_canvas.bind("<B1-Motion>", self._on_pan_move)
        self.preview_canvas.bind("<ButtonRelease-1>", self._on_pan_stop)

        # Keyboard binds for Space (Panning)
        self.bind("<KeyPress-space>", self._on_space_press)
        self.bind("<KeyRelease-space>", self._on_space_release)

        # Ensure canvas can receive focus for keyboard events
        self.preview_canvas.config(takefocus=True)
        self.preview_canvas.bind("<Enter>", lambda e: self.preview_canvas.focus_set())

        # 4. Export (Moved and Redesigned for UX)
        card4 = self._create_card(right_area, "Export")
        
        export_form = tb.Frame(card4)
        export_form.pack(fill=X, pady=5)

        # Row 1: Mode & Prefix
        row1 = tb.Frame(export_form)
        row1.pack(fill=X, pady=5)
        
        mode_frame = tb.Frame(row1)
        mode_frame.pack(side=LEFT, fill=X, expand=YES, padx=(0, 10))
        tb.Label(mode_frame, text="Mode:").pack(anchor=W)
        tb.Combobox(mode_frame, textvariable=self.mode_var, values=["layered", "2bpp", "4bpp"], state="readonly").pack(fill=X)
        
        prefix_frame = tb.Frame(row1)
        prefix_frame.pack(side=LEFT, fill=X, expand=YES)
        tb.Label(prefix_frame, text="Prefix:").pack(anchor=W)
        tb.Entry(prefix_frame, textvariable=self.prefix_var).pack(fill=X)

        # Row 2: Output
        row2 = tb.Frame(export_form)
        row2.pack(fill=X, pady=5)
        tb.Label(row2, text="Output File:").pack(anchor=W)
        out_row = tb.Frame(row2)
        out_row.pack(fill=X)
        tb.Entry(out_row, textvariable=self.output_path_var).pack(side=LEFT, fill=X, expand=YES, padx=(0, 5))
        tb.Button(out_row, text="...", width=3, bootstyle="secondary-outline", command=self._browse_output).pack(side=LEFT)

        # Big Export Button
        tb.Button(card4, text="Export Sprites", bootstyle="info", 
                  command=self._on_compile, padding=(0, 15)).pack(fill=X, pady=(15, 5))

        # Log
        card_log = self._create_card(right_area, "Log")
        self.log_area = ScrolledText(card_log, height=6, autohide=True, bootstyle="dark")
        self.log_area.pack(fill=BOTH, expand=YES)
        self.log("Ready...")

    # --- UI Logic ---

    def _show_about(self):
        about = AboutPanel(self)
        about.show()

    def _adjust_zoom(self, delta):
        self.zoom_level = max(0.1, min(10.0, self.zoom_level + delta))
        self.zoom_label.config(text=f"{int(self.zoom_level * 100)}%")
        self._update_preview()

    def _on_mouse_zoom(self, event):
        """Zoom with mouse wheel."""
        delta = 0.1 if event.delta > 0 else -0.1
        self._adjust_zoom(delta)

    def _on_space_press(self, event):
        self.space_pressed = True
        self.preview_canvas.config(cursor="fleur")

    def _on_space_release(self, event):
        self.space_pressed = False
        self.preview_canvas.config(cursor="")

    def _on_pan_start(self, event):
        """Start panning if space is pressed."""
        if self.space_pressed:
            self.is_panning = True
            self.preview_canvas.scan_mark(event.x, event.y)

    def _on_pan_move(self, event):
        """Pan the canvas."""
        if self.is_panning:
            self.preview_canvas.scan_dragto(event.x, event.y, gain=1)

    def _on_pan_stop(self, event):
        """Stop panning."""
        self.is_panning = False

    def _update_preview(self):
        input_path = self.input_path_var.get()
        if not input_path or not os.path.exists(input_path):
            self.preview_canvas.delete("all")
            return

        try:
            # Load image if not already loaded or if path changed
            if not self.raw_image or getattr(self, '_last_path', None) != input_path:
                self.raw_image = Image.open(input_path).convert("RGBA")
                self._last_path = input_path

            # Scale image
            w, h = self.raw_image.size
            sw, sh = int(w * self.zoom_level), int(h * self.zoom_level)
            
            # Optimization: only resize if dimensions changed
            resized = self.raw_image.resize((sw, sh), Image.NEAREST)
            self.tk_image = ImageTk.PhotoImage(resized)

            self.preview_canvas.delete("all")
            self.preview_canvas.create_image(0, 0, anchor=NW, image=self.tk_image)
            self.preview_canvas.config(scrollregion=(0, 0, sw, sh))

            # Draw grid
            try:
                gw = int(self.grid_w_var.get())
                gh = int(self.grid_h_var.get())
                ox = int(self.offset_x_var.get())
                oy = int(self.offset_y_var.get())
            except:
                gw, gh = 16, 16
                ox, oy = 0, 0

            # Scale grid parameters
            sgw, sgh = gw * self.zoom_level, gh * self.zoom_level
            sox, soy = ox * self.zoom_level, oy * self.zoom_level

            # Draw vertical lines
            if sgw > 0:
                for x in range(int(sox), sw, int(sgw)):
                    self.preview_canvas.create_line(x, 0, x, sh, fill="#444444", dash=(2, 2))
            
            # Draw horizontal lines
            if sgh > 0:
                for y in range(int(soy), sh, int(sgh)):
                    self.preview_canvas.create_line(0, y, sw, y, fill="#444444", dash=(2, 2))

            # Draw sprites
            selection = self.sprite_listbox.curselection()
            selected_idx = selection[0] if selection else -1

            for i, s in enumerate(self.sprites_list):
                sx = sox + (s.gx * sgw)
                sy = soy + (s.gy * sgh)
                sww = s.gw * sgw
                shh = s.gh * sgh
                
                color = "red" if i == selected_idx else "cyan"
                width = 2 if i == selected_idx else 1
                
                self.preview_canvas.create_rectangle(sx, sy, sx + sww, sy + shh, 
                                                   outline=color, width=width)
                if i == selected_idx:
                    # Draw a semi-transparent fill for selection
                    self.preview_canvas.create_rectangle(sx, sy, sx + sww, sy + shh, 
                                                       fill=color, stipple="gray25", outline="")

        except Exception as e:
            self.log(f"Preview error: {e}", "warning")

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
            
            self._update_preview()
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
            self._update_preview()

    def _on_clear_sprites(self):
        self.sprite_listbox.delete(0, END)
        self.sprites_list = []
        self._update_preview()

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
            self._update_preview()

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
                gw = int(self.grid_w_var.get())
                gh = int(self.grid_h_var.get())
            except:
                gw, gh = 16, 16
                self.grid_w_var.set("16")
                self.grid_h_var.set("16")

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
            self._update_preview()
            
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
            gw = int(self.grid_w_var.get())
            gh = int(self.grid_h_var.get())
            ox = int(self.offset_x_var.get())
            oy = int(self.offset_y_var.get())
            
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
