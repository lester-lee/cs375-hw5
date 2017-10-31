#Lester Lee & Vincent Lin
import string, re
from nltk.corpus import stopwords
from nltk import word_tokenize
<<<<<<< HEAD

#question processing: remove stop words from question
=======
>>>>>>> 4ff006b4ce057419f5cf9b9f456a2ed6a55ec637

stopword_list = stopwords.words('english')
def preprocess(s, getstopwords=False):
        #given s, tokenize and remove punctuation
        s = s.lower()
        s = word_tokenize(s)
        s = [w.translate(None, string.punctuation) for w in s]
        s = list(filter(None, s))
        if getstopwords:
                return ([w for w in s if not w in stopword_list],
                        [w for w in s if w in stopword_list])
        else:
                return [w for w in s if not w in stopword_list]

<<<<<<< HEAD
=======
#find the ngram 
# the number = n
def ngram(textlist, number):
	for text in textlist:
		ngramlist =[]
		for n in range(len(text)-number+1):
			singleNgram = []
			for e in range(number):
				singleNgram.append(text[e+n])
			ngramlist.append(singleNgram)
	return ngramlist

'''
questions about vector similarity and etc require more thoughts
def compare_ngram(text, wordbag):
	for e in text:
		if e is in wordbag:
			count+=1
'''
#question processing: remove stop words from question
>>>>>>> 4ff006b4ce057419f5cf9b9f456a2ed6a55ec637
with open("qadata/train/questions.txt") as question_file:
	question_list = list(filter(None,question_file.read().split("\n")))
	questions = {}
	for i in range(0, len(question_list), 2):
		#Lower case everything, tokenize, then remove punctuation, and then remove stopwords
		qnum = question_list[i].split()[-1]
<<<<<<< HEAD
		question = question_list[i+1].lower() 
		question = word_tokenize(question)
		question = [w.translate(None, string.punctuation) for w in question]
		question = list(filter(None, question))
		questions[qnum] =  ([w for w in question if not w in stopword_list], [w for w in question if w in stopword_list])
=======
		question = preprocess(question_list[i+1], getstopwords=True)
		questions[qnum] = question
		#print questions
>>>>>>> 4ff006b4ce057419f5cf9b9f456a2ed6a55ec637
#questions is a dictionary {question#: question tokens}
		
#passage retrieval
for qnum in questions:
	docname = "top_docs.{}".format(qnum)
<<<<<<< HEAD
	with open("topdocs/train/{}".format(docname)) as docfile:
		#parse docfile into etree
		qidlist = []
		textlist = []
		textstring= ""
		oneTextfile = False
		for docstring in docfile:
			
			#get the qid
			if docstring.startswith("Qid:"):
				qidlist.append(docstring)
				textlist.append(textstring)
				textstring = ""
			elif oneTextfile:
				textstring+=docstring

			#Get all elements that starts with the <text> and end with </text>
			#since there may be multiple elements in one qid
			if docstring.startswith("<TEXT>"):
				oneTextfile = True
			if docstring.startswith("</TEXT>"):
				oneTextfile = False
		#print textlist
		print len(textlist)
		#print qidlist
		print len(qidlist)

		qidtextTuple = zip(qidlist, textlist)
			print qidtextTuple





=======
        textRE = re.compile(r'<TEXT>(.*)</TEXT>', re.DOTALL)
	with open("topdocs/train/{}".format(docname)) as docfile:
		#for each qid, make a string containing everything within <text> tags
		qidlist = []
		textlist = []
                parsedtextlist = []
		textstring= ""
		for docstring in docfile:
                        if docstring.startswith("Qid:"):
                                qidlist.append(docstring)
                                textlist.append(textstring)
                                textstring = ""
                        else:
                                textstring += docstring

                for textchunk in textlist:
                        texts = textRE.findall(textchunk)
                        tempstring = " ".join(texts)
                        parsedtextlist.append(preprocess(tempstring))
                #print parsedtextlist
                print ngram(parsedtextlist, 10)
		qidtextTuple = zip(qidlist, parsedtextlist)
		#print(qidtextTuple)
            
>>>>>>> 4ff006b4ce057419f5cf9b9f456a2ed6a55ec637
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
