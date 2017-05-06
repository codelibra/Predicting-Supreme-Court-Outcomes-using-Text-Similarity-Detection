
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








nearest_neighbour_data = pd.DataFrame(nearest_neighbour_data)
temp = nearest_neighbour_data.transpose()



temp.to_csv('../tempData/neigh.csv')



temp['diff'] = temp['correct'] - temp['incorrect']
sumi = 0
for i, num in enumerate(temp['incorrect']):
    temp['incorrect'].iloc[i] = num - sumi
    sumi = sumi + num


temp


# query X125RLM003.p
# ['X3N2AT.p', 'X3STSL.p', 'X3SVLB.p', 'X40SI8.p', 'X41U2A.p', 'X444UL.p', 'X44CQF.p', 'X44EKO.p']
# ['X3N2AT.p', 'X3STSL.p', 'X40SI8.p', 'X420CQ.p', 'X42GRI.p', 'X44EKO.p', 'X49BDU.p', 'X49G2R.p']



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



my_text = "this is a bad sentence"
import nltk
words = nltk.word_tokenize(my_text)
my_bigrams = nltk.bigrams(words)
my_trigrams = nltk.trigrams(words)

dict(my_bigrams)
bom = pd.read_csv('../data/remove_data_unknown.csv')
bom.shape

sc_lc.shape

bom.shape

len(sc_lc['docket'])




case_data = sc_lc[["year","docket","title", "citation"]]

for col in sc_lc.columns:
    print col


case_data.to_csv('../data/case_ui_data.csv')
case_data.drop_duplicates(inplace=True)



casees = case_data.to_dict()



ans = [ lda.show_topic(x) for x,y in lda_corpus[0]]

ans  = [item for sublist in ans for item in sublist]

ans = [x for x,y in sorted(ans, key=lambda x: x[1], reverse=True)[:3]]

ans


lda.show_topic(38)
