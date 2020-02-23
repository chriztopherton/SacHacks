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

########################################################################################################################################################################################################################################################################

external_stylesheets = ['https://codepen.io/chriddyp/pen/bWLwgP.css', dbc.themes.BOOTSTRAP]

app = dash.Dash(__name__, external_stylesheets = external_stylesheets)

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

# Get Player Rankings

ps = player_stats.copy()
ps["Two Pointers"] = ps["Field Goals"] - ps["Three Pointers"]
ps["Two Pointers Attempted"] = ps["Field Goals Attempted"] - ps["Three Pointers Attempted"]
ps["Two Pointers Missed"] = ps["Two Pointers Attempted"] - ps["Two Pointers"]
ps["Three Pointers Missed"] = ps["Three Pointers Attempted"] - ps["Three Pointers"]
ps["Free Throws Missed"] = ps["Free Throws Attempted"] - ps["Free Throws"]
p = ps[["Player", "Team"]]
s = ps[["Games Played", "Minutes Played", "Two Pointers", "Two Pointers Missed",
        "Three Pointers", "Three Pointers Missed", "Free Throws",
        "Free Throws Missed", "Offensive Rebounds", "Defensive Rebounds", "Assists",
        "Personal Fouls", "Steals", "Turnovers", "Blocks", "Career High Points"]]
weights = [1, (1/24), 8, -2, 12, -3, 4, -1, 1, 2, 2, -6, 2, -2, 2, 4]
s["Score"] = np.average(s.values, axis = 1, weights = weights)
psr = pd.concat((p, s), axis = 1)
psr.sort_values(["Score"], ascending = False, inplace = True)
psr.reset_index(drop = True, inplace = True)
psr["Rank"] = psr.index + 1
player_rank = psr[["Player", "Team", "Rank"]]

# Get Team Rankings

ts = team_stats.copy()
ts["Two Pointers"] = ts["Field Goals"] - ts["Three Pointers"]
ts["Two Pointers Attempted"] = ts["Field Goals Attempted"] - ts["Three Pointers Attempted"]
ts["Two Pointers Missed"] = ts["Two Pointers Attempted"] - ts["Two Pointers"]
ts["Three Pointers Missed"] = ts["Three Pointers Attempted"] - ts["Three Pointers"]
ts["Free Throws"] = ts["Points"] - (2 * ts["Two Pointers"]) - (3 * ts["Three Pointers"])
t = ts[["Nickname"]]
st = ts[["Two Pointers", "Two Pointers Missed", "Three Pointers", "Three Pointers Missed", "Free Throws", "Offensive Rebounds",
         "Defensive Rebounds", "Assists", "Steals", "Turnovers", "Blocked Shots"]]
weights_t = [8, -2, 12, -3, 4, 1, 2, 2, 2, -2, 2]
st["Score"] = np.average(st.values, axis = 1, weights = weights_t)
tsr = pd.concat((t, st), axis = 1)
tsr.sort_values(["Score"], ascending = False, inplace = True)
tsr.reset_index(drop = True, inplace = True)
tsr["Rank"] = tsr.index + 1
team_rank = tsr[["Nickname", "Rank"]]

