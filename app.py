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
        dcc.Graph(id='entries-by-border', style={'border': '1px solid #ddd', 'borderRadius': '10px', 'padding': '10px'}),
        dcc.Graph(id='top-ports', style={'border': '1px solid #ddd', 'borderRadius': '10px', 'padding': '10px'}),
        dcc.Graph(id='monthly-trends', style={'border': '1px solid #ddd', 'borderRadius': '10px', 'padding': '10px'})
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
    Output('entries-by-border', 'figure'),
    Input('measure-dropdown', 'value')
)
def update_entries_by_border(selected_measure):
    fig = px.bar(df.groupby('Border')['Value'].sum().reset_index(), x='Border', y='Value',
                 title='Entries by Border Type', color='Border', template='plotly_white')
    return fig

@app.callback(
    Output('top-ports', 'figure'),
    Input('measure-dropdown', 'value')
)
def update_top_ports(selected_measure):
    top_ports_df = df.groupby('Port Name')['Value'].sum().nlargest(5).reset_index()
    fig = px.bar(top_ports_df, x='Value', y='Port Name',
                 title='Top 5 Border Crossing Ports', orientation='h', template='plotly_white')
    return fig

@app.callback(
    Output('monthly-trends', 'figure'),
    Input('measure-dropdown', 'value')
)
def update_monthly_trends(selected_measure):
    df['Month'] = df['Date'].dt.month_name()
    df_monthly = df.groupby('Month')['Value'].sum().reset_index()
    fig = px.bar(df_monthly, x='Month', y='Value',
                 title='Monthly Trends in Border Crossings', template='plotly_white')
    return fig

# Expose the Flask server for Gunicorn
server = app.server

if __name__ == '__main__':
    app.run_server(debug=True)


# In[ ]:




