#from generate_date_ranges import generate_date_ranges
from data_processing import load_data
from pattern_search import find_most_similar_pattern
import numpy as np
import pandas as pd
from pattern_search_plotly import plot_stock_patterns
from volatility import volatility

# 'numpy.ndarray'인 경우 'DataFrame'으로 변환
def convert_to_dataframe(data):
    if isinstance(data, np.ndarray):
        return pd.DataFrame(data)
    return data

def params(ticker, pattern_search_start_date, pattern_search_end_date, input_start_date, input_end_date):

    # pattern_search 데이터 로드
    data_pattern, price_data_pct_change_pattern, data_eco_pattern= load_data(ticker, pattern_search_start_date, pattern_search_end_date)

    # input 데이터 로드 
    data_input, price_data_pct_change_input, data_eco_input= load_data(ticker, input_start_date, input_end_date)
    
    data_input = convert_to_dataframe(data_input)
    price_data_pct_change_input = convert_to_dataframe(price_data_pct_change_input)
    data_eco_input = convert_to_dataframe(data_eco_input)

    data_pattern = convert_to_dataframe(data_pattern)
    price_data_pct_change_pattern = convert_to_dataframe(price_data_pct_change_pattern)
    data_eco_pattern = convert_to_dataframe(data_eco_pattern)

    # 결측치 처리
    data_input.ffill(inplace=True)  # 또는 bfill
    price_data_pct_change_input.ffill(inplace=True)  # 또는 bfill
    data_eco_input.ffill(inplace=True)  # 또는 bfill

    data_pattern.ffill(inplace=True)
    price_data_pct_change_pattern.ffill(inplace=True)
    data_eco_pattern.ffill(inplace=True)

    # 입력 데이터 기간의 길이
    n_days = len(data_input)

    # 입력 데이터에서 패턴 추출
    current_window = price_data_pct_change_input
    current_eco = data_eco_input

    # 검색 기간에서 입력 데이터 기간을 제외하기 위한 마스크 생성
    mask = (data_pattern.index < input_start_date) | (data_pattern.index > input_end_date)

    # mask의 길이를 맞추기 위해 데이터프레임의 길이에 맞는지 확인하고, 부족한 경우 False 값으로 채우기
    if len(mask) < len(data_eco_pattern):
        mask = np.append(mask, [False] * (len(data_eco_pattern) - len(mask)))

    # 각 데이터프레임에 대해 동일한 길이로 마스크 적용
    data_pattern_filtered = data_pattern[mask[:len(data_pattern)]]
    price_data_pct_change_pattern_filtered = price_data_pct_change_pattern[mask[:len(price_data_pct_change_pattern)]]
    data_eco_pattern_filtered = data_eco_pattern[mask[:len(data_eco_pattern)]]

    # 패턴 검색 및 시각화
    min_distances = find_most_similar_pattern(
        n_days,
        price_data_pct_change_pattern_filtered,
        #data_eco_pattern_filtered,
        current_window,
        #current_eco
    )


    return min_distances, data_pattern_filtered, data_pattern

def extract_high_volatility_ranges(data_pattern):
    high_volatility_dates = volatility(data_pattern)
    high_volatility_ranges = [
        (pd.Timestamp(dates[0]).date(), pd.Timestamp(dates[-1]).date())
        for dates in high_volatility_dates
    ]
    return high_volatility_ranges

def params_volatility(ticker, pattern_start_date, pattern_end_date, input_start_date, input_end_date):
    data_pattern, price_data_pct_change_pattern, data_eco_pattern = load_data(ticker, pattern_start_date, pattern_end_date)
    data_input, price_data_pct_change_input, data_eco_input = load_data(ticker, input_start_date, input_end_date)

    # DataFrame 변환 및 결측치 처리
    data_input = convert_to_dataframe(data_input).ffill()
    price_data_pct_change_input = convert_to_dataframe(price_data_pct_change_input).ffill()
    data_eco_input = convert_to_dataframe(data_eco_input).ffill()
    data_pattern = convert_to_dataframe(data_pattern).ffill()
    price_data_pct_change_pattern = convert_to_dataframe(price_data_pct_change_pattern).ffill()
    data_eco_pattern = convert_to_dataframe(data_eco_pattern).ffill()

    high_volatility_ranges = extract_high_volatility_ranges(data_pattern)

    n_days = len(data_input)
    mask = (data_pattern.index < input_start_date) | (data_pattern.index >input_end_date)
    if len(mask) <len(data_eco_pattern):
        mask = np.append(mask, [False] * (len(data_eco_pattern) - len(mask)))
    
    data_pattern_filtered = data_pattern[mask[:len(data_pattern)]]
    price_data_pct_change_pattern_filtered = price_data_pct_change_pattern[mask[:len(price_data_pct_change_pattern)]]

    min_distances = find_most_similar_pattern(
        n_days,
        price_data_pct_change_pattern_filtered,
        price_data_pct_change_input
    )
    return min_distances, data_pattern_filtered, data_input, high_volatility_ranges