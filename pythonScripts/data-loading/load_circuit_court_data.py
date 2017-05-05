'''
This file creates complete_data file which contains all circuit court filenames and their corresponding text
'''
import pandas as pd
import BeautifulSoup as bs
import os
import graphlab as gl
from scipy.sparse import csr_matrix
from sklearn.metrics.pairwise import cosine_similarity
from scipy import io
import numpy as np
import math
from numpy import inf
import pickle
from os.path import dirname
from sklearn.preprocessing import normalize
from nltk.stem.snowball import SnowballStemmer
import string


pd.options.display.max_rows = 100
pd.options.display.max_columns = 100

#get_ipython().magic(u"run 'text-mapping-circuit-filesystem.ipynb'")

## If this file exists then we can directly load into dataframe
if(os.path.exists('../data/complete_data.csv')):
    data = pd.read_csv('../data/complete_data.csv')
else:
    ## We are using graphlab to create the 'complete_dat.csv' file
    # # Generate tf-idf circuit court data
    stemmer = SnowballStemmer("english")
    data = gl.SFrame({'filename':[""], 'text':[""]})
    count = 0
    for root, dirs, files in os.walk('../data/circuit-scbd-mapped-files/', topdown=False):
    for idx,name in enumerate(files):
        if ".p" in name:
            res = pickle.load(open( os.path.join(root, name), "rb" ))
            res = " ".join(res)
            res = " ".join([stemmer.stem(word) for word in res.split(" ")])
            res = "".join(l for l in res if l not in string.punctuation)
            res = res.encode('ascii', 'ignore').decode('ascii')
            df = gl.SFrame({'filename':[name], 'text':[str(res)]})
            data = data.append(df)
        print str(count) + str(" Done!!")
        count = count + 1

    docs = gl.text_analytics.count_words(data['text'])
    docs = docs.dict_trim_by_keys(gl.text_analytics.stopwords(), exclude=True)
    data['tf_idf'] = gl.text_analytics.tf_idf(docs)

    # This is added since the first data element is empty.
    data = data[1:]
    data = data.add_row_number()
    data.save('../data/complete_data.csv')
