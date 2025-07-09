#!/usr/bin/env python
# coding: utf-8
import requests
from bs4 import BeautifulSoup
import pandas as pd
import time
import random
import re

df_final = pd.read_csv("general_info.csv")
df_filtered = (
    df_final
    .astype({"number_review":float})
    .loc[lambda df: df["number_review"]>100]
    .reset_index(drop=True)
    )
df_filtered

# empty dict to prepare the df
df_prep = {
    "website": [],
    "5_star_percentage": [],
    "4_star_percentage": [],
    "3_star_percentage": [],
    "2_star_percentage": [],
    "1_star_percentage": [],    
}

url_base = "https://www.trustpilot.com/review/"

for index, website in enumerate(df_filtered["website"].to_list()):
    print(index, website)
    
    url_complete = url_base + website
    headers = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64)"}

    # use sleep in case of ip bloackge (error 403)
    # time.sleep(random.uniform(5, 15))
    
    try:
        html = requests.get(url_complete, headers=headers, timeout=10)
        if html.status_code != 200:
            print(f"Error loading {html.status_code} at {index, website}")
            break  # oder break, je nach gewünschtem Verhalten

        soup = BeautifulSoup(html.text, "lxml")

        #extract relevant field that includes percentages
        field = soup.find("div", class_="paper_paper__EGeEb paper_outline__bqVmn card_card__yyGgu styles_reviewFilterCard__sn4Nz")
        
        if field:
            df_prep["website"].append(website)
            review_classes = re.findall(r'\d+%|<1%', field.text)
            if len(review_classes) == 5:
                df_prep["5_star_percentage"].append(review_classes[0])
                df_prep["4_star_percentage"].append(review_classes[1])
                df_prep["3_star_percentage"].append(review_classes[2])
                df_prep["2_star_percentage"].append(review_classes[3])
                df_prep["1_star_percentage"].append(review_classes[4])
            else:
                print(f"unexpected number of review classes at {website}: {review_classes}")
                continue
        else:
            print(f"field not found on {website}")
            break

    except Exception as e:
        print(f"error at {website}: {e}")
        continue

# DataFrame erzeugen
df_reviews = pd.DataFrame(df_prep)
print(df_reviews.isna().sum())


df_reviews = pd.DataFrame(df_prep)
#quick look
print(df_reviews.isna().sum())

# df_reviews.to_csv("review_classes.csv",index=False)