# App Layout
app.layout = html.Div(
    [
        html.Div(
            [
                html.H1('NBA 2K DASH', style = {'fontSize': 50, 'text-transform': 'uppercase', 'font-weight': '800'}),
                html.Img(src = '/assets/2k20.png')
            ],
            className = 'banner'
        ),
        
        dbc.Row(dbc.Col(html.H1("Kevin Chu, Christopher Ton, John Tran, Nilay Varshney",
                                style = {'fontSize': 15, 'paddingLeft': '1%'})),
                align = "left"),
        
        html.Div([
            # Left dropdown for team 1
            dcc.Markdown('''# Select First Team '''),
                dcc.Dropdown(
                    id = 'team1',
                    options = [{'label': i, 'value': i} for i in teams],
                    value = 'Kings Guard Gaming'),
            # Left dropdown for team 2
            dcc.Markdown('''# Select Second Team'''),
                dcc.Dropdown(
                    id = 'team2',
                    options = [{'label': i, 'value': i} for i in teams],
                    value = 'Lakers Gaming'),
            dcc.Graph(id = 'indicator-graphic')
        ],
            style = {'width': '50%', 'display': 'inline-block', 'paddingLeft': '1%', 'paddingRight': '1%'}
        ),

######################################################################################################################################################################################################

        # Right dropdown for category
        html.Div(
            [
                dcc.Markdown('''# All Teams'''),
                    dcc.Dropdown(
                        id = 'team_stat_category',
                        options = [{'label': i, 'value': i} for i in team_stat_categories],
                        value = 'Three Pointers'
                    ),
                dcc.Graph(id = 'allteams_output-graphic')
            ],
            style = {'width': '50%', 'display': 'inline-block', 'paddingLeft': '1%', 'paddingRight': '1%'}
        ),

#################################################################################################################################################################################################################
        
        html.Div(
            [
                dcc.Markdown('''# All Players'''),
                    dcc.Dropdown(
                        id = 'player_stat_category',
                        options = [{'label': i, 'value': i} for i in player_stat_categories],
                        value = 'Steals'
                    ),
                dcc.Graph(id = 'allplayers_output-graphic')
            ],
            style = {'width': '50%', 'display': 'inline-block', 'paddingLeft': '1%', 'paddingRight': '1%'}
        ),
        
#################################################################################################################################################################################################################        
        
        html.Div([
            # Middle dropdown for team 1
            dcc.Markdown('''# Select First Team '''),
                dcc.Dropdown(
                    id = 'team11',
                    options = [{'label': i, 'value': i} for i in teams],
                    value = 'Kings Guard Gaming'),
            # Middle dropdown for team 2
            dcc.Markdown('''# Select Second Team'''),
                dcc.Dropdown(
                    id = 'team22',
                    options = [{'label': i, 'value': i} for i in teams],
                    value = 'Lakers Gaming'),
            dcc.Graph(id = 'indicator-graphic2')
        ],
            style = {'width': '50%', 'display': 'inline-block', 'paddingLeft': '1%', 'paddingRight': '1%'}
        ),
        
        # Player Rankings
        html.Div(
            [
                dcc.Markdown('''# Player Rankings'''),
                dash_table.DataTable(
                    id = 'player_ranking',
                    columns = [{"name": i, "id": i} for i in player_rank.columns],
                    data = player_rank.to_dict('records'),
                    style_table = {'maxHeight': '400px', 'overflowY': 'scroll'}
                )
            ],
            style = {'width': '40%', 'display': 'inline-block', 'paddingLeft': '1%', 'paddingRight': '1%'}
        ),
        
        # Team Rankings
        html.Div(
            [
                dcc.Markdown('''# Team Rankings'''),
                dash_table.DataTable(
                    id = 'team_ranking',
                    columns = [{"name": i, "id": i} for i in team_rank.columns],
                    data = team_rank.to_dict('records'),
                    style_table = {'maxHeight': '400px', 'overflowY': 'scroll'}
                )
            ],
            style = {'width': '30%', 'display': 'inline-block', 'paddingLeft': '1%', 'paddingRight': '1%'}
        ),
        
        #Player Rankings by Team
        html.Div(
            [
                dcc.Markdown('''# Select Team'''),
                dcc.Dropdown(
                    id = 'team_player_ranking',
                    options = [{'label': i, 'value': i} for i in teams],
                    value = 'Kings Guard Gaming'),
                    dash_table.DataTable(
                        id = 't_player_ranking',
                        columns = [{"name": i, "id": i} for i in player_rank.columns],
                        data = [],
                        style_table = {'maxHeight': '400px', 'overflowY': 'scroll'}
                    )
            ],
            style = {'width': '30%', 'display': 'inline-block', 'paddingLeft': '1%', 'paddingRight': '1%'}
        )
    ]
)

#################################################################################################################################################################################################################

@app.callback(
    Output('t_player_ranking', 'data'),
    [Input('team_player_ranking', 'value')])

def update_team_player_ranking(team):
    df = player_rank[player_rank['Team'] == team]
    return df.to_dict('records')

#################################################################################################################################################################################################################

@app.callback(
    Output('allteams_output-graphic', 'figure'),
    [Input('team_stat_category','value')])

