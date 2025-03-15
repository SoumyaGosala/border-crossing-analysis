#!/usr/bin/env python
# coding: utf-8

# In[1]:

import pandas as pd
import seaborn as sns
import matplotlib.pyplot as plt
import numpy as np
import plotly.express as px
import warnings
import dash
from dash import dcc, html
from dash.dependencies import Input, Output
from statsmodels.tsa.holtwinters import ExponentialSmoothing

# Suppress warnings
warnings.simplefilter(action='ignore', category=FutureWarning)
warnings.simplefilter(action='ignore', category=UserWarning)

# Load the dataset
file_path = "Border_Crossing_Entry_Data.csv"
df = pd.read_csv(file_path)

# Convert Date column to datetime format
df['Date'] = pd.to_datetime(df['Date'], format='%b %Y', errors='coerce')

# Extract month and year
df['Month'] = df['Date'].dt.month_name()
df['Year'] = df['Date'].dt.year

# Filter only numeric columns for correlation analysis
numeric_df = df.select_dtypes(include=[np.number])

# Initialize Dash App with external stylesheet for better UI
theme = "https://codepen.io/chriddyp/pen/bWLwgP.css"
app = dash.Dash(__name__, external_stylesheets=[theme])

# Layout of the dashboard
app.layout = html.Div([
    html.H1("Border Crossing Analysis", style={'textAlign': 'center', 'color': '#007BFF'}),
    
    # Slicer row
    html.Div([
        html.Label("Select a Measure:", style={'fontSize': '18px', 'fontWeight': 'bold'}),
        dcc.Dropdown(
            id='measure-dropdown',
            options=[{'label': m, 'value': m} for m in df['Measure'].unique()],
            value=df['Measure'].unique()[0],
            style={'width': '40%', 'margin': 'auto', 'display': 'inline-block'}
        )
    ], style={'textAlign': 'center', 'padding': '20px'}),

    # Graphs
    html.Div([
        dcc.Graph(id='measure-bar-chart'),
        dcc.Graph(id='dynamic-pie-chart')
    ], style={'display': 'grid', 'gridTemplateColumns': 'repeat(2, 1fr)', 'gap': '20px', 'padding': '20px'}),

    html.Div([
        dcc.Graph(id='monthly-trends')
    ], style={'padding': '20px'}),

    html.Div([
        dcc.Graph(id='future-trend-forecast')
    ], style={'padding': '20px'}),

    html.Div([
        dcc.Graph(id='correlation-heatmap'),
        dcc.Graph(id='forecasting-histogram')
    ], style={'display': 'grid', 'gridTemplateColumns': 'repeat(2, 1fr)', 'gap': '20px', 'padding': '20px'}),
])

@app.callback(
    Output('future-trend-forecast', 'figure'),
    Input('measure-dropdown', 'value')
)
def update_forecast(selected_measure):
    filtered_df = df[df['Measure'] == selected_measure].groupby('Date')['Value'].sum().reset_index()
    model = ExponentialSmoothing(filtered_df['Value'], trend='add', seasonal=None).fit()
    forecast_index = pd.date_range(start=filtered_df['Date'].max(), periods=7, freq='M')
    forecast_values = model.forecast(steps=6)
    forecast_df = pd.DataFrame({'Date': forecast_index, 'Forecast': forecast_values})
    
    fig = px.line(filtered_df, x='Date', y='Value', title=f'Forecasted Trends for {selected_measure}',
                  template='plotly_white', labels={'Value': 'Total Crossings', 'Date': 'Date'},
                  markers=True)
    fig.add_scatter(x=forecast_df['Date'], y=forecast_df['Forecast'], mode='lines+markers',
                     name='Forecasted Crossings', line=dict(color='red', dash='dot'))
    return fig

@app.callback(
    Output('forecasting-histogram', 'figure'),
    Input('measure-dropdown', 'value')
)
def update_histogram(selected_measure):
    filtered_df = df[df['Measure'] == selected_measure]['Value']
    
    fig = px.histogram(filtered_df, x='Value', nbins=50, title='Forecasting Histogram of Border Crossings',
                        template='plotly_white', labels={'Value': 'Number of Crossings'}, opacity=0.7)
    return fig

server = app.server

if __name__ == '__main__':
    app.run_server(debug=True)



# In[ ]:




