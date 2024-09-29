from data_processing import load_data
from pattern_search import find_most_similar_pattern, plot_stock_patterns, plot_results
from evaluation import calculate_accuracy_metrics
import numpy as np


# Ticker symbol 설정 (삼성전자 예시)
#ticker = "005930.KS"
ticker = "MSFT"


# Load data
data_with_ta, price_data_pct_change, data_eco = load_data(ticker, start_date="2000-01-01", end_date="2023-12-27")

# Define parameters
days_to = [15, 20, 30]
subsequent_days = 20

# Pattern search and plotting
subsequent_prices_all = []
for n_days in days_to:
    min_distances = find_most_similar_pattern(price_data_pct_change, n_days, subsequent_days)
    print(f"Most similar patterns for {n_days} days window:", min_distances)
    plot_stock_patterns(ticker, data_with_ta['Close'], price_data_pct_change, min_distances, n_days, subsequent_days, subsequent_prices_all)

# Prepare data for final plot
current_window = (price_data_pct_change[-days_to[-1]:] + 1).cumprod() * 100
indexed_subsequent_prices = {
    'window15_1st': (subsequent_prices_all[0] + 1).cumprod() * current_window.iloc[-1],
    'window20_1st': (subsequent_prices_all[5] + 1).cumprod() * current_window.iloc[-1],
    'window30_1st': (subsequent_prices_all[10] + 1).cumprod() * current_window.iloc[-1]
}
subsequent_mean = np.mean([subsequent_prices_all[0], subsequent_prices_all[5], subsequent_prices_all[10]], axis=0)
subsequent_mean_cum = (subsequent_mean + 1).cumprod() * current_window.iloc[-1]

plot_results(current_window, indexed_subsequent_prices, subsequent_mean_cum, days_to, subsequent_days, subsequent_prices_all, data_with_ta['Close'])

# Example evaluation (Assuming you have actual and predicted prices)
# Replace the following with actual data extraction and prediction results
actual_prices = (data_with_ta['Close'][-(subsequent_days + days_to[-1]):] + 1).cumprod() * 100
predicted_prices = [ (subsequent_prices_all[i] + 1).cumprod() * current_window.iloc[-1] for i in range(len(subsequent_prices_all)) ]

# Flatten lists and concatenate if needed for comparison
actual_prices_flat = np.concatenate([actual_prices.values])
predicted_prices_flat = np.concatenate([prices for prices in predicted_prices])

calculate_accuracy_metrics(actual_prices_flat, predicted_prices_flat)

