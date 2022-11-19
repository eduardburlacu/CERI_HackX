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
    return rands * 50 + 50 - (coefs - 0.5) * time

## GENERATE FIGURE

def get_figure(num_steps, step_time):
    with open('uk-counties-2.json') as file:
        counties = json.load(file)

    def construct_df():
        df = pd.DataFrame({ 'fips': [], 'days': [], 'cases': [] });
        for t in range(num_steps):
            data = get_dummy_data(t*step_time)
            for i in range(len(data)):
                df.loc[len(df.index)] = [int(i), f"Day {t*step_time}", data[i]]
        df.astype({ 'fips': 'int32' })
        return df

    fig = px.choropleth_mapbox(
        construct_df(), 
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

fig = get_figure(20, 5)

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
    dbc.Container([
        dbc.Row(
            [
                dbc.Col(
                    dcc.Graph(
                        id='graph-map',
                        figure=fig
                    ),
                    xxl=6,
                    xl=6,
                    lg=12,
                    md=12,
                    sm=12,
                    xs=12,
                ),
                dbc.Col(
                    dcc.Markdown(children='''
# Plots
This is where your plots will show up
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
# Plots
This is where your plots will show up
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
# Plots
This is where your plots will show up
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
                        ''',
                        style={ 'height': 'calc(100vh-35px)', 'overflow': 'scroll-y' }
                    ),
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
    style={ 'margin-top': '20px', "margin-bottom": '100px' })
])

selections = set()

@app.callback(
    #Output('graph-map', 'figure'),
    input=[Input('graph-map', 'clickData')])
def update_figure(clickData):
    print('AAAAAAAAAAA!')  
    if clickData is not None:            
        location = clickData['points'][0]['location']

        if location not in selections:
            selections.add(location)
        else:
            selections.remove(location)
        
        print(selections)


if __name__ == '__main__':
    app.run_server(debug=True)