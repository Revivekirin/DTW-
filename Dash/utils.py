import pandas as pd
from typing import Tuple

def determine_dates(figure:dict, selected_date:str)->Tuple[pd.Timestamp, pd.Timestamp]:
    """
    주어진 figure에서 selected_date에 포함된 패턴의 첫번째 날짜와 마지막 날짜를 반환합니다.

    :param figure: 그래프 데이터
    :param selected_date: 선택된 날짜
    :return: 시작일과 종료일
    """
    selected_date = pd.to_datetime(selected_date)

    for data in figure['data']:
        # 'Stock Price' 데이터는 건너뜁니다.
        if data['name'] == 'Stock Price':
            continue
        
        x_dates = pd.to_datetime(data['x'])  # x값을 pd.Timestamp로 변환

        # 선택된 날짜가 x_dates에 있는지 확인
        if selected_date in x_dates.values:
            index = x_dates.get_loc(selected_date)  # 선택된 날짜의 인덱스를 찾기
            start_date = pd.to_datetime(data['x'][0])  # 첫 번째 날짜
            end_date = pd.to_datetime(data['x'][-1])  # 마지막 날짜
            return start_date, end_date
        
    raise ValueError(f"Selected date {selected_date} not found in figure data.")