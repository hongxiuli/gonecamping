from utils import get_content
from bs4 import BeautifulSoup
import pandas as pd

def process_introduction(content):
    bs = BeautifulSoup(content, 'html.parser')
    temp = bs.find('div', id='introduction')
    intro = temp.find('div', class_='intro_list').get_text().strip()
    temp = bs.find('img', class_='park_name_logo')
    name = temp.next_sibling.get_text().strip()
    if(name.startswith('Algonquin')):
        name = name.replace('-', '') + ' Campground'
    else:
        name = name + ' Provincial Park'
    return name, intro
    
def process_camping(content):
    bs = BeautifulSoup(content, 'html.parser')
    temp = bs.find('div', id='camping')
    return str(temp), temp.get_text().strip()
    
def process_activities(content):
    bs = BeautifulSoup(content, 'html.parser')
    temp = bs.find('div', id='activities')
    h2s = temp.find_all('h2')
    activities = []
    for h2 in h2s:
        activities.append(h2.get_text().strip())
        
    return str(temp), ','.join(activities)
    
def process_facilities(content):
    bs = BeautifulSoup(content, 'html.parser')
    temp = bs.find('div', id='facilities')
    h2s = temp.find_all('h2')
    facilities = []
    for h2 in h2s:
        facilities.append(h2.get_text().strip())
        
    return str(temp), ','.join(facilities)
    
    
def scrape_all():
    with open('public_campsite_urls.txt') as f:
        contents = f.readlines()
    contents = [x.strip() for x in contents]
    
    result = {
        'name': [],
        'introduction': [],
        'camping': [],
        'activities': [],
        'facilities': [],
        'camping_raw': [],
        'activities_raw': [],
        'facilities_raw': [],
        'address': [],
        'phone': []
    }
    for url in contents:
        #introduction
        content = get_content(url)
        name, intro = process_introduction(content)
        result['name'].append(name)
        result['introduction'].append(intro)
        
        #camping
        content = get_content(url+'/camping')
        raw, text = process_camping(content)
        result['camping'].append(text)
        result['camping_raw'].append(raw)
        
        #activities
        content = get_content(url+'/activities')
        raw, text = process_activities(content)
        result['activities'].append(text)
        result['activities_raw'].append(raw)
        
        #facilities
        content = get_content(url+'/facilities')
        raw, text = process_facilities(content)
        result['facilities'].append(text)
        result['facilities_raw'].append(raw)
        
        #address, phone
        result['address'].append(None)
        result['phone'].append(None)
        
    df = pd.DataFrame(result)
    df.to_csv('public_campsites.csv', encoding='utf-8', index= False, header = True)

scrape_all()