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

# Interactive Dash Application
app = dash.Dash(__name__)
app.layout = html.Div([
    html.H1("Border Crossing Analysis"),
    html.Label("Select a Measure:"),
    dcc.Dropdown(
        id='measure-dropdown',
        options=[{'label': m, 'value': m} for m in df['Measure'].unique()],
        value=df['Measure'].unique()[0]
    ),
    dcc.Graph(id='measure-bar-chart'),
    dcc.Graph(id='time-series-plot'),
    dcc.Graph(id='heatmap-correlation'),
    dcc.Graph(id='geospatial-plot')
])

@app.callback(
    Output('measure-bar-chart', 'figure'),
    Input('measure-dropdown', 'value')
)
def update_bar_chart(selected_measure):
    filtered_df = df[df['Measure'] == selected_measure]
    fig = px.bar(filtered_df.groupby('State')['Value'].sum().reset_index(), x='Value', y='State',
                 title=f'Total Border Crossings for {selected_measure}', orientation='h',
                 color='State', color_continuous_scale='viridis')
    return fig

@app.callback(
    Output('time-series-plot', 'figure'),
    Input('measure-dropdown', 'value')
)
def update_time_series(selected_measure):
    filtered_df = df[df['Measure'] == selected_measure]
    fig = px.line(filtered_df, x='Date', y='Value', color='Border',
                  title=f'Time Series Analysis of {selected_measure}',
                  markers=True)
    return fig

@app.callback(
    Output('heatmap-correlation', 'figure'),
    Input('measure-dropdown', 'value')
)
def update_heatmap(selected_measure):
    fig = px.imshow(df.corr(numeric_only=True), color_continuous_scale='coolwarm', title='Correlation Matrix')
    return fig

@app.callback(
    Output('geospatial-plot', 'figure'),
    Input('measure-dropdown', 'value')
)
def update_geospatial(selected_measure):
    filtered_df = df[df['Measure'] == selected_measure]
    fig = px.scatter_mapbox(filtered_df, lat='Latitude', lon='Longitude', size='Value', color='Border',
                            hover_name='Port Name', zoom=3, mapbox_style="carto-positron",
                            title=f'Geospatial Analysis for {selected_measure}')
    return fig

# Expose the Flask server for Gunicorn
server = app.server

if __name__ != "__main__":
    gunicorn_app = server

if __name__ == '__main__':
    app.run_server(debug=True)


# In[ ]:




