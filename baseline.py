#Lester Lee & Vincent Lin
import string
from nltk.corpus import stopwords
from nltk import word_tokenize

#question processing: remove stop words from question

stopword_list = stopwords.words('english')

with open("qadata/train/questions.txt") as question_file:
	question_list = list(filter(None,question_file.read().split("\n")))
	questions = {}
	for i in range(0, len(question_list), 2):
		#Lower case everything, tokenize, then remove punctuation, and then remove stopwords
		qnum = question_list[i].split()[-1]
		question = question_list[i+1].lower() 
		question = word_tokenize(question)
		question = [w.translate(None, string.punctuation) for w in question]
		question = list(filter(None, question))
		questions[qnum] =  ([w for w in question if not w in stopword_list], [w for w in question if w in stopword_list])
#questions is a dictionary {question#: question tokens}
		
#passage retrieval
for qnum in questions:
	docname = "top_docs.{}".format(qnum)
	with open("topdocs/train/{}".format(docname)) as docfile:
		#parse docfile into etree
		qidlist = []
		textlist = []
		oneTextfile = False
		textstring= ""
		for docstring in docfile:
			if oneTextfile is True:
				textstring+=docstring
			#get the qid
			if docstring.startswith("Qid:"):
				qidlist.append(docstring)
			#Get all elements that starts with the <text> and end with </text>
			if docstring.startswith("<TEXT>"):
				oneTextfile = True
			if docstring.startswith("</TEXT>"):
				oneTextfile = False
				textlist.append(textstring)
				textstring = ""
		
		print textlist
		#len of this is 51
		print len(textlist)
		print qidlist
		#len of this more than 51
		print len(qidlist)

		#i was thinking of zipping them to make tuples fo the lengths are diiferent
		#the bug is here 

		#qidtextTuple = zip(qidlist, textlist)
		#print qidtextTuple





		#retrieve appropriate 10-grams
		#map each 10-gram to binary feature vector with question as bag of words
		#compute vector similarity score between question & each feature vector
		#retrieve the most-similar one


#answer formation
#Find the sentence that gave highest score (some way of tracking this)
#Stanford Named Entity Tagger
#Output 10 most relevant answers using most similar passage
#That's just reordering words / fitting info into sentence templates
#Figure what heuristics to use to pull the best words from the 10gram
