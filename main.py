from data_processing import load_data
from pattern_search import find_most_similar_pattern, plot_stock_patterns, plot_results_with_mean_and_actual_data
import numpy as np
from generate_date_ranges import generate_date_ranges
import matplotlib.pyplot as plt


# Ticker symbol 설정 (삼성전자 예시)
#ticker = "005930.KS"
ticker = "MSFT"
#ticker = "466400.KS" #Hana 1Q 25-08 Corp Bond(A+) Active ETF 

days_to = [15, 20, 30]
subsequent_days = 20 #예상 범위
start_date = "2000-09-14"
end_date = "2024-09-14"
start_dates, end_dates = generate_date_ranges(start_date, end_date)
print(f"start_dates: {start_dates}")
print(f"end_dates: {end_dates}")

similarities = []  # 유사도 저장 리스트

for start_date, end_date in zip(start_dates, end_dates):
    data_with_ta, price_data_pct_change, data_eco, trend_features, vol_features = load_data(ticker, start_date, end_date)

    subsequent_prices_all=[]

    for n_days in days_to:
        min_distances = find_most_similar_pattern(n_days, price_data_pct_change, trend_features, vol_features, data_eco, subsequent_days)
        plot_stock_patterns(ticker, data_with_ta['Close'], price_data_pct_change, min_distances, n_days, subsequent_days, subsequent_prices_all)

    # Prepare data for final plot
    current_window = (price_data_pct_change[-days_to[-1]:] + 1).cumprod() * 100
    indexed_subsequent_prices = {}
    for idx, n_days in enumerate(days_to):
        if idx < len(subsequent_prices_all):
            indexed_subsequent_prices[f'window{n_days}_1st'] = (subsequent_prices_all[idx] + 1).cumprod() * current_window.iloc[-1]
    subsequent_mean = np.mean([subsequent_prices_all[0], subsequent_prices_all[3], subsequent_prices_all[6]], axis=0)
    subsequent_mean_cum = (subsequent_mean + 1).cumprod() * current_window.iloc[-1]


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

    # Plotting the differences for each date range
    import pandas as pd

    all_differences = pd.concat([pd.Series(sim['differences'], name=f"Start: {sim['start_date']}, End: {sim['end_date']}") for sim in similarities], axis=1)

    all_differences.plot(figsize=(14, 7))
    plt.title('Differences for Each Date Range')
    plt.xlabel('Date')
    plt.ylabel('Difference')
    plt.legend(title='Date Ranges')
    plt.show()
    