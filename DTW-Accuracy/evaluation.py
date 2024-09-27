from sklearn.preprocessing import StandardScaler
from sklearn.metrics import mean_absolute_error, mean_squared_error, r2_score
import numpy as np
import matplotlib.pyplot as plt


def plot_similarity_over_time(similarities):
    # 각 날짜 범위의 중간 날짜를 계산
    mid_dates = [(np.datetime64(start) + (np.datetime64(end) - np.datetime64(start)) / 2) for start, end, _, _, _ in similarities]
    
    # MAE와 RMSE 리스트 추출
    maes = [mae for _, _, mae, _, _ in similarities]
    rmses = [rmse for _, _, rmse, _, _ in similarities]

    # 그래프 그리기
    plt.figure(figsize=(10, 6))

    # MAE 그래프
    plt.plot(mid_dates, maes, marker='o', label='MAE', color='blue', linestyle='-')

    # RMSE 그래프
    plt.plot(mid_dates, rmses, marker='s', label='RMSE', color='red', linestyle='--')

    # 그래프 설정
    plt.title('MAE and RMSE Over Time')
    plt.xlabel('Date Range (Midpoint)')
    plt.ylabel('Error Value')
    plt.xticks(rotation=45)
    plt.legend()

    # 그래프 출력
    plt.tight_layout()
    plt.show()



def calculate_similarity(mean_predicted_prices, actual_20days_prices):
    """
    mean_predicted_prices와 actual_20days_prices 간의 유사도를 계산하는 함수
    """

    # 평균 절대 오차(MAE)
    mae = mean_absolute_error(actual_20days_prices, mean_predicted_prices)
    
    # 평균 제곱근 오차(RMSE)
    rmse = np.sqrt(mean_squared_error(actual_20days_prices, mean_predicted_prices))
    
    # 차이의 리스트 (절대값 기준)
    differences = np.abs(mean_predicted_prices - actual_20days_prices)
    
    return mae, rmse, differences


def calculate_accuracy_metrics(actual, predicted):
    # 실제값과 예측값을 동일한 길이로 맞추기
    min_length = min(len(actual), len(predicted))
    actual = actual[:min_length]
    predicted = predicted[:min_length]

    # 데이터 스케일링
    scaler = StandardScaler()
    actual_scaled = scaler.fit_transform(actual.reshape(-1, 1)).flatten()
    predicted_scaled = scaler.transform(predicted.reshape(-1, 1)).flatten()

    # 평가 메트릭 계산
    mae = mean_absolute_error(actual_scaled, predicted_scaled)
    mse = mean_squared_error(actual_scaled, predicted_scaled)
    r2 = r2_score(actual_scaled, predicted_scaled)
    accuracy_direction = np.mean((np.sign(actual_scaled) == np.sign(predicted_scaled)).astype(int))

    print(f'Mean Absolute Error (MAE): {mae}')
    print(f'Mean Squared Error (MSE): {mse}')
    print(f'R-squared (R2): {r2}')
    print(f'Prediction Direction Accuracy: {accuracy_direction * 100}%')
