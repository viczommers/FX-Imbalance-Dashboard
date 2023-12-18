import dash
from dash import Dash, dcc, html, Input, Output, callback
import dash_bootstrap_components as dbc

import plotly.graph_objects as go
import pandas_datareader as pdr
import pandas as pd
from pandas import Timestamp
import numpy as np
import requests
import io
import datetime
from datetime import date, timedelta

FX = pdr.get_data_fred(['DEXUSUK','M2SL'],start='2000-01-01')#.sort_index()
boe_series = {'Datefrom':'01/Jan/2000','SeriesCodes':'LPMVWYW','CSVF':'TN','UsingCodes':'Y','VPD':'N','VFD':'N'}
url2 = 'http://www.bankofengland.co.uk/boeapps/iadb/fromshowcolumns.asp?csv.x=yes'
headers = {'User-Agent': 'Mozilla/5.0 (X11; Linux x86_64) ' 'AppleWebKit/537.36 (KHTML, like Gecko) ' 'Chrome/54.0.2840.90 ' 'Safari/537.36'}
response = requests.get(url2, params=boe_series, headers=headers,verify = False)
df2 = pd.read_csv(io.BytesIO(response.content))
df2['DATE'] = pd.to_datetime(df2['DATE'],format='%d %b %Y')
df2['DATE'] = df2['DATE'].apply(lambda dt: dt.replace(day=1))
df2.set_index('DATE', inplace=True)
FX['M2UK'] = FX.index.map(df2['LPMVWYW'])
FX['M2UK'] = (FX['M2UK']/1000)
FX['DEXUSUK'] = FX['DEXUSUK'].interpolate(method='linear')

# Select Range to Plot:
FX_sorted1 = FX.loc[FX.index.year >= 2018]
# Create duplicated df and Drop NAs for monthly data (different frequency)
FX_sorted2 = FX_sorted1.loc[FX_sorted1['M2SL'].notna()]

# Placeholder Plot for time T0 rendering
layout = go.Layout(title="",
               	yaxis=dict(
                    title="Time",
                    autorange='reversed'
                ),
                xaxis=dict(title="M2 Imbalance (Billions)"),
               	barmode="overlay",
               	bargap=0.1,
                xaxis2=dict(title='$ Dollars to £ Sterling Spot Exchange Rate', overlaying='x', side='top'),
                autosize=False,
                width=800,
                height=800,
                template="plotly_dark"
                )
trace_US = go.Bar(x=FX_sorted2.M2SL*(-1), y=FX_sorted2.index,
                orientation="h",
                name="US: M2 Money Base",
                marker=dict(color="#1f77b4"),opacity=0.75)
trace_UK = go.Bar(x=FX_sorted2.M2UK, y=FX_sorted2.index,
                orientation="h",
                name="UK: M2 Money Base",
                marker=dict(color="#d62728"),opacity=0.75)
fig = go.Figure(data=[trace_US, trace_UK], layout=layout)
fig.add_trace(go.Scatter(x=FX_sorted1.DEXUSUK,y=FX_sorted1.index, orientation='h', mode='lines',xaxis='x2',marker=dict(color='lightgreen'),name='FX Rate'))


app = Dash(__name__, external_stylesheets=[dbc.themes.DARKLY])
server = app.server

table_body = [html.Tr([html.Td("US M2 vs UK M2:"),html.Td(id='corr-pearson'),html.Td(id='corr-kendall'),html.Td(id='corr-spearman')]),
              html.Tr([html.Td("US M2 vs FX:"),html.Td(id='corr-US-p'),html.Td(id='corr-US-k'),html.Td(id='corr-US-s')]),
              html.Tr([html.Td("UK M2 vs FX:"),html.Td(id='corr-UK-p'),html.Td(id='corr-UK-k'),html.Td(id='corr-UK-s')])
              ]
