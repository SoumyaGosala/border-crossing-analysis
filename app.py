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

    # Graph 1 & Graph 2 side by side
    html.Div([
        dcc.Graph(id='measure-bar-chart', style={'border': '1px solid #ddd', 'borderRadius': '10px', 'padding': '10px'}),
        dcc.Graph(id='dynamic-pie-chart', style={'border': '1px solid #ddd', 'borderRadius': '10px', 'padding': '10px'})
    ], style={'display': 'grid', 'gridTemplateColumns': 'repeat(2, 1fr)', 'gap': '20px', 'padding': '20px'}),

    # Graph 3: Monthly Trends
    html.Div([
        dcc.Graph(id='monthly-trends')
    ], style={'padding': '20px'}),

    # Graph 4: Time Series Trends
    html.Div([
        dcc.Graph(id='time-series-trend')
    ], style={'padding': '20px'}),

    # Graph 5 & Graph 6 side by side
    html.Div([
        dcc.Graph(id='correlation-heatmap', style={'border': '1px solid #ddd', 'borderRadius': '10px', 'padding': '10px'}),
        dcc.Graph(id='total-crossings-state', style={'border': '1px solid #ddd', 'borderRadius': '10px', 'padding': '10px'})
    ], style={'display': 'grid', 'gridTemplateColumns': 'repeat(2, 1fr)', 'gap': '20px', 'padding': '20px'})
])

@app.callback(
    Output('measure-bar-chart', 'figure'),
    Input('measure-dropdown', 'value')
)
def update_bar_chart(selected_measure):
    filtered_df = df[df['Measure'] == selected_measure]
    fig = px.bar(filtered_df.groupby('State')['Value'].sum().reset_index(), x='Value', y='State',
                 title=f'Total Border Crossings for {selected_measure}', orientation='h',
                 color='State', color_continuous_scale='viridis', template='plotly_white')
    return fig

@app.callback(
    Output('dynamic-pie-chart', 'figure'),
    Input('measure-dropdown', 'value')
)
def update_pie_chart(selected_measure):
    filtered_df = df[df['Measure'] == selected_measure]
    fig = px.pie(filtered_df, names='State', values='Value', title=f'{selected_measure} Distribution by State')
    return fig

@app.callback(
    Output('monthly-trends', 'figure'),
    Input('measure-dropdown', 'value')
)
def update_monthly_trends(selected_measure):
    filtered_df = df[df['Measure'] == selected_measure].groupby(['Month', 'Year'])['Value'].sum().reset_index()
    fig = px.line(filtered_df, x='Month', y='Value', color='Year', title=f'Monthly Trends for {selected_measure}',
                  template='plotly_white')
    return fig

@app.callback(
    Output('time-series-trend', 'figure'),
    Input('measure-dropdown', 'value')
)
def update_time_series(selected_measure):
    filtered_df = df[df['Measure'] == selected_measure]
    fig = px.line(filtered_df, x='Date', y='Value', title=f'Trend of Border Crossings Over Time for {selected_measure}',
                  template='plotly_white')
    return fig

@app.callback(
    Output('correlation-heatmap', 'figure'),
    Input('measure-dropdown', 'value')
)
def update_correlation_heatmap(selected_measure):
    fig = px.imshow(numeric_df.corr(), color_continuous_scale='viridis',
                    title='Correlation Matrix', template='plotly_white')
    return fig

@app.callback(
    Output('total-crossings-state', 'figure'),
    Input('measure-dropdown', 'value')
)
def update_total_crossings_state(selected_measure):
    filtered_df = df[df['Measure'] == selected_measure]
    fig = px.bar(filtered_df.groupby('State')['Value'].sum().reset_index(), x='State', y='Value',
                 title=f'Total Crossings by State for {selected_measure}', template='plotly_white')
    return fig

# Expose the Flask server for Gunicorn
server = app.server

if __name__ == '__main__':
    app.run_server(debug=True)



# In[ ]:




