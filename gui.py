#!/usr/bin/env python3
import plotly.express as px
import plotly.graph_objects as go
from dash_extensions.enrich import MultiplexerTransform, DashProxy
from dash import html, dcc, Input, Output
import dash_bootstrap_components as dbc
import numpy as np
import pandas as pd
import json
import sys

## GET DATA

sys.path.append('Covid_Cases_Predictor-main/')
from script_model2 import *
data_raw = get_predicted(30)
other_data_raw = get_other_predicted()
# other_data_raw["York"]["Cases"] = lista 30 
all_data_raw = get_all_data()
sys.path.append('../')

idmap = {}
data = {}
all_data = {}
other_data = { 'Cases': {}, 'Deaths': {}, 'Tests': {} }
with open('uk-counties-2.json') as file:
    counties = json.load(file)
for f in counties['features']:
    cnam = f['properties']['name']
    idmap[f['properties']['id']] = cnam
    data[cnam] = data_raw[cnam]
    other_data['Cases'][cnam] = other_data_raw[cnam]['Cases']
    other_data['Deaths'][cnam] = other_data_raw[cnam]['Deaths']
    other_data['Tests'][cnam] = other_data_raw[cnam]['Tests']
num_dataset = len(list(idmap.keys()))
idmap = [idmap[i] for i in range(num_dataset)]
for (cn, dn) in all_data_raw:
    all_data[cn] = dn


## GENERATE MAP FIGURE

num_steps = 15
step_time = 2
risk_range = 0.2
selections = set()
last_clicked = -1

def get_map_figure():

    df = pd.DataFrame({ 'cid': [], 'days': [], 'risk': [] })
    for i in range(num_dataset):
        for t in range(num_steps):
            df.loc[len(df.index)] = [int(i), f"Day {t*step_time}", data[idmap[i]][t*step_time]]
    df = df.astype({ 'cid': 'int32' })
    
    ar = []
    for i in idmap:
        ar += ([i]*num_steps)

    fig = px.choropleth_mapbox(
        df, 
        locations='cid', 
        color='risk',
        animation_frame='days',
        geojson=counties, 
        featureidkey="properties.id",
        color_continuous_scale="Viridis",
        range_color=(0, risk_range),
        hover_name=ar,
        center={ 'lon': -2, 'lat': 54 },
        mapbox_style="carto-positron",
        zoom=4.5,
        opacity=0.5,
        labels={'risk':'True positive rate', 'cid': 'Region ID', 'days': 'Day'}
    )

    fig.update_layout({ 'margin':{"r":0,"t":0,"l":0,"b":0}, 'height':600, 'uirevision': 'constant' })
    return fig

# GENERATE GRAPH FIGURE

def get_graph_figure(selections):
    df = pd.DataFrame({ 'cid': [], 'days': [], 'risk': [] })
    for t in range(num_steps*step_time-1, 0, -1):
        for i in selections:
            df.loc[len(df.index)] = [i, -t, all_data[idmap[i]].iloc[-t]['True_Positive']]
    for t in range(num_steps*step_time):
        for i in selections:
            df.loc[len(df.index)] = [i, t, data[idmap[i]][t]]
    df = df.astype({ 'cid': 'int32', 'days': 'int32' })
    
    fig = go.Figure()
    for i in selections:
        dfi = df.loc[df['cid'] == i]
        fig.add_trace(go.Scatter(x=list(dfi['days']), y=list(dfi['risk']), name=idmap[i]))

    fig.update_layout(
        xaxis_title="Days",
        yaxis_title="True positive rate",
        legend_title="Region",
    )
    fig.update_xaxes(range=(-num_steps*step_time, num_steps*step_time))
    fig.update_yaxes(range=(0, risk_range))
    return fig
    
def get_table_old_figure(selected):
    if selected == -1:
        fig = go.Figure(
            data=[go.Table(
            header=dict(values=['Date', 'Cases', 'Deaths', 'Tests', 'True Positivie Rate'], align='left'),
            cells=dict(values=[[], [], [], []], align='right'))
        ])
        fig.update_layout({ 'margin':{"r":10,"t":0,"l":10,"b":0} })
        return fig
    df = all_data[idmap[selected]]
    lastcol = np.around(np.array(df['True_Positive']), 4)
    fig = go.Figure(
        data=[go.Table(
            header=dict(values=['Date', 'Cases', 'Deaths', 'Tests', 'True Positivie Rate'], align='left'),
            cells=dict(values=[df['Date'], df['Cases'], df['Deaths'], df['Tests'], lastcol], align='right'))
    ])
    fig.update_layout({ 'margin':{"r":10,"t":0,"l":10,"b":0} })
    return fig

