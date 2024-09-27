import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
from data_processing import load_data
from pattern_search import find_most_similar_pattern, plot_stock_patterns_and_extract_periods, plot_results_with_mean_and_actual_data
from plot_similarity_differences import plot_most_similar_pattern

def analyze_similarity(ticker, start_dates, end_dates, days_to, subsequent_days):
    similarities = []
    most_similar_period=None
    most_similar_rmse=float('inf')
    today = pd.Timestamp('today')

    for start_date, end_date in zip(start_dates, end_dates):
        start_date = pd.Timestamp(start_date)
        end_date = start_date + pd.DateOffset(months=6)

        if end_date > today:
            print(f"End date {end_date} exceeds today's date {today}, stopping analysis.")
            break

        data_with_ta, price_data_pct_change, data_eco, trend_features, vol_features = load_data(ticker, start_date, end_date)

        subsequent_prices_all = []

        for n_days in days_to:
            min_distances = find_most_similar_pattern(n_days, price_data_pct_change, trend_features, vol_features, data_eco, subsequent_days)
            similar_periods = plot_stock_patterns_and_extract_periods(ticker, data_with_ta['Close'], price_data_pct_change, min_distances, n_days, subsequent_days, subsequent_prices_all)
            

        # Prepare data for final plot
        current_window = (price_data_pct_change[-days_to[-1]:] + 1).cumprod() * 100
        indexed_subsequent_prices = {}

        for idx, n_days in enumerate(days_to):
            if idx < len(subsequent_prices_all):
                indexed_subsequent_prices[f'window{n_days}_1st'] = (subsequent_prices_all[idx] + 1).cumprod() * current_window.iloc[-1]

        available_indices = [i for i in [0, 3, 6] if i < len(subsequent_prices_all)]
        if available_indices:
            subsequent_mean = np.mean([subsequent_prices_all[i] for i in available_indices], axis=0)
            subsequent_mean_cum = (subsequent_mean + 1).cumprod() * current_window.iloc[-1]
        else:
            print(f"Insufficient data for start_date {start_date} and end_date {end_date}")
            continue  # 다음 루프로 넘어가도록 처리

        mae, rmse, differences = plot_results_with_mean_and_actual_data(
            ticker=ticker,
            current_window=current_window,
            indexed_subsequent_prices=indexed_subsequent_prices,
            subsequent_mean_cum=subsequent_mean_cum,
            days_to=days_to,
            subsequent_days=subsequent_days,
            subsequent_prices_all=subsequent_prices_all,
            actual_prices=data_with_ta['Close'],
            start_date=start_date, 
            end_date=end_date
        )

        similarities.append({
            'start_date': start_date,
            'end_date': end_date,
            'mae': mae,
            'rmse': rmse,
            'differences': differences
        })

       # 가장 유사한 패턴 찾기
        if rmse < most_similar_rmse:
            most_similar_rmse = rmse
            most_similar_period = {
                'start_date': start_date,
                'end_date': end_date,
                'mae': mae,
                'rmse': rmse,
                'differences': differences
            }

        # 가장 유사한 패턴 출력
        if most_similar_period:
            print(f"Most similar pattern found between {most_similar_period['start_date']} and {most_similar_period['end_date']}")
            print(f"MAE: {most_similar_period['mae']}, RMSE: {most_similar_period['rmse']}")
            plot_most_similar_pattern(ticker, most_similar_period, data_with_ta['Close'], price_data_pct_change, subsequent_prices_all)
        else:
            print("No similar patterns found.")


    return similar_periods, similarities