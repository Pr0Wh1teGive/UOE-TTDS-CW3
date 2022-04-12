# In this script, all support functions are defined.
# The overall search function
from preprocessing import *
import numpy as np


def search_content(content, tokens, index_pos):
    # Split the content to deal with long query
    phrases = []
    absolute = []
    if "\"" in content:
        index = [i for i, ltr in enumerate(content) if ltr == "\""]
        # Get the index of " mark to identify phrase
        for i in range(int(len(index)/2)):
            phrase = content[int(index[2*i]):int(index[2*i+1])+1]
            if " " in phrase : phrases.append(remove_punction(phrase.lower()))
            else: absolute.append(remove_punction(phrase.lower()))

    normal = [remove_punction(token.lower()) for token in content.split(' ') if remove_punction(token.lower()) in tokens]

    # Phrases is to apply phrase search
    # Absolute is to apply boolean search
    # Tokens is to apply boolean search
    result = {}
    result['phrase'] = {}
    result['absolute'] = {}
    result['normal'] = {}
    result['proximity'] = []

    # Apply phrase search to all "" marked phrases
    if len(phrases) != 0:
        for each in list(set(phrases)):
            result['phrase'][each] = phrase_search(each, index_pos)

    # Apply boolean search to all "" marked word
    if len(absolute) != 0:
        for each in list(set(absolute)):
            result['absolute'][each] = boolean_search(each, index_pos)
    if (len(phrases) != 0) or (len(absolute) != 0):
        def get_ids(dictionary):
            result = []
            for each in dictionary.keys():
                result += dictionary[each]
            return result
        news_ids = []
        news_ids += get_ids(result['phrase'])
        news_ids += get_ids(result['absolute'])
        news_ids = list(set(news_ids))

        def update_index(index_pos, news_ids):
            for vocab in index_pos.keys():
                index_pos[vocab] = [pair for pair in index_pos[vocab] if pair[0] in news_ids]
            return index_pos
        index_pos = update_index(index_pos, news_ids)
    # Apply boolean search to all normal words
    print("BOOLEAN SEARCH START")
    for each in list(set(normal)):
        result['normal'][each] = boolean_search(each, index_pos)

    print("FINISHED BOOLEAN SEARCH")
    # Apply proximity search to the entire search content
    result['proximity'] = proximity_search(content, index_pos)
    print("PROXIMITY SEARCH FINISHED")


    return result
    # return rank(result, index_frq, len(phrases)!=0, len(absolute)!=0)

# Used in phrase_search, proximity_search
def get_positions(pairs, news_id):
    for pair in pairs:
        if pair[0] == news_id:
            return pair[1]

# Used in phrase_search, proximity_search
def find_common_news(res, tmp):
    # [[news_id, pos_string],
    #  [news_id, pos_string], ... ]
    res_id = [pair[0] for pair in res]
    com_id = [pair[0] for pair in tmp if pair[0] in res_id]
    res = [pair for pair in res if pair[0] in com_id]
    tmp = [pair for pair in tmp if pair[0] in com_id]
    return res, tmp, com_id

# Used in phrase_search
def find_continue_pos(pos_res, pos_tmp, i):
    # For each pos in pos_res, check whether pos + i is in pos_tmp
    # Return those matches positions
    pos_res = pos_res.split(';')[:-1]
    pos_tmp = pos_tmp.split(';')[:-1]
    return [pos for pos in pos_res if str(int(pos)+i) in pos_tmp]

