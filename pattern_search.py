import numpy as np
import matplotlib.pyplot as plt
from fastdtw import fastdtw
from scipy.spatial.distance import euclidean
import pandas as pd
from evaluation import calculate_similarity
import yfinance as yf

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

    # 유효한 패턴만 반환 (무한대 패턴 필터링)
    #min_distances = [(distance, index) for distance, index in min_distances if index is not None and distance != float('inf')]

    if not min_distances:
        print(f"No valid patterns found for {n_days} days window.")
    
    return min_distances


def plot_stock_patterns(ticker, price_data, price_data_pct_change, min_distances, n_days, subsequent_days, subsequent_prices_all):
    #fig, axs = plt.subplots(1, 2, figsize=(30, 6))
    #axs[0].plot(price_data, color='blue', label='Overall stock price')
    #color_cycle = ['red', 'pink', 'purple', 'orange', 'cyan']
    subsequent_prices = []

    for i, (_, start_index) in enumerate(min_distances):
        
        # 인덱스 범위 검사
        if start_index is not None and start_index + n_days + subsequent_days <= len(price_data):
            #color = color_cycle[i % len(color_cycle)]
            past_window_start_date = price_data.index[start_index]
            past_window_end_date = price_data.index[start_index + n_days + subsequent_days]
            #axs[0].plot(price_data[past_window_start_date:past_window_end_date], color=color, label=f"Pattern {i+1}")

            # Store subsequent prices for median calculation
            subsequent_window = price_data_pct_change[start_index + n_days: start_index + n_days + subsequent_days].values
            subsequent_prices.append(subsequent_window)
            subsequent_prices_all.append(subsequent_window)

    #axs[0].set_title(f'{ticker} Stock Price Data')
    #axs[0].set_xlabel('Date')
    #axs[0].set_ylabel('Stock Price')
    #axs[0].legend()

    for i, (_, start_index) in enumerate(min_distances):
        if start_index is not None and start_index + n_days + subsequent_days <= len(price_data):
            #color = color_cycle[i % len(color_cycle)]
            past_window = price_data_pct_change[start_index:start_index + n_days + subsequent_days]
            reindexed_current_window = (past_window + 1).cumprod() * 100
            #axs[1].plot(range(n_days), reindexed_current_window[:n_days], color=color, linewidth=3, label="Current window")

            # Compute and plot the median subsequent prices
            subsequent_prices = np.array(subsequent_prices)
            median_subsequent_prices = np.median(subsequent_prices, axis=0)
            median_subsequent_prices_cum = (median_subsequent_prices + 1).cumprod() * reindexed_current_window.iloc[n_days - 1]

            #axs[1].plot(range(n_days, n_days + subsequent_days), median_subsequent_prices_cum, color=color, linestyle='dashed', label='Median Subsequent Price Estimation')

    #axs[1].set_title(f"Most similar {n_days}-day patterns in {ticker} stock price history (aligned, reindexed)")
    #axs[1].set_xlabel("Days")
    #axs[1].set_ylabel("Reindexed Price")
    #axs[1].legend()
    #plt.show()


