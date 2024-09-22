from generate_date_ranges import generate_date_ranges
from analyze_similarity import analyze_similarity
from plot_similarity_differences import plot_similarity_differences

# Ticker symbol 설정 (삼성전자 예시)
#ticker = "005930.KS"
ticker = "MSFT"
#ticker = "466400.KS" #Hana 1Q 25-08 Corp Bond(A+) Active ETF 

days_to = [15, 20, 30]
subsequent_days = 20 #예상 범위
start_date = "2023-09-22"
end_date = "2024-09-22"
start_dates, end_dates = generate_date_ranges(start_date, end_date)

# 유사도 분석 결과를 받은 후
similarities = analyze_similarity(ticker, start_dates, end_dates, days_to, subsequent_days)

# 시각화 함수 호출
plot_similarity_differences(similarities, figsize=(14, 7), title='Stock Pattern Differences', xlabel='Date', ylabel='Difference', legend_title='Time Periods')