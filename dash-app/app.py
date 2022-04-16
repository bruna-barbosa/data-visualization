from ctypes import alignment
from turtle import width
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
data = pd.read_csv("dash-app/data/hotel_bookings.csv")

# Format data for dashboard
data["children"] = data["children"].fillna(0) # null chilrdren replace with 0
data["country"] = data["country"].fillna("Undefined") # null country replace with undefined
data["agent"] = data["agent"].fillna(0)   # null agent replace with 0
data["company"] = data["company"].fillna(0)  # null company replace with 0
filter = (data.children == 0) & (data.adults == 0) & (data.babies == 0)
data = data[~filter]
data["is_canceled"] = data["is_canceled"].replace({1:"Yes", 0:"No"})
data["is_repeated_guest"] = data["is_repeated_guest"].replace({1:"Yes", 0:"No"})

filters = [(data['children']==0) & (data['babies']==0),
            (data['children']>0),
            (data['babies']>0)
            ]
categories = ["No Kids", "Children", "Babies"]
data["Kids"] = np.select(filters, categories)


# ********************* DASH APP *********************

# Helper functions for dropdowns and slider
def create_slider_marks(values):
    marks = {i: {'label': str(i)} for i in values}
    return marks

def sort_month(df, column_name):
    # Function for sorting months
    return sd.Sort_Dataframeby_Month(df, column_name)

app = dash.Dash(external_stylesheets=[dbc.themes.BOOTSTRAP])
    
sidebar = html.Div([
            html.H1("Hotel Bookings",style={'text-align': 'center'}),
            html.P("In this project we intend to explore booking information for a city hotel and a resort hotel, comparing the differences between the choices made by guests with and without children along the years."),
            html.Br(),
            html.Img(src="assets/icons/6.png",style={'width': '100%'})    
            ],className='left-container' , style={'height': '100%'}           
        )
            
content = \
html.Div(children=[
    
    #filter bar
    html.Div(children=[
        html.Div(children=[
                html.Label('Year'),
                dcc.RangeSlider(
                    id='rangeslider',
                    marks={i: str(i) for i in range(min(data.arrival_date_year.unique()), max(data.arrival_date_year.unique())+1)},
                    min=min(data.arrival_date_year.unique()),
                    max=max(data.arrival_date_year.unique()),
                    value=[min(data.arrival_date_year.unique()), max(data.arrival_date_year.unique())],
                    step=1)
        ],style={'width': '50%','float': 'left'}),

        html.Div(children=[
                html.Label('Type of Guest',className='other-labels',style={'margin':'auto','width':'100%'}),
                dcc.Checklist(
                id='checkbox',
                options=list(data.Kids.unique()),
                value=categories,
                className='other-labels')
        ],style={'width': '50%','float': 'left'}),
    
    ],
    className='container',
    style={'background-color':'#1D74C1','height': '100%'}
    ),


    #First row of graph
    html.Div(children=[
        html.Div(children=[
            dcc.Graph(id="barplot",style={'border':'solid white'})
        ],className='columns',style={'background-color':'#1D74C1','width': '35%'}),
        html.Div(children=[
            html.Img(src="assets/icons/4.png",style={'width': '100%','object-fit': 'fill'})
        ],className='columns',style={'width': '30%'}),
        html.Div(children=[
            dcc.Graph(id="map")
        ],className='columns',style={'background-color':'#1D74C1','width': '35%'})
    ],
    className='container'
    ),


    #Second row of graphs
    html.Div(children=[

        html.Div(children=[
            dcc.Graph(id="scatterplot1")
        ],className='two columns',style={'background-color':'#1D74C1','width': '49%'}),

        html.Div(children=[
            dcc.Graph(id="piecharts")
        ],className='two columns',style={'background-color':'#1D74C1','width': '49%'})
    ],
    className='container',
    style={ 'justify-content': 'space-between'}
    )

])

app.layout = html.Div([dcc.Location(id="url"), sidebar, content])

