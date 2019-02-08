import os
import pandas as pd
import math

def process_user_review(files=None, df = None):
    if(files is None):
        files = os.listdir("./reviews")
    names = ['user'] + [f.replace('.csv', '') for f in files]
    if(df is None):
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
            df.to_csv('public_campsites_user_reviews.csv', encoding='utf-8', index=True, header=True)
    print('writing to csv')
    df.to_csv('public_campsites_user_reviews.csv', encoding='utf-8', index=True, header=True)

def remove_user_with_one_review():
    df = pd.read_csv('public_campsites_user_reviews.csv', encoding='utf-8')
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
    df.to_csv('public_campsites_user_reviews_more_than_one.csv', encoding='utf-8', index=False, header=True)


#process_user_review()
remove_user_with_one_review()