import plotly
import plotly.graph_objs as go

import pandas as pd
import numpy as np
import json
import random

import dateutil
from datetime import datetime
from wordcloud import WordCloud, STOPWORDS

from sklearn.externals import joblib


def sentiment_classifier(df):
    nb_spam_model = open('naive_bayes.pkl','rb')
    clf = joblib.load(nb_spam_model)
    mood = []
    for tweet in df['tweet_text']:
        tweet_mood = clf.predict([tweet])
        mood.append(tweet_mood[0])
        tweet_mood = ''
    df['mood'] = mood
    return df

def create_plot(df):
    df_new = df[df.mood != 'neutral']
    count = df_new['mood'].count()
    yScale = np.linspace(0, 100, count)

    data = [dict(
        type = 'bar',
        x = df_new['mood'],
        y = yScale,
        fillcolor = 'rgb(224, 102, 102)',
        transforms = [dict(
            type = 'aggregate',
            groups = df_new['mood'],
            aggregations = [dict(target = 'y', func = 'count', enabled = True)]
            )]
    )]

    graphJSON = json.dumps(data, cls=plotly.utils.PlotlyJSONEncoder)

    return graphJSON

def create_pie(df):

    data = go.Pie(
        values=df['likes'],
        labels=df['party'],
    )

    layout = go.Layout({
            "title": "Popularity of parties based on likes",
            "grid": {"rows": 1, "columns": 2},
        })
    fig = go.Figure(data=[data], layout=layout)

    graphJSON = json.dumps(fig, cls=plotly.utils.PlotlyJSONEncoder)

    return graphJSON

# Generating timeseries graph
def create_timeseries(df):
    df['timestamp'] = df['timestamp'].apply(dateutil.parser.parse)
    date_list = []
    for times in df['timestamp']:
        date = datetime.date(times)
        date_list.append(str(date))
        date = ''
    df['date'] = date_list
    df['dedup_mood'] = df['mood']
    new_df = df.groupby(['date', 'party', 'mood'], as_index=False).agg({"dedup_mood": "count"}).reset_index()

    positive_moods = ['happiness', 'faith', 'support']
    negative_moods = ['anger', 'dislike', 'fear', 'sadness', 'jealous']

    bjp_positive_df = new_df[new_df.party == 'BJP'][new_df.mood.isin(positive_moods)]
    congress_positive_df = new_df[new_df.party == 'Congress'][new_df.mood.isin(positive_moods)]
    bjp_negative_df = new_df[new_df.party == 'BJP'][new_df.mood.isin(negative_moods)]
    congress_negative_df = new_df[new_df.party == 'Congress'][new_df.mood.isin(negative_moods)]

    bjp_positive_mood = dict(
        type='scatter',
        x=bjp_positive_df['date'],
        y=bjp_positive_df['dedup_mood'],
        mode='line + markers',
        name='BJP positive mood',
        transforms=[dict(
            type='aggregate',
            groups=bjp_positive_df['date'],
            aggregations=[dict(target='y', func='sum', enabled=True)]
        )]
    )

    bjp_negative_mood = dict(
        type='scatter',
        x=bjp_negative_df['date'],
        y=bjp_negative_df['dedup_mood'],
        mode='line + markers',
        name='BJP negative mood',
        transforms=[dict(
            type='aggregate',
            groups=bjp_negative_df['date'],
            aggregations=[dict(target='y', func='sum', enabled=True)]
        )]
    )

    congress_positive_mood = dict(
        type='scatter',
        x=congress_positive_df['date'],
        y=congress_positive_df['dedup_mood'],
        mode='line + markers',
        name='Congress positive mood',
        transforms=[dict(
            type='aggregate',
            groups=congress_positive_df['date'],
            aggregations=[dict(target='y', func='sum', enabled=True)]
        )]
    )

    congress_negative_mood = dict(
        type='scatter',
        x=congress_negative_df['date'],
        y=congress_negative_df['dedup_mood'],
        mode='line + markers',
        name='Congress negative mood',
        transforms=[dict(
            type='aggregate',
            groups=congress_negative_df['date'],
            aggregations=[dict(target='y', func='sum', enabled=True)]
        )]
    )
    data = [bjp_positive_mood, bjp_negative_mood, congress_positive_mood, congress_negative_mood]

    updatemenus = list([
        dict(active=-1,
             buttons=list([
                 dict(label='Positive',
                      method='update',
                      args=[{'visible': [True, False, True, False]},
                            {'title': 'Positive'}]),
                 dict(label='Negative',
                      method='update',
                      args=[{'visible': [False, True, False, True]},
                            {'title': 'Negative'}]),
             ]),
             )
    ])

    layout = dict(showlegend=True, updatemenus=updatemenus)

    # fig = go.Figure(data=[data], layout=layout)
    graphJSON = json.dumps(data, cls=plotly.utils.PlotlyJSONEncoder)

    return graphJSON

# Generating graph for BJP and Congress Mood distribution
def create_graph_two(df):
    bjp_df = df[df.party == 'BJP']
    congress_df = df[df.party == 'Congress']

    count = congress_df['mood'].count()
    yScale = np.linspace(0, 100, count)

    bjp_mood = dict(
        type = 'bar',
        x = bjp_df['mood'],
        y = yScale,
        name = 'BJP',
    )

    congress_mood = dict(
        type = 'bar',
        x = congress_df['mood'],
        y = yScale,
        name = 'Congress',
    )

    data = [bjp_mood,congress_mood]

    # fig = go.Figure(data=data)

    graphJSON = json.dumps(data, cls=plotly.utils.PlotlyJSONEncoder)

    return graphJSON

# Word cloud
def create_word_cloud(df):
    # Reference : https://community.plot.ly/t/wordcloud-in-dash/11407/16
    # words = df.tweet_text.values
    words = ' '.join(df.tweet_text.values)
    # print(words)
    fig = plotly_wordcloud(words)

    graphJSON = json.dumps(fig, cls=plotly.utils.PlotlyJSONEncoder)

    return graphJSON


def plotly_wordcloud(text):
    wc = WordCloud(stopwords=set(STOPWORDS),
                   max_font_size=10)
    wc.generate(text)

    word_list = []
    freq_list = []
    fontsize_list = []
    position_list = []
    orientation_list = []
    color_list = []

    for (word, freq), fontsize, position, orientation, color in wc.layout_:
        word_list.append(word)
        freq_list.append(freq)
        fontsize_list.append(fontsize)
        position_list.append(position)
        orientation_list.append(orientation)
        color_list.append(color)

    # get the positions
    x = []
    y = []
    for i in position_list:
        # print(i[1])
        if(i[0]>100):
            x.append(i[0]-100)
        elif(i[0]>50):
                x.append(i[0] - 30)
        else:
            x.append(i[0])
        y.append(i[1])

    # get the relative occurence frequencies
    new_freq_list = []
    for i in freq_list:
        new_freq_list.append(i * 100)
    new_freq_list

    lenth = len(word_list)
    trace = go.Scatter(
                       x=y,
                       y=x,
                       textfont=dict(size=new_freq_list,color=color_list),
                       hoverinfo='text',
                       hovertext=['{0} {1}'.format(w, f) for w, f in zip(word_list, freq_list)],
                       mode="text",
                       text=word_list
                       )

    layout = go.Layout(
        xaxis=dict(showgrid=False,
                   showticklabels=False,
                   zeroline=False,
                   automargin=True),
        yaxis=dict(showgrid=False,
                   showticklabels=False,
                   zeroline=False,
                   automargin=True)
    )

    fig = go.Figure(data=[trace], layout=layout)

    return fig