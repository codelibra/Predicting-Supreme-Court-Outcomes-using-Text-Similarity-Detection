import re
import pickle
import pandas as pd
import os

def get_citations_from_file(filename):
    res = pickle.load(open( filename, "rb" ))
    res = " ".join(res)
    all_citations = set()
    all_citations |= set(re.findall("\d+ F\. Supp\.(?: \dd) \d+",res))
    all_citations |= set(re.findall("\d+ F\.(?:\dd) \d+",res))
    all_citations |= set(re.findall("\d+ U\.S\. \d+",res))
    all_citations |= set(re.findall("\d+ U\.S\.C\. .. \d+",res))
    return all_citations

get_citations_from_file('../data/circuit-scbd-mapped-files/X125RLM003.p')


count = 0
citations_dict  = {}
for root, dirs, files in os.walk('../data/circuit-scbd-mapped-files/', topdown=False):
    for idx,name in enumerate(files):
        if ".p" in name:
            citations_dict[name] = get_citations_from_file(root+name)
        print count
        count = count + 1

total_citations = set()
for key,value in citations_dict.iteritems():
    total_citations |= set(value)


citations_transpose={}
for key,value in citations_dict.iteritems():
    for citation in value:
        if citation not in citations_transpose:
            citations_transpose[citation] = list()
        citations_transpose[citation].append(key)

save_obj(citations_transpose, 'citations_transpose')
save_obj(citations_dict, 'citations_dict')


def save_obj(obj, name ):
    with open('../data/'+ name + '.pkl', 'wb') as f:
        pickle.dump(obj, f, pickle.HIGHEST_PROTOCOL)

def load_obj(name ):
    with open('../data/' + name + '.pkl', 'rb') as f:
        return pickle.load(f)


for key,value in citations_transpose.iteritems():
    print key + " -> "+str(len(value))
