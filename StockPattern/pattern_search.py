import numpy as np
import pandas as pd
import matplotlib.pyplot as plt

from fastdtw import fastdtw
from scipy.spatial.distance import euclidean
from typing import List, Tuple

def normalize_and_fill(ts: np.ndarray) -> np.ndarray:
    """ Normalize time series and replace NaN or inf values with 0 """
    return np.nan_to_num((ts - ts.min()) / (ts.max() - ts.min()))

def dtw_distance(
    ts1: np.ndarray, 
    ts2: np.ndarray, 
    ts1_ta_trend: np.ndarray, 
    ts2_ta_trend: np.ndarray, 
    ts1_vol: np.ndarray, 
    ts2_vol: np.ndarray, 
    data_eco1: np.ndarray, 
    data_eco2: np.ndarray, 
    w1: float = 0.4, 
    w2: float = 0.2, 
    w3: float = 0.2
) -> float:
    """ Calculate the weighted DTW distance between two sets of time series. """
    # Normalize and handle NaN/inf values for all series
    ts1_normalized = normalize_and_fill(ts1)
    ts2_normalized = normalize_and_fill(ts2)
    ts1_ta_trend_nor = normalize_and_fill(ts1_ta_trend)
    ts2_ta_trend_nor = normalize_and_fill(ts2_ta_trend)
    ts1_vol_nor = normalize_and_fill(ts1_vol)
    ts2_vol_nor = normalize_and_fill(ts2_vol)
    eco1_nor = normalize_and_fill(data_eco1)
    eco2_nor = normalize_and_fill(data_eco2)

    # Calculate individual DTW distances
    distance_pct_change, _ = fastdtw(ts1_normalized.reshape(-1, 1), ts2_normalized.reshape(-1, 1), dist=euclidean)
    distance_trend, _ = fastdtw(ts1_ta_trend_nor, ts2_ta_trend_nor, dist=euclidean)
    distance_vol, _ = fastdtw(ts1_vol_nor, ts2_vol_nor, dist=euclidean)
    distance_eco, _ = fastdtw(eco1_nor, eco2_nor, dist=euclidean)
    
    # Weighted sum of distances
    return w1 * distance_pct_change + w2 * distance_trend + w3 * distance_vol + (1 - w1 - w2 - w3) * distance_eco

def find_most_similar_pattern(
    n_days: int,
    price_data_pct_change: pd.Series,
    trend_features: np.ndarray,
    vol_features: np.ndarray,
    data_eco: np.ndarray,
    current_window: np.ndarray,
    current_trend: np.ndarray,
    current_vol: np.ndarray,
    current_eco: np.ndarray,
    top_n: int = 3
) -> List[Tuple[float, int]]:
    """ Find the most similar patterns based on DTW distance. """
    min_distances = [(float('inf'), None)] * top_n

    for start_index in range(len(price_data_pct_change) - n_days + 1):
        past_window = price_data_pct_change.iloc[start_index:start_index + n_days].values
        past_trend = trend_features[start_index:start_index + n_days]
        past_vol = vol_features[start_index:start_index + n_days]
        past_eco = data_eco[start_index:start_index + n_days]

        distance = dtw_distance(
            current_window, past_window,
            current_trend, past_trend,
            current_vol, past_vol,
            current_eco, past_eco
        )

        # Update closest patterns
        for i, (min_distance, _) in enumerate(min_distances):
            if distance < min_distance:
                min_distances[i] = (distance, start_index)
                min_distances = sorted(min_distances, key=lambda x: x[0])
                break

    return min_distances

def plot_stock_patterns(
    ticker: str, 
    data_input: pd.DataFrame, 
    data_pattern: pd.DataFrame, 
    min_distances: List[Tuple[float, int]], 
    n_days: int, 
    data_with_ta: pd.DataFrame
) -> None:
    """ Plot the stock patterns and similar patterns found. """
    fig, ax = plt.subplots(figsize=(12, 6))

    # Input data pattern (target)
    ax.plot(data_input.index, data_input['Close'], color='blue', label='Input Data Pattern')

    # Actual stock data
    ax.plot(data_with_ta.index, data_with_ta['Close'], color='black', label='Actual Data', alpha=0.2)

    # Plot similar patterns
    color_cycle = plt.cm.get_cmap('tab10', len(min_distances))  # Use colormap for better variety
    for i, (_, start_index) in enumerate(min_distances):
        pattern_indices = data_pattern.index[start_index:start_index + n_days]
        pattern_values = data_pattern['Close'].iloc[start_index:start_index + n_days]
        ax.plot(pattern_indices, pattern_values, color=color_cycle(i), linestyle='--', label=f'Similar Pattern {i+1}')

    ax.set_title(f"{ticker} comparison with similar pattern")
    ax.set_xlabel('Date')
    ax.set_ylabel('Stock Price')
    ax.legend()
    plt.show()
