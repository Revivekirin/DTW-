import numpy as np
from fastdtw import fastdtw
from scipy.spatial.distance import euclidean
import pandas as pd
from evaluation import calculate_similarity
import yfinance as yf
import matplotlib.pyplot as plt

def normalize(ts):
    return (ts - ts.min()) / (ts.max() - ts.min())

def dtw_distance(ts1, ts2, ts1_ta_trend, ts2_ta_trend, ts1_vol, ts2_vol, data_eco1, data_eco2, w1=0.4, w2=0.2, w3=0.2):
    # 결측치와 inf 값을 0으로 대체
    ts1_normalized = np.nan_to_num(normalize(ts1))
    ts2_normalized = np.nan_to_num(normalize(ts2))
    ts1_ta_trend_nor = np.nan_to_num(normalize(ts1_ta_trend))
    ts2_ta_trend_nor = np.nan_to_num(normalize(ts2_ta_trend))
    ts1_vol_nor = np.nan_to_num(normalize(ts1_vol))
    ts2_vol_nor = np.nan_to_num(normalize(ts2_vol))
    eco1_nor = np.nan_to_num(normalize(data_eco1))
    eco2_nor = np.nan_to_num(normalize(data_eco2))

    distance_pct_change, _ = fastdtw(ts1_normalized.reshape(-1, 1), ts2_normalized.reshape(-1, 1), dist=euclidean)
    distance_trend, _ = fastdtw(ts1_ta_trend_nor, ts2_ta_trend_nor, dist=euclidean)
    distance_vol, _ = fastdtw(ts1_vol_nor, ts2_vol_nor, dist=euclidean)
    distance_eco, _ = fastdtw(eco1_nor, eco2_nor, dist=euclidean)
    
    distance = w1 * distance_pct_change + w2 * distance_trend + w3 * distance_vol + (1 - w1 - w2 - w3) * distance_eco
    return distance

def find_most_similar_pattern(n_days, price_data_pct_change, trend_features, vol_features, data_eco, subsequent_days):
    # 현재 창의 주가 변화 및 관련 특성들
    current_window = price_data_pct_change[-n_days:].values
    current_trend = trend_features[-n_days:]
    current_vol = vol_features[-n_days:]
    current_eco = data_eco[-n_days:]

    # 가장 유사한 3개의 패턴을 저장하기 위한 초기화
    min_distances = [(float('inf'), None)] * 3

    # 패턴 검색 범위 설정 (데이터 길이 제한 고려)
    for start_index in range(len(price_data_pct_change) - 2 * n_days - subsequent_days):
        past_window = price_data_pct_change[start_index:start_index + n_days].values
        past_trend = trend_features[start_index:start_index + n_days]
        past_vol = vol_features[start_index:start_index + n_days]
        past_eco = data_eco[start_index:start_index + n_days]

        # DTW 거리 계산 (현재 창과 과거 창 비교)
        distance = dtw_distance(
            current_window, past_window,
            current_trend, past_trend,
            current_vol, past_vol,
            current_eco, past_eco
        )

        # 가장 가까운 3개 패턴 업데이트
        for i, (min_distance, _) in enumerate(min_distances):
            if distance < min_distance:
                min_distances[i] = (distance, start_index)
                min_distances = sorted(min_distances, key=lambda x: x[0])  # 거리 기준으로 정렬
                break

    if not min_distances:
        print(f"No valid patterns found for {n_days} days window.")
    
    return min_distances


# def plot_stock_patterns(ticker, price_data, price_data_pct_change, min_distances, n_days, subsequent_days, subsequent_prices_all):
#     """
#     비슷한 패턴을 가진 주가 구간을 시각화하여 출력하는 함수.
    
#     :param ticker: 주식 티커
#     :param price_data: 원본 주가 데이터 (데이터프레임)
#     :param price_data_pct_change: 주가의 퍼센트 변화 (데이터프레임)
#     :param min_distances: 추출된 유사 패턴 정보
#     :param n_days: 비교할 창 크기
#     :param subsequent_days: 예측할 후속일 수
#     :param subsequent_prices_all: 예측한 모든 패턴의 후속 주가 데이터 저장소
#     """

#     subsequent_prices = []

#     plt.figure(figsize=(12, 8))
    
#     # 각 패턴에 대해 처리
#     for i, (_, start_index) in enumerate(min_distances):
#         if start_index is not None and start_index + n_days + subsequent_days <= len(price_data):
#             # 과거 창의 시작과 끝 날짜 설정
#             past_window_start_date = price_data.index[start_index]
#             past_window_end_date = price_data.index[start_index + n_days + subsequent_days]

#             # 해당 창의 주가 데이터 추출 및 시각화
#             past_window = price_data_pct_change[start_index:start_index + n_days + subsequent_days]
#             reindexed_current_window = (past_window + 1).cumprod() * 100  # 퍼센트 변화를 원본 스케일로 변환

#             # 후속 주가 데이터 추출 및 저장
#             subsequent_window = price_data_pct_change[start_index + n_days: start_index + n_days + subsequent_days].values
#             subsequent_prices.append(subsequent_window)
#             subsequent_prices_all.append(subsequent_window)

