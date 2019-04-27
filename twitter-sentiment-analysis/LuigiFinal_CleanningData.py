#!/usr/bin/env python
# coding: utf-8

import luigi
from boto.s3.connection import S3Connection
from boto.s3.key import Key
import re
import string 
string.punctuation
import nltk
nltk.download('stopwords')
stopword = nltk.corpus.stopwords.words('english')
import pandas as pd
import csv
import re
from textblob import TextBlob
from zipfile import ZipFile
#import fastText
import sys
import os
import nltk
nltk.download('punkt')
import csv




class accessfile(luigi.Task):
    
    def run(self):
        df = pd.read_csv('training-dataset-final-rites.csv') 
        #print(df)
        df.to_csv(self.output().path,index = False)
        
        print("Task1 completed") 
    
    def output(self):
        return luigi.LocalTarget("training-dataset-final-rites1.csv")

    
    
class cleanningData(luigi.Task):
         
    def requires(self):
        yield accessfile() 
        
    def run(self):
        def lower_tweets(tweets):
            lowertweetlist = []
            for tweet in tweets:
                lowertweetlist.append(tweet.lower())
            return lowertweetlist
        print("run cleaning ")
        df = pd.read_csv(accessfile().output().path)
        df = df.dropna()
        search_congress = ['congress', 'gandhi', 'sonia','rahul', 'Congress','#Congress']
        search_bjp = ['modi', 'BJP', 'narendramodi', 'namo', 'bjp', '#BJP']
        search_both = ['congress', 'bjp']
        search_anti = ['rahulvsmodi', 'congressvsbjp','bjpvscongress']
        party=[]
        for tweet in df['tweet_text'].str.lower():
            if all(x in tweet for x in search_both):
                party.append('Both')
            elif all(x in tweet for x in search_anti):
                party.append('Anti')
            elif any(x in tweet for x in search_congress):
                party.append('Congress')
            elif any(x in tweet for x in search_bjp):
                party.append('BJP')
            else:
                party.append('Others')
        df['party'] = party
        print("before method")

        tweets = df['tweet_text']
        lowertweetlist = lower_tweets(tweets)    
        #lowertweetlist = lower_tweets(tweets)
        def clean_tweets(tweets):
            processed_tweets = [] 
            for tweet in tweets:
                tweet = re.sub(r'((www\.[\S]+)|(https?://[\S]+))', '', tweet) #Remove URLs
                tweet = re.sub(r'\\x[a-zA-Z0-9][a-zA-Z0-9]',r'',tweet) #Remove special texts, eg: \xe8
                tweet = re.sub(r'@[\S]+', '', tweet) #Remove @user mentions
                tweet = re.sub(r'\.{2,}', ' ', tweet) #Remove more than 2 dots with a space
                tweet = re.sub(r'\,', ' ', tweet) #Replace ,  with space
                tweet = tweet.strip(' "\'') #Strip space, " and ' from tweet
                tweet = re.sub(r'\s+', ' ', tweet) #Replace multiple spaces with a single space
                tweet = re.sub(r'[b][\'"]', '', tweet)
                tweet = re.sub(r'\brt\b', '', tweet)
                processed_tweets.append(tweet)
            return processed_tweets
        tweets = df['tweet_text']
        df['tweet_text'] = clean_tweets(tweets)
        #special character 
        bad_chars = ['à', '¤', '¶', "•", "à", "´","¨","±","µ","Ÿ","à","“","¦","¬","š"]
        processed_tweet =[]
        def badCharRemove(tweets):
            for tweet in df['tweet_text']:
                    tweet = re.sub("|".join(bad_chars), " ",tweet)
                    processed_tweet.append(tweet)
            return processed_tweet
        
        tweets = df['tweet_text']
        df['tweet_text'] = badCharRemove(tweets)
        
        # remove non-ASCII-special character 
        def remove_non_ascii(tweet_text):
            return ''.join(i for i in tweet_text if ord(i)<128)
        df['tweet_text'] = df['tweet_text'].apply(remove_non_ascii)
        
        
        def replace_emojis(tweets):
            replace_emojis = [] 
            for tweet in tweets:
        # Smile -- :), : ), :-), (:, ( :, (-:, :')
                tweet = re.sub(r'(:\s?\)|:-\)|\(\s?:|\(-:|:\'\))', ' Smile ', tweet)
        # Laugh -- :D, : D, :-D, xD, x-D, XD, X-D
                tweet = re.sub(r'(:\s?D|:-D|x-?D|X-?D)', ' Laugh ', tweet)
        # Love -- <3, :*
                tweet = re.sub(r'(<3|:\*)', ' Love ', tweet)
        # Wink -- ;-), ;), ;-D, ;D, (;,  (-;
                tweet = re.sub(r'(;-?\)|;-?D|\(-?;)', ' Wink ', tweet)
        # Sad -- :-(, : (, :(, ):, )-:
                tweet = re.sub(r'(:\s?\(|:-\(|\)\s?:|\)-:)', ' Sad ', tweet)
        # Cry -- :,(, :'(, :"(
                tweet = re.sub(r'(:,\(|:\'\(|:"\()', ' Cry ', tweet)
                replace_emojis.append(tweet)
            return replace_emojis
        
        tweets = df['tweet_text']
        df['tweet_text'] = replace_emojis(tweets)
        
        def remove_punct(text):
            text  = "".join([char for char in text if char not in string.punctuation])
            text = re.sub('[0-9]+', '', text)
            return text

        df['tweet_text'] = df['tweet_text'].apply(lambda x: remove_punct(x))
        
        def tokenization(text):
            text = re.split('\W+', text)
            return text

        df['tweet_text'] = df['tweet_text'].apply(lambda x: tokenization(x))
        
        def remove_stopwords(text):
            text = [word for word in text if word not in stopword]
            return text
    
        df['tweet_text'] = df['tweet_text'].apply(lambda x: remove_stopwords(x))
        
        ps = nltk.PorterStemmer()

        def stemming(text):
            text = [ps.stem(word) for word in text]
            return text

        df['tweet_text'] = df['tweet_text'].apply(lambda x: stemming(x))
        
        wn = nltk.WordNetLemmatizer()

        def lemmatizer(text):
            text = [wn.lemmatize(word) for word in text]
            return text

        df['tweet_text'] = df['tweet_text'].apply(lambda x: lemmatizer(x))
        def rejoin_words(row):
            my_list = row['tweet_text']
            joined_words = (" ".join(my_list))
            return joined_words

        df['tweet_text'] = df.apply(rejoin_words, axis=1)
        df["is_duplicate"]= df['tweet_text'].duplicated()
        df = df.drop(df.index[df['is_duplicate'] == True])
        
        #df.to_csv('labelled-train-Luigi.csv', encoding='utf-8', index=False)
        
        df.to_csv(self.output().path,index = False)
        
        #df.to_csv("LuigiDataTry1.csv")
    
        
        
        print("task2 completed ") 
    def output(self):
        return luigi.LocalTarget("labelled-train-Luigi.csv")

class finalClass(luigi.Task):
    def requires(self):
        yield cleanningData()
        
    def run(self):
        df = pd.read_csv(cleanningData().output().path)
        print("Luigi Completed")

def luigi_init():
    print("Luigi start")
    luigi.build([finalClass()], local_scheduler=True)

if __name__ == '__main__':
    # print("Luigi initiated")
    luigi.build([finalClass()], local_scheduler=True)
    # print("Pipeline over")



