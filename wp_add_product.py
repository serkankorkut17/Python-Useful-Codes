import tkinter as tk
from tkinter import ttk, filedialog, messagebox
from PIL import Image, ImageTk
import os
from datetime import datetime
import json
import re
from playwright.sync_api import Playwright, sync_playwright, expect

FOLDER_NAME = "WP-Products"
PRODUCTS_FILE = "WP-Products/products.json"

CATEGORIES = {
    "Nüsse": ["Gebrannte Nüsse", "Geröstete Nüsse", "Geschenk Boxen", "Natur Nüsse", "Nussmischungen", "Wasabi"],
    "Kerne": [],
    "Trockenfrüchte": ["Behandelte früchte", "Natur früchte"],
    "Gewürze": [],
    "Krauter": [],
    "Geschenke": [],
    "Schokolade": [],
    "Turkisch Delight": ["Halva", "Spezial Lokum"],
    "Tee&Coffee": [],
}


def load_config():
    with open("config.json") as config_file:
        return json.load(config_file)

# config = load_config()
# CATEGORIES = config["Categories"]

def convert_compress_webp(input_image_path, output_image_path, quality=75, lossless=False, effort=4):
    with Image.open(input_image_path) as img:
        img.save(output_image_path, 'webp', quality=quality, lossless=lossless, method=effort)
    # print(f"Successfully converted {input_image_path} to {output_image_path} with quality={quality}, lossless={lossless}, effort={effort}")
    
class Product:
    def __init__(self, name, categories, prices, tags=None, image=None, description=None, gallery=None):
        self.name = name
        self.categories = categories
        self.prices = prices
        self.image = image
        self.description = description
        self.tags = tags
        self.gallery = gallery

