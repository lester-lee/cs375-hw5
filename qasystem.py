#Lester Lee & Vincent Lin
import string, re, nltk, codecs
import sys

reload(sys)
sys.setdefaultencoding('utf8')

from nltk.corpus import stopwords
from collections import Counter
from nltk import word_tokenize, pos_tag
from nltk.tag import StanfordNERTagger
from nltk.stem import SnowballStemmer
from nltk.tokenize import RegexpTokenizer
tokenizer = RegexpTokenizer(r'\w+')
snowball_stemmer = SnowballStemmer('english')
stopword_list = stopwords.words('english') + [u'p']

stanford_classifier ='/Users/michaelqi/Downloads/stanford-ner-2017-06-09/classifiers/english.muc.7class.distsim.crf.ser.gz'
stanford_ner_path = '/Users/michaelqi/Downloads/stanford-ner-2017-06-09/stanford-ner.jar'
st = StanfordNERTagger(stanford_classifier, stanford_ner_path, encoding='utf-8')


def preprocess(s, getstopwords=False, stopwords=False, text = False):
        #given s, tokenize and remove punctuation
        #s = [snowball_stemmer.stem(w) for w in s]
        if text:
                s = nltk.sent_tokenize(s)
                s = [nltk.word_tokenize(e) for e in s]
                s = list(filter(None, s))
        else:
                s = tokenizer.tokenize(s)
                s = list(filter(None, s))
        if getstopwords:
                return ([w for w in s if not w.lower() in stopword_list],
                        [w.lower() for w in s if w.lower() in stopword_list])
        elif stopwords:
                return [w for w in s if not w.lower() in stopword_list]
        else:
                return s
#find the ngram 
# the number = n
#textlist = list of list of textual passages
# work on deeper passage seperation instead of text seperation
def find_best_passages(textlist, questions, qidlist):
        best = []
        for i in range(len(textlist)):
                text = textlist[i]
                qid = qidlist[i]
                score = float(qid.split()[-1])
                '''
                for n in range(len(text)-number+1):
			singleNgram = []
			for e in range(number):
				singleNgram.append(text[e+n])
			ngramlist.append(singleNgram)
		'''	
                best.append(compare_ngram(text, questions, score))
        best = list(filter(None, best))
        best = sorted(best, reverse = True)[:3]
        finallist = []
        for e in best:
        	for i in range(len(e)):
        		if i is not 0:
        			finallist.append(e[i])
        #print finallist
	return finallist

'''
since the vector are [1 1 1 1] *[ x y z w] where x,y,z,w are the frequency of each word from the wordbag, 
we can compute this by summing all the x,y,z,w together. 
the length of the vector is determined by the wordbag.
this returns a list of tuples [(10gram, freq)...]
'''
def compare_ngram(text, wordbag, score):
        frequency = []
        maximum = 1     
	for e in text:
		# e is a list of tokens           
                freqs = Counter(e)
                res = sum([freqs[word] for word in freqs if word in wordbag]) * float(score)
                #only save the maximum 
                if res == maximum:
                        maximum = res
                        frequency.append(e)
                        #frequency.append(e)
                elif res > maximum:
                        frequency =[]
                        maximum = res
                        frequency.append(res)
                        frequency.append(e)
	return frequency

