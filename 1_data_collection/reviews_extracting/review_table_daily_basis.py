#!/usr/bin/env python
# coding: utf-8
import requests
from bs4 import BeautifulSoup
import time
from datetime import datetime
import csv

headers = {
    "User-Agent": "Mozilla/5.0"
}

# Base URL for the Trustpilot travel agency category, sorted by review count, paginated
base_url = "https://www.trustpilot.com/categories/travel_agency?sort=reviews_count&page="
# This list will store companies that meet the 10,000+ reviews threshold
companies = []
page = 1

while True:
    url = f"{base_url}{page}"
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
            name_tag = card.find("p", class_="CDS_Typography_heading-s__bedfe1")
            # Extract the company website
            website_tag = card.find("p", class_="styles_websiteUrlDisplayed__Eafdn")
            
            # Locate the tag containing the review count
            reviews_span = card.find("span", attrs={"data-business-unit-review-count": True})

            if not name_tag or not website_tag or not reviews_span:
                continue

            name = name_tag.get_text(strip=True)
            website = website_tag.get_text(strip=True)

            inner_span = reviews_span.find("span")
            if not inner_span:
                continue

            # Get the last <span> inside the ratingText block (it contains review count)
            review_count_text = inner_span.get_text(strip=True)
            # Convert string (e.g., "12,345") to integer
            review_count = int(review_count_text.replace(",", ""))

            # If we find a company below 10k, assume rest are smaller and stop
            if review_count < 10000:
                print(f"Found company with less than 10,000 reviews: {name} ({review_count})")
                stop = True
                break

            companies.append({
                "name": name,
                "reviews": review_count,
                "website": website
            })

        except Exception as e:
            # Catch any parsing error and skip the current card
            print(f"Error parsing card: {e}")
            continue

    if stop:
        print("Stopping: encountered company with <10,000 reviews.")
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
    reviews = []
    articles = soup.find_all("article")

    for article in articles:
        # Get time label like "15 hours ago" or "2 days ago"
        try:
            time_tag = article.find("time", attrs={"data-service-review-date-time-ago": "true"})
            if not time_tag:
                continue
            time_text = time_tag.get_text(strip=True)

            # Skip if it's not from today (e.g. "2 days ago")
            if not time_text.endswith("hours ago"):
                continue
        except Exception:
            continue

        # If it's recent enough, continue extracting the rest
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
            raw_text = article.find('p', attrs={"data-service-review-date-of-experience-typography": True}).get_text(strip=True)
            if raw_text.startswith("Date of experience:"):
                raw_date = raw_text.replace("Date of experience:", "").strip()
                date_obj = datetime.strptime(raw_date, "%B %d, %Y").date()
                if date_obj != datetime.today().date():
                    continue
                date = date_obj
            else:
                continue
        except Exception:
            continue

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
csv_file = 'trustpilot_reviews_daily.csv'

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
