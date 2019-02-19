"""
This module calculates the average percentage of similar user reviews for our recommended campsites VS the target campsite.
The result serves as a metric to evaluate the performance of our recommendation algorithm. 
"""
import model_cos
import pandas as pd

def verify(model, name, candidates):
    """
    Callback function to be called in model.get_recommendations to evaluate percentage of similar user reviews between name and candidates
    @param model: a GC_Model() object
    @param name:  the name of the campsite based on which to recommend other campsites
    @param candidates: the recommended campsites in a DataFrame
    """
    global rating_percentage
    print("#### verification for %s ####" % (name) )
    rating_total = 0
    similar_rating = 0
    for c in candidates:
        if(c == name):
            continue
        if(name not in all_names):
            print("%s is not in the reviews file" %(name))
            continue
        if(c not in all_names):
            print("%s is not in the reviews file" %(c))
            continue

        temp = uv[[name, c]]
        temp = temp.loc[(temp[name]>0) & (temp[c]>0)]
        if(temp.shape[0] == 0):
            print("there is not enough reviews for %s and %s" % (name, c))
            continue
        rating_total += temp.shape[0]

        #similar rating:
        temp = temp.loc[abs(temp[name] - temp[c]) <= 1]
        similar_rating += temp.shape[0]
    if(rating_total == 0):
        print("there is not enough reviews for %s" % (name))
    else:
        rating_percentage[name] = similar_rating/rating_total
        print("all: %d, same ratings: %d, percentage: %.2f" % (rating_total, similar_rating, similar_rating/rating_total))

rating_percentage = {}

#create the model
model = model_cos.GC_Model()

#load all public campsites names
public_campsites = pd.read_csv('./data/public_campsites_ready.csv', encoding='utf-8')
names = public_campsites['name'].tolist()

#load user reviews
uv = pd.read_csv('./data/public_campsites_user_reviews_more_than_one.csv', encoding='utf-8')
uv = uv.fillna(0)
all_names = uv.columns.tolist()

for name in names:
    model.get_recommendations({'name': name}, verify)
values = list(rating_percentage.values())
print("overal user rating percentage for all recommended sites is: %.2f" %(sum(values)/len(values)))
