from flaskblog import app, db
from flaskblog.models import tweets
from flaskblog.process import create_plot, create_timeseries, create_graph_two, create_word_cloud, sentiment_classifier, create_pie
from flask import render_template, url_for, flash, redirect, request
import csv
import pandas as pd
from datetime import datetime
import urllib.parse



import LuigiFinal_CleanningData
from LuigiFinal_CleanningData import *


# URL to execute pipeline.
@app.route("/pipeline", methods=['GET', 'POST'])
def cron():
    LuigiFinal_CleanningData.luigi_init()
    return "Pipeline Executed"

# Convert csv to dataframe
def Load_Data(file_name):
    data_frame = pd.read_csv(file_name)
    return data_frame


# Fetch data from RDS database
@app.route("/fetch_data", methods=['GET', 'POST'])
def fetch_data():
    from_date = urllib.parse.unquote(request.args['from_date'], encoding='utf-8', errors='replace')
    from_date = from_date + " 00:01"

    to_date = urllib.parse.unquote(request.args['to_date'], encoding='utf-8', errors='replace')
    to_date = to_date + " 23:59"
    tweets_result = db.session.query(tweets).filter(tweets.timestamp>= from_date, tweets.timestamp<= to_date)

    df = pd.DataFrame([(d.id, d.timestamp, d.tweet_text, d.source, d.username, d.location, d.likes, d.party) for d in tweets_result], columns=['id', 'timestamp', 'tweet_text',  'source', 'username', 'location', 'likes', 'party'])

    classified_df = sentiment_classifier(df)
    bar = create_plot(classified_df)
    timeseries = create_timeseries(classified_df)
    bar2 = create_graph_two(classified_df);
    wordcloud = create_word_cloud(classified_df)
    pie = create_pie(df)
    return render_template('tweets.html', title='Tweets display', plot = bar, plot1 = timeseries,plot2 = bar2, wordcloud = wordcloud, pie= pie)


# Home page with date fields
@app.route("/", methods=['GET', 'POST'])
@app.route("/home", methods=['GET', 'POST'])
def home():
    if request.method == 'POST':
        from_date = datetime.strptime(request.form['from'],"%Y-%m-%d")
        from_date = datetime.strftime(from_date, "%#m/%d/%Y")

        to_date = datetime.strptime(request.form['to'],"%Y-%m-%d")
        to_date = datetime.strftime(to_date, "%#m/%d/%Y")
        return  redirect(url_for('fetch_data',from_date = from_date, to_date = to_date))

    return render_template('date_form.html', title='Date Range')
