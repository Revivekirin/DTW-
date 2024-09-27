from params import params

# 한국 소형주 8개와 대형주 2개 (yfinance ticker)
korean_stocks = [
    "068270.KS",  # 셀트리온헬스케어
    "357780.KQ",  # 솔브레인
    "277810.KS",  # 레인보우로보틱스
    "096530.KQ",  # 씨젠
    "247540.KQ",  # 에코프로비엠
    "112040.KQ",  # 위메이드
    "293490.KQ",  # 카카오게임즈
    "009830.KS",  # 한화솔루션
    "005930.KS",  # 삼성전자 (대형주)
    "051910.KS"   # LG화학 (대형주)
]

# 미국 소형주 8개와 대형주 2개 (yfinance ticker)
us_stocks = [
    "ROKU",     # Roku, Inc.
    "SQ",       # Square, Inc.
    "PLUG",     # Plug Power Inc.
    "UPWK",     # Upwork Inc.
    "BYND",     # Beyond Meat, Inc.
    "RUN",      # Sunrun Inc.
    "Z",        # Zillow Group, Inc.
    "TDOC",     # Teladoc Health, Inc.
    "AAPL",     # Apple Inc. (대형주)
    "MSFT"      # Microsoft Corporation (대형주)
]

for idx in range(len(korean_stocks)):
    params(korean_stocks[idx])

for idx in range(len(us_stocks)):
    params(us_stocks[idx])


# # 사용자 입력
# input_start_date = "2023-10-01"
# input_end_date = "2023-10-10"
# pattern_search_start_date = "2023-09-22"
# pattern_search_end_date = "2024-09-22"

# # 데이터 로드
# data_input, price_data_pct_change_input, data_eco_input, trend_features_input, vol_features_input = load_data(ticker, input_start_date, input_end_date)
# data_pattern, price_data_pct_change_pattern, data_eco_pattern, trend_features_pattern, vol_features_pattern = load_data(ticker, pattern_search_start_date, pattern_search_end_date)


# # 'numpy.ndarray'인 경우 'DataFrame'으로 변환
# def convert_to_dataframe(data):
#     if isinstance(data, np.ndarray):
#         return pd.DataFrame(data)
#     return data

# data_input = convert_to_dataframe(data_input)
# price_data_pct_change_input = convert_to_dataframe(price_data_pct_change_input)
# data_eco_input = convert_to_dataframe(data_eco_input)
# trend_features_input = convert_to_dataframe(trend_features_input)
# vol_features_input = convert_to_dataframe(vol_features_input)

# data_pattern = convert_to_dataframe(data_pattern)
# price_data_pct_change_pattern = convert_to_dataframe(price_data_pct_change_pattern)
# data_eco_pattern = convert_to_dataframe(data_eco_pattern)
# trend_features_pattern = convert_to_dataframe(trend_features_pattern)
# vol_features_pattern = convert_to_dataframe(vol_features_pattern)

# # 결측치 처리
# data_input.ffill(inplace=True)  # 또는 bfill
# price_data_pct_change_input.ffill(inplace=True)  # 또는 bfill
# data_eco_input.ffill(inplace=True)  # 또는 bfill
# trend_features_input.ffill(inplace=True)  # 또는 bfill
# vol_features_input.ffill(inplace=True)  # 또는 bfill

# data_pattern.ffill(inplace=True)
# price_data_pct_change_pattern.ffill(inplace=True)
# data_eco_pattern.ffill(inplace=True)
# trend_features_pattern.ffill(inplace=True)
# vol_features_pattern.ffill(inplace=True)

# # 입력 데이터 기간의 길이
# n_days = len(data_input)

# # 입력 데이터에서 패턴 추출
# current_window = price_data_pct_change_input
# current_trend = trend_features_input
# current_vol = vol_features_input
# current_eco = data_eco_input

# # 검색 기간에서 입력 데이터 기간을 제외하기 위한 마스크 생성
# mask = (data_pattern.index < input_start_date) | (data_pattern.index > input_end_date)

# # mask의 길이를 맞추기 위해 데이터프레임의 길이에 맞는지 확인하고, 부족한 경우 False 값으로 채우기
# if len(mask) < len(data_eco_pattern):
#     mask = np.append(mask, [False] * (len(data_eco_pattern) - len(mask)))

