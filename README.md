# apr25_bde_int_supply
# trustpilot customer satisfaction
This repository is a Data Engineering group project aimed at analyzing the customer satisfaction of companies operating in the travel industry. 
The project is organized the followingwise.

#### Step 1 : Data Collection (Done)
Collection of two types of data through web scraping with BeautifulSoup. One gathering general information about companies (the domain, the number of reviews, the Trustscore, the percentages on each class of reviews (the percentage of Excellent reviews)). The other grouping all the comments of a company with more than 10000 reviews with the information related to the review (number of stars, if the company has responded to the negative review)

#### Step 2 : Data Modelling (Work in progress)
Organizing the data into database.
- **Domain frequency and IDs**: Domains were grouped and counted by frequency. A new unique domain ID was generated in the format `<rank>_<count>`, where:
  - `rank` is the frequency rank (1 for most common),
  - `count` is the number of times the domain appears in the dataset.

- **Domain Table**: Created a `Domain` table with:
  - `domain_id`: primary key in the format "rank_count" (e.g., `1_721`),
  - `domain`: cleaned domain name.

- **Company_Domain Table**: Created a `Company_Domain` linking table with:
  - `website` (foreign key from `Company`),
  - `domain_id` (foreign key from `Domain`).

These tables establish a many-to-many relationship between companies and domains and prepare the data for normalized insertion into the final database schema.


#### Step 3 : Data Consumption
Performing a sentiment analysis using Machine Learninig and produce a Dashboard displaying the different ratings of the companies.

