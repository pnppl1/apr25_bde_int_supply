import requests
from bs4 import BeautifulSoup
import time
import csv

headers = {
    'User-Agent': 'Mozilla/5.0'
}

base_url = 'https://www.trustpilot.com/review/headout.com?page='
all_reviews = []

def extract_reviews(soup):
    articles = soup.find_all('article', attrs={"data-service-review-card-paper": True})
    reviews = []

    for article in articles:
        try:
            name = article.find('span', attrs={"data-consumer-name-typography": True}).get_text(strip=True)
        except:
            name = None

        try:
            country = article.find('span', attrs={"data-consumer-country-typography": True}).get_text(strip=True)
        except:
            country = None

        try:
            rating_tag = article.find('div', attrs={"data-service-review-rating": True})
            rating = int(rating_tag["data-service-review-rating"])
        except:
            rating = None

        try:
            title = article.find('h2', attrs={"data-service-review-title-typography": True}).get_text(strip=True)
        except:
            title = None

        try:
            text = article.find('p', attrs={"data-service-review-text-typography": True}).get_text(strip=True)
        except:
            text = None

        try:
            date = article.find('p', attrs={"data-service-review-date-of-experience-typography": True}).get_text(strip=True)
        except:
            date = None

        reviews.append({
            "name": name,
            "country": country,
            "rating": rating,
            "title": title,
            "text": text,
            "date_of_experience": date
        })

    return reviews

for page_num in range(1, 2):
    url = f"{base_url}{page_num}"
    response = requests.get(url, headers=headers)

    if response.status_code != 200:
        print(f"Failed to fetch page {page_num}")
        break

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
    print(f"{r['date_of_experience']}")

csv_file = 'trustpilot_reviews.csv'
if all_reviews:
    with open(csv_file, 'w', newline='', encoding='utf-8') as f:
        writer = csv.DictWriter(f, fieldnames=all_reviews[0].keys())
        writer.writeheader()
        writer.writerows(all_reviews)
    print(f"\n Saved {len(all_reviews)} reviews to '{csv_file}'")
else:
    print("No reviews found to save.")
