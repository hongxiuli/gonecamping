"""
Using Google Location API to get the reviews for the campsites
"""
import requests
import urllib.parse
import pandas as pd
import time
import math
import os

google_api_key = 'PUT GOOGLE API KEY HERE'
textsearch_url = 'https://maps.googleapis.com/maps/api/place/findplacefromtext/json?inputtype=textquery&key=' + google_api_key
textsearch_url += '&fields=name,rating,place_id'
textsearch_url += '&input='

phonesearch_url = 'https://maps.googleapis.com/maps/api/place/findplacefromtext/json?inputtype=phonenumber&key=' + google_api_key
phonesearch_url += '&fields=name,rating,place_id'
phonesearch_url += '&input=' 

detaillsearch_url = 'https://maps.googleapis.com/maps/api/place/details/json?key=' + google_api_key
detaillsearch_url += '&fields=rating,review,price_level'
detaillsearch_url += '&placeid='

geocoding_url = 'https://maps.googleapis.com/maps/api/geocode/json?key=' + google_api_key
geocoding_url += '&address='

def get_google_api_response(url):
    res = requests.get(url)
    if(res.status_code==200):
        return res.json()
    else:
        print("status: %d" % res.status_code)
        raise Exception(res.content)

def get_place_info(name, address=None, phone=None):
    """
    Locate the object using Google Place API based on
        name, if not found, then
        address, if not found, then
        phone, if not found, then None
    @param name: place name to be searched
    @param address: address to be searched
    @param phone: phone to be searched
    @return: dictionary from Google's place API call
    """
    print("=========================================")
    #try name first
    url = textsearch_url + urllib.parse.quote_plus(name)
    print("get by name: %s, url: %s" % (name, url))
    result = get_google_api_response(url)
    if(len(result['candidates'])>0 and result['candidates'][0]['rating']>0):
        temp = result['candidates'][0]
        temp['by'] = 'name'
        return temp
    
    if(phone is not None and not math.isnan(phone)):
        #try phone second
        phone = phone.replace('-','')
        phone = '+1'+phone
        url = phonesearch_url + urllib.parse.quote_plus(phone)
        print("get by phone: %s, url: %s" % (phone, url))
        result = get_google_api_response(url)
        if(len(result['candidates'])>0 and result['candidates'][0]['rating']>0):
            temp = result['candidates'][0]
            temp['by'] = 'phone'
            return temp
    else:
        return {
                'name': None,
                'place_id': None,
                'rating': None,
                'by': 'name'
            }

    if(address is not None and not math.isnan(address)):
        #try address finally
        # this typically does not generate any result on ratings and has a different rating on
        url = textsearch_url + urllib.parse.quote_plus(address)
        print("get by address: %s, url: %s" % (address, url))
        result =  get_google_api_response(url)
        if(len(result['candidates'])>0):
            temp = result['candidates'][0]
            temp['by'] = 'address'
            return temp
        else:
            return {
                'name': None,
                'place_id': None,
                'rating': None,
                'by': 'address'
            }
    else:
        return {
                'name': None,
                'place_id': None,
                'rating': None,
                'by': 'phone'
            }
    
def get_all_basic_info(df, output_fn):
    """
    get the basic information for a place especailly the place_id, 
    which will be used in another google API call to get the reviews.
    A csv file will be generated to contain the place_id along with other information
    @param df: DataFrame containing campsite basic information including name, address, phone
    @param output_fn: the file name of the csv file to be generated
    """
    result = {}
    keys = ['name', 'place_id', 'rating', 'by']
    
    i = 0
    while(i<df.shape[0]):
        row = df.iloc[i]
        try:
            time.sleep(0.3)
            temp = get_place_info(row['name'], row['address'], row['phone'])
            if(temp['rating'] is None or temp['rating']==0):
                print("%s, %s, %s has no ratings %s: " %(row['name'], row['address'], row['phone'], temp['rating']))
            
            if('original_name' in result):
                result['original_name'].append(row['name'])
            else:
                result['original_name'] = [row['name']]
                
            for key in keys:
                if(key in result):
                    result[key].append(temp[key])
                    
                else:
                    result[key] = [temp[key]]
            
        except Exception as e:
            print(e)
        i+=1
    
    temp = pd.DataFrame(result)
    temp.to_csv(output_fn, encoding='utf-8', header=True, index=False)
    
def get_reviews(df, output_fn):
    """
    get Google user reviews and write results to csv
    @param df: DataFrame containing campsites information including place_id
    @param output_fn: file name of csv to be written to
    """
    i = 0
    result = {}
    keys = ['author_name', 'author_url', 'profile_photo_url', 'rating', 'relative_time_description', 'text', 'time']
    while(i<df.shape[0]):
        row = df.iloc[i]
        print("processing %d: %s" %(i+1, row['original_name']) )
        try:
            if(row['place_id'] is not None):
                url = detaillsearch_url + row['place_id']
                res = get_google_api_response(url)
                if(res['status']=='OK'):
                    temp = res['result']
                    for r in temp['reviews']:
                        if('name' in result):
                            result['name'].append(row['original_name'])
                        else:
                            result['name'] = [row['original_name']]
                            
                        for key in keys:
                            if(key in result):
                                result[key].append(r[key])
                            else:
                                result[key] = [r[key]]
                else:
                    print("%s for %s" %(res.status, url))
            else:
                print("%s has not place_id, skipping" %(row['name']))
        except Exception as e:
            print(e)
        i+=1
    
    temp = pd.DataFrame(result)
    temp.to_csv(output_fn, encoding='utf-8', header=True, index=False)

def process_public_campsite_review():
    """
    get public campsite reivews. two csv files are generated:
        public_campsites_googleinfo.csv
        public_campsites_reviews.csv
    """
    if(not os.path.isfile('./data/public_campsites_googleinfo.csv')):
        df = pd.read_csv('./data/public_campsites.csv', encoding='utf-8')
        get_all_basic_info(df, './data/public_campsites_googleinfo.csv')
    
    df = pd.read_csv('./data/public_campsites_googleinfo.csv', encoding='utf-8')
    df.dropna(inplace=True)
    get_reviews(df, './data/public_campsites_reviews.csv')

def get_geocoding():
    """
    use Google geocoding API to get the latitude and longitude of public campsites
    public_campsites_latlng.csv is generated
    """
    public_sites = pd.read_csv('./data/public_campsites.csv')
    public_sites['lat'] = 0.0
    public_sites['lng'] = 0.0
    for i in range(public_sites.shape[0]):
        try:
            name = public_sites.iloc[i]['name']
            print("processing " + name)
            res = get_google_api_response(geocoding_url + urllib.parse.quote_plus(name))
            if(res['status']=='OK'):
                result = res['results']
                if(len(result) >= 1):
                    r = result[0]
                    public_sites.at[i, 'lat'] = r['geometry']['location']['lat']
                    public_sites.at[i, 'lng'] = r['geometry']['location']['lng']
            else:
                print("%s for %s" %(res.status, name))
        except Exception as e:
            print("exception occurred to geocode %s" % (name))
            print(e)
        time.sleep(0.2)
    public_sites.to_csv('./data/public_campsites_latlng.csv', encoding='utf-8', header=True, index= False)

"""
#To get reviews for public campsites, uncomment the following line and run this file
process_public_campsite_review()
"""