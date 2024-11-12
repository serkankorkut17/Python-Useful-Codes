import tkinter as tk
from tkinter import filedialog
from PIL import Image, ImageTk

class ImageCropper:
    def __init__(self, root):
        self.root = root
        self.root.title("Image Cropper")
        
        self.image = None
        self.display_image_obj = None
        self.image_tk = None
        self.rect = None
        self.start_x = None
        self.start_y = None
        self.crop_box = None
        self.rect_label = None
        self.resize_ratio = 1  # Ratio to map displayed image coordinates to original image coordinates

        self.canvas = tk.Canvas(self.root, cursor="cross")
        self.canvas.pack(fill=tk.BOTH, expand=True)

        self.crop_button = tk.Button(self.root, text="Crop", command=self.crop_image)
        self.crop_button.pack()

        self.menu = tk.Menu(self.root)
        self.root.config(menu=self.menu)
        file_menu = tk.Menu(self.menu, tearoff=0)
        self.menu.add_cascade(label="File", menu=file_menu)
        file_menu.add_command(label="Open", command=self.open_image)
        file_menu.add_command(label="Save", command=self.save_image)
        file_menu.add_separator()
        file_menu.add_command(label="Exit", command=root.quit)

        self.canvas.bind("<ButtonPress-1>", self.on_button_press)
        self.canvas.bind("<B1-Motion>", self.on_mouse_drag)
        self.canvas.bind("<ButtonRelease-1>", self.on_button_release)

        self.root.bind("<Configure>", self.on_resize)

    def open_image(self):
        file_path = filedialog.askopenfilename()
        if file_path:
            self.image = Image.open(file_path)
            self.display_image()

    def resize_image(self, image, max_width, max_height):
        width_ratio = max_width / image.width
        height_ratio = max_height / image.height
        new_width, new_height = image.width, image.height

        if width_ratio < 1 or height_ratio < 1:
            if width_ratio < height_ratio:
                new_width = int(image.width * width_ratio)
                new_height = int(image.height * width_ratio)
            else:
                new_width = int(image.width * height_ratio)
                new_height = int(image.height * height_ratio)
        self.resize_ratio = image.width / new_width  # Update resize ratio
        return image.resize((new_width, new_height), Image.Resampling.LANCZOS)

    def display_image(self):
        self.canvas.delete("all")
        max_width = self.canvas.winfo_width()
        max_height = self.canvas.winfo_height()

        self.display_image_obj = self.resize_image(self.image, max_width, max_height)
        self.image_tk = ImageTk.PhotoImage(self.display_image_obj)
        self.canvas.create_image(0, 0, anchor=tk.NW, image=self.image_tk)
        self.canvas.config(scrollregion=self.canvas.bbox(tk.ALL))

    def save_image(self):
        if self.crop_box:
            cropped_image = self.image.crop(self.crop_box)
            save_path = filedialog.asksaveasfilename(defaultextension=".png")
            if save_path:
                cropped_image.save(save_path)

    def on_button_press(self, event):
        self.start_x = self.canvas.canvasx(event.x)
        self.start_y = self.canvas.canvasy(event.y)
        if self.rect:
            self.canvas.delete(self.rect)
        self.rect = self.canvas.create_rectangle(self.start_x, self.start_y, self.start_x, self.start_y, outline='red', dash=(2, 2))
        if self.rect_label:
            self.canvas.delete(self.rect_label)
        self.rect_label = self.canvas.create_text(self.start_x, self.start_y, anchor=tk.SW, text="")

    def on_mouse_drag(self, event):
        cur_x = self.canvas.canvasx(event.x)
        cur_y = self.canvas.canvasy(event.y)
        self.canvas.coords(self.rect, self.start_x, self.start_y, cur_x, cur_y)
        self.update_label(cur_x, cur_y)

    def on_button_release(self, event):
        end_x = self.canvas.canvasx(event.x)
        end_y = self.canvas.canvasy(event.y)
        self.update_label(end_x, end_y)
        self.crop_box = (
            int(self.start_x * self.resize_ratio),
            int(self.start_y * self.resize_ratio),
            int(end_x * self.resize_ratio),
            int(end_y * self.resize_ratio)
        )

    def on_resize(self, event):
        if self.image:
            self.display_image()

    def update_label(self, end_x, end_y):
        width = abs(end_x - self.start_x)
        height = abs(end_y - self.start_y)
        label_text = f"{int(width * self.resize_ratio)}x{int(height * self.resize_ratio)}"
        self.canvas.coords(self.rect_label, (self.start_x + end_x) / 2, (self.start_y + end_y) / 2)
        self.canvas.itemconfig(self.rect_label, text=label_text)

    def crop_image(self):
        if self.crop_box:
            x1, y1, x2, y2 = self.crop_box
            cropped_image = self.image.crop((x1, y1, x2, y2))
            self.image = cropped_image
            self.display_image()
            self.crop_box = None
            self.canvas.delete(self.rect_label)
            self.rect_label = None

if __name__ == "__main__":
    root = tk.Tk()
    root.geometry("800x600")  # Set the initial window size
    app = ImageCropper(root)
    root.mainloop()
