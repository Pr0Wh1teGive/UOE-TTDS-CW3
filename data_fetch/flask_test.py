import os
import json

from flask import Flask
from flask_sqlalchemy import SQLAlchemy

app = Flask(__name__)


host = '127.0.0.1'
port = 3306
username = 'root'
password = 'gatewayttds'
db = 'TTDS'
connect_str = 'mysql+pymysql://{}:{}@{}:{}/{}'.format(username, password, host, port, db)
# app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql+pymysql://root:mysql@127.0.0.1:3306/test5'
app.config['SQLALCHEMY_DATABASE_URI'] = connect_str
db = SQLAlchemy(app)

class News(db.Model):
    __tablename__ = 'test_2'
    id = db.Column(db.Integer, primary_key=True)
    date = db.Column(db.DATE)
    title = db.Column(db.String(250))
    author = db.Column(db.String(20), nullable=True)

db.create_all()
list = []
list.append(News(date="2022-03-13", title="-----"))
list.append(News(date="2019-03-13", title="!!!!!!", author=""))
list.append(News(date="2019-03-13", title="!!!!!!", author="Kuangdi"))
db.session.add_all(list)
db.session.commit()
