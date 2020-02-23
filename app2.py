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
#import cufflinks as cf #Using cufflinks, a wrapper for easing plotting with pandas and plotly

import dash_daq as daq


external_stylesheets =['https://codepen.io/chriddyp/pen/bWLwgP.css', dbc.themes.BOOTSTRAP]

app = dash.Dash(__name__,external_stylesheets=external_stylesheets)

colors = {
    'background': '#111111',
    'text': '#7FDBFF'
}


# Load Data
player_stats = pd.read_excel('2K Player Stats.xlsx')
team_stats = pd.read_excel('2KL Team Stats.xlsx')

player_stats = player_stats.rename(columns = {"FG%":"FG_pct","FG3%":"FDG3_pct","FT%":"FT_pct","eFG%":"effi_pct","TS%":"Tru_shoot_pct"})
team_stats = team_stats.rename(columns={"FG%":"FG_pct","3P%":"3P_pct","Opp_3P%":"Opp_3P_pct","Opp_FG%":"Opp_FG_pct"})

pysqldf = lambda q: sqldf(q,globals())
q1 = '''
     SELECT Nickname,Points,Offensive_Rebounds,Defensive_Rebounds,Assists,Steals,Turnovers
     FROM team_stats
    '''
main_cats_teams = pysqldf(q1)


q2 = '''
     SELECT Player,OREB,DREB,REB,AST,PF,STL,TOV,BLK,PTS
     FROM player_stats
    '''
main_cats_players = pysqldf(q2)

#teams = team_stats['Nickname'].unique()
teams = main_cats_teams['Nickname'].unique()
players = main_cats_players['Player'].unique()

#team_stat_categories = team_stats.columns.tolist()
team_stat_categories = main_cats_teams.columns.tolist()
player_stat_categories = main_cats_players.columns.tolist()







def build_banner():
    return html.Div(
        id="banner",
        className="banner",
        children=[
            html.Div(
                id="banner-text",
                children=[
                    html.H5("Manufacturing SPC Dashboard"),
                    html.H6("Process Control and Exception Reporting"),
                ],
            ),
            html.Div(
                id="banner-logo",
                children=[
                    html.Button(
                        id="learn-more-button", children="LEARN MORE", n_clicks=0
                    ),
                    html.Img(id="logo"),
                ],
            ),
        ],
    )

def barplt_teams(data,feat):
    
    fig = px.bar(data.sort_values(by=[feat]), x='Nickname', y=str(feat),
                hover_data = ['Nickname'],color = feat,text = feat)
    fig.show()
    

def barplt_players(data,feat):
    data_names= data.columns.tolist()
    data_names.remove(feat)
    
    fig = px.bar(data.sort_values(by=[feat]), x='Player', y=str(feat),
                hover_data= ['Player','Team'],color=feat,text = feat)
    fig.show()


# App Layout
app.layout = html.Div(
    [
        html.Div(
            [
                html.H1('NBA 2K Rankings', style = {'fontSize': 50, 'font-family': 'Open Sans', 'text-transform': 'uppercase', 'font-weight': '800'}, 
                className = 'text-center'),
                
                html.Img(src = '/assets/2k20.png')
            ],
            className = 'banner'
        ),

        dbc.Row(dbc.Col(html.H1("NBA 2K RANKINGS",className= 'text-center')),align="center",),
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
                    value = '76ers GC'
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
                        value = 'Points'
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
                        value = 'STL' 
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
    return {

        'data':[piedata],'layout':{'title':(team_1 +' vs.' + team_2)}


        #'data': [
           #{'x': [stat], 'y': team_stats[team_stats["Nickname"] == team_1][stat], 'type': 'bar', 'name': team_1},
            #{'x': [stat], 'y': team_stats[team_stats["Nickname"] == team_2][stat], 'type': 'bar', 'name': team_2},
        #],
        #'layout': {
            #'title': (team_1 + ' vs. ' + team_2 + ' on ' + stat)
        #}
    }




if __name__ == '__main__':
    app.run_server(debug=True)