
# Install the Python ScrapingBee library:    
# pip install scrapingbee
from dotenv import load_dotenv
import os
from scrapingbee import ScrapingBeeClient

# Load environment variables from .env file
load_dotenv()

# Access the API key
api_key = os.getenv("API_KEY")

client = ScrapingBeeClient(api_key=api_key)

response = client.get("https://www.glassdoor.com/Reviews/Phillips-66-Reviews-E498821_P3.htm?sort.sortType=RD&sort.ascending=false&filter.iso3Language=eng")

print('Response HTTP Status Code: ', response.status_code)
print('Response HTTP Response Body: ', response.content)
