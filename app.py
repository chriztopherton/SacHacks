# -*- coding: utf-8 -*-
import pandas as pd
import dash
import dash_core_components as dcc
import dash_html_components as html
from dash.dependencies import Input, Output, State, ClientsideFunction


app = dash.Dash(__name__)


# Load Data
player_stats = pd.read_excel('2K Player Stats.xlsx')
team_stats = pd.read_excel('2KL Team Stats.xlsx')

player_stats = player_stats.rename(columns = {"FG%":"FG_pct","FG3%":"FDG3_pct","FT%":"FT_pct","eFG%":"effi_pct","TS%":"Tru_shoot_pct"})
team_stats = team_stats.rename(columns={"FG%":"FG_pct","3P%":"3P_pct","Opp_3P%":"Opp_3P_pct","Opp_FG%":"Opp_FG_pct"})

teams = team_stats['Nickname'].unique()
players = player_stats['Player'].unique()

team_features = team_stats.columns.tolist()
player_features = player_stats.columns.tolist()

# App Layout
app.layout = html.Div(
    [
        html.Div(
            [
                dcc.Dropdown(
                    id = 'xaxis-column',
                    options = [{'label': i, 'value': i} for i in teams],
                ),
            ],
            style = {'width': '48%', 'display': 'inline-block'}
        ),

        html.Div(
            [
                dcc.Dropdown(
                    id = 'yaxis-column',
                    options = [{'label': i, 'value': i} for i in players],
                    # value = 'lol'
                ),
            ],
            style = {'width' : '48%', 'display': 'inline-block', 'float': 'right'}
        ),

        dcc.Graph(id='indicator-graphic'),
        
    ]
)

@app.callback(
    Output('indicator-graphic', 'figure'),
    [
        Input('xaxis-column', 'value'),
        Input('yaxis-column', 'value'),
    ]
)

def update_graph(xaxis_columnname, yaxis_columnname):
    return{
        'data': [
            dict(
                # x = ,
                y = team_stats[team_stats['']]
            )
        ]
    }


if __name__ == '__main__':
    app.run_server(debug=True)