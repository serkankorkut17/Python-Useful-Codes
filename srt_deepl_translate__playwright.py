from playwright.sync_api import Playwright, sync_playwright, expect
import pysubs2
import re
import time

WAIT_FOR_CONFIG = 5
CHARACTER_LIMIT_PER_LINE = 20
SLEEP_TIME = 0.2
SRT_FILE = "House.of.the.Dragon.S02E05.1080p.WEB.H264-SuccessfulCrab.srt"

def extract_tags_and_text(text):
    text = re.sub(r'\\N', ' ', text)
    tags = re.findall(r'{.*?}', text)
    clean_text = re.sub(r'{.*?}', '', text)
    
    return tags, clean_text

def reinsert_tags(tags, translated_text):
    result = translated_text
    if len(result) > CHARACTER_LIMIT_PER_LINE:
        half_of_text = len(result) // 2
        first_space_index = result[half_of_text:].find(' ')
        if first_space_index != -1:
            first_space_index += half_of_text
            result = result[:first_space_index] + '\\N' + result[first_space_index+1:]
    if len(tags) == 2:
        result = tags[0] + translated_text + tags[1]
    
    return result



def translate_text(text, page):
    try:
        # clear the input field
        page.get_by_test_id("translator-source-input").get_by_label("Kaynak metni").fill("")
        # write the text to the input field
        page.get_by_test_id("translator-source-input").get_by_label("Kaynak metni").fill(text)
        page.get_by_test_id("translator-source-input").get_by_label("Kaynak metni").press("Enter")
        page.wait_for_timeout(100)
        # get the translated text
        while len(page.get_by_test_id("translator-target-input").get_by_label("Çeviri sonuçları").inner_text().strip()) <= 1:
            page.wait_for_timeout(SLEEP_TIME * 1000)
        translated_text = page.get_by_test_id("translator-target-input").get_by_label("Çeviri sonuçları").inner_text()
        # return the translated text
        return translated_text.strip()
    except Exception as e:
        print(f"Error translating text: {e}")
        time.sleep(20)
        page.screenshot(path="error_screenshot.png")
        raise e

with sync_playwright() as playwright:
    subs = pysubs2.load(SRT_FILE)
    
    browser = playwright.chromium.launch(headless=False)
    context = browser.new_context()
    page = context.new_page()
    page.goto("https://www.deepl.com/tr/translator")
    page.get_by_test_id("chrome-extension-toast").get_by_label("Kapat").click()
    
    # Choose the target language
    page.get_by_test_id("translator-target-lang-btn").click()
    page.get_by_test_id("translator-lang-option-tr").click()
    
    counter = 0
    try:
        for line in subs:
            if counter % 50 == 0:
                page.reload()
                page.wait_for_timeout(WAIT_FOR_CONFIG * 1000)
            tags, clean_text = extract_tags_and_text(line.text)
            clean_text = translate_text(clean_text, page)
            print(f"Translated text: {clean_text}")
            line.text = reinsert_tags(tags, clean_text)
            counter += 1
        # save the translated srt file
        subs.save(SRT_FILE.replace('.srt', '_translated.srt'))
    except Exception as e:
        print(f"Error translating srt file: {e}")
        subs.save(SRT_FILE.replace('.srt', '_error.srt'))
    finally:
        context.close()
        browser.close()
        exit()
