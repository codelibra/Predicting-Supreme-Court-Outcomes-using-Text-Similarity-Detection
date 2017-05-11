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
lda_corpus = corpora.MmCorpus('../data/lda_final/lda-corpus.mm')
with open('../data/lda_final/filenames.out','rb') as f:
    filenames = pickle.load(f)
best_num_topics = 100 #ideally from gridsearchcv

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

def get_file_outcome(file):
    # NOTE: -2 is used since the files were in .p format 2 is length of ".p"
    # If extension changes we need to change this .2
    if len(sc_lc[sc_lc['caseid']==file[:-2]]['case_outcome_disposition'].values) > 0:
        return sc_lc[sc_lc['caseid']==file[:-2]]['case_outcome_disposition'].values[0]
    else:
        print "File not found "+file
        return -1

def get_compare_case_outcomes(cases):
    '''
    TODO: remove the actual case whose neighbour are being considered
    '''
    neighbour_filename_outcome = []
    affirm = 0
    reverse = 0
    outcome = 0
    for idx,case in enumerate(cases):
        case_outcome = get_file_outcome(case)
        if case_outcome == -1:
            continue
        neighbour_filename_outcome.append({'file': case, 'outcome': case_outcome})
        if case_outcome == 1:
            affirm = affirm + 1
        else:
            reverse = reverse + 1

    if affirm>reverse:
        outcome = 1
    else:
        # if number of affirms is same as reverse we predict reverse.
        # this assumption is made making use of scotus-1, where baseline classifier always predicts reverse.
        outcome = 0
    return neighbour_filename_outcome,outcome


feature_weights = {'topic' : 1, 'citations' : 3, 'issue' : 10, 'issueArea' : 5, 'lawSupp': 8}

def calculate_begina_and_end_index():
    weightage_indexes = {}
    for category, weight in feature_weights.iteritems():
        category_first_idx = next(idx for idx,column_name in enumerate(lda_dataframe.columns) if category in column_name)
        category_last_idx = next(idx for idx,column_name in enumerate(reversed(lda_dataframe.columns)) if category in column_name)
        category_last_idx = len(lda_dataframe.columns) - category_last_idx
        weightage_indexes[category] = {}
        weightage_indexes[category]['beginIndex'] = category_first_idx
        weightage_indexes[category]['endIndex'] = category_last_idx
        weightage_indexes[category]['weight'] = weight
    return weightage_indexes

def calculate_cosine_similarity(lda_dataframe, weightage_indexes):
    from sklearn.metrics.pairwise import cosine_similarity
    total_cosine_similarity = np.zeros((lda_dataframe.shape[0],lda_dataframe.shape[0]))


    for category, index_value in weightage_indexes.iteritems():
        total_cosine_similarity += index_value['weight'] * cosine_similarity(lda_dataframe.ix[:,index_value['beginIndex']:index_value['endIndex']],
                          lda_dataframe.ix[:,index_value['beginIndex']:index_value['endIndex']])
    return total_cosine_similarity

x=list()
y=list()

def compute_pairwise_cosine_similarity():
    global x
    global y
    num_files = lda_dataframe.shape[0]
    similarity_matrix = np.zeros((num_files,num_files))
    weightage_indexes = calculate_begina_and_end_index()
    print weightage_indexes
    correct = 0
    incorrect = 0
    nearest_neighbour_data = {}
    similarities = calculate_cosine_similarity(lda_dataframe, weightage_indexes)

    for idx1,row1 in enumerate(lda_dataframe.itertuples()):

        similarity = similarities[5,:]


        cases_indexes = np.array(similarity).argsort()[::-1][1:11]
        cases = all_file_names[cases_indexes]

        df,predicted_outcome = get_compare_case_outcomes(cases)
        actual_outcome = get_file_outcome(all_file_names[idx1])

        if actual_outcome == predicted_outcome:
            correct = correct + 1
        else:
            incorrect = incorrect + 1

        nearest_neighbour_data[idx1] = {
                                       'query_file': all_file_names[idx1],
                                       'similar_cases': cases,
                                       'similar_case_outcomes' : df,
                                       'cosine_similarity' : similarity[cases_indexes]
                                      }
        accuracy = (float(correct)*100)/float(idx1+1)
        x.append(idx1)
        y.append(accuracy)
        print str(idx1) + " "+ str(correct) + " " + str(incorrect) + " " + str(accuracy)

    return correct, incorrect, nearest_neighbour_data


print 'Starting with similarities...'
sm = compute_pairwise_cosine_similarity()
