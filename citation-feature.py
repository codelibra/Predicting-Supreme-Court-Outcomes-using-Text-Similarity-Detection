
sc_lc = pd.read_csv('../data/sc_lc.csv')

case_id_citations_merged = pd.DataFrame(0, index=sc_lc['caseid'],columns=citations_transpose_pruned.keys())
def generate_citations_merged_df(file):
    for key,value in citations_transpose_pruned.iteritems():
        d = {current_file[:-2]: 1 for current_file in value}
        case_id_citations_merged[key].update(pd.Series(d))



case_id_citations_merged.to_csv('../data/case_id_citations_merged.csv', encoding='utf-8')

df.sum()
