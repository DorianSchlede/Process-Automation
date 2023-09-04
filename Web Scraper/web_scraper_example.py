import requests
from bs4 import BeautifulSoup
import openai

# Set OpenAI API key
openai.api_key = "your_openai_api_key_here"  # Replace with your OpenAI API key

# List of verticals or industries
verticals = ["Technology", "Healthcare", "Finance", "Entertainment", "Real Estate", "Automotive", "Energy", "Agriculture", "Manufacturing", "Hospitality"]

class WebsiteScraper:
    def __init__(self, url):
        self.url = url
        self.html = None
        self.text_content = None
    
    def scrape(self):
        try:
            response = requests.get(self.url)
            if response.status_code == 200:
                self.html = BeautifulSoup(response.content, 'html.parser')
                self.text_content = self.html.get_text()  # Get text content, stripping HTML tags
            else:
                print(f"Failed to scrape {self.url}, status code {response.status_code}")
        except Exception as e:
            print(f"Failed to scrape {self.url}, error: {e}")

if __name__ == "__main__":
    while True:
        url = input("Enter a website URL to scrape (or 'quit' to exit): ")
        if url.lower() == 'quit':
            break
            
        scraper = WebsiteScraper(url)
        scraper.scrape()
        
        if scraper.text_content:
            print("Scraped Content:")
            print(scraper.text_content[:500])  # Prints the first 500 characters of the text content
        else:
            print(f"Failed to scrape {url}")
