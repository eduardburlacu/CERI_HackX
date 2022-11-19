#!/usr/bin/env python3
import plotly.express as px
import plotly.graph_objects as go
from dash import Dash, html, dcc, Input, Output
import dash_bootstrap_components as dbc
import numpy as np
import pandas as pd
import json
from perlin_noise import PerlinNoise

## GET DATA

rands = np.random.rand(192)
coefs = np.random.rand(192)
def get_dummy_data(time):
    """
    Input:
    time - time value in days (between 1 and 100)
    Output:
    df - case numbers for each county for a time t
    """
    noise = PerlinNoise(octaves=10, seed=122)
    return rands * 50 + 25 - (coefs - 0.5) * time

idmap = {}
with open('uk-counties-2.json') as file:
    counties = json.load(file)
for f in counties['features']:
    idmap[f['properties']['ID_2']] = f['properties']['NAME_2']
idmap = [idmap[i+1] for i in range(192)]

## GENERATE MAP FIGURE

def get_map_figure(num_steps, step_time):

    df = pd.DataFrame({ 'fips': [], 'days': [], 'cases': [] });
    for t in range(num_steps):
        data = get_dummy_data(t*step_time)
        for i in range(len(data)):
            df.loc[len(df.index)] = [i, f"Day {t*step_time}", data[i]]
    df = df.astype({ 'fips': 'int32' })
    
    fig = px.choropleth_mapbox(
        df, 
        locations='fips', 
        color='cases',
        animation_frame='days',
        geojson=counties, 
        featureidkey="properties.ID_2",
        color_continuous_scale="Viridis",
        range_color=(0, 100),
        center={ 'lon': -2, 'lat': 54 },
        mapbox_style="carto-positron",
        zoom=4.5,
        opacity=0.5,
        labels={'cases':'Number of cases', 'fips': 'County number', 'days': 'Day'}
    )
    fig.update_layout({ 'margin':{"r":0,"t":0,"l":0,"b":0}, 'height':600, 'uirevision': 'constant' })
    fig.update_traces(showlegend=False)
    return fig

# GENERATE GRAPH FIGURE

def get_graph_figure(selections):
    df = pd.DataFrame({ 'fips': [], 'days': [], 'cases': [] });
    for t in range(0, 100):
        data = get_dummy_data(t)
        for i in selections:
            df.loc[len(df.index)] = [i, t, data[i]]
    df = df.astype({ 'fips': 'int32', 'days': 'int32' })

    fig = px.line(df, x="days", y="cases", labels=idmap, color='fips', range_x=(0, 100), range_y=(0, 100))
    return fig
    

## CREATE APP

app = Dash(__name__, external_stylesheets=[dbc.themes.BOOTSTRAP])

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
                        figure=get_map_figure(20, 5)
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

selections = set()

@app.callback(
    Output('graph-figure', 'figure'),
    [Input('map-figure', 'clickData')])
def update_figure(clickData):
    if clickData is not None:
        location = clickData['points'][0]['location']

        if location not in selections:
            selections.add(location)
        else:
            selections.remove(location)
        
        print(selections)

    return get_graph_figure(selections)

if __name__ == '__main__':
    app.run_server(debug=True)