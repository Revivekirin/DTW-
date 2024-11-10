import yfinance as yf
import pandas as pd
import numpy as np
from dash import Dash, dcc, html, Input, Output
import plotly.graph_objects as go
from volatility import fetch_stock_data, volatility
from news import get_news_summaries_for_periods
from typing import List

app = Dash(__name__)

app.layout = html.Div(style={'backgroundColor': '#f4f7fc', 'padding': '20px'}, children=[
    html.H1("Stock Volatility Analysis", style={'textAlign': 'center', 'color': '#2d3b5f'}),
    
    html.Div(style={'marginBottom': '20px'}, children=[
        html.Label("Ticker Symbol:", style={'color': '#2d3b5f'}),
        dcc.Input(
            id="ticker-input",
            value="AAPL",
            type="text",
            placeholder="Enter ticker symbol",
            style={'width': '300px', 'padding': '8px', 'borderRadius': '5px', 'border': '1px solid #ddd'}
        ),
    ]),

    html.Div(style={'backgroundColor': '#ffffff', 'padding': '20px', 'borderRadius': '8px', 'boxShadow': '0 4px 10px rgba(0, 0, 0, 0.1)', 'marginBottom': '20px'}, children=[
        html.Label("Select Date Range:", style={'color': '#2d3b5f'}),
        dcc.Input(id="start-date-input", value="2023-01-01", type="text", placeholder="Start Date (YYYY-MM-DD)", style={'marginRight': '10px'}),
        dcc.Input(id="end-date-input", value="2024-01-01", type="text", placeholder="End Date (YYYY-MM-DD)"),
    ]),

    html.Button("Submit", id="submit-button", n_clicks=0, 
                style={'backgroundColor': '#4caf50', 'color': 'white', 'padding': '10px 20px', 'border': 'none', 'borderRadius': '5px', 'cursor': 'pointer'}),

    html.Div(id='news-output', style={'marginTop': '20px'}),
    dcc.Graph(id="volatility-graph")
])

@app.callback(
    [Output("volatility-graph", "figure"),
     Output("news-output", "children")],
    [Input("submit-button", "n_clicks")],
    [Input("ticker-input", "value"),
     Input("start-date-input", "value"),
     Input("end-date-input", "value")]
)
def update_graph(n_clicks, ticker, start_date, end_date):
    if n_clicks > 0:
        # Fetch and process stock data
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

        # Highlight high volatility periods
        for start, end in high_volatility_periods:
            fig.add_trace(go.Scatter(
                x=[start, end],
                y=[stock_data['Close'].loc[start], stock_data['Close'].loc[end]], 
                mode='lines',
                line=dict(color='green', width=4), 
                name=f'High Volatility: {start.date()} to {end.date()}',
                showlegend=True
            ))

        fig.update_layout(
            title=f"{ticker} Stock Volatility Analysis",
            xaxis_title="Date",
            yaxis_title="Close Price",
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

        summaries = get_news_summaries_for_periods(high_volatility_periods, ticker)
        news_output = [
            html.Div([
                html.H4(f"High Volatility Period: {summary['start_date'].date()} to {summary['end_date'].date()}"),
                html.Pre(f"Summary: {summary['summary']}", style={'white-space': 'pre-wrap'}),
                html.Pre(f"Label: {summary['label']}", style={'white-space': 'pre-wrap', 'color': 'blue'})  # Label 추가
            ]) for summary in summaries
        ]

        return fig, news_output

    # Return empty graph and message if no data
    return go.Figure(), "Please input ticker and date range, then submit."

if __name__ == "__main__":
    app.run_server(debug=True)