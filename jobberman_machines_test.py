import requests
import re
from bs4 import BeautifulSoup
import time
import datetime
from urllib.request import Request, urlopen
from urllib.error import HTTPError
from threading import Thread, Lock
import threading


#threading._deadlock_debug()
#import jobberman_tools.Jobberman_Basic_Tools
from jobberman_tools import Jobberman_Basic_Tools as jbt


JBT = jbt()

website_name = "JOBBERMAN"
landing_page_URL = "https://www.jobberman.com/jobs"
landing_page_URL2 = "https://www.jobberman.com/jobs?page="



def add_last_page_decorator(func):
    """
    A decorator function that enhances the provided function by calculating the last page number of job listings.

    Args:
        func (function): The function to enhance.

    Returns:
        function: The enhanced function.
    """
    
    
    def _number_of_main_pages(URL = landing_page_URL + "?page="):
        """
        Scrapes the landing page of the website to determine the last page number of job listings.

        Args:
            URL (str): The URL of the landing page.

        Returns:
            list: A list of job page links.
        """

        thread_name = threading.current_thread().getName()
        soup = JBT.webpage_soup(landing_page_URL, thread_name = thread_name)
        print(soup)
        
        clunky_links = JBT.vals_from_href_pattern(soup, "https://www.jobberman.com/jobs?")
        
        useful_links = []
        for link in clunky_links:
            extract = JBT.link_from_html_attr(link)
            if "page=" in extract:
                useful_links.append(extract)

        pages = []
        for link in useful_links:
            page_num = link.lstrip(URL)
            page_num = int(page_num)
            pages.append(page_num)

        pages.sort()

        try:
            last_page= pages[-1]
        except (IndexError, Exception) as e:
            print(f"No pages! This could be due to an earlier hidden error!\nCheck your internet connection\nPython error: {e}")
            last_page = None
        print(f"There are {last_page} pages in {website_name}")
        jobpage_links = func(last_page)

        return jobpage_links

    return _number_of_main_pages




def _create_page_listings(base_link, list_source_URL, page_num, page_listings,
                          job_listings, mutex):

    """
    Scrapes individual pages of job listings and extracts job listing links.

    Args:
        base_link (str): The base URL of job listings pages.
        list_source_URL (str): The URL pattern for job listings pages.
        page_num (int): The page number to scrape.
        page_listings (list): A list to store job listing links.
        job_listings (dict): A dictionary to store job listings.
        mutex (Lock): A mutex for thread synchronization.
    """
    thread_name = threading.current_thread().getName()
    new_main_page_link = base_link + f"{page_num}"

    time.sleep(3)

    new_main_soup = JBT.webpage_soup(new_main_page_link, thread_name = thread_name)

    mutex.acquire()
    page_listings.extend(JBT.vals_from_href_pattern(new_main_soup, list_source_URL))

    for i, link in enumerate(page_listings):
        #print(f"LINK: {link}")
        page_listings[i] = JBT.link_from_html_attr(link)

    job_listings[page_num] = page_listings.copy()

    page_listings.clear()

    mutex.release()




def  _last_page_function(last_page, file_path = "last_page.txt"):

    """
    Manages the last page information, including reading, updating, and writing to a file.

    Args:
        last_page (int): The last page number.
        file_path (str): The path to the file storing last page information (default is "last_page.txt").
    
    Returns:
        tuple: A tuple containing the previous last page number and time.
    """

    
    import os

    current_datetime = datetime.datetime.now()
    formatted_datetime = current_datetime.strftime("%Y-%m-%d %H:%M:%S")
        
    if os.path.exists(file_path) and os.path.getsize(file_path) != 0:
        print("We have done this before")
        with open("last_page.txt", "r") as last_page_file:
            last_page_details = last_page_file.read()

        previous_last_page = last_page_details.split("\n")
        previous_last_page_num = previous_last_page[0].split(":")[1]
        previous_last_page_time = previous_last_page[1].split(":")[1]

        with open("last_page.txt", "w") as last_page_file:
            last_page_file.writelines([f"last_page: {last_page}\n",
                                       f"Time: {formatted_datetime}\n\n"])

        print("Number of pages updated!")
        

    else:
        print("We have never done this before")
        
        with open("last_page.txt", "w") as last_page_file:
            last_page_file.writelines([f"last_page: {last_page}\n",
                                       f"Time: {formatted_datetime}\n\n"])

        print("file created!")
        previous_last_page_num = 0
        previous_last_page_time = formatted_datetime 

    return previous_last_page_num, previous_last_page_time