############################################First Bar Plot##########################################################
@app.callback(
    Output(component_id='barplot', component_property='figure'),
    [Input(component_id='checkbox', component_property='value')]
) 
def barplot(kids):
    #with kids hotel and year distribution
    guest_with_kids_hotel = data[data['Kids'].isin(kids)].groupby(['arrival_date_year' , 'hotel'], as_index=False).size()
    guest_with_kids_hotel.columns = ['arrival_date_year','hotel' , 'guest with kids']
    slider_guest_with_kids_hotel = guest_with_kids_hotel.pivot_table('guest with kids', ['hotel'], 'arrival_date_year')

    # An empty graph object
    fig_bar_kids = go.Figure(layout = dict(colorway = ['#E24E42','#E24E42']))

    # Each year defines a new hidden (implies visible=False) trace in our visualization
    for year in slider_guest_with_kids_hotel.columns:
        fig_bar_kids.add_trace(dict(type='bar',
                        x= slider_guest_with_kids_hotel.index,
                        y=slider_guest_with_kids_hotel[year],
                        name=year,
                        showlegend=False,
                        visible=False,
                        )
                )

    # First seen trace
    fig_bar_kids.data[0].visible = True

    # Lets create our slider, one option for each trace
    steps = []
    for i in range(len(fig_bar_kids.data)):
        step = dict(
            label='Year ' + str(2015 + i),
            method="restyle", #there are four methods restyle changes the type of an argument (in this case if visible or not)
            args=["visible", [False] * len(fig_bar_kids.data)], # Changes all to Not visible
        )
        step["args"][1][i] = True  # Toggle i'th trace to "visible"
        steps.append(step)

        
    sliders = [dict(
        active=2015,
        pad={"t": 100},
        steps=steps,
        font = dict(color = 'white')
    )]

    fig_bar_kids.update_layout(
        dict(
            title=dict(
                text='Hotel reservations from guests with kids between 2015 and 2017', 
                font = dict(color = 'white')
            ),
            yaxis=dict(
                title='Number of guests',
                range=[0,5*(10**3)], 
                showgrid = False, 
                color = 'white' 
            ),
            plot_bgcolor = '#1D74C1',
            paper_bgcolor = '#1D74C1',
            xaxis=dict(color="white")
        )
    )

    return fig_bar_kids

#############################################Second Choropleth######################################################
@app.callback(
    Output(component_id='map', component_property='figure'),
    [Input(component_id='checkbox', component_property='value')]
)
def map(kids):

    country_wise_guests = data[data['is_canceled'] == 'No'].groupby(['country', 'hotel'], as_index=False).size()
    country_wise_guests.columns = ['country', 'No of guests' ,'hotel']
    
    basemap = folium.Map()
    guests_map = px.choropleth(country_wise_guests, locations = country_wise_guests['country'],
                           color = country_wise_guests['No of guests'], hover_name = country_wise_guests['country'], 
                           color_continuous_scale="sunset")
    return guests_map 

############################################Third Scatter Plot######################################################
@app.callback(
    Output(component_id='piecharts', component_property='figure'),
    [Input(component_id='checkbox', component_property='value')]
) 
def pie_chart(kids):
    children_market_segment = data[data['Kids'].isin(kids)].groupby(['market_segment', 'hotel'], as_index=False).size()
    children_market_segment.columns= ['market_segment' ,'hotel', 'number_of_guest']

    filtered_by_hotel_df = children_market_segment#.loc[children_market_segment['hotel'] == input]


    labels_market_nokids = filtered_by_hotel_df['market_segment']


    values_market_nokids = filtered_by_hotel_df['number_of_guest']

    data_market_nokids = dict(type='pie', labels=labels_market_nokids, values=values_market_nokids)
    layout_market_nokids = dict(title=dict(text='market segment with out kids'))

    return  go.Figure(data=[data_market_nokids], layout=layout_market_nokids)

############################################Forth Scatter Plot######################################################
@app.callback(
    Output(component_id='scatterplot1', component_property='figure'),
     [Input(component_id='checkbox', component_property='value')])
def scatterplot(kids):
    # Function for creating a Scatterplot
    
    # Guests without children
    no_children_month = data[data['Kids'].isin(kids)].groupby(['arrival_date_month'], as_index=False).size()
    no_children_month.rename(columns={"arrival_date_month": "month", "size": "number_of_guest"}, inplace=True)
    no_children_month=sort_month(no_children_month, 'month')
    

    # Guests with children
    children_month = data[(data['children'] != 0) | (data['babies'] != 0)].groupby(['arrival_date_month'], as_index=False).size()
    children_month.rename(columns={"arrival_date_month": "month", "size": "number_of_guest"}, inplace=True)
    children_month=sort_month(children_month, 'month')
    

    children_month_trace1 = dict(type='scatter',
                  x=children_month['month'],
                  y=children_month['number_of_guest'],
                  name='Guests with kids',
                  line=dict(color='#E0FFF8')
                  )

    no_children_month_trace2 = dict(type='scatter',
                  x=no_children_month['month'],
                  y=no_children_month['number_of_guest'],
                  name='Guests without kids',
                  line=dict(color='#E9B000')
                  )

    month_data = [children_month_trace1, no_children_month_trace2]


    month_layout = dict(title=dict(text='Favourite month of the year to travel with kids and without kids', font = dict(color = 'white')),
                  xaxis=dict(title='Months',showgrid = False, color = 'white'),
                  yaxis=dict(title='Number of guests',showgrid = False, color = 'white'),
                  plot_bgcolor = '#1D74C1',
                  paper_bgcolor = '#1D74C1',
                  )

    return go.Figure(data=month_data, layout=month_layout)  

if __name__ == '__main__':
    app.run_server(debug=True)