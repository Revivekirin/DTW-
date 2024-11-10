import plotly.graph_objs as go
import pandas as pd


def plot_stock_patterns(ticker, data_input, data_pattern, min_distances, n_days, data_with_ta, recent_start_date, recent_end_date):
    fig = go.Figure()
    print(ticker)

    fig.add_trace(go.Scatter(
        x=data_input.index,
        y=data_input['Close'],
        mode='lines',
        name='Input Data Pattern',
        line=dict(color='blue', width=3),  # 선 두께 조정
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
        
     # recent_start_date부터 recent_end_date까지 힌색으로 구간 표시
    fig.add_vrect(
        x0=recent_start_date, x1=recent_end_date,
        fillcolor="black", line_width=3  # 하얀색 반투명 박스, 테두리 없음
    )
    
    # 최근 기간을 설명하는 주석 추가
    fig.add_annotation(
        x=recent_start_date, y=max(data_input['Close']),
        text="Recent Start Date",
        showarrow=True, arrowhead=1, ax=0, ay=-40, font=dict(color='black')
    )
    fig.add_annotation(
        x=recent_end_date, y=max(data_input['Close']),
        text="Recent End Date",
    )

    fig.update_layout(
        title=f"{ticker} Comparision with Similar Pattern",
        xaxis_title='Date',
        yaxis_title="Stock Price",
        template="plotly_white",
        plot_bgcolor='#8181F7',  
        paper_bgcolor='#8181F7',  
        font=dict(color='white'), 
        legend=dict(x=0, y=1, traceorder='normal', orientation='h'), 
        height=500,  
        xaxis=dict(showgrid=True, gridcolor='gray'), 
        yaxis=dict(showgrid=True, gridcolor='gray')  
    )

    return fig