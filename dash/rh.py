import dash
from dash.dependencies import Output, Event, Input
import dash_core_components as dcc
import dash_html_components as html
import plotly
import random
import plotly.graph_objs as go
from collections import deque
import sqlite3
import pandas as pd

from cache import cache
import time
#print...
app = dash.Dash(__name__)
app.layout = html.Div(
    [
        html.H2('Live Twitter Sentiment'),
        dcc.Input(id='sentiment_term', value='twitter', type='text'),
        dcc.Graph(id='live-graph', animate=False),
        dcc.Interval(
            id='graph-update',
            interval=1*1000
        ),
    ]
)

app_colors = {
    'background': '#0C0F0A',
    'text': '#FFFFFF',
    'sentiment-plot':'#41EAD4',
    'volume-bar':'#FBFC74',
    'someothercolor':'#FF206E',
}

@app.callback(Output('live-graph', 'figure'),
              [Input(component_id='sentiment_term', component_property='value')],
              events=[Event('graph-update', 'interval')])
def update_graph_scatter(sentiment_term):
    try:
        conn = sqlite3.connect('twitter.db')
        c = conn.cursor()
        df = pd.read_sql("SELECT * FROM sentiment WHERE tweet LIKE ? ORDER BY unix DESC LIMIT 1000", conn ,params=('%' + sentiment_term + '%',))
        df.sort_values('unix', inplace=True)
        df['date'] = pd.to_datetime(df['unix'],unit='ms')
        df.set_index('date', inplace=True)
        df['sentiment_smoothed'] = df['sentiment'].rolling(int(len(df)/5)).mean()
        df.dropna(inplace=True)
        #df = df.resample('1s').mean() #averaging per second

        
        X = df.index[-100:]
        Y = df.sentiment_smoothed.values[-100:]
    
        data = plotly.graph_objs.Scatter(
                x=list(X),
                y=list(Y),
                name='Scatter',
                mode= 'lines+markers'
                )
    
        return {'data': [data],'layout' : go.Layout(xaxis=dict(range=[min(X),max(X)]),
                                                    yaxis=dict(range=[min(Y),max(Y)]),
                                                    title='Term: {}'.format(sentiment_term))}
    
    except Exception as e:
        with open('errors.txt','a') as f:
            f.write(str(e))
            f.write('\n')


@app.callback(Output('sentiment-pie', 'figure'),
              [Input(component_id='sentiment_term', component_property='value')],
              events=[Event('sentiment-pie-update', 'interval')])
def update_pie_chart(sentiment_term):

    # get data from cache
    for i in range(100):
        sentiment_pie_dict = cache.get('sentiment_shares', sentiment_term)
        if sentiment_pie_dict:
            break
        time.sleep(0.1)

    if not sentiment_pie_dict:
        return None

    labels = ['Positive','Negative']

    try: pos = sentiment_pie_dict[1]
    except: pos = 0

    try: neg = sentiment_pie_dict[-1]
    except: neg = 0

    
    
    values = [pos,neg]
    colors = ['#007F25', '#800000']

    trace = go.Pie(labels=labels, values=values,
                   hoverinfo='label+percent', textinfo='value', 
                   textfont=dict(size=20, color=app_colors['text']),
                   marker=dict(colors=colors, 
                               line=dict(color=app_colors['background'], width=2)))

    return {"data":[trace],'layout' : go.Layout(
                                                  title='Positive vs Negative sentiment for "{}" (longer-term)'.format(sentiment_term),
                                                  font={'color':app_colors['text']},
                                                  plot_bgcolor = app_colors['background'],
                                                  paper_bgcolor = app_colors['background'],
                                                  showlegend=True)}





if __name__ == '__main__':
    app.run_server(debug=True)