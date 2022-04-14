import seaborn as sns
import numpy as np
import pandas as pd

from sklearn.model_selection import train_test_split
from sklearn.preprocessing import OneHotEncoder
from sklearn.impute import SimpleImputer
from sklearn.compose import ColumnTransformer
from sklearn.pipeline import Pipeline
from sklearn.ensemble import RandomForestClassifier

import folium
from folium.plugins import HeatMap

import plotly.graph_objects as go
import plotly.express as px

import dash
from dash import html, dcc
import dash_daq as daq
from dash.dependencies import Input, Output, State

# ********************* DATA PREPARATION *********************
# Load data
data = pd.read_csv('hotel_bookings.csv')

# Format data for dashboard
data["children"] = data["children"].fillna(0) # null chilrdren replace with 0
data["country"] = data["country"].fillna("Undefined") #null counry replace with undefined
data["agent"] = data["agent"].fillna(0)   # null agent replace with 0
data["company"] = data["company"].fillna(0)  # null company replace with 0
filter = (data.children == 0) & (data.adults == 0) & (data.babies == 0)
data[filter]
data = data[~filter]


# Helper functions for dropdowns and slider
def create_slider_marks(values):
    marks = {i: {'label': str(i)} for i in values}
    return marks

# ********************* DASH APP *********************
app = dash.Dash(__name__)
app.layout = html.Div([
    html.Div([
        html.H1("Hotel Bookings"),
        html.P("In this project we intend to explore booking information for a city hotel and a resort hotel, comparing the differences between the choices made by guests with and without children along the years."),
        # html.Img(src=app.get_asset_url("left_pane.png")),
        html.Img(src="assets/icons/6.png"),
        
        html.Button(id='kids-button', children="Guests with Kids", n_clicks=0),
        
        html.Button(id='nokids-button', children="Guests without Kids", n_clicks=0),
        
        html.Button(id='all-button', children="All Guests", n_clicks=0),
        ], id='left-container'),
    
], id='container')

""" @app.callback(
    
) """
    
    # Visual 1: Barplot


    # Visual 2: Map
    

    # Visual 3: Pie charts


    # Visual 4: Scatterplot
    

    # return barplot, mapping, piechart, scatterplot

if __name__ == '__main__':
    app.run_server(debug=True)