table_header = [
                html.Tr([  # Second row of headers
                    html.Th(" ",style={'border': 'none'}),  # Empty header cell above the first column
                    html.Th("Correlation Type:", colSpan=3, style={'text-align': 'center'}),  # Big header spanning the last 3 columns
                ]),
                html.Tr([html.Th("",style={'border': 'none'}),
                         html.Th("Pearson"),
                         html.Th("Kendall"),
                         html.Th("Spearman")])
                ]

filter_card = dbc.Card([
        dbc.Row([
        html.Label("Date Range:"),
        html.Br(),
        dcc.DatePickerRange(id='daterange',
              start_date=datetime.datetime(2018, 1, 1),
              end_date=datetime.date.today(),
              min_date_allowed=datetime.datetime(2000, 1, 1),
              max_date_allowed=datetime.date.today(),
              display_format="MMM-YYYY",
        )], className="mt-3 mb-3"),
        dbc.Row([
        html.Label("Differencing:"),
        html.Br(),
        dbc.RadioItems(
            options=[
                {"label": "M2 Stock (Level)", "value": 1},
                {"label": "M2 Change (First-Order)", "value": 2},
                {"label": "M2 Rate of Change (Second-Order)", "value": 3},
                {"label": "M2 Pct Change (%)", "value": 4},
            ],
            value=1,
            id="radioitems",
        )], className="mt-3 mb-3"),
        dbc.Row([
        html.Label("Convert both Money Bases into:"),
        html.Br(),
        dbc.RadioItems(
            options=[
                {"label": "USD ($)", "value": 1},
                {"label": "Keep Nominal", "value": 2},
                {"label": "GBP (£)", "value": 3},
            ],
            value=2,
            id="radioitems-convert",
            className="btn-group",
            inputClassName="btn-check",
            labelClassName="btn btn-outline-primary",
            labelCheckedClassName="active",
        )], className="mt-3 mb-3"),
        dbc.Row([
            dbc.Table([html.Thead(table_header), html.Tbody(table_body)],bordered=True,striped=True)
        ], className="mt-3 mb-3"),
        dbc.Row([
            html.Label("References:"),
            html.A("1. M2 ($, Seasonally Adj.), FRED", href="https://fred.stlouisfed.org/series/M2SL",target="_blank"),
            html.A("2. M2 (£, Seasonally Adj.), BOE", href="https://www.bankofengland.co.uk/boeapps/database/FromShowColumns.asp?Travel=&searchText=LPMVWYW",target="_balnk")

        ])
], body=True, className="bg-dark rounded")

signature_card = dbc.Card([
                    html.Footer([html.P("Developed by Victor Zommers | ",style={'display': 'inline-block'}),
                                html.A("Check out other dashboards", href="https://sites.google.com/view/victor-zommers/",
                                    style={'display': 'inline-block', 'margin-left': '5px'}, target="_blank")
                                ], style={'text-align': 'left', 'margin-top': '20px','margin-left': '30px'})
                  ], className="border-0")

app.layout = dbc.Container([
    html.H1("FX Currency Supply Imbalance in GBP/USD"),
    dbc.Row([
        dbc.Col(filter_card,
                width={"size": 4},
                className="mt-3 mb-3"
        ),
        dbc.Col(
            dcc.Graph(figure=fig,id="fxgraph"),
            width={"size": 8},
            className="mt-3 mb-3"
        )
    ]),
    dbc.Row(dbc.Col(signature_card,width={"size":12},className="mt-0 mb-3"))
], fluid=False)