# # 각 데이터프레임에 대해 동일한 길이로 마스크 적용
# data_pattern_filtered = data_pattern[mask[:len(data_pattern)]]
# price_data_pct_change_pattern_filtered = price_data_pct_change_pattern[mask[:len(price_data_pct_change_pattern)]]
# trend_features_pattern_filtered = trend_features_pattern[mask[:len(trend_features_pattern)]]
# vol_features_pattern_filtered = vol_features_pattern[mask[:len(vol_features_pattern)]]
# data_eco_pattern_filtered = data_eco_pattern[mask[:len(data_eco_pattern)]]

# # 패턴 검색 및 시각화
# min_distances = find_most_similar_pattern(
#     n_days,
#     price_data_pct_change_pattern_filtered,
#     trend_features_pattern_filtered,
#     vol_features_pattern_filtered,
#     data_eco_pattern_filtered,
#     current_window,
#     current_trend,
#     current_vol,
#     current_eco
# )

# print(f"입력된 기간과 유사한 패턴을 찾았습니다: {min_distances}")
# plot_stock_patterns(ticker, data_input, data_pattern_filtered, min_distances, n_days, data_pattern)




# from generate_date_ranges import generate_date_ranges
# from data_processing import load_data
# from pattern_search import find_most_similar_pattern, plot_stock_patterns, plot_results
# from evaluation import calculate_accuracy_metrics
# import numpy as np

# # Ticker symbol 설정 (삼성전자 예시)
# #ticker = "005930.KS"
# #ticker = "068270.KS"
# ticker="MSFT"
# #ticker = "466400.KS" #Hana 1Q 25-08 Corp Bond(A+) Active ETF 

# days_to = [15, 20, 30]
# subsequent_days = 30 #예상 범위
# start_date = "2023-09-22"
# end_date = "2024-09-22"
# start_dates, end_dates = generate_date_ranges(start_date, end_date)


# # Load data
# data_with_ta, price_data_pct_change, data_eco, trend_features, vol_features = load_data(ticker, start_date, end_date)

# # Define parameters
# days_to = [15, 20, 30]
# subsequent_days = 20

# # Pattern search and plotting
# subsequent_prices_all = []
# for n_days in days_to:
#     min_distances = find_most_similar_pattern(n_days, price_data_pct_change, trend_features, vol_features, data_eco, subsequent_days)
#     print(f"Most similar patterns for {n_days} days window:", min_distances)
#     plot_stock_patterns(ticker, data_with_ta['Close'], price_data_pct_change, min_distances, n_days, subsequent_days, subsequent_prices_all)

# # Prepare data for final plot
# current_window = (price_data_pct_change[-days_to[-1]:] + 1).cumprod() * 100
# indexed_subsequent_prices = {
#     'window15_1st': (subsequent_prices_all[0] + 1).cumprod() * current_window.iloc[-1],
#     'window20_1st': (subsequent_prices_all[3] + 1).cumprod() * current_window.iloc[-1],
#     'window30_1st': (subsequent_prices_all[6] + 1).cumprod() * current_window.iloc[-1]
# }
# subsequent_mean = np.mean([subsequent_prices_all[0], subsequent_prices_all[3], subsequent_prices_all[6]], axis=0)
# subsequent_mean_cum = (subsequent_mean + 1).cumprod() * current_window.iloc[-1]

# plot_results(current_window, indexed_subsequent_prices, subsequent_mean_cum, days_to, subsequent_days, subsequent_prices_all, data_with_ta['Close'])

# # Example evaluation (Assuming you have actual and predicted prices)
# # Replace the following with actual data extraction and prediction results
# actual_prices = (data_with_ta['Close'][-(subsequent_days + days_to[-1]):] + 1).cumprod() * 100
# predicted_prices = [ (subsequent_prices_all[i] + 1).cumprod() * current_window.iloc[-1] for i in range(len(subsequent_prices_all)) ]

# # Flatten lists and concatenate if needed for comparison
# actual_prices_flat = np.concatenate([actual_prices.values])
# predicted_prices_flat = np.concatenate([prices for prices in predicted_prices])

# calculate_accuracy_metrics(actual_prices_flat, predicted_prices_flat)

