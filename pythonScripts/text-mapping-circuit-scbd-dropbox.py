
# coding: utf-8


import dropbox
import pandas as pd
import pickle
import sys



# Include the Dropbox SDK

# Get your app key and secret from the Dropbox developer website
app_key = '72wskb63a1ayvce'
app_secret = 'zi42jh8bgv7d392'

flow = dropbox.client.DropboxOAuth2FlowNoRedirect(app_key, app_secret)

# Have the user sign in and authorize this token
authorize_url = flow.start()
print '1. Go to: ' + authorize_url
print '2. Click "Allow" (you might have to log in first)'
print '3. Copy the authorization code.'
code = raw_input("Enter the authorization code here: ").strip()

# This will fail if the user enters an invalid authorization code
access_token, user_id = flow.finish(code)

client = dropbox.client.DropboxClient(access_token)
print 'linked account: ', client.account_info()



access_token



dbx = dropbox.Dropbox(access_token)



f, metadata = client.get_file_and_metadata('/1880_complete/XALNA1.html')
out = open('/Users/shiv/Desktop/magnum-opus.html', 'wb')
out.write(f.read())
out.close()
print metadata



circuit_files = pd.read_csv('/Users/shiv/.bin/10_scotus/sc_lc_link.csv')



for file,term in zip(circuit_files['caseid'],circuit_files['term']):
    path =  '/'+str(term)+'_complete/'+file+".html"
    try:
        f, metadata = client.get_file_and_metadata(path)
        out = open('/Users/shiv/Desktop/circuit-scbd-mapped-files/'+file+'.html', 'wb')
        out.write(f.read())
        out.close()
    except:
        print path
