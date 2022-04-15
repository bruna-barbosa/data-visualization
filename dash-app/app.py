from matplotlib.pyplot import sca
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
import dash_bootstrap_components as dbc
import dash_daq as daq
from dash.dependencies import Input, Output, State

import sort_dataframeby_monthorweek as sd

# ********************* DATA PREPARATION *********************
# Load data
<<<<<<< HEAD
data = pd.read_csv("dash-app/data/hotel_bookings.csv")
=======
data = pd.read_csv("data/hotel_bookings.csv")
>>>>>>> 59abe310e4cbe38bd90ff3bb43ace42312364f97

# Format data for dashboard
data["children"] = data["children"].fillna(0) # null chilrdren replace with 0
data["country"] = data["country"].fillna("Undefined") # null country replace with undefined
data["agent"] = data["agent"].fillna(0)   # null agent replace with 0
data["company"] = data["company"].fillna(0)  # null company replace with 0
filter = (data.children == 0) & (data.adults == 0) & (data.babies == 0)
data = data[~filter]
data["is_canceled"] = data["is_canceled"].replace({1:"Yes", 0:"No"})
data["is_repeated_guest"] = data["is_repeated_guest"].replace({1:"Yes", 0:"No"})


# ********************* DASH APP *********************
app = dash.Dash(external_stylesheets=[dbc.themes.BOOTSTRAP])

# Helper functions for dropdowns and slider
def create_slider_marks(values):
    marks = {i: {'label': str(i)} for i in values}
    return marks

def sort_month(df, column_name):
    # Function for sorting months
    return sd.Sort_Dataframeby_Month(df, column_name)
<<<<<<< HEAD
    
sidebar = html.Div([
            html.H1("Hotel Bookings"),
            html.P("In this project we intend to explore booking information for a city hotel and a resort hotel, comparing the differences between the choices made by guests with and without children along the years."),
            # html.Img(src=app.get_asset_url("left_pane.png")),
            html.Img(src="assets/icons/6.png")    
            ],
            id='left-container'
            )

content = html.Div([
   
    dbc.Container(
=======


# ********************* DASH APP *********************
app = dash.Dash(external_stylesheets=[dbc.themes.BOOTSTRAP])

# the styles for the main content position it to the right of the sidebar and
# add some padding
CONTENT_STYLE = {
    "margin-left": "18rem",
    "margin-right": "2rem",
    "padding": "2rem 1rem",
}

sidebar = dbc.Container(
    [
        html.Div([
            html.H1("Hotel Bookings"),
            html.P("In this project we intend to explore booking information for a city hotel and a resort hotel, comparing the differences between the choices made by guests with and without children along the years."),
            # html.Img(src=app.get_asset_url("left_pane.png")),
            html.Img(src="assets/icons/6.png"),
            
            html.Button(id='kids-button', children="Guests with Kids", n_clicks=0),
            
            html.Button(id='nokids-button', children="Guests without Kids", n_clicks=0),
            
            html.Button(id='all-button', children="All Guests", n_clicks=0),
        ], 
        
        id='left-container'),

        dbc.Row(
            [
                dbc.Col(dcc.Graph(id="barplot"), md=4),
                dbc.Col(dcc.Graph(id="map"), md=8),                
            ],
            align="center",
        ),

        dbc.Row(
            [
                dbc.Col(dcc.Graph(id="piecharts"), md=4),
                dbc.Col(dcc.Graph(id="scatterplot"), md=8),                
            ],
            align="center",
        ),
    ],
    fluid=True, style=CONTENT_STYLE
)

"""     html.Div([
        html.Div(className='row', children=[
            
            html.Div(className='parent', children=[
                dcc.Graph(id="barplot", className='plot'),
                html.Div(className='spacer'),
                dcc.Graph(id="map", className='plot'),
                html.Div(className='spacer'),

        html.Div(className='row', children=[            
            html.Div(className='parent', children=[
                dcc.Graph(id="piecharts", className='plot'),
                html.Div(className='spacer'),
                dcc.Graph(id="scatterplot", className='plot'),                
            ])
            ])
            ])
        ], id='visualisation'),   

    ], id='right-container') """

""" content = dbc.Container(
>>>>>>> 59abe310e4cbe38bd90ff3bb43ace42312364f97
    [
        dbc.Row(
            [
                dbc.Col( daq.BooleanSwitch(
                            id='kids_toggle',
                            className='toggle',                
                            label="With kids",
                            labelPosition="top",
                            on=False,
                            color="#E9B000"
                        ),),
                dbc.Col(daq.BooleanSwitch(
                            id='nokids_toggle',
                            label="Without kids",
                            labelPosition="top",
                            on=True,
                            color="#E9B000"                        
                        ),),
                dbc.Col( html.Button(id='all-button', children="All Guests", n_clicks=0)),
            ],
            style={'padding':'.3rem', 'marginLeft':'1rem', 'boxShadow': '#e3e3e3 4px 4px 2px', 'border-radius': '10px', 'backgroundColor': 'white' },
            align="center",
        ),

        dbc.Row(
            [
                dbc.Col(
                    dcc.Graph(id="barplot"),
                    style={'padding':'.3rem', 'marginLeft':'1rem', 'boxShadow': '#e3e3e3 4px 4px 2px', 'border-radius': '10px', 'backgroundColor': '#1D74C1' }
                ),
                dbc.Col(html.Img(src="assets/icons/4.png")),
                dbc.Col(dcc.Graph(id="map")),                
            ],
            #style={'padding':'.3rem', 'marginLeft':'1rem', 'boxShadow': '#e3e3e3 4px 4px 2px', 'border-radius': '10px', 'backgroundColor': 'white' },
            align="center",
        ),
<<<<<<< HEAD
=======
    ],
    fluid=True, style=CONTENT_STYLE
) """

app.layout = html.Div([dcc.Location(id="url"), sidebar])

""" @app.callback(
    [Output(component_id='barplot', component_property='figure'),
     Output(component_id='map', component_property='figure'),
     Output(component_id='piecharts', component_property='figure'),
     Output(component_id='scatterplot', component_property='figure')],
    
)  """ 
>>>>>>> 59abe310e4cbe38bd90ff3bb43ace42312364f97

        # dbc.Row(
        #     [
        #         dbc.Col(dcc.Graph(id="piecharts")),
        #         dbc.Col(dcc.Graph(id="scatterplot1")),                
        #     ],
        #     align="center",
        # ),
    ],
    #id='right-container',
    fluid=True)
    ])

