
# coding: utf-8

# ### This file copies circuit court bloomberg text to folder circuit-scbd-mapped-files which have supreme court case associated.


import pandas as pd
import pickle
import sys
import os


circuit_files = pd.read_csv('../../data/sc_lc.csv', low_memory=False)
circuit_files = circuit_files[circuit_files['case_outcome_disposition']!=-1]

file_availability = {}
count = 0
for file,term in zip(circuit_files['caseid'],circuit_files['term']):
    found = False
    current_term = int(term)
    if file in file_availability:
        continue

    while term-current_term <= 7:
        path =  '../../data/cleaned_Mar_28_python2/' + str(current_term) + '/maj/'+file+"-maj.p"
        if os.path.exists(path):
            found = True
            break
        current_term = current_term - 1

    if found:
        file_availability[file] = current_term
    else:
        file_availability[file] = "Not found"


    try:
        with open(path, "rb") as f:
            w = pickle.load(f)
            pickle.dump(w, open('../../data/circuit-scbd-mapped-files-final/'+file+'.p',"wb"), protocol=2)
    except Exception as e:
        count = count + 1
        print e




print count
