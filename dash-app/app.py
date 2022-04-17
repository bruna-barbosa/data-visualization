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
from dash.exceptions import PreventUpdate

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
            html.H1("Hotel Bookings",style={'text-align': 'left'}),
            html.P("In this project we intend to explore booking information for a city hotel and a resort hotel, comparing the differences between the choices made by guests with and without children along the years."),
            html.Br(),
            html.Img(src="assets/icons/6.png",style={'width': '100%'})    
            ],className='left-container'        
        )
            
content = \
html.Div(children=[
    
    # Filter bar
    html.Div(children=[
            html.Div(children=[
                    html.Label('Year',className='other-labels',style={'width':'100%'}),
                    dcc.RangeSlider(
                        id='rangeslider',
                        marks={h : {'label' : str(h), 'style':{'color':'white'}} for h in range(min(data.arrival_date_year.unique()), max(data.arrival_date_year.unique())+1)},
                        min=min(data.arrival_date_year.unique()),
                        max=max(data.arrival_date_year.unique()),
                        value=[min(data.arrival_date_year.unique()), max(data.arrival_date_year.unique())],
                        step=1)
            ]
            ,style={'width': '49%','float': 'left'}
            ),

            html.Div(children=[
                    html.Label('Type of Guests',className='other-labels',style={'width':'100%'}),
                    dcc.Dropdown(
                    id='dynamic-dropdown',
                    options=list(data.Kids.unique()),
                    value=categories,
                    className='dropdown',
                    multi=True)
            ]
            ,style={'width': '49%','float': 'left'}
            ),
        
        ],
        className='top-container'
        ,style={'background-color':'#1D74C1'}
        ),

    # First row of Graphs
    html.Div(children=[
        html.Div(children=[
            dcc.Graph(id="map")
        ]
        #,className='columns'
        ,style={'background-color':'#1D74C1'})
    ]
    ,className='top-container'
    #,style={'border':'solid red'}
    ),


    # Second row of Graphs
    html.Div(children=[

        html.Div(children=[
            dcc.Graph(id="scatterplot",style={'box-sizing': 'border-box'})
        ]
        ,className='columns'
        ,style={'background-color':'#1D74C1','width': '80%'}),
      
        html.Div(children=[
            html.Img(src="assets/icons/4.png",style={'width': '100%'})
        ]
        ,className='columns'
        ,style={'width': '20%', 'height': '100%'})
    ],
    className='top-container'
    ),

    # Third row of Graphs
    html.Div(children=[

        html.Div(children=[
            dcc.Graph(id="barplot")
        ]
        ,className='columns'
        ,style={'background-color':'#1D74C1','width': '49%'}),

        html.Div(children=[
            dcc.Graph(id="piecharts")
        ]
        ,className='columns'
        ,style={'background-color':'#1D74C1','width': '50%','float':'right'})
    ],
    className='top-container'
    ),

    # Authors
    html.Div(children=[
            html.Div(children=[
                  html.P("NOVA IMS 2021/2022, Data Visualization Group 22: Bruna Duarte, Francisco Ornelas, Isha Pandya, and Lucas Corrêa")  
            ]
            ,style={'width': '100%','float': 'left'}       
            ),
        
        ],
        className='bottom-container'
        ,style={'background-color':'#E9B000'}
        )

],style={'margin-bottom': '2%','height':'96%','margin-top': '2%','width': '100%'})

app.layout = html.Div([dcc.Location(id="url"), sidebar, content])

############################################Dynamic Dropdown##########################################################
@app.callback(
    Output("dynamic-dropdown", "options"),
    Input("dynamic-dropdown", "search_value")
)

def update_options(search_value):
    options=list(data.Kids.unique())

    if not search_value:
        raise PreventUpdate
    return [o for o in options if search_value in o["label"]]
    

############################################First Bar Plot##########################################################
@app.callback(
    Output(component_id='barplot', component_property='figure'),
    [Input(component_id='dynamic-dropdown', component_property='value'),
    Input(component_id='rangeslider', component_property='value')]
) 
def barplot(kids,year):
    #applying filters
    filters = (data['Kids'].isin(kids)) & \
              (data['arrival_date_year'].between(year[0],year[1])
              )
    guest_with_kids_hotel = data[filters].groupby(['hotel' , 'Kids'], as_index=False).size()
    guest_with_kids_hotel.columns = ['hotel' , 'Kids','no of guest']
        
    data_bar = []
    for kid in kids:
        df_bar = guest_with_kids_hotel.loc[(guest_with_kids_hotel['Kids'] == kid)]

        x_bar = df_bar['hotel']
        y_bar = df_bar['no of guest']

        data_bar.append(dict(type='bar', x=x_bar, y=y_bar, name=kid))

    resort_layout =dict(title=dict(text='Hotel reservations with diffrent categories', font = dict(color = 'white')),
                    yaxis=dict(title='Number of guests log',type='log',
                                showgrid = False, color = 'white'
                                ), 
                                xaxis=dict(title = 'Hotel type' , color="white"),plot_bgcolor = '#1D74C1',
                                    paper_bgcolor = '#1D74C1',colorway = ['#E24E42','#E9B000','#E0FFF8'])

    
    return go.Figure(data=data_bar, layout=resort_layout)

