from datetime import datetime
from transformers import AutoModelForSeq2SeqLM, AutoTokenizer
from newspaper import Article 
from typing import List, Optional, Dict
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import time
import os

# 환경 변수 설정
os.environ["TOKENIZERS_PARALLELISM"] = "false"


def get_news_data(query: str, start_date: Optional[datetime] = None, end_date: Optional[datetime] = None) -> List[dict]:
    driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()))
    news_data = []
    
    try:
        ds = start_date.strftime('%Y.%m.%d') if start_date else ''
        de = end_date.strftime('%Y.%m.%d') if end_date else ''
        url = f"https://search.naver.com/search.naver?where=news&query={query}&sm=tab_opt&sort=0&photo=0&field=0&pd=3&ds={ds}&de={de}&nso=so%3Ar%2Cp%3Afrom{ds}to{de}"
        driver.get(url)
        time.sleep(2)

        news_items = driver.find_elements(By.CSS_SELECTOR, 'div.news_area')[:3]

        for item in news_items:
            try:
                title = item.find_element(By.CSS_SELECTOR, 'a.news_tit').text
                link = item.find_element(By.CSS_SELECTOR, 'a.news_tit').get_attribute('href')
                
                driver.execute_script("window.open(arguments[0]);", link)
                time.sleep(3)

                current_window = driver.current_window_handle
                driver.switch_to.window(driver.window_handles[-1])

                article_text = get_article_text(link)
                paragraphs = article_text.split('\n\n') if article_text else ["", ""]  # 기본값으로 빈 문단을 설정
                
                # 첫 번째와 두 번째 문단을 가져옵니다.
                first_paragraph = paragraphs[0] if len(paragraphs) > 0 else ""
                second_paragraph = paragraphs[1] if len(paragraphs) > 1 else ""

                news_data.append({
                    'title': title,
                    'originallink': link,
                    'first_paragraph': first_paragraph
                })

                driver.close()
                driver.switch_to.window(current_window)
            except Exception as e:
                print(f"Error while processing news item: {e}")
                continue  # Skip to the next news item in case of an error
    except Exception as e:
        print(f"Failed to fetch news data from Naver: {e}")
    finally:
        driver.quit()  # Ensure the driver quits even if there is an error
    return news_data




def get_article_text(url: str) -> str:
    try:
        article = Article(url)
        article.download()
        article.parse()
        return article.text
    except Exception as e:
        print(f"Failed to fetch article from {url}. Error: {e}")
        return ""


def get_news_summary(query: str, start_date: Optional[datetime], end_date: Optional[datetime]) -> List[dict]:
    summaries = []
    try:
        news_data = get_news_data(query, start_date=start_date, end_date=end_date)
        if not news_data:
            print("뉴스 데이터가 없습니다.")
            return []

        full_text = ""
        for news in news_data:
            full_text += news['title'] + "\n" + news['first_paragraph'] + "\n\n"
            print(full_text)
        
            tokenizer = AutoTokenizer.from_pretrained("noahkim/KoT5_news_summarization")
            model = AutoModelForSeq2SeqLM.from_pretrained("noahkim/KoT5_news_summarization")

            prompt = f"""
                당신은 금융 분야의 요약 전문가입니다. 

                아래의 금융 관련 텍스트를 읽고, 다음 지침에 따라 요약해 주세요:
                1. 전체 내용을 50단어 이내로 요약한 'summary' 필드를 작성해 주세요.
                2. 핵심 내용을 5-10개 간결하게 정리해서 'key_points' 필드에 작성해 주세요.
                3. 각 key_points 내용은 한 문장으로, 20단어를 넘지 않도록 해주세요.
                4. 텍스트의 핵심 키워드와 관련된 단어나 개념을 10개 내외로 'tags' 필드에 추가해 주세요.
                5. 전문 용어가 있다면 간단히 설명을 덧붙여 주세요.
                6. 숫자나 통계가 있다면 반드시 포함시켜 주세요.
                7. 요약은 객관적이고 중립적인 톤을 유지해 주세요.
                8. 연관된 회사가 있으면 해당 회사와의 관계를 설명해 주세요.
                9. {query}가 들어간 문장을 우선적으로 분석해 주시오.

                응답은 반드시 아래의 JSON 형식을 따라 주세요: 
                {{
                    "summary": "전체 내용 요약 (50단어 이내)",
                    "key_points": [
                        "핵심 포인트 1 (20단어 이내)",
                        "핵심 포인트 2 (20단어 이내)",
                        "핵심 포인트 3 (20단어 이내)",
                        "핵심 포인트 4 (20단어 이내)",
                        "핵심 포인트 5 (20단어 이내)",
                        ...
                    ],
                    "tags": ["태그1", "태그2", "태그3", ...]
                }}

                텍스트: 
                {full_text}

                위 지침에 따라 JSON 형식으로 요약해 주세요. 
                """
            inputs = tokenizer(prompt, return_tensors="pt", max_length=3400, truncation=True)
            summary_ids = model.generate(inputs['input_ids'], max_length=1500, num_beams=4, early_stopping=True)
            summary = tokenizer.decode(summary_ids[0], skip_special_tokens=True)
            summaries.append(summary)

        return summaries
    except Exception as e:
        print(f"Failed to generate summary: {e}")
        return ""


def get_news_summaries_for_volatility_periods(high_volatility_periods: List[tuple], query:str) -> List[dict]:
    summaries = []
    for start_date, end_date in high_volatility_periods:
        try:
            summary = get_news_summary(query, start_date, end_date)
            summaries.append({
                'start_date': start_date,
                'end_date': end_date,
                'summary': summary
            })
        except Exception as e:
            print(f"Failed to get news summary for period {start_date} - {end_date}: {e}")
    return summaries
