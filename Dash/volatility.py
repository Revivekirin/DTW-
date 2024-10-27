import pandas as pd
import numpy as np

def volatility(stock_data, window_size=6, threshold_multiplier=2):
    """
    주식 데이터에서 변동성이 큰 구간의 날짜를 반환합니다.

    Parameters:
    - stock_data (pd.DataFrame): 'Date'와 'Close' 열이 포함된 주가 데이터.
    - window_size (int): 이동 표준 편차를 계산할 기간 (기본값: 5일).
    - threshold_multiplier (float): 평균 이동 표준 편차에 대한 임계값을 설정하는 배수 (기본값: 2배).

    Returns:
    - high_volatility_dates (list of lists): 변동성이 큰 구간의 날짜 리스트.
    """
    
    # 이동 표준 편차 계산
    stock_data['volatility'] = stock_data['Close'].rolling(window=window_size).std()
    stock_data = stock_data.dropna()
    
    # 평균과 임계값 설정
    mean_volatility = stock_data['volatility'].mean()
    threshold = mean_volatility * threshold_multiplier

    # 변동성이 임계값 이상인 날짜 찾기
    high_volatility_periods = []
    current_dates = []

    for date, row in stock_data.iterrows():
        if row['volatility'] >= threshold:
            current_dates.append(date)  # 변동성이 큰 날을 추가
        else:
            if current_dates:
                extended_dates = current_dates[-1]-pd.DateOffset(days=6)
                high_volatility_periods.append(pd.date_range(start=extended_dates, end=current_dates[-1]))
                current_dates=[]

    # 마지막 구간이 끝나지 않은 경우 추가
    if current_dates:
        extended_dates = current_dates[-1]-pd.DateOffset(days=6)
        high_volatility_periods.append(pd.date_range(start=extended_dates, end=current_dates[-1]))

    return high_volatility_periods

