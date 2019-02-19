import requests
import urllib.parse
import os
import time

def get_content(url):
    """
    Get the HTML source for url and cache the content locally.
    @param url: the url of the webpage
    """
    fn = 'htmls/' + urllib.parse.quote_plus(url) + '.html'
    contents = None
    if(os.path.isfile(fn)):
        print("get " + url + " from cache")
        with open(fn, 'r', encoding='utf-8') as f:
            contents = f.read()
    else:
        time.sleep(0.7)
        print("get " + url  + " remotely")
        temp = requests.get(url)
        if(temp.status_code == 200):
            # status_code == 200 means the request is successful
            contents = temp.content.decode('utf-8', 'ignore')
            with open(fn, 'w', encoding='utf-8') as f:
                f.write(contents)
        else:
            #the request failed. so let us raise an Exception
            raise Exception("Exception: could not get HTML for  " + url)
    return contents