#             # 추출된 패턴을 시각화
#             plt.plot(price_data.index[start_index:start_index + n_days + subsequent_days], reindexed_current_window, label=f"Pattern {i+1}: {past_window_start_date} - {past_window_end_date}")

#     # 3개 패턴의 예측값을 기반으로 중앙값 계산 후 시각화
#     subsequent_prices = np.array(subsequent_prices)
#     if subsequent_prices.size > 0:
#         median_subsequent_prices = np.median(subsequent_prices, axis=0)
#         median_subsequent_prices_cum = (median_subsequent_prices + 1).cumprod() * reindexed_current_window.iloc[n_days - 1]
#         plt.plot(price_data.index[start_index + n_days:start_index + n_days + subsequent_days], median_subsequent_prices_cum, 'k--', label="Median Predicted Pattern", linewidth=2)

#     plt.title(f"{ticker} Stock Patterns and Predicted Trends")
#     plt.xlabel("Date")
#     plt.ylabel("Price")
#     plt.legend()
#     plt.grid(True)
#     plt.show()


def plot_stock_patterns_and_extract_periods(ticker, price_data, price_data_pct_change, min_distances, n_days, subsequent_days, subsequent_prices_all):
    """
    비슷한 패턴을 가진 시기와 해당 시기의 시작일과 종료일을 추출하는 함수.
    
    :param ticker: 주식 티커
    :param price_data: 원본 주가 데이터 (데이터프레임)
    :param price_data_pct_change: 주가의 퍼센트 변화 (데이터프레임)
    :param min_distances: 추출된 유사 패턴 정보
    :param n_days: 비교할 창 크기
    :param subsequent_days: 예측할 후속일 수
    :param subsequent_prices_all: 예측한 모든 패턴의 후속 주가 데이터 저장소
    :return: 유사 패턴의 시작 날짜와 종료 날짜
    """
    subsequent_prices = []
    similar_periods = []  # 유사 패턴의 시기를 저장할 리스트

    plt.figure(figsize=(12, 8))
    
    for i, (_, start_index) in enumerate(min_distances):
        if start_index is not None and start_index + n_days + subsequent_days <= len(price_data):
            # 과거 창의 시작과 종료 날짜
            past_window_start_date = price_data.index[start_index]
            past_window_end_date = price_data.index[start_index + n_days + subsequent_days - 1]

            # 해당 구간의 주가 변화 추출 및 시각화
            past_window = price_data_pct_change[start_index:start_index + n_days + subsequent_days]
            reindexed_current_window = (past_window + 1).cumprod() * 100

            # 후속 주가 데이터 추출 및 저장
            subsequent_window = price_data_pct_change[start_index + n_days: start_index + n_days + subsequent_days].values
            subsequent_prices.append(subsequent_window)
            subsequent_prices_all.append(subsequent_window)

            # 추출된 패턴을 시각화
            #plt.plot(price_data.index[start_index:start_index + n_days + subsequent_days], reindexed_current_window, label=f"Pattern {i+1}: {past_window_start_date} - {past_window_end_date}")

            # 유사 패턴의 시작일과 종료일을 저장
            similar_periods.append((past_window_start_date, past_window_end_date))

    
    return similar_periods




def plot_results_with_mean_and_actual_data(ticker, current_window, indexed_subsequent_prices, subsequent_mean_cum, 
                                           days_to, subsequent_days, subsequent_prices_all, actual_prices, 
                                           start_date, end_date):
    # yfinance에서 1년간의 주가 데이터를 가져옴
    stock_data = yf.download(ticker, start=start_date, end=end_date)
    
    # 마지막 20일을 제외한 데이터로 예측
    stock_data_without_last_20 = stock_data['Close'][:-30]  # 마지막 20일 제외
    
    # 날짜 범위 설정
    current_length = len(current_window)
    future_length = subsequent_days
    total_length = current_length + future_length

    # 실제 마지막 20일 데이터
    actual_20days_prices = stock_data['Close'][-30:]
    actual_dates = range(current_length, total_length)

    # 각 예측된 주가지수 그리기 (0, 3, 6번째 인덱스만)
    indices_to_plot = [0, 3, 6]
    mean_predicted_prices = np.zeros(subsequent_days)
    predictions_to_plot = []


    for idx in indices_to_plot:
        if idx < len(subsequent_prices_all):
            prices = subsequent_prices_all[idx]
            actual_indexed_price = (prices + 1).cumprod() * stock_data_without_last_20.iloc[-1]  # 마지막 주가 기준으로 예측값 계산
            predictions_to_plot.append(actual_indexed_price)
            
            # 3개의 예측값 평균 계산
            mean_predicted_prices += actual_indexed_price

    # 3개의 예측값 평균
    mean_predicted_prices /= len(indices_to_plot)
    
    # 유사도 계산
    mae, rmse, differences = calculate_similarity(mean_predicted_prices, actual_20days_prices)
    
    print(f"MAE (Mean Absolute Error): {mae}")
    print(f"RMSE (Root Mean Squared Error): {rmse}")
    print(f"Differences: {differences}")


    return mae, rmse, differences

