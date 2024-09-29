import numpy as np
import matplotlib.pyplot as plt
from fastdtw import fastdtw
from scipy.spatial.distance import euclidean

def normalize(ts):
    return (ts - ts.min()) / (ts.max() - ts.min())

def dtw_distance(ts1, ts2):
    # 결측치와 inf 값을 0으로 대체
    ts1_normalized = np.nan_to_num(normalize(ts1))
    ts2_normalized = np.nan_to_num(normalize(ts2))

    distance, _ = fastdtw(ts1_normalized.reshape(-1, 1), ts2_normalized.reshape(-1, 1),
                          dist=euclidean)
    return distance

def find_most_similar_pattern(n_days, price_data_pct_change, current_window):
    """
    가장 유사한 패턴을 찾는 함수
    :param n_days: 입력 데이터의 기간 (일 수)
    :param price_data_pct_change: 과거 패턴 데이터의 주가 변동률
    :param data_eco_pattern: 과거 패턴 데이터의 경제 지표
    :param current_window: 입력 데이터의 주가 변동률
    :param current_eco: 입력 데이터의 경제 지표
    :return: 유사한 패턴의 리스트 (거리, 시작 인덱스)
    """
    current_window = price_data_pct_change[-n_days:].values
    min_distances = [(float('inf'), -1) for _ in range(5)]  # 가장 작은 거리와 인덱스를 저장하는 리스트

    # 각 과거 패턴 구간에 대해 유사도를 계산
    for start_index in range(len(price_data_pct_change) - 2* n_days):
        past_window = price_data_pct_change[start_index:start_index + n_days].values

        # DTW를 사용하여 주가 변동률과 경제 지표의 유사도 계산
        distance = dtw_distance(current_window, past_window)

        # 가장 유사한 패턴 5개 저장 (거리와 시작 인덱스)
        for i, (min_distance, _) in enumerate(min_distances):
            if distance < min_distance:
                min_distances[i] = (distance, start_index)
                min_distances.sort(key=lambda x: x[0])  # 거리 기준으로 정렬
                break

    return min_distances


# def find_most_similar_pattern(n_days, price_data_pct_change,subsequent_days):
#     current_window = price_data_pct_change[-n_days:].values
#     min_distances = [(float('inf'), -1) for _ in range(5)]
#     for start_index in range(len(price_data_pct_change) - 2 * n_days - subsequent_days):
#         past_window = price_data_pct_change[start_index:start_index + n_days].values
#         distance = dtw_distance(current_window, past_window)
#         for i, (min_distance, _) in enumerate(min_distances):
#             if distance < min_distance:
#                 min_distances[i] = (distance, start_index)
#                 min_distances.sort(key=lambda x: x[0])  # keep the list sorted by distance
#                 break
#     return min_distances



def plot_stock_patterns(ticker, data_input, data_pattern, min_distances, n_days, data_with_ta):
    import matplotlib.pyplot as plt
    fig, ax = plt.subplots(figsize=(12, 6))

    # 입력 데이터 패턴
    ax.plot(data_input.index, data_input['Close'], color='blue', label='Input Data Pattern')

    # 실제 데이터
    ax.plot(data_with_ta.index, data_with_ta['Close'], color='black', label='Actual Data', alpha=0.3)

    # 유사한 패턴들
    color_cycle = ['red', 'green', 'orange', 'purple', 'cyan']
    for i, (_, start_index) in enumerate(min_distances):
        color = color_cycle[i % len(color_cycle)]
        pattern_indices = data_pattern.index[start_index:start_index + n_days]
        pattern_values = data_pattern['Close'].iloc[start_index:start_index + n_days]
        ax.plot(pattern_indices, pattern_values, color=color, linestyle='--', label=f'Similar Pattern {i+1}')

    ax.set_title(f"{ticker} comparison with similar pattern")
    ax.set_xlabel('Date')
    ax.set_ylabel('Stock Price')
    ax.legend()
    plt.show()





