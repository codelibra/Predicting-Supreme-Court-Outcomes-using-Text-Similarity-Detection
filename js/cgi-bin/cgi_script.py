#!/usr/bin/env python
import cgi,cgitb
import json
import sys,getopt
cgitb.enable()


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


def get_similar_case_text(id):
    '''
    Given a particular caseId the function would return text of 5 nearest neighbours.
    '''
    similar_cases = {}
    similar_cases['original'] = words[int(id)]
    similar_cases['case1']= words1
    similar_cases['case2']= words2
    similar_cases['case3']= words3
    similar_cases['case4']= words4
    similar_cases['case5']= words5

    return json.dumps(similar_cases)



def main(argv):
    try:
        opts, args = getopt.getopt(argv,"q:r:")
    except getopt.GetoptError:
        sys.exit()


    for opt, arg in opts:
        if opt in ("-q"):
            query = arg
        else:
            query = -1

        if opt in ("-r"):
            caseId = int(arg)


    print "Content-type: text\n\n"

    if query!=-1:
        print get_all_cases()
    else:
        print get_similar_case_text(caseId)

if  __name__ =='__main__':
    main(sys.argv[1:])


# what should the script do?
#couple of functions are requrired ,
#get_all_cases() -> must return array of text of all cases
#get_similar_case_text(index) -> must return array of text of current case, similar cases
