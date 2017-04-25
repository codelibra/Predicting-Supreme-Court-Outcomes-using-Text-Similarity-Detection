import logging, sys, pprint
import gensim
logging.basicConfig(filename='/Users/shiv/.bin/10_scotus/pythonScripts/lda_model.log', format='%(asctime)s : %(levelname)s : %(message)s', level=logging.DEBUG)


### Generating a training/background corpus from your own source of documents
from gensim.corpora import TextCorpus
from gensim.corpora import  MmCorpus
from gensim.corpora import  Dictionary
from gensim import corpora, models, similarities
from nltk.corpus import stopwords
# gensim docs: "Provide a filename or a file-like object as input and TextCorpus will be initialized with a
# dictionary in `self.dictionary`and will support the `iter` corpus method. For other kinds of corpora, you only
# need to override `get_texts` and provide your own implementation."
import pickle
import os
from gensim import corpora

all_files = []
texts = []
count = 0
for root, dirs, files in os.walk('../data/circuit-scbd-mapped-files/', topdown=False):
    for idx,name in enumerate(files):
        if ".p" in name:
            res = pickle.load(open( all_files[count], "rb" ))
            res = " ".join(res).lower()
            res = "".join(l for l in res if l not in string.punctuation)
            res = res.encode('ascii', 'ignore').decode('ascii').split()
            res = [word for word in res if word not in stopwords.words('english')]
            res = [word for word in res if len(word)>3 ]
            texts.append(res)
            all_files.append(name)
            print count
            count = count + 1


dictionary = corpora.Dictionary(texts)
dictionary.save('../data/my-dictionary.dict')  # store the dictionary, for future reference

my_corpus = [dictionary.doc2bow(text) for text in texts]
corpora.MmCorpus.serialize('../data/my-corpus.mm', my_corpus)

tfidf = models.TfidfModel(my_corpus)
corpus_tfidf = tfidf[my_corpus]

lsi = models.LdaModel(corpus_tfidf, id2word=dictionary, num_topics=100)
corpus_lsi = lsi[corpus_tfidf]
lsi.print_topics()






# Testing the results of a single document
res = pickle.load(open("/Users/shiv/.bin/10_scotus/data/circuit-scbd-mapped-files/X4AF96.p", "rb" ))
res = " ".join(res).lower()
res = "".join(l for l in res if l not in string.punctuation)
res = res.encode('ascii', 'ignore').decode('ascii').split()
res = [word for word in res if word not in stopwords.words('english')]
res = [word for word in res if len(word)>3 ]

vec_bow = dictionary.doc2bow(res)
vec_tf_idf = tfidf[vec_bow]
vec_lsi = lsi[vec_tf_idf] # convert the query to LSI space

# generate index for matrix similarity calculation.
index = similarities.MatrixSimilarity(lsi[corpus_tfidf])
sims = index[vec_lsi]
# top 10 similar documents
sims = sorted(enumerate(sims), key=lambda item: -item[1])
sims[0:10]

print(sims) # print sorted (document number, similarity score) 2-tuples

texts[403]

cases = []
for key,val in sims[0:10]:
    print key
    cases.append(all_files[key])
cases



# Generate all_file_names data structure for lsi-nearest-neighbour model
all_file_names = []
for test in all_files:
    all_file_names.append(test.split('/')[-1:])
