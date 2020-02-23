# -*- coding: utf-8 -*-
import pandas as pd
import numpy as np
import dash
import dash_core_components as dcc
import dash_html_components as html
import dash_bootstrap_components as dbc
from dash.dependencies import Input, Output, State, ClientsideFunction

import pandasql as ps
from pandasql import sqldf
import plotly.express as px

import dash_table
import plotly.graph_objs as go
import io
import dash_daq as daq

external_stylesheets = ['https://codepen.io/chriddyp/pen/bWLwgP.css', dbc.themes.BOOTSTRAP]

app = dash.Dash(__name__,external_stylesheets = external_stylesheets)

colors = {
    'background': '#111111',
    'text': '#7FDBFF'
}

# Load Data
team_url = 'https://drive.google.com/uc?export=download&id=1RoAG1mCkR9_O2EgVIZEpAJi6eVGtF-V0'
player_url = 'https://drive.google.com/uc?export=download&id=119yYXWRKDelXqcv6CK2g0570iZKh0NWU'
team_stats = pd.read_excel(team_url)
player_stats = pd.read_excel(player_url)

player_stats.columns = ["Person ID", "Player", "Team", "Season Type", "Games Played", "Minutes Played", "Field Goals",
                        "Field Goals Attempted", "Percentage of Successful Field Goal Attempts", "Three Pointers",
                        "Three Pointers Attempted", "Percentage of Successful Three Point Attempts", "Free Throws",
                        "Free Throws Attempted", "Percentage of Successful Free Throw Attempts", "Offensive Rebounds",
                        "Defensive Rebounds", "Rebounds", "Assists", "Personal Fouls", "Steals", "Turnovers", "Blocks",
                        "Points", "Career High Points", "Effective Field Goal Percentage", "True Shooting Percentage"]
team_stats.columns = ["Team ID", "Nickname", "Games Played", "Sum of Minutes Played by All Players", "Minutes Played by Team",
                      "Points", "Field Goals", "Field Goals Attempted", "Percentage of Successful Field Goal Attempts",
                      "Three Pointers", "Three Pointers Attempted", "Percentage of Successful Three Point Attempts",
                      "Offensive Rebounds", "Defensive Rebounds", "Assists", "Steals", "Turnovers", "Blocked Shots",
                      "Points by Opponent", "Point Differential", "Field Goals by Opponent",
                      "Field Goals Attempted by Opponent", "Percentage of Successful Field Goal Attempts by Opponent",
                      "Three Pointers by Opponent", "Three Pointers Attempted by Opponent",
                      "Percentage of Successful Three Point Attempts by Opponent", "Offensive Rebounds by Opponent",
                      "Defensive Rebounds by Opponent", "Assists by Opponent", "Steals by Opponent", "Turnovers by Opponent",
                      "Blocked Shots by Opponent"]

teams = team_stats['Nickname'].unique()
players = player_stats['Player'].unique()

team_stat_categories = team_stats.columns.tolist()[5:18]
player_stat_categories = player_stats.columns.tolist()[4:]

# App Layout
app.layout = html.Div(
    [
        html.Div(
            [
                html.H1('NBA 2K Rankings', style = {'fontSize': 50, 'text-transform': 'uppercase', 'font-weight': '800'}),
                
                html.Img(src = '/assets/2k20.png')
            ],
            className = 'banner'
        ),

        dbc.Row(dbc.Col(html.H1("Kevin Chu, Christopher Ton, John Tran, Nilay Varshney", style = {'fontSize': 15})),
                align = "left"),
        
        # Left dropdown for team 1
        html.Div([
            dcc.Markdown('''# Select First Team '''),
                dcc.Dropdown(
                    id = 'team1',
                    options = [{'label': i, 'value': i} for i in teams],
                    value = 'Kings Guard Gaming'),

        # Middle dropdown for team 2
            dcc.Markdown('''# Select Second Team'''),
                dcc.Dropdown(
                    id = 'team2',
                    options = [{'label': i, 'value': i} for i in teams],
                    value = 'Lakers Gaming'
                ),
            dcc.Graph(id = 'indicator-graphic')
            ],
            style = {'width' : '50%', 'display': 'inline-block', 'float': 'center'}
        ),

        # Right dropdown for category
        html.Div(
            [
                dcc.Markdown('''# All Teams'''),
                    dcc.Dropdown(
                        id = 'team_stat_category',
                        options = [{'label': i, 'value': i} for i in team_stat_categories],
                        value = 'Three Pointers'
                    ),
                    dcc.Graph(id='allteams_output-graphic')
            ],
            style = {'width': '50%', 'display': 'inline-block', 'float': 'right'}
        ),

        html.Div(
            [
                dcc.Markdown('''# All Players'''),
                    dcc.Dropdown(
                        id = 'player_stat_category',
                        options = [{'label': i, 'value': i}for i in player_stat_categories],
                        value = 'Steals' 
                    ),
                    dcc.Graph(id='allplayers_output-graphic')
            ],
            style = {'width': '100%','display': 'inline-block', 'float': 'right'}
        )
        
    ]
)

@app.callback(
    Output('allteams_output-graphic', 'figure'),
    [Input('team_stat_category','value')])

def update_output_div(feat):
    data_feat = team_stats.sort_values(by=[feat], ascending=False)

    return {
        'data':[
        {'x':data_feat["Nickname"],'y':data_feat[feat],'type': 'bar','marker':{'color':data_feat[feat],'colorscale': 'Viridis'}}],
        'layout': {
            'title': (feat)
        }
}

@app.callback(
    Output('allplayers_output-graphic', 'figure'),
    [Input('player_stat_category','value')])

def update_output_div(feat):
    data_feat = player_stats.sort_values(by=[feat], ascending=False)

    return {
        'data':[
        {'x':data_feat["Player"],'y':data_feat[feat],'type': 'bar','marker':{'color':data_feat[feat],'colorscale': 'Viridis'}}],
        'layout': {
            'title': (feat)
        }
}


@app.callback(
    Output('indicator-graphic', 'figure'),
    [Input('team1', 'value'),
     Input('team2', 'value'),
     Input('team_stat_category', 'value')])

def update_graph(team_1, team_2, stat):
    piedata = go.Pie(labels = [team_1,team_2],values = [team_stats[team_stats["Nickname"] == team_1][stat].values[0],
                                                        team_stats[team_stats["Nickname"] == team_2][stat].values[0]])
    return {'data':[piedata],'layout':{'title':(team_1 + ' vs. ' + team_2)}}

if __name__ == '__main__':
    app.run_server(debug = False)