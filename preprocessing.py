# In this script, the data preprocessing is implemented.
# NLP model should be trained and used to predict section
# Based on the title or contect of the news (CW2)

# 1: Take all our data from database
# 2: Removed the label if the occurrence is less than X
# 3: Train a model on the classified data
# 4: Save the params for the model and write a pipeline
# 5: Predict the label for the rest news (prob distribution)
# 6: Select the top 3 if they are above a threshold Y
# # TODO: trained NLP model

# 7: Stemmer needed for index and vocabulary generation.
from langdetect import detect
import os
from nltk.stem.porter import PorterStemmer
import re
import joblib
from sklearn.feature_extraction.text import TfidfVectorizer
import pandas as pd

def predict(content):
    model = joblib.load('./model/model.pkl')
    id_category = dict({0: 'business', 1: 'tech', 2: 'politics', 3: 'sport', 4: 'entertainment'})
    TRAIN_PATH = os.path.join("./input/", "BBC News Train.csv")
    df = pd.read_csv(TRAIN_PATH)
    tfidf = TfidfVectorizer(sublinear_tf=True, min_df=5, norm='l2', encoding='latin-1', ngram_range=(1, 2),
                            stop_words='english')
    tfidf.fit_transform(df.Text).toarray()
    text_features = tfidf.transform(content)
    predictions = model.predict(text_features)
    for predicted in predictions:
        result = format(predicted)
    return result

def stem_word(word):
    porter = PorterStemmer()
    result = porter.stem(word)
    return result

def remove_punction(content):
    tmp = re.sub('-+',' ',content)
    result = re.sub('[^a-zA-Z-\']+',' ',tmp).strip()
    return result

def det(x):
    try:
        lang = detect(x)
    except:
        lang = 'Other'
    return lang

def is_english(content):
    # from langdetect import detect
    result = det(content)
    if result == 'en':
        # detect whether the content is in English
        return True
    else:
        return False

def remove_unicode(content):
    result = content.encode("ascii", "ignore").decode("utf-8")
    return result

def tokenization(content):
    tokens = []
    result = content.split()
    if len(result) != 0:
        tokens += result
    return tokens

def stem_string(content):
    # return stemmed content
    porter = PorterStemmer()
    with open('./input/englishST.txt') as f:
        stops = [each.strip() for each in f.readlines()]
        stops = [re.sub('\'+', '', stop) for stop in stops]
        f.close()
    result = [porter.stem(each.lower()) for each in content if each.lower() not in stops]
    return result

def preprocess(content):
    # entire pipeline
    # call is_english, remove_unicode, stem_string,
    # return stemmed english content without unicode
    tmp = remove_unicode(content)
    tmp = remove_punction(tmp)
    tmp = tokenization(tmp)
    result = stem_string(tmp)
    return result
