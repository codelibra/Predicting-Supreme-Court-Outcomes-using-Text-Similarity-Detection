
# coding: utf-8

# In[2]:

from tqdm import tnrange, tqdm_notebook
from time import sleep

for i in tnrange(10, desc='1st loop'):
    for j in tqdm_notebook(xrange(100), desc='2nd loop'):
        sleep(0.01)


# In[4]:

import os


# In[14]:

for root, dirs, files in os.walk('circuit-scbd-mapped-files/', topdown=False):
    for idx,name in enumerate(tqdm(files)):
        print name
        sleep(10)


data.head()


tf_idf.shape

data.shape

tf_idf_normalise.shape





neighs = neigh.kneighbors(tf_idf[128], 10)

neighs
neighs = neighs[1][0][1:]


similar_cases = data.filter_by(neighs, 'id')['filename']

data[data['id']==128]

print similar_cases



for idx,f in enumerate(similar_cases):
    print similar_cases[idx] +" -> "+ str(get_case_outcomes_for_file(f))


data






nearest_neighbour_data = pd.DataFrame(nearest_neighbour_data)
temp = nearest_neighbour_data.transpose()



temp.to_csv('../tempData/neigh.csv')



temp



print sc_lc[sc_lc['caseid']=='X125RLM003']['term']

print temp[temp['query_file']=='X125RLM003.p']['similar_cases']


# query X125RLM003.p
# results ['X3C7FN.p', 'X3G3UN.p', 'X3N2AT.p', 'X3STSL.p', 'X3SVLB.p', 'X40SI8.p', 'X41U2A.p', 'X444UL.p', 'X44CQF.p', 'X44EKO.p']



def get_tf_idf_for_file(filename):
    import operator
    x = data[data['filename']==filename]['tf_idf'][0]
    sorted_x = sorted(x.items(), key=operator.itemgetter(1),reverse=True)
    return sorted_x


query = get_tf_idf_for_file('X125RLM003.p')
result = get_tf_idf_for_file('X3N2AT.p')

query

result

for word_result, value_result in result:
    for word_query, value_query in query:
        if word_query == word_result:
            print word_query + " " + str(value_query) + " " + str(value_result)
            break
