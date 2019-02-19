import model_cos
import pandas as pd

rating_percentage = {}

def verify(model, name, candidates):
    global rating_percentage
    all_names = model.uv.columns.tolist()
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

        temp = model.uv[[name, c]]
        temp = temp.loc[(temp[name]>0) & (temp[c]>0)]
        if(temp.shape[0] == 0):
            print("there is not enough reviews for %s and %s" % (name, c))
            continue
        rating_total += temp.shape[0]

        #same rating:
        #same_rating += temp[temp[name] == temp[c]].shape[0]

        #similar rating:
        temp = temp.loc[abs(temp[name] - temp[c]) <= 1]
        similar_rating += temp.shape[0]
    if(rating_total == 0):
        print("there is not enough reviews for %s" % (name))
    else:
        rating_percentage[name] = similar_rating/rating_total
        print("all: %d, same ratings: %d, percentage: %.2f" % (rating_total, similar_rating, similar_rating/rating_total))

model = model_cos.GC_Model()
public_campsites = pd.read_csv('public_campsites_ready.csv', encoding='utf-8')
names = public_campsites['name'].tolist()
for name in names:
    model.get_recommendations({'name': name}, verify)
values = list(rating_percentage.values())
print("overal user rating percentage for all recommended sites is: %.2f" %(sum(values)/len(values)))
