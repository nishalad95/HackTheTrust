import gensim
import os
import re
import pickle
import numpy as np
from stop_words import get_stop_words
from gensim.parsing.porter import PorterStemmer
from gensim.corpora import Dictionary
from gensim import corpora, models, similarities

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

def tokenize_documents(documents, dictionary):
    documents = [dictionary.doc2bow(doc) for doc in documents]
    return documents

def get_relevent_video_ids(query, top_n=1):
    # load lsi model
    lsi = models.LsiModel.load('./preprocessed_data/video_model.lsi')

    # load index
    index = similarities.MatrixSimilarity.load('./preprocessed_data/video.index')

    # load dictionary
    dictionary = Dictionary.load('./preprocessed_data/video_dictionary.dict')
    
    # preprocess query
    query = tokenize_documents(preprocess_documents([query]), dictionary)
    
    # index query
    sims = index[lsi[query]]
    
    # sort similarity
    sims = [sorted(enumerate(sim), key=lambda item: -item[1]) for sim in sims]
    
    # return index result and top_n topic ids
    sims = [[list(sim[i]) for i in range(top_n)] for sim in sims]
    
    return sims

def give_video_names(list_of_ids):
    # load topic_names
    with open ('./preprocessed_data/video_names', 'rb') as f:
        video_names = pickle.load(f)
        
    # display
    return([[video_names[i] for i in ids] for ids in list_of_ids])

def update_progress(sims, t_len):
    # update to progress
    if os.path.exists("./preprocessed_data/progress.npy"):
        progress = np.load("./preprocessed_data/progress.npy")
        for sim in sims:
            for i in sim:
                progress[i[0]] += i[1]
        np.save('./preprocessed_data/progress', progress)
    else:
        #progress = np.zeros(t_len)
        progress = np.random.rand(t_len) * 0.2
        for sim in sims:
            for i in sim:
                progress[i[0]] += i[1]
        np.save('./preprocessed_data/progress', progress)
            
def clear_progress():
    # get the length of the progress
    with open ('./preprocessed_data/topic_names', 'rb') as f:
        topic_names = pickle.load(f)
        t_len = len(topic_names)
        
    # create empty progress list
    #progress = np.zeros(t_len)
    progress = np.random.rand(t_len) * 0.2
    np.save('./preprocessed_data/progress', progress)

def retrieve_progress():
    # generating initial progress if no progress was there
    if not os.path.exists("./preprocessed_data/progress.npy"):
        clear_progress()
    
    # grab and return progress data
    progress = np.load("./preprocessed_data/progress.npy")
    
    # thresholding to 5 levels
    for i in range(len(progress)):
        if progress[i] < 0.2:
            progress[i] = 0
        elif progress[i] < 0.4:
            progress[i] = 1
        elif progress[i] < 0.6:
            progress[i] = 2
        elif progress[i] < 0.8:
            progress[i] = 3
        else:
            progress[i] = 4
    
    return progress

def get_relevent_topic_ids(query, top_n=5, is_update=True):
    # load lsi model
    lsi = models.LsiModel.load('./preprocessed_data/concept_model.lsi')

    # load index
    index = similarities.MatrixSimilarity.load('./preprocessed_data/concept.index')

    # load dictionary
    dictionary = Dictionary.load('./preprocessed_data/concept_dictionary.dict')
    
    # preprocess query
    query = tokenize_documents(preprocess_documents([query]), dictionary)
    
    # index query
    sims = index[lsi[query]]
    
    # sort similarity
    sims = [sorted(enumerate(sim), key=lambda item: -item[1]) for sim in sims]
    
    # return index result and top_n topic ids
    sims = [[list(sim[i]) for i in range(top_n)] for sim in sims]
    
    # normalize sims
    for j in range(len(sims)):
        tmp_sum = 0
        for sim in sims[j]:
            tmp_sum += sim[1]
        for i in range(len(sims[j])):
            sims[j][i][1] /= tmp_sum
    
    # updating progress if necessary
    if is_update:
        with open ('./preprocessed_data/topic_names', 'rb') as f:
            topic_names = pickle.load(f)
            t_len = len(topic_names)
        update_progress(sims, t_len)
    
    return sims

def display_topics(list_of_ids):
    # load topic_names
    with open ('./preprocessed_data/topic_names', 'rb') as f:
        topic_names = pickle.load(f)
        
    # display
    print([[topic_names[i] for i in ids] for ids in list_of_ids])

def video_complete_function(query, top_n=1):
    sims = get_relevent_video_ids(query, top_n=top_n)
    list_of_ids = [[i[0] for i in sim]for sim in sims]
    return give_video_names(list_of_ids)