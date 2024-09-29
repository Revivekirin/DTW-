import numpy as np
import matplotlib.pyplot as plt
from fastdtw import fastdtw
from scipy.spatial.distance import euclidean

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

def find_most_similar_pattern(
    n_days,
    price_data_pct_change,
    trend_features,
    vol_features,
    data_eco,
    current_window,
    current_trend,
    current_vol,
    current_eco,
    top_n=3
):
    # 가장 유사한 패턴을 저장하기 위한 초기화
    min_distances = [(float('inf'), None)] * top_n

    # 패턴 검색 범위 설정 (데이터 길이 제한 고려)
    for start_index in range(len(price_data_pct_change) - n_days + 1):
        past_window = price_data_pct_change.iloc[start_index:start_index + n_days].values
        past_trend = trend_features.iloc[start_index:start_index + n_days].values
        past_vol = vol_features.iloc[start_index:start_index + n_days].values
        past_eco = data_eco.iloc[start_index:start_index + n_days].values

        # DTW 거리 계산 (현재 창과 과거 창 비교)
        distance = dtw_distance(
            current_window, past_window,
            current_trend, past_trend,
            current_vol, past_vol,
            current_eco, past_eco
        )
        # 가장 가까운 패턴 업데이트
        for i, (min_distance, _) in enumerate(min_distances):
            if distance < min_distance:
                min_distances[i] = (distance, start_index)
                min_distances = sorted(min_distances, key=lambda x: x[0])
                break

    return min_distances



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