def plot_results_with_mean_and_actual_data(ticker, current_window, indexed_subsequent_prices, subsequent_mean_cum, 
                                           days_to, subsequent_days, subsequent_prices_all, actual_prices, 
                                           start_date, end_date):
    # yfinance에서 1년간의 주가 데이터를 가져옴
    stock_data = yf.download(ticker, start=start_date, end=end_date)
    
    # 마지막 20일을 제외한 데이터로 예측
    stock_data_without_last_20 = stock_data['Close'][:-20]  # 마지막 20일 제외
    
    # 날짜 범위 설정
    current_length = len(current_window)
    future_length = subsequent_days
    total_length = current_length + future_length

    # 실제 마지막 20일 데이터
    actual_20days_prices = stock_data['Close'][-20:]
    actual_dates = range(current_length, total_length)
    #actual_dates = range(len(stock_data_without_last_20), len(stock_data_without_last_20) + len(actual_20days_prices))

    # 각 예측된 주가지수 그리기 (0, 3, 6번째 인덱스만)
    indices_to_plot = [0, 3, 6]
    mean_predicted_prices = np.zeros(subsequent_days)
    predictions_to_plot = []

    #plt.figure(figsize=(15, 7))

    for idx in indices_to_plot:
        if idx < len(subsequent_prices_all):
            prices = subsequent_prices_all[idx]
            actual_indexed_price = (prices + 1).cumprod() * stock_data_without_last_20.iloc[-1]  # 마지막 주가 기준으로 예측값 계산
            predictions_to_plot.append(actual_indexed_price)
            #plt.plot(range(current_length, total_length), actual_indexed_price, linestyle='dotted', label=f'Prediction {idx}')
            
            # 3개의 예측값 평균 계산
            mean_predicted_prices += actual_indexed_price

    # 3개의 예측값 평균
    mean_predicted_prices /= len(indices_to_plot)
    
    # 유사도 계산
    mae, rmse, differences = calculate_similarity(mean_predicted_prices, actual_20days_prices)
    
    print(f"MAE (Mean Absolute Error): {mae}")
    print(f"RMSE (Root Mean Squared Error): {rmse}")
    print(f"Differences: {differences}")

    # 평균 예측 주가지수 그리기
    #plt.plot(range(current_length, total_length), mean_predicted_prices, color='orange', linestyle='solid', linewidth=3, label='Mean Prediction')

    # 실제 마지막 20일 데이터를 그래프에 추가
    #plt.plot(actual_dates, actual_20days_prices, color='blue', label='Actual Stock Price (last 20 days)', linewidth=2)

    # 그래프 설정
    #plt.title(f"Predicted vs Actual Stock Price ({ticker})")
    #plt.xlabel("Days")
    #plt.ylabel("Stock Price")
    #plt.xlim(0, total_length)
    #plt.legend()
    #plt.show()

    return mae, rmse, differences

    # # 오른쪽 그래프: 재조정된 패턴과 예측값 비교
    # plt.figure(figsize=(15, 7))
    # plt.plot(range(current_length), current_window, color='k', linewidth=3, label="Current window")

    # for label, indexed_price in indexed_subsequent_prices.items():
    #     plt.plot(range(current_length, total_length), indexed_price, label=label)

    # plt.plot(range(current_length, total_length), subsequent_mean_cum, color='green', linestyle='dashed', label='Median Subsequent')

    # plt.title(f"Most similar patterns in stock price history (aligned, reindexed)")
    # plt.xlabel("Days")
    # plt.ylabel("Reindexed Price")
    # plt.xlim(0, total_length)
    # plt.legend()
    # plt.show()




def plot_results(current_window, indexed_subsequent_prices, subsequent_mean_cum, days_to, subsequent_days, subsequent_prices_all, actual_prices):
    # 날짜 범위 설정
    current_length = len(current_window)
    future_length = subsequent_days
    total_length = current_length + future_length

    # 왼쪽 그래프: 예측 결과와 실제 주가 비교
    plt.figure(figsize=(15, 7))
    # 현재 윈도우 끝 날짜를 기준으로 x축을 설정
    plt.plot(range(current_length), actual_prices[-current_length:], color='blue', label='Actual Stock Price')

    # 각 예측된 주가지수 그리기 (0, 5, 10번째 인덱스만)
    indices_to_plot = [0, 3, 6]  # 인덱스를 0, 5, 10으로 설정
    for idx in indices_to_plot:
        if idx < len(subsequent_prices_all):
            prices = subsequent_prices_all[idx]
            actual_indexed_price = (prices + 1).cumprod() * actual_prices.iloc[-1]
            plt.plot(range(current_length, total_length), actual_indexed_price, linestyle='dotted', label=f'Actual Prediction {idx}')

    plt.title("Predicted vs Actual Stock Price")
    plt.xlabel("Days")
    plt.ylabel("Stock Price")
    plt.xlim(0, total_length)  # Set x-axis limits to match the right graph
    plt.legend()
    plt.show()

    # 오른쪽 그래프: 재조정된 패턴과 예측값 비교
    plt.figure(figsize=(15, 7))
    plt.plot(range(current_length), current_window, color='k', linewidth=3, label="Current window")

    for label, indexed_price in indexed_subsequent_prices.items():
        plt.plot(range(current_length, total_length), indexed_price, label=label)

    plt.plot(range(current_length, total_length), subsequent_mean_cum, color='green', linestyle='dashed', label='Median Subsequent')

    plt.title("Most similar patterns in stock price history (aligned, reindexed)")
    plt.xlabel("Days")
    plt.ylabel("Reindexed Price")
    plt.xlim(0, total_length)  # Set x-axis limits to match the left graph
    plt.legend()
    plt.show()





