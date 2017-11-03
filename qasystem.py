#Lester Lee & Vincent Lin
import string, re, nltk
from nltk.corpus import stopwords
from collections import Counter
from nltk import word_tokenize, pos_tag

stopword_list = stopwords.words('english') + [u'p']
def preprocess(s, getstopwords=False):
        #given s, tokenize and remove punctuation
        s = word_tokenize(s)
        s = [w.translate(None, string.punctuation) for w in s]
        s = list(filter(None, s))
        if getstopwords:
                return ([w for w in s if not w.lower() in stopword_list],
                        [w for w in s if w.lower() in stopword_list])
        else:
                return [w for w in s if not w.lower() in stopword_list]

#find the ngram 
# the number = n
def find_best_ngram(textlist, number, questions):
	for text in textlist:
		ngramlist =[]
		for n in range(len(text)-number+1):
			singleNgram = []
			for e in range(number):
				singleNgram.append(text[e+n])
			ngramlist.append(singleNgram)
			compare_ngram(ngramlist, questions)
	return ngramlist

'''
since the vector are [1 1 1 1] *[ x y z w] where x,y,z,w are the frequency of each word from the wordbag, 
we can compute this by summing all the x,y,z,w together. 
the length of the vector is determined by the wordbag.
this returns a list of tuples [(10gram, freq)...]
'''
def compare_ngram(ngramlist, wordbag):
	frequency = []
	for e in ngramlist:
		# e is a list of tokens
                freqs = Counter(e)
                res = 0
                for word in freqs:
                        if word in wordbag:
                                res += freqs[word]
                frequency.append((res, e))
	return frequency

#question processing: remove stop words from question
with open("qadata/train/questions.txt") as question_file:
	question_list = list(filter(None,question_file.read().split("\n")))
	questions = {}
	for i in range(0, len(question_list), 2):
		#Lower case everything, tokenize, then remove punctuation, and then remove stopwords
		qnum = question_list[i].split()[-1]
		question = preprocess(question_list[i+1], getstopwords=True)
		questions[qnum] = question

#questions is a dictionary {question#: (question tokens,stopwords)}
		
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
                        
                #print parsedtextlist
                #print find_best_ngram(parsedtextlist, 10, questions[qnum][0])
		qidtextTuple = zip(qidlist, parsedtextlist[1:])
		#print(qidtextTuple)

                
                #answer formation
                #Find the sentence that gave highest score (some way of tracking this)
                best_sentence = "soya agricultural exports roads rather railways become focus attention Bolivia".split()
                #Stanford Named Entity Tagger
                best_sentence = pos_tag(best_sentence)
                best_ne = nltk.ne_chunk(best_sentence)
                print(best_ne)
                #Output 10 most relevant answers using most similar passage
                #That's just reordering words / fitting info into sentence templates
                #Figure what heuristics to use to pull the best words from the 10gram

                break
