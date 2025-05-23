## Treatment Explanation File

In this file, we explain our approach of scraping the data.

We decided for the travel industry, since it offers a  lot of companies with many reviews (>1000) as well as mixed trust-scores. In order to avoid long loading times as well as low estimation power, we decided to exclude comapnies with smaller than a hundred total reviews for our analysis. 

### Part 1: Scraping General Info

In scrapeing_general_info.ipynb we scrape general info, this was done by iterating over each of the pages from trustpilot and extracting the company "cards" via beautiful soup. In this cards we extract the information of interest. Namely company-name, company-website, trustscore, number of reviews, operating domains. 


### Part 2: Scraping Review Classes

In order to get the review classes (Percentage of reviews being 5 star, 4 star and 3,2,1 respectively), we will need to open each company website to extract that information. This will happen in the scraping_review_classes.ipynb files. In this case, since we need to request over 1000  websites in a short time period, we encountered the issue of 403, i.e. Trustpilot blocking our IP. Probably due to too many requests. This might lead to buggy reproducability. 

### Part 3: Scraping Reviews

Implementation of this step can be found in [reviews_extracting/review_table.ipynb](https://github.com/pnppl1/apr25_bde_int_supply/blob/main/reviews_extracting/review_table.ipynb) file.
The data from the reviews page of the chosen category was extracted to get the list of companies with a review number higher than 10,000. It was extracted with the BeautifulSoup function, searching for specific elements and attributes. For every company, the reviews with the name, country, review title, text, rating (in number of stars), and whether the company replied to the review were collected. The information resulted in a [CSV](https://github.com/pnppl1/apr25_bde_int_supply/blob/main/reviews_extracting/trustpilot_reviews_2.csv) file with 21,000 reviews.

### Part 4: Merging tables

In merge_dataframes.ipynb we merge all tables.


### remaining TODO list:

##### imrpove general info ipynb for clarity (mixed languages etc.)
##### introduce file structure
##### convert to .ipnby to .py files
##### ?