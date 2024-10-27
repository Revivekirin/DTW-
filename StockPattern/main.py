from params import params
from params import load_and_process_data
from evaluation import compare_patterns

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
    "MSFT",     # Microsoft Corporation (대형주)
    "NVDA",     # Nvidea (대형 기술주)
    "KO",       # 코카콜라 (대형 배당주)
    "JNJ",      # 존슨앤존스 (대형 배당주)
    "LLY",      # 일라일리리 (대형 바이오주)
    "GS",       # 골드만삭스 (대형 금융주)
    "ALTR",     # 알테어 엔지니어링 (중형 기술주)
    "IONQ",     # 아이온큐 (소형 기술주)
]

# 시작일과 종료일 설정
pattern_search_start_date = "2023-09-22"
pattern_search_end_date = "2024-09-22"


# 주식 목록을 처리하는 함수
def process_stocks(stock_list, start_date, end_date):
    for stock in stock_list:
        # params 함수 호출 및 결과 저장
        similar_patterns = params(stock, start_date, end_date)
        print(f"{stock}의 유사한 패턴 결과: {similar_patterns}")

# def get_actual_pattern(ticker, data_pattern, end_date, n_days):
#     """실제 패턴을 로드하는 함수 (예: 마지막 n일의 데이터)"""
#     # 실제 데이터를 로드하고, 마지막 n_days의 패턴을 반환합니다.
#     data, price_data_pct_change, *_ = load_and_process_data(ticker, end_date, end_date)  # 실제 데이터 로드
#     recent_data = data_pattern.tail(n_days)  # data_pattern에서 최근 n_days 추출
#     return price_data_pct_change.tail(n_days).values  # 마지막 n_days 데이터 반환


# # 주식 목록을 처리하고 패턴을 비교하는 함수
# def process_stocks(stock_list, start_date, end_date):
    
#     for stock in stock_list:
#         data_pattern, price_data_pct_change_pattern, data_eco_pattern, trend_features_pattern, vol_features_pattern = \
#                 load_and_process_data(stock, pattern_search_start_date, pattern_search_end_date)
        
#         actual_pattern = get_actual_pattern(stock, data_pattern, end_date, 6)  # 마지막 6일의 실제 패턴 로드
#         # params 함수 호출 및 결과 저장 (유사 패턴 반환)
#         similar_patterns = params(stock, start_date, end_date)

#         # 유사 패턴이 있는 경우 평가
#         for pattern_info in similar_patterns:
#             predicted_pattern = pattern_info['predicted_pattern']  # 유사 패턴 데이터 추출
#             # 실제 패턴과 유사 패턴 간 비교
#             evaluation_results = compare_patterns(actual_pattern, predicted_pattern)
#             print(f"{stock}의 유사 패턴 평가 결과: {evaluation_results}")


# 한국 주식 처리
process_stocks(korean_stocks, pattern_search_start_date, pattern_search_end_date)

# 미국 주식 처리
process_stocks(us_stocks, pattern_search_start_date, pattern_search_end_date)