import requests
import json
import pandas as pd
import datetime
from bs4 import BeautifulSoup
from time import sleep, time
from scrapingbee import ScrapingBeeClient
from dotenv import load_dotenv
import os

# Load environment variables from .env file
load_dotenv()

# Access the API key
api_key = os.getenv("API_KEY")

# The Extract reviews function with number of pages to extract
def extract_reviews(company_name, num_pages):
    review_data = []
    url_list = []
    client = ScrapingBeeClient(api_key=api_key)
    
    for page in range(1, num_pages+1):
        url = f'https://www.glassdoor.com/Reviews/{company_name}-Reviews-E805672_P{page}.htm'
        headers = {'User-Agent': 'Mozilla/5.0'}
        response = client.get(url, headers=headers)
        print(page)
        
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
            review_data.append({'ExtractURL': url, 'Rating': review_rating, 'Title': review_title, 'Date': review_date, 'Jobrole': review_jobrole, 'Pros':review_pros, 'Cons':review_cons, 'Helpful': review_helpful })
    
    return review_data

# The Export to csv function
def export_to_csv(review_data):
    df = pd.DataFrame(review_data)
    df.to_csv('007_Berkshire_Hathaway.csv', index=False)

# Set parameters for the functions to use
start_time = time()
company_name = 'Berkshire-Hathaway'
num_pages = 3

# Call the extract reviews function
reviews = extract_reviews(company_name, num_pages)

# Call Export data to CSV function
export_to_csv(reviews)

# Print the time it took to run full script
end_time = time()
elapsed_time = end_time - start_time
print(f"Elapsed run time: {elapsed_time} seconds")
