import yfinance as yf
import pandas as pd
import numpy as np
import ta
from sklearn.decomposition import PCA
from sklearn.impute import KNNImputer

def add_to_features(data):
    data.fillna(method='ffill', inplace=True)

    # Add Trend indicators
    data['trend_ichimoku_a'] = ta.trend.ichimoku_a(data['High'], data['Low'])
    data['trend_ichimoku_b'] = ta.trend.ichimoku_b(data['High'], data['Low'])
    data['trend_ichimoku_base'] = ta.trend.ichimoku_base_line(data['High'], data['Low'])
    data['trend_ema_fast'] = ta.trend.ema_indicator(data['Close'], 20)
    data['trend_ema_slow'] = ta.trend.ema_indicator(data['Close'], 100)
    data['trend_sma_fast'] = ta.trend.sma_indicator(data['Close'], 20)
    data['trend_sma_slow'] = ta.trend.sma_indicator(data['Close'], 200)
    data['trend_psar_up'] = ta.trend.psar_up(data['High'], data['Low'], data['Close'])
    data['momentum_kama'] = ta.momentum.kama(data['Close'])
    data['volume_vwap'] = ta.volume.VolumeWeightedAveragePrice(data['High'], data['Low'], data['Close'], data['Volume']).volume_weighted_average_price()
    data['volatility_dcm'] = ta.volatility.DonchianChannel(data['High'], data['Low'], data['Close']).donchian_channel_mband()
    data['volatility_dch'] = ta.volatility.DonchianChannel(data['High'], data['Low'], data['Close']).donchian_channel_hband()
    data['volatility_dcw'] = ta.volatility.DonchianChannel(data['High'], data['Low'], data['Close']).donchian_channel_wband()
    data['volatility_bbl'] = ta.volatility.BollingerBands(data['Close']).bollinger_lband()
    data['volatility_bbm'] = ta.volatility.BollingerBands(data['Close']).bollinger_mavg()
    data['volatility_bbw'] = ta.volatility.BollingerBands(data['Close']).bollinger_wband()
    data['volatility_kcc'] = ta.volatility.KeltnerChannel(data['High'], data['Low'], data['Close']).keltner_channel_mband()
    data['volatility_kcl'] = ta.volatility.KeltnerChannel(data['High'], data['Low'], data['Close']).keltner_channel_lband()
    data['volatility_kch'] = ta.volatility.KeltnerChannel(data['High'], data['Low'], data['Close']).keltner_channel_hband()
    data['volatility_kcw'] = ta.volatility.KeltnerChannel(data['High'], data['Low'], data['Close']).keltner_channel_wband()
    data['others_cr'] = ta.others.cumulative_return(data['Close'])
    return data

def extract_and_reduce_features(data, n_components=3):
    ta_features = data.drop(columns=['Open', 'High', 'Low', 'Close', 'Volume', 'Adj Close'])
    column_trend = ['trend_ichimoku_a', 'trend_ichimoku_b', 'trend_ichimoku_base', 'trend_ema_fast', 'trend_ema_slow', 'trend_sma_fast', 'trend_sma_slow', 'trend_psar_up', 'others_cr']
    ta_features_trend = ta_features.loc[:, column_trend]
    ta_features_vol = ta_features.drop(columns=column_trend)

    # Impute missing values
    imputer1, imputer2 = KNNImputer(n_neighbors=2, weights="uniform"), KNNImputer(n_neighbors=2, weights="uniform")
    imputed_trend_features = imputer1.fit_transform(ta_features_trend)
    imputed_vol_features = imputer2.fit_transform(ta_features_vol)

    # pca1, pca2 = PCA(n_components=n_components), PCA(n_components=n_components - 1)
    # trend_features = pca1.fit_transform(imputed_trend_features)
    # 데이터의 샘플 수와 피처 수에 맞게 n_components를 조정
    n_components = min(2, imputed_trend_features.shape[0], imputed_trend_features.shape[1])
    pca1 = PCA(n_components=n_components)
    trend_features = pca1.fit_transform(imputed_trend_features)

    vol_features = pca1.fit_transform(imputed_vol_features)

    return trend_features, vol_features


def load_data(ticker, start_date, end_date):
    data = yf.download(ticker, start=start_date, end=end_date)
    data_with_ta = add_to_features(data)
    trend_features, vol_features = extract_and_reduce_features(data_with_ta, n_components=2)
    price_data_pct_change = data_with_ta['Close'].pct_change().dropna()
    data_ex = yf.download(["USDKRW=x", "^KS11", "^GSPC"], start=start_date, end=end_date)
    data_interest = yf.download("^FVX", start=start_date, end=end_date)

    # Remove timezone information to make both indices tz-naive
    data_ex.index = data_ex.index.tz_localize(None)
    data_interest.index = data_interest.index.tz_localize(None)

    data_eco = pd.concat([data_ex["Close"], data_interest['Close']], axis=1)
    imputer = KNNImputer(n_neighbors=2, weights="uniform")
    data_eco = imputer.fit_transform(data_eco)
    return data_with_ta, price_data_pct_change, data_eco
