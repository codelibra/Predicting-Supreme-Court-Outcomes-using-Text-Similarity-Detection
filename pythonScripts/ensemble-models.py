# Using bommorito's scotus predict model we are getting the  probability with which each judge predicts a particular value.
# Our model predicts the case outcome not the justice outcome.
# To get the case outcome probability using bommorito's model, we can average the probabilities of all the judges who vote for 1
# That will give us the probability with which we are predicting 1


def affirm_probability(x):
    affirm_count = 0 if 1.0 not in x.value_counts() else  x.value_counts()[1.0]
    reverse_count = 0 if 0.0 not in x.value_counts() else  x.value_counts()[0.0]
    if affirm_count==0 and reverse_count==0:
        print x
        return -1
    return float(float(affirm_count) / (affirm_count+ reverse_count))

affirm_probabilties = pandas.DataFrame(raw_data.groupby('docketId')['rf_predicted'].agg(affirm_probability))
affirm_probabilties.columns = ["affirm_probabilties"]

sc_lc_bomma = sc_lc.join(affirm_probabilties, on="docketId")
sc_lc_bomma.loc[:, "affirm_probabilties"] = sc_lc_bomma


sc_lc_bomma['affirm_probabilties'].value_counts()


sc_lc_bomma.to_csv('../data/sc_lc_with_affirm_bomma_proba.csv')
