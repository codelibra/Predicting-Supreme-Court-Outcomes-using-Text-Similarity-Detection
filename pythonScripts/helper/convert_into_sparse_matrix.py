## THIS CODE IS NEVER USED. IT IS JUST HELPER CODE.

def dataframe_to_scipy_sparse(x, column_name):
    '''
    Convert a dictionary column of an SFrame into a sparse matrix format where
    each (row_id, column_id, value) triple corresponds to the value of
    x[row_id][column_id], where column_id is a key in the dictionary.

    Example
    >>> sparse_matrix, map_key_to_index = sframe_to_scipy(sframe, column_name)
    '''
    assert x[column_name].dtype() == dict,         'The chosen column must be dict type, representing sparse data.'

    # Create triples of (row_id, feature_id, count).
    # 1. Stack will transform x to have a row for each unique (row, key) pair.
    x = x.stack(column_name, ['feature', 'value'])

    # Map words into integers using a OneHotEncoder feature transformation.
    f = gl.feature_engineering.OneHotEncoder(features=['feature'])
    # 1. Fit the transformer using the above data.
    f.fit(x)
    # 2. The transform takes 'feature' column and adds a new column 'feature_encoding'.
    x = f.transform(x)
    # 3. Get the feature mapping.
    mapping = f['feature_encoding']
    # 4. Get the feature id to use for each key.
    x['feature_id'] = x['encoded_features'].dict_keys().apply(lambda x: x[0])

    # Create numpy arrays that contain the data for the sparse matrix.
    i = np.array(x['id'])
    j = np.array(x['feature_id'])
    v = np.array(x['value'])

    width = x['id'].max() + 1
    height = x['feature_id'].max() + 1
    # Create a sparse matrix.
    mat = csr_matrix((v, (i, j)), shape=(width, height))

    return mat, mapping

tf_idf, map_index_to_word = dataframe_to_scipy_sparse(data, 'tf_idf')
tf_idf_normalise = normalize(tf_idf)


# ### Save sparse matrix representation
io.mmwrite("../data/tf-idf-sparse.mtx", tf_idf)
io.mmwrite("../data/tf-idf-sparse-normalized.mtx", tf_idf_normalise)


# back to sparse matrix
newm = io.mmread("../data/tf-idf-sparse")
newm_norm = io.mmread("../data/tf-idf-sparse-normalized")
tf_idf = newm.tocsr()
tf_idf_normalise = newm_norm.tocsr()


# change sparse matrix to dense matrix.
#dense = tf_idf.todense()