def update_output_div(feat):
    data_feat = team_stats.sort_values(by=[feat], ascending=False)

    return {
        'data': [{'x': data_feat["Nickname"], 'y': data_feat[feat], 'type': 'bar',
                  'marker': {'color': data_feat[feat], 'colorscale': 'Viridis'}}],
        'layout': {'title': (feat)}
    }

#######################################################################################################################################################################################################################################

@app.callback(
    Output('allplayers_output-graphic', 'figure'),
    [Input('player_stat_category','value')])

def update_output_div(feat):
    data_feat = player_stats.sort_values(by=[feat], ascending=False)

    return {
        'data': [{'x': data_feat["Player"], 'y': data_feat[feat], 'type': 'bar',
                  'marker':{'color': data_feat[feat], 'colorscale': 'Viridis'}}],
        'layout': {'title': (feat)}
    }

############################################################################################################################################################################################################################

@app.callback(
    Output('indicator-graphic', 'figure'),
    [Input('team1', 'value'), Input('team2', 'value'), Input('team_stat_category', 'value')])

def update_graph(team_1, team_2, stat):
    piedata = go.Pie(labels = [team_1,team_2],values = [team_stats[team_stats["Nickname"] == team_1][stat].values[0],
                                                        team_stats[team_stats["Nickname"] == team_2][stat].values[0]])
    
    return {'data': [piedata], 'layout': {'title': (team_1 + ' vs. ' + team_2)}}

############################################################################################################################################################################################################################

@app.callback(
    Output('indicator-graphic2', 'figure'),
    [Input('team11', 'value'), Input('team22', 'value')])

def update_graph2(team_1, team_2):
    return {
        'data': [
            {'y': ['Points'], 'x': team_stats[team_stats['Nickname'] == team_1]['Points'], 'type': 'bar', 'name': team_1,
             'orientation': 'h'},
            {'y': ['Points'], 'x': team_stats[team_stats['Nickname'] == team_2]['Points'], 'type': 'bar', 'name': team_2,
             'orientation': 'h'},
            {'y': ['Offensive Rebounds'], 'x': team_stats[team_stats['Nickname'] == team_1]['Offensive Rebounds'],
             'type': 'bar', 'name': team_1, 'orientation': 'h'},
            {'y': ['Offensive Rebounds'], 'x': team_stats[team_stats['Nickname'] == team_2]['Offensive Rebounds'],
             'type': 'bar', 'name': team_2,'orientation':'h'},
            {'y': ['Defensive Rebounds'], 'x': team_stats[team_stats['Nickname'] == team_1]['Defensive Rebounds'],
             'type': 'bar', 'name': team_1, 'orientation': 'h'},
            {'y': ['Defensive Rebounds'], 'x': team_stats[team_stats['Nickname'] == team_2]['Defensive Rebounds'],
             'type': 'bar', 'name': team_2, 'orientation': 'h'},
            {'y': ['Assists'], 'x': team_stats[team_stats['Nickname'] == team_1]['Assists'], 'type': 'bar',
             'name': team_1, 'orientation': 'h'},
            {'y': ['Assists'], 'x': team_stats[team_stats['Nickname'] == team_2]['Assists'], 'type': 'bar',
             'name': team_2, 'orientation': 'h'},
            {'y': ['Steals'], 'x': team_stats[team_stats['Nickname'] == team_1]['Steals'], 'type': 'bar',
             'name': team_1, 'orientation': 'h'},
            {'y': ['Steals'], 'x': team_stats[team_stats['Nickname'] == team_2]['Steals'], 'type': 'bar',
             'name': team_2, 'orientation': 'h'},
            {'y': ['Turnovers'], 'x': team_stats[team_stats['Nickname'] == team_1]['Turnovers'], 'type': 'bar',
             'name': team_1, 'orientation': 'h'},
            {'y': ['Turnovers'], 'x': team_stats[team_stats['Nickname'] == team_2]['Turnovers'], 'type': 'bar',
             'name': team_2, 'orientation': 'h'}
        ],
        'layout': {'title': ('Comparison of Major Features')}
    }

############################################################################################################################################################################################################################

if __name__ == '__main__':
    app.run_server(debug = False)