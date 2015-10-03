from flask import Flask
from flask.ext.sqlalchemy import SQLAlchemy
from flask.ext.httpauth import HTTPBasicAuth

UPLOAD_FOLDER = 'assets/'

app = Flask(__name__)
app.config.from_object('config')
db = SQLAlchemy(app)
auth = HTTPBasicAuth()
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

from app import views, models