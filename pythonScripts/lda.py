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

'''
Loading the inputs of this program.
1. Document Topic distribution.
2. Filenames
3. Number of topics(Hardcoded)
'''
print 'Loading input from filesystem... '
print '1. Document Topic distribution.'
print '2. Filenames'
print '3. Number of topics(hard-coded)'
lda_corpus = corpora.MmCorpus('../data/lda-corpus.mm')
with open('../data/filenames.out','rb') as f:
    filenames = pickle.load(f)
best_num_topics = 40 #ideally from gridsearchcv

print 'Input done!!'
input_size = len(filenames)
document_probabilities = np.zeros((input_size,input_size))
for idx1,document_probability in enumerate(lda_corpus):
    for idx2, probability in document_probability:
        document_probabilities[idx1][idx2] = probability

print 'Loading lda dataframe ...'
lda_dict = {}
lda_dict['filename'] = [filename[:-2] for filename in filenames]
for i in range(best_num_topics):
    lda_dict['topic_' + str(i)] = document_probabilities[:,i]
lda_dataframe = pd.DataFrame(lda_dict)

print 'Loading scdb dataframe...'
scdb_dataframe = pd.read_csv('../data/sc_lc.csv')

def one_hot_encode_categories(filename_values_dict, new_column_name):
    from sklearn.preprocessing import MultiLabelBinarizer
    multilabel_binarizer = MultiLabelBinarizer()
    values_per_filename = filename_values_dict.values()
    categories_per_filename = multilabel_binarizer.fit_transform(values_per_filename)
    categories = multilabel_binarizer.classes_

    output_dict = {}
    output_dict['filename'] = filename_values_dict.keys()
    for idx,category in enumerate(categories):
            values_list = categories_per_filename[:,idx]
            if type(category) == 'str':
	            category = category.encode('utf-8')
            output_dict[new_column_name + ' = ' + str(category)] = values_list
    return pd.DataFrame(output_dict)


def extract_filename_and_column_from_scbd(column_name):
     category_per_filename = scdb_dataframe.set_index('caseid')[column_name].to_dict()
     for key, value in category_per_filename.iteritems():
         category_per_filename[key] = [value]
     return category_per_filename


def merge_lda_model(main_dataframe, dataframe):
    files_not_found = main_dataframe[~main_dataframe['filename'].isin(dataframe['filename'])]
    print 'Number of filenames not found ' + str(files_not_found.shape[0])
    print files_not_found['filename']
    merged_dataframe = main_dataframe.merge(dataframe, on='filename', how='left')
    return merged_dataframe

print 'Initial lda columns ' + str(lda_dataframe.shape[1])
print 'Loading citations data...'
valid_citations = pd.read_csv('../data/case_id_citations_merged.csv').columns
citations_dict = pickle.load(open('../data/citations_dict.pkl','rb'))
pruned_citations_dict = {}
count = 0
for key, values in citations_dict.iteritems():
     if key not in pruned_citations_dict.keys():
         key = key[:-2] # removing .p
         files = [value for value in values if value in valid_citations]
         pruned_citations_dict[key] = files
         count = count + 1
citations_dataframe = one_hot_encode_categories(pruned_citations_dict, 'citations')
lda_dataframe = merge_lda_model(lda_dataframe, citations_dataframe)
print 'Lda columns after citations ' + str(lda_dataframe.shape[1])

print 'Merging issues data...'
category_per_filename = extract_filename_and_column_from_scbd('issue')
issues_dataframe = one_hot_encode_categories(category_per_filename,'issue')
del issues_dataframe['issue = nan']
lda_dataframe = merge_lda_model(lda_dataframe, issues_dataframe)
print 'Lda columns after issues ' + str(lda_dataframe.shape[1])

print 'Merging issue area data...'
category_per_filename = extract_filename_and_column_from_scbd('issueArea')
issueArea_dataframe = one_hot_encode_categories(category_per_filename,'issueArea')
del issueArea_dataframe['issueArea = nan']
lda_dataframe = merge_lda_model(lda_dataframe, issueArea_dataframe)
print 'Lda columns after issue area ' + str(lda_dataframe.shape[1])

print 'Merging law supplement data...'
category_per_filename = extract_filename_and_column_from_scbd('lawSupp')
lawSupplement_dataframe = one_hot_encode_categories(category_per_filename,'lawSupp')
del lawSupplement_dataframe['lawSupp = nan']
lda_dataframe = merge_lda_model(lda_dataframe, lawSupplement_dataframe)
print 'Lda columns after law supplement ' + str(lda_dataframe.shape[1])

def calculate_cosine_similarity(row1, row2):
    from sklearn.metrics.pairwise import cosine_similarity
    weightage = {'topic' : 1, 'citations' : 3, 'issue' : 10, 'issueArea' : 5, 'lawSupp': 8}
    total_cosine_similarity = 0
    for category, weight in weightage.iteritems():
        category_first_idx = next(idx for idx,column_name in enumerate(lda_dataframe.columns) if category in column_name)
        category_last_idx = next(idx for idx,column_name in enumerate(reversed(lda_dataframe.columns)) if category in column_name)
        category_last_idx = len(lda_dataframe.columns) - category_last_idx
        #print 'sklearn value'
        #print row1[category_first_idx:category_last_idx]
        #print row2[category_first_idx:category_last_idx]
        #print cosine_similarity(row1[category_first_idx:category_last_idx].reshape(1,-1),row2[category_first_idx:category_last_idx].reshape(1,-1))
        #print 'weight'
        #print weightage[category]
        total_cosine_similarity += weightage[category] * cosine_similarity(row1[category_first_idx:category_last_idx].reshape(1,-1),row2[category_first_idx:category_last_idx].reshape(1,-1))
    print 'total_cosine_similarity ' + str(total_cosine_similarity)
    return total_cosine_similarity

def compute_pairwise_cosine_similarity():
    num_files = lda_dataframe.shape[0]
    similarity_matrix = np.zeros((num_files,num_files))
    for idx1,row1 in enumerate(lda_dataframe.itertuples()):
        row1 = np.asarray(row1[1:])
        print 'pairwise'
        print row1
        for idx2,row2 in enumerate(lda_dataframe.itertuples()):
            if(idx2>idx1):
                print 'computing similarity of ' + str(idx1) + ' ' + str(idx2)
                row2 = np.asarray(row2[1:])
                print row2
                #Now need to calculate cosine distance between row 1 and row 2
                similarity_matrix[idx1][idx2] = calculate_cosine_similarity(row1, row2)
    return similarity_matrix

print 'Starting with similarities...'
sm = compute_pairwise_cosine_similarity()
