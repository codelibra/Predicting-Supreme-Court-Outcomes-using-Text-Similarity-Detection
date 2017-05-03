
sc_lc = pd.read_csv('../data/sc_lc.csv')


# # Case similarity approach
# ### Algorithms
# Using lsi model and 10 nearest neighbour search
#
index_lsi = similarities.MatrixSimilarity(lsi[corpus_tfidf])
index_lda = similarities.MatrixSimilarity(lsi[corpus_tfidf])


def get_file_outcome(file):
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
        case_outcome = get_file_outcome(case)
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



def get_overall_score_lsi():
    correct = 0
    incorrect = 0
    nearest_neighbour_data = {}
    for root, dirs, files in os.walk('../data/circuit-scbd-mapped-files/', topdown=False):
        for idx,name in enumerate(files):
            if ".p" in name:
                res = pickle.load(open(os.path.join(root, name), "rb" ))
                res = " ".join(res).lower()
                res = "".join(l for l in res if l not in string.punctuation)
                res = res.encode('ascii', 'ignore').decode('ascii').split()
                res = [word for word in res if word not in stopwords.words('english')]
                res = [word for word in res if len(word)>3 ]
                vec_bow = dictionary.doc2bow(res)
                vec_tf_idf = tfidf[vec_bow]
                vec_lsi = lsi_model[vec_tf_idf] # convert the query to LSI space
                sims = index_lsi[vec_lsi]
                sims = sorted(enumerate(sims), key=lambda item: -item[1])
                cases = []
                # excluding 0th since it will be the query doc itself
                for f,score in sims[1:11]:
                    cases.append(all_file_names[f])
                df,predicted_outcome = get_compare_case_outcomes(cases)

                actual_outcome = get_file_outcome(name)

                if actual_outcome == predicted_outcome:
                    correct = correct + 1
                else:
                    incorrect = incorrect + 1

                nearest_neighbour_data[idx] = {'query_file': name,
                                               'similar_cases': cases,
                                               'similar_case_outcomes' : df,
                                               'correct':correct,
                                               'incorrect':incorrect
                                              }
                accuracy = (float(correct)*100)/float(incorrect+correct)
                print str(idx) + " "+ str(correct) + " " + str(incorrect) + " " + str(accuracy)

    return correct, incorrect, nearest_neighbour_data


overall_correct, overall_incorrect, nearest_neighbour_data = get_overall_score_lsi()
accuracy = float(overall_correct)/float(overall_incorrect+overall_correct)


print accuracy*100



def get_overall_score_lda():
    correct = 0
    incorrect = 0
    nearest_neighbour_data = {}
    for root, dirs, files in os.walk('../data/circuit-scbd-mapped-files/', topdown=False):
        for idx,name in enumerate(files):
            if ".p" in name:
                res = pickle.load(open(os.path.join(root, name), "rb" ))
                res = " ".join(res).lower()
                res = "".join(l for l in res if l not in string.punctuation)
                res = res.encode('ascii', 'ignore').decode('ascii').split()
                res = [word for word in res if word not in stopwords.words('english')]
                res = [word for word in res if len(word)>3 ]
                vec_bow = dictionary.doc2bow(res)
                vec_tf_idf = tfidf[vec_bow]
                vec_lda = lda[vec_tf_idf] # convert the query to LSI space
                sims = index_lda[vec_lda]
                sims = sorted(enumerate(sims), key=lambda item: -item[1])
                cases = []
                # excluding 0th since it will be the query doc itself
                for f,score in sims[1:11]:
                    cases.append(all_file_names[f])
                df,predicted_outcome = get_compare_case_outcomes(cases)

                actual_outcome = get_file_outcome(name)

                if actual_outcome == predicted_outcome:
                    correct = correct + 1
                else:
                    incorrect = incorrect + 1

                nearest_neighbour_data[idx] = {'query_file': name,
                                               'similar_cases': cases,
                                               'similar_case_outcomes' : df,
                                               'correct':correct,
                                               'incorrect':incorrect
                                              }
                accuracy = (float(correct)*100)/float(incorrect+correct)
                print str(idx) + " "+ str(correct) + " " + str(incorrect) + " " + str(accuracy)

    return correct, incorrect, nearest_neighbour_data


overall_correct, overall_incorrect, nearest_neighbour_data = get_overall_score_lda()
accuracy = float(overall_correct)/float(overall_incorrect+overall_correct)


print accuracy*100
