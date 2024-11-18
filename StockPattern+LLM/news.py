from datetime import datetime
from newspaper import Article 
from typing import List, Optional
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import time
import os
import torch
import requests
import json

torch.cuda.empty_cache()

# 환경 변수 설정
os.environ["TOKENIZERS_PARALLELISM"] = "false"

def get_news_data(qur: str, start_date: Optional[datetime] = None, end_date: Optional[datetime] = None) -> List[dict]:
    driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()))
    news_data = []
    query = qur+"주가"
    
    try:
        ds = start_date.strftime('%Y.%m.%d') if start_date else ''
        de = end_date.strftime('%Y.%m.%d') if end_date else ''
        url = f"https://search.naver.com/search.naver?where=news&query={query}&sm=tab_opt&sort=0&photo=0&field=0&pd=3&ds={ds}&de={de}&nso=so%3Ar%2Cp%3Afrom{ds}to{de}"
        driver.get(url)

        # 명시적 대기 사용
        WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.CSS_SELECTOR, 'div.news_area'))
        )

        news_items = driver.find_elements(By.CSS_SELECTOR, 'div.news_area')[:2]

        for item in news_items:
            try:
                title = item.find_element(By.CSS_SELECTOR, 'a.news_tit').text
                link = item.find_element(By.CSS_SELECTOR, 'a.news_tit').get_attribute('href')
                
                driver.execute_script("window.open(arguments[0]);", link)
                time.sleep(2)

                current_window = driver.current_window_handle
                driver.switch_to.window(driver.window_handles[-1])

                article_text = get_article_text(link)
                paragraphs = article_text.split('\n\n') if article_text else ["", ""]  # 기본값으로 빈 문단을 설정
                
                # 첫 번째와 두 번째 문단을 가져옵니다.
                first_paragraph = paragraphs[0] if len(paragraphs) > 0 else ""
                second_paragraph = paragraphs[1] if len(paragraphs)>0 else ""

                news_data.append({
                    'title': title,
                    'originallink': link,
                    #'paragraphs' :paragraphs,
                    'first_paragraph': first_paragraph,
                    'second_paragraph':second_paragraph,
                    # 'third_paragraph':third_paragraph,
                })

                driver.close()
                driver.switch_to.window(current_window)
            except Exception as e:
                print(f"Error while processing news item: {e}")
                continue 
    except Exception as e:
        print(f"Failed to fetch news data from Naver: {e}")
    finally:
        driver.quit()  
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


colab_url = 'https://3de2-34-74-138-59.ngrok-free.app/data'

def get_news_summaries_for_periods(high_volatility_periods: List[tuple], query: str) -> List[dict]:
    summaries = []
    for start_date, end_date in high_volatility_periods:
        try:
            # 뉴스 데이터를 가져옵니다.
            news_data = get_news_data(query, start_date=start_date, end_date=end_date)

            if not news_data:
                print("뉴스 데이터가 없습니다.")
                continue

            # 뉴스의 제목과 본문을 결합하여 full_text 생성
            full_text = ""
            for news in news_data:
                #paragraphs = ' '.join(news['paragraphs']) if isinstance(news['paragraphs'], list) else news['paragraphs']
                first_paragraph = ' '.join(news['first_paragraph']) if isinstance(news['first_paragraph'], list) else news['first_paragraph']
                second_paragraph = ' '.join(news['second_paragraph']) if isinstance(news['second_paragraph'], list) else news['second_paragraph']
                full_text += news['title'] + first_paragraph+second_paragraph+"\n\n"
            
            # Colab 서버로 full_text를 전송하여 요약을 요청
            response = requests.post(
                colab_url, 
                json={
                    'query': query,
                    'full_text': full_text,
                }
            )

            # Colab 서버의 응답 확인 및 요약 데이터 저장
            if response.status_code == 200:
                summary = response.json().get('summary', '')
                label = response.json().get('label', '')
                summaries.append({
                    'start_date': start_date,
                    'end_date': end_date,
                    'summary': summary,
                    'label': label
                })
            else:
                print(f"Failed to get summary from Colab server. Status code: {response.status_code}")

        except Exception as e:
            print(f"Failed to get news summary for period {start_date} - {end_date}: {e}")

    return summaries
