import pandas as pd
#import jobberman_machines as jm
import jobberman_machines_test as jm
#from openpyxl import load_workbook
import time

start = time.time()

soup_objs, _, datetimes, urls = jm.jobs_soups_dates_urls()

dataframe_list = jm.pre_dataframe(soup_objs, datetimes, urls)


try:
    dataframe = pd.DataFrame(data = dataframe_list,
                             columns = ["Job_Name", "Company_Name", "Industry",
                                        "Location", "Job_Type", "Job_Summary",
                                        "Education_Requirements",
                                        "Experience_Level_Requirements",
                                        "Experience_Length_Requirements",
                                        "Job_Description",
                                        "Salary", "Date_Posted", "Scrape_Time", "url"]
                             )
    if len(dataframe) > 0:
        # Append the DataFrame to the existing Excel file
        dataframe.to_csv("Jobberman_data_raw.csv", index= False, mode = "a")
        #written_data =  pd.read_csv("Jobberman_data.csv")
        #written_data.to_excel("Jobberman_data.xlsx")
        #dataframe.to_excel("Jobberman_data.xlsx", index = False, mode = "a")

except ValueError as e:
    print(f"No data scraped! Value Error raised: \n{e}")


else:
    print(dataframe.head())

end = time.time()

print(f"The entire process took {end - start} seconds")