@add_last_page_decorator
def _main_pages_links(last_page,
                     list_source_URL = "https://www.jobberman.com/listings/",
                     base_link = landing_page_URL2):

    """
    Retrieves and processes job listings from multiple pages of the website.

    Args:
        last_page (int): The last page number of job listings.
        list_source_URL (str): The URL pattern for individual job listings.
        base_link (str): The base URL of job listings pages.

    Returns:
        tuple: A tuple containing dictionaries of soup objects, job listings, and datetime information.
    """

    start = time.time()
    job_listings = {}
    job_listings_combo = {}
    threads = []
    page_listings = []
    mutex = Lock()
##    mutex_2 = Lock()
##    mutex_list = [mutex, mutex_2]
##    soup_dict = {}
##    soup_dict_combo = {}
##    #datetime_list = []
##    datetime_dict = {}
##    datetime_dict_combo = {}
##    url_dict = {}
##    url_dict_combo = {}

    
##    if last_page == None:
##        print(f"There is no last page. Probably due to an earlier error.\nAlso, check internet connection.")
##        return {}
##    previous_last_page, _ = _last_page_function(last_page)
##
##    previous_last_page = int(previous_last_page)
##
##    if previous_last_page > 0:
##        delta_pages = last_page - previous_last_page
##

    import retrieve_last_scrape as rls

    delta_pages = rls.find_link_in_pages()
    delta_pages -= 1

    if delta_pages <= 0:
        print("No new page on Jobberman!")
        return {}


    else:
        #delta_pages = last_page - previous_last_page
        batch_list = _batch_maker(delta_pages, 10)
        print(f"Scraping {delta_pages} pages")

    
    for batch in batch_list:
        print(batch)
           

        job_listings.clear()
        
        
        for page_num in range(batch[0], batch[1]):
        #for page_num in range(1,3):
            #Mutex here!

            page_listings_thread = Thread(target = _create_page_listings, args = (base_link, list_source_URL,
                                                                                  page_num, page_listings,
                                                                                  job_listings, mutex))

            threads.append(page_listings_thread)

            page_listings_thread.start()        

        print(f"The threads for job lists are: {threads}")
        for thread in threads:
            thread.join()

        threads.clear()
        job_listings_combo.update(job_listings.copy())
        
        print(f"Job listings completed for batch {batch[0]} to {batch[1]}!")
    print("Job listings completed!")

    print(f"\nThere were {len(job_listings_combo)} jobberman pages scraped")
    print(f"There were {delta_pages} unscraped pages on jobberman")
        
            #page_listings.clear()

            #print(job_listings[page_num])
        #for loop and Mutex here!
    print(f"The first scraping took {time.time()-start} seconds")
    return job_listings_combo 


def jobs_soups_dates_urls():

    start = time.time()

    job_listings_combo = _main_pages_links()

    if len(job_listings_combo) == 0:
        
        return {}, {}, {}, {}
    
    threads = []
    #page_listings = []
    mutex = Lock()
    mutex_2 = Lock()
    mutex_list = [mutex, mutex_2]
    soup_dict = {}
    soup_dict_combo = {}
    #datetime_list = []
    datetime_dict = {}
    datetime_dict_combo = {}
    url_dict = {}
    url_dict_combo = {}
    
    joblink_batches = _batch_maker(len(job_listings_combo), 5)

    print("Threads for soup dict have begun")
    for batch in joblink_batches:
            
        soup_dict.clear()
        datetime_dict.clear()
        url_dict.clear()
            
        for key in list(job_listings_combo.keys())[batch[0]:batch[1]]:

            key_list = []
            datetime_list = []
            url_list = []

            soup_thread = Thread(target = _joblinks_to_soup, args = (job_listings_combo,
                                                                             key_list,
                                                                             soup_dict,
                                                                         datetime_list,
                                                                         datetime_dict,
                                                                             key, mutex_list,
                                                                         url_dict, url_list)
                                     )
            threads.append(soup_thread)

            soup_thread.start()

                
        print(f"Threads for soup dict batch {batch} are: {threads}")
        for thread in threads:
            thread.join()

        threads.clear()
        #print(soup_dict)
        #print(datetime_dict)
        #print(url_dict)
        soup_dict_combo.update(soup_dict.copy())
        datetime_dict_combo.update(datetime_dict.copy())
        url_dict_combo.update(url_dict.copy())

        #print("Sleeping for 3 minutes...")
        #time.sleep(180)
        print("Moving to the next batch...")
                                     
            
    print("\nDone creating soup_dict!!!\n")
    print(f"soup_dict: {len(soup_dict_combo)}")
    print(f"datetime_dict_combo: {len(datetime_dict_combo)}")
    print(f"url_dict_combo: {len(url_dict_combo)}")

    print(f"The second scraping took {time.time()-start} seconds")       
    #soup_dict = _joblinks_to_soup(job_listings)

    return soup_dict_combo, job_listings_combo, datetime_dict_combo, url_dict_combo




