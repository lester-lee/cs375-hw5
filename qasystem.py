#Lester Lee & Vincent Lin
import string, re, nltk, codecs
import sys
reload(sys)
sys.setdefaultencoding('utf8')

from nltk.corpus import stopwords
from collections import Counter
from nltk import word_tokenize, pos_tag

from nltk.stem import SnowballStemmer
snowball_stemmer = SnowballStemmer('english')
stopword_list = stopwords.words('english') + [u'p']

stanford_classifier = '/Users/michaelqi/Downloads/stanford-ner-2017-06-09/classifiers/english.all.7class.distsim.crf.ser.gz'

stanford_ner_path = '/Users/michaelqi/Downloads/stanford-ner-2017-06-09/stanford-ner.jar'
st = StanfordNERTagger(stanford_classifier, stanford_ner_path, encoding='utf-8')


def preprocess(s, getstopwords=False, stopwords=False):
        #given s, tokenize and remove punctuation
#        s = str(s)
        s = word_tokenize(s)
       # s = [w.translate(None, string.punctuation) for w in s]
        s = list(filter(None, s))
        s = [snowball_stemmer.stem(w) for w in s]
        if getstopwords:
                return ([w for w in s if not w.lower() in stopword_list],
                        [w for w in s if w.lower() in stopword_list])
        elif stopwords:
                return [w for w in s if not w.lower() in stopword_list]
        else:
                return s
#find the ngram 
# the number = n
def find_best_ngram(textlist, number, questions, qidlist):
	for i in range(len(textlist)):
                text = textlist[i]
                qid = qidlist[i]
                score = float(qid.split()[-1])
		ngramlist =[]
                best = []
		for n in range(len(text)-number+1):
			singleNgram = []
			for e in range(number):
				singleNgram.append(text[e+n])
			ngramlist.append(singleNgram)
		best.append(compare_ngram(ngramlist, questions, score))
	return best

'''
since the vector are [1 1 1 1] *[ x y z w] where x,y,z,w are the frequency of each word from the wordbag, 
we can compute this by summing all the x,y,z,w together. 
the length of the vector is determined by the wordbag.
this returns a list of tuples [(10gram, freq)...]


'''
def compare_ngram(ngramlist, wordbag, score):
        frequency = []
        maximum = 1     
	for e in ngramlist:
		# e is a list of tokens
                freqs = Counter(e)
                res = sum([freqs[word] for word in freqs if word in wordbag]) #* float(score)
                #only save the maximum 
                if res == maximum:
                        maximum = res
                        frequency.append((res, e))
                        #frequency.append(e)
                elif res > maximum:
                        frequency =[]
                        maximum = res
                        #frequency.append(e)

                        frequency.append((res, e))
	return frequency

def heuristic_list(best_ne, question):
        people = [subtree[0][0] for subtree in best_ne if isinstance(subtree, nltk.tree.Tree) and subtree.label() == "PERSON"]
        gpes = [subtree[0][0] for subtree in best_ne if isinstance(subtree, nltk.tree.Tree) and subtree.label() == "GPE"]
        locations = [subtree[0][0] for subtree in best_ne if isinstance(subtree, nltk.tree.Tree) and subtree.label() == "LOCATION"]
        times = [subtree[0][0] for subtree in best_ne if isinstance(subtree, nltk.tree.Tree) and subtree.label() == "TIME"]
        dates = [subtree[0][0] for subtree in best_ne if isinstance(subtree, nltk.tree.Tree) and subtree.label() == "DATE"]
        org = [subtree[0][0] for subtree in best_ne if isinstance(subtree, nltk.tree.Tree) and subtree.label() == "ORGANIZATION"]
        percent = [subtree[0][0] for subtree in best_ne if isinstance(subtree, nltk.tree.Tree) and subtree.label() == "PERCENT"]
        money = [subtree[0][0] for subtree in best_ne if isinstance(subtree, nltk.tree.Tree) and subtree.label() == "MONEY"]
        facility = [subtree[0][0] for subtree in best_ne if isinstance(subtree, nltk.tree.Tree) and subtree.label() == "FACILITY"]
        nouns = [leaf[0] for leaf in best_ne if not isinstance(leaf, nltk.tree.Tree) and "NN" in leaf[1]]
        answers = []
        if "where" in question[1]:
                answers = locations+facility
        elif "who" in question[1]:
                answers = people+org
                print question
                print answers
        elif "when" in question[1]:
                answers = times+dates
        elif "how" in question[1]:
                answers = money+percent
        elif "name" in question[0]:
                answers = people+locations+gpes+org+facility
        answers += nouns
        return answers[:1]
             

#question processing: remove stop words from question
with codecs.open("qadata/train/questions.txt", encoding = 'utf-8') as question_file:
	question_list = list(filter(None,question_file.read().split("\n")))
	questions = {}
	for i in range(0, len(question_list), 2):
		#Lower case everything, tokenize, then remove punctuation, and then remove stopwords
		qnum = question_list[i].split()[-1]
		question = preprocess(question_list[i+1], getstopwords=True)
		questions[qnum] = question
                #print questions[qnum]
#questions is a dictionary {question#: (question tokens,stopwords)}
		
finalanswers = []
'''
def closestdistance():
def scoreaccount():
        pass
'''
#passage retrieval
for qnum in range(0, 150):
        qnum = str(qnum)
        if qnum in questions:
        	docname = "top_docs.{}".format(qnum)
                textRE = re.compile(r'<TEXT>(.*)</TEXT>', re.DOTALL)
        	with codecs.open("topdocs/train/{}".format(docname), encoding='utf-8', errors='replace') as docfile:
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
                                parsedtextlist.append(preprocess(tempstring,getstopwords=False, stopwords=False))
                                #parsedtextlist.append(tempstring)
                        
                        #potential bug the stopword removed the word "won".
                       # print questions[qnum]
                        #print parsedtextlist
                        bestngram = find_best_ngram(parsedtextlist, 10, questions[qnum][0], qidlist)
        		print bestngram
                        qidtextTuple = zip(qidlist, parsedtextlist[1:])
        		#print(qidtextTuple)

                        #answer formation
                        #Find the sentence that gave highest score (some way of tracking this)
                        answers = []
                        #ideally we want to pass into the entire center
                        '''
                        for e in bestngram:
                                for best_sentence in e:
                                        #stanford tag
                                        best_ne = st.tag(best_sentence)
                                        answers += heuristic_list(best_ne, questions[qnum])
                                        
                        '''
                        '''
                        count the number of named entity. so (Bolivia: location), make a list of all these named entity
                        make a list of if then statements of sample heuristic. so if "where" then prioritize location entity.
                        if "what"
                        '''
                        #answers = heuristic_list(best_ne, questions[qnum])
                        finalanswers.append("qid {}".format(qnum))
                        finalanswers += answers

                        #best_sentence = "soya agricultural exports roads rather railways become focus attention Bolivia".split()
                        #Stanford Named Entity Tagger
                        
                        #Output 10 most relevant answers using most similar passage
                        #That's just reordering words / fitting info into sentence templates
                        #Figure what heuristics to use to pull the best words from the 10gram
with open("predictions.txt", "w") as f:
        for a in finalanswers:
                f.write("{}\n".format(a))