# Used in search_content
def phrase_search(phrase, index_pos):
    # To get the document id list containing the phrase
    # '"hello world happy"' to ['hello', 'world', 'happ']
    tokens = preprocess(phrase)
    #       index_pos:{ vocab(String) : [[news_id, pos_string],
    #                                    [news_id, pos_string], ... ]
    #                 }
    # result is the dict in the format: { position in content : [list of IndexPos objects] }
    for i in range(len(tokens)):
        # if the first word -> get the entire index of it
        token = tokens[i]
        if token not in index_pos.keys():
            return []

        if i == 0:
            # [[news_id, pos_string],
            #  [news_id, pos_string], ... ]
            res = index_pos[token]
        # the following words -> check whether it match the current result
        else:
            # [[news_id, pos_string],
            #  [news_id, pos_string], ... ]
            tmp = index_pos[token]
            # update result and tmp based on the common news ids
            res, tmp, com_id = find_common_news(res, tmp)
            # for a certain key : if no matching about pos : remove the key from result
            remove_id = []
            for id in com_id:
                # get the list of continous positions
                # pos_string : '3;5;6;'
                pos_res = get_positions(res, id)
                pos_tmp = get_positions(tmp, id)
                pos = find_continue_pos(pos_res, pos_tmp, i)
                # if no matching : remove the key
                if len(pos) == 0:
                    # mark the current news_id to be removed from result
                    remove_id.append(id)
                else:
                    # Result is updated with the matched new postion index
                    new_pos = ''
                    for each in pos:
                        new_pos+=each
                        new_pos+=';'
                    # new_pos: 3;6;
                    for j in range(len(res)):
                        if res[j][0] == id:
                            res[j][1] = new_pos
            res = [pair[0] for pair in res if pair[0] not in remove_id]
    # Return a list of news_id
    return res

# Used in search_content
def boolean_search(token, index_pos):
    # To get the document id list containing the token
    token = stem_word(token)
    if token not in index_pos.keys():
        return []
    result = [pair[0] for pair in index_pos[token]]
    return result

# Used in proximity_search
def generate_segment(pos, distance):
    pos = pos.split(';')[:-1]
    return [(int(each)-distance, int(each)+distance) for each in pos]

# Used in proximity_search
def update_segment(seg_res, pos_tmp, distance):
    result = []
    for pos in pos_tmp:
        for seg in seg_res:
            if pos in range(seg[0], seg[1]):
                seg_tmp = (pos-distance, pos+distance)
                lower = np.max(seg[0], seg_tmp[0])
                upper = np.lower(seg[1], seg_tmp[1])
                result.append((lower, upper))
    return result

# Used in proximity_search
def find_segment(seg, pos):
    # result : {seg(min, max) : Bool}
    result = {}
    for (min, max) in seg:
        if len([p for p in pos if p in range(min, max)]) != 0:
            result[(min, max)] = True
        else:
            result[(min, max)] = False
    return result

# Used in search_content
def proximity_search(content, index_pos, distance=100, partially_search=False):
    # To get the document id list containing the tokens within a range
    # Apply the proximity search on the entire query:
    
    tokens = list(set(preprocess(content)))
    #       index_pos:{ vocab(String) : [[news_id, pos_string],
    #                                    [news_id, pos_string], ... ]
    #                 }
    
    if not partially_search:
        # similar to the phrase search, we aim to find the segment with
        # the length of distance to contain all tokens
        # Change compared to phrase search : find_continue_pos to 
        # find_common_segment
        seg_res = {}
        for i in range(len(tokens)):
            token = tokens[i]
            if token not in index_pos.keys():
                return []
            if i == 0:
                # [[news_id, pos_string],
                #  [news_id, pos_string], ... ]
                res = index_pos[tokens[i]]

                # { news_id : [segment(lower bound, upper bound)] }
            else:
                # [[news_id, pos_string],
                #  [news_id, pos_string], ... ]
                tmp = index_pos[tokens[i]]
                res, tmp, com_id = find_common_news(res, tmp)

                for id in com_id:
                    seg_res[id] = []
                    # get the list of continous positions
                    pos_res = get_positions(res, id) #1;2;3;4;
                    pos_tmp = get_positions(tmp, id)
                    if len(seg_res[id]) == 0:
                        seg_res[id] = generate_segment(pos_res, distance)
                    else:
                        seg_res[id] = update_segment(seg_res, pos_tmp, distance)
        result = []

        for id in seg_res.keys():
            if len(seg_res[id]) != 0:
                result.append(id)
        # Return a list of news_id
        return result
    else:
        return "ERROR: CANNOT HANDLE PARTIALLY SEARCH FOR PROXIMITY_SEARCH"

