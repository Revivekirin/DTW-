from datetime import datetime, timedelta

def generate_date_ranges(start_date: str, end_date: str, day_gap: int = 20) -> tuple:
    """
    시작 날짜와 종료 날짜를 기준으로 1년 주기의 start_dates와 end_dates 리스트를 생성합니다.
    day_gap: 두 날짜 사이의 간격을 의미합니다. 기본값은 20일입니다.
    """
    # 날짜 포맷 지정
    date_format = "%Y-%m-%d"
    current_start_date = datetime.strptime(start_date, date_format)
    
    # 시작 날짜와 종료 날짜 리스트 생성
    start_dates = []
    end_dates = []

    # 종료 날짜를 datetime 객체로 변환
    final_end_date = datetime.strptime(end_date, date_format)

    # 날짜 리스트 생성
    while current_start_date < final_end_date:
        # 종료 날짜를 1년 뒤로 설정
        current_end_date = current_start_date + timedelta(days=365)
        
        # 마지막 종료 날짜가 최종 종료 날짜를 넘지 않도록 조정
        if current_end_date > final_end_date:
            current_end_date = final_end_date
        
        # start_dates와 end_dates에 추가
        start_dates.append(current_start_date.strftime(date_format))
        end_dates.append(current_end_date.strftime(date_format))
        
        # 20일씩 이동
        current_start_date += timedelta(days=day_gap)
    
    return start_dates, end_dates