def heuristic_list(best_ne, pos_tag, question):
        '''
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
        '''
        NamedEntities = []
        for listoftokens in best_ne:
            previous = ("", 'O')
            string = ""
            for element in listoftokens:
                if element[0] not in question[0]:
                    if element[1] != 'O' and previous[1] != 'O':
                        if previous[1] == element[1]:
                            string += " "+element[0]
                            previous = element
                        elif previous[1]!= 'O':
                            NamedEntities.append((string, previous[1]))
                            string = str(element[0])
                            previous = element
                    elif element[1] != 'O' and previous[1] == 'O':
                            string = str(element[0])
                            previous = element
                    elif element[1] == 'O' and previous[1] !='O':
                            NamedEntities.append((string, previous[1]))
                            previous = ("", 'O')
                            string = ""

        answers = []
        if "where" in question[1]:
                answers = namedEntitySearch(NamedEntities, "LOCATION")+namedEntitySearch(NamedEntities, "ORGANIZATION")
        elif "who" in question[1]:
                answers = namedEntitySearch(NamedEntities, "PERSON")+namedEntitySearch(NamedEntities, "ORGANIZATION")
        elif "when" in question[1] or "year" in question[0]:
                answers = namedEntitySearch(NamedEntities, "DATE")+namedEntitySearch(NamedEntities, "TIME")
        elif "how" in question[1] or "population" in question[0]:
                answers = namedEntitySearch(NamedEntities, "PERCENT")+namedEntitySearch(NamedEntities, "MONEY")+namedEntitySearch(NamedEntities, "TIME")
        elif "name" in question[0]:
                answers = namedEntitySearch(NamedEntities, "ORGANIZATION")+namedEntitySearch(NamedEntities, "LOCATION")+namedEntitySearch(NamedEntities, "PERSON")
        elif "date" in question[0] or "time" in question[0]:
                answers = namedEntitySearch(NamedEntities, "DATE")+namedEntitySearch(NamedEntities, "TIME")
        #elif "is" in question[1] and question[1][question[1].index("is")-1] == "what":
        #		answers = [] 
        else:
                answers = namedEntitySearch(NamedEntities, "ORGANIZATION")[:2]+namedEntitySearch(NamedEntities, "LOCATION")[:2]+namedEntitySearch(NamedEntities, "PERSON")[:2]

        #find noun phrases
        nounphrases = []
        tempphrase = []
        print question
        for sentence in pos_tag:
            for i in range(len(sentence)):
                    taggedword = sentence[i]
                    word = taggedword[0]
                    tag = taggedword[1]
                    if tag in ["NN", "POS", "JJ", "JJR", "JJS", "NNS"]:
                            tempphrase.append(word)
                    else:
                            nounphrases.append(" ".join(tempphrase))
                            tempphrase = []
        nounphrases = sorted(set(nounphrases), key = nounphrases.count, reverse=True)
        nounphrases = [n for n in nounphrases if not n in ["<",">", "P", "the", '', "'s"]]
        nounphrases = [n for n in nounphrases if not n in question[0]]
        answers += nounphrases
        print sorted(set(answers), key=lambda x: answers.index(x))[:10]
        return sorted(set(answers), key=lambda x: answers.index(x))[:10]

def namedEntitySearch(NamedEntities, term):
    entityList = []
    for element in NamedEntities:
        if element[1] == term:
            entityList.append(element[0])
    return entityList


#question processing: remove stop words from question
with codecs.open("qadata/train/questions.txt", encoding = 'utf-8') as question_file:
	question_list = list(filter(None,question_file.read().split("\n")))
	questions = {}
	for i in range(0, len(question_list), 2):
		#Lower case everything, tokenize, then remove punctuation, and then remove stopwords
		qnum = question_list[i].split()[-1]
		question = preprocess(question_list[i+1], getstopwords=True)
		questions[qnum] = question
        print questions[qnum]
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
                                parsedtextlist.append(preprocess(tempstring,text =True))
                                #print parsedtextlist
                        #potential bug the stopword removed the word "won".
                       # print questions[qnum]
                        #print parsedtextlist
                        bestngram = find_best_passages(parsedtextlist, questions[qnum][0], qidlist)
        				#print bestngram
                        #qidtextTuple = zip(qidlist, parsedtextlist[1:])
        				#print(qidtextTuple)

                        #answer formation
                        #Find the sentence that gave highest score (some way of tracking this)
                        NamedEntities = []
                        PosTag =[]
                        #ideally we want to pass into the entire center
                        for best_sentence in bestngram:
                                #stanford entity tag
                                best_ne = st.tag(best_sentence)
                                #best_ne =[]
                                pos_tag = nltk.pos_tag(best_sentence)
                                NamedEntities.append(best_ne)
                                PosTag.append(pos_tag)
                        answers = heuristic_list(NamedEntities, PosTag, questions[qnum])
                                        
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
