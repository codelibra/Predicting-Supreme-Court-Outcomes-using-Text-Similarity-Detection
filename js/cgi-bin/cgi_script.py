#!/usr/bin/env python
import cgi,cgitb
import json
cgitb.enable()

# create the result html file
from subprocess import call
call(["touch", "action_page.html"])

# concatenate user query to this cmd to pass to search.py
form  = cgi.FieldStorage()
query = form.getvalue('query')
relevanceFeedback = form.getvalue('relevanceFeedback')

words1 = "You don't know about me without you have read a book called The Adventures of Tom Sawyer but that ain't no matter. The boy with fair hair lowered himself down the last few feet of rock and began to pick his way toward the lagoon. When Mr. Bilbo Baggins of Bag End announced that he would shortly be celebrating his eleventy-first birthday with a party of special magnificence, there was much talk and excitement in Hobbiton. It was inevitable: the scent of bitter almonds always reminded him of the fate of unrequited love."

words2= "You don't know about me without you have read a book called The Adventures of Tom Sawyer but that ain't no matter. The boy with fair hair lowered himself down the last few feet of rock and began to pick his way toward the lagoon. When Mr. Bilbo Baggins of Bag End announced that he would shortly be celebrating his eleventy-first birthday with a party of special magnificence, there was much talk and excitement in Hobbiton. It was inevitable: the scent of bitter almonds always reminded him of the fate of unrequited love."

words3 = "You don't know about me without you have read a book called The Adventures of Tom Sawyer but that ain't no matter. The boy with fair hair lowered himself down the last few feet of rock and began to pick his way toward the lagoon. When Mr. Bilbo Baggins of Bag End announced that he would shortly be celebrating his eleventy-first birthday with a party of special magnificence, there was much talk and excitement in Hobbiton. It was inevitable: the scent of bitter almonds always reminded him of the fate of unrequited love."

words4 = "You don't know about me without you have read a book called The Adventures of Tom Sawyer but that ain't no matter. The boy with fair hair lowered himself down the last few feet of rock and began to pick his way toward the lagoon. When Mr. Bilbo Baggins of Bag End announced that he would shortly be celebrating his eleventy-first birthday with a party of special magnificence, there was much talk and excitement in Hobbiton. It was inevitable: the scent of bitter almonds always reminded him of the fate of unrequited love."

words5 = "You don't know about me without you have read a book called The Adventures of Tom Sawyer but that ain't no matter. The boy with fair hair lowered himself down the last few feet of rock and began to pick his way toward the lagoon. When Mr. Bilbo Baggins of Bag End announced that he would shortly be celebrating his eleventy-first birthday with a party of special magnificence, there was much talk and excitement in Hobbiton. It was inevitable: the scent of bitter almonds always reminded him of the fate of unrequited love."

words6 = "You don't know about me without you have read a book called The Adventures of Tom Sawyer but that ain't no matter. The boy with fair hair lowered himself down the last few feet of rock and began to pick his way toward the lagoon. When Mr. Bilbo Baggins of Bag End announced that he would shortly be celebrating his eleventy-first birthday with a party of special magnificence, there was much talk and excitement in Hobbiton. It was inevitable: the scent of bitter almonds always reminded him of the fate of unrequited love."

words = [words1,  words2,  words3, words4, words5, words6]
caseNames = ["case1",  "case2",  "case3", "case4", "case5", "case6"]
caseTopics = ["word1",  "word2",  "word3", "word4", "word5", "word6"]
caseTerm = [1991,  1992,  1993, 1994, 1995, 1996]
def get_all_cases():
    '''
    Json object must have
    1. id of each case
    2. caseName
    3. caseDescription
    4. caseTopics
    5. caseTerm
    '''
    data = {}
    for idx,text in enumerate(words):
        case = {}
        case['caseName'] = caseNames[idx]
        case['caseTopic'] = caseTopics[idx]
        case['caseDescription'] = text
        case['caseTerm'] = caseTerm[idx]
        data[idx] = case
    return json.dumps(data)

data = ["this is one hell of a script", "let's c what happens", "click and render", "hell yeahhh!"]
print "Content-type: text\n\n"
print get_all_cases()

# what should the script do?
#couple of functions are requrired ,
#get_all_cases() -> must return array of text of all cases
#get_similar_case_text(index) -> must return array of text of current case, similar cases
