
# In[1]:

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


# In[4]:

pd.options.display.max_rows = 100
pd.options.display.max_columns = 100


# # Create Data folder for further usage

# In[2]:

get_ipython().magic(u"run 'text-mapping-circuit-filesystem.ipynb'")


# # Generate tf-idf circuit court data

# In[2]:

data = gl.SFrame({'filename':[""], 'text':[""]})
count = 1880
for root, dirs, files in os.walk('/Users/shiv/Desktop/circuit-scbd-mapped-files/', topdown=False):
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


# In[5]:

# This is added since the first data element is empty.
data = data[1:]
data.save('/Users/shiv/Desktop/data')


# ## Save output

# In[6]:

data = gl.load_sframe('/Users/shiv/Desktop/data')
data = data.add_row_number()


# In[7]:

data


# In[8]:

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


# In[9]:

tf_idf, map_index_to_word = dataframe_to_scipy(data, 'tf_idf')


# In[10]:

from sklearn.preprocessing import normalize
tf_idf = normalize(tf_idf)


# ### Save sparse matrix representation

# In[11]:

io.mmwrite("/Users/shiv/Desktop/tf-idf-sparse-merged", tf_idf)


# In[26]:

# back to sparse matrix
newm = io.mmread("/Users/shiv/Desktop/tf-idf-sparse.mtx")
tf_idf = newm.tocsr()


# In[101]:

dense = tf_idf.todense()


# In[12]:

from sklearn.neighbors import NearestNeighbors
neigh = NearestNeighbors(n_neighbors=10)
neigh.fit(tf_idf)


# In[17]:

neighs = neigh.kneighbors(tf_idf[128], 10, return_distance=False)


# In[18]:

neighs = neighs[0]


# In[20]:

similar_cases = data.filter_by(neighs, 'id')['filename']


# In[21]:

similar_cases


# In[13]:

joined = pd.read_csv('/Users/shiv/.bin/10_scotus/sc_lc.csv')


# In[ ]:

joined


# # Case similarity approach
# ### Algorithms
# 1. Using tf-idf and 10 nearest neighbour search
# 2. Using cosine similarity
#
# ### Steps
# 1. Genearate tf-idf/word vector data for circuit court bloomberg text.
# 2. Map circuit court data to scbd data ie., use only those circuit court texts which were appealed in supreme court.
# 3. Train model based on Nearest neighbour model.
# 4. Predict for all cases.
# 5. Evaluate outcome
#
# ### Evaluation
# 1. Predict for all scbd cases
# 2. Since cases are justice centred, each docket will appear 8-9 times (ie., number of judges). Since *case_outcome_disposition* is same for all, use any of them.
# 3. Take majority vote of 10 nearest neighbour, and take that as predicted output.
# 4. accuracy = number of correct predictoins / total number of cases

# In[18]:

def print_case_outcomes_for_file(file):
    # NOTE: -2 is used since the files were in .p format 2 is length of ".p"
    # If extension changes we need to change this .2
    if len(joined[joined['caseid']==file[:-2]]['case_outcome_disposition'].values) > 0:
        return joined[joined['caseid']==file[:-2]]['case_outcome_disposition'].values[0]
    else:
        print "File not found "+file
        return -1


# In[14]:

def get_compare_case_outcomes(cases):
    d = []
    affirm = 0
    reverse = 0
    outcome = 0
    for idx,case in enumerate(cases):
        case_outcome = print_case_outcomes_for_file(case)
        if case_outcome == -1:
            continue
        d.append({'file': case, 'outcome': case_outcome})
        if case_outcome == 1:
            affirm = affirm + 1
        else:
            reverse = reverse + 1

    if affirm>reverse:
        outcome = 1
    else:
        outcome = 0
    return d,outcome


# In[15]:

def get_overall_score_tf_idf():
    correct = 0
    incorrect = 0
    num = tf_idf.shape[0]
    nearest_neighbour_data = {}
    for idx in range(1,num):
        print idx
        neighs = neigh.kneighbors(tf_idf[idx], 10, return_distance=False)[0]
        similar_cases = data.filter_by(neighs, 'id')['filename']
        df,outcome = get_compare_case_outcomes(similar_cases)
        query_file = data[data['id']==idx]['filename'] [0]
        actual_outcome = print_case_outcomes_for_file(query_file)

        if actual_outcome == outcome:
            correct = correct + 1
        else:
            incorrect = incorrect + 1

        nearest_neighbour_data[idx] = {'query_file': query_file,
                                       'similar_cases': similar_cases,
                                       'similar_case_outcomes' : df,
                                       'correct':correct,
                                       'incorrect':incorrect
                                      }

    return correct, incorrect, nearest_neighbour_data


# In[16]:

def get_overall_score_cosine_similarity():
    def getKey(item):
        return item[0]

    correct = 0
    incorrect = 0
    num = tf_idf.shape[0]
    nearest_neighbour_data = {}
    for idx in range(1,num):
        similarity = cosine_similarity(tf_idf[idx:idx+1], tf_idf)[0]
        indices = range(1,num)
        tuples = zip(similarity,indices)
        tuples = sorted(tuples,reverse=True,key=getKey)

        neighs = list()
        for key,val in tuples[0:10]:
            neighs.append(val)

        similar_cases = data.filter_by(neighs, 'id')['filename']
        df,outcome = get_compare_case_outcomes(similar_cases)
        if outcome == -1:
            continue
        query_file = data[data['id']==idx]['filename'] [0]
        actual_outcome = print_case_outcomes_for_file(query_file)

        if actual_outcome == outcome:
            correct = correct + 1
        else:
            incorrect = incorrect + 1

        nearest_neighbour_data[idx] = {'query_file': query_file,
                                       'similar_cases': similar_cases,
                                       'similar_case_outcomes' : df,
                                       'correct':correct,
                                       'incorrect':incorrect
                                      }

    return correct, incorrect, nearest_neighbour_data


# In[19]:

# Some files are not found, could not download all files post 1975
overall_correct, overall_incorrect, nearest_neighbour_data = get_overall_score_tf_idf()
accuracy = float(overall_correct)/float(overall_incorrect+overall_correct)


# ### Tf-idf model current accuracy

# In[20]:

accuracy


# In[21]:

# Some files are not found, could not download all files post 1975
overall_correct, overall_incorrect, nearest_neighbour_data = get_overall_score_cosine_similarity()


# #### Cosine similarity model current accuracy

# In[3]:

# In order to run cosine similarity dense matrix is requird


# In[ ]:

accuracy = float(overall_correct)/float(overall_incorrect+overall_correct)


# In[ ]:

accuracy


# In[41]:

nearest_neighbour_data = pd.DataFrame(nearest_neighbour_data)


# In[43]:

nearest_neighbour_data.transpose()


# In[ ]:




# In[59]:

f = pd.read_csv('/Users/shiv/.bin/10_scotus/sc_lc_link.csv')


# In[64]:

f


# In[ ]:




# In[ ]:
