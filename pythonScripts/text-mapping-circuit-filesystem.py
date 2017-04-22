
# coding: utf-8

# ### This file copies circuit court bloomberg text to folder circuit-scbd-mapped-files which have supreme court case associated.


import pandas as pd
import pickle
import sys



circuit_files = pd.read_csv('/Users/shiv/.bin/10_scotus/sc_lc_link.csv')



count = 0
for file,term in zip(circuit_files['caseid'],circuit_files['term']):
    path =  '/Users/shiv/Desktop/cleaned_Mar_28_python2/' + str(term) + '/maj/'+file+"-maj.p"
    try:
        with open(path, "rb") as f:
            w = pickle.load(f)
            pickle.dump(w, open('/Users/shiv/Desktop/circuit-scbd-mapped-files/'+file+'.p',"wb"), protocol=2)
    except Exception as e:
        count = count + 1
        print e



print count
