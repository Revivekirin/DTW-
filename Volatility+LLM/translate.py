from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from webdriver_manager.chrome import ChromeDriverManager
import os

os.environ["TOKENIZERS_PARALLELISM"] = "false"

def translate(text_to_translate: str) -> str:
    # ChromeDriver를 자동 설치하여 설정
    driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()))

    # URL에 텍스트를 포함하여 Papago 웹사이트 접속
    encoded_text = text_to_translate.replace(" ", "%20")  # URL 인코딩
    url = f"https://papago.naver.com/?sk=en&tk=ko&hn=1&st={encoded_text}"
    driver.get(url)

    # 번역 결과가 나타날 때까지 대기 (최대 15초)
    try:
        # 번역된 텍스트가 나타날 때까지 기다림
        output_box = WebDriverWait(driver, 15).until(
            EC.presence_of_element_located((By.CSS_SELECTOR, ".txtTarget"))
        )
        translated_text = output_box.text  # 번역 결과 텍스트 가져오기
    except:
        translated_text = "번역 결과를 찾을 수 없습니다."

    print("Translated Text:", translated_text)

    # 드라이버 종료
    driver.quit()

    return translated_text

# 번역할 텍스트 예시
text_to_translate = "A global investment financial institution, Mizuho, has advised investors to purchase Intel stocks (NAS:INTC) as interest in the company's semiconductor manufacturing business is rising, despite server business concerns."
translate(text_to_translate)
