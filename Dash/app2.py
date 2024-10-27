import dash
from dash import dcc, html
import plotly.graph_objs as go
import pandas as pd
import yfinance as yf
from dash.dependencies import Input, Output
from params import params, params_volatility
from pattern_search_plotly import plot_stock_patterns, plot_high_volatility_ranges

# Dash 앱 생성
app = dash.Dash(__name__)

# Dash 레이아웃 설정
app.layout = html.Div(children=[
    html.H1(children='주식 가격 시각화'),

    # 반투명 블록을 생성하여 다운로드할 데이터 범위 선택을 포함
    html.Div(style={
        'backgroundColor': 'rgba(129, 129, 247, 0.8)',  # 배경색과 투명도
        'padding': '20px',  # 여백
        'borderRadius': '8px',  # 모서리 둥글기
        'boxShadow': '0 4px 8px rgba(0, 0, 0, 0.1)',  # 그림자 효과
        'marginBottom': '20px'  # 아래쪽 여백
    }, children=[
        html.Label("다운로드할 데이터 범위 선택: "),
        dcc.DatePickerRange(
            id='download-date-range',
            min_date_allowed=pd.to_datetime('2020-01-01').date(),
            max_date_allowed=pd.to_datetime('today').date(),
            start_date=pd.to_datetime('2023-01-01').date(),
            end_date=pd.to_datetime('2024-10-01').date()
        ),
    ]),

    # 반투명 블록을 생성하여 최근 데이터 범위 선택을 포함
    html.Div(style={
        'backgroundColor': 'rgba(129, 129, 247, 0.8)',  # 배경색과 투명도
        'padding': '20px',  # 여백
        'borderRadius': '8px',  # 모서리 둥글기
        'boxShadow': '0 4px 8px rgba(0, 0, 0, 0.1)',  # 그림자 효과
        'marginBottom': '20px'  # 아래쪽 여백
    }, children=[
        html.Label("분석할 최근 데이터 범위 선택: "),
        dcc.DatePickerRange(
            id='recent-date-range',
            min_date_allowed=pd.to_datetime('2020-01-01').date(),
            max_date_allowed=pd.to_datetime('today').date(),
            start_date=pd.to_datetime('2024-09-20').date(),
            end_date=pd.to_datetime('2024-10-01').date()
        ),
    ]),

    html.Button('데이터 다운로드 및 그래프 업데이트', id='update-button', n_clicks=0),
    html.Div(id='output-container', style={'marginTop': 20}),
    
    # 드롭다운을 오른쪽 정렬하기 위한 Flexbox Div
    html.Div(style={'display': 'flex', 'justifyContent': 'flex-end', 'marginBottom': '20px'}, children=[
        dcc.Dropdown(id='volatility-dropdown',
                     options=[],
                     placeholder="변동성 구간 선택",
                     value=None,
                     style={'width': '530px'})  # 드롭다운 폭 고정
    ]),
    
    # 그래프를 좌우로 배치하기 위한 Div
    html.Div([
        html.Div(dcc.Graph(id='stock-graph'), style={'flex': '1', 'padding': '10px'}),
        html.Div(id='volatility-graphs-container', style={'flex': '1', 'padding': '10px'})
    ], style={'display': 'flex'})  # Flexbox를 사용하여 그래프를 나란히 배치
])


figures = []