def get_table_new_figure(selected):
    if selected == -1:
        fig = go.Figure(
            data=[go.Table(
                header=dict(values=['Days', 'Cases', 'Deaths', 'Tests', 'True Positive Rate'], align='left'),
            cells=dict(values=[[], []], align='right'))
        ])
        fig.update_layout({ 'margin':{"r":10,"t":0,"l":10,"b":0} })
        return fig
    
    row = np.around(np.array(data[idmap[selected]]), 4)
    fig = go.Figure(
        data=[go.Table(
            header=dict(values=['Days', 'Cases', 'Deaths', 'Tests', 'True Positive Rate'], align='left'),
            cells=dict(values=[list(range(0, 30)), other_data['Cases'][idmap[selected]], other_data['Deaths'][idmap[selected]], other_data['Tests'][idmap[selected]], row], align='right'))
    ])
    fig.update_layout({ 'margin':{"r":10,"t":0,"l":10,"b":0} })
    return fig


## CREATE APP

app = DashProxy(__name__, external_stylesheets=[dbc.themes.BOOTSTRAP], prevent_initial_callbacks=True, transforms=[MultiplexerTransform()], )

navbar = dbc.Navbar(
    dbc.Container([
        html.A(
            dbc.Row(
                [
                    dbc.Col(html.Img(src='', height="30px")),
                    dbc.Col(dbc.NavbarBrand("Predictor", className="ms-2")),
                ],
                align="center",
                className="g-0",
            ),
            href="/",
            style={"textDecoration": "none"},
        )
    ]),
    color="dark",
    dark=True,
)

def align_two(el_a, el_b):
    return dbc.Container([
        dbc.Row(
            [
                dbc.Col(el_a,
                    xxl=6, xl=6,  lg=12,
                    md=12, sm=12, xs=12,
                ),
                dbc.Col(
                    el_b,
                    xxl=6, xl=5, lg=12,
                    md=12, sm=12, xs=12,
                ),
            ],
            align="center",
            className="g-0"
        )
        ],
        style={ 'margin-top': '20px', "margin-bottom": '20px' }
    )

app.layout = html.Div(children=[
    navbar,
    dbc.Container(dcc.Markdown(children='''
        # Introduction
        This dashboard aims to forecast epidemic risk rates for UK. The risk rate is measured as the fraction of the positive tests out of the total tests taken in a day.
    ''', style={'margin-top': 20, 'margin-bottom': 20})),
    align_two([
        dcc.Graph(
            id='map-figure',
            figure=get_map_figure()
        )
    ], [
        dcc.Markdown(children='''
            # Plots
            Click a county to plot the number of cases in the next 30 days.
        '''),
        dbc.Button(children='Clear', id='clear-btn', n_clicks=0),
        dcc.Graph(
            id='graph-figure',
            figure=get_graph_figure(set())
        )   
    ]),
    align_two([
        dcc.Markdown(children='''
            # Old statistics
            Select a county to display its past data
        ''', id='table-old-name'),
        dcc.Graph(
            id='table-old',
            figure=get_table_old_figure(-1)
        )
    ], [
        dcc.Markdown(children='''
            # Predicted statistics
            Select a county to display predicted true positive rate
        ''', id='table-new-name'),
        dcc.Graph(
            id='table-new',
            figure=get_table_new_figure(-1)
        )
    ]),
    dbc.Container(
        [dcc.Markdown(children='''
# Motives

## Purpose
This app provides forecasting for the next 30 days for every county in England.
To see the details about local risk, hover the cursor over the relevant region. By clicking, past data for infection rate is plotted in the section Plots. 

## Training Data
The data was fetched from the Gov UK official site, attached [here](coronavirus.data.gov.uk/details/download).
For developers, a file containing all the training models and with extracted weight/bias values can be downloaded [here](/Covid_Cases_Predictor-main/models.zip).

## Why is it important
If a new epidemic arises, it is important to localize regions with high potential of risk before it gets out of control,
so preventive measures can be undertaken before cases start arising.

# Future steps
We have many other features we would like to recreate:
- Extending the data over England's borders
- Plotting the predicted values for other metrics
- Creating an API for embedding the map and prediction data into a website
- Decrease website bloat
- Speed up inference for the true positive rate model
        ''', style={"padding-bottom": 50})]
    ),
], style={'font-size': '15px' }) #, 'background-color': '#110226', 'color': 'white'})

# CALLBACKS

@app.callback(
    Output('graph-figure', 'figure'),
    Output('table-old-name', 'children'),
    Output('table-new-name', 'children'),
    Output('table-old', 'figure'),
    Output('table-new', 'figure'),
    Input('map-figure', 'clickData'))
def update_figure(clickData):
    if clickData is not None:
        location = clickData['points'][0]['location']
        last_clicked = location

        if location not in selections:
            selections.add(location)
        else:
            selections.remove(location)

    return get_graph_figure(selections), ('''
        # Old statistics  
        ''' + ('Select a county to display past data' if last_clicked == -1 else f'Displaying past data from {idmap[last_clicked]}') + '''
    '''), ('''
        # Predicted statistics  
        ''' + ('Select a county to display predicted true positive rate' if last_clicked == -1 else f'Displaying past data from {idmap[last_clicked]}') + '''
    '''), get_table_old_figure(last_clicked), get_table_new_figure(last_clicked)


@app.callback(
    Output('graph-figure', 'figure'),
    Input('clear-btn', 'n_clicks'))
def update_figure_2(_):
    selections = set()
    return get_graph_figure(selections)


if __name__ == '__main__':
    app.run_server()