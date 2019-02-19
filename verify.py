import model_cos
import pandas as pd

def verify(model, name, candidates):
    all_names = model.uv.columns.tolist()
    print("#### verification for %s ####" % (name) )
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
        same_rating = temp[temp[name] == temp[c]]
        print("%s all: %d, same ratings: %d, percentage: %.2f" % (c, temp.shape[0], same_rating.shape[0], same_rating.shape[0]/temp.shape[0]))

model = model_cos.GC_Model()
public_campsites = pd.read_csv('public_campsites_ready.csv', encoding='utf-8')
names = public_campsites['name'].tolist()
for name in names:
    model.get_recommendations({'name': name}, verify)
