import yfinance as yf

def fetch_stock_data(ticker, start_date, end_date):
    stock_data = yf.download(ticker, start=start_date, end=end_date)
    return stock_data

def volatility(stock_data, window_size=6, threshold_multiplier=2):
    """
    주식 데이터에서 변동성이 큰 구간의 날짜를 반환합니다.

    Parameters:
    - stock_data (pd.DataFrame): 'Date'와 'Close' 열이 포함된 주가 데이터.
    - window_size (int): 이동 표준 편차를 계산할 기간 (기본값: 6일).
    - threshold_multiplier (float): 평균 이동 표준 편차에 대한 임계값을 설정하는 배수 (기본값: 2배).

    Returns:
    - high_volatility_periods (list of pd.DatetimeIndex): 변동성이 큰 구간의 날짜 범위 리스트.
    """
    
    # 이동 표준 편차 계산
    stock_data['volatility'] = stock_data['Close'].rolling(window=window_size).std()
    stock_data = stock_data.dropna()
    
    # 평균과 임계값 설정
    mean_volatility = stock_data['volatility'].mean()
    threshold = mean_volatility * threshold_multiplier

    # 변동성이 임계값 이상인 날짜 찾기
    high_volatility_periods = []
    current_dates = []

    for date, row in stock_data.iterrows():
        if row['volatility'] >= threshold:
            current_dates.append(date)  # 변동성이 큰 날을 추가
        else:
            if current_dates:
                # 고변동성 구간이 종료되면 날짜 범위를 생성하고 추가
                start_date = current_dates[0]
                end_date = current_dates[-1]
                high_volatility_periods.append((start_date, end_date))
                current_dates = []  # current_dates 초기화

    # 마지막 고변동성 구간이 끝나지 않았을 경우 추가
    if current_dates:
        start_date = current_dates[0]
        end_date = current_dates[-1]
        high_volatility_periods.append((start_date, end_date))

    return high_volatility_periods

