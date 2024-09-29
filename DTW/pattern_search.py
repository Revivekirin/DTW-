import numpy as np
import matplotlib.pyplot as plt
from fastdtw import fastdtw
from scipy.spatial.distance import euclidean

def normalize(ts):
    return (ts - ts.min()) / (ts.max() - ts.min())

def dtw_distance(ts1, ts2):
    ts1_normalized = normalize(ts1)
    ts2_normalized = normalize(ts2)
    distance, _ = fastdtw(ts1_normalized.reshape(-1, 1), ts2_normalized.reshape(-1, 1),
                          dist=euclidean)
    return distance

def find_most_similar_pattern(price_data_pct_change, n_days, subsequent_days):
    current_window = price_data_pct_change[-n_days:].values
    min_distances = [(float('inf'), -1) for _ in range(5)]
    for start_index in range(len(price_data_pct_change) - 2 * n_days - subsequent_days):
        past_window = price_data_pct_change[start_index:start_index + n_days].values
        distance = dtw_distance(current_window, past_window)
        for i, (min_distance, _) in enumerate(min_distances):
            if distance < min_distance:
                min_distances[i] = (distance, start_index)
                min_distances.sort(key=lambda x: x[0])  # keep the list sorted by distance
                break
    return min_distances

def plot_stock_patterns(ticker, price_data, price_data_pct_change, min_distances, n_days, subsequent_days, subsequent_prices_all):
    fig, axs = plt.subplots(1, 2, figsize=(30, 6))
    axs[0].plot(price_data, color='blue', label='Overall stock price')
    color_cycle = ['red', 'pink', 'purple', 'orange', 'cyan']
    subsequent_prices = []

    for i, (_, start_index) in enumerate(min_distances):
        color = color_cycle[i % len(color_cycle)]
        past_window_start_date = price_data.index[start_index]
        past_window_end_date = price_data.index[start_index + n_days + subsequent_days]
        axs[0].plot(price_data[past_window_start_date:past_window_end_date], color=color, label=f"Pattern {i+1}")

        # Store subsequent prices for median calculation
        subsequent_window = price_data_pct_change[start_index + n_days: start_index + n_days + subsequent_days].values
        subsequent_prices.append(subsequent_window)
        subsequent_prices_all.append(subsequent_window)

    axs[0].set_title(f'{ticker} Stock Price Data')
    axs[0].set_xlabel('Date')
    axs[0].set_ylabel('Stock Price')
    axs[0].legend()

    for i, (_, start_index) in enumerate(min_distances):
        color = color_cycle[i % len(color_cycle)]
        past_window = price_data_pct_change[start_index:start_index + n_days + subsequent_days]
        reindexed_current_window = (past_window + 1).cumprod() * 100
        axs[1].plot(range(n_days), reindexed_current_window[:n_days], color=color, linewidth=3, label="Current window")

        # Compute and plot the median subsequent prices
        subsequent_prices = np.array(subsequent_prices)
        median_subsequent_prices = np.median(subsequent_prices, axis=0)
        median_subsequent_prices_cum = (median_subsequent_prices + 1).cumprod() * reindexed_current_window.iloc[n_days - 1]

        axs[1].plot(range(n_days, n_days + subsequent_days), median_subsequent_prices_cum, color=color, linestyle='dashed', label='Median Subsequent Price Estimation')

    axs[1].set_title(f"Most similar {n_days}-day patterns in {ticker} stock price history (aligned, reindexed)")
    axs[1].set_xlabel("Days")
    axs[1].set_ylabel("Reindexed Price")
    axs[1].legend()
    plt.show()



import matplotlib.pyplot as plt

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
    indices_to_plot = [0, 5, 10]  # 인덱스를 0, 5, 10으로 설정
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





