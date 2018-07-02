import gensim
import os
import re
import pickle, json
import numpy as np
from stop_words import get_stop_words
from gensim.parsing.porter import PorterStemmer
from gensim.corpora import Dictionary
from gensim import corpora, models, similarities
from difflib import SequenceMatcher

'''
Tool to read all the .txt file under one directory and store them into list
'''
# grab all the file names of texts
file_names = []
for f in os.listdir('./concepts'):
    if f.endswith(".txt"):
        file_names.append(f)
        
# read all the txt into list
documents = []
topic_names = []
for file_name in file_names:
    with open('./concepts/' + file_name) as f:
        topic_names.append(f.readline()) 
        documents.append(f.read())
In [3]:

'''
Preprocessing the documents, by low_casing it and stemming it
'''
def preprocess_doc(doc):
    #  removing all the stop words and punctuations and digits
    stop_words = get_stop_words(language='en')
    regex = re.compile('[,\.!?()1234567890]')
    doc = ' '.join([word for word in regex.sub(' ', doc.lower()).split() if not word in stop_words and len(word) > 1])
    
    return doc

def preprocess_documents(documents):
    # preprocess each doc
    documents = [preprocess_doc(doc) for doc in documents]

    # stem the documents
    stemmer = PorterStemmer()
    documents = stemmer.stem_documents(documents)

    # split all the documents into list of tokens
    documents = [doc.split() for doc in documents]
    
    return documents

documents = preprocess_documents(documents)

'''
Preparing dictionary for documents
'''
no_below = 5
dictionary = Dictionary(documents=documents)
dictionary.filter_extremes(no_below=no_below)
dictionary.compactify()
dictionary.save('./preprocessed_data/concept_dictionary.dict')
print('Dictionary generated, with a vocabulary of: ', len(dictionary))

'''
Convertion from documents to corpus
'''
def tokenize_documents(documents, dictionary):
    documents = [dictionary.doc2bow(doc) for doc in documents]
    return documents

documents = tokenize_documents(documents, dictionary)

'''
Do LSI modelling
'''
# do tfidf first
tfidf = models.TfidfModel(documents)

# create lsi model
lsi = models.LsiModel(tfidf[documents], id2word=dictionary, num_topics=350)
index = similarities.MatrixSimilarity(lsi[documents])

'''
What is needed to be save and reloaded is: LSI model, Index, Dictionary, Topic_names
'''
# saving lsi model
lsi.save(fname='./preprocessed_data/concept_model.lsi')

# saving index
index.save('./preprocessed_data/concept.index')

# saving topic_names
with open('./preprocessed_data/topic_names', 'wb') as f:
    pickle.dump(topic_names, f)
    
'''
Rearranging sequence of topic names, and create a matching dict
'''
# getting new topic structure
with open ('./preprocessed_data/parent_to_child', 'rb') as f:
    bob_topics = pickle.load(f)
    
# getting new sequence
new_topics = []
for parent in bob_topics:
    for topic in parent[1]:
        new_topics.append(topic[0])

# prepare string similarity checking
def similar(a, b):
    return SequenceMatcher(None, a, b).ratio()

# creating matching dict
convertor = dict()
for i in range(len(topic_names)):
    scores = np.zeros(len(new_topics))
    for j in range(len(new_topics)):
        scores[j] = similar(topic_names[i], new_topics[j])
    convertor[i] = scores.argmax()

# store the convertor
with open('./preprocessed_data/parent_to_child.pickle', 'wb') as handle:
    pickle.dump(a, handle, protocol=pickle.HIGHEST_PROTOCOL)

