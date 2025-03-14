#!/usr/bin/env python
# coding: utf-8

# In[1]:


import pandas as pd
import seaborn as sns
import matplotlib.pyplot as plt
import numpy as np
import plotly.express as px
import warnings
import plotly.graph_objects as go
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
            style={'width': '50%', 'margin': 'auto'}
        )
    ], style={'textAlign': 'center', 'padding': '20px'}),
    
    html.Div([
        dcc.Graph(id='measure-bar-chart', style={'border': '1px solid #ddd', 'borderRadius': '10px', 'padding': '10px'}),
        dcc.Graph(id='time-series-plot', style={'border': '1px solid #ddd', 'borderRadius': '10px', 'padding': '10px'})
    ], style={'display': 'flex', 'flexWrap': 'wrap', 'justifyContent': 'space-around'}),
    
    html.Div([
        dcc.Graph(id='heatmap-correlation', style={'border': '1px solid #ddd', 'borderRadius': '10px', 'padding': '10px'}),
        dcc.Graph(id='geospatial-plot', style={'border': '1px solid #ddd', 'borderRadius': '10px', 'padding': '10px'})
    ], style={'display': 'flex', 'flexWrap': 'wrap', 'justifyContent': 'space-around', 'padding': '20px'})
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
    Output('time-series-plot', 'figure'),
    Input('measure-dropdown', 'value')
)
def update_time_series(selected_measure):
    filtered_df = df[df['Measure'] == selected_measure]
    fig = px.line(filtered_df, x='Date', y='Value', color='Border',
                  title=f'Time Series Analysis of {selected_measure}',
                  markers=True, template='plotly_white')
    return fig

@app.callback(
    Output('heatmap-correlation', 'figure'),
    Input('measure-dropdown', 'value')
)
def update_heatmap(selected_measure):
    fig = px.imshow(df.corr(numeric_only=True), color_continuous_scale='coolwarm', title='Correlation Matrix', template='plotly_white')
    return fig

@app.callback(
    Output('geospatial-plot', 'figure'),
    Input('measure-dropdown', 'value')
)
def update_geospatial(selected_measure):
    filtered_df = df[df['Measure'] == selected_measure]
    fig = px.scatter_mapbox(filtered_df, lat='Latitude', lon='Longitude', size='Value', color='Border',
                            hover_name='Port Name', zoom=3, mapbox_style="carto-positron",
                            title=f'Geospatial Analysis for {selected_measure}', template='plotly_white')
    return fig

# Expose the Flask server for Gunicorn
server = app.server

if __name__ == '__main__':
    app.run_server(debug=True)


# In[ ]:




