#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Mon Jan 21 13:00:01 2019

Scrape private campsites information from https://www.campinginontario.ca
Results will be written into private_campsites.csv

@author: hongxiu
"""

import requests
import urllib.parse

from bs4 import BeautifulSoup
import os
import time
import pandas as pd
import utils

def get_all_campsites_urls():
    '''
    scrape all camp sites' URLs from the give url.
    @return all URLs in an array
    '''
    #get the HTML of the url
    url = 'https://www.campinginontario.ca/campgrounds?region=0'
    content = utils.get_content(url)
    
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


def get_info(content):
    """
    scrape information for one particular campsite
    @param content: html source for the particular campsite
    @return: dict containg the basic information
    """
    #define a dictionary object to hold all the information
    result = {}
    
    soup = BeautifulSoup(content, 'html.parser')

    #Address and GPS
    address_tag = soup.find('div', class_='cg-address')
    name = address_tag.find('h1').get_text().strip()
    temp = address_tag.find_all('div', class_ = 'float-left')
    
    address_ = temp[0].contents
    address = address_[2].strip().replace('<br>', '')
    address += ', '
    # address_[3] is a tag object, so need to call the get_text method first
    address+= address_[3].get_text().strip()
    
    gps = temp[1].get_text().strip().replace('GPS Information: ', '')
    parts = gps.split(',')
    latitude = parts[0].strip()
    longitude = parts[1].strip()
    
    
    phone_tag = address_tag.find('div', class_='mt10')
    phone = phone_tag.find('span').get_text().strip()
    phone = phone.replace('Phone:','').strip()
    
    result['name'] = name
    result['address'] = address
    result['latitude'] = latitude
    result['longitude'] = longitude
    result['phone'] = phone
    
    ov_tag = soup.find('div', class_='campg-overview-left')
    #overview
    ov = ov_tag.find('p').get_text().strip()
    result['overview'] = ov
    
    #details
    details_tag = ov_tag.find_all('div', class_='numbers')
    for detail in details_tag:
        num = detail.get_text().strip()
        name= detail.parent.find('div', class_='dotdot').get_text().strip()
        result[name]=num
    
    #activities
    temp = ov_tag.find_all('div', class_='mb15')
    #the last one is the activities div
    activities = temp[-1].get_text().strip()
    result['activities'] = activities
    
    #Facilites
    active_facility_tags = soup.find_all('span', class_='profileAmenActive')
    for active in active_facility_tags:
        result[active.get_text().strip()] = 1
    inactive_facility_tags = soup.find_all('span', class_='profileAmen')
    for inactive in inactive_facility_tags:
        result[inactive.get_text().strip()] = 0
        
    return result

def scrape_all():
    """
    drive function to scrape all private campsites information
    """
    result = {}
    all_prcampsites_url = get_all_campsites_urls()
    for url in all_prcampsites_url:
        try:
            time.sleep(0.2)
            content = get_content(url)
            site_content = get_info(content)
            
            '''
            site_content is a dictionary, it looks like:
            {
                name: '1000 Islands Kinston KOA Holiday',
                address: '2039 Cordukes Rd, Kingston, Ontario, K7L 4V4',
                ... and so on
            }
            loop through all keys and add it to the result dictionary, result will look like:
            {
                name: ['1000 Islands Kinston KOA Holiday', 'Almaguin Campground', ...],
                address: ['2039 Cordukes Rd, Kingston, Ontario, K7L 4V4', '419 Owl Lake Rd, Katrine, Ontario, P0A 1L0', ...],
                ... and so on
            }
            '''
            for key in site_content:
                if(key in result):
                    result[key].append(site_content[key])
                else:
                    result[key] = [site_content[key]]
        except Exception as e:
            print(e)
    
    #create a dataframe based on result, which is a dictionary of arrays, the keys will be the csv columns
    df = pd.DataFrame(result)
    #write to csv
    df.to_csv('./data/private_campsites.csv', encoding='utf-8', header=True, index=False)

"""
Uncomment the following line and run this file
scrape_all()
"""
