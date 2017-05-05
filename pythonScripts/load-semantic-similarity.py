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
all_file_names = []
for root, dirs, files in os.walk('../data/circuit-scbd-mapped-files/', topdown=False):
    for idx,name in enumerate(files):
        if ".p" in name:
            all_files.append(root+name)



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
            all_file_names.append(name)
            print count
            count = count + 1


dictionary = corpora.Dictionary(texts)
dictionary.save('../data/lsi-dictionary.dict')  # store the dictionary, for future reference
#dictionary.load('../best_lda/dictionary.dict')  # store the dictionary, for future reference



my_corpus = [dictionary.doc2bow(text) for text in texts]
corpora.MmCorpus.serialize('../data/lsi-corpus.mm', my_corpus)

tfidf = models.TfidfModel(my_corpus)
corpus_tfidf = tfidf[my_corpus]


lda = models.LdaModel(corpus_tfidf, id2word=dictionary, num_topics=50)
corpus_lda = lda[corpus_tfidf]
lda.print_topics()

lsi_model = models.LsiModel(corpus_tfidf, id2word=dictionary, num_topics=100)
corpus_lsi_model = lsi_model[corpus_tfidf]
lsi_model.print_topics()

index_lsi = similarities.MatrixSimilarity(lsi_model[corpus_tfidf])
index_lda = similarities.MatrixSimilarity(lda[corpus])

#----------- Testing the results of a single document
res = pickle.load(open("/Users/shiv/.bin/10_scotus/data/circuit-scbd-mapped-files/X4AF96.p", "rb" ))
res = " ".join(res).lower()
res = "".join(l for l in res if l not in string.punctuation)
res = res.encode('ascii', 'ignore').decode('ascii').split()
res = [word for word in res if word not in stopwords.words('english')]
res = [word for word in res if len(word)>3 ]

vec_bow = dictionary.doc2bow(res)
vec_tf_idf = tfidf[vec_bow]
vec_lsi = lsi_model[vec_tf_idf] # convert the query to LSI space
vec_lda = lda[vec_tf_idf] # convert the query to LSI space

sims = index_lsi[vec_lsi]
# top 10 similar documents
sims_lsi = sorted(enumerate(sims), key=lambda item: -item[1])
sims_lsi[0:10]




sims = index_lda[vec_lda]
# top 10 similar documents
sims_lda = sorted(enumerate(sims), key=lambda item: -item[1])
sims_lda[0:10]





texts[403]

cases = []
for key,val in sims_lda[0:10]:
    print key
    cases.append(all_files[key])
cases


for key,val in sims_lsi[0:10]:
    print key
    cases.append(all_files[key])
cases
