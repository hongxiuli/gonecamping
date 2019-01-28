import requests
import urllib.parse
from bs4 import BeautifulSoup
import os

#!!!!!!!!!!!!!!this line is new
import time


def get_content(url):
    parts = url.split('/')
    
    #!!!!!!!!!!!!!this line is changed. we are encoding parts[-1] now.
    fn = 'htmls/' + urllib.parse.quote_plus(parts[-1]) + '.html'
    
    
    contents = None
    if(os.path.isfile(fn)):
        print("get " + url + " from cache")
        with open(fn, 'r', encoding='utf-8') as f:
            contents = f.read()
    else:
        print("get " + url  + " remotely")
        temp = requests.get(url)
        #!!!!!!!!!!!!!!this line is new
        if(temp.status_code == 200):
            # status_code == 200 means the request is successful
            contents = temp.content.decode('utf-8', 'ignore')
            with open(fn, 'w', encoding='utf-8') as f:
                f.write(contents)
        else:
            #the request failed. so let us raise an Exception
            raise Exception("Exception: could not get HTML for  " + url)
    return contents

def get_camping_sites():
    '''
    scrape all camping sites' URLs from the give url.
    return all URLs in an array
    '''
    #get the HTML of the url
    url = 'https://www.campinginontario.ca/campgrounds?region=0'
    content = get_content(url)
    
    #array to store the result
    result = []
    
    #create beautiful soup object
    bs = BeautifulSoup(content, 'html.parser')
    
    #find all <div> tags that has a 'camp-link' class
    rows = bs.find_all('div', class_='camp-link')
    
    #loop through all rows to get the address for the camp group
    for row in rows:
        address = row['onclick']
        # addres looks like:
        # window.location='/1000IslandsKingstonKOA'
        # we only need /1000IslandsKingstonKOA
        address = address[17:-1]
        result.append('https://www.campinginontario.ca'+address)
    
    return result

all_camping_sties = get_camping_sites()

for url in all_camping_sties:
    #for now I just print the url
    try:
        #sleep 2 seconds before each scrape
        #need to import time in the beginning of the file
        time.sleep(2)
        content = get_content(url)
        ##do more things here...
    except Exception as e:
        print(e)