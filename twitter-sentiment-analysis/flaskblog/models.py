from datetime import datetime
from flaskblog import db

class tweets(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    tweet_id = db.Column(db.String(45))
    timestamp = db.Column(db.String(45))
    tweet_text = db.Column(db.String(150))
    source = db.Column(db.String(45))
    username = db.Column(db.String(45))
    location = db.Column(db.String(45))
    likes = db.Column(db.BIGINT)
    party = db.Column(db.String(45))


    def __repr__(self):
        return "classifiedtweets('{self.id}', '{self.tweet_id}', '{self.timestamp}', '{self.tweet_text}', '{self.source}', , '{self.username}'), '{self.location}', '{self.likes}', '{self.party}'"
    # timestamp = db.Column(db.String(50))
    # id = db.Column(db.BIGINT, primary_key=True)
    # tweet_text = db.Column(db.String(40))
    # username = db.Column(db.String(40))
    # followers_count = db.Column(db.Integer)
    # favorite_count = db.Column(db.Integer)
    # location = db.Column(db.String(40))
    #
    # def __repr__(self):
    #     return "Tweets('{self.timestamp}', '{self.id}'), '{self.tweet_text}'), '{self.username}'), '{self.followers_count}'), '{self.favorite_count}'), '{self.location}')"


class classifiedtweets(db.Model):
    timestamp = db.Column(db.String(50))
    id = db.Column(db.BIGINT, primary_key=True)
    tweet_text = db.Column(db.String(150))
    tweet_id = db.Column(db.String(45))
    likes = db.Column(db.BIGINT)
    retweets = db.Column(db.BIGINT)
    replies = db.Column(db.BIGINT)
    party = db.Column(db.String(40))
    mood = db.Column(db.String(45))
    url = db.Column(db.String(150))

    def __repr__(self):
        return "classifiedtweets('{self.timestamp}', '{self.id}', '{self.tweet_text}', '{self.tweet_id}', '{self.likes}', '{self.retweets}', '{self.replies}', '{self.party}', '{self.mood}', '{self.url}','{self.polarity}', '{self.compound_score}')"