def _joblinks_to_soup(job_listings, key_list, soup_dict,
                      datetime_list, datetime_dict, key, mutex_list, url_dict,
                      url_list):

    """
    Extract HTML content and timestamps from job listing links.

    Args:
        job_listings (dict): Dictionary of job listing links.
        key_list (list): List to store HTML content.
        soup_dict (dict): Dictionary to store HTML content per key.
        datetime_list (list): List to store timestamps.
        datetime_dict (dict): Dictionary to store timestamps per key.
        key (int): Key for the current batch.
        mutex_list (list): List of mutexes for synchronization.

    Returns:
        None
    """

    thread_name = threading.current_thread().getName()
    #soup_dict = {}
    for link in job_listings[key]:
        soup = JBT.webpage_soup(link, iterations = True, thread_name = thread_name)
        current_datetime = datetime.datetime.now()
        formatted_datetime = current_datetime.strftime("%Y-%m-%d %H:%M:%S")
        
        mutex_list[0].acquire()
        try:
            key_list.extend(soup)
            datetime_list.append(formatted_datetime)
            url_list.append(link)
        except (AttributeError, Exception) as e:
            print(e)
        mutex_list[0].release()

    mutex_list[1].acquire()
    soup_dict[key] = key_list.copy()
    datetime_dict[key] = datetime_list.copy()
    url_dict[key] = url_list.copy()
    
    key_list.clear()
    datetime_list.clear()
    mutex_list[1].release()   




def _batch_maker(number, value):
    """
    Divide a number into batches of a specified size.

    Args:
        number (int): Total number to be divided.
        value (int): Size of each batch.

    Returns:
        list of tuples: List of tuples representing batch ranges.
    """

    if value >= number:
        return [(0, number), (number, number)]

    quotient, remainder = divmod(number, value)
    result = [value] * quotient
    if remainder > 0:
        result.append(remainder)

    cumulative_sum_list = []
    cumulative_sum = 0

    for num in result:
        cumulative_sum += num
        cumulative_sum_list.append(cumulative_sum)

    cumulative_sum_list.insert(0, 0)  # Insert 0 at the beginning

    tuple_list = [(cumulative_sum_list[i], cumulative_sum_list[i + 1]) for i in range(len(cumulative_sum_list) - 1)]

    return tuple_list

        



def _within_txt_info(soup_obj):
    """
    Extract non-empty lines of text from a BeautifulSoup object.

    Args:
        soup_obj (BeautifulSoup): BeautifulSoup object containing HTML content.

    Returns:
        list: List of non-empty text lines.
    """
    
    val_list = [x for x in soup_obj.text.split("\n") if x != ""]

    return val_list


     

