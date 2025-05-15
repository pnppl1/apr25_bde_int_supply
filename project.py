import requests
from bs4 import BeautifulSoup
import time
from datetime import datetime
import csv

headers = {
    'User-Agent': 'Mozilla/5.0'
}

base_url = 'https://www.trustpilot.com/review/headout.com?page='
all_reviews = []

# Function to extract reviews from a page
def extract_reviews(soup):
    # Find all review articles
    articles = soup.find_all('article', attrs={"data-service-review-card-paper": True})
    reviews = []

    # Loop through each review article
    for article in articles:
        try:
            # Extract the reviewer's name
            name = article.find('span', attrs={"data-consumer-name-typography": True}).get_text(strip=True)
        except:
            name = None

        try:
            # Extract the reviewer's country
            country = article.find('span', attrs={"data-consumer-country-typography": True}).get_text(strip=True)
        except:
            country = None

        try:
            # Extract the review rating
            rating_tag = article.find('div', attrs={"data-service-review-rating": True})
            rating = int(rating_tag["data-service-review-rating"])
        except:
            rating = None

        try:
            # Extract the review title
            title = article.find('h2', attrs={"data-service-review-title-typography": True}).get_text(strip=True)
        except:
            title = None

        try:
            # Extract the review text
            text = article.find('p', attrs={"data-service-review-text-typography": True}).get_text(strip=True)
        except:
            text = None

        try:
            # Extract the date of experience
            element = article.find('p', attrs={"data-service-review-date-of-experience-typography": True})
            raw_text = element.get_text(strip=True) 
            # Split on ":" and take the second part to get rid of the text "Date of experience:"
            raw_date = raw_text.split(":", 1)[1].strip()
            # Parse date string to datetime.date object
            date_obj = datetime.strptime(raw_date, "%B %d, %Y").date() 
            # Convert to ISO format
            date = date_obj.isoformat()  # '2025-05-11' string format, or just use date_obj directly
        except:
            date = None

        # Append the extracted data to the reviews list
        reviews.append({
            "name": name,
            "country": country,
            "rating": rating,
            "title": title,
            "text": text,
            "date_of_experience": date
        })

    return reviews

# Loop through pages
for page_num in range(1, 2):
    url = f"{base_url}{page_num}"
    response = requests.get(url, headers=headers)

    # Check if the request was successful
    if response.status_code != 200:
        print(f"Failed to fetch page {page_num}")
        break

    # Parse the page content
    soup = BeautifulSoup(response.content, 'lxml')
    all_reviews.extend(extract_reviews(soup))
    time.sleep(2)

# Print results
for idx, r in enumerate(all_reviews, 1):
    print(f"\nReview {idx}")
    print(f"Name: {r['name']} ({r['country']})")
    print(f"Rating: {r['rating']} stars")
    print(f"Title: {r['title']}")
    print(f"Text: {r['text']}")
    print(f"Date of experience: {r['date_of_experience']}")

# Save to CSV
csv_file = 'trustpilot_reviews.csv'
if all_reviews:
    with open(csv_file, 'w', newline='', encoding='utf-8') as f:
        writer = csv.DictWriter(f, fieldnames=all_reviews[0].keys())
        writer.writeheader()
        writer.writerows(all_reviews)
    print(f"\n Saved {len(all_reviews)} reviews to '{csv_file}'")
else:
    print("No reviews found to save.")
