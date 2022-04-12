import json
from preprocessing import preprocess, predict, is_english
from database import *
import os


# pipeline
# 1: read file
# 2: News object with category == None
# 3: proprocessing(content) -> predict (save preprocessed version)
# 4: News object update with category
# 5: Upload News object
# 6: Combine preprocessed title with content(saved step 3)
# 7: Create indexes and save locally (Content start from 100)
# 8: Iterate 1000 samples and keep updating indexes (1-7)
# 9: Upload indexes
# 10: Back to 1.
def pipeline(path, id):
    db = DBConnector()
    for root, dirs, files in os.walk(path):
        for name in files:
            if name == 'articles':
                new_path = os.path.join(root, name)
                with open(new_path) as f:
                    data = json.load(f)
                f.close()
                new_records = []
                if data["number"] >> 0:
                    print(new_path)
                    print(data['number'])
                    for i in range(len(data['articles'])):
                        if data['articles'][i]['content'] != None:
                            if is_english(data['articles'][i]['content']):
                                data1 = preprocess(data['articles'][i]['content'])
                                data['articles'][i]['section'] = predict(data1)
                                key = ['date', 'title', 'content', 'category', 'source', 'link']
                                new_record = dict([(k, []) for k in key])
                                if data['articles'][i]['published_date'] == None or data['articles'][i]['title'] == None or data['articles'][i]['link'] == None:
                                    continue
                                else:
                                    new_record['date'] = data['articles'][i]['published_date'][0:10]
                                    new_record['title'] = data['articles'][i]['title']
                                    new_record['content'] = data['articles'][i]['content']
                                    new_record['category'] = int(data['articles'][i]['section'])
                                    new_record['source'] = id
                                    new_record['link'] = data['articles'][i]['link']
                                    new_records.append(new_record)
                print('!!!!!!!!!!!!!!!!!!!!!!!')
                print(new_records)
                db.upload_records(new_records)

    return None


def get_index(start_id, num):
    db = DBConnector()
    doc_list = {}
    data = db.pull_news_batch(start_id, num)
    for doc in data:
        doc_list[doc['id']] = preprocess(doc['title']) + preprocess(doc['content'])
    index = {}
    for key in doc_list.keys():
        document = doc_list[key]
        for i in range(len(document)):
            word = document[i]
            if not word in index.keys():
                index[word] = {}
            if not key in index[word].keys():
                index[word][key] = []
            index[word][key].append(i)
    db.upload_index(index)
    return index