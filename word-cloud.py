# -*- coding: utf-8 -*-
"""
Created on Mon May  4 20:57:46 2015

@author: elliott
"""

from wordcloud import WordCloud
import pandas as pd
import os
import numpy as np

os.chdir('...')

# parameters
MIN_DOCFREQ = 50 # minimum document frequency to be included
ONLY_PHRASES = True # keep true if dont include single words

# load data
tstats = pd.read_pickle('tstats.pkl')
id2word = pd.read_pickle('id2word.pkl')
P = len(id2word)

words = list(['']*P)
for i,w in id2word.items():
    words[i] = w

# optional: filter on document frequency
docfreqs = pd.read_pickle('docfreqs.pkl')
freqvector = [0] * P
for k, v in docfreqs.items():
    freqvector[k] = v
freqvector = np.array(freqvector)
keep = freqvector > 1000
tstats = tstats[keep]
words = [words[i] for i in range(P) if keep[i]]

# split up positive-effect and negative-effect words
pos = tstats > 0
neg = tstats < 0

tpos = tstats[pos]
wordpos = words[pos]
tneg = np.abs(tstats[neg]) # reverse sign for negative effect words
wordneg = words[neg]

maincol = np.random.randint(0,360) # this is the "main" color
def colorfunc(word=None, font_size=None, position=None,
                  orientation=None, font_path=None, random_state=None):
    color = np.random.randint(maincol-10, maincol+10)
    if color < 0:
        color = 360 + color
    return "hsl(%d, %d%%, %d%%)" % (color,np.random.randint(65, 75)+font_size / 7, np.random.randint(35, 45)-font_size / 10)

# build scores tuples
# positive effect words
scores = list(zip(tpos,wordpos))
scores = [s for s in scores if np.isfinite(s[0])]
if ONLY_PHRASES:
    scores = [s for s in scores if '_' in s[1]]
scores.sort()
scores.reverse()
scores = [(b,np.log(a)) for (a,b) in scores]
print(scores[:10])
wordcloud = WordCloud(background_color="white", ranks_only=False,max_font_size=100,
                        color_func=colorfunc,
                        height=600,width=1000).generate_from_frequencies(scores[:100])
wordcloud.to_file('pos-words.png')

# negative effect words
scores = list(zip(tneg,wordneg))
scores = [s for s in scores if np.isfinite(s[0])]
if ONLY_PHRASES:
    scores = [s for s in scores if '_' in s[1]]
scores.sort()
scores.reverse()
scores = [(b,np.log(a)) for (a,b) in scores]
print(scores[:10])
wordcloud = WordCloud(background_color="white", ranks_only=False,max_font_size=100,
                        color_func=colorfunc,
                        height=600,width=1000).generate_from_frequencies(scores[:100])
wordcloud.to_file('neg-words.png')
