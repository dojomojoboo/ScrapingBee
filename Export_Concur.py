import aiohttp
import asyncio
import json
import pandas as pd
from bs4 import BeautifulSoup
from time import time
from dotenv import load_dotenv
import os

# Load environment variables from .env file
load_dotenv()

# Access the API key
api_key = os.getenv("API_KEY")

async def fetch(session, url):
    async with session.get(url) as response:
        return await response.text()

async def extract_reviews(session, num_pages):
    review_data = []
    url_list = []

    base_url = f'https://api.scrapingdog.com/scrape?api_key='+api_key'&url=https://www.glassdoor.com/Reviews/Phillips-66-Reviews-E498821_P'
    # base_url = f'https://www.glassdoor.com/Reviews/Berkshire-Hathaway-Reviews-E805672_P'

    headers = {'User-Agent': 'Mozilla/5.0'}

    tasks = []
    semaphore = asyncio.Semaphore(5)  # Set concurrency limit to 5

    for page in range(1, num_pages+1):
        url = f'{base_url}{page}.htm?sort.sortType=RD&sort.ascending=false&filter.iso3Language=eng&dynamic=false'
        url_list.append(url)  # Store the URL
        tasks.append(asyncio.ensure_future(fetch_with_semaphore(session, url, semaphore)))

    responses = await asyncio.gather(*tasks)

    for i, response_text in enumerate(responses):
        soup = BeautifulSoup(response_text, 'html.parser')
        reviews = soup.find_all('div', class_='gdReview')
        stripped_url = url_list[i].replace('https://api.scrapingdog.com/scrape?api_key='+api_key'&url=', '')

        for review in reviews:
            review_rating = review.find('span', class_='ratingNumber').get_text(strip=True)
            review_title = review.find('a', class_='reviewLink').get_text(strip=True)
            review_author_info = review.find('span', class_='middle common__EiReviewDetailsStyle__newGrey').get_text(strip=True)        
            split_text = review_author_info.split(' - ', 1)
            print(split_text)
            review_date = split_text[0]
            if len(split_text) > 1:
                review_jobrole = split_text[1]  # Set the second part to variable2 if it exists
            else:
                review_jobrole = None  # Set variable2 to None if there is no second part
            review_pros = review.find('span', attrs={'data-test': 'pros'}).get_text(strip=True)
            review_cons = review.find('span', attrs={'data-test': 'cons'}).get_text(strip=True)
            review_helpful = review.find('div', class_='common__EiReviewDetailsStyle__socialHelpfulcontainer').get_text(strip=True)
            review_data.append({'ExtractURL': stripped_url, 'Rating': review_rating, 'Title': review_title, 'Date': review_date, 'Jobrole': review_jobrole, 'Pros':review_pros, 'Cons':review_cons, 'Helpful': review_helpful })

    return review_data

async def fetch_with_semaphore(session, url, semaphore):
    async with semaphore:
        async with session.get(url) as response:
            return await response.text()

def export_to_csv(review_data):
    df = pd.DataFrame(review_data)
    df.to_csv('029_Phillips66.csv', index=False)

async def main():
    start_time = time()
    num_pages = 57

    async with aiohttp.ClientSession(headers={'User-Agent': 'Mozilla/5.0'}) as session:
        reviews = await extract_reviews(session, num_pages)
        export_to_csv(reviews)

    end_time = time()
    elapsed_time = end_time - start_time
    print(f"Elapsed run time: {elapsed_time} seconds")

loop = asyncio.get_event_loop()
loop.run_until_complete(main())
# asyncio.run(main())