#############################################Second Choropleth######################################################
@app.callback(
    Output(component_id='map', component_property='figure'),
    [Input(component_id='dynamic-dropdown', component_property='value'),
     Input(component_id='rangeslider', component_property='value')]
)
def map(kids,year):

    filters = (data['Kids'].isin(kids)) & \
              (data['arrival_date_year'].between(year[0],year[1]) & \
              (data['is_canceled'] == 'No')
              )

    country_wise_guests = data[filters].groupby(['country'], as_index=False).size()
    country_wise_guests.columns = ['country', 'No of guests' ]
    
    guests_map = px.choropleth(country_wise_guests, 
                               locations = country_wise_guests['country'],
                               color = country_wise_guests['No of guests'], 
                               hover_name = country_wise_guests['country'], 
                               color_continuous_scale="sunset")
    guests_map.update_layout(margin=dict(l=40, r=40, t=40, b=40),
                            paper_bgcolor='#1D74C1')

    return guests_map 

############################################Third Scatter Plot######################################################
@app.callback(
    Output(component_id='piecharts', component_property='figure'),
    [Input(component_id='dynamic-dropdown', component_property='value'),
    Input(component_id='rangeslider', component_property='value')]
) 
def pie_chart(kids,year):

    filters = (data['Kids'].isin(kids)) & \
            (data['arrival_date_year'].between(year[0],year[1])
            )

    children_market_segment = data[filters].groupby(['market_segment', 'hotel'], as_index=False).size()
    children_market_segment.columns= ['market_segment' ,'hotel', 'number_of_guest']

    colors= ['#E24E42',
            '#E9B000',
            '#EB6E80',
            '#008F95',
            '#E0FFF8',
            '#1D74C1']

    data_market_nokids   = dict(type='pie',
                                labels=children_market_segment.market_segment,
                                values=children_market_segment.number_of_guest)
    layout_market_nokids = dict(title=dict(text='Market Segment', font = dict(color = 'white')),
                                paper_bgcolor = '#1D74C1',
                                colorway=colors,
                                font=dict(family="sVerdana, Geneva, Tahoma, sans-serif",size=18,color="white")
                            )


    return  go.Figure(data=[data_market_nokids], layout=layout_market_nokids)

############################################Forth Scatter Plot######################################################
@app.callback(
    Output(component_id='scatterplot', component_property='figure'),
     [Input(component_id='dynamic-dropdown', component_property='value'),
     Input(component_id='rangeslider', component_property='value')])
def scatterplot(kids,year):

    filters = (data['Kids'].isin(kids)) & \
            (data['arrival_date_year'].between(year[0],year[1])
            )

    no_children_month = data[filters].groupby(['Kids','arrival_date_month']).size()
    no_children_month = pd.DataFrame(no_children_month.groupby(level=0).apply(lambda x: x / float(x.sum()))).reset_index()

    no_children_month.columns=('kids category','Month'  , '% of guest')
    no_children_month=sort_month(no_children_month, 'Month')
    
    data_agg = []

    for kid in kids:
        data_scatter = no_children_month.loc[(no_children_month['kids category'] == kid)]
        data_agg.append(dict(type='scatter',
                                x=data_scatter['Month'],
                                y=data_scatter['% of guest'],
                                name=kid, 
                                #color = 'white'
                                #line=dict(color='#E9B000'),
                                #mode='markers'
                                )
                            )
                        


    month_layout = dict(title=dict(text='When people go on Vacation<br><sup>Percentage of Guests in each Month</sup>', font = dict(color = 'white')),
                    xaxis=dict(title='Months',showgrid = False, color = 'white'),
                    yaxis=dict(title='% of Guests',showgrid = True, 
                                color = 'white',
                                gridcolor='#9CAEA9',
                                layer="below traces",
                                tickformat=".0%"),
                    plot_bgcolor = '#1D74C1',
                    paper_bgcolor = '#1D74C1',colorway = ['#E24E42','#E9B000','#E0FFF8']
                    )


    return go.Figure(data=data_agg, layout=month_layout)

if __name__ == '__main__':
    app.run_server(debug=True)