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


campsite_list = pd.read_csv("private_campsites.csv", encoding='utf-8') 

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


stop_words = stopwords.words('english')

##############Reviews
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

campsite_list_rv = campsite_list.merge(reviews_all, on='name')

campsite_list_rv['ov_rv'] = campsite_list_rv['overview'] + campsite_list_rv['review']

#####Preprocessing 
ov_rv =campsite_list_rv[['ov_rv']]
ov_rv['ov_rv'] = ov_rv['ov_rv'].str.replace("[^a-zA-Z#]", " ")
# make entire text lowercase
ov_rv_done = [remove_stopwords(r.split()) for r in ov_rv['ov_rv']]
# make entire text lowercase and stem them
stemmer = nltk.stem.PorterStemmer()
ov_rv_done = [stem_sentence(r, stemmer) for r in ov_rv_done]

#print(stemmer.stem('working'))


tfidf = TfidfVectorizer(stop_words='english',)
tfidf_matrix = tfidf.fit_transform(ov_rv_done)
#print(tfidf.get_feature_names())



######add other binary features
bin_cols = ['Accessible facilities', 'Credit/debit cards', 'Dumping (station or mobile)',
          'Group camping','Internet (WiFi at site)','Laundromat','Pet-friendly',
          'Planned activities/events','Playground','Pull-thru sites','Rec hall/games room',
          'Restaurant/snack bar','Store','Swimming (outdoor pool)','Toilets/showers (comfort station)',
          'Boating (marina, boat launch, or docks)','Cable TV (at site)','Controlled access',
          'Hot tub','Internet (hot spot)','Propane','Swimming (indoor pool)','Swimming (lake, river, or beach)',
          'Toilets (pit/outhouse)'
          ]
bin_list =campsite_list_rv[bin_cols]
corr= bin_list.corr()

all_features = np.concatenate((tfidf_matrix.toarray(),bin_list),axis=1)
cosine_sim = cosine_similarity(all_features, all_features)

def get_recommendations(name):
    row = campsite_list_rv.loc[campsite_list_rv['name']==name]
    print("look for index %d for name %s" %(row.index[0], name))
    candidates = cosine_sim[row.index[0]]
    df = campsite_list_rv[['name']].copy()
    df['score'] = list(candidates)
    df_sorted = df.sort_values(by='score', ascending=False)
    top=df_sorted.iloc[:6].copy()
    return_cols = ['name','address', 'phone', 'overview']
    for col in return_cols:
        top[col] = campsite_list_rv[col]
    result = top.to_dict('records')
    return result

