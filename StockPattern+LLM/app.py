import dash
from dash import dcc, html
import plotly.graph_objs as go
import pandas as pd
import yfinance as yf
import requests
from dash.dependencies import Input, Output
from flask import Flask, request, jsonify
import json
from params import params
from plot_stock_pattern import plot_stock_patterns
from volatility import volatility
from news import get_news_summaries_for_periods, get_news_data
from flask import Flask, request, jsonify

# Dash 앱 생성
app = dash.Dash(__name__)
server = app.server

app.layout = html.Div(style={'backgroundColor': '#f4f7fc', 'padding': '20px'}, children=[
    html.H1("Stock Price Visualization", style={'textAlign': 'center', 'color': '#2d3b5f'}),
    
    # Ticker 입력 필드
    html.Div(style={'marginBottom': '20px'}, children=[
        html.Label("Ticker 입력:", style={'color': '#2d3b5f'}),
        dcc.Input(
            id='ticker-input',
            type='text',
            placeholder='Enter ticker symbol',
            value='',
            style={'width': '300px', 'padding': '8px', 'borderRadius': '5px', 'border': '1px solid #ddd'}
        ),
    ]),

    # 데이터 범위 선택
    html.Div(style={'backgroundColor': '#ffffff', 'padding': '20px', 'borderRadius': '8px', 'boxShadow': '0 4px 10px rgba(0, 0, 0, 0.1)', 'marginBottom': '20px'}, children=[
        html.Label("다운로드할 데이터 범위 선택:", style={'color': '#2d3b5f'}),
        dcc.DatePickerRange(
            id='download-date-range',
            min_date_allowed=pd.to_datetime('2020-01-01').date(),
            max_date_allowed=pd.to_datetime('today').date(),
            start_date=pd.to_datetime('2023-01-01').date(),
            end_date=pd.to_datetime('2024-10-01').date(),
            style={'padding': '10px', 'borderRadius': '5px'}
        ),
    ]),

    # 버튼
    html.Button('데이터 다운로드 및 그래프 업데이트', id='update-button', n_clicks=0, 
                style={'backgroundColor': '#4caf50', 'color': 'white', 'padding': '10px 20px', 'border': 'none', 'borderRadius': '5px', 'cursor': 'pointer'}),

    html.Div(id='output-container', style={'marginTop': '20px'}),

    # Graph 컴포넌트
    dcc.Graph(id='stock-graph')
])

@app.callback(
    [Output('stock-graph', 'figure'),
     Output('output-container', 'children')],
    [Input('update-button', 'n_clicks')],
    [Input('ticker-input', 'value'),
     Input('download-date-range', 'start_date'),
     Input('download-date-range', 'end_date'),]
)
def update_graph(n_clicks, ticker, pattern_start_date, pattern_end_date):
    if n_clicks > 0:
        high_volatility_periods = []

        if ticker and pattern_start_date and pattern_end_date:
            try:
                # Yahoo Finance에서 데이터 다운로드
                stock_data = yf.download(ticker, start=pattern_start_date, end=pattern_end_date)

                # 데이터가 비어 있으면 예외 처리 (예: 티커가 삭제되었거나 데이터가 없음)
                if stock_data.empty:
                    raise ValueError(f"No price data found for {ticker} from {pattern_start_date} to {pattern_end_date}")

                high_volatility_periods = volatility(stock_data)

                recent_start_date = pd.to_datetime(high_volatility_periods[-1][0])
                recent_end_date = pd.to_datetime(high_volatility_periods[-1][1].date())

                # params 함수 호출
                min_distances, data_pattern_filtered, data_input = params(
                    ticker, pattern_start_date, pattern_end_date, recent_start_date, recent_end_date)

                figure_pattern = plot_stock_patterns(
                    ticker, 
                    data_input, 
                    data_pattern_filtered, 
                    min_distances, 
                    n_days=20, 
                    data_with_ta=stock_data,
                    recent_start_date=recent_start_date,
                    recent_end_date=recent_end_date
                )

                # 최종 그래프 생성
                pattern_graph = {
                    'data': [
                        go.Scatter(
                            x=figure_pattern['data'][i]['x'],
                            y=figure_pattern['data'][i]['y'],
                            mode='lines+markers',
                            line=dict(width=3),
                            marker=dict(size=6),
                            name=figure_pattern['data'][i]['name'],
                        ) for i in range(len(figure_pattern['data']))
                    ],
                    'layout': go.Layout(
                        title=f'{ticker} 주식 가격 ({pattern_start_date}부터 {pattern_end_date}까지)',
                        xaxis={'title': '날짜'},
                        yaxis={'title': '가격'},
                        plot_bgcolor='#f0f0f5',
                        paper_bgcolor='#f4f7fc',
                        font=dict(color='#2d3b5f'),
                        legend=dict(
                            x=0.5,
                            y=-0.25,
                            xanchor='center',
                            yanchor='top',
                            orientation='h',
                        )
                    )
                }

                x_values=[]
                for scatter in figure_pattern['data'][1:]:
                    x_values.append((pd.Timestamp(scatter['x'][0]), pd.Timestamp(scatter['x'][-1])))

                summaries = get_news_summaries_for_periods(x_values, ticker)

                news_output=[]
                for summary in summaries:
                    news_output.append(html.Div([
                        html.H4(f"High Volatility Period: {summary['start_date'].date()} to {summary['end_date'].date()}"),
                        html.Pre(summary['summary'], style={'white-space': 'pre-wrap'})
                    ]))

                return pattern_graph, news_output

            except ValueError as e:
                # 데이터가 없을 경우 처리
                return {
                    'data': [],
                    'layout': go.Layout(
                        title="데이터가 없습니다.",
                        xaxis={'title': '날짜'},
                        yaxis={'title': '가격'}
                    )
                }, f"Error: {str(e)}"
            except Exception as e:
                # 그 외 오류 처리
                return {
                    'data': [],
                    'layout': go.Layout(
                        title="알 수 없는 오류 발생",
                        xaxis={'title': '날짜'},
                        yaxis={'title': '가격'}
                    )
                }, f"Error: {str(e)}"

    # 빈 그래프와 빈 출력 반환
    empty_graph = {
        'data': [],
        'layout': go.Layout(
            title="데이터가 없습니다.",
            xaxis={'title': '날짜'},
            yaxis={'title': '가격'}
        )
    }
    return empty_graph, ""


# 애플리케이션 실행
if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=8050)
