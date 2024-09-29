from sklearn.metrics import mean_absolute_error, mean_squared_error, r2_score
import numpy as np

def calculate_accuracy_metrics(actual, predicted):
    # 실제값과 예측값을 동일한 길이로 맞추기
    min_length = min(len(actual), len(predicted))
    actual = actual[:min_length]
    predicted = predicted[:min_length]

    # 평가 메트릭 계산
    mae = mean_absolute_error(actual, predicted)
    mse = mean_squared_error(actual, predicted)
    r2 = r2_score(actual, predicted)
    accuracy_direction = np.mean((np.sign(actual) == np.sign(predicted)).astype(int))

    print(f'Mean Absolute Error (MAE): {mae}')
    print(f'Mean Squared Error (MSE): {mse}')
    print(f'R-squared (R2): {r2}')
    print(f'Prediction Direction Accuracy: {accuracy_direction * 100}%')
