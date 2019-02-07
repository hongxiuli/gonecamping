#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Thu Jan 24 23:10:21 2019

@author: hongxiu
"""
import numpy as np
import pandas as pd
import nltk
from nltk.corpus import stopwords
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity
from gensim.models import Word2Vec, Doc2Vec
import gensim

stop_words = stopwords.words('english')

#############utility functions
def stem_sentence(sentence, stemmer):
    stemmed = []
    sentence = sentence.split(' ')
    for word in sentence:
        stemmed.append(stemmer.stem(word))
    return ' '.join(stemmed)


def remove_stopwords(rev):
    rev_new = " ".join([i for i in rev if i not in stop_words])
    return rev_new

def activity_str_to_set(a):
    result = set()
    temp = a.split(',')
    for t in temp:
        t = t.replace('Activities In or Around the Campground:', '').strip().lower()
        if(len(t)>0):
            result.add(t)
    return result

def process_activities(pv_campground):
    activities = set()
    for i in range(pv_campground.shape[0]):
        temp = activity_str_to_set(pv_campground.iloc[i]['activities'])
        activities = activities.union(temp) 
                
    #add the columns
    for a in activities:
        pv_campground[a] = 0
    
    for i in range(pv_campground.shape[0]):
        temp = activity_str_to_set(pv_campground.iloc[i]['activities'])
        for t in temp:
            pv_campground.at[i, t] = 1
    
    return activities



###### STEP 1: load the campsite into memory 
        
pv_campground = pd.read_csv("private_campsites.csv", encoding='utf-8') 
#pb_campground = pd.read_csv("public_campsites.csv", encoding='utf-8') 



###### SETP 2: process activities to binary columns
activities = process_activities(pv_campground)
#activities = process_activities(pb_campground)
#pv_campground.to_csv("private_feature.csv",encoding='utf-8')





###### SETP 3: Reviews
campsite_review = pd.read_csv("private_campsites_reviews.csv", encoding='utf-8') 
review = campsite_review[['name','text']]
review.dropna(inplace=True)
names = review['name'].unique().tolist()
temp_dict = {
    'name': [],
    'review': []
}
for name in names:
    temp = review.loc[review['name'] == name]
    reviews_for_name = ' ' + ' '.join(temp['text'].tolist())
    temp_dict['name'].append(name)
    temp_dict['review'].append(reviews_for_name)
reviews_all = pd.DataFrame(temp_dict)
pv_campground_rv = pv_campground.merge(reviews_all, on='name')
pv_campground_rv['ov_rv'] = pv_campground_rv['overview'] + pv_campground_rv['review']

##### SETP 4: add overview and review together
ov_rv =pv_campground_rv[['ov_rv']]
ov_rv['ov_rv'] = ov_rv['ov_rv'].str.replace("[^a-zA-Z#]", " ")
ov_rv_done = [remove_stopwords(r.split()) for r in ov_rv['ov_rv']]
# make entire text lowercase and stem them
stemmer = nltk.stem.PorterStemmer()
ov_rv_done = [stem_sentence(r, stemmer).lower() for r in ov_rv_done]


##### SETP 5.1: TFIDF vectorize text and pre-calculate the cosine similarity
tfidf = TfidfVectorizer(stop_words='english',)
tfidf_matrix = tfidf.fit_transform(ov_rv_done)
cosine_tfidf = cosine_similarity(tfidf_matrix, tfidf_matrix)

#### STEP 5.2 Word2Vec
ov_rv_tokenized = [nltk.word_tokenize(sent) for sent in ov_rv_done]
word2vec = Word2Vec(ov_rv_tokenized, min_count=2)  
vocabulary = word2vec.wv.vocab
count=0
def get_vec_for_doc(doc):
    global count
    temp = []
    for word in doc:
        try:
            temp.append(word2vec.wv[word])
        except KeyError as k:
            count+=1
            #print(k)
    result = np.mean(temp, axis=0)
    return result
ov_rv_w2v = [ get_vec_for_doc(doc) for doc in ov_rv_tokenized]
cosine_w2v = cosine_similarity(ov_rv_w2v, ov_rv_w2v)

#### STEP 5.3 Doc2Vec
class LabeledLineSetence():
    def __init__(self, doc_list, labels_list):
       self.labels_list = labels_list
       self.doc_list = doc_list
    def __iter__(self):
        for idx, doc in enumerate(self.doc_list):
            yield gensim.models.doc2vec.TaggedDocument(words=doc,tags=[self.labels_list[idx]])
labels = pv_campground_rv['name'].tolist()
it = LabeledLineSetence(ov_rv_tokenized, labels)
doc2vec = Doc2Vec(size=100, window=10, min_count=5, workers=11,alpha=0.025, iter=20)
doc2vec.build_vocab(it)
doc2vec.train(it,total_examples=doc2vec.corpus_count, epochs=doc2vec.iter)
ov_rv_d2v = [doc2vec[name] for name in labels]
cosine_d2v = cosine_similarity(ov_rv_d2v, ov_rv_d2v)

#### STEP 5.4 Comparison
w2v_minus_d2v = cosine_w2v-cosine_d2v
tf_minus_d2v = cosine_tfidf-cosine_d2v

#print(ov_rv.loc[8])
#ov_rv.to_csv("ov_rv.csv",sep='\t', encoding='utf-8')


##### STEP 6: pre-calculate cosine similarity for binary columns
bin_cols = ['Accessible facilities', 'Credit/debit cards', 'Dumping (station or mobile)',
          'Group camping','Internet (WiFi at site)','Laundromat','Pet-friendly',
          'Planned activities/events','Playground','Pull-thru sites','Rec hall/games room',
          'Restaurant/snack bar','Store','Swimming (outdoor pool)','Toilets/showers (comfort station)',
          'Boating (marina, boat launch, or docks)','Cable TV (at site)','Controlled access',
          'Hot tub','Internet (hot spot)','Propane','Swimming (indoor pool)','Swimming (lake, river, or beach)',
          'Toilets (pit/outhouse)'
          ]
bin_cols += list(activities)
bin_list =pv_campground_rv[bin_cols]
coss_binary_vars = cosine_similarity(bin_list, bin_list)

print("****model is ready")


##### STEP 7: Summary of Reviews using TextRank
from gensim.summarization.summarizer import summarize
#from gensim.summarization import keywords

pv_campground_rv['sum_rv']=pv_campground_rv['review']
for i in range(pv_campground_rv.shape[0]):
    try:
        temp = summarize(str(pv_campground_rv['review'].iloc[i]), word_count=80)
        pv_campground_rv.at[i, 'sum_rv']=temp
    except ValueError:
        pv_campground_rv.at[i, 'sum_rv']=pv_campground_rv['review'].iloc[i]
        pass

for i in range(pv_campground_rv.shape[0]):
    if(pv_campground_rv.iloc[i]['sum_rv'] == ''):
        pv_campground_rv.at[i, 'sum_rv']=pv_campground_rv['review'].iloc[i]


def get_recommendations(data):
    name = data.pop('name')
    
    row = pv_campground_rv.loc[pv_campground_rv['name']==name]
    print("look for index %d for name %s" %(row.index[0], name))
    
    #get the cosine similarity for binary values
    bin_similarity = coss_binary_vars[row.index[0]]
    
    #get the cosine similarity for text values
    text_similarity = cosine_d2v[row.index[0]]
    
    similarity = 0.5*bin_similarity + 0.5*text_similarity
    
    return_cols = ['name','address', 'phone', 'sum_rv', 'latitude', 'longitude']
    df = pv_campground_rv[return_cols].copy()
    df['score'] = list(similarity)

    #filter
    temp = pv_campground_rv
    for col in data.keys():
        temp = temp.loc[temp[col]==1]
    valid_indexes = temp.index.tolist()
    print("after filtering, we get:")
    print(valid_indexes)

    df_filtered = df.iloc[valid_indexes]

    df_sorted = df_filtered.sort_values(by='score', ascending=False)
    top = df_sorted.iloc[:6]

    result = top.to_dict('records')
    return result















