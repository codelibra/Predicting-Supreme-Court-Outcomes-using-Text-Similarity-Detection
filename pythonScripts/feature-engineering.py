
from sklearn.neighbors import NearestNeighbors
# we need to tune the number of neighbours
neigh = NearestNeighbors(n_neighbors=11)
neigh.fit(tf_idf)


sc_lc = pd.read_csv('../data/sc_lc.csv')


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
            key = str(data[data['id']==n]['filename'][0])
            file_distance_dict[key] = distances[index]

        similar_cases = data.filter_by(neighs, 'id')['filename']
        df,predicted_outcome = get_compare_case_outcomes(similar_cases)
        query_file = data[data['id']==idx]['filename'] [0]
        actual_outcome = get_case_outcomes_for_file(query_file)

        if actual_outcome == predicted_outcome:
            correct = correct + 1
        else:
            incorrect = incorrect + 1

        print str(idx) + " correct: " + str(correct) + "incorrect: " + str(incorrect)
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



overall_correct, overall_incorrect, nearest_neighbour_data = get_filtered_tf_idf()
accuracy = float(overall_correct)/float(overall_incorrect+overall_correct)


print accuracy*100











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
        actual_outcome = get_case_outcomes_for_file(query_file)

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



# Some files are not found, could not download all files post 1975
overall_correct, overall_incorrect, nearest_neighbour_data = get_overall_score_cosine_similarity()
accuracy = float(overall_correct)/float(overall_incorrect+overall_correct)

print accuracy*100
