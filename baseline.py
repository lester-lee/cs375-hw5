#Lester Lee & Vincent Lin
import string, re
from nltk.corpus import stopwords
from nltk import word_tokenize

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

#question processing: remove stop words from question
with open("qadata/train/questions.txt") as question_file:
	question_list = list(filter(None,question_file.read().split("\n")))
	questions = {}
	for i in range(0, len(question_list), 2):
		#Lower case everything, tokenize, then remove punctuation, and then remove stopwords
		qnum = question_list[i].split()[-1]
		question = preprocess(question_list[i+1], getstopwords=True)
		questions[qnum] = question
#questions is a dictionary {question#: question tokens}
		
#passage retrieval
for qnum in questions:
	docname = "top_docs.{}".format(qnum)
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

		qidtextTuple = zip(qidlist, parsedtextlist)
		print(qidtextTuple)
                
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
