import re
import json
from playwright.sync_api import Playwright, sync_playwright, expect

PRODUCT_NAME = "ttttest ürünüüüü"
PRODUCT_CATEGORIES = None #["Turkisch Delight", "Halva"]
PRODUCT_PRICES =None #["10", "20", "30", "40"]

PRODUCT_IMAGE = None #"car.webp"
PRODUCT_DESCRIPTION = None #"Bu ürün test amaçlı eklenmiştir."
PRODUCT_TAGS = None #["ürün", "hebele", "hübele"]
# PRODUCT_GALLERY = ["kumru111.webp", "kumru111-2.webp", "kumru111-3.webp"]
PRODUCT_GALLERY = ["car-1.jpg", "car-2.jpg", "car-3.jpg"]

def load_config():
    with open("config.json") as config_file:
        return json.load(config_file)
    
def open_wordpress(playwright):
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
    
    return browser, context, page
    
def add_new_product(page, product):
    page.locator("#wpbody-content").get_by_role("link", name="Yeni ekle").click()
    # Ürün adı
    page.get_by_label("Ürün adı").fill(product.name)
    
    # Ürün açıklaması
    if product.description:
        # page.frame_locator("#content_ifr").get_by_role("paragraph").click()
        page.frame_locator("#content_ifr").locator("#tinymce").fill(product.description)
        
    # Ürün kategorileri
    # if not none iterate over categories
    if product.categories:
        for category in product.categories:
            page.get_by_role("checkbox", name=category).check()
    
    if product.prices:
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
        page.get_by_role("button", name="El ile ekle").click()
        page.locator("select[name=\"attribute_pa_weight\\[0\\]\"]").select_option("100g")
        page.locator("#variable_product_options_inner").get_by_role("link", name="Düzenle").click()
        page.get_by_placeholder("Varyasyon fiyatı (gerekli)").click()
        page.get_by_placeholder("Varyasyon fiyatı (gerekli)").fill(product.prices[0])
        page.locator("#variable_product_options_inner").get_by_role("link", name="Düzenle").click()
        page.get_by_role("button", name="El ile ekle").click()
        page.locator("select[name=\"attribute_pa_weight\\[1\\]\"]").select_option("250g")
        page.get_by_role("link", name="Düzenle").nth(3).click()
        page.get_by_role("textbox", name="Normal fiyat (€)").click()
        page.get_by_role("textbox", name="Normal fiyat (€)").fill(product.prices[1])
        page.get_by_role("link", name="Düzenle").nth(3).click()
        page.get_by_role("button", name="El ile ekle").click()
        page.locator("select[name=\"attribute_pa_weight\\[2\\]\"]").select_option("500g")
        page.get_by_role("link", name="Düzenle", exact=True).nth(1).click()
        page.get_by_role("textbox", name="Normal fiyat (€)").click()
        page.get_by_role("textbox", name="Normal fiyat (€)").fill(product.prices[2])
        page.get_by_role("link", name="Düzenle", exact=True).nth(1).click()
        page.get_by_role("button", name="El ile ekle").click()
        page.locator("select[name=\"attribute_pa_weight\\[3\\]\"]").select_option("1kg")
        page.get_by_role("link", name="Düzenle", exact=True).nth(1).click()
        page.get_by_role("textbox", name="Normal fiyat (€)").click()
        page.get_by_role("textbox", name="Normal fiyat (€)").fill(product.prices[3])
        page.get_by_role("button", name="Değişiklikleri kaydet").click()
    
    # Ürün etiketleri
    if product.tags:
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
        page.wait_for_timeout(10000)
        page.get_by_label("Alternatif metin").fill(product.name)
        page.get_by_role("button", name="Ürün resmini ayarla").click()
        page.wait_for_timeout(5000)
        
    # Ürün galerisi
    page.wait_for_timeout(10000)
    if product.gallery:
        i = 1
        page.get_by_role("link", name="Ürün galerisine görsel ekle").click()
        page.get_by_role("tab", name="Dosya yükle").click()
        
        # image isminin sonuna tarih ekle
        for image in product.gallery:
            try:
                page.locator("input[type='file']").nth(0).set_input_files(image)
                page.wait_for_selector(".media-uploader-status > .media-progress-bar > div", state="hidden", timeout=300000)
                page.wait_for_timeout(1000)
                image_name = re.split(r"\.", image)[0]
                if i > 1:
                    page.get_by_label(image_name).first.click()
                page.get_by_label("Alternatif metin").fill(product.name + " " + str(i))
                i += 1
            except Exception as e:
                print(e)
                i += 1
                # click X button
                # page.get_by_role("button", name="Kapat").click()
                # playwright debugging
                page.screenshot(path="error.png")
        
        page.get_by_role("button", name="Galeriye ekle").click()
    # ///////////////////////////////////////////////////////////////////
    # Ürün yayınlama
    page.get_by_role("button", name="Yayınla", exact=True).click()
    page.wait_for_timeout(10000)
    
        
    
    
    
def run(playwright: Playwright) -> None:
    browser, context, page = open_wordpress(playwright)
    
    class Product:
        def __init__(self, name, categories, prices, tags=None, image=None, description=None, gallery=None):
            self.name = name
            self.categories = categories
            self.prices = prices
            self.image = image
            self.description = description
            self.tags = tags
            self.gallery = gallery
            
    product = Product(PRODUCT_NAME, PRODUCT_CATEGORIES, PRODUCT_PRICES, PRODUCT_TAGS, PRODUCT_IMAGE, PRODUCT_DESCRIPTION, PRODUCT_GALLERY)
    
    add_new_product(page, product)
    
    
    
    

    # ---------------------
    context.close()
    browser.close()


with sync_playwright() as playwright:
    run(playwright)
