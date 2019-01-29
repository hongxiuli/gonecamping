#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Mon Jan 21 13:00:01 2019

@author: hongxiu
"""

import requests
#We need this module to encode the url
#because when we write the file to disk, the file name cannot contain ?
import urllib.parse

from bs4 import BeautifulSoup
import os
from utils import get_content

def get_content(url):
    '''
    get HTML for url, serving from cache if possible.
    '''
    parts = url.split('/')
    fn = 'htmls/' + urllib.parse.quote_plus(parts[-1]) + '.html'

    contents = None
    if(os.path.isfile(fn)):
        print("get " + url + " from cache")
        with open(fn, 'r', encoding='utf-8') as f:
            contents = f.read()            
    else:
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


def get_campsites():
    '''
    scrape all camp sites' URLs from the give url.
    return all URLs in an array
    '''
    #get the HTML of the url
    url = 'https://www.campinginontario.ca/campgrounds?region=0'
    content = get_content(url)
    
    #array to store the result
    result = []
    
    #create beautiful soup object
    bs = BeautifulSoup(content, 'html.parser')
   # bs = BeautifulSoup('https://www.campinginontario.ca/campgrounds?region=0', 'html.parser')

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


def get_info(content):
    soup = BeautifulSoup(content, 'html.parser')
    
    #################Name:
    
    #################Address and GPS
    address_tag = soup.find('div', class_='cg-address')
    name = address_tag.find('h1').get_text().strip()
    temp = address_tag.find_all('div', class_ = 'float-left')
    print("=========Address==========")
    address = temp[0].get_text().strip()
    gps = temp[1].get_text().strip()
    print("%s:%s:%s" %(name, address, gps))    
    
    ov_tag = soup.find('div', class_='campg-overview-left')
    ############overview
    ov = ov_tag.find('p').get_text().strip()
    print("=========overview==========")
    print(ov)
    
    ############details
    details_tag = ov_tag.find_all('div', class_='numbers')
    print("=========details==========")
    for detail in details_tag:
        num = detail.get_text().strip()
        name= detail.parent.find('div', class_='dotdot').get_text().strip()
        print("%s:%s" %(name, num))
    
    ############activities
    temp = ov_tag.find_all('div', class_='mb15')
    #the last one is the activities div
    print("=========activities==========")
    act_tag = temp[-1]
    print(act_tag.get_text().strip())
    
    ############Facilites
    active_facility_tags = soup.find_all('span', class_='profileAmenActive')
    print("=========facilities ACTIVE==========")
    for active in active_facility_tags:
        print(active.get_text().strip())
    inactive_facility_tags = soup.find_all('span', class_='profileAmen')
    print("=========facilities INACTIVE==========")
    for inactive in inactive_facility_tags:
        print(inactive.get_text().strip())


def get_google_review(address):
    google_url = 'https://maps.googleapis.com/maps/api/place/findplacefromtext/json?inputtype=textquery'
    google_url += '&key=AIzaSyDX8Uxzozw5kOzezJ5Cfz-DPsXXG8neOkM'
    google_url += '&fields=name,rating,place_id'
    google_url += '&input='
    google_url += urllib.parse.quote_plus(address)
    
    print(google_url)
    res = requests.get(google_url)
    if(res.status_code==200):
        print(res.content)
    else:
        print(res.status_code)

'''
all_prcampsites = get_campsites()
for url in all_prcampsites:
    #for now I just print the url
    try:
        #sleep 2 seconds before each scrape
        #need to import time in the beginning of the file
       time.sleep(0)
       content = get_content(url)
       site_content = get_info(content)
    except Exception as e:
        print(e)

'''

#get_google_review('2900 Hwy 518 E, RR 1 Kearney, Ontario, P0A 1M0')