class WordPressProductAdder:
    def __init__(self, products):
        self.products = products
        self.browser = None
        self.context = None
        self.page = None
        with sync_playwright() as playwright:
            self.run(playwright)
            
        
    def run(self, playwright: Playwright) -> None:
        browser, context, page = self.open_wordpress(playwright)
        
        for product in self.products:
            self.add_new_product(page, product)

        context.close()
        browser.close()
    
    def open_wordpress(self, playwright):
        config = load_config()
        username = config["Username"]
        password = config["Password"]
        address = config["Address"]
        
        browser = playwright.chromium.launch(headless=False)
        # browser = playwright.chromium.launch(headless=True)
        context = browser.new_context()
        page = context.new_page()
        page.goto(address)
        
        # temporary
        page.locator("span").first.click()
        page.get_by_role("button", name="Continue to website").click()

        # HESAP GİRİŞİ 
        page.get_by_label("Benutzername oder E-Mail-").fill(username)
        page.get_by_label("Passwort", exact=True).fill(password)
        page.get_by_role("button", name="Anmelden").click()
        
        # ÜRÜNLERE GİT
        page.locator("#menu-posts-product").get_by_role("link", name="Ürünler", exact=True).click()
        
        self.browser = browser
        self.context = context
        self.page = page
        
        return browser, context, page
    
    def add_new_product(self, page, product):
        page.locator("#wpbody-content").get_by_role("link", name="Yeni ekle").click()
        # Ürün adı
        page.get_by_label("Ürün adı").fill(product.name)
        
        # Ürün açıklaması
        if product.description and product.description != "":
            # page.frame_locator("#content_ifr").get_by_role("paragraph").click()
            page.frame_locator("#content_ifr").locator("#tinymce").fill(product.description)
            
        # Ürün kategorileri
        if product.categories and len(product.categories) > 0:
            for category in product.categories:
                page.get_by_role("checkbox", name=category, exact=True).check()
        
        # Ürün fiyatları
        if product.prices and product.prices != {}:
            # Varyasyonlu ürün seç  
            page.get_by_label("Basit ürün Gruplandırılmış ür").select_option("variable")
            # Niteliği ekle
            page.get_by_role("link", name="Nitelikler").click()
            page.get_by_text("Var olanı ekle").click()
            page.get_by_role("option", name="Gewicht").click()
            page.get_by_role("button", name="Tümünü seç").click()
            page.get_by_role("button", name="Nitelikleri kaydet").click()
            # Varyasyonları ekle
            page.get_by_role("link", name="Varyasyonlar").click()
            # Fiyatları ekle
            # loop prices dict
            # for weight, price in product.prices.items():
            #     price = str(price)

            # str change . to coma
            #     price = price.replace(".", ",")
    
            page.get_by_role("button", name="El ile ekle").click()
            page.locator("select[name=\"attribute_pa_weight\\[0\\]\"]").select_option("100g")
            page.locator("#variable_product_options_inner").get_by_role("link", name="Düzenle").click()
            page.get_by_placeholder("Varyasyon fiyatı (gerekli)").click()
            page.get_by_placeholder("Varyasyon fiyatı (gerekli)").fill(str(product.prices["100g"]).replace(".", ","))
            page.locator("#variable_product_options_inner").get_by_role("link", name="Düzenle").click()
            page.get_by_role("button", name="El ile ekle").click()
            page.locator("select[name=\"attribute_pa_weight\\[1\\]\"]").select_option("250g")
            page.get_by_role("link", name="Düzenle").nth(3).click()
            page.get_by_role("textbox", name="Normal fiyat (€)").click()
            page.get_by_role("textbox", name="Normal fiyat (€)").fill(str(product.prices["250g"]).replace(".", ","))
            page.get_by_role("link", name="Düzenle").nth(3).click()
            page.get_by_role("button", name="El ile ekle").click()
            page.locator("select[name=\"attribute_pa_weight\\[2\\]\"]").select_option("500g")
            page.get_by_role("link", name="Düzenle", exact=True).nth(1).click()
            page.get_by_role("textbox", name="Normal fiyat (€)").click()
            page.get_by_role("textbox", name="Normal fiyat (€)").fill(str(product.prices["500g"]).replace(".", ","))
            page.get_by_role("link", name="Düzenle", exact=True).nth(1).click()
            page.get_by_role("button", name="El ile ekle").click()
            page.locator("select[name=\"attribute_pa_weight\\[3\\]\"]").select_option("1kg")
            page.get_by_role("link", name="Düzenle", exact=True).nth(1).click()
            page.get_by_role("textbox", name="Normal fiyat (€)").click()
            page.get_by_role("textbox", name="Normal fiyat (€)").fill(str(product.prices["1kg"]).replace(".", ","))
            page.get_by_role("button", name="Değişiklikleri kaydet").click()
        
        # Ürün etiketleri
        if product.tags and len(product.tags) > 0:
            page.get_by_label("Yeni etiket ekle").click()
            for tag in product.tags:
                page.get_by_label("Yeni etiket ekle").fill(tag)
                page.get_by_label("Yeni etiket ekle").press("Enter")
        
        if product.image:
            # Ürün görseli ayarlama
            page.get_by_role("link", name="Ürün resmini ayarla").click()
            page.get_by_role("tab", name="Dosya yükle").click()
            page.locator("input[type='file']").set_input_files(product.image)
            # wait until image is uploaded
            page.wait_for_selector(".media-uploader-status > .media-progress-bar > div", state="hidden", timeout=300000)
            # page.wait_for_timeout(10000)
            page.get_by_label("Alternatif metin").fill(product.name)
            page.get_by_role("button", name="Ürün resmini ayarla").click()
            page.wait_for_timeout(5000)
            
        # Ürün galerisi
        # page.wait_for_timeout(10000)
        if product.gallery:
            i = 1
            page.get_by_role("link", name="Ürün galerisine görsel ekle").click()
            page.get_by_role("tab", name="Dosya yükle").click()
            
            # image isminin sonuna tarih ekle
            for image in product.gallery:
                try:
                    page.locator("input[type='file']").nth(0).set_input_files(image)
                    page.wait_for_selector(".media-uploader-status > .media-progress-bar > div", state="hidden", timeout=300000)
                    # page.wait_for_timeout(1000)
                    # image_name = re.split(r"\.", image)[0]
                    # if i > 1:
                    #     page.get_by_label(image_name).first.click()
                    # page.get_by_label("Alternatif metin").fill(product.name + " " + str(i))
                    # i += 1
                except Exception as e:
                    print(e)
                    i += 1
                    # click X button
                    # page.get_by_role("button", name="Kapat").click()
                    page.screenshot(path="error.png")
            
            page.get_by_role("button", name="Galeriye ekle").click()
        # ///////////////////////////////////////////////////////////////////
        # Ürün yayınlama
        page.get_by_role("button", name="Yayınla", exact=True).click()
        page.wait_for_timeout(10000)

