import re
import json
from playwright.sync_api import Playwright, sync_playwright, expect

PRODUCT_NAME = "test ürünü ttttttttt"
CATEGORIES = ["Nüsse", "Gewürze"]
PRODUCT_PRICES = ["10", "20", "30", "40"]
PRODUCT_TAGS = ["ürün", "hebele", "hübele"]


def load_config():
    with open("config.json") as config_file:
        return json.load(config_file)

def run(playwright: Playwright) -> None:
    config = load_config()
    username = config["username"]
    password = config["password"]
    address = config["address"]
    
    browser = playwright.chromium.launch(headless=False)
    # browser = playwright.chromium.launch(headless=True)
    context = browser.new_context()
    page = context.new_page()
    page.goto(address)
    
    # --------------------- HESAP GİRİŞİ ---------------------
    page.get_by_label("Kullanıcı adı ya da e-posta").fill(username)
    page.get_by_label("Parola", exact=True).fill(password)
    page.get_by_role("button", name="Oturum aç").click()
    # --------------------- ÜRÜN EKLEME ---------------------
    page.locator("#menu-posts-product").get_by_role("link", name="Ürünler", exact=True).click()
    page.locator("#wpbody-content").get_by_role("link", name="Yeni ekle").click()
    # --------------------- ÜRÜN BİLGİLERİ ---------------------
    page.get_by_label("Ürün adı").fill(PRODUCT_NAME)
    for category in CATEGORIES:
        page.get_by_role("checkbox", name=category).check()
    # --------------------- ÜRÜN FİYATLARI ---------------------
    page.get_by_label("Basit ürün Gruplandırılmış ür").select_option("variable")
    page.get_by_role("link", name="Nitelikler").click()
    page.get_by_text("Var olanı ekle").click()
    page.get_by_role("option", name="Gewicht").click()
    page.get_by_role("button", name="Tümünü seç").click()
    page.get_by_role("button", name="Nitelikleri kaydet").click()
    page.get_by_role("link", name="Varyasyonlar").click()
    page.get_by_role("button", name="El ile ekle").click()
    page.locator("select[name=\"attribute_pa_weight\\[0\\]\"]").select_option("100g")
    page.locator("#variable_product_options_inner").get_by_role("link", name="Düzenle").click()
    page.get_by_placeholder("Varyasyon fiyatı (gerekli)").click()
    page.get_by_placeholder("Varyasyon fiyatı (gerekli)").fill(PRODUCT_PRICES[0])
    page.locator("#variable_product_options_inner").get_by_role("link", name="Düzenle").click()
    page.get_by_role("button", name="El ile ekle").click()
    page.locator("select[name=\"attribute_pa_weight\\[1\\]\"]").select_option("250g")
    page.get_by_role("link", name="Düzenle").nth(3).click()
    page.get_by_role("textbox", name="Normal fiyat (€)").click()
    page.get_by_role("textbox", name="Normal fiyat (€)").fill(PRODUCT_PRICES[1])
    page.get_by_role("link", name="Düzenle").nth(3).click()
    page.get_by_role("button", name="El ile ekle").click()
    page.locator("select[name=\"attribute_pa_weight\\[2\\]\"]").select_option("500g")
    page.get_by_role("link", name="Düzenle", exact=True).nth(1).click()
    page.get_by_role("textbox", name="Normal fiyat (€)").click()
    page.get_by_role("textbox", name="Normal fiyat (€)").fill(PRODUCT_PRICES[2])
    page.get_by_role("link", name="Düzenle", exact=True).nth(1).click()
    page.get_by_role("button", name="El ile ekle").click()
    page.locator("select[name=\"attribute_pa_weight\\[3\\]\"]").select_option("1kg")
    page.get_by_role("link", name="Düzenle", exact=True).nth(1).click()
    page.get_by_role("textbox", name="Normal fiyat (€)").click()
    page.get_by_role("textbox", name="Normal fiyat (€)").fill(PRODUCT_PRICES[3])
    page.get_by_role("button", name="Değişiklikleri kaydet").click()
    # --------------------- ÜRÜN ETİKETLERİ ---------------------
    page.get_by_label("Yeni etiket ekle").click()
    for tag in PRODUCT_TAGS:
        page.get_by_label("Yeni etiket ekle").fill(tag)
        page.get_by_label("Yeni etiket ekle").press("Enter")
    # --------------------- ÜRÜN GÖRSELİ ---------------------
    # page.get_by_role("button", name="Panoyu aç/kapat: Ürün görseli").click()
    page.get_by_role("link", name="Ürün resmini ayarla").click()
    page.get_by_role("tab", name="Dosya yükle").click()
    # page.get_by_label("Dosya seçin").click()
    page.locator("input[type='file']").set_input_files("cardamon.jpeg")
    page.wait_for_timeout(10000)
    page.get_by_role("button", name="Ürün resmini ayarla").click()
    # --------------------- ÜRÜN YAYINLAMA ---------------------
    page.get_by_role("button", name="Yayınla", exact=True).click()
    page.wait_for_timeout(10000)

    # ---------------------
    context.close()
    browser.close()


with sync_playwright() as playwright:
    run(playwright)
