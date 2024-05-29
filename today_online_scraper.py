# Import necessary libraries and modules

from bs4 import BeautifulSoup 
from selenium import webdriver 
from selenium.webdriver.common.by import By 
from selenium.webdriver.chrome.options import Options 
import time
import json
from tqdm import trange


# Want the article body, summary, and URL

# Function to navigate to a specific category URL
def go_to_category(driver, category_URL):
    driver.get(category_URL)
def scrape_categories(driver, base_url):
    driver.get(base_url)
    time.sleep(2)
        
    try:
        navbar_items = driver.find_elements(By.CSS_SELECTOR, "li.main-menu__item a.main-menu__link")
        exclude = ['watch, myfeed']
        sub_cats = []
        for item in navbar_items:
            heading = item.get_attribute("href").split('/')[-1]
            if heading not in exclude:
                sub_cats.append(heading)
    except Exception as e:
        print(f"Error extracting sub category: {e}")
    sub_cats.remove('watch')
    sub_cats.remove('myfeed')
    return sub_cats
# # Function to gather article URLs from a category page
def gather_article_urls(driver):
    urls = []
    article_cards = driver.find_elements(By.CLASS_NAME, "card-object__figure")
    for card in article_cards:
        try:
            article_link = card.find_element(By.CLASS_NAME, "link")
            url = article_link.get_attribute("href")
            urls.append(url)
        except Exception as e:
            print(f"Error finding article URL: {e}")
    return urls

# Function to scrape articles from gathered URLs
def scrape_articles(scraped_articles, driver, urls, sub_url):
    sub_url_ls = []
    for url in urls:
        sub_url_hash = {}
        sub_url_hash["Article URL"] = url
        try:
                # Navigate to the article page
                driver.get(url)
                time.sleep(2)  # Waiting for the page to load

                # Get article summaries
                summary_elements = driver.find_elements(By.CSS_SELECTOR, "div.text-long ul li")
                summary_texts = [li.text for li in summary_elements]
                Combined_Summary = ".\n".join(summary_texts)
                if len(Combined_Summary) == 0:
                    sub_url_hash["Article Summary"] = 'NO SUMMARY'
                else:
                    sub_url_hash["Article Summary"] = Combined_Summary

                # Get article body
                try:
                    paragraphs = driver.find_elements(By.CSS_SELECTOR, "div.text-long p")
                    body = "\n".join([p.text for p in paragraphs])
                    sub_url_hash['Article Body'] = body
                except Exception as e:
                    sub_url_hash['Article Body'] = None
                    print("Body paragraphs not extracted")

        except Exception as e:
                print(f"Error scraping article: {e}")
        sub_url_ls.append(sub_url_hash)
    section = f"{sub_url} section"
    scraped_articles[section] = sub_url_ls

def run_scraper(base_url):
    options = Options()
    options.add_argument("--headless=new")
    driver = webdriver.Chrome(options=options)
    driver.maximize_window()
    scraped_articles = {}
    driver.get(base_url)
    time.sleep(2)  # Wait for the page to load
    category_sub_URLs = scrape_categories(driver, base_url)
    for i in trange(len(category_sub_URLs)):
        print(f'Collecting data for {category_sub_URLs[i]} section...')
        full_category_url = f"{base_url}{category_sub_URLs[i]}"
        go_to_category(driver, full_category_url)
        urls = gather_article_urls(driver)
        scrape_articles(scraped_articles, driver, urls, category_sub_URLs[i])
        print(f"Done collecting data for {category_sub_URLs[i]} section...\n")
    # Close the driver after scraping
    driver.quit()
    # Write files to json 
    with open("today_online/articles.json", "w", encoding='utf-8') as fout:
        json.dump(scraped_articles, fout, indent=4, ensure_ascii=False)

if __name__ == "__main__":
    run_scraper("https://www.todayonline.com/")