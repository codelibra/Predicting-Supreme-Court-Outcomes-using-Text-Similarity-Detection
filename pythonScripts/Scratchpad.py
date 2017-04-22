
# coding: utf-8

# In[2]:

from tqdm import tnrange, tqdm_notebook
from time import sleep

for i in tnrange(10, desc='1st loop'):
    for j in tqdm_notebook(xrange(100), desc='2nd loop'):
        sleep(0.01)


# In[4]:

import os


# In[14]:

for root, dirs, files in os.walk('/Users/shiv/Desktop/circuit-scbd-mapped-files/', topdown=False):
    for idx,name in enumerate(tqdm(files)):
        print name
        sleep(10)

