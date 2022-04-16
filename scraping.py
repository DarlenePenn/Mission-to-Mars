# Import dependencies
from matplotlib.pyplot import title
from splinter import Browser
from bs4 import BeautifulSoup as soup
import pandas as pd
import datetime as dt
from sqlalchemy import desc
from webdriver_manager.chrome import ChromeDriverManager

def scrape_all():
    # Initiate headless driver for deployment
    executable_path = {'executable_path': ChromeDriverManager().install()}
    browser = Browser('chrome', **executable_path, headless=True)

    news_title, news_paragraph = mars_news(browser)

    # Run all scraping functions and store results in dictionary
    data = {
        "news_title": news_title,
        "news_paragraph": news_paragraph,
        "featured_image": featured_image(browser),
        "facts": mars_facts(),
        "last_modified": dt.datetime.now(),
        "hemispheres": hemisphere_images(browser)
    }
    

    # Stop webdriver and return data
    browser.quit()
    return data

def mars_news(browser):

    # Scrape Mars News
    # Visit the mars nasa news site
    url = 'https://redplanetscience.com/'
    browser.visit(url)

    # Optional delay for loading the page
    browser.is_element_present_by_css('div.list_text', wait_time=1)

    # Convert the browser html to a soup object and then quit the browser
    html = browser.html
    news_soup = soup(html, 'html.parser')

    # Add try/except for error handling
    try:
        slide_elem = news_soup.select_one('div.list_text')
        # Use the parent element to find the first 'a' tag and save it as 'news_title'
        news_title = slide_elem.find('div', class_='content_title').get_text()
        # Use the parent element to find the paragraph text
        news_p = slide_elem.find('div', class_='article_teaser_body').get_text()

    except AttributeError:
        return None, None

    return news_title, news_p
    
### Featured Images
def featured_image(browser):   
    # Visit URL
    url = 'https://spaceimages-mars.com'
    browser.visit(url)

    # Find and click the full image button
    full_image_elem = browser.find_by_tag('button')[1]
    full_image_elem.click()

    # Parse the resulting html with soup
    html = browser.html
    img_soup = soup(html, 'html.parser')

    # Add try/except for error handling
    try:
        # Find the relative image url
        img_url_rel = img_soup.find('img', class_='fancybox-image').get('src')

    except AttributeError:
        return None

    # Use the base URL to create an absolute URL
    img_url = f'https://spaceimages-mars.com/{img_url_rel}'
    
    return img_url

def mars_facts():
    # Add try/except for error handling
    try:
        # Use 'read_html' to scrape the facts table into a dataframe
        df = pd.read_html('https://galaxyfacts-mars.com')[0]

    except BaseException:
        return None

    #assign columns
    df.columns=['description', 'Mars', 'Earth']
    #set Description Column as index
    df.set_index('description', inplace=True)
    
    #convert table to a html object 
    return df.to_html(classes="table table-striped")

def hemisphere_images():
    # 1. Use browser to visit the URL 
    url = 'https://marshemispheres.com/'
    browser.visit(url)
    
    # 2. Create a list to hold the images and titles.
    hemisphere_image_urls = []

    # 3. Write code to retrieve the image urls and titles for each hemisphere.

    #html parser
    html = browser.html
    hemi_soup = soup(html, 'html.parser')

    #get elements that contain image urls and descriptions
    hemi_items = hemi_soup.find_all('div',class_='item')
    try:
        #loop through each item
        for i in hemi_items:
            title = i.find('h3').text
            thumb_url = i.find('a', class_='itemLink product-item')['href']
    
    except AttributeError:
        return None
        
        #go to image url
        browser.visit(url + thumb_url)

        #parse html for each hemisphere
        new_html = browser.html
        image_soup = soup(new_html, 'html.parser')

        #get high res image
        highres_url = url + image_soup.find('img', class_='wide-image')['src']

        #add it to the list
        hemisphere_image_urls.append({'title': title, "highres_url": highres_url})

        return hemisphere_image_urls

        browser.back()


if __name__ == "__main__":

    # If running as script, print scraped data
    print(scrape_all())