def calculate_tdidf(term_count, term_news_count, news_term_count, total_news_count):
    tf = term_count / news_term_count
    idf = np.log( total_news_count / term_news_count )
    return tf * idf

def rank_intitle(result, index):
    # Create a tmp dict for each news_id
    tmp = {}
    # Initialize
    for id in result:
        tmp[id] = 0
    # For each searching content
    for word in index.keys():
        # get the news_id that contains this word in title of news
        intitle_news = [news[0] for news in index[word] if news[1]]
        # Increase the count by 1
        for each in intitle_news:
            tmp[each] += 1
    # Sort the tmp by the intitle count
    tmp = dict(sorted(tmp.items(), key=lambda item: item[1], reverse=True))
    # Get the news_id list and return it
    result_intitle = tmp.keys()
    
    return list(result_intitle)

def rank(result, index, db):
    proximity = result['proximity']
    normal = result['normal']
    # all news_ids
    news_ids = proximity.copy()
    for each in normal.keys():
        news_ids += normal[each]
    news_ids = list(set(news_ids))
    # total related news count
    total_news_count = len(news_ids)
    # news_term_count : {news_id : total terms count in this news}
    # TODO: Use the new table
    # Input [news_id]
    # Output { news_id : len() }
    news_term_counts = db.get_news_length_for_ids(news_ids)
    for each in news_ids:
        if each not in news_term_counts.keys():
            tmp = db.find_news_by_ids([each])
            news_term_counts[each] = len(tmp[0]['content'])
    # news_term_counts = {each['id'] : len(each['content']) for each in db.find_news_by_ids(news_ids)}

    # term_news_count: {term : news count that contains the term}
    term_news_count = {term : len(index[term]) for term in index.keys()}
    # For each term, get the tfidf for them on all news_ids
    scored_proximity = {}
    scored_normal = {}
    # for term in index.keys():
    #     for id in proximity:
    #         tmp = [each[2] for each in index[term] if each[0] == id]
    #         if len(tmp) == 0:
    #             term_count = 0
    #         else:
    #             term_count = tmp[0]
    #         score = calculate_tdidf(term_count, term_news_count[term], news_term_counts[id], total_news_count)
    #         if id not in scored_proximity.keys():
    #             scored_proximity[id] = 0
    #         scored_proximity[id] += score
    #     for id in news_ids:
    #         if id not in proximity:
    #             tmp = [each[2] for each in index[term] if each[0] == id]
    #             if len(tmp) == 0:
    #                 term_count = 0
    #             else:
    #                 term_count = tmp[0]
    #             score = calculate_tdidf(term_count, term_news_count[term], news_term_counts[id], total_news_count)
    #             if id not in scored_normal.keys():
    #                 scored_normal[id] = 0
    #             scored_normal[id] += score

    for term in index.keys():
        for record in index[term]:
            id = record[0]
            term_count = record[2]
            score = calculate_tdidf(term_count, term_news_count[term], news_term_counts[id], total_news_count)
            if id in proximity:
                if id not in scored_proximity.keys() : scored_proximity[id] = 0
                scored_proximity[id] += score
            else:
                if id not in scored_normal.keys() : scored_normal[id] = 0
                scored_normal[id] += score
    # scored_proximity, scored_normal are now in the form : { news_id : a summed score}
    ranked_proximity = list(dict(sorted(scored_proximity.items(), key=lambda item: item[1], reverse=True)).keys())
    ranked_normal = list(dict(sorted(scored_normal.items(), key=lambda item: item[1], reverse=True)).keys())
    # Only return top 200 results
    ranked_combined = (ranked_proximity + ranked_normal)
    result = rank_intitle(ranked_combined,index)
    if len(result) > 501:
        return result[:501]
    return result
