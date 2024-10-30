import os
import sys
import urllib.request
import json
from datetime import datetime
from transformers import AutoModelForSeq2SeqLM, AutoTokenizer
from newspaper import Article 
from typing import List, Optional, Dict

def filter_news_by_date(news_data: dict, start_date: Optional[datetime], end_date: Optional[datetime]) -> List[dict]:
    filtered_news = []
    for item in news_data['items']:
        pub_date = datetime.strptime(item['pubDate'], "%a, %d %b %Y %H:%M:%S +0900")
        print(pub_date)
        if (pub_date >= start_date) and (pub_date <= end_date):
            filtered_news.append(item)
            print(filtered_news)
    return filtered_news

def get_news_data(query: str, display: int = 20, start_date: Optional[datetime] = None, end_date: Optional[datetime] = None) -> List[dict]:
    encText = urllib.parse.quote(query)
    all_filtered_news = []
    start = 1

    while True:
        print("Fetching news data...")
        url = f"https://openapi.naver.com/v1/search/news.json?query={encText}&display={display}&start={start}"
        request = urllib.request.Request(url)
        request.add_header("X-Naver-Client-Id", "gzXIxnMcjyEU2yijI6Qq")
        request.add_header("X-Naver-Client-Secret", "gBPFUxZTc6")

        try:
            response = urllib.request.urlopen(request)
            rescode = response.getcode()
            if rescode != 200:
                print("Error Code: " + str(rescode))
                break
            
            response_body = response.read()
            news_data = json.loads(response_body.decode('utf-8'))
            print("Fetched news data:", news_data)

            filtered_news = filter_news_by_date(news_data, start_date, end_date)
            all_filtered_news.extend(filtered_news)
            print("Filtered news:", all_filtered_news)

            # 종료 조건
            if len(all_filtered_news) >=display or len(news_data['items'])<display:
                break
            start += display

        except json.JSONDecodeError as e:
            print(f"Failed to parse JSON response. Error: {e}")
            break
        except Exception as e:
            print(f"An error occurred: {e}")
            break

    return all_filtered_news[:display]


def get_article_text(url: str) -> str:
    """가사 본문을 크롤링"""
    try:
        article = Article(url)
        article.download()
        article.parse()
        return article.text
    except Exception as e:
        print(f"Failed to fetch article from {url}. Error: {e}")
        return ""

def get_news_summary(query: str, start_date: Optional[datetime], end_date: Optional[datetime]) -> List[dict]:
    news_data = get_news_data(query, start_date=start_date, end_date=end_date)
    print("최종 뉴스 데이터", news_data)

    if news_data:
        filtered_news = news_data
        full_text=""
        for news in filtered_news:
            article_text = get_article_text(news['originallink'])
            first_paragraph = article_text.split('\n\n')[0]
            full_text+=first_paragraph+"\n\n"
        
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

        return summary
    return "뉴스 데이터가 없습니다"