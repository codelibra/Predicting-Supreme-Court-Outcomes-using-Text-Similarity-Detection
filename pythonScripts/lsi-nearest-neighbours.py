
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
index = similarities.MatrixSimilarity(lsi[corpus_tfidf])


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



def get_overall_score_ldi():
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
                vec_lsi = lsi[vec_tf_idf] # convert the query to LSI space
                sims = index[vec_lsi]
                sims = sorted(enumerate(sims), key=lambda item: -item[1])
                cases = []
                for f,score in sims[0:10]:
                    cases.append(all_file_names[f][0])
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


overall_correct, overall_incorrect, nearest_neighbour_data = get_overall_score_ldi()
accuracy = float(overall_correct)/float(overall_incorrect+overall_correct)


print accuracy*100



# Some files are not found, could not download all files post 1975
overall_correct, overall_incorrect, nearest_neighbour_data = get_overall_score_cosine_similarity()
accuracy = float(overall_correct)/float(overall_incorrect+overall_correct)

print accuracy*100
