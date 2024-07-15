from seleniumbase import SB
from selenium.webdriver.common.keys import Keys
import pysubs2
import re

WAIT_FOR_CONFIG = 5
CHARACTER_LIMIT_PER_LINE = 20
SLEEP_TIME = 0.2
SRT_FILE = "House.of.the.Dragon.S02E05.1080p.WEB.H264-SuccessfulCrab.srt"

def translate_text(text, sb):
    try:
        while True:
            input_text = sb.get_text('d-textarea[name="source"]')
            if input_text.strip().startswith("Çevirmek için yaz.") or input_text.strip().startswith("Type to translate."):
                break
            else:
                #### clear the d-textarea[name="source"]
                sb.click('d-textarea[name="source"]')
                # push ctrl + a to select all
                sb.send_keys('d-textarea[name="source"]', Keys.COMMAND + 'a')
                # push delete to delete all
                sb.send_keys('d-textarea[name="source"]', Keys.DELETE)
        
        
        sb.type('d-textarea[name="source"]', text)
        
        # Wait for translation to complete
        while True:
            result = sb.get_text('d-textarea[name="target"]')
            if len(result.strip()) > 1:
                break
            sb.sleep(SLEEP_TIME)
        
        #### alternative way to clear the textarea
        # sb.refresh()
        # sb.sleep(1)
        return result

    except Exception as e:
        print(f"Error translating text: {e}")
        sb.save_screenshot("error_screenshot.png")
        sb.refresh()
        sb.sleep(WAIT_FOR_CONFIG)
        return translate_text(text, sb)
    
def extract_tags_and_text(text):
    # remove \N from text and add whitespace instead of it
    text = re.sub(r'\\N', ' ', text)
    
    # Extract tags from text
    tags = re.findall(r'{.*?}', text)
    # Extract clean text without tags
    clean_text = re.sub(r'{.*?}', '', text)
    
    return tags, clean_text

def reinsert_tags(tags, translated_text):
    result = translated_text
    
    # if result is longer than CHARACTER_LIMIT_PER_LINE, split it into two lines by changing the last whitespace with \N
    if len(result) > CHARACTER_LIMIT_PER_LINE:
        half_of_text = len(result) // 2
        # Find the first occurrence of space in the second half of the result string
        first_space_index = result[half_of_text:].find(' ')
    
        if first_space_index != -1:  # Ensure a space was found
            # Adjust index to the second half of the result string
            first_space_index += half_of_text
            
            # Split the result string at the found space
            result = result[:first_space_index] + '\\N' + result[first_space_index+1:]
    
    if len(tags) == 2:
        result = tags[0] + translated_text + tags[1]
    
    return result
        
    
    
with SB(uc=True) as sb:
    sb.open("https://www.deepl.com/translator")
    sb.sleep(WAIT_FOR_CONFIG)
    
    subs = pysubs2.load(SRT_FILE)
    
    #### TEST
    # print(subs[5].text)
    # tags_positions, clean_text = extract_tags_and_text(subs[5].text)
    # translated_text = translate_text(clean_text, sb)
    # subs[5].text = reinsert_tags(tags_positions, translated_text)
    # print(subs[5].text)
    
    counter = 0
    try:
        for line in subs:
            #  every 100 lines, refresh the page
            # if counter % 100 == 0:
            #     sb.refresh()
            #     sb.sleep(WAIT_FOR_CONFIG)
            
            tags, clean_text = extract_tags_and_text(line.text)
            translated_text = translate_text(clean_text, sb)
            print(f"Translated text: {translated_text}")
            line.text = reinsert_tags(tags, translated_text)
            counter += 1
        subs.save(SRT_FILE.replace('.srt', '_translated.srt'))
    except Exception as e:
        print(f"Error translating srt file: {e}")
        subs.save(SRT_FILE.replace('.srt', '_translated.srt'))
    finally:
        exit()
                                                                   