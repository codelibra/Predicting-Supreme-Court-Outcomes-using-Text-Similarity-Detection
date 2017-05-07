#!/usr/bin/env python
import cgi,cgitb
import json
import sys,getopt
cgitb.enable()

import logging, sys, pprint
import gensim
import string
from gensim.corpora import TextCorpus
from gensim.corpora import  MmCorpus
from gensim.corpora import  Dictionary
from gensim import corpora, models, similarities
import pickle
import os
from gensim import corpora
from nltk import pos_tag
import pandas as pd
import numpy as np
import pyLDAvis.gensim
from gensim.models import LdaModel

similarities = np.load("/Users/shiv/.bin/10_scotus/data/final model d/cosine_similarity.npy")
lda_corpus = corpora.MmCorpus('/Users/shiv/.bin/10_scotus/data/final model d/lda-corpus.mm')
lda = models.LdaModel.load("/Users/shiv/.bin/10_scotus/data/final model d/best_lda.model")
dictionary =  Dictionary.load('/Users/shiv/.bin/10_scotus/data/final model d/dictionary.dict')
tf_idf = corpora.MmCorpus('/Users/shiv/.bin/10_scotus/data/final model d/tfidf-corpus.mm')
case_data = pd.read_csv('/Users/shiv/.bin/10_scotus/data/case_ui_data.csv')

def get_top5_similar_document_indexes(index):
    similarity = similarities[index,:]
    cases_indexes = np.array(similarity).argsort()[::-1][1:6]
    #sims = index_lda[lda_corpus[index]]
    #sims = sorted(enumerate(sims), key=lambda item: -item[1])
    return cases_indexes.tolist()

def get_top_10_words_for_document(index):
    try:
        sorted_tf_idf = sorted(tf_idf[index], key=lambda x: x[1], reverse=True)
        return [dictionary[key] for key,value in sorted_tf_idf[:10]]
    except:
        return "Not found"

def get_word_cloud_data(index):
    docIndexes = get_top5_similar_document_indexes(index)
    return [get_top_10_words_for_document(x) for x in docIndexes], docIndexes

def get_topic_of_document(index):
    best_topics = sorted(lda_corpus[index], key=lambda x: x[1], reverse=True)[:3]
    ans = [ lda.show_topic(x) for x,y in best_topics]
    ans  = [item for sublist in ans for item in sublist]
    ans = [x for x,y in sorted(ans, key=lambda x: x[1], reverse=True)[:3]]
    return ans

def get_all_cases():
    '''
    Json object must have
    1. id of each case
    2. caseName
    3. caseDescription
    4. caseTopics
    5. caseTerm
    '''
    data = {}
    for index, row in case_data.iterrows():
        case = {}
        case['caseName'] = row['title']
        case['caseTopic'] = " ".join(get_topic_of_document(index))
        case['caseDescription'] = " ".join(get_top_10_words_for_document(index))
        case['caseTerm'] = row['year']
        data[index] = case
        if index==100:
            break
    return json.dumps(data)

def get_case_titles(elements):
    return pd.Series(case_data.iloc[elements]['title']).tolist()

def get_similar_case_text(id):
    '''
    Given a particular caseId the function would return text of 5 nearest neighbours.
    '''
    similar_cases = {}
    similar_cases['original'] = " ".join(get_top_10_words_for_document(id))

    word_cloud_data, word_cloud_indexes = get_word_cloud_data(id)
    similar_cases['case1']= " ".join(word_cloud_data[0])
    similar_cases['case2']= " ".join(word_cloud_data[1])
    similar_cases['case3']= " ".join(word_cloud_data[2])
    similar_cases['case4']= " ".join(word_cloud_data[3])
    similar_cases['case5']= " ".join(word_cloud_data[4])

    word_cloud_indexes.insert(0,id)
    similar_cases['caseTitles'] = get_case_titles(word_cloud_indexes)
    return json.dumps(similar_cases)


def main(argv):
    form  = cgi.FieldStorage()
    query = form.getvalue('query')
    caseId = int(form.getvalue('caseId'))
    try:
        opts, args = getopt.getopt(argv,"q:r:")
    except getopt.GetoptError:
        sys.exit()


    for opt, arg in opts:
        if opt in ("-q"):
            query = arg
        else:
            query = -1

        if opt in ("-r"):
            caseId = int(arg)


    print "Content-type: text\n\n"
    if query is not None and len(query)!=0:
        print get_all_cases()
    else:
        print get_similar_case_text(caseId)

if  __name__ =='__main__':
    main(sys.argv[1:])


# what should the script do?
#couple of functions are requrired ,
#get_all_cases() -> must return array of text of all cases
#get_similar_case_text(index) -> must return array of text of current case, similar cases
