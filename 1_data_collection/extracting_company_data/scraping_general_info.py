#!/usr/bin/env python
# coding: utf-8
import requests
from bs4 import BeautifulSoup
import pandas as pd

stop_scraping = False

df_list = []
for page_number in range(1, 501):
    if stop_scraping:
        break

    print(page_number)
    url = f"https://www.trustpilot.com/categories/travel_vacation?page={page_number}&sort=reviews_count"
    headers = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64)"}
    html = requests.get(url, headers=headers)

    if html.status_code != 200: 
        print("error loading", html.status_code)
        break

    soup = BeautifulSoup(html.text, "lxml")
    cards = soup.find_all("div", attrs={"class": "CDS_Card_card__16d1cc CDS_Card_appearance-default__16d1cc CDS_Card_borderRadius-m__16d1cc styles_wrapper__Jg8fe"})

    company_names, websites, ratings, number_reviews, domains = [], [], [], [], []

    for card in cards:
        # number of Reviews
        number_review_tag = card.select_one('p[class*="styles_ratingText"]')
        number_review_element = (
            number_review_tag.text.split()[1].split("|")[-1].replace(",", "") if number_review_tag else None
        )
        if number_review_element and float(number_review_element) < 100:
            print("Exclude companies with small amount of reviews - stopping")
            stop_scraping = True
            break

        number_reviews.append(number_review_element)

        # Company
        company_nametag = card.find("p", class_="CDS_Typography_heading-xs__bedfe1")
        company_names.append(company_nametag.text.strip() if company_nametag else None)

        # Website 
        website_tag = card.select_one('p[class*="websiteUrlDisplayed"]')
        websites.append(website_tag.text.strip() if website_tag else None)

        # TrustScore
        rating_tag = card.select_one('span[class*="styles_trustScore"]')
        ratings.append(float(rating_tag.text.split()[-1]) if rating_tag else None)

        #domains
        domain_tag = card.find_all("div", attrs={"class":"styles_wrapper__90tpR styles_categoriesLabels__Y_RKI styles_desktop__ytR38"})
        for domain in domain_tag: domains.append(domain.text.split("·"))

    if stop_scraping:
        break

    df = pd.DataFrame({
        "company": company_names,
        "website": websites,
        "rating": ratings,
        "number_review": number_reviews,
        "domain": domains
    })
    df_list.append(df)

df_final = pd.concat(df_list)

# df_final.to_csv("general_info.csv", index = False)

