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



pd.options.display.max_rows = 100
pd.options.display.max_columns = 100


# # Create Data folder for further usage


get_ipython().magic(u"run 'text-mapping-circuit-filesystem.ipynb'")


# # Generate tf-idf circuit court data


data = gl.SFrame({'filename':[""], 'text':[""]})
count = 1880
for root, dirs, files in os.walk('circuit-scbd-mapped-files/', topdown=False):
    for idx,name in enumerate(files):
        if ".p" in name:
            res = pickle.load(open( os.path.join(root, name), "rb" ))
            df = gl.SFrame({'filename':[name], 'text':[str(res)]})
            data = data.append(df)
        print str(count) + str(" Done!!")
        count = count + 1
docs = gl.text_analytics.count_words(data['text'])
docs = docs.dict_trim_by_keys(gl.text_analytics.stopwords(), exclude=True)
data['tf_idf'] = gl.text_analytics.tf_idf(docs)



# This is added since the first data element is empty.
data = data[1:]
data.save('data/tf-idf-dataframe')


# ## Save output


data = gl.load_sframe('data/tf-idf-dataframe')
data = data.add_row_number()



def dataframe_to_scipy(x, column_name):
    '''
    Convert a dictionary column of an SFrame into a sparse matrix format where
    each (row_id, column_id, value) triple corresponds to the value of
    x[row_id][column_id], where column_id is a key in the dictionary.

    Example
    >>> sparse_matrix, map_key_to_index = sframe_to_scipy(sframe, column_name)
    '''
    assert x[column_name].dtype() == dict,         'The chosen column must be dict type, representing sparse data.'

    # Create triples of (row_id, feature_id, count).
    # 1. Stack will transform x to have a row for each unique (row, key) pair.
    x = x.stack(column_name, ['feature', 'value'])

    # Map words into integers using a OneHotEncoder feature transformation.
    f = gl.feature_engineering.OneHotEncoder(features=['feature'])
    # 1. Fit the transformer using the above data.
    f.fit(x)
    # 2. The transform takes 'feature' column and adds a new column 'feature_encoding'.
    x = f.transform(x)
    # 3. Get the feature mapping.
    mapping = f['feature_encoding']
    # 4. Get the feature id to use for each key.
    x['feature_id'] = x['encoded_features'].dict_keys().apply(lambda x: x[0])

    # Create numpy arrays that contain the data for the sparse matrix.
    i = np.array(x['id'])
    j = np.array(x['feature_id'])
    v = np.array(x['value'])

    width = x['id'].max() + 1
    height = x['feature_id'].max() + 1
    # Create a sparse matrix.
    mat = csr_matrix((v, (i, j)), shape=(width, height))

    return mat, mapping



tf_idf, map_index_to_word = dataframe_to_scipy(data, 'tf_idf')



from sklearn.preprocessing import normalize
tf_idf = normalize(tf_idf)


# ### Save sparse matrix representation


io.mmwrite("data/tf-idf-sparse-normalized.mtx", tf_idf)



# back to sparse matrix
newm = io.mmread("data/tf-idf-sparse-normalized")
tf_idf = newm.tocsr()



dense = tf_idf.todense()
