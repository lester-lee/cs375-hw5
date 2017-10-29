#Lester Lee & Vincent Lin
import string
from nltk.corpus import stopwords
from nltk import word_tokenize
import xml.etree.ElementTree as etree

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
        questions[qnum] =
        ([w for w in question if not w in stopword_list],
         [w for w in question if w in stopword_list])

#questions is a dictionary {question#: question tokens}
        
#passage retrieval
for qnum in questions:
    docname = "top_docs.{}".format(qnum)
    with open("topdocs/train/{}".format(docname)) as docfile:
        #parse docfile into etree
        docstring = str(docfile.read())
        tree = etree.fromstring(docstring)
        root = tree.getroot()[0]
        for doc in root:
            print(doc)
        #retrieve appropriate 10-grams
        #map each 10-gram to binary feature vector with question as bag of words
        #compute vector similarity score between question & each feature vector
        #retrieve the most-similar one


#answer formation
#Find the sentence that gave highest score (some way of tracking this)
#Stanford Named Entity Tagger
#Output 10 most relevant answers using most similar passage
#That's just reordering words / fitting info into sentence templates
