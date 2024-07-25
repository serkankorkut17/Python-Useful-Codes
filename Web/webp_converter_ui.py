import tkinter as tk
from tkinter import filedialog, messagebox
from PIL import Image, ImageTk
import threading
from io import BytesIO
import os

# Global variables to store the images
original_image = None
converted_image = None
input_image_path = None
update_pending = None
loading_label = None
original_image_size = 0
converted_image_size = 0

# def convert_compress_webp2(input_image_path, quality=75, lossless=False, effort=4):
#     global converted_image, converted_image_size
#     output_image_path = "temp_converted_image.webp"
#     try:
#         with Image.open(input_image_path) as img:
#             img.save(output_image_path, 'webp', quality=quality, lossless=lossless, method=effort)
#         converted_image = Image.open(output_image_path)
#         converted_image_size = os.path.getsize(output_image_path) / (1024 * 1024)  # Convert bytes to MB
#         update_display()
#         stop_loading_animation()
#         show_image_sizes()
#     except Exception as e:
#         messagebox.showerror("Error", str(e))
#         stop_loading_animation()
        
def convert_compress_webp(input_image_path, quality=75, lossless=False, effort=4):
    global converted_image, converted_image_size
    try:
        with Image.open(input_image_path) as img:
            buffer = BytesIO()
            img.save(buffer, 'webp', quality=quality, lossless=lossless, method=effort)
            buffer.seek(0)
            converted_image_size = buffer.getbuffer().nbytes / (1024 * 1024)  # Convert bytes to MB
            converted_image = Image.open(buffer)
            update_display()
            stop_loading_animation()
            show_image_sizes()
    except Exception as e:
        messagebox.showerror("Error", str(e))
        stop_loading_animation()

def browse_input():
    global input_image_path, original_image_size
    input_image_path = filedialog.askopenfilename(filetypes=[("Image files", "*.jpg *.jpeg *.png *.bmp *.gif")])
    input_path.set(input_image_path)
    if input_image_path:
        original_image_size = os.path.getsize(input_image_path) / (1024 * 1024)  # Convert bytes to MB
        show_images(input_image_path)
        start_loading_animation()
        threading.Thread(target=convert_compress_webp, args=(input_image_path, quality_slider.get(), lossless_var.get(), effort_slider.get())).start()

def browse_output():
    output_image_path = filedialog.asksaveasfilename(defaultextension=".webp", filetypes=[("WebP files", "*.webp")])
    if output_image_path:
        save_image(output_image_path)

def show_images(input_image_path):
    global original_image, original_photo
    try:
        original_image = Image.open(input_image_path)
        update_display()
    except Exception as e:
        messagebox.showerror("Error", str(e))

