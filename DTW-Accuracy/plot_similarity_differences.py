import pandas as pd
import matplotlib.pyplot as plt

import pandas as pd
import matplotlib.pyplot as plt

def plot_most_similar_pattern(ticker, most_similar_period, price_data, price_data_pct_change, subsequent_prices_all):
    """
    가장 유사한 패턴을 시각화하는 함수.
    
    :param ticker: 주식 티커
    :param most_similar_period: 가장 유사한 패턴의 시작일과 종료일 정보
    :param price_data: 원본 주가 데이터 (데이터프레임)
    :param price_data_pct_change: 주가의 퍼센트 변화 (데이터프레임)
    :param subsequent_prices_all: 예측한 모든 패턴의 후속 주가 데이터 저장소
    """
    start_date = most_similar_period['start_date']
    end_date = most_similar_period['end_date']

    # 유사한 패턴 구간 추출
    similar_window = price_data_pct_change.loc[start_date:end_date]

    plt.figure(figsize=(12, 6))
    plt.plot(similar_window.index, (similar_window + 1).cumprod() * 100, label=f"Similar Pattern: {start_date} - {end_date}")

    # 후속 주가 데이터 시각화
    for i, subsequent_window in enumerate(subsequent_prices_all):
        plt.plot(similar_window.index[-len(subsequent_window):], 
                 (subsequent_window + 1).cumprod() * (similar_window.iloc[-1] + 1) * 100,
                 linestyle='--', label=f"Subsequent Prediction {i+1}")
        
    

    plt.title(f"Most Similar Pattern for {ticker}")
    plt.xlabel("Date")
    plt.ylabel("Price (%)")
    plt.legend()
    plt.grid()
    plt.show()


def plot_similarity_differences(similarities, figsize=(14, 7), title='Differences for Each Date Range', xlabel='Date', ylabel='Difference', legend_title='Date Ranges'):

    # 유사도에서 differences를 추출하여 DataFrame으로 변환
    all_differences = pd.concat([pd.Series(sim['differences'], name=f"Start: {sim['start_date']}, End: {sim['end_date']}") for sim in similarities], axis=1)
    #print(all_differences)

    # 차이값 그래프 시각화
    all_differences.plot(figsize=figsize)
    plt.title(title)
    plt.xlabel(xlabel)
    plt.ylabel(ylabel)
    plt.legend(title=legend_title)
    plt.show()
