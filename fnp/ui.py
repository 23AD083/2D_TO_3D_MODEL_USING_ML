#!/usr/bin/env python3
"""
Simple Tkinter GUI for 2D to 3D Building Blueprint Converter
"""

import tkinter as tk
from tkinter import filedialog, messagebox, ttk
import threading
import sys
import os
from pathlib import Path
from PIL import Image, ImageTk, ImageDraw
import subprocess
import json

# Import main functionality
import main as main_module


class BlueprintConverterGUI:
    def __init__(self, root):
        self.root = root
        self.root.title("2D to 3D Building Blueprint Converter")
        self.root.geometry("1400x900")
        
        # Make fullscreen
        self.root.state('zoomed')  # Windows fullscreen
        
        # Variables
        self.input_file = tk.StringVar()
        self.output_dir = tk.StringVar(value="output")
        self.height = tk.DoubleVar(value=3.5)
        self.scale = tk.DoubleVar(value=100.0)
        self.wall_thickness = tk.DoubleVar(value=0.2)
        self.stair_width = tk.DoubleVar(value=1.2)
        self.show_furniture = tk.BooleanVar(value=True)
        self.show_map = tk.BooleanVar(value=False)
        self.map_file = tk.StringVar()
        self.skip_blender = tk.BooleanVar(value=False)
        
        self.create_widgets()
        
    def create_widgets(self):
        # Use a horizontal paned layout: left controls, right preview
        paned = ttk.Panedwindow(self.root, orient=tk.HORIZONTAL)
        paned.pack(fill=tk.BOTH, expand=True)

        controls = ttk.Frame(paned, width=420, padding=12)
        preview = ttk.Frame(paned, padding=12)
        paned.add(controls, weight=1)
        paned.add(preview, weight=3)

        # Controls (left)
        row = 0
        title = ttk.Label(controls, text="2D → 3D Converter", font=("Segoe UI", 18, "bold"))
        title.grid(row=row, column=0, columnspan=3, pady=(0, 12), sticky=tk.W)
        row += 1

        ttk.Label(controls, text="Blueprint File:").grid(row=row, column=0, sticky=tk.W, pady=4)
        ttk.Entry(controls, textvariable=self.input_file, width=30).grid(row=row, column=1, sticky=(tk.W, tk.E))
        ttk.Button(controls, text="Browse", command=self.browse_input).grid(row=row, column=2, padx=6)
        row += 1

        ttk.Label(controls, text="Output Directory:").grid(row=row, column=0, sticky=tk.W, pady=4)
        ttk.Entry(controls, textvariable=self.output_dir, width=24).grid(row=row, column=1, sticky=(tk.W, tk.E))
        ttk.Button(controls, text="Browse", command=self.browse_output).grid(row=row, column=2, padx=6)
        row += 1

        self.output_path_label = ttk.Label(controls, text=f"📁 Path: {Path(self.output_dir.get()).resolve()}", foreground="#666")
        self.output_path_label.grid(row=row, column=0, columnspan=3, sticky=tk.W, pady=(2,8))
        self.output_dir.trace('w', self.update_output_path_label)
        row += 1

        # Parameters
        ttk.Separator(controls, orient='horizontal').grid(row=row, column=0, columnspan=3, sticky=(tk.W, tk.E), pady=8)
        row += 1

        ttk.Label(controls, text="Height (m):").grid(row=row, column=0, sticky=tk.W)
        ttk.Spinbox(controls, from_=1.0, to=50.0, textvariable=self.height, width=10).grid(row=row, column=1, sticky=tk.W)
        row += 1

        ttk.Label(controls, text="Pixels / Meter:").grid(row=row, column=0, sticky=tk.W)
        ttk.Spinbox(controls, from_=10, to=800, textvariable=self.scale, width=10).grid(row=row, column=1, sticky=tk.W)
        row += 1

        ttk.Label(controls, text="Wall thickness (m):").grid(row=row, column=0, sticky=tk.W)
        ttk.Spinbox(controls, from_=0.05, to=2.0, increment=0.01, textvariable=self.wall_thickness, width=10).grid(row=row, column=1, sticky=tk.W)
        row += 1

        ttk.Label(controls, text="Stair width (m):").grid(row=row, column=0, sticky=tk.W)
        ttk.Spinbox(controls, from_=0.5, to=3.0, increment=0.1, textvariable=self.stair_width, width=10).grid(row=row, column=1, sticky=tk.W)
        row += 1

        # Options
        ttk.Separator(controls, orient='horizontal').grid(row=row, column=0, columnspan=3, sticky=(tk.W, tk.E), pady=8)
        row += 1
        ttk.Checkbutton(controls, text="Generate Furniture", variable=self.show_furniture).grid(row=row, column=0, columnspan=2, sticky=tk.W)
        row += 1
        ttk.Checkbutton(controls, text="Skip Blender (save plan only)", variable=self.skip_blender).grid(row=row, column=0, columnspan=2, sticky=tk.W)
        row += 1
        ttk.Checkbutton(controls, text="Show Map Overlay", variable=self.show_map, command=self.toggle_map_input).grid(row=row, column=0, columnspan=2, sticky=tk.W)
        row += 1

        # Map input
        self.map_frame = ttk.Frame(controls)
        ttk.Label(self.map_frame, text="Map File:").grid(row=0, column=0, sticky=tk.W)
        ttk.Entry(self.map_frame, textvariable=self.map_file, width=20).grid(row=0, column=1, sticky=(tk.W, tk.E))
        ttk.Button(self.map_frame, text="Browse", command=self.browse_map).grid(row=0, column=2)
        self.map_frame.grid(row=row, column=0, columnspan=3, sticky=(tk.W, tk.E), pady=4)
        self.map_frame.grid_remove()
        row += 1

        # Action buttons
        ttk.Separator(controls, orient='horizontal').grid(row=row, column=0, columnspan=3, sticky=(tk.W, tk.E), pady=8)
        row += 1

        btn_frame = ttk.Frame(controls)
        btn_frame.grid(row=row, column=0, columnspan=3, pady=6)
        self.convert_button = ttk.Button(btn_frame, text="Convert", command=self.start_conversion)
        self.convert_button.pack(side=tk.LEFT, padx=6)
        self.report_button = ttk.Button(btn_frame, text="Open Report", command=self.open_report, state='disabled')
        self.report_button.pack(side=tk.LEFT, padx=6)
        ttk.Button(btn_frame, text="Generate Samples", command=self.generate_samples).pack(side=tk.LEFT, padx=6)
        ttk.Button(btn_frame, text="Exit", command=self.root.quit).pack(side=tk.LEFT, padx=6)
        row += 1

        # Status & progress
        self.progress = ttk.Progressbar(controls, mode='indeterminate')
        self.progress.grid(row=row, column=0, columnspan=3, sticky=(tk.W, tk.E), pady=8)
        row += 1
        self.status_label = ttk.Label(controls, text="Ready", foreground="green")
        self.status_label.grid(row=row, column=0, columnspan=3, sticky=tk.W)

        # Preview (right)
        preview_title = ttk.Label(preview, text="Preview & Sketch", font=("Segoe UI", 14, "bold"))
        preview_title.pack(anchor=tk.W)
        self.canvas = tk.Canvas(preview, bg="#ffffff")
        self.canvas.pack(fill=tk.BOTH, expand=True, padx=8, pady=8)
        self.preview_image = None
        
        # Initial preview update
        self.root.after(200, self.update_preview)
        
    def browse_input(self):
        filename = filedialog.askopenfilename(
            title="Select Blueprint File",
            filetypes=[
                ("Image files", "*.png *.jpg *.jpeg *.bmp"),
                ("DXF files", "*.dxf"),
                ("All files", "*.*")
            ]
        )
        if filename:
            self.input_file.set(filename)
            
    def browse_output(self):
        dirname = filedialog.askdirectory(title="Select Output Directory")
        if dirname:
            self.output_dir.set(dirname)
            
    def browse_map(self):
        filename = filedialog.askopenfilename(
            title="Select Map File",
            filetypes=[("MBTiles", "*.mbtiles"), ("All files", "*.*")]
        )
        if filename:
            self.map_file.set(filename)
            
    def toggle_map_input(self):
        if self.show_map.get():
            self.map_frame.grid()
        else:
            self.map_frame.grid_remove()
            
    def start_conversion(self):
        if not self.input_file.get():
            messagebox.showerror("Error", "Please select a blueprint file")
            return
            
        # Disable button and start progress
        self.convert_button.config(state='disabled')
        self.progress.start()
        self.status_label.config(text="Processing...", foreground="blue")
        
        # Run conversion in separate thread
        thread = threading.Thread(target=self.run_conversion)
        thread.daemon = True
        thread.start()
        
    def run_conversion(self):
        try:
            # Build arguments
            sys.argv = [
                'main.py',
                '--input', self.input_file.get(),
                '--output', self.output_dir.get(),
                '--height', str(self.height.get()),
                '--scale', str(self.scale.get()),
                '--wall-thickness', str(self.wall_thickness.get()),
                '--stair-width', str(self.stair_width.get())
            ]
            
            if not self.show_furniture.get():
                sys.argv.append('--no-furniture')
            
            if self.skip_blender.get():
                sys.argv.append('--no-blender')
                
            if self.show_map.get() and self.map_file.get():
                sys.argv.extend(['--map', self.map_file.get()])
                
            # Run main conversion
            result = main_module.main()
            
            # Update UI in main thread
            self.root.after(0, self.conversion_complete, result == 0)
            
        except Exception as e:
            self.root.after(0, self.conversion_error, str(e))
            
    def conversion_complete(self, success):
        self.progress.stop()
        self.convert_button.config(state='normal')
        
        if success:
            self.status_label.config(text="Conversion complete!", foreground="green")
            self.report_button.config(state='normal')
            # Refresh the preview to show the newly generated plan
            try:
                self.root.after(100, self.update_preview)
            except Exception:
                pass
            msg = f"3D model generated in:\n{self.output_dir.get()}"
            if self.skip_blender.get():
                msg += "\n\nClick 'Open Report' to view the blueprint."
            messagebox.showinfo("Success", msg)
        else:
            self.status_label.config(text="Conversion failed", foreground="red")
            self.report_button.config(state='disabled')
            messagebox.showerror("Error", "Conversion failed. Check console for details.")
            
    def conversion_error(self, error_msg):
        self.progress.stop()
        self.convert_button.config(state='normal')
        self.report_button.config(state='disabled')
        self.status_label.config(text="Error occurred", foreground="red")
        messagebox.showerror("Error", f"An error occurred:\n{error_msg}")
    
    def open_report(self):
        import webbrowser
        report_path = Path(self.output_dir.get()) / 'report.html'
        if report_path.exists():
            webbrowser.open(f'file://{report_path.resolve()}')
        else:
            messagebox.showerror("Error", f"Report not found at:\n{report_path}")
    
    def update_output_path_label(self, *args):
        """Update the output path label when directory changes."""
        output_dir = Path(self.output_dir.get())
        abs_path = output_dir.resolve()
        self.output_path_label.config(text=f"📁 Path: {abs_path}")

    def generate_samples(self):
        """Run the sample blueprint generator to create multiple sample inputs."""
        try:
            script = Path(__file__).parent / 'generate_sample_blueprints.py'
            result = subprocess.run(['py', str(script)], capture_output=True, text=True, timeout=60)
            if result.returncode == 0:
                messagebox.showinfo('Samples Created', 'Sample blueprints generated in sample_input/')
            else:
                messagebox.showwarning('Generate Samples', f'Generator returned non-zero:\n{result.stderr}')
        except Exception as e:
            messagebox.showerror('Error', f'Failed to generate samples:\n{e}')

    def update_preview(self):
        """Update the right-hand preview canvas with the input image or an interpreted sketch from plan.json."""
        try:
            out_dir = Path(self.output_dir.get())
            plan_path = out_dir / 'plan.json'
            if plan_path.exists():
                with open(plan_path, 'r') as f:
                    plan = json.load(f)
                # Render a sketch from plan polygons
                # Determine bounds
                polys = plan.get('walls', []) or plan.get('rooms', [])
                if not polys:
                    # show input image
                    self._show_input_image()
                    return

                # Compute bounds
                xs = [p[0] for poly in polys for p in poly]
                ys = [p[1] for poly in polys for p in poly]
                minx, maxx = min(xs), max(xs)
                miny, maxy = min(ys), max(ys)
                width = int((maxx - minx) * self.scale.get()) + 40
                height = int((maxy - miny) * self.scale.get()) + 40

                img = Image.new('RGBA', (max(320, width), max(240, height)), (250, 250, 250, 255))
                draw = ImageDraw.Draw(img)

                # draw floor
                draw.rectangle([0,0,img.width,img.height], fill=(245,245,245))

                def to_px(pt):
                    x, y = pt
                    px = int((x - minx) * self.scale.get()) + 20
                    py = int((maxy - y) * self.scale.get()) + 20
                    return (px, py)

                # Draw polygons with pseudo-3D effect (offset shadow)
                for poly in polys:
                    pts = [to_px(p) for p in poly]
                    # offset for height
                    offset = int(self.height.get() * 4)
                    shadow = [(x+offset, y-offset) for (x,y) in pts]
                    draw.polygon(shadow, fill=(200,200,200,180))
                    draw.polygon(pts, fill=(220,240,255), outline=(30,80,120))

                # Convert to Tk image and display
                self.preview_image = ImageTk.PhotoImage(img)
                self.canvas.delete('all')
                self.canvas.create_image(0, 0, anchor='nw', image=self.preview_image)
                self.canvas.config(scrollregion=self.canvas.bbox(tk.ALL))
            else:
                self._show_input_image()
        except Exception as e:
            print('Preview error:', e)

    def _show_input_image(self):
        try:
            inp = self.input_file.get()
            if not inp:
                return
            img = Image.open(inp)
            # fit to canvas
            cw = max(400, self.canvas.winfo_width() or 600)
            ch = max(300, self.canvas.winfo_height() or 400)
            img.thumbnail((cw, ch), Image.ANTIALIAS)
            self.preview_image = ImageTk.PhotoImage(img)
            self.canvas.delete('all')
            self.canvas.create_image(10, 10, anchor='nw', image=self.preview_image)
        except Exception:
            pass


def launch_ui():
    """Launch the GUI application."""
    root = tk.Tk()
    app = BlueprintConverterGUI(root)
    root.mainloop()


if __name__ == '__main__':
    launch_ui()
