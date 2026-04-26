import os
import tkinter as tk
from tkinter import filedialog, messagebox, ttk
from typing import Optional, Tuple

from PIL import Image, ImageTk


IMAGE_TYPES = [("Image Files", (".jpg", ".jpeg", ".png"))]


class LogoAdderApp:
    def __init__(self, root: tk.Tk) -> None:
        self.root = root
        self.root.title("Logo Adder")
        self.root.geometry("1020x700")
        self.root.minsize(980, 620)

        self.logo_path: Optional[str] = None
        self.logo_image: Optional[Image.Image] = None
        self.preview_image_path: Optional[str] = None
        self.preview_image: Optional[Image.Image] = None

        self.logo_preview_tk: Optional[ImageTk.PhotoImage] = None
        self.canvas_main_tk: Optional[ImageTk.PhotoImage] = None
        self.canvas_logo_tk: Optional[ImageTk.PhotoImage] = None

        self.width_var = tk.StringVar()
        self.height_var = tk.StringVar()
        self.logo_size_percent_var = tk.DoubleVar(value=20.0)
        self.status_var = tk.StringVar(value="Select a logo to get started.")

        self.logo_rel_x = 0.0
        self.logo_rel_y = 0.0
        self.logo_dragging = False
        self.drag_offset_x = 0
        self.drag_offset_y = 0
        self.logo_bbox_canvas: Optional[Tuple[int, int, int, int]] = None
        self.canvas_image_bounds: Optional[Tuple[int, int, int, int]] = None
        self.logo_display_state: Optional[Tuple[int, int, int, int, int, int]] = None

        self._build_ui()

    def _build_ui(self) -> None:
        container = ttk.Frame(self.root, padding=16)
        container.pack(fill="both", expand=True)
        container.columnconfigure(0, weight=1)
        container.rowconfigure(4, weight=1)

        title = ttk.Label(container, text="Logo Adder", font=("TkDefaultFont", 16, "bold"))
        title.grid(row=0, column=0, sticky="w")

        subtitle = ttk.Label(
            container,
            text="Choose a logo once, then process one image or many at once.",
        )
        subtitle.grid(row=1, column=0, sticky="w", pady=(4, 12))

        settings_frame = ttk.LabelFrame(container, text="Output Resize Settings (Optional)", padding=12)
        settings_frame.grid(row=2, column=0, sticky="ew", pady=(0, 12))
        settings_frame.columnconfigure(0, weight=1)
        settings_frame.columnconfigure(1, weight=1)

        ttk.Label(settings_frame, text="Width (px)").grid(row=0, column=0, sticky="w")
        ttk.Entry(settings_frame, textvariable=self.width_var).grid(
            row=1, column=0, sticky="ew", padx=(0, 8)
        )

        ttk.Label(settings_frame, text="Height (px)").grid(row=0, column=1, sticky="w")
        ttk.Entry(settings_frame, textvariable=self.height_var).grid(
            row=1, column=1, sticky="ew", padx=(8, 0)
        )

        ttk.Label(
            settings_frame,
            text="Tip: Fill both for exact size, or only one value to keep aspect ratio.",
        ).grid(row=2, column=0, columnspan=2, sticky="w", pady=(8, 0))

        buttons = ttk.Frame(container)
        buttons.grid(row=3, column=0, sticky="ew", pady=(0, 12))
        buttons.columnconfigure(0, weight=1)
        buttons.columnconfigure(1, weight=1)
        buttons.columnconfigure(2, weight=1)
        buttons.columnconfigure(3, weight=1)
        buttons.columnconfigure(4, weight=1)

        ttk.Button(buttons, text="1) Select Logo", command=self.select_logo).grid(
            row=0, column=0, sticky="ew", padx=(0, 6)
        )
        ttk.Button(buttons, text="2) Load Preview Image", command=self.select_preview_image).grid(
            row=0, column=1, sticky="ew", padx=6
        )
        ttk.Button(buttons, text="3) Add to One Image", command=self.add_to_single_image).grid(
            row=0, column=2, sticky="ew", padx=6
        )
        ttk.Button(buttons, text="4) Add to Multiple Images", command=self.add_to_multiple_images).grid(
            row=0, column=3, sticky="ew", padx=6
        )
        ttk.Button(buttons, text="Quit", command=self.root.quit).grid(
            row=0, column=4, sticky="ew", padx=(6, 0)
        )

        preview_area = ttk.Frame(container)
        preview_area.grid(row=4, column=0, sticky="nsew")
        preview_area.columnconfigure(0, weight=0)
        preview_area.columnconfigure(1, weight=1)
        preview_area.rowconfigure(0, weight=1)

        logo_box = ttk.LabelFrame(preview_area, text="Logo Preview", padding=10)
        logo_box.grid(row=0, column=0, sticky="nsew", padx=(0, 6))
        logo_box.columnconfigure(0, weight=0)
        logo_box.rowconfigure(0, weight=1)
        self.logo_preview_label = ttk.Label(logo_box, anchor="center")
        self.logo_preview_label.configure(text="No logo selected")
        self.logo_preview_label.grid(row=0, column=0, sticky="nsew")

        main_box = ttk.LabelFrame(
            preview_area,
            text="Interactive Preview (Drag logo to move it)",
            padding=10,
        )
        main_box.grid(row=0, column=1, sticky="nsew", padx=(6, 0))
        main_box.columnconfigure(0, weight=1)
        main_box.rowconfigure(1, weight=1)

        control_row = ttk.Frame(main_box)
        control_row.grid(row=0, column=0, sticky="ew", pady=(0, 8))
        control_row.columnconfigure(1, weight=1)
        ttk.Label(control_row, text="Logo size (% of image height):").grid(row=0, column=0, sticky="w")
        ttk.Scale(
            control_row,
            from_=5,
            to=60,
            variable=self.logo_size_percent_var,
            command=self._on_logo_size_changed,
        ).grid(row=0, column=1, sticky="ew", padx=(8, 8))
        self.logo_size_value_label = ttk.Label(control_row, text="20%")
        self.logo_size_value_label.grid(row=0, column=2, sticky="e")

        self.preview_canvas = tk.Canvas(main_box, bg="#f2f2f2", highlightthickness=0)
        self.preview_canvas.grid(row=1, column=0, sticky="nsew")
        self.preview_canvas.bind("<Configure>", self._on_canvas_resized)
        self.preview_canvas.bind("<ButtonPress-1>", self._on_canvas_press)
        self.preview_canvas.bind("<B1-Motion>", self._on_canvas_drag)
        self.preview_canvas.bind("<ButtonRelease-1>", self._on_canvas_release)

        status = ttk.Label(container, textvariable=self.status_var)
        status.grid(row=5, column=0, sticky="w", pady=(12, 0))

    def _parse_target_size(self) -> Optional[Tuple[Optional[int], Optional[int]]]:
        width_text = self.width_var.get().strip()
        height_text = self.height_var.get().strip()

        width = None
        height = None

        if width_text:
            if not width_text.isdigit() or int(width_text) <= 0:
                messagebox.showerror("Invalid Width", "Width must be a positive whole number.")
                return None
            width = int(width_text)

        if height_text:
            if not height_text.isdigit() or int(height_text) <= 0:
                messagebox.showerror("Invalid Height", "Height must be a positive whole number.")
                return None
            height = int(height_text)

        return width, height

    def _resize_with_aspect_ratio(
        self, image: Image.Image, target_width: Optional[int], target_height: Optional[int]
    ) -> Image.Image:
        if target_width and target_height:
            return image.resize((target_width, target_height), Image.LANCZOS)

        if target_width:
            ratio = target_width / float(image.width)
            new_height = int(image.height * ratio)
            return image.resize((target_width, new_height), Image.LANCZOS)

        if target_height:
            ratio = target_height / float(image.height)
            new_width = int(image.width * ratio)
            return image.resize((new_width, target_height), Image.LANCZOS)

        return image

    def _render_small_preview(self, pil_image: Image.Image, label: ttk.Label, max_size: Tuple[int, int]) -> None:
        preview = pil_image.copy()
        preview.thumbnail(max_size, Image.LANCZOS)
        preview_tk = ImageTk.PhotoImage(preview)
        label.configure(image=preview_tk, text="")
        self.logo_preview_tk = preview_tk

    def select_logo(self) -> None:
        logo_path = filedialog.askopenfilename(title="Select Logo", filetypes=IMAGE_TYPES)
        if not logo_path:
            return

        try:
            logo = Image.open(logo_path)
            logo.load()
        except Exception as exc:  # pylint: disable=broad-except
            messagebox.showerror("Error", f"Could not open logo:\n{exc}")
            return

        self.logo_path = logo_path
        self.logo_image = logo
        self._render_small_preview(logo, self.logo_preview_label, (280, 280))
        self._refresh_preview_canvas()
        self.status_var.set(f"Logo selected: {os.path.basename(logo_path)}")

    def select_preview_image(self) -> None:
        preview_path = filedialog.askopenfilename(title="Select Preview Image", filetypes=IMAGE_TYPES)
        if not preview_path:
            return
        self._load_preview_image(preview_path)

    def _load_preview_image(self, image_path: str) -> bool:
        try:
            preview = Image.open(image_path)
            preview.load()
        except Exception as exc:
            messagebox.showerror("Error", f"Could not open preview image:\n{exc}")
            return False

        self.preview_image_path = image_path
        self.preview_image = preview
        self._refresh_preview_canvas()
        self.status_var.set(
            f"Preview image loaded: {os.path.basename(image_path)}. Drag logo on the canvas to place it."
        )
        return True

    def _on_logo_size_changed(self, _event: str) -> None:
        self.logo_size_value_label.configure(text=f"{int(self.logo_size_percent_var.get())}%")
        self._refresh_preview_canvas()

    def _on_canvas_resized(self, _event: tk.Event) -> None:
        self._refresh_preview_canvas()

    def _on_canvas_press(self, event: tk.Event) -> None:
        if not self.logo_bbox_canvas:
            self.logo_dragging = False
            return

        left, top, right, bottom = self.logo_bbox_canvas
        if left <= event.x <= right and top <= event.y <= bottom:
            self.logo_dragging = True
            self.drag_offset_x = event.x - left
            self.drag_offset_y = event.y - top
        else:
            self.logo_dragging = False

    def _on_canvas_drag(self, event: tk.Event) -> None:
        if not self.logo_dragging:
            return
        if not self.canvas_image_bounds or not self.logo_display_state:
            return

        image_left, image_top, _, _ = self.canvas_image_bounds
        _, _, _, _, max_x, max_y = self.logo_display_state

        local_x = event.x - image_left - self.drag_offset_x
        local_y = event.y - image_top - self.drag_offset_y
        local_x = max(0, min(local_x, max_x))
        local_y = max(0, min(local_y, max_y))

        self.logo_rel_x = 0.0 if max_x == 0 else local_x / float(max_x)
        self.logo_rel_y = 0.0 if max_y == 0 else local_y / float(max_y)
        self._refresh_preview_canvas()

    def _on_canvas_release(self, _event: tk.Event) -> None:
        self.logo_dragging = False

    def _refresh_preview_canvas(self) -> None:
        self.preview_canvas.delete("all")

        canvas_w = self.preview_canvas.winfo_width()
        canvas_h = self.preview_canvas.winfo_height()
        if canvas_w <= 1 or canvas_h <= 1:
            return

        if not self.preview_image:
            self.preview_canvas.create_text(
                canvas_w // 2,
                canvas_h // 2,
                text="Load a preview image to position your logo",
                fill="#666666",
                font=("TkDefaultFont", 12),
            )
            self.logo_bbox_canvas = None
            self.canvas_image_bounds = None
            self.logo_display_state = None
            return

        margin = 20
        scale = min(
            (canvas_w - margin * 2) / float(self.preview_image.width),
            (canvas_h - margin * 2) / float(self.preview_image.height),
        )
        scale = max(scale, 0.05)

        display_w = max(1, int(self.preview_image.width * scale))
        display_h = max(1, int(self.preview_image.height * scale))
        offset_x = (canvas_w - display_w) // 2
        offset_y = (canvas_h - display_h) // 2
        self.canvas_image_bounds = (offset_x, offset_y, display_w, display_h)

        preview_main = self.preview_image.resize((display_w, display_h), Image.LANCZOS).convert("RGB")
        self.canvas_main_tk = ImageTk.PhotoImage(preview_main)
        self.preview_canvas.create_image(offset_x, offset_y, anchor="nw", image=self.canvas_main_tk)
        self.preview_canvas.create_rectangle(
            offset_x, offset_y, offset_x + display_w, offset_y + display_h, outline="#999999"
        )

        if not self.logo_image:
            self.logo_bbox_canvas = None
            self.logo_display_state = None
            return

        logo_h = max(1, int(display_h * (self.logo_size_percent_var.get() / 100.0)))
        logo_ratio = self.logo_image.width / float(self.logo_image.height)
        logo_w = max(1, int(logo_h * logo_ratio))

        max_x = max(0, display_w - logo_w)
        max_y = max(0, display_h - logo_h)

        logo_x = 0 if max_x == 0 else int(self.logo_rel_x * max_x)
        logo_y = 0 if max_y == 0 else int(self.logo_rel_y * max_y)

        logo_x = max(0, min(logo_x, max_x))
        logo_y = max(0, min(logo_y, max_y))

        self.logo_rel_x = 0.0 if max_x == 0 else logo_x / float(max_x)
        self.logo_rel_y = 0.0 if max_y == 0 else logo_y / float(max_y)
        self.logo_display_state = (logo_x, logo_y, logo_w, logo_h, max_x, max_y)

        logo_resized = self.logo_image.resize((logo_w, logo_h), Image.LANCZOS).convert("RGBA")
        self.canvas_logo_tk = ImageTk.PhotoImage(logo_resized)

        abs_x = offset_x + logo_x
        abs_y = offset_y + logo_y
        self.preview_canvas.create_image(abs_x, abs_y, anchor="nw", image=self.canvas_logo_tk)
        self.preview_canvas.create_rectangle(
            abs_x, abs_y, abs_x + logo_w, abs_y + logo_h, outline="#0078D4", width=2
        )
        self.logo_bbox_canvas = (abs_x, abs_y, abs_x + logo_w, abs_y + logo_h)

    def _build_merged_image(self, main_image_path: str) -> Optional[Image.Image]:
        if not self.logo_image:
            messagebox.showwarning("No Logo Selected", "Please select a logo first.")
            return None

        size_values = self._parse_target_size()
        if size_values is None:
            return None

        target_width, target_height = size_values

        try:
            main_image = Image.open(main_image_path)
            main_image.load()
        except Exception as exc:  # pylint: disable=broad-except
            messagebox.showerror("Error", f"Could not open image:\n{exc}")
            return None

        main_image = self._resize_with_aspect_ratio(main_image, target_width, target_height)

        logo_new_height = max(1, int(main_image.height * (self.logo_size_percent_var.get() / 100.0)))
        logo_aspect_ratio = self.logo_image.width / self.logo_image.height
        logo_new_width = max(1, int(logo_new_height * logo_aspect_ratio))
        logo_resized = self.logo_image.resize((logo_new_width, logo_new_height), Image.LANCZOS)

        merged = main_image.convert("RGBA")
        if logo_resized.mode not in ("RGBA", "LA"):
            logo_resized = logo_resized.convert("RGBA")

        max_x = max(0, merged.width - logo_new_width)
        max_y = max(0, merged.height - logo_new_height)
        paste_x = 0 if max_x == 0 else int(self.logo_rel_x * max_x)
        paste_y = 0 if max_y == 0 else int(self.logo_rel_y * max_y)
        merged.paste(logo_resized, (paste_x, paste_y), logo_resized)
        return merged.convert("RGB")

    def add_to_single_image(self) -> None:
        if not self.logo_image:
            messagebox.showwarning("No Logo Selected", "Please select a logo first.")
            return

        main_image_path = filedialog.askopenfilename(title="Select Main Image", filetypes=IMAGE_TYPES)
        if not main_image_path:
            return

        if not self.preview_image:
            self._load_preview_image(main_image_path)

        merged = self._build_merged_image(main_image_path)
        if merged is None:
            return

        file_name = os.path.splitext(os.path.basename(main_image_path))[0] + "+Wasserzeichen"
        save_path = filedialog.asksaveasfilename(
            title="Save Image As",
            initialfile=file_name,
            defaultextension=".png",
            filetypes=[("PNG", ".png"), ("JPEG", ".jpg"), ("JPEG", ".jpeg")],
        )
        if not save_path:
            self.status_var.set("Save canceled.")
            return

        merged.save(save_path)
        self.preview_image = merged
        self._refresh_preview_canvas()
        self.status_var.set(f"Saved: {os.path.basename(save_path)}")

    def add_to_multiple_images(self) -> None:
        if not self.logo_image:
            messagebox.showwarning("No Logo Selected", "Please select a logo first.")
            return

        image_paths = filedialog.askopenfilenames(title="Select Images", filetypes=IMAGE_TYPES)
        if not image_paths:
            return

        if not self.preview_image:
            self._load_preview_image(image_paths[0])

        output_folder = filedialog.askdirectory(title="Select Output Folder")
        if not output_folder:
            self.status_var.set("No output folder selected.")
            return

        success_count = 0
        failed_count = 0

        for image_path in image_paths:
            merged = self._build_merged_image(image_path)
            if merged is None:
                failed_count += 1
                continue

            base_name = os.path.splitext(os.path.basename(image_path))[0]
            output_path = os.path.join(output_folder, f"{base_name}+Wasserzeichen.png")
            try:
                merged.save(output_path)
                success_count += 1
            except Exception:  # pylint: disable=broad-except
                failed_count += 1

        if success_count > 0:
            self._load_preview_image(image_paths[0])

        self.status_var.set(f"Done. Saved {success_count} image(s), failed {failed_count}.")
        if success_count > 0:
            messagebox.showinfo("Batch Complete", f"Saved {success_count} image(s) to:\n{output_folder}")


def main() -> None:
    root = tk.Tk()
    app = LogoAdderApp(root)
    root.mainloop()


if __name__ == "__main__":
    main()
