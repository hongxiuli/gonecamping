#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Thu Jan 24 23:10:21 2019

@author: hongxiu
"""
import numpy as np
import pandas as pd
import nltk
import os
from nltk.corpus import stopwords
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity
from gensim.models import Word2Vec, Doc2Vec
from gensim.summarization.summarizer import summarize
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


class LabeledLineSetence():
    def __init__(self, doc_list, labels_list):
        self.labels_list = labels_list
        self.doc_list = doc_list
    def __iter__(self):
        for idx, doc in enumerate(self.doc_list):
            yield gensim.models.doc2vec.TaggedDocument(words=doc,tags=[self.labels_list[idx]])

############main class for model
class GC_Model():
    def __init__(self):
        
        ###### load private and public campsites and merge them
        print('load files')
        self.all_campground = pd.read_csv("all_campsites_ready.csv", encoding='utf-8')
        not_useful = ['activities', 'ov_rv', 'review', 'address','overview']
        self.all_campground.drop(columns=not_useful, inplace=True)
        #for debugging purpose
        global all_campground
        all_campground= self.all_campground
        
        ##### prepare Doc2Vec similarity
        print('prepare cosine_d2v')
        self._cosine_d2v()
    

        ##### pre-calculate cosine similarity for binary columns
        print('calculate binary variables cosine similarity')
        non_bin_cols = [
          'name',
          'Max length (of RV)',
          'Maximum Amperage',
          'Min / Max (Daily)',
          'Seasonal Sites',
          'Total Sites',
          'latitude',
          'longitude',
          'phone',
          'sum_rv']
        
        all_cols = self.all_campground.columns.tolist()
        
        bin_cols = [ c for c in all_cols if c not in non_bin_cols]
        bin_list = self.all_campground[bin_cols]
        self.coss_binary_vars = cosine_similarity(bin_list, bin_list)
        
        #######facilities and activities to return
        self.fa = {
            'Dumping (station or mobile)' : 'Dumping Station',
            'Group camping' : 'Group Camping',
            'Laundromat' : 'Laundromat',
            'Pet-friendly' : 'Pet Friendly',
            'Playground' : 'Playground',
            'Toilets/showers (comfort station)' : 'Shower',
            'horseback riding' : 'Horseback Riding',
            'fishing' : 'Fishing',
            'boat rental (non-motorized)' : 'Boat Rental(non-motorized)',
            'whitewater rafting' : 'Whitewater Rafting',
            'walking/hiking trails' : 'Hiking',
            'cycling' : 'Biking'
        }
        
        ######load user reviews
        uv = pd.read_csv('public_campsites_user_reviews_more_than_one.csv', encoding='utf-8')
        self.uv = uv.fillna(0)
        
    ##### PUBLIC FUNCTIONS #####
    def get_recommendations(self, data, recommendation_postFunc = None):
        name = data.pop('name')
        
        row = self.all_campground.loc[self.all_campground['name']==name]
        print("look for index %d for name %s" %(row.index[0], name))
        
        #get the cosine similarity for binary values
        bin_similarity = self.coss_binary_vars[row.index[0]]
        
        #get the cosine similarity for text values
        text_similarity = self.cosine_d2v[row.index[0]]
        
        #overall similarity is a weighted sum of binary variables' similarity and text similarity
        similarity = 0.5*bin_similarity + 0.5*text_similarity
        
        return_cols = ['name', 'sum_rv', 'latitude', 'longitude']
        df = self.all_campground[return_cols].copy()
        df['score'] = list(similarity)
        df['facilities_activities'] = ''

        #filtering
        temp = self.all_campground
        for col in data.keys():
            temp = temp.loc[temp[col]==1]
        valid_indexes = temp.index.tolist()
        df_filtered = df.iloc[valid_indexes]

        #rank
        df_sorted = df_filtered.sort_values(by='score', ascending=False)
        top = df_sorted.iloc[:6]
        
        #add facilities and activities
        all_indexes = top.index.tolist()
        for i in all_indexes:
            features = []
            for feature in self.fa.keys():
                if(self.all_campground.iloc[i][feature] == 1):
                    features.append(self.fa[feature])
            if(len(features)>0):
                top.at[i, 'facilities_activities'] = ', '.join(features)
        
        if(recommendation_postFunc is not None):
            recommendation_postFunc(self, name, top['name'].tolist())

        result = top.to_dict('records')
        return result

    ##### PRIVATE FUNCTIONS #####
    
    def _cosine_d2v(self):
        model_path = './models/cosine_d2v.npy'
        if(os.path.isfile(model_path)):
            print('loading cosine_d2v model from %s' % (model_path))
            self.cosine_d2v = np.load(model_path)
        else:
            self._tokenize_ov_rv()
            self._doc2vec_similarity()
            print("calculated and saving cosine_d2v model")
            np.save(model_path, self.cosine_d2v)
    
    def _doc2vec_similarity(self):
        print('calculating cosine_d2v')
        labels = self.all_campground['name'].tolist()
        it = LabeledLineSetence(self.ov_rv_tokenized, labels)
        doc2vec = Doc2Vec(size=100, window=10, min_count=5, workers=11,alpha=0.025, iter=20)
        doc2vec.build_vocab(it)
        doc2vec.train(it,total_examples=doc2vec.corpus_count, epochs=doc2vec.iter)
        ov_rv_d2v = [doc2vec[name] for name in labels]
        self.cosine_d2v = cosine_similarity(ov_rv_d2v, ov_rv_d2v)

    def _get_vec_for_doc(self, word2vec, doc):
        temp = []
        for word in doc:
            try:
                temp.append(word2vec.wv[word])
            except KeyError:
                pass
        result = np.mean(temp, axis=0)
        return result
    
    def _preprocess_private_campsites(self):
        pv_campground = pd.read_csv("private_campsites.csv", encoding='utf-8') 
        self._process_private_activities(pv_campground)
        reviews_all = self._process_private_reviews()
        pv_campground_rv = pv_campground.merge(reviews_all, on='name')
        pv_campground_rv['ov_rv'] = pv_campground_rv['overview'] + pv_campground_rv['review']
        pv_campground_rv.to_csv('private_campsites_ready.csv', encoding='utf-8', header=True, index=False)
    
    def _preprocess_merge_and_summary(self):
        print('=====load files')
        pv_campground = pd.read_csv("private_campsites_ready.csv", encoding='utf-8') 
        pb_campground = pd.read_csv('public_campsites_ready.csv', encoding='utf-8')
        all_campground = pv_campground.append(pb_campground)
        
        print('=====fill na')
        #fillna: empty string for reveiws
        all_campground['review'] = all_campground['review'].fillna('')
        #fillna: other features with 0
        all_campground = all_campground.fillna(0)
        
        ##### STEP 7: Summary of Reviews using TextRank
        print('=====summary of reviews')
        all_campground['sum_rv']=all_campground['review']
        for i in range(all_campground.shape[0]):
            try:
                temp = summarize(str(all_campground['review'].iloc[i]), word_count=80)
                all_campground.at[i, 'sum_rv']=temp
            except ValueError:
                #self.all_campground.at[i, 'sum_rv']=self.all_campground['review'].iloc[i]
                pass
        for i in range(all_campground.shape[0]):
            if(all_campground.iloc[i]['sum_rv'] == ''):
                all_campground.at[i, 'sum_rv']=all_campground['review'].iloc[i]
        
        print('=====write file')
        all_campground.to_csv('all_campsites_ready.csv',encoding='utf-8', header=True, index=False)

    def _process_private_activities(self, pv_campground):
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

    def _process_private_reviews(self):
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
        return pd.DataFrame(temp_dict)
    
    def _tfidf_similarity(self, data):
        tfidf = TfidfVectorizer(stop_words='english',)
        tfidf_matrix = tfidf.fit_transform(data)
        cosine_tfidf = cosine_similarity(tfidf_matrix, tfidf_matrix)
        return cosine_tfidf
    
    def _tokenize_ov_rv(self):
        print('tokenize ov_rv')
        ov_rv = self.all_campground[['ov_rv']]
        ov_rv['ov_rv'] = ov_rv['ov_rv'].str.replace("[^a-zA-Z#]", " ")
        ov_rv_done = [remove_stopwords(r.split()) for r in ov_rv['ov_rv']]
        #make entire text lowercase and stem them
        stemmer = nltk.stem.PorterStemmer()
        ov_rv_done = [stem_sentence(r, stemmer).lower() for r in ov_rv_done]
        self.ov_rv_tokenized = [nltk.word_tokenize(sent) for sent in ov_rv_done]

    def _w2vec_similarity(self):
        word2vec = Word2Vec(self.ov_rv_tokenized, min_count=2)  
        #vocabulary = word2vec.wv.vocab
        
        ov_rv_w2v = [self._get_vec_for_doc(word2vec, doc) for doc in self.ov_rv_tokenized]
        cosine_w2v = cosine_similarity(ov_rv_w2v, ov_rv_w2v)
        return cosine_w2v


#Test code for adding web features&activities of campground
#pv_campground_rv= self.pv_campground_rv
#model = GC_Model()
#temp = pv_campground_rv[pv_campground_rv.columns[17:96]].mean()




'''
pb_campground = pd.read_csv("public_campsites_googleinfo.csv", encoding='utf-8') 
pb_campground.mean()
###
pb_campground = pd.read_csv("public_campsites_latlng.csv", encoding='utf-8') 
pb_campground = pd.read_csv("public_campsites_reviews.csv", encoding='utf-8') 
pb_campground = pd.read_csv("public_campsites_user_reviews.csv", encoding='utf-8') 
pb_campground.shape
pb_campground = pd.read_csv("public_campsites_user_reviews_more_than_one.csv", encoding='utf-8') 
pb_campground.shape

'''























