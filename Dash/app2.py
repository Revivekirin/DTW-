import dash
from dash import dcc, html
import plotly.graph_objs as go
import pandas as pd
import yfinance as yf
from dash import MATCH
from dash.dependencies import Input, Output, State
from dash.exceptions import PreventUpdate

from params import params, params_volatility
from pattern_search_plotly import plot_stock_patterns, plot_high_volatility_ranges
from news import get_news_summary
from utils import determine_dates

summary_style = {
    "fontFamily": "Arial, sans-serif",
    "fontSize": "16px",
    "color": "#333333",
    "backgroundColor": "#f4f6f9",
    "padding": "15px",
    "borderRadius": "8px",
    "boxShadow": "0px 4px 8px rgba(0, 0, 0, 0.1)",
    "whiteSpace": "pre-line"
}

loading_style = {
    "fontFamily": "Arial, sans-serif",
    "fontSize": "16px",
    "color": "#888888",
    "padding": "15px",
    "borderRadius": "8px",
    "backgroundColor": "#f4f6f9",
    "whiteSpace": "pre-line"
}


# Dash 앱 생성
app = dash.Dash(__name__)

# Dash 레이아웃 설정
app.layout = html.Div(children=[
    html.H1(children='주식 가격 시각화'),

    # Ticker 입력 필드 추가
    html.Div(style={'marginBottom': '20px'}, children=[
        html.Label("Ticker 입력: "),
        dcc.Input(
            id='ticker-input',
            type='text',
            placeholder='Enter ticker symbol',
            value='',  # 초기값을 빈 문자열로 설정
            style={'width': '200px'}
        ),
    ]),

    # 반투명 블록을 생성하여 다운로드할 데이터 범위 선택을 포함
    html.Div(style={
        'backgroundColor': 'rgba(129, 129, 247, 0.5)',  # 배경색과 투명도
        'padding': '20px',  # 여백
        'borderRadius': '8px',  # 모서리 둥글기
        'boxShadow': '0 4px 8px rgba(0, 0.2, 0.2, 0.4)',  # 그림자 효과
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
        'backgroundColor': 'rgba(129, 129, 247, 0.5)',  # 배경색과 투명도
        'padding': '20px',  # 여백
        'borderRadius': '8px',  # 모서리 둥글기
        'boxShadow': '0 4px 8px rgba(0, 0.2, 0.2, 0.4)',  # 그림자 효과
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
    ], style={'display': 'flex'}),  # Flexbox를 사용하여 그래프를 나란히 배치

    # # 뉴스 요약 결과를 표시할 Div
    # html.Div(id='news-summary-container', style={
    #     'backgroundColor': '#f0f8ff',
    #     'padding': '15px',
    #     'borderRadius': '8px',
    #     'marginTop': '20px',
    #     'boxShadow': '0 4px 8px rgba(0, 0, 0, 0.2)',
    #     'maxWidth': '530px',
    #     'width': '100%',
    # })

])


figures = []  # plot_high_volatility_ranges 결과


@app.callback(
    [Output('stock-graph', 'figure'),
     Output('volatility-dropdown', 'options'),  
     Output('output-container', 'children')],
    [Input('update-button', 'n_clicks')],
    [Input('ticker-input', 'value'),
     Input('download-date-range', 'start_date'),
     Input('download-date-range', 'end_date'),
     Input('recent-date-range', 'start_date'),
     Input('recent-date-range', 'end_date')]
)

def update_graph(n_clicks, ticker, pattern_start_date, pattern_end_date, recent_start_date, recent_end_date):
    global figures

    if ticker and pattern_start_date and pattern_end_date and recent_start_date and recent_end_date:

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

figure =[]   # volatility 결과중 selected_range의 결과

@app.callback(
    Output('volatility-graphs-container', 'children'),
    [Input('volatility-dropdown', 'value')],
    [State('ticker-input', 'value')]
)
def update_volatility_graph(selected_range, ticker):
    global figure

    if selected_range is None:
        empty_figure = {'data': [], 'layout': {'title': 'Volatility Graph'}}
        return html.Div([dcc.Graph(id="volatility-graph-empty", figure=empty_figure)], style={'width': '100%'})
        
    figure = figures[selected_range]
    print(figure)
    
    # Update the layout of the volatility graph
    figure['layout'].update({
        'plot_bgcolor': '#8181F7',
        'paper_bgcolor': '#8181F7',
        'font': dict(color='white'),
        'legend': {
            'x': 0.5,
            'y': -0.2,
            'traceorder': 'normal',
            'orientation': 'h',
            'xanchor': 'center',
            'yanchor': 'top'
        },
        'xaxis': {'showgrid': True, 'gridcolor': 'gray'},
        'yaxis': {'showgrid': True, 'gridcolor': 'gray'},
        'height': 500
    })

    # 라인과 마커 강조
    for data in figure['data']:
        data.update({
            'line': dict(width=3),
            'marker': dict(size=6)
        })

    return html.Div([
        dcc.Graph(
            id={'type': 'volatility-graph', 'index': selected_range},
            figure=figure
        ),
        html.Div(id={'type': 'news-summary-container', 'index': selected_range})  # MATCH를 사용하기 위해 수정
    ], style={'width': '100%'})


@app.callback(
    [
        Output({'type': 'news-summary-container', 'index': MATCH}, 'children'),
        Output({'type': 'news-summary-container', 'index': MATCH}, 'style')
    ],
    Input({'type': 'volatility-graph', 'index': MATCH}, 'clickData'),
    State('ticker-input', 'value')
)
def update_news_summary(selected_click_data, ticker):
    if selected_click_data:
        clicked_point = selected_click_data['points'][0]
        selected_date = clicked_point['x']

        try:
            start_date, end_date = determine_dates(figure, selected_date)
            news_summary = get_news_summary(ticker, start_date=start_date, end_date=end_date)
            print(news_summary)

            if news_summary:
                # 구조화되고 스타일이 적용된 뉴스 요약 생성
                news_summary_html = html.Div(
                    children=[
                        html.H3("뉴스 요약", style={'textAlign': 'center', 'color': '#333'}),
                        html.P(news_summary, style={'fontSize': '16px', 'lineHeight': '1.5'}),
                        html.Div(
                            style={
                                'backgroundColor': '#f0f8ff',
                                'padding': '15px',
                                'borderRadius': '8px',
                                'marginTop': '20px',
                                'boxShadow': '0 4px 8px rgba(0, 0, 0, 0.2)',
                                'maxWidth': '530px',
                                'width': '100%',
                            }
                        )
                    ],
                    style={'margin': '20px'}
                )
                return news_summary_html
            else:
                return "뉴스 요약이 없습니다", loading_style

        except Exception as e:
            return f"뉴스 요약을 가져오는 중 오류 발생: {str(e)}"

    return "news summary가 존재하지 않습니다"


# 애플리케이션 실행
if __name__ == '__main__':
    app.run_server(debug=True)