@app.callback(
    [Output('stock-graph', 'figure'),
     Output('volatility-dropdown', 'options'),  
     Output('output-container', 'children')],
    [Input('update-button', 'n_clicks')],
    [Input('download-date-range', 'start_date'),
     Input('download-date-range', 'end_date'),
     Input('recent-date-range', 'start_date'),
     Input('recent-date-range', 'end_date')]
)
def update_graph(n_clicks, pattern_start_date, pattern_end_date, recent_start_date, recent_end_date):
    global figures

    if pattern_start_date and pattern_end_date and recent_start_date and recent_end_date:
        ticker='AAPL'
        stock_data = yf.download(ticker, start=pattern_start_date, end=pattern_end_date)

        min_distances, data_pattern_filtered, data_input = params(
            ticker, pattern_start_date, pattern_end_date, recent_start_date, recent_end_date
        )

        figure_pattern = plot_stock_patterns(
            ticker, 
            data_input, 
            data_pattern_filtered, 
            min_distances, 
            n_days=20, 
            data_with_ta=stock_data
        )

        pattern_graph = {
            'data': [
                go.Scatter(
                    x=figure_pattern['data'][i]['x'],
                    y=figure_pattern['data'][i]['y'],
                    mode='lines+markers',
                    line=dict(width=3),  # 선 두께 조정
                    marker=dict(size=6),  # 마커 크기 조정
                    name=figure_pattern['data'][i]['name'],
                ) for i in range(len(figure_pattern['data']))
            ],
            'layout': go.Layout(
                title=f'{ticker} 주식 가격 ({pattern_start_date}부터 {pattern_end_date}까지)',
                xaxis={'title': '날짜'},
                yaxis={'title': '가격'},
                plot_bgcolor='#8181F7',  # 그래프 배경 색상 변경
                paper_bgcolor='#8181F7',  # 전체 배경 색상 변경
                font=dict(color='white'),  # 글자 색상
                legend=dict(
                    x=0.5,  # 레전드의 x 위치 (가운데 정렬)
                    y=-0.25,  # 레전드의 y 위치 (그래프 아래)
                    xanchor='center',  # 레전드의 x 앵커
                    yanchor='top',  # 레전드의 y 앵커
                    orientation='h',  # 레전드 방향 (수평)
                )
            )
        }

        min_distances_volatility, data_pattern_filtered_volatility, data_input_volatility, high_volatility_ranges = params_volatility(
            ticker, pattern_start_date, pattern_end_date, recent_start_date, recent_end_date
        )
        
        figures = plot_high_volatility_ranges(
            min_distances_volatility, data_pattern_filtered_volatility, high_volatility_ranges
        )

        volatility_options = [{'label':f'Range {i+1}', 'value':i} for i in range(len(figures))]

        data_summary = [
            html.H4(f"선택한 범위: {pattern_start_date}부터 {pattern_end_date}까지"),
            html.H4(f"최근 데이터 범위: {recent_start_date}부터 {recent_end_date}까지"),
        ]

        return pattern_graph, volatility_options, data_summary
    
    return {}, [], "날짜 범위를 선택해 주세요."

@app.callback(
    Output('volatility-graphs-container', 'children'),
    [Input('volatility-dropdown', 'value')]
)
def update_volatility_graph(selected_range):
    if selected_range is not None:
        figure = figures[selected_range]

        # Update the layout of the volatility graph
        figure['layout'].update({
            'plot_bgcolor': '#8181F7',  # 배경 색상 변경
            'paper_bgcolor': '#8181F7',  # 전체 배경 색상 변경
            'font': dict(color='white'),  # 글자 색상
            'legend': {
                'x': 0.5,  # 레전드를 그래프의 중앙에 위치
                'y': -0.2,  # 레전드를 그래프 아래로 이동
                'traceorder': 'normal',
                'orientation': 'h',  # 수평으로 배치
                'xanchor': 'center',  # x축 중앙 앵커
                'yanchor': 'top'  # y축 상단 앵커
            },
            'xaxis': {'showgrid': True, 'gridcolor': 'gray'},  # x축 그리드 설정
            'yaxis': {'showgrid': True, 'gridcolor': 'gray'},  # y축 그리드 설정
            'height': 500  # 그래프 높이 설정
        })

        # 라인과 마커 강조
        for data in figure['data']:
            data.update({
                'line': dict(width=3),  # 선 두께 조정
                'marker': dict(size=6)  # 마커 크기 조정
            })

        return html.Div([
            dcc.Graph(
                id=f"volatility-graph-{selected_range}",
                figure=figure
            )
        ], style={'width': '100%'})  # 전체 가로 폭 100%로 설정

    return []


# 애플리케이션 실행
if __name__ == '__main__':
    app.run_server(debug=True)



