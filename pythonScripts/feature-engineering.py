import pandas as pd

# First load data
if(os.path.exists('../data/complete_data.csv')):
    data = pd.read_csv('../data/complete_data.csv')

# Then generate tf-idf
from sklearn.feature_extraction.text import TfidfVectorizer
files = [os.path.join('../data/circuit-scbd-mapped-files/',f) for f in os.listdir('../data/circuit-scbd-mapped-files/')]
model = TfidfVectorizer(ngram_range=(1, 3), min_df=0, stop_words='english')
tf_idf = model.fit_transform(files)

# Then load sc-lc file
sc_lc = pd.read_csv('../data/sc_lc.csv')

def get_case_outcomes_for_file(file):
    # NOTE: -2 is used since the files were in .p format 2 is length of ".p"
    # If extension changes we need to change this .2
    if len(sc_lc[sc_lc['caseid']==file[:-2]]['case_outcome_disposition'].values) > 0:
        return sc_lc[sc_lc['caseid']==file[:-2]]['case_outcome_disposition'].values[0]
    else:
        print "File not found "+file
        return -1


def get_compare_case_outcomes(cases):
    '''
    TODO: remove the actual case whose neighbour are being considered
    '''
    neighbour_filename_outcome = []
    affirm = 0
    reverse = 0
    outcome = 0
    for idx,case in enumerate(cases):
        case_outcome = get_case_outcomes_for_file(case)
        if case_outcome == -1:
            continue
        neighbour_filename_outcome.append({'file': case, 'outcome': case_outcome})
        if case_outcome == 1:
            affirm = affirm + 1
        else:
            reverse = reverse + 1

    if affirm>reverse:
        outcome = 1
    else:
        # if number of affirms is same as reverse we predict reverse.
        # this assumption is made making use of scotus-1, where baseline classifier always predicts reverse.
        outcome = 0
    return neighbour_filename_outcome,outcome

def get_filtered_tf_idf(num_correct=5, num_incorrect=5):
    correct = 0
    incorrect = 0
    num = tf_idf.shape[0]
    nearest_neighbour_data = {}
    for idx in range(1,num):
        # used 11 since one of the files is always the query file itself
        knn_output = neigh.kneighbors(tf_idf[idx], 11)
        neighs = knn_output[1][0][1:]
        distances =  knn_output[0][0][1:]

        file_distance_dict = {}
        for index,n in enumerate(neighs):
            key = data[data['id']==n]['filename'].iloc[0]
            file_distance_dict[key] = distances[index]

        similar_cases = data[data['id'].isin(neighs)]['filename'].tolist()
        df,predicted_outcome = get_compare_case_outcomes(similar_cases)
        query_file = data[data['id']==idx]['filename'].iloc[0]
        actual_outcome = get_case_outcomes_for_file(query_file)

        if actual_outcome == predicted_outcome:
            correct = correct + 1
        else:
            incorrect = incorrect + 1

        nearest_neighbour_data[idx] = {'query_file': query_file,
                                       'similar_cases': similar_cases,
                                       'distances' : file_distance_dict,
                                       'similar_case_outcomes' : df,
                                       'isSuccess':(actual_outcome == predicted_outcome),
                                      }
        # breaking when number of correct/incorrect for analysis is acquired
        if num_correct <= correct and num_incorrect <= incorrect:
            break

    return correct, incorrect, nearest_neighbour_data

from sklearn.neighbors import NearestNeighbors
# we need to tune the number of neighbours
neigh = NearestNeighbors(n_neighbors=11)
neigh.fit(tf_idf)

# This is just to test for 5 nearest neighbours
overall_correct, overall_incorrect, nearest_neighbour_data = get_filtered_tf_idf()
accuracy = float(overall_correct)/float(overall_incorrect+overall_correct)
print accuracy*100