@app.callback(
    [
        Output('fxgraph','figure'),
        Output('corr-pearson', 'children'),
        Output('corr-kendall', 'children'),
        Output('corr-spearman', 'children'),
        Output('corr-US-p', 'children'),
        Output('corr-US-k', 'children'),
        Output('corr-US-s', 'children'),
        Output('corr-UK-p', 'children'),
        Output('corr-UK-k', 'children'),
        Output('corr-UK-s', 'children')
    ],
    [
        Input("radioitems","value"),
        Input("radioitems-convert","value"),
        Input('daterange', 'start_date'),
        Input('daterange', 'end_date')
    ]
)
def update_graph(radio,conversion,starttime,endtime):
    #global FX, FX_sorted1, FX_sorted2, layout
    axis_text = "M2 Imbalance (Billions)"
    start = Timestamp(starttime)
    end = Timestamp(endtime)
    FX_sorted1 = FX[(FX.index >= start) & (FX.index <= end)]
    #FX_sorted1['DEXUSUK'] = FX_sorted1['DEXUSUK'].interpolate(method='linear')
    FX_sorted2 = FX_sorted1[FX_sorted1.M2SL.notna()]
    if conversion == 1:
        FX_sorted2.loc[:, 'M2UK'] = FX_sorted2['M2UK']*FX_sorted2['DEXUSUK']
        axis_text = "M2 Imbalance ($ Billions)"
    elif conversion == 3:
        FX_sorted2.loc[:, 'M2SL'] = FX_sorted2['M2SL']/FX_sorted2['DEXUSUK']
        axis_text = "M2 Imbalance (£ Billions)"
    if radio == 1:
        pass
    elif radio == 2:
        FX_sorted2.loc[:, 'M2SL'] = FX_sorted2['M2SL'].diff()
        FX_sorted2.loc[:, 'M2UK'] = FX_sorted2['M2UK'].diff()
    elif radio == 3:
        FX_sorted2.loc[:, 'M2SL'] = FX_sorted2['M2SL'].diff().diff()
        FX_sorted2.loc[:, 'M2UK'] = FX_sorted2['M2UK'].diff().diff()
    elif radio == 4:
        FX_sorted2.loc[:, 'M2SL'] = FX_sorted2['M2SL'].pct_change()*100
        FX_sorted2.loc[:, 'M2UK'] = FX_sorted2['M2UK'].pct_change()*100
        axis_text = "M2 Imbalance (Pct Change %)"
    #print(FX_sorted2)

    trace_US = go.Bar(x=FX_sorted2.M2SL*(-1), y=FX_sorted2.index,
                orientation="h",
                name="US: M2 Money Base",
                marker=dict(color="#1f77b4"),opacity=0.75)
    trace_UK = go.Bar(x=FX_sorted2.M2UK, y=FX_sorted2.index,
                orientation="h",
                name="UK: M2 Money Base",
                marker=dict(color="#d62728"),opacity=0.75)
    fig = go.Figure(data=[trace_US, trace_UK], layout=layout)
    fig.add_trace(go.Scatter(x=FX_sorted1.DEXUSUK,y=FX_sorted1.index, orientation='h', mode='lines',xaxis='x2',marker=dict(color='lightgreen'),name='FX Rate'))
    fig.update_layout(xaxis_title=axis_text)

    corr_p = round(FX_sorted2['M2SL'].corr(FX_sorted2['M2UK'], method='pearson'), 3)
    corr_k = round(FX_sorted2['M2SL'].corr(FX_sorted2['M2UK'], method='kendall'), 3)
    corr_s = round(FX_sorted2['M2SL'].corr(FX_sorted2['M2UK'], method='spearman'), 3)
    corr_p_UK = round(FX_sorted2['M2UK'].corr(FX_sorted2['DEXUSUK'], method='pearson'), 3)
    corr_k_UK = round(FX_sorted2['M2UK'].corr(FX_sorted2['DEXUSUK'], method='kendall'), 3)
    corr_s_UK = round(FX_sorted2['M2UK'].corr(FX_sorted2['DEXUSUK'], method='spearman'), 3)
    corr_p_US = round(FX_sorted2['M2SL'].corr(FX_sorted2['DEXUSUK'], method='pearson'), 3)
    corr_k_US = round(FX_sorted2['M2SL'].corr(FX_sorted2['DEXUSUK'], method='kendall'), 3)
    corr_s_US = round(FX_sorted2['M2SL'].corr(FX_sorted2['DEXUSUK'], method='spearman'), 3)
    return fig, corr_p, corr_k, corr_s, corr_p_US, corr_k_US, corr_s_US, corr_p_UK, corr_k_UK, corr_s_UK



if __name__ == '__main__':
    app.run_server(debug=True)