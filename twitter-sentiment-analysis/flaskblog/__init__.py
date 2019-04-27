from flask import Flask
from flask_sqlalchemy import SQLAlchemy
import pymysql

app = Flask(__name__)
app.config['SECRET_KEY'] = '5791628bb0b13ce0c676dfde280ba245'
app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql+pymysql://root:1234567aA@newinstance.cbrgfxuqelbo.us-east-2.rds.amazonaws.com:3306/election_sentiment_analysis'
db = SQLAlchemy(app)

# Imported here to avoid circular import error
from flaskblog import routes