# Visual 1: Barplot

# Visual 2: Map
def map():
    # Function for creating a Choropleth
    country_wise_guests = data[data['is_canceled'] == 'No']['country'].value_counts().reset_index()
    country_wise_guests.columns = ['country', 'number_guests']
    
    basemap = folium.Map()
    guests_map = px.choropleth(country_wise_guests, locations = country_wise_guests['country'],
                           color = country_wise_guests['number_guests'], hover_name = country_wise_guests['country'])
    return map 

# Visual 3: Pie charts

@app.callback(
    Output(component_id='scatterplot1', component_property='figure'),
    [Input(component_id='kids_toggle', component_property='on'),
     Input(component_id='nokids_toggle', component_property='on')]
) 
# Visual 4: Scatterplot
def scatterplot(kids,no_kids):
    # Function for creating a Scatterplot
    
    # Guests without children
    no_children_month = data[(data['children'] == 0) & (data['babies'] == 0)].groupby(['arrival_date_month'], as_index=False).size()
    no_children_month.rename(columns={"arrival_date_month": "month", "size": "number_of_guest"}, inplace=True)
    no_children_month=sort_month(no_children_month, 'month')
    

    # Guests with children
    children_month = data[(data['children'] != 0) | (data['babies'] != 0)].groupby(['arrival_date_month'], as_index=False).size()
    children_month.rename(columns={"arrival_date_month": "month", "size": "number_of_guest"}, inplace=True)
    children_month=sort_month(children_month, 'month')
    

    children_month_trace1 = dict(type='scatter',
                  x=children_month['month'],
                  y=children_month['number_of_guest'],
                  name='Guests with kids'
                  )

    no_children_month_trace2 = dict(type='scatter',
                  x=no_children_month['month'],
                  y=no_children_month['number_of_guest'],
                  name='Guests with no kids'
                  )

    month_data = [children_month_trace1, no_children_month_trace2]

    month_layout = dict(title=dict(text='Favourite month of the year to travel with kids and without kids'),
                  xaxis=dict(title='Months'),
                  yaxis=dict(title='Number of guests')
                  )

    return go.Figure(data=month_data, layout=month_layout)  


app.layout = html.Div([dcc.Location(id="url"), sidebar, content])

if __name__ == '__main__':
    app.run_server(debug=True)