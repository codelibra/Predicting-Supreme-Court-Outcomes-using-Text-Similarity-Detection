

# We are using scdb docket centered data because it doesn't consolidate cases
# Below two functions are made available by Micheal Bommirito's paper
raw_data = get_raw_scdb_data('../data/SCDB_2016_01_justiceCentered_Docket.csv')
scbd_dataframe = raw_data



sc_lc_link_dataframe = pd.read_csv('../data/sc_lc_link.csv', header=0)

sc_lc_link_dataframe['key'] = sc_lc_link_dataframe['term'].map(str) + '-' + sc_lc_link_dataframe['docket']
scbd_dataframe['key'] = scbd_dataframe['term'].map(str) + '-' + scbd_dataframe['docket']

scbd_no_lc_dataframe = scbd_dataframe[~scbd_dataframe['key'].isin(sc_lc_link_dataframe['key'])]
scbd_no_lc_dataframe.shape
scbd_dataframe.shape

scbd_dataframe = scbd_dataframe[scbd_dataframe['key'].isin(sc_lc_link_dataframe['key'])]
scbd_dataframe.shape

sc_lc_link_cols_to_use = sc_lc_link_dataframe.columns.difference(scbd_dataframe.columns)
sc_lc_link_cols_to_use = sc_lc_link_cols_to_use | ['key']
merged_dataframe = scbd_dataframe.merge(sc_lc_link_dataframe[sc_lc_link_cols_to_use], on='key', how='left', suffixes=('', '_y'))

merged_dataframe.to_csv('../data/sc_lc.csv',header=True,index=False, encoding='utf-8')
# The program ends here

# This is just some testing to show which dataset to use. Need not run this.
docket_dataframe = pd.read_csv('SCDB_2016_01_caseCentered_Docket.csv', header=0)
docket_dataframe['docket'].value_counts()
group_by_dataframe = docket_dataframe.groupby(['usCite'])
group_by_with_clause_dataframe = group_by_dataframe.filter(lambda x: len(x) == 3)

group_by_with_clause_dataframe.shape
group_by_with_clause_dataframe[['term','docket','usCite','caseDisposition']]
