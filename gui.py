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
from script_model import get_predicted
data = get_predicted()
sys.path.append('../')

idmap = {}
namemap = {}
data2 = {}
with open('uk-counties-2.json') as file:
    counties = json.load(file)
for f in counties['features']:
    idmap[f['properties']['id']] = f['properties']['name']
    namemap[f['properties']['name']] = f['properties']['id']
    data2[f['properties']['name']] = data[f['properties']['name']]
num_dataset = len(list(idmap.keys()))
idmap = [idmap[i] for i in range(num_dataset)]
data = data2

## GENERATE MAP FIGURE

num_steps = 15
step_time = 2
risk_range = 0.2

def get_map_figure():

    df = pd.DataFrame({ 'cid': [], 'days': [], 'risk': [] })
    for i in range(num_dataset):
        for t in range(num_steps):
            df.loc[len(df.index)] = [int(i), f"Day {t*step_time}", data[idmap[i]][t*step_time]]
    df = df.astype({ 'cid': 'int32' })
    
    fig = px.choropleth_mapbox(
        df, 
        locations='cid', 
        color='risk',
        animation_frame='days',
        geojson=counties, 
        featureidkey="properties.id",
        color_continuous_scale="Viridis",
        range_color=(0, risk_range),
        hover_name=idmap*num_steps,
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
    df = pd.DataFrame({ 'cid': [], 'days': [], 'risk': [] });
    for i in selections:
        for t in range(num_steps*step_time):
            df.loc[len(df.index)] = [i, t, data[idmap[i]][t]]
    df = df.astype({ 'cid': 'int32', 'days': 'int32' })

    fig = px.line(df, x="days", y="risk", 
        # hover_name=idmap*20, 
        color='cid', range_x=(0, num_steps*step_time), range_y=(0, risk_range))
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

app.layout = html.Div(children=[
    navbar,
    html.Div(id='hidden-div', style={'display':'none'}),
    dbc.Container([
        dbc.Row(
            [
                dbc.Col(
                    dcc.Graph(
                        id='map-figure',
                        figure=get_map_figure()
                    ),
                    xxl=6,
                    xl=6,
                    lg=12,
                    md=12,
                    sm=12,
                    xs=12,
                ),
                dbc.Col(
                    [
                        dcc.Markdown(children='''
                            # Plots
                            Click a county to plot the number of cases in the next 30 days.
                        '''),
                        dbc.Button(children='Clear', id='clear-btn', n_clicks=0),
                        dcc.Graph(
                            id='graph-figure',
                            figure=get_graph_figure(set())
                        )   
                    ],
                    xxl=6,
                    xl=5,
                    lg=12,
                    md=12,
                    sm=12,
                    xs=12,
                ),
            ],
            align="center",
            className="g-0"
        )
        ],
        style={ 'margin-top': '20px', "margin-bottom": '20px' }
    ),
    dbc.Container(
        [dcc.Markdown(children='''
            # Motives
            ## Purpose
            This app does x and y and z. 234534 534 5
            245 345 35 34 5345345 345 34 53 45 3 435
            34 53 5345 345 34 5sd f sf sdf sd fsf fe
            wf ew fwe f ewf wf w f wferg trhrthrh 
            ## How to use
            This is how you use the app. 1 2 3 4
            5 4 5 545675675 7857 876 8 678 67 867  ergrege geergeg egergerg gege
            ge egegergergge fwsofwfkwopef weefjiweofi ewdioej wefn wefn weoifjwio
            ## Why is it important
            Because it is. dfije freferf rernfwf eefne fernfe eof
            efue efne eroif eorif opkwe ewoejd wlioejd weopjkd weifj weopfj wpoefk
            wlfn wefjn, wfoij owiefj wopf. iwjef wefj 
        ''')]
    )
])

# CALLBACK

selections = set()
@app.callback(
    Output('graph-figure', 'figure'),
    Input('map-figure', 'clickData'))
def update_figure(clickData):
    if clickData is not None:
        location = clickData['points'][0]['location']

        if location not in selections:
            selections.add(location)
        else:
            selections.remove(location)
        
        print(selections)

    return get_graph_figure(selections)

@app.callback(
    Output('graph-figure', 'figure'),
    Input('clear-btn', 'n_clicks'))
def update_figure_2(clickInfo):
    print(clickInfo)
    if clickInfo is not None:
        selections = set()
    return get_graph_figure(selections)


if __name__ == '__main__':
    app.run_server(debug=True)