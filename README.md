# apr25_bde_int_supply
# trustpilot customer satisfaction (Work In Progress)
This repository is a Data Engineering group project aimed at analyzing the customer satisfaction of companies operating in the travel industry. 
The project is organized the followingwise.

#### Step 1 : Data Collection (Done)
Collection of two types of data through web scraping with BeautifulSoup. One gathering general information about companies (the domain, the number of reviews, the Trustscore, the percentages on each class of reviews (the percentage of Excellent reviews)). The other grouping all the comments of a company with more than 10000 reviews with the information related to the review (number of stars, if the company has responded to the negative review)

#### Step 2 : Data Modelling (Done)
Organizing the data into a relational database using Postgresql and Docker. We implement a schema regarding our Diagram and insert the tables given our scraped data. 

#### Step 3 : Data Consumption (Done)
Performing a sentiment analysis with VADER, TextBlob and BERT and produce a Dashboard (Dash) displaying the different ratings of the companies.

#### Step 4 : Deployment (Done)
Recovering the work of Data Scientist to make an API of the best performing and leightweight model. Couple the API with Dash to have a "report" of the company.
Dockerizing all the project.

Docker container is accessible with:<br>
    ``` docker compose down && docker compose up --build```

#### Step 5 : Automation (Optional, in progress)
We will automate the steps creating a Pipeline.
