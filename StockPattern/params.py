from generate_date_ranges import generate_date_ranges
from data_processing import load_data
from pattern_search import find_most_similar_pattern, plot_stock_patterns
import numpy as np
import pandas as pd

def params(ticker):
    # 초기 날짜 설정
    pattern_search_start_date = "2023-09-22"
    pattern_search_end_date = "2024-09-22"

    # 데이터 로드
    data_pattern, price_data_pct_change_pattern, data_eco_pattern, trend_features_pattern, vol_features_pattern = load_data(ticker, pattern_search_start_date, pattern_search_end_date)

    # 데이터에서 최근 5일치를 추출
    recent_data = data_pattern.tail(6)

    # input_start_date와 input_end_date 재설정
    input_start_date = recent_data.index[0].strftime('%Y-%m-%d')
    input_end_date = recent_data.index[-1].strftime('%Y-%m-%d')

    # 새로 로드한 데이터 사용
    data_input, price_data_pct_change_input, data_eco_input, trend_features_input, vol_features_input = load_data(ticker, input_start_date, input_end_date)


    # 'numpy.ndarray'인 경우 'DataFrame'으로 변환
    def convert_to_dataframe(data):
        if isinstance(data, np.ndarray):
            return pd.DataFrame(data)
        return data
    
    data_input = convert_to_dataframe(data_input)
    price_data_pct_change_input = convert_to_dataframe(price_data_pct_change_input)
    data_eco_input = convert_to_dataframe(data_eco_input)
    trend_features_input = convert_to_dataframe(trend_features_input)
    vol_features_input = convert_to_dataframe(vol_features_input)

    data_pattern = convert_to_dataframe(data_pattern)
    price_data_pct_change_pattern = convert_to_dataframe(price_data_pct_change_pattern)
    data_eco_pattern = convert_to_dataframe(data_eco_pattern)
    trend_features_pattern = convert_to_dataframe(trend_features_pattern)
    vol_features_pattern = convert_to_dataframe(vol_features_pattern)

    # 결측치 처리
    data_input.ffill(inplace=True)  # 또는 bfill
    price_data_pct_change_input.ffill(inplace=True)  # 또는 bfill
    data_eco_input.ffill(inplace=True)  # 또는 bfill
    trend_features_input.ffill(inplace=True)  # 또는 bfill
    vol_features_input.ffill(inplace=True)  # 또는 bfill

    data_pattern.ffill(inplace=True)
    price_data_pct_change_pattern.ffill(inplace=True)
    data_eco_pattern.ffill(inplace=True)
    trend_features_pattern.ffill(inplace=True)
    vol_features_pattern.ffill(inplace=True)

    # 입력 데이터 기간의 길이
    n_days = len(data_input)
    print(data_input)

    # 입력 데이터에서 패턴 추출
    current_window = price_data_pct_change_input
    current_trend = trend_features_input
    current_vol = vol_features_input
    current_eco = data_eco_input

    # 검색 기간에서 입력 데이터 기간을 제외하기 위한 마스크 생성
    mask = (data_pattern.index < input_start_date) | (data_pattern.index > input_end_date)

    # mask의 길이를 맞추기 위해 데이터프레임의 길이에 맞는지 확인하고, 부족한 경우 False 값으로 채우기
    if len(mask) < len(data_eco_pattern):
        mask = np.append(mask, [False] * (len(data_eco_pattern) - len(mask)))

    # 각 데이터프레임에 대해 동일한 길이로 마스크 적용
    data_pattern_filtered = data_pattern[mask[:len(data_pattern)]]
    price_data_pct_change_pattern_filtered = price_data_pct_change_pattern[mask[:len(price_data_pct_change_pattern)]]
    trend_features_pattern_filtered = trend_features_pattern[mask[:len(trend_features_pattern)]]
    vol_features_pattern_filtered = vol_features_pattern[mask[:len(vol_features_pattern)]]
    data_eco_pattern_filtered = data_eco_pattern[mask[:len(data_eco_pattern)]]

    # 패턴 검색 및 시각화
    min_distances = find_most_similar_pattern(
        n_days,
        price_data_pct_change_pattern_filtered,
        trend_features_pattern_filtered,
        vol_features_pattern_filtered,
        data_eco_pattern_filtered,
        current_window,
        current_trend,
        current_vol,
        current_eco
    )

    print(f"입력된 기간과 유사한 패턴을 찾았습니다: {min_distances}")
    plot_stock_patterns(ticker, data_input, data_pattern_filtered, min_distances, n_days, data_pattern)

