# In this sceipt, the flask application is defined and
# all of its functionality is implemented here. 
from flask import Flask,request,render_template,redirect
from transformers import TokenSpan
from support import search_content, rank
from preprocessing import preprocess
from database import *

def search(content, start, end, source, category):
    # get access to database
    db = DBConnector()
    # To get the index tables and vocabulary table
    tokens = preprocess(content)
    index_pos = db.search_index(tokens, index_type="pos", start_date=start, end_date=end, category_list=category, source_list=source)
    index_frq = db.search_index(tokens, index_type="frq", start_date=start, end_date=end, category_list=category, source_list=source)
    tokens = [token for token in tokens if (len(index_pos[token]) != 0)]
    if len(tokens) == 0:
        return []
    index_pos = {token : index_pos[token] for token in tokens}
    index_frq = {token : index_frq[token] for token in tokens}
    result = search_content(content, tokens, index_pos)
    ranked_result = rank(result, index_frq, db)

    return ranked_result