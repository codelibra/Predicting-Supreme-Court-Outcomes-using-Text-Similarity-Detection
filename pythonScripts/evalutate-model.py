import logging, sys, pprint
import gensim
logging.basicConfig(filename='/Users/shiv/.bin/10_scotus/pythonScripts/lda_model.log', format='%(asctime)s : %(levelname)s : %(message)s', level=logging.DEBUG)
from gensim.corpora import TextCorpus
from gensim.corpora import  MmCorpus
from gensim.corpora import  Dictionary
from gensim import corpora, models, similarities
from nltk.corpus import stopwords
import pickle
import os
from gensim import corpora
import pandas as pd
import string
from nltk import pos_tag
import matplotlib.pyplot as plt

plt.axis([0, 4500, 0, 100])
plt.ion()

sc_lc = pd.read_csv('../data/sc_lc.csv')
lda_corpus = corpora.MmCorpus('../data/best_lda/lda-corpus.mm')
index_lda = similarities.MatrixSimilarity(lda_corpus)
lda = models.LdaModel.load("../data/best_lda/best_lda.model")
dictionary =  Dictionary.load('../data/best_lda/dictionary.dict')

tf_idf = corpora.MmCorpus('../data/best_lda/tfidf-corpus.mm')



x = list()
y = list()

with open ('../data/best_lda/filenames.out', 'rb') as fp:
    all_file_names = pickle.load(fp)
all_file_names = np.asarray(all_file_names)

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




def get_overall_score_lda():
    global x
    global y
    correct = 0
    incorrect = 0
    nearest_neighbour_data = {}

    for idx,element in enumerate(lda_corpus):
        sims = index_lda[element]
        sims = sorted(enumerate(sims), key=lambda item: -item[1])
        cases = []
        # excluding 0th since it will be the query doc itself
        for f,score in sims[1:12]:
            cases.append(all_file_names[f])

        df,predicted_outcome = get_compare_case_outcomes(cases)
        actual_outcome = get_file_outcome(all_file_names[idx])

        if actual_outcome == predicted_outcome:
            correct = correct + 1
            print "Correct!"
        else:
            incorrect = incorrect + 1

        nearest_neighbour_data[idx] = {'query_file': all_file_names[idx],
                                       'similar_cases': cases,
                                       'similar_case_outcomes' : df,
                                       'correct':correct,
                                       'incorrect':incorrect
                                      }
        accuracy = (float(correct)*100)/float(idx+1)
        x.append(idx)
        y.append(accuracy)
        print str(idx) + " "+ str(correct) + " " + str(incorrect) + " " + str(accuracy)
        if idx==20:
            break
    return correct, incorrect, nearest_neighbour_data


overall_correct, overall_incorrect, nearest_neighbour_data = get_overall_score_lda()
accuracy = float(overall_correct)/float(overall_incorrect+overall_correct)
print accuracy*100
plt.scatter(x, y)
plt.show()

idx = 8
sims = index_lda[lda_corpus[idx]]
sims = sorted(enumerate(sims), key=lambda item: -item[1])
cases = []
for f,score in sims[1:11]:
    cases.append(all_file_names[f])


df,predicted_outcome = get_compare_case_outcomes(cases)
actual_outcome = get_file_outcome(all_file_names[idx])

predicted_outcome
actual_outcome
print all_file_names[1216]
df

sims

lda_corpus[1216]

lda.show_topics([100])
