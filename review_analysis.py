"""
Pre-process user reviews:
1. combine individual reviews from ./reviews directory to public_campsites_user_reviews.csv
2. remove users that only have one single review on one single campsites, results stored in public_campsites_user_reviews_more_than_one.csv
"""
import os
import pandas as pd
import math

def combine_user_reviews(files=None):
    """
    Combine user reveiws to a single csv file
    @param files: if provided, only combine these files. otherwise combine everything under ./reviews directory
    @param df
    """
    if(files is None):
        files = os.listdir("./reviews")
    names = ['user'] + [f.replace('.csv', '') for f in files]
    df = pd.DataFrame(columns=names)
    df.set_index("user", inplace = True)
    count=1
    for f in files:
        print("processing %s, %d out of %d" %(f, count, len(files)))
        temp = pd.read_csv('./reviews/'+f, encoding='utf-8')
        users = df.index
        for index, row in temp.iterrows():
            #if(row['user'] in users):
            #    print('%s has more than 1 comment' % row['user'])
            df.at[row['user'], row['name']] = row['stars']
        count += 1
        if(count%10==0):
            df.to_csv('./data/public_campsites_user_reviews.csv', encoding='utf-8', index=True, header=True)
    print('writing to csv')
    df.to_csv('./data/public_campsites_user_reviews.csv', encoding='utf-8', index=True, header=True)

def remove_users_with_one_review():
    """
    Remove users who only left one review on one particular campsites.
    Result is written to public_campsites_user_reviews_more_than_one.csv
    """
    if(not os.path.isfile('./data/public_campsites_user_reviews.csv')):
        combine_user_reviews()
    df = pd.read_csv('./data/public_campsites_user_reviews.csv', encoding='utf-8')
    columns = df.columns.tolist()
    columns.remove('user')
    indexes_to_keep = []
    for index, row in df.iterrows():
        good = 0
        for c in columns:
            if(not math.isnan(row[c])):
                good +=1
                if(good > 1):
                    indexes_to_keep.append(index)
                    break
    
    df = df.iloc[indexes_to_keep]
    df.to_csv('./data/public_campsites_user_reviews_more_than_one.csv', encoding='utf-8', index=False, header=True)

"""
uncomment the following line and run this file
remove_users_with_one_review()
"""