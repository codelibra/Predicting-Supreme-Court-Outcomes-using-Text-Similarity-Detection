import re
import pickle

def get_citations_from_file(filename):
    res = pickle.load(open( filename, "rb" ))
    res = " ".join(res)
    district_court_pattern = re.findall("\d+ F\. Supp\.( \dd)? \d+",res)
    circuit_court_pattern = re.findall("\d+ F\.(\dd)? \d+",res)
    supreme_court_pattern = re.findall("\d+ U\.S\. \d+",res)
    usc_pattern = re.findall("\d+ U\.S\.C\. .. \d+",res)
    print district_court_pattern,circuit_court_pattern,supreme_court_pattern,usc_pattern
