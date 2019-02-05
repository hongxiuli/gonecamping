from utils import get_content
from bs4 import BeautifulSoup
import pandas as pd
import re

def process_introduction(content):
    bs = BeautifulSoup(content, 'html.parser')
    intro_tag = bs.find('div', id='introduction')
    intro = intro_tag.find('div', class_='intro_list').get_text().strip()
    temp = bs.find('img', class_='park_name_logo')
    name = temp.next_sibling.get_text().strip()
    if(name.startswith('Algonquin')):
        name = name.replace('-', '') + ' Campground'
    else:
        name = name + ' Provincial Park'
        
    activities_icon = [];
    facilities_icon = [];
    '''
        div introduction
            div-11
                div-11-21
                div-11-22
                    div-11-22-31
                        embed //facilities
                        embed
                        ...
                    div-11-22-32
                        embed //activites
                        embed
                        ...
                    div-11-22-33
            div-12
                div-12-21
                    div-12-21-31
                        div-12-21-31-41
                            
                    div-12-21-32
                div-12-22
    '''
    div11 = list(intro_tag.children)[1]
    div1122 = list(div11.children)[3]
    temp = list(div1122.children)
    div112231 = temp[1]
    div112232 = temp[3]
    facilities_img_tags = div112231.find_all('embed')
    for img_tag in facilities_img_tags:
        if(img_tag['title'].find('Not available') == -1):
            facilities_icon.append(img_tag['title'])
    activities_img_tags = div112232.find_all('embed')
    for img_tag in activities_img_tags:
        if(img_tag['title'].find('Not available') == -1):
            activities_icon.append(img_tag['title'])
            
    div12 = list(intro_tag.children)[3]
    card_body = div12.find('div', class_='card-body')
    temp = card_body.find_all('div', class_='col-12')
    address_tag = temp[1]
    address = address_tag.get_text()
    address = re.sub('\s+',' ', address)
    address = address.replace('Address:', '').strip()
    return name, intro, address, facilities_icon, activities_icon
    
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
        'phone': [],
        'activities_icon':[],
        'facilities_icon':[]
    }
    for url in contents:
        #introduction
        content = get_content(url)
        name, intro, address, facilities_icon, activities_icon = process_introduction(content)
        result['name'].append(name)
        result['introduction'].append(intro)
        result['address'].append(address)
        result['facilities_icon'] = ','.join(facilities_icon)
        result['activities_icon'] = ','.join(activities_icon)
        
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
        
        #phone
        result['phone'].append(None)
    df = pd.DataFrame(result)
    df.to_csv('public_campsites.csv', encoding='utf-8', index= False, header = True)

scrape_all()