def update_display(event=None):
    global original_photo, converted_photo
    
    if original_image is None or converted_image is None:
        return
    
    canvas_width = comparison_canvas.winfo_width()
    canvas_height = comparison_canvas.winfo_height()
    
    # Determine the cropping box
    img_width, img_height = original_image.size
    center_x = img_width // 2
    center_y = img_height // 2
    crop_width = min(img_width, canvas_width) // 2
    crop_height = min(img_height, canvas_height)
    
    box = (center_x - crop_width, center_y - crop_height // 2,
           center_x + crop_width, center_y + crop_height // 2)
    
    cropped_original = original_image.crop(box)
    cropped_converted = converted_image.crop(box)
    
    resized_original = cropped_original.resize((canvas_width // 2, canvas_height), Image.LANCZOS)
    resized_converted = cropped_converted.resize((canvas_width // 2, canvas_height), Image.LANCZOS)
    
    original_photo = ImageTk.PhotoImage(resized_original)
    converted_photo = ImageTk.PhotoImage(resized_converted)
    
    comparison_canvas.delete("all")
    comparison_canvas.create_image(0, 0, anchor='nw', image=original_photo, tags="original")
    comparison_canvas.create_image(canvas_width // 2, 0, anchor='nw', image=converted_photo, tags="converted")
    comparison_canvas.create_text(canvas_width // 4, 10, anchor='n', text="Original", fill="white", tags="label")
    comparison_canvas.create_text(3 * canvas_width // 4, 10, anchor='n', text="Converted", fill="white", tags="label")
    
    comparison_canvas.image = original_photo  # Keep a reference to the image to avoid garbage collection
    comparison_canvas.image2 = converted_photo  # Keep a reference to the image to avoid garbage collection

def save_image(output_image_path):
    if converted_image:
        try:
            converted_image.save(output_image_path)
            messagebox.showinfo("Success", f"Image saved to {output_image_path}")
        except Exception as e:
            messagebox.showerror("Error", str(e))

def on_slider_change(event):
    global update_pending
    if update_pending:
        root.after_cancel(update_pending)
    update_pending = root.after(500, update_conversion)

def update_conversion():
    global update_pending
    if input_image_path:
        start_loading_animation()
        threading.Thread(target=convert_compress_webp, args=(input_image_path, quality_slider.get(), lossless_var.get(), effort_slider.get())).start()
    update_pending = None

def start_loading_animation():
    global loading_label
    loading_label = tk.Label(root, text="Loading", font=("Arial", 20))
    loading_label.grid(row=5, column=1, pady=20)
    animate_loading()

def animate_loading():
    if loading_label is not None and loading_label.winfo_exists():
        current_text = loading_label.cget("text")
        if current_text.endswith("..."):
            new_text = "Loading"
        else:
            new_text = current_text + "."
        loading_label.config(text=new_text)
        root.after(500, animate_loading)

def stop_loading_animation():
    global loading_label
    if loading_label is not None:
        loading_label.destroy()
        loading_label = None

def show_image_sizes():
    if original_image_size > 0 and converted_image_size > 0:
        size_diff = original_image_size - converted_image_size
        percentage_smaller = (size_diff / original_image_size) * 100
        size_info.set(f"Original Size: {original_image_size:.2f} MB\n"
                      f"Converted Size: {converted_image_size:.2f} MB\n"
                      f"Reduced by: {size_diff:.2f} MB ({percentage_smaller:.2f}%)")

# Create the main window
root = tk.Tk()
root.title("Image to WebP Converter")

# Input path
input_path = tk.StringVar()
tk.Label(root, text="Input Image:").grid(row=0, column=0, padx=10, pady=10)
tk.Entry(root, textvariable=input_path, width=50).grid(row=0, column=1, padx=10, pady=10)
tk.Button(root, text="Browse...", command=browse_input).grid(row=0, column=2, padx=10, pady=10)

# Quality
tk.Label(root, text="Quality:").grid(row=2, column=0, padx=10, pady=10)
quality_slider = tk.Scale(root, from_=0, to=100, orient="horizontal", label="Quality")
quality_slider.set(75)
quality_slider.grid(row=2, column=1, padx=10, pady=10)
quality_slider.bind("<ButtonRelease-1>", on_slider_change)
quality_slider.bind("<Motion>", lambda event: root.after_cancel(update_pending) if update_pending else None)

# Lossless
lossless_var = tk.BooleanVar()
lossless_check = tk.Checkbutton(root, text="Lossless", variable=lossless_var)
lossless_check.grid(row=3, column=1, padx=10, pady=10)
lossless_check.bind("<ButtonRelease-1>", on_slider_change)

# Effort
tk.Label(root, text="Effort:").grid(row=4, column=0, padx=10, pady=10)
effort_slider = tk.Scale(root, from_=0, to=6, orient="horizontal", label="Effort")
effort_slider.set(4)
effort_slider.grid(row=4, column=1, padx=10, pady=10)
effort_slider.bind("<ButtonRelease-1>", on_slider_change)
effort_slider.bind("<Motion>", lambda event: root.after_cancel(update_pending) if update_pending else None)

# Save button
tk.Button(root, text="Save", command=browse_output).grid(row=5, column=0, columnspan=3, pady=20)

# Comparison frame
comparison_frame = tk.Frame(root)
comparison_frame.grid(row=6, column=0, columnspan=3, padx=10, pady=10, sticky="nsew")

# Add a canvas with a scrollbar
comparison_canvas = tk.Canvas(comparison_frame, width=600, height=600)
comparison_canvas.pack(expand=True, fill=tk.BOTH)

# Size info label
size_info = tk.StringVar()
size_label = tk.Label(root, textvariable=size_info, font=("Arial", 12))
size_label.grid(row=7, column=0, columnspan=3, pady=10)

# Configure grid to make canvas expandable
root.grid_rowconfigure(6, weight=1)
root.grid_columnconfigure(1, weight=1)

# Bind the configure event to update the display when the window is resized
comparison_canvas.bind("<Configure>", update_display)

# Run the main loop
root.mainloop()
