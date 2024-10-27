import plotly.graph_objs as go
from pattern_search import find_most_similar_pattern
import pandas as pd
from volatility import volatility

def plot_stock_patterns(ticker, data_input, data_pattern, min_distances, n_days, data_with_ta):
    fig = go.Figure()

    fig.add_trace(go.Scatter(
        x=data_input.index,
        y=data_input['Close'],
        mode='lines',
        name='Input Data Pattern',
        line=dict(color='white', width=3),  # 선 두께 조정
        opacity=0.3
    ))

    # 유사한 패턴들
    color_cycle = ['red', 'green', 'orange', 'purple', 'cyan']
    for i, (_, start_index) in enumerate(min_distances):
        color = color_cycle[i % len(color_cycle)]
        pattern_indices = data_pattern.index[start_index:start_index + n_days]
        pattern_values = data_pattern['Close'].iloc[start_index:start_index + n_days]

        fig.add_trace(go.Scatter(
            x=pattern_indices,
            y=pattern_values,
            mode='lines',
            name=f'Similar Pattern {i + 1}',
            line=dict(color=color, dash='dash', width=3)  # 선 두께 조정
        ))

    fig.update_layout(
        title=f"{ticker} Comparision with Similar Pattern",
        xaxis_title='Date',
        yaxis_title="Stock Price",
        template="plotly_white",
        plot_bgcolor='#8181F7',  # 배경 색상 변경
        paper_bgcolor='#8181F7',  # 전체 배경 색상 변경
        font=dict(color='white'),  # 글자 색상
        legend=dict(x=0, y=1, traceorder='normal', orientation='h'),  # 레전드 위치 조정
        height=500,  # 그래프 높이 설정
        xaxis=dict(showgrid=True, gridcolor='gray'),  # x축 그리드 설정
        yaxis=dict(showgrid=True, gridcolor='gray')   # y축 그리드 설정
    )

    return fig

def plot_high_volatility_ranges(min_distances, data_pattern, high_volatility_ranges, n_days=10):
    figures = []  # 각 고변동성 구간의 개별 그래프를 저장할 리스트

    color_cycle = ['red', 'green', 'orange', 'purple', 'cyan']

    for j, (start_date, end_date) in enumerate(high_volatility_ranges):
        fig = go.Figure()

        fig.add_trace(go.Scatter(
            x=data_pattern.index,
            y=data_pattern['Close'],
            mode='lines+markers',
            name='Stock Price',
            line=dict(color='#1f77b4', width=3),  
        ))

        start_date = pd.Timestamp(start_date)
        end_date = pd.Timestamp(end_date)

        if start_date in data_pattern.index and end_date in data_pattern.index:
            range_indices = data_pattern.index[data_pattern.index.get_loc(start_date):data_pattern.index.get_loc(end_date) + 1]
            range_values = data_pattern['Close'].loc[start_date:end_date]

            fig.add_trace(go.Scatter(
                x=range_indices,
                y=range_values,
                mode='lines+markers',
                name=f'High Volatility Range {start_date.date()} - {end_date.date()}',
                line=dict(color='white', width=2),
            ))

        for i, (_, start_index) in enumerate(min_distances):
            color = color_cycle[i % len(color_cycle)]
            pattern_indices = data_pattern.index[start_index:start_index + n_days]
            pattern_values = data_pattern['Close'].iloc[start_index:start_index + n_days]

            fig.add_trace(go.Scatter(
                x=pattern_indices,
                y=pattern_values,
                mode='lines+markers',
                name=f'Similar Pattern {i + 1}',
                line=dict(color=color, dash='dash', width=3)  
            ))


        fig.update_layout(
            title=f'High Volatility Range {j + 1}: {start_date.date()} - {end_date.date()}',
            xaxis_title='Date',
            yaxis_title='Price',
            template='plotly_white',
            plot_bgcolor='#8181F7',  # 배경 색상 변경
            paper_bgcolor='#8181F7',  # 전체 배경 색상 변경
            font=dict(color='white'),  # 글자 색상
            legend=dict(x=0, y=1, traceorder='normal', orientation='h'),  # 레전드 위치 조정
            height=500,  # 그래프 높이 설정
            xaxis=dict(showgrid=True, gridcolor='gray'),  # x축 그리드 설정
            yaxis=dict(showgrid=True, gridcolor='gray')   # y축 그리드 설정

        ),
        

        figures.append(fig)

    return figures  # 각 고변동성 구간에 대한 개별 Figure 객체들을 포함한 리스트



