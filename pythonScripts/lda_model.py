import logging, sys, pprint
import gensim
import string
from gensim.corpora import TextCorpus
from gensim.corpora import  MmCorpus
from gensim.corpora import  Dictionary
from gensim import corpora, models, similarities
import pickle
import os
import numpy as np
from gensim import corpora
from nltk import pos_tag
from gensim.models import LdaModel
import pyLDAvis.gensim

#THIS SCRIPT IS INTENDED TO TRAIN LDA MODEL

noun_tags = ['NN','NNS','NNP','NNPS']
def filter_nouns(text):
    '''
    Given an array of texts, return nouns
    All other words are trimmed.
    '''
    text = pos_tag(text)
    text = [word for word,pos in text if pos in noun_tags]
    return text

def filter_text(text):
    '''
    Three preprocessing steps:
    1. Remove punctuations
    2. Filter out only Nouns from text. This is because lda is trained on nouns only.
    3. Filter out words that are only lower case. This is done to get rid of names,etc. since this is court's opinions all names have atleast first letter capital.
    '''
    text = " ".join(text)
    text = "".join(l for l in text if l not in string.punctuation)
    text = text.encode('ascii', 'ignore').decode('ascii').split()
    text = filter_nouns(text)
    text = [word for word in text if word.islower()]
    return text

def load_files():
    '''
    This loads the entire lower court corpus into memory
    '''
    filenames = []
    texts = []
    base_file = '../data/circuit-scbd-mapped-files/'
    count =0

    for root, dirs, files in os.walk('../data/circuit-scbd-mapped-files/', topdown=False):

        for idx,name in enumerate(files):
            if ".p" in name:
                print name
                text = pickle.load(open(os.path.join(base_file,name), "rb" ))
                filtered_text = filter_text(text)
                texts.append(filtered_text)
                filenames.append(name)
                print count
                count = count + 1
                
               
    return np.asarray(filenames), np.asarray(texts)

print 'Starting to load circuit court corpus...'
filenames, texts = load_files()

print 'Starting to create dictonary...'
dictionary = corpora.Dictionary(texts)
print 'UNPRUNED Dictionary contains ' + str(len(dictionary.token2id)) + ' tokens'
dictionary.filter_extremes(no_above=0.8)
print 'After pruning dictionary contains ' + str(len(dictionary.token2id)) + ' tokens'
print 'Saving dictionary..'
dictionary.save('./dictionary.dict')
dictionary = Dictionary.load('dictionary.dict')

max_likelihood = -10000
best_num_topics = -1
num_topics_input = [50,100,200,400]
for num_topics in num_topics_input:
    print 'Training LDA for number of topics as ' + str(num_topics)
    training_size = len(filenames)
    indices = np.random.permutation(training_size)
    split_size = 0.80
    split_idx = int(split_size * training_size)
    training_idx, test_idx = indices[:split_idx], indices[split_idx:]
    training_filenames, test_filenames = filenames[training_idx], filenames[test_idx]
    training_texts, test_texts = texts[training_idx], texts[test_idx]

    print 'Starting to create corpus...'
    my_corpus = [dictionary.doc2bow(text) for text in training_texts]
    tfidf = models.TfidfModel(my_corpus)
    corpus_tfidf = tfidf[my_corpus]

    print 'Starting lda training....'
    #Discussion about evaluation: https://groups.google.com/forum/#!topic/gensim/yJan7QlKr4I
    model = LdaModel(corpus_tfidf, id2word=dictionary, iterations = 500, num_topics=num_topics, update_every=0, passes=2)

    test_corpus = [dictionary.doc2bow(text) for text in test_texts]
    test_corpus_tfidf = tfidf[test_corpus]
    log_likelihood = model.log_perplexity(test_corpus_tfidf)
    print 'Log likelihood in current run ' + str(log_likelihood)
    if(log_likelihood>max_likelihood):
        max_likelihood = log_likelihood
        best_num_topics = num_topics

print 'Completed training!! Best number of topics ' + str(best_num_topics)

my_corpus = [dictionary.doc2bow(text) for text in texts]
corpora.MmCorpus.serialize('./my-corpus.mm', my_corpus)
serialized_corpus = corpora.MmCorpus('my-corpus.mm')
tfidf = models.TfidfModel(serialized_corpus)
corpus_tfidf = tfidf[serialized_corpus]
corpora.MmCorpus.serialize('./tfidf-corpus.mm', corpus_tfidf)
corpus_tfidf = corpora.MmCorpus('tfidf-corpus.mm')
model = LdaModel(corpus_tfidf, id2word=dictionary, iterations = 500, num_topics=best_num_topics, update_every=0, passes=2)

print 'Calculating document topic distribution...'
document_probabilities = model[corpus_tfidf]

print 'Saving script outputs:'

print '1. Best LDA model'
model.save('./best_lda.model')

print '2. Document Topic distributions'
corpora.MmCorpus.serialize('./lda-corpus.mm', document_probabilities)

print '3. Document names'
with open("./data/filenames.out",'wb') as f:
    pickle.dump(filenames,f)

print '4. Word cloud for best topic model'
data = pyLDAvis.gensim.prepare(model, document_probabilities, dictionary)
pyLDAvis.show(data)

print 'Execution completed succesfully!!!'

