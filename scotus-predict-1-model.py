# Project imports
from model import *

# In[2]:

# Get raw data
raw_data = pd.read_csv('../data/sc_lc.csv')

# Get feature data
feature_df = pd.read_csv('../data/sc_lc_feature.csv').filter(items=['docket',
          'term_raw',
          'term_encoded',
          'natural_court_raw',
          'natural_court_encoded',
          'argument_month_encoded',
          'decision_month_encoded',
          'as_column_vector(decision_delay)',
          'justice_encoded',
          'petitioner_encoded',
          'respondent_encoded',
          'petitioner_group_encoded',
          'respondent_group_encoded',
          'jurisdiction_encoded',
          'admin_action_encoded',
          'case_source_encoded',
          'case_origin_encoded',
          'lc_disagreement_encoded',
          'cert_reason_encoded',
          'lc_outcome_encoded',
          'issue_encoded',
          'issue_area_encoded',
          'law_type_encoded',
          'law_supp_encoded',
          'justice_previous_direction',
          'justice_cumulative_direction',
          'justice_previous_court_direction',
          'justice_cumulative_court_direction',
          'justice_previous_court_direction_diff',
          'justice_cumulative_court_direction_diff',
          'justice_previous_action',
          'justice_cumulative_action',
          'justice_previous_court_action',
          'justice_cumulative_court_action',
          'justice_previous_court_action_diff',
          'justice_cumulative_court_action_diff',
          'justice_previous_agreement',
          'justice_cumulative_agreement',
          'justice_previous_court_agreement',
          'justice_cumulative_court_agreement',
          'justice_previous_court_agreement_diff',
          'justice_cumulative_court_agreement_diff',
          'justice_previous_lc_direction_diff',
          'justice_cumulative_lc_direction_diff'
          ])




# In[3]:

# Output some diagnostics on features
print(raw_data.shape)
print(feature_df.shape)
assert(raw_data.shape[0] == feature_df.shape[0])


# In[4]:

# Output basic quantities for sample
ind = raw_data["justice_outcome_disposition"] == -1
raw_data = raw_data[~ind]
feature_df = feature_df[~ind]
feature_df.drop('docket', inplace=True, axis=1)

print(pandas.DataFrame(raw_data["justice_outcome_disposition"].value_counts()))
print(pandas.DataFrame(raw_data["justice_outcome_disposition"].value_counts(normalize=True)))


# In[5]:

# Setup training time period
min_training_years = 5
term_range = range(raw_data["term"].min() + min_training_years,
                   raw_data["term"].max()+1)

# Setting growing random forest parameters
# Number of trees to grow per term
trees_per_term = 20

# Number of trees to begin with
initial_trees = min_training_years * trees_per_term

# Number of years between "forest fires"
reset_interval = 9999

# Setup model
m = None
term_count = 0

for term in term_range:
    # Diagnostic output
    print("Term: {0}".format(term))
    term_count += 1

    # Setup train and test periods
    train_index = (raw_data.loc[:, "term"] < term).values
    test_index = (raw_data.loc[:, "term"] == term).values

    # Setup train data
    feature_data_train = feature_df.loc[train_index, :]
    target_data_train = raw_data.loc[train_index, "justice_outcome_disposition"].astype(int).values

    # Setup test data
    feature_data_test = feature_df.loc[test_index, :]
    target_data_test = raw_data.loc[test_index, "justice_outcome_disposition"].astype(int).values

    # Check if we should rebuild the model based on changing natural court
    if term_count % reset_interval == 0:
        # "Forest fire;" grow a new forest from scratch
        print("Reset interval hit; rebuilding with {0} trees".format(initial_trees + (term_count * trees_per_term)))
        m = None
    else:
        # Check if the justice set has changed
        if set(raw_data.loc[raw_data.loc[:, "term"] == (term-1), "justice"].unique()) !=  set(raw_data.loc[raw_data.loc[:, "term"] == (term), "justice"].unique()):
            # natural Court change; trigger forest fire
            print("Natural court change; rebuilding with {0} trees".format(initial_trees + (term_count * trees_per_term)))

            m = None

    # Build or grow a model depending on initial/reset condition
    if not m:
        # Grow an initial forest
        m = sklearn.ensemble.RandomForestClassifier(n_estimators=initial_trees + (term_count * trees_per_term),
                                                    class_weight="balanced_subsample",
                                                    warm_start=True,
                                                    n_jobs=-1, random_state=0)
    else:
        # Grow the forest by increasing the number of trees (requires warm_start=True)
        m.set_params(n_estimators=initial_trees + (term_count * trees_per_term))


    # Fit the forest model
    m.fit(feature_data_train,target_data_train)

    # Fit the "dummy" model
    d = sklearn.dummy.DummyClassifier(strategy="most_frequent")
    d.fit(feature_data_train, target_data_train)

    # Perform forest predictions
    raw_data.loc[test_index, "rf_predicted"] = m.predict(feature_data_test)

    # Store scores per class
    scores = m.predict_proba(feature_data_test)
    raw_data.loc[test_index, "rf_predicted_score_affirm"] = scores[:, 0]
    raw_data.loc[test_index, "rf_predicted_score_reverse"] = scores[:, 1]

    # Store dummy predictions
    raw_data.loc[test_index, "dummy_predicted"] = d.predict(feature_data_test)


