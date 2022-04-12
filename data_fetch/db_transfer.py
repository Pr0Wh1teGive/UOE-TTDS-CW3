import os
import json

from flask import Flask
from flask_sqlalchemy import SQLAlchemy

# EDIT HERE
# one from "bbc" / "nytimes"
from sqlalchemy import UniqueConstraint
from sqlalchemy import exc

news_source = "nytimes"
news_file_root_path = os.path.join("dataset", news_source)
print(news_file_root_path)


# create instance for database connection
app = Flask(__name__)

host = '127.0.0.1'
port = 3306
username = 'root'
password = ''
db = 'TTDS'
connect_str = 'mysql+pymysql://{}:{}@{}:{}/{}?charset=utf8'.format(username, password, host, port, db)
# app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql+pymysql://root:mysql@127.0.0.1:3306/test5'
app.config['SQLALCHEMY_DATABASE_URI'] = connect_str
db = SQLAlchemy(app)


# the table for storing the news articles
class News(db.Model):
    __tablename__ = 'news'
    id = db.Column(db.Integer, primary_key=True)
    date = db.Column(db.DATE)
    title = db.Column(db.String(500))
    content = db.Column(db.TEXT)
    category = db.Column(db.String(50), default=db.null)
    link = db.Column(db.TEXT)
    __table_args__ = (UniqueConstraint('date', 'title', name='unique_title_per_day'),)

# iterate files from one source
news_count = 0
error_count = 0
duplicate_count = 0
max_des = 0
max_title = 0
max_content = 0
max_link = 0

db.create_all()
for path, dir_list, file_list in os.walk(news_file_root_path):
    for file_name in file_list:
        if file_name == "articles":
            with open(os.path.join(path, file_name)) as f:
                json_file = json.load(f)
                print(os.path.join(path, file_name) + " ---- " + str(len(json_file['articles'])) + " files")
                news_count += len(json_file['articles'])
                default_date = path[-8:]
                for article in json_file['articles']:
                    if article['section'] == None:
                        category = db.null
                    else:
                        category = (article['section'].split('&')[0]).lower()
                        category = db.null if category == 'null' else category
                    if article['published_date'] == None:
                        date = default_date
                    else:
                        date_lower = (article['published_date']).lower()
                        date = default_date if (date_lower=='null' or date_lower=='none') else str(article['published_date'])[0:10]
                    new_article = News(
                            date=date,
                            title=article['title'],
                            content=article['description'] + ", " + article['content'],
                            category=category,
                            link=article['link']
                    )
                    max_des = max(max_des, len(article['description']))
                    max_link = max(max_link, len(article['link']))
                    max_title = max(max_title, len(article['title']))
                    try:
                        max_content = max(max_content, len(article['content']))
                        dup = db.session.query(News).filter_by(date=date).filter_by(title=article['title']).first()
                        if not dup:
                            db.session.add(new_article)
                            db.session.commit()
                        else:
                            duplicate_count += 1
                    except exc.SQLAlchemyError as e:
                        error_count += 1
                        print(type(e))
                        db.session.rollback()
                print("--- finished")



print("====== Transfer finished with " + str(news_count) + " news ======")
print(str(error_count) + " error occurs, " + str(duplicate_count) + " duplicates are ignored")
print("max_title: " + str(max_title))
print("max_des: " + str(max_des))
print("max_content: " + str(max_content))
print("max_link: " + str(max_link))