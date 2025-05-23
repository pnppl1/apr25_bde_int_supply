## Treatment Explanation File

In this file, we explain our approach of scraping the data.

We decided for the travel industry, since it offers a  lot of companies with many reviews (>1000) as well as mixed trust-scores. In order to avoid long loading times as well as low estimation power, we decided to exclude comapnies with smaller than a hundred total reviews for our analysis. 

### Part 1: Scraping General Info

In scrapeing_general_info.ipynb we scrape general info, this was done by iterating over each of the pages from trustpilot and extracting the company "cards" via beautiful soup. In this cards we extract the information of interest. Namely company-name, company-website, trustscore, number of reviews, operating domains. 


### Part 2: Scraping Review Classes

In order to get the review classes (Percentage of reviews being 5 star, 4 star and 3,2,1 respectively), we will need to open each company website to extract that information. This will happen in the scraping_review_classes.ipynb files. In this case, since we need to request over 1000  websites in a short time period, we encountered the issue of 403, i.e. Trustpilot blocking our IP. Probably due to too many requests. This might lead to buggy reproducability. 

### Part 3: Scraping Reviews


### Part 4: Merging tables

In merge_dataframes.ipynb we merge all tables.


### remaining TODO list:

##### imrpove general info ipynb for clarity (mixed languages etc.)
##### introduce file structure
##### convert to .ipnby to .py files
##### ?