# # In[6]:

# # Evaluation range
evaluation_index = raw_data.loc[:, "term"].isin(term_range)
target_actual = raw_data.loc[evaluation_index, "justice_outcome_disposition"]
target_predicted = raw_data.loc[evaluation_index, "rf_predicted"]
target_dummy = raw_data.loc[evaluation_index, "dummy_predicted"]
raw_data.loc[:, "rf_correct"] = numpy.nan
raw_data.loc[:, "dummy_correct"] = numpy.nan
raw_data.loc[evaluation_index, "rf_correct"] = (target_actual == target_predicted).astype(float)
raw_data.loc[evaluation_index, "dummy_correct"] = (target_actual == target_dummy).astype(float)

# Compare model
print("RF model")
print("="*32)
print(sklearn.metrics.classification_report(target_actual, target_predicted))
print(sklearn.metrics.confusion_matrix(target_actual, target_predicted))
print(sklearn.metrics.accuracy_score(target_actual, target_predicted))
print("="*32)
print("")

# Dummy model
print("Dummy model")
print("="*32)
print(sklearn.metrics.classification_report(target_actual, target_dummy))
print(sklearn.metrics.confusion_matrix(target_actual, target_dummy))
print(sklearn.metrics.accuracy_score(target_actual, target_dummy))
print("="*32)
print("")



# ## Case Outcomes

# In[11]:

# Get case-level prediction
#scdb_data.loc[evaluation_index, "rf_predicted_case"] =
rf_predicted_case = pandas.DataFrame(raw_data.loc[evaluation_index, :].groupby(["docketId"])["rf_predicted"].agg(lambda x: x.value_counts().index[0]))
rf_predicted_case.columns = ["rf_predicted_case"]

dummy_predicted_case = pandas.DataFrame(raw_data.loc[evaluation_index, :].groupby(["docketId"])["dummy_predicted"].agg(lambda x: x.value_counts().index[0]))
dummy_predicted_case.columns = ["dummy_predicted_case"]

# Set DFs
rf_predicted_case = raw_data[["docketId", "case_outcome_disposition", "rf_predicted"]].join(rf_predicted_case, on="docketId")
dumy_predicted_case = raw_data[["docketId", "dummy_predicted"]].join(dummy_predicted_case, on="docketId")

raw_data.loc[:, "rf_predicted_case"] = rf_predicted_case
raw_data.loc[:, "dummy_predicted_case"] = dumy_predicted_case




# Output case distribution
case_outcomes = raw_data.groupby(["docketId"])["case_outcome_disposition"].agg(lambda x: list(x.mode())[0])
case_outcomes = case_outcomes.apply(lambda x: int(x))
print(case_outcomes.value_counts())
print(case_outcomes.value_counts(normalize=True))


# In[13]:

# Output comparison
# Evaluation range
evaluation_index = raw_data.loc[:, "term"].isin(term_range) & -raw_data.loc[:, "case_outcome_disposition"].isnull()
target_actual = raw_data.loc[evaluation_index, "case_outcome_disposition"]
target_predicted = raw_data.loc[evaluation_index, "rf_predicted_case"]
target_dummy = raw_data.loc[evaluation_index, "dummy_predicted_case"]

raw_data.loc[:, "rf_correct_case"] = numpy.nan
raw_data.loc[:, "dummy_correct_case"] = numpy.nan
raw_data.loc[evaluation_index, "rf_correct_case"] = (target_actual == target_predicted).astype(float)
raw_data.loc[evaluation_index, "dummy_correct_case"] = (target_actual == target_dummy).astype(float)

# Compare model
print("RF model")
print("="*32)
print(sklearn.metrics.classification_report(target_actual, target_predicted))
print(sklearn.metrics.confusion_matrix(target_actual, target_predicted))
print(sklearn.metrics.accuracy_score(target_actual, target_predicted))
print("="*32)
print("")

# Dummy model
print("Dummy model")
print("="*32)
print(sklearn.metrics.classification_report(target_actual, target_dummy))
print(sklearn.metrics.confusion_matrix(target_actual, target_dummy))
print(sklearn.metrics.accuracy_score(target_actual, target_dummy))
print("="*32)
print("")
