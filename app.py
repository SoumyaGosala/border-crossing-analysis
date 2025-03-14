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

# Checking for missing values
missing_values = df.isnull().sum()
print("Missing values in each column:\n", missing_values)

# Summary statistics
print(df.describe())

# Filter only numeric columns for correlation analysis
numeric_df = df.select_dtypes(include=[np.number])

# Initialize Dash App with external stylesheet for better UI
theme = "https://codepen.io/chriddyp/pen/bWLwgP.css"
app = dash.Dash(__name__, external_stylesheets=[theme])

app.layout = html.Div([
    html.H1("Border Crossing Analysis", style={'textAlign': 'center', 'color': '#007BFF'}),
    html.P("Explore border crossing trends with interactive visualizations.",
           style={'textAlign': 'center', 'fontSize': '16px', 'color': '#555'}),
    
    html.Div([
        html.Label("Select a Measure:", style={'fontSize': '18px', 'fontWeight': 'bold'}),
        dcc.Dropdown(
            id='measure-dropdown',
            options=[{'label': m, 'value': m} for m in df['Measure'].unique()],
            value=df['Measure'].unique()[0],
            style={'width': '40%', 'margin': 'auto', 'display': 'inline-block'}
        ),
        html.Label("Select Date Range:", style={'fontSize': '18px', 'fontWeight': 'bold', 'marginLeft': '20px'}),
        dcc.DatePickerRange(
            id='date-picker',
            start_date=df['Date'].min(),
            end_date=df['Date'].max(),
            display_format='YYYY-MM-DD',
            style={'display': 'inline-block', 'marginLeft': '10px'}
        )
    ], style={'textAlign': 'center', 'padding': '20px'}),
    
    html.Div([
        dcc.Graph(id='measure-bar-chart', style={'border': '1px solid #ddd', 'borderRadius': '10px', 'padding': '10px'}),
        dcc.Graph(id='time-series-plot', style={'border': '1px solid #ddd', 'borderRadius': '10px', 'padding': '10px'}),
        dcc.Graph(id='interactive-pie-chart', style={'border': '1px solid #ddd', 'borderRadius': '10px', 'padding': '10px'}),
        dcc.Graph(id='static-heatmap', style={'border': '1px solid #ddd', 'borderRadius': '10px', 'padding': '10px'})
    ], style={'display': 'grid', 'gridTemplateColumns': 'repeat(2, 1fr)', 'gap': '20px', 'padding': '20px'})
])

@app.callback(
    Output('measure-bar-chart', 'figure'),
    [Input('measure-dropdown', 'value'), Input('date-picker', 'start_date'), Input('date-picker', 'end_date')]
)
def update_bar_chart(selected_measure, start_date, end_date):
    filtered_df = df[(df['Measure'] == selected_measure) & (df['Date'] >= start_date) & (df['Date'] <= end_date)]
    fig = px.bar(filtered_df.groupby('State')['Value'].sum().reset_index(), x='Value', y='State',
                 title=f'Total Border Crossings for {selected_measure}', orientation='h',
                 color='State', color_continuous_scale='viridis', template='plotly_white')
    return fig

@app.callback(
    Output('time-series-plot', 'figure'),
    [Input('measure-dropdown', 'value'), Input('date-picker', 'start_date'), Input('date-picker', 'end_date')]
)
def update_time_series(selected_measure, start_date, end_date):
    filtered_df = df[(df['Measure'] == selected_measure) & (df['Date'] >= start_date) & (df['Date'] <= end_date)]
    fig = px.line(filtered_df, x='Date', y='Value', color='Border',
                  title=f'Time Series Analysis of {selected_measure}',
                  markers=True, template='plotly_white')
    return fig

@app.callback(
    Output('interactive-pie-chart', 'figure'),
    Input('measure-dropdown', 'value')
)
def update_pie_chart(selected_measure):
    filtered_df = df[df['Measure'] == selected_measure]
    fig = px.pie(filtered_df, names='State', values='Value',
                 title=f'Border Crossings by State for {selected_measure}', hole=0.3, template='plotly_white')
    return fig

# Static Heatmap
fig_heatmap = px.imshow(numeric_df.corr(), color_continuous_scale='viridis', title='Correlation Matrix', template='plotly_white')

@app.callback(
    Output('static-heatmap', 'figure'),
    Input('measure-dropdown', 'value')
)
def update_static_heatmap(selected_measure):
    return fig_heatmap

# Expose the Flask server for Gunicorn
server = app.server

if __name__ == '__main__':
    app.run_server(debug=True)




# In[ ]:




