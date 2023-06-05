import json
import pandas as pd
import datetime
from bs4 import BeautifulSoup
from time import sleep, time
import concurrent.futures
from scrapingbee import ScrapingBeeClient
from dotenv import load_dotenv
import os

# Load environment variables from .env file
load_dotenv()

# Access the API key
api_key = os.getenv("API_KEY")

# The Extract reviews function with number of pages to extract
def extract_reviews(num_pages):
    review_data = []
    url_list = []
    client = ScrapingBeeClient(api_key=api_key)

    def process_page(page):
        # url = f'https://www.glassdoor.com/Reviews/Berkshire-Hathaway-Reviews-E805672_P{page}.htm?sort.sortType=RD&sort.ascending=false&filter.iso3Language=eng'
        url = f'https://www.glassdoor.com/Reviews/Berkshire-Hathaway-Reviews-E805672_P14.htm?sort.sortType=RD&sort.ascending=false&filter.iso3Language=eng'
        headers = {'User-Agent': 'Mozilla/5.0'}
        response = client.get(url, headers=headers, params = {'wait': '10000'})
        print(f"Page: {page} | Response Status: {response.status_code}")

        soup = BeautifulSoup(response.text, 'html.parser')

        reviews = soup.find_all('div', class_='gdReview')

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
            review_data.append({'ExtractURL': url, 'Rating': review_rating, 'Title': review_title, 'Date': review_date, 'Jobrole': review_jobrole, 'Pros': review_pros, 'Cons': review_cons, 'Helpful': review_helpful})

    with concurrent.futures.ThreadPoolExecutor(max_workers=5) as executor:
        pages = range(1, num_pages + 1)
        executor.map(process_page, pages)

    return review_data


# The Export to csv function
def export_to_csv(review_data):
    df = pd.DataFrame(review_data)
    df.to_csv('007_Berkshire_Hathaway.csv', index=False)


def main():
    start_time = time()
    num_pages = 1

    # Call the extract reviews function
    reviews = extract_reviews(num_pages)

    # Call Export data to CSV function
    export_to_csv(reviews)

    # Print the time it took to run full script
    end_time = time()
    elapsed_time = end_time - start_time
    print(f"Elapsed run time: {elapsed_time} seconds")


if __name__ == '__main__':
    main()
