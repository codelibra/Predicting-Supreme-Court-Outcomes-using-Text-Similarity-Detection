#!/usr/bin/env python
import cgi,cgitb
import json
import sys,getopt
cgitb.enable()


words1 = "Larson has been quoted in the opinion of the Court by Mr. Justice Burton in Anti-Fascist Committee v. McGrath, supra, 341 U.S. at page 140, 71 S.Ct. at page 632, as followsThere is no evidence in the record to support that statement. As the statute itself and the Senate Committee Report plainly state, one inquiry under section 131(h) is whether the tax was levied by the foreign country in place of or instead of or as a substitute for some existing income or profits tax.4 Referring to Treasury Regulation 118 the district court said"

words2= "It is hardly reasonable to presume that all the stockholders are domiciled in each of two separate states. But the principal point is that, even laying aside the matter of multiple incorporation, unincorporated associations cannot be equated with corporations by a simple judicial decision attributing citizenship to them. They are incapable of dual citizenship and hence would be treated more favorably than corporations for diversity purposes"

words3 = "Another claimed error is the charge that no contributory negligence on the part of the plaintiff had been shown. While the better practice is to let this question go to the jury, LaGuerra v. Brasileiro, 124 F.2d 553, 2 Cir. 1942, we cannot say that the ruling was error in the circumstances of this case where evidence was lacking that Albanese knew of the complaints or appreciated the danger on the day of his injury, or indeed had any real choice of action if he had. There is, however, one other ruling which was erroneous on the proof here. That is the instruction that the Safety and Health Regulations for Longshoring were binding on the shipowner, in spite of the"

words4 = "On appeal is a judgment rendered by a magistrate in favor of a prisoner who was physically mistreated by corrections officers. In light of the standards established by this court's intervening decision in Huguet v. Barnett, 900 F.2d 838 (5th Cir.1990), and progeny, however, we must reverse.qX Keith J. Hudson, a Louisiana state prisoner confined to Angola penitentiary invoked 42 U.S.C. 1983 and sued corrections officers Jack McMillian, Marvin Woods, and Arthur Mezo. The parties consented to disposition."

words5 = "Fernandez also claims that his wife filed a relative visa petition for him at some point and that he was provided employment authorization due to his pending adjustment application, although there is nothing in the record to support these assertions. It does appear, however, that the government treated Fernandez' adjustment application as if a relative visa petition had been filed on his behalf prior to April 30, 2001, and the government does not dispute in its brief that such a petition was filed."

words6 = "encumbrance or obligation to be taken into account in valuing the property to be excluded means an encumbrance or obligation on the property such as a lien against the property for a debt, as distinguished from an obligation or encumbrance in the nature of a condition as here under the election. Wachovia Bank & Trust Co. v. United States, 1958, 163 F.Supp. 832, 143 Ct.Cl. 376.qXDWe look to the terms of the statute itself for its meaning. The last clause of it teaches how the valuation is to be computed and this is the key to the determination of this issue. It shall be taken into account in the same manner as if the amount of a gift of such interest by the husband to his wife was being determined.qXThe value of a gift by a husband to a wife of property, on the condition"

words = [words1,  words2,  words3, words4, words5, words6]
caseNames = ["Case 1",  "Case 2",  "Case 3", "Case 4", "Case 5", "Case 6"]
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

    form  = cgi.FieldStorage()
    query = form.getvalue('query')
    caseId = form.getvalue('caseId')

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

    if query is not None and len(query)!=0:
        print get_all_cases()
    else:
        print get_similar_case_text(caseId)

if  __name__ =='__main__':
    main(sys.argv[1:])


# what should the script do?
#couple of functions are requrired ,
#get_all_cases() -> must return array of text of all cases
#get_similar_case_text(index) -> must return array of text of current case, similar cases
