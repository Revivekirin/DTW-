from data_processing import load_data
from pattern_search import find_most_similar_pattern, plot_stock_patterns

import numpy as np
import pandas as pd


def convert_to_dataframe(data):
    """numpy 배열을 DataFrame으로 변환"""
    if isinstance(data, np.ndarray):
        return pd.DataFrame(data)
    return data

def fill_missing_values(*dataframes):
    """모든 데이터프레임에 대해 결측치 채우기"""
    for df in dataframes:
        df.bfill(inplace=True)  # 또는 bfill
    return dataframes

def load_and_process_data(ticker, start_date, end_date):
    """데이터 로드 및 전처리"""
    data, price_data_pct_change, data_eco, trend_features, vol_features = load_data(ticker, start_date, end_date)
    data, price_data_pct_change, data_eco, trend_features, vol_features = fill_missing_values(
        convert_to_dataframe(data),
        convert_to_dataframe(price_data_pct_change),
        convert_to_dataframe(data_eco),
        convert_to_dataframe(trend_features),
        convert_to_dataframe(vol_features)
    )
    return data, price_data_pct_change, data_eco, trend_features, vol_features

def filter_data_by_mask(mask, *dataframes):
    """주어진 마스크를 적용하여 데이터프레임 필터링"""
    return [df[mask[:len(df)]] for df in dataframes]

def print_similar_patterns(data_pattern, min_distances, n_days):
    """유사한 패턴의 날짜와 거리를 출력"""
    similar_patterns = []
    for distance, start_index in min_distances:
        if start_index is not None:
            start_date = data_pattern.index[start_index]
            end_date = data_pattern.index[start_index + n_days - 1]
            print(f"유사한 패턴 {start_index}: {start_date} ~ {end_date} (거리: {distance})")
            similar_patterns.append((start_date, end_date, distance))
    return similar_patterns

def params(ticker, pattern_search_start_date, pattern_search_end_date):

    # 데이터 로드
    data_pattern, price_data_pct_change_pattern, data_eco_pattern, trend_features_pattern, vol_features_pattern = \
        load_and_process_data(ticker, pattern_search_start_date, pattern_search_end_date)

    # 데이터에서 최근 5일치를 추출
    recent_data = data_pattern.tail(6)
    input_start_date = recent_data.index[0].strftime('%Y-%m-%d')
    input_end_date = recent_data.index[-1].strftime('%Y-%m-%d')

    # 새로 로드한 데이터 사용
    data_input, price_data_pct_change_input, data_eco_input, trend_features_input, vol_features_input = \
        load_and_process_data(ticker, input_start_date, input_end_date)


    # 입력 데이터 기간의 길이
    n_days = len(data_input)

    # 검색 기간에서 입력 데이터 기간을 제외하기 위한 마스크 생성
    mask = (data_pattern.index < input_start_date) | (data_pattern.index > input_end_date)
    if len(mask) < len(data_eco_pattern):
        mask = np.append(mask, [False] * (len(data_eco_pattern) - len(mask)))
    
    data_pattern_filtered, price_data_pct_change_pattern_filtered, trend_features_pattern_filtered, \
        vol_features_pattern_filtered, data_eco_pattern_filtered = filter_data_by_mask(
        mask, data_pattern, price_data_pct_change_pattern, trend_features_pattern, vol_features_pattern, data_eco_pattern
    )
    # 패턴 검색 및 시각화
    min_distances = find_most_similar_pattern(
        n_days,
        price_data_pct_change_pattern_filtered,
        trend_features_pattern_filtered,
        vol_features_pattern_filtered,
        data_eco_pattern_filtered,
        price_data_pct_change_input,
        trend_features_input,
        vol_features_input,
        data_eco_input
    )

    print(f"입력된 기간과 유사한 패턴을 찾았습니다: {min_distances}")
    # 유사한 패턴의 시작일, 종료일, 거리 반환
    similar_patterns = print_similar_patterns(data_pattern, min_distances, n_days)

    #그래프 그리기
    plot_stock_patterns(ticker, data_input, data_pattern_filtered, min_distances, n_days, data_pattern)  

    # 결과 반환
    return similar_patterns
