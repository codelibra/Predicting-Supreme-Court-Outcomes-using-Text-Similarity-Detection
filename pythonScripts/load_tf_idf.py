from sklearn.feature_extraction.text import TfidfVectorizer
files = [os.path.join('../data/circuit-scbd-mapped-files-complete/',f) for f in os.listdir('../data/circuit-scbd-mapped-files-complete/')]
model = TfidfVectorizer(ngram_range=(1, 3), min_df=0, stop_words='english')
tf_idf = model.fit_transform(files)

from sklearn.feature_extraction.text import CountVectorizer
vectorizer = CountVectorizer(input='filename',min_df=1,ngram_range=(1,3))
X = vectorizer.fit_transform(files)