class Product:
    def __init__(self, name, categories, prices, tags=None, image=None, description=None, gallery=None):
        self.name = name
        self.categories = categories
        self.prices = prices
        self.image = image
        self.description = description
        self.tags = tags
        self.gallery = gallery

class ProductApp:
    def __init__(self, root):
        self.root = root
        self.root.geometry("1280x720")
        self.root.title("Product Input")
        self.image_path = tk.StringVar()
        self.image_original = None
        self.gallery_images = []
        self.create_widgets()
        self.root.bind('<Configure>', self.on_resize)
        self.loading_label = None
        self.loading_screen = None

    def create_widgets(self):
        # Name input
        tk.Label(self.root, text="Product Name:").grid(row=0, column=0, sticky=tk.W)
        self.name_entry = tk.Entry(self.root)
        self.name_entry.grid(row=0, column=1, sticky=tk.EW)

        # Categories input
        tk.Label(self.root, text="Categories:").grid(row=1, column=0, sticky=tk.W)
        self.category_var = tk.StringVar()
        self.category_combobox = ttk.Combobox(self.root, textvariable=self.category_var, values=list(CATEGORIES.keys()), state="readonly")
        self.category_combobox.grid(row=1, column=1, sticky=tk.EW)
        self.category_combobox.bind("<<ComboboxSelected>>", self.update_subcategories)

        # Subcategories input
        tk.Label(self.root, text="Subcategories:").grid(row=2, column=0, sticky=tk.W)
        
        self.subcategories_vars = {}
        for category, subcategories in CATEGORIES.items():
            self.subcategories_vars[category] = {}
            for subcategory in subcategories:
                self.subcategories_vars[category][subcategory] = tk.BooleanVar()
        
        self.subcategories_frame = tk.Frame(self.root)
        self.subcategories_frame.grid(row=2, column=1, sticky=tk.W)

        # Prices input
        tk.Label(self.root, text="Prices:").grid(row=3, column=0, sticky=tk.W)
        prices_frame = tk.Frame(self.root)
        prices_frame.grid(row=3, column=1, sticky=tk.W)
        self.prices_vars = {
            "100g": tk.StringVar(),
            "250g": tk.StringVar(),
            "500g": tk.StringVar(),
            "1kg": tk.StringVar()
        }
        for i, (size, var) in enumerate(self.prices_vars.items()):
            tk.Label(prices_frame, text=f"{size}:").grid(row=0, column=i*2, sticky=tk.W)
            tk.Entry(prices_frame, textvariable=var).grid(row=0, column=i*2+1, sticky=tk.EW)
        
        # Tags input
        tk.Label(self.root, text="Tags (comma separated):").grid(row=4, column=0, sticky=tk.W)
        self.tags_entry = tk.Entry(self.root)
        self.tags_entry.grid(row=4, column=1, sticky=tk.EW)

        # Description input
        tk.Label(self.root, text="Description:").grid(row=5, column=0, sticky=tk.W)
        self.description_text = tk.Text(self.root, height=4, width=30)
        self.description_text.grid(row=5, column=1, sticky=tk.EW)

        # Image input
        tk.Label(self.root, text="Main Image:").grid(row=6, column=0, sticky=tk.W)
        tk.Entry(self.root, textvariable=self.image_path).grid(row=6, column=1, sticky=tk.EW)
        tk.Button(self.root, text="Browse", command=self.load_image).grid(row=6, column=2)

        # Gallery input
        tk.Label(self.root, text="Gallery Images:").grid(row=7, column=0, sticky=tk.W)
        tk.Button(self.root, text="Add Images", command=self.load_gallery_images).grid(row=7, column=1, sticky=tk.W)

        self.gallery_frame = tk.Frame(self.root)
        self.gallery_frame.grid(row=8, column=0, columnspan=3, sticky=tk.W)

        # Submit button
        self.submit_button = tk.Button(root, text="Submit", command=self.create_product)
        self.submit_button.grid(row=9, column=0, columnspan=3, pady=10)

        # Image display
        self.image_label = tk.Label(self.root)
        self.image_label.grid(row=10, column=0, columnspan=3, sticky=tk.NSEW)
        
        # Send button make it diffrent color its more importatn button and margin to botom
        self.send_button = tk.Button(root, text="Send", command=self.send_product, bg="red")
        self.send_button.grid(row=11, column=0, columnspan=3, pady=10)

        # Grid configuration for resizing
        self.root.columnconfigure(1, weight=1)
        self.root.rowconfigure(10, weight=1)
    
    def clear_inputs(self):
        self.name_entry.delete(0, tk.END)
        self.category_combobox.set('')
        for var in self.subcategories_vars.values():
            for subcat_var in var.values():
                subcat_var.set(False)
        for var in self.prices_vars.values():
            var.set('')
        # clear subcategories
        for widget in self.subcategories_frame.winfo_children():
            widget.destroy()
        self.tags_entry.delete(0, tk.END)
        self.description_text.delete("1.0", tk.END)
        self.image_path.set('')
        self.image_original = None
        self.gallery_images = []
        # image display delete
        self.photo = None
        self.image_label.configure(image=None)
        self.image_label.image = None
        self.display_gallery_images()

    def update_subcategories(self, event):
        category = self.category_var.get()
        for widget in self.subcategories_frame.winfo_children():
            widget.destroy()
        if category in self.subcategories_vars:
            for subcat, var in self.subcategories_vars[category].items():
                tk.Checkbutton(self.subcategories_frame, text=subcat, variable=var).pack(anchor=tk.W)

    def load_image(self):
        filepath = filedialog.askopenfilename(filetypes=[("Image files", "*.jpg *.jpeg *.png *.webp")])
        if filepath:
            self.image_path.set(filepath)
            self.image_original = Image.open(filepath)
            self.display_image()

    def load_gallery_images(self):
        filepaths = filedialog.askopenfilenames(filetypes=[("Image files", "*.jpg *.jpeg *.png *.webp")])
        for filepath in filepaths:
            if filepath not in self.gallery_images:
                self.gallery_images.append(filepath)
                self.display_gallery_images()

    def display_image(self):
        if self.image_original:
            window_width = self.root.winfo_width()
            window_height = self.root.winfo_height()

            image_ratio = self.image_original.width / self.image_original.height
            max_width = window_width * 0.6
            max_height = window_height * 0.6

            if max_width / image_ratio <= max_height:
                new_width = int(max_width)
                new_height = int(max_width / image_ratio)
            else:
                new_width = int(max_height * image_ratio)
                new_height = int(max_height)

            image = self.image_original.resize((new_width, new_height), Image.LANCZOS)
            self.photo = ImageTk.PhotoImage(image)
            self.image_label.configure(image=self.photo)
            self.image_label.image = self.photo
        else:
            self.image_label.configure(image=None)
            self.image_label.image = None

    def display_gallery_images(self):
        for widget in self.gallery_frame.winfo_children():
            widget.destroy()
        for idx, img_path in enumerate(self.gallery_images):
            img = Image.open(img_path)
            img.thumbnail((100, 100), Image.LANCZOS)
            photo = ImageTk.PhotoImage(img)
            frame = tk.Frame(self.gallery_frame)
            frame.grid(row=0, column=idx, padx=5, pady=5)
            lbl = tk.Label(frame, image=photo)
            lbl.image = photo
            lbl.pack()
            btn = tk.Button(frame, text="X", command=lambda p=img_path: self.remove_gallery_image(p))
            btn.pack(side=tk.TOP, anchor=tk.NE)

    def remove_gallery_image(self, path):
        if path in self.gallery_images:
            self.gallery_images.remove(path)
            self.display_gallery_images()
    
    def show_loading_screen(self):
        # global loading_screen
        # Create a new Toplevel window
        self.submit_button.config(state=tk.DISABLED)

        # loading_screen = tk.Toplevel(self.root)
        # # loading_screen = tk.Tk()
        # loading_screen.title("Loading Page")
        # # loading_screen.geometry("300x200")
        # loading_screen.resizable(False, False)
        # loading_screen.grab_set()  # This makes the loading screen modal

        # # Create a label for the loading message
        # loading_label = ttk.Label(loading_screen, text="Loading...", font=("Arial", 14))
        # loading_label.pack(pady=50)
        # import time

        # # Create a progress bar
        # progress_bar = ttk.Progressbar(loading_screen, length=200, mode='indeterminate')
        # progress_bar.pack()

        # # Start the progress bar animation
        # progress_bar.start(10)
        
        # Make sure the loading screen is always on top
        # self.loading_screen.attributes("-topmost", True)
        # time.sleep(10)

    def hide_loading_screen(self):
        # global loading_screen
        # # Close the Toplevel window
        # if loading_screen:
        #     loading_screen.destroy()
        #     loading_screen = None
        # Re-enable the main window
        self.submit_button.config(state=tk.NORMAL)
    
    def create_product(self):
        # Product name   
        name = self.name_entry.get()
        if not name:
            messagebox.showerror("Invalid input", "Name cannot be empty.")
            return
        # Product categories
        category = self.category_var.get()
        if not category:
            messagebox.showerror("Invalid input", "Category must be selected.")
            return
        elif category not in self.subcategories_vars:
            messagebox.showerror("Invalid input", "Category must be selected.")
            return
        subcategories = [subcat for subcat, var in self.subcategories_vars[category].items() if var.get()]
        # Product prices
        prices = {}
        for size, var in self.prices_vars.items():
            try:
                prices[size] = float(var.get().replace(',', '.'))
            except ValueError:
                messagebox.showerror("Invalid input", f"Price for {size} must be a number.")
                return
        
        # Loading screen
        self.show_loading_screen()

        # Product tags, image, description, gallery
        tags = self.tags_entry.get().split(',') if self.tags_entry.get() else None
        image = self.image_path.get()
        description = self.description_text.get("1.0", tk.END).strip()
        gallery = self.gallery_images if self.gallery_images else None
        
        # Convert images to WebP format
        date_now = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
        if image:
            webp_path = f"{FOLDER_NAME}/{name} - {date_now}.webp"
            convert_compress_webp(image, webp_path)
            image = webp_path

        if gallery:
            gallery_webp = []
            for img_path in gallery:
                webp_path = f"{FOLDER_NAME}/{name} - {date_now} - {os.path.basename(img_path).rsplit(".", 1)[0]}.webp"
                convert_compress_webp(img_path, webp_path)
                gallery_webp.append(webp_path)
            gallery = gallery_webp
        
        # write inputs to products.json file
        product = Product(name, [category] + subcategories, prices, tags, image, description, gallery)
        # add product to products.json file if not exist create one
        if not os.path.exists(PRODUCTS_FILE):
            with open(PRODUCTS_FILE, "w", encoding="utf-8") as f:
                json.dump([], f)
        with open(PRODUCTS_FILE, "r", encoding="utf-8") as f:
            products = json.load(f)
        products.append(vars(product))
        with open(PRODUCTS_FILE, "w", encoding="utf-8") as f:
            json.dump(products, f, indent=4)
        
    
        # Hide loading screen
        self.hide_loading_screen()
        self.clear_inputs()
        
    def send_product(self):
        # load products from products.json
        def load_products():
            with open("WP-Products/products.json") as products_file:
                return json.load(products_file)
            
        products = load_products()
        # make a list of Product objects
        products_obj = [Product(**product) for product in products]
        # print(products)
        WordPressProductAdder(products_obj)

    def on_resize(self, event):
        self.display_image()

if __name__ == "__main__":
    # create Product Info folder if not exist
    if not os.path.exists(FOLDER_NAME):
        os.mkdir(FOLDER_NAME)
    root = tk.Tk()
    app = ProductApp(root)
    root.mainloop()
