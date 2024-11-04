import yfinance as yf
import pandas as pd
import numpy as np
from dash import Dash, dcc, html, Input, Output
import plotly.graph_objects as go
from volatility import fetch_stock_data, volatility
from typing import List, Optional, Dict
from news import get_news_summaries_for_volatility_periods

app =Dash(__name__)

high_volatility_periods=[]

app.layout = html.Div([
    html.H1("Stock Volatility Analysis"),
    html.Label("Ticker Symbol:"),
    dcc.Input(id="ticker-input", value="AAPL", type="text"),
    html.Label("Start Date:"),
    dcc.Input(id="start-date-input", value="2023-01-01", type="text"),
    html.Label("End Date:"),
    dcc.Input(id="end-date-input", value="2024-01-01", type="text"),
    html.Button("Submit", id="submit-button", n_clicks=0),
    dcc.Graph(id="volatility-graph"),
    html.Div(id='news-output')
])

@app.callback(
    Output("volatility-graph", "figure"),
    Output("news-output", "children"),
    Input("submit-button", "n_clicks"),
    Input("ticker-input", "value"),
    Input("start-date-input", "value"),
    Input("end-date-input", "value")
)
def update_graph(n_clicks, ticker, start_date, end_date):
    global high_volatility_periods

    if n_clicks>0:
        stock_data = fetch_stock_data(ticker, start_date, end_date)
        high_volatility_periods = volatility(stock_data)

        fig = go.Figure()
        fig.add_trace(go.Scatter(
            x=stock_data.index, 
            y=stock_data['Close'],
            mode='lines', 
            name="Close Price",
            line=dict(color='rgba(0, 0, 0, 0.5)', width=2) 
        ))

        # 변동성 구간 강조 
        for start, end in high_volatility_periods:
            fig.add_trace(go.Scatter(
                x=[start, end],
                y=[stock_data['Close'].loc[start], stock_data['Close'].loc[end]], 
                mode='lines',
                line=dict(color='green', width=4), 
                name=f'High Volatility: {start.date()} to {end.date()}',
                showlegend=True
            ))

        #레이아웃 설정
        fig.update_layout(
            title=f"{ticker} 주가변동성 분석",
            xaxis_title="Date",
            yaxis_title="Close Price",
            showlegend=True
        )

        summaries = get_news_summaries_for_volatility_periods(high_volatility_periods, ticker)

        news_output=[]
        for summary in summaries:
            news_output.append(html.Div([
                html.H4(f"High Volatility Period: {summary['start_date'].date()} to {summary['end_date'].date()}"),
                html.Pre(summary['summary'], style={'white-space': 'pre-wrap'})
            ]))
        return fig, news_output

    return go.Figure(), []

if __name__=="__main__":
    app.run_server(debug=True)



