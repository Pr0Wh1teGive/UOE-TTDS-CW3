from flask_cors import *
from flask import Flask, request, jsonify
from gevent import pywsgi
import database
from database import *
from engine import *

# app = Flask(__name__)
app = database.app

CORS(app, supports_credentials=True)

@app.route('/')
def hello_world():  # put application's code here
    return 'Hello World!'

@app.route('/searching', methods=['POST'])
def searching():
    # get data from frontend
    backGet = request.get_json()
    print(backGet)

    content = backGet["Search"]
    start = backGet["StartTime"].replace("/", "-")
    end = backGet["EndTime"].replace("/", "-")
    if len(start) == 0:
        start = None
    if len(end) == 0:
        end = None

    source = backGet["Source"]
    if len(source) == 0:
        source = None
    else:
        for i in range(0, len(source)):
            if source[i] == "New York Times":
                source[i] = "nytimes"
            if source[i] == "BBC News":
                source[i] = "bbc"
            if source[i] == "Reuters":
                source[i] = "reuters"

    category = backGet["Category"]
    if len(category) == 0:
        category = None
    print(content)
    print(start)
    print(end)
    print(source)
    print(category)

    searchResult = search(content, start, end, source, category)

    db = DBConnector()
    returnData = db.find_news_by_ids(searchResult)

    # sendFrontend = [
    #     {
    #         "Title": "come back",
    #         "Date": "2021-03-28",
    #         "Source": "CCTV",
    #         "Abstract": "123456678aefsbsf",
    #         "Category": "sports",
    #         "URL": "www.baidu.com"
    #     },
    #     {
    #         "Title": "aaa",
    #         "Date": "2021-03-27",
    #         "Source": "BBC",
    #         "Abstract": "jdsfjahwbkcjiw",
    #         "Category": "health",
    #         "URL": "www.baidu.com"
    #     },
    #     {
    #         "Title": "bbb",
    #         "Date": "2021-03-30",
    #         "Source": "CNN",
    #         "Abstract": "aefwakedwe",
    #         "Category": "sports",
    #         "URL": "www.baidu.com"
    #     },
    #     {
    #         "Title": "bbb",
    #         "Date": "2021-03-30",
    #         "Source": "CNN",
    #         "Abstract": "aefwakedwe",
    #         "Category": "sports",
    #         "URL": "www.baidu.com"
    #     },
    #     {
    #         "Title": "bbb",
    #         "Date": "2021-03-30",
    #         "Source": "CNN",
    #         "Abstract": "aefwakedwe",
    #         "Category": "sports",
    #         "URL": "www.baidu.com"
    #     },
    #     {
    #         "Title": "bbb",
    #         "Date": "2021-03-30",
    #         "Source": "CNN",
    #         "Abstract": "aefwakedwe",
    #         "Category": "sports",
    #         "URL": "www.baidu.com"
    #     },
    #     {
    #         "Title": "bbb",
    #         "Date": "2021-03-30",
    #         "Source": "CNN",
    #         "Abstract": "aefwakedwe",
    #         "Category": "sports",
    #         "URL": "www.baidu.com"
    #     },
    #     {
    #         "Title": "bbb",
    #         "Date": "2021-03-30",
    #         "Source": "CNN",
    #         "Abstract": "aefwakedwe",
    #         "Category": "sports",
    #         "URL": "www.baidu.com"
    #     },
    #     {
    #         "Title": "bbb",
    #         "Date": "2021-03-30",
    #         "Source": "CNN",
    #         "Abstract": "aefwakedwe",
    #         "Category": "sports",
    #         "URL": "www.baidu.com"
    #     },
    #     {
    #         "Title": "bbb",
    #         "Date": "2021-03-30",
    #         "Source": "CNN",
    #         "Abstract": "aefwakedwe",
    #         "Category": "sports",
    #         "URL": "www.baidu.com"
    #     },
    #     {
    #         "Title": "bbb",
    #         "Date": "2021-03-30",
    #         "Source": "CNN",
    #         "Abstract": "aefwakedwe",
    #         "Category": "sports",
    #         "URL": "www.baidu.com"
    #     },
    #     {
    #         "Title": "bbb",
    #         "Date": "2021-03-30",
    #         "Source": "CNN",
    #         "Abstract": "aefwakedwe",
    #         "Category": "sports",
    #         "URL": "www.baidu.com"
    #     },
    #     {
    #         "Title": "bbb",
    #         "Date": "2021-03-30",
    #         "Source": "CNN",
    #         "Abstract": "aefwakedwe",
    #         "Category": "sports",
    #         "URL": "www.baidu.com"
    #     }
    # ]
    #
    # noResult = []
    # Title:title, Date:date, Source:source, Abstract:abstract, Category:category, URL:url
    return jsonify(returnData)

if __name__ == '__main__':
    # serve(app, host="127.0.0.1", port=5000)
    # app.run()
    server = pywsgi.WSGIServer(('0.0.0.0', 5000), app)
    server.serve_forever()
