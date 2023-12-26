# Jobsite_Scraping

## About the Project:
This project provides a system for automating the scraping of a jobsite.

## Installation
- dotenv
- streamlit
- pandas
- plotly
- import pyodbc
- import requests
- BeautifulSoup
- warnings
- azure
- openai


## Project Objectives Achieved
The following was achieved in the project:
1. Scrape a jobsite using Beautiful soup
2. Clean and transform the scraped information
3. Create machine learning algorithms to predict the salary ranges of jobs given certain features about jobs, and association between certain job skills to help decipher more similar roles.
4. Upload the cleaned data on Azure SQL Database.
5. Upload the cleaned data as a parquet file in an Azure Data Lake Gen2.
6. Upload the raw data file before cleaning, to the Azure Data Lake Gen2 to a different container.
7. Build a deployment solution using streamlit.
8. Automate the entire process (except Machine learning) to run everyday using task scheduler.
9. For missing data on the jobsite, chatgpt's API was used to make inference of what the missing values could be. The missing values derived from chatgpt's API were metrics like salary, years of experience that were buried deep in the job description given in the jobsite. Using the LLM's ability to understand text, some of these missing values which were embedded in the description were easily extracted.


## Project Steps:
1. Automate the scraping of the data from the website into a csv file
2. Create a cleaning script for the data in the csv file.
3. Create a script for uploading the raw csv file and the cleaned csv file to an Azure blob storage.
4. Create a script for uploading the cleaned data into Azure SQL DB
5. Create a machine learning algorithm that can predict the salary range reasonably well
6. Store the Machine learning algorithm file.
7. Create a script that displays the results of the machine learning algorithm on a strealit application. The application also allows you to slice and visualize the data directly from the Azure SQL DB
8. All the scripts from scraping down to uploading the file to the Azure SQL DB are kept in an orchestrator.ipynb file which runs them all in sequence.


## Code explanation:
The explanation of the code functions are given in the codeExplanation.txt file
