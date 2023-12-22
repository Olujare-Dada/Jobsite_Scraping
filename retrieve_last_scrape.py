import pandas as pd
#from bs4 import BeautifulSoup
#import requests
from jobberman_tools import Jobberman_Basic_Tools as jbt
import re
#import numpy as np



def checking_recorded_column_names(dataframe):
    df = dataframe.copy()
    mask_check = all (df[col].isin(df.columns).sum() for col in df.columns)

    if mask_check:
        mask = df["Salary"].isin(df.columns)
        idx = df.loc[mask, :].index
        print(idx)
        df.drop(idx, inplace = True)
        print(f"{len(idx)} rows dropped because they are recorded column names")
        
    return df
        


data = pd.read_parquet("Completed_Cleaned_Jobberman.parquet")
#data = pd.read_csv("Jobberman_data_raw.csv")
data = checking_recorded_column_names(data)

data.to_csv("readable.csv", index = False)

data = pd.read_csv("readable.csv", parse_dates= ["Day_Posted"])
##
data["Day_Posted"] = pd.to_datetime(data["Day_Posted"], 
                                    format = "%Y-%m-%d",
                                    dayfirst= True)
#data["Scrape_Time"] = pd.to_datetime(data["Scrape_Time"])

latest_links_scraped = list(set(data.sort_values("Day_Posted",
                                            ascending = False)["url"]))[0:5]

latest_job_name = list(set(data.sort_values("Day_Posted",
                                            ascending = False)["Job_Name"]))[0:5]

latest_company_name = list(set(data.sort_values("Day_Posted",
                                            ascending = False)["Company_Name"]))[0:5]


#response = requests.get("https://www.jobberman.com/jobs")

import re


def find_link_in_pages():
    JBT = jbt()
    soup = JBT.webpage_soup(start_url)

    if isinstance(soup, str):
        print("Returned empty string as soup")
        return

    pages = soup.find_all("span", attrs={"class": "pagination-list flex"})
    last_page = int([val.text.split() for val in pages][-1][-1])

    iterate_url = start_url + "?page="

    url_found = False
    job_name_comp_found = False
    for page_num in range(1, last_page):
        url = f"{iterate_url}{page_num}"
        page_soup = JBT.webpage_soup(url)

        links = page_soup.find_all(href=re.compile(pattern="https://www.jobberman.com/listings/"))
        
        
        job_names_soup = page_soup.find_all("p", attrs = {"class":"text-lg font-medium break-words text-link-500"})
        job_names = [job_name.text.replace("\n", "") for job_name in job_names_soup]
        
        company_names_soup = page_soup.find_all("p", attrs = {"class":"text-lg font-medium break-words text-link-500"})
        company_names = [company_name.text.replace("\n", "") for company_name in company_names_soup]
        
        
        useful_links = []
        
        

        for link in links:
            extract = link.attrs["href"]
            useful_links.append(extract)

        for link in useful_links:
            if link in latest_links_scraped:
                print(f"Link found in page {page_num}")
                print(f"Link: {link}")
                url_found = True
                print(f"The link found is {link}")
                break
            
            
        
        if url_found:
            break
        
        job_name_result = any(elem in job_names for elem in latest_job_name)
        
        comp_name_result = any(elem in company_names for elem in latest_company_name)
        
        if job_name_result and comp_name_result:
            job_name_comp_found = True
            
        if job_name_comp_found:
            break
        
        else:
            print("Latest job scraped not found yet!")
        
        
    return page_num

# Example usage

start_url = "https://www.jobberman.com/jobs"

if __name__ == "__main__":
    find_link_in_pages()


##JBT = jbt()
##soup = JBT.webpage_soup("https://www.jobberman.com/jobs")
##
##if isinstance(soup, str):
##    print("Returned empty string as soup")
##
##else:
##    pages  =soup.find_all("span", attrs = {"class": "pagination-list flex"})
##
##    last_page = int([val.text.split() for val in pages][-1][-1])
##
##
##iterate_url = "https://www.jobberman.com/jobs?page="
##
##page_found = False
##for page_num in range(1, last_page):
##    url = f"{iterate_url}{page_num}"
##
##    page_soup = JBT.webpage_soup(url)
##
##    links = page_soup.find_all(href = re.compile(pattern = "https://www.jobberman.com/listings/"))
##
##    useful_links = []
##
##    for link in links:
##        extract = link.attrs["href"]
##        useful_links.append(extract)
##
##    for link in useful_links:
##        if link == latest_link_scraped:
##            print(f"Link found in page {page_num}")
##            print(f"Link: {link}")
##            page_found = True
##            break
##    if page_found:
##        break
##
##
##    
##    
##    
