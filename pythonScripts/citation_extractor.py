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


citations = pd.DataFrame(citations_dict)


citations_dict['X125RLM003.p']
