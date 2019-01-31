from selenium import webdriver
from selenium.webdriver.common.keys import Keys
import time
import pandas as pd

def get_place_reviews(google_name, name, result):
    driver = webdriver.Chrome()
    driver.get("https://www.google.com/maps/")
    elem = driver.find_element_by_name("q")
    elem.clear()
    print(google_name)
    elem.send_keys(google_name)
    elem.send_keys(Keys.RETURN)
    time.sleep(1)
    
    elem = None
    while(True):
        try:
            elem = driver.find_element_by_xpath('//button[@jsaction="pane.rating.moreReviews"]')
            break
        except Exception as e:
            print('wating for reviews to load')
            time.sleep(0.1)
            pass
    total_reviews = int(elem.text.replace(' reviews', '').replace(',',''))
    elem.click()
    time.sleep(1)
    
    elem = driver.find_element_by_css_selector('div.section-scrollbox')
    
    while(True):
        driver.execute_script("arguments[0].scrollTop = arguments[0].scrollHeight", elem)
        time.sleep(1)
        reviews = driver.find_elements_by_css_selector('div.section-review')
        loaded = len(reviews)
        print("loaded %d reviews, %d to go" % (loaded, total_reviews - loaded))
        if(len(reviews) >= total_reviews):
            break
        print('scroll for more...')
        
    #now we have all the reviews, grab them
    reviews = driver.find_elements_by_css_selector('div.section-review')
    for review in reviews:
        #get user name
        review_user = review.find_element_by_css_selector('div.section-review-title')
        print(review_user.text)
        #get star
        review_star = review.find_elements_by_css_selector('span.section-review-star-active')
        print("stars: %d" %(len(review_star)))
        #get review text
        review_content = review.find_element_by_css_selector('span.section-review-text')
        print(review_content.text)
        
        result['name'].append(name)
        result['user'].append(review_user.text)
        result['stars'].append(len(review_star))
        result['review'].append(review_content.text)

    time.sleep(0.5)
    driver.close()

def get_places_reviews():
    result = {
        'name':[],
        'user': [],
        'stars': [],
        'review': []
    }
    
    '''
    df = pd.read_csv('public_campsites_googleinfo.csv', encoding='utf-8')
    df.dropna(inplace=True)
    total = df.shape[0]
    for i in range(total):
        row = df.iloc[i]
        name= row['original_name']
        google_name = row['name']
        print('===============process %d out of %d' %(i+1, total))
        get_place_reviews(google_name, name, result)
    
    temp = pd.DataFrame(result)
    temp.to_csv('public_campsites_reviews.csv', header=True, index=False, encoding='utf-8')
    '''
    get_place_reviews('Arrowhead Provincial Park', 'Arrowhead Provincial Park', result)
get_places_reviews()