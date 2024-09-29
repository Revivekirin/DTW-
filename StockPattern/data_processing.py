import yfinance as yf
import pandas as pd
import numpy as np
import ta

from sklearn.decomposition import PCA
from sklearn.impute import KNNImputer

def fill_missing_values(data, method='bfill'):
    """결측치를 채우는 함수"""
    data.fillna(method=method, inplace=True)
    return data

def add_trend_indicators(data):
    """트렌드 인디케이터를 추가하는 함수"""
    data['trend_ichimoku_a'] = ta.trend.ichimoku_a(data['High'], data['Low'])
    data['trend_ichimoku_b'] = ta.trend.ichimoku_b(data['High'], data['Low'])
    data['trend_ichimoku_base'] = ta.trend.ichimoku_base_line(data['High'], data['Low'])
    data['trend_ema_fast'] = ta.trend.ema_indicator(data['Close'], 20)
    data['trend_ema_slow'] = ta.trend.ema_indicator(data['Close'], 100)
    data['trend_sma_fast'] = ta.trend.sma_indicator(data['Close'], 20)
    data['trend_sma_slow'] = ta.trend.sma_indicator(data['Close'], 200)
    data['trend_psar_up'] = ta.trend.psar_up(data['High'], data['Low'], data['Close'])
    data['momentum_kama'] = ta.momentum.kama(data['Close'])
    return data

def add_volatility_indicators(data):
    """볼래틸리티 인디케이터를 추가하는 함수"""
    donchian = ta.volatility.DonchianChannel(data['High'], data['Low'], data['Close'])
    bollinger = ta.volatility.BollingerBands(data['Close'])
    keltner = ta.volatility.KeltnerChannel(data['High'], data['Low'], data['Close'])

    data['volatility_dcm'] = donchian.donchian_channel_mband()
    data['volatility_dch'] = donchian.donchian_channel_hband()
    data['volatility_dcw'] = donchian.donchian_channel_wband()
    data['volatility_bbl'] = bollinger.bollinger_lband()
    data['volatility_bbm'] = bollinger.bollinger_mavg()
    data['volatility_bbw'] = bollinger.bollinger_wband()
    data['volatility_kcc'] = keltner.keltner_channel_mband()
    data['volatility_kcl'] = keltner.keltner_channel_lband()
    data['volatility_kch'] = keltner.keltner_channel_hband()
    data['volatility_kcw'] = keltner.keltner_channel_wband()
    return data

def add_features(data):
    """모든 지표 추가"""
    data = add_trend_indicators(data)
    data = add_volatility_indicators(data)
    data['others_cr'] = ta.others.cumulative_return(data['Close'])
    return fill_missing_values(data)

def apply_pca(imputed_features, n_components):
    """PCA 적용"""
    pca = PCA(n_components=n_components)
    return pca.fit_transform(imputed_features)

def impute_data(data):
    """KNN을 사용한 결측치 대체"""
    imputer = KNNImputer(n_neighbors=2, weights="uniform")
    return imputer.fit_transform(data)

def extract_and_reduce_features(data, n_components=3):
    """특징 추출 및 차원 축소"""
    ta_features = data.drop(columns=['Open', 'High', 'Low', 'Close', 'Volume', 'Adj Close'])
    
    # 트렌드 및 볼래틸리티 분리
    column_trend = ['trend_ichimoku_a', 'trend_ichimoku_b', 'trend_ichimoku_base', 
                    'trend_ema_fast', 'trend_ema_slow', 'trend_sma_fast', 'trend_sma_slow', 
                    'trend_psar_up', 'others_cr']
    ta_features_trend = ta_features.loc[:, column_trend]
    ta_features_vol = ta_features.drop(columns=column_trend)

    # 결측치 대체 및 PCA
    imputed_trend_features = impute_data(ta_features_trend)
    imputed_vol_features = impute_data(ta_features_vol)
    
    trend_features = apply_pca(imputed_trend_features, n_components)
    vol_features = apply_pca(imputed_vol_features, n_components - 1)
    
    return trend_features, vol_features

def load_data(ticker, start_date, end_date):
    """데이터 로드 및 전처리"""
    data = yf.download(ticker, start=start_date, end=end_date)
    data_with_ta = add_features(data)
    
    # PCA 및 변화율 계산
    trend_features, vol_features = extract_and_reduce_features(data_with_ta, n_components=2)
    price_data_pct_change = data_with_ta['Close'].pct_change().dropna()

    # 경제 지표 로드
    data_ex = yf.download(["USDKRW=x", "^KS11", "^GSPC"], start=start_date, end=end_date)
    data_interest = yf.download("^FVX", start=start_date, end=end_date)
    
    # 타임존 및 결측치 처리
    data_ex.index, data_interest.index = data_ex.index.tz_localize(None), data_interest.index.tz_localize(None)
    data_eco = pd.concat([data_ex["Close"], data_interest['Close']], axis=1)
    data_eco = impute_data(data_eco)
    
    return data_with_ta, price_data_pct_change, data_eco, trend_features, vol_features
