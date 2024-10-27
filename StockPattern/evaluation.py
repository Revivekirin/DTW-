from sklearn.metrics import mean_absolute_error
from sklearn.metrics import mean_squared_error
from sklearn.metrics.pairwise import cosine_similarity
import numpy as np

# def calculate_similarity(ts1, ts2):
#     distance, _ = fastdtw(ts1, ts2, dist=euclidean)
#     similarity = 1 / (1 + distance)  # 거리 기반 유사도 계산
#     return similarity

def calculate_mae(actual, predicted):
    return mean_absolute_error(actual, predicted)


def calculate_rmse(actual, predicted):
    return np.sqrt(mean_squared_error(actual, predicted))


def calculate_cosine_similarity(ts1, ts2):
    ts1 = ts1.reshape(1, -1)  # 2D 배열로 변환
    ts2 = ts2.reshape(1, -1)  # 2D 배열로 변환
    return cosine_similarity(ts1, ts2)[0][0]


def compare_patterns(actual, predicted):
    # dtw_sim = calculate_similarity(actual, predicted)
    mae = calculate_mae(actual, predicted)
    rmse = calculate_rmse(actual, predicted)
    cos_sim = calculate_cosine_similarity(np.array(actual), np.array(predicted))

    print(f"DTW Similarity: {dtw_sim:.4f}")
    print(f"MAE: {mae:.4f}")
    print(f"RMSE: {rmse:.4f}")
    print(f"Cosine Similarity: {cos_sim:.4f}")

    return {
        'dtw_similarity': dtw_sim,
        'mae': mae,
        'rmse': rmse,
        'cosine_similarity': cos_sim
    }
