# Lester Lee & Vincent Lin
import string
import re
import nltk
import codecs
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

stanford_classifier = '/Users/michaelqi/Downloads/stanford-ner-2017-06-09/classifiers/english.muc.7class.distsim.crf.ser.gz'
stanford_ner_path = '/Users/michaelqi/Downloads/stanford-ner-2017-06-09/stanford-ner.jar'
st = StanfordNERTagger(stanford_classifier,
                       stanford_ner_path, encoding='utf-8')


def preprocess(s, getstopwords=False, stopwords=False, text=False):
        # given s, tokenize and remove punctuation
        if text:
                s = nltk.sent_tokenize(s)
                s = [nltk.word_tokenize(e) for e in s]
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


def find_best_passages(textlist, questions, qidlist):
        best = []
        for i in range(len(textlist)):
                text = textlist[i]
                qid = qidlist[i]
                score = float(qid.split()[-1])
                best.append(compare_ngram(text, questions, score))
        best = list(filter(None, best))
        best = sorted(best, reverse=True)[:3]
        finallist = []
        for e in best:
        	for i in range(1, len(e)):
        		finallist.append(e[i])
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
                res = sum([freqs[word]
                          for word in freqs if word in wordbag]) * float(score)
                # only save the maximum
                if res == maximum:
                        maximum = res
                        frequency.append(e)
                        # frequency.append(e)
                elif res > maximum:
                        frequency = []
                        maximum = res
                        frequency.append(res)
                        frequency.append(e)
	return frequency


def heuristic_list(best_ne, pos_tag, question):
        NamedEntities = []
        for listoftokens in best_ne:
            previous = ("", 'O')
            string = ""
            for element in listoftokens:
                if element[0] not in question[0]:
                    if element[1] != 'O' and previous[1] != 'O':
                        if previous[1] == element[1]:
                            string += " " + element[0]
                            previous = element
                        elif previous[1] != 'O':
                            NamedEntities.append((string, previous[1]))
                            string = str(element[0])
                            previous = element
                    elif element[1] != 'O' and previous[1] == 'O':
                            string = str(element[0])
                            previous = element
                    elif element[1] == 'O' and previous[1] != 'O':
                            NamedEntities.append((string, previous[1]))
                            previous = ("", 'O')
                            string = ""

        answers = []
        if "where" in question[1]:
                answers = namedEntitySearch(
                    NamedEntities, "LOCATION") + namedEntitySearch(NamedEntities, "ORGANIZATION")
        elif "who" in question[1]:
                answers = namedEntitySearch(
                    NamedEntities, "PERSON") + namedEntitySearch(NamedEntities, "ORGANIZATION")
        elif "when" in question[1] or "year" in question[0] or "date" in question[0] or "time" in question[0]:
                answers = namedEntitySearch(
                    NamedEntities, "DATE") + namedEntitySearch(NamedEntities, "TIME")
        elif "how" in question[1] or "population" in question[0]:
                answers = namedEntitySearch(NamedEntities, "PERCENT") + namedEntitySearch(
                    NamedEntities, "MONEY") + namedEntitySearch(NamedEntities, "TIME")
        elif "name" in question[0]:
                answers = namedEntitySearch(NamedEntities, "ORGANIZATION") + namedEntitySearch(
                    NamedEntities, "LOCATION") + namedEntitySearch(NamedEntities, "PERSON")
        else:
                answers = namedEntitySearch(NamedEntities, "ORGANIZATION")[:2] + namedEntitySearch(
                    NamedEntities, "LOCATION")[:2] + namedEntitySearch(NamedEntities, "PERSON")[:2]

        # find noun phrases
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
        nounphrases = sorted(
            set(nounphrases), key=nounphrases.count, reverse=True)
        nounphrases = [n for n in nounphrases if not n in [
            "<", ">", "P", "the", '', "'s"]]
        nounphrases = [n for n in nounphrases if not n in question[0]]
        answers += nounphrases
        return sorted(set(answers), key=lambda x: answers.index(x))[:10]


def namedEntitySearch(NamedEntities, term):
    entityList = []
    for element in NamedEntities:
        if element[1] == term:
            entityList.append(element[0])
    return entityList


# question processing: remove stop words from question
with codecs.open("qadata/train/questions.txt", encoding='utf-8') as question_file:
	question_list = list(filter(None, question_file.read().split("\n")))
	questions = {}
	for i in range(0, len(question_list), 2):
		# Lower case everything, tokenize, then remove punctuation, and then
		# remove stopwords
		qnum = question_list[i].split()[-1]
		question = preprocess(question_list[i + 1], getstopwords=True)
		questions[qnum] = question
        print questions[qnum]
# questions is a dictionary {question#: (question tokens,stopwords)}

finalanswers = []

# passage retrieval
start = 0
end = 300
if len(sys.argv) >= 2:
    start = int(sys.argv[1])
    end = int(sys.argv[2])
for qnum in range(start,end):
        qnum = str(qnum)
        if qnum in questions:
        	docname = "top_docs.{}".format(qnum)
            textRE = re.compile(r'<TEXT>(.*)</TEXT>', re.DOTALL)
        	with codecs.open("topdocs/train/{}".format(docname), encoding='utf-8', errors='replace') as docfile:
        		# for each qid, make a string containing everything within <text> tags
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

                    best_passage = find_best_passages(parsedtextlist, questions[qnum][0], qidlist)

                    NamedEntities = []
                    PosTag =[]
                    for best_sentence in best_passage:
                            best_ne = st.tag(best_sentence)
                            pos_tag = nltk.pos_tag(best_sentence)
                            NamedEntities.append(best_ne)
                            PosTag.append(pos_tag)
                    answers = heuristic_list(NamedEntities, PosTag, questions[qnum])

                    finalanswers.append("qid {}".format(qnum))
                    finalanswers += answers

with open("predictions.txt", "w") as f:
        for a in finalanswers:
                f.write("{}\n".format(a))
