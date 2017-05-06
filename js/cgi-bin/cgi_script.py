#!/usr/bin/env python
import cgi,cgitb
cgitb.enable()

# create the result html file
from subprocess import call
call(["touch", "action_page.html"])

# concatenate user query to this cmd to pass to search.py
form  = cgi.FieldStorage()
query = form.getvalue('query')
relevanceFeedback = form.getvalue('relevanceFeedback')

data = ["this is one hell of a script", "let's c what happens", "click and render", "hell yeahhh!"]
print "Content-type: text\n\n"
print ["Hello world","on fine","get lost"]


# what should the script do?
#couple of functions are requrired ,
#get_all_cases() -> must return array of text of all cases
#get_similar_case_text(index) -> must return array of text of current case, similar cases
