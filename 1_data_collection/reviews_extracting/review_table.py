#!/usr/bin/env python
# coding: utf-8
import requests
from bs4 import BeautifulSoup
import time
from datetime import datetime
import csv
import pandas as pd

headers = {
    'User-Agent': 'Mozilla/5.0'
}

# ## Search companies with over 10k reviews
# Base URL for the Trustpilot travel agency category, sorted by review count, paginated
base_url_over_10k = "https://www.trustpilot.com/categories/travel_agency?sort=reviews_count&page="

# This list will store companies that meet the 10,000+ reviews threshold
companies = []

# Start from the first page
page = 1

while True:
    url = f"{base_url_over_10k}{page}"
    print(f"Scraping page {page}...")

    # Send GET request to the page with headers
    response = requests.get(url, headers=headers)

    # Exit loop if the page fails to load
    if response.status_code != 200:
        print(f"Failed to load page {page}")
        break

    # Parse HTML content
    soup = BeautifulSoup(response.text, 'lxml')

    # Extract all company cards (each one is an <a> element with name='business-unit-card')
    cards = soup.find_all("a", attrs={"name": "business-unit-card"})

    # If no company cards found, we've reached the end
    if not cards:
        print("No more companies found.")
        break

    # Flag to determine whether we should stop after this page
    stop = False

    for card in cards:
        try:
            # Extract the company name
            name = card.find("p", class_="CDS_Typography_heading-xs__bedfe1").get_text(strip=True)

            # Extract the company website
            website = card.find("p", class_="styles_websiteUrlDisplayed__lSw1A").get_text(strip=True)

            # Locate the tag containing the review count
            reviews_text = card.find("p", class_="styles_ratingText__A2dmB")
            if not reviews_text:
                continue  # Skip if missing

            # Get the last <span> inside the ratingText block (it contains review count)
            review_count_text = reviews_text.find_all("span")[-1].get_text(strip=True)

            # Convert string (e.g., "12,345") to integer
            review_count = int(review_count_text.replace(",", ""))

            # If review count is 10,000 or more, add to results
            if review_count >= 10000:
                companies.append({
                    "name": name,
                    "reviews": review_count,
                    "website": website
                })
            else:
                # If we find a company below 10k, assume rest are smaller and stop
                stop = True
                break

        except Exception as e:
            # Catch any parsing error and skip the current card
            print(f"Error parsing company card: {e}")
            continue

    if stop:
        print("Found company with fewer than 10,000 reviews. Stopping.")
        break

    # Go to next page
    page += 1

    # Delay to avoid being blocked (can be lowered, but 1s is safe)
    time.sleep(1)

# ### Output the result
# Print each company with its index, name, review count, and website
for i, c in enumerate(companies, 1):
    print(f"{i}. {c['name']} – {c['reviews']} reviews – {c['website']}")

# Print the total number of companies found with over 10,000 reviews
print(f"\nTotal companies with over 10,000 reviews: {len(companies)}")

# ## Get the data
# ### Function for scraping the review data from the page of a company
# Function to extract reviews from a BeautifulSoup-parsed review page
def extract_reviews(soup):
    # Find all review article elements on the page
    articles = soup.find_all('article', attrs={"data-service-review-card-paper": True})
    reviews = []

    # Loop through each review article
    for article in articles:
        try:
            # Extract reviewer's name
            name = article.find('span', attrs={"data-consumer-name-typography": True}).get_text(strip=True)
        except:
            name = None # Skip if name of reviewer is empty

        try:
            # Extract reviewer's country
            country = article.find('span', attrs={"data-consumer-country-typography": True}).get_text(strip=True)
        except:
            country = None # Skip if review country field is empty

        try:
            # Extract the rating as an integer from the data attribute
            rating_tag = article.find('div', attrs={"data-service-review-rating": True})
            rating = int(rating_tag["data-service-review-rating"])
        except:
            rating = None # Skip if review rating is empty

        try:
            # Extract review title
            title = article.find('h2', attrs={"data-service-review-title-typography": True}).get_text(strip=True)
        except:
            title = None # Skip if review title is empty

        try:
            # Extract review text
            text = article.find('p', attrs={"data-service-review-text-typography": True}).get_text(strip=True)
            if not text:
                continue  # Skip if review text is empty (helps ignoring recent reviews block)
        except:
            continue  # Skip this review if there's no text

        try:
            # Extract and parse the date of experience, if available
            raw_text = article.find('p', attrs={"data-service-review-date-of-experience-typography": True}).get_text(strip=True)
            if raw_text.startswith("Date of experience:"):
                raw_date = raw_text.replace("Date of experience:", "").strip()
                date = datetime.strptime(raw_date, "%B %d, %Y").date()
            else:
                date = None
        except Exception:
            date = None

        try:
            # Check if the company replied to the review
            company_reply = article.find('p', attrs={"data-service-review-business-reply-text-typography": True})
            has_reply = 1 if company_reply else 0
        except:
            has_reply = 0

        # Add the extracted data as a dictionary to the reviews list
        reviews.append({
            "name": name,
            "country": country,
            "rating": rating,
            "title": title,
            "text": text,
            "date_of_experience": date,
            "has_reply": has_reply,
            "company": company_url,  # Assumes company_url is defined outside this function
        })

    # Return the list of extracted reviews
    return reviews


# ### Go through the companies
all_reviews = []

# Limit the number of companies to scrape
max_companies = 60
# Create a list of company URLs
company_links = [company['website'] for company in companies]

# Loop through each company and scrape reviews
for i, company_url in enumerate(company_links):
    if i >= max_companies:
        break
    # Loop through the review pages
    page = 1
    while page <= 20:
        # Construct the URL for the review page
        url = f"https://www.trustpilot.com/review/{company_url}?page={page}"
        # Get the page content
        response = requests.get(url, headers=headers)

        # Check if the request was successful
        if response.status_code != 200:
            print(f"Failed to fetch page {page} for {company_url}, status code: {response.status_code}")
            break
        
        # Parse the page content
        soup = BeautifulSoup(response.content, 'lxml')
        # Extract reviews from the page with the function
        reviews = extract_reviews(soup)
        if not reviews: 
            break
        # Append the reviews to the all_reviews list
        all_reviews.extend(reviews)
        page += 1
        time.sleep(0.5)  # Sleep to avoid overwhelming the server


# ### Save to CSV
# Save reviews to CSV
csv_file = 'trustpilot_reviews_2.csv'

if all_reviews:
    # Open the CSV file in write mode
    with open(csv_file, 'w', newline='', encoding='utf-8') as f:
        # Write as a dictionary
        writer = csv.DictWriter(f, fieldnames=all_reviews[0].keys())
        writer.writeheader()
        writer.writerows(all_reviews)
    print(f"\nSaved {len(all_reviews)} reviews to '{csv_file}'")
else:
    print("No reviews found to save.")