def _scrape_info(main_page_soup):
    job_info = JBT.html_from_tag(main_page_soup, "article")

    #Name of the Job
    job_role_tag = JBT.html_from_tag(job_info[0], "h1")

    try:
        job_role = JBT.get_text(job_role_tag[0])

    except IndexError as e:
        print(f"Job role missing:\n{e}")
        job_role = ""


    #Company name and Industry
    company_industry_tag = JBT.html_from_tag(job_info[0], "h2")

    try:
        company_name = JBT.get_text(company_industry_tag[0])
        industry = JBT.get_text(company_industry_tag[1])

    except IndexError as e:
        print(f"Company name and Industry missing:\n{e}")
        company_name = ""
        industry = ""

    #Location and Job type
    location_jobtype_tag = JBT.html_from_tag_attrs(job_info[0], "div",
                                                   "class", "mt-3")
    
    location_jobtype_list = _within_txt_info(location_jobtype_tag[0])

    try:
        location = location_jobtype_list[0]
        jobtype = location_jobtype_list[1]

    except IndexError as e:
        print(f"Location and Job type missing:\n{e}")
        location = ""
        jobtype = ""


    #Job Summary
    summary_tag = JBT.html_from_tag_attrs(job_info[0], "p", "class",
                                          "mb-4 text-sm text-gray-500")
    try:
        summary_list = _within_txt_info(summary_tag[0])
        summary = summary_list[0]

    except IndexError as e:
        print(f"Job summary is missing:\n{e}")
        summary = ""



    #Entry Requirements
    requirements_tag = JBT.html_from_tag(job_info[0], "ul")

    try:
        requirements = _within_txt_info(requirements_tag[0])

        education_requirements = requirements[1]
        experience_level_requirements = requirements[3]
        experience_length_requirements = requirements[5]

    except IndexError as e:
        print(e)
        education_requirements = ""
        experience_level_requirements = ""
        experience_length_requirements = ""

        print(f"Education requirements, experience level and length requirements missing.\n{e}")


    #Job Description
    job_description_tag = JBT.html_from_tag_attrs(job_info[0], "ul", "class",
                                                  "list-disc list-inside")

    try:
        job_description = JBT.get_text(job_description_tag[0])

    except IndexError as e:
        print(f"Job description missing:\n{e}")
        new_job_description_tag = JBT.html_from_tag_attrs(job_info[0], "div", "class",
                                                         "text-sm text-gray-500")

        if len(new_job_description_tag[0].text)> 1:
            job_description = new_job_description_tag[0].text

        else:
            job_description = ""



    #Salary
    salary_tag = JBT.html_from_tag_attrs(job_info[0], "div", "class",
                                         "text-sm text-gray-500 break-all")
    try:
        salary_tag = JBT.html_from_tag(salary_tag[0], "p")
    except IndexError as e:
        print(f"Salary missing:\n{e}")
        #print("In the soup else")
        salary_list = [x.text for x in salary_tag if "Remuneration" in x.text]
        if len(salary_list) > 0:
            print("salary_list greater than 0")
            salary = [x.text for x in salary_tag if "Remuneration" in x.text][0]

        else:
            salary_tag = JBT.html_from_tag_attrs(job_info[0], "span", "class", "text-sm font-normal")
            try:
                salary = salary_tag[0].text
            except IndexError as e:
                print(f"Salary not available for {job_role} at {company_name}")
                salary = ""
    


    #Date of post
    date_tag = JBT.html_from_tag_attrs(job_info[0], "div", "class",
                                       "flex relative justify-end pl-3 text-gray-500 font-sm ml-auto")

    try:
        date = date_tag[0].text.strip("\n") 

    except (IndexError, Exception) as e:
        print(f"Date of post missing:\n{e}")
        date = ""


    return job_role, company_name, industry, location, jobtype, summary, education_requirements, experience_level_requirements, experience_length_requirements, job_description,salary, date



if __name__ == "__main__":
    soup_objs, jobpage_links, datetimes, urls = jobs_soups_dates_urls()


        
#if __name__ == "__main__":
 #   soup_objs, jobpage_links, datetimes, urls = main_pages_links()



def pre_dataframe(soup_objs, datetimes, urls):

    if len(soup_objs) == 0:
        print("No new data to scrape!")
        return [[]]

    frame_list_combo = []
    frame_list = []
    for page_num in soup_objs.keys():
        jobs_on_page = soup_objs[page_num]
        datetime_sub = datetimes[page_num]
        url_sub = urls[page_num]

        for idx in range(2, len(jobs_on_page), 4):
            scraped_data = list(_scrape_info(jobs_on_page[idx]))
            frame_list.append(scraped_data)

        #print(len(frame_list))
        #print(len(datetime_sub))

        #print(frame_list)
        #print(datetime_sub)
        frame_list_copy = frame_list.copy()

        for i in range(len(frame_list_copy)):
            frame_list_copy[i].append(datetime_sub[i])
            frame_list_copy[i].append(url_sub[i])
        #[frame_list_copy[i].append(datetime_sub[i]) for i in range(len(frame_list))]

        frame_list_combo.extend(frame_list_copy)

        frame_list.clear()
        #for idx in range(len(datetime_sub)):
         #   frame_list.append(datetime_sub[idx])

        print(f"Done with page {page_num}")


    return frame_list_combo
        
        
        
        






    
                               
        
    

#PROCESS:
#CHECK IF WEBPAGE IS AVAILABLE WITH TIMEOUT
#GET MAIN WEBPAGE
#GET ALL JOB PAGE LISTINGS
#CHECK PARTICULAR PAGE ON JOB PAGE
#OPEN UP A PARTICULAR PAGE ON JOB PAGE
#THREAD ALL THE JOB LISTINGS ON THE PAGE: CHECK ALL JOB LISTINGS FIRST
#GET ALL THE INFORMATION FROM THE JOB LISTINGS AND STORE THEM IN A CSV USING
#MUTEXES
