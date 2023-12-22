# -*- coding: utf-8 -*-
"""
Created on Sat Oct 21 00:22:25 2023

@author: olanr
"""

import streamlit as st
import pandas as pd
import plotly.express as px 
from datetime import datetime
import pyodbc

st.title('DECISION SUPPORT SYSTEM')

#begin_date_time = datetime(2023, 10, 8, 9, 30)
#another_date_time = datetime(2023, 10, 11, 9, 30)



# @st.cache_data
# def load_data():
#     df = pd.read_csv("Downloaded_db.csv")
#     df["Day_Posted"] = pd.to_datetime(df["Day_Posted"])
#     df["Scrape_Time"] = pd.to_datetime(df["Scrape_Time"])
#     return df




# Initialize connection.
# Uses st.cache_resource to only run once.

    
    
@st.cache_resource
def init_connection():
    return pyodbc.connect(
        "DRIVER={ODBC Driver 17 for SQL Server};SERVER="
        + st.secrets["server"]
        + ";DATABASE="
        + st.secrets["database"]
        + ";UID="
        + st.secrets["username"]
        + ";PWD="
        + st.secrets["password"]
    )

conn = init_connection()

# Perform query.
# Uses st.cache_data to only rerun when the query changes or after 10 min.
@st.cache_data(ttl=6000)
def run_query(query):
    with conn.cursor() as cur:
        cur.execute(query)
        return cur.fetchall()

data_load_state = st.text('Loading data...')
rows = run_query("SELECT * from [dbo].[Final_template_df];")
# rows = run_query(f"""SELECT *
# FROM [dbo].[Final_template_df]
# WHERE day_posted >= DATEADD(month, -1, GETDATE())""")

data_load_state.text('Loading data...done!')
# Print results.


reload_database = st.button("Reload")
if reload_database:
    data_load_state = st.text('Refreshing data from the database...')
    rows = run_query("SELECT * from [dbo].[Final_template_df];")
    
    data_load_state.text('Loading data...done!')
# else:
#     st.write('Goodbye')


df = pd.DataFrame([tuple(row) for row in rows], columns = [desc[0] for desc in rows[0].cursor_description])
df["Day_Posted"] = pd.to_datetime(df["Day_Posted"])
df["Scrape_Time"] = pd.to_datetime(df["Scrape_Time"])


#df = load_data()

begin_date_time = df["Day_Posted"].min().to_pydatetime()
end_date_time = df["Day_Posted"].max().to_pydatetime()
mean_date_time = df["Day_Posted"].mean()#.to_pydatetime().replace(second=0, microsecond=0)
# filter_date_time = st.slider(
#     "Select Time Period",
#     (begin_date_time, end_date_time),
#     format="MM/DD/YY")

filter_date_time = st.date_input(
    "Select your vacation for next year",
    mean_date_time,
    format="MM.DD.YYYY",
)



begin_date = begin_date_time.strftime('%Y-%m-%d')
filter_date = filter_date_time.strftime('%Y-%m-%d')

st.write(f"### Showing data between {begin_date} and {filter_date}")
displayed_df = df.loc[df["Day_Posted"].dt.date <= mean_date_time.date(), :]
displayed_df = displayed_df[['Job_Name', 'Company_Name', 'Industry', 'Location',
       'Job_Type', 'Job_Summary', 'Education_Requirements',
       'Experience_Level_Requirements', 'Experience_Length_Requirements',
       'Job_Description', 'Salary_Range', 'Salary', 'Day_Posted', 'url']]


#displayed_df = displayed_df.loc[displayed_df["Salary_Range"]!= "Not given", :]
displayed_df.sort_values("Day_Posted", ascending = True)
displayed_df = displayed_df.drop_duplicates()
df_st = st.dataframe(
    displayed_df.sort_values("Day_Posted", ascending = False),
    column_config={
        "Salary_Range": st.column_config.Column(
            "Salary (₦)",
            help="Remuneration in Naira",
        ),
        "url": st.column_config.LinkColumn("Job URL")
        
    
    },
    hide_index=True,
)

#st.write(df_st)


@st.cache_resource
def convert_df(df):
    # IMPORTANT: Cache the conversion to prevent computation on every rerun
    return df.to_csv().encode('utf-8')

csv = convert_df(displayed_df)

st.download_button(
    label="Download data as CSV",
    data=csv,
    file_name='Displayed_data.csv',
    mime='text/csv',
)



#TOP INDUSTRIES:
def top_category(category_name, top_n):
    x_df = displayed_df.loc[df[category_name] != "Not given", :]
    x_df = x_df[category_name].value_counts().nlargest(top_n).reset_index()
    x_df.rename(columns = {
                            "Frequency": f"{category_name}"}, inplace = True)
    
    return x_df


st.write("### Select Category")
category_name = st.selectbox(
    '',
    ('Industry', 'Job Type', 'Education Requirements', "Experience Length",
      "Experience Level"))

category_dict = {
    'Industry': 'Industry',
    'Job Type': 'Job_Type',
    'Education Requirements': 'Education_Requirements',
    "Experience Length": "Experience_Length_Requirements",
    "Experience Level": "Experience_Level_Requirements"
    }

category_chosen = category_dict[category_name]
top_n = st.sidebar.slider("Top Value by Category", 1, 
                          len(df[category_chosen].unique()), 1)

st.write(f"### Top {top_n} most common {category_name}")




chart_data1 = top_category(category_dict[category_name], top_n)
st.write(chart_data1)

# st.bar_chart(
#    chart_data1, x=f"{category_dict[category_name]}", y=["Frequency"]) #color=["#FF0000"]


fig1=px.bar(chart_data1,x = ["count"] , y= f"{category_dict[category_name]}", 
            orientation='h')
st.write(fig1)





def top_salary_by_category(category_name, top_n):
    salary_mask = (displayed_df["Salary"] != "Not given") & (displayed_df["Salary"] != "Commission Only")

    salary_df = displayed_df.loc[salary_mask, :]
    #salary_df["Salary"] = salary_df["Salary"].astype(float)
    salary_df["Salary"] = pd.to_numeric(salary_df["Salary"], errors='coerce')


    x_df = salary_df.groupby(category_name).agg({'Salary': 'mean'}).nlargest(top_n, columns='Salary').reset_index()#salary_df.groupby(category_name).mean()["Salary"].nlargest(top_n).reset_index()
    #x_df.rename(columns = {"index": category_name,
     #                       category_name: "Salary"}, inplace = True)
    
    
    return x_df



chart_data2 = top_salary_by_category(category_chosen, top_n)

fig2=px.bar(chart_data2,x =["Salary"] , y= category_chosen, 
            orientation='h')
st.write(fig2)






# st.write("### Select Category")
# salary_category_name = st.selectbox(
#     '',
#     ('Industry', 'Job Type', 'Education Requirements', "Experience Length",
#       "Experience Level"))



# salary_top_n = st.sidebar.slider("Top Value by Category", 1, 
#                           len(df[category_dict[salary_category_name]].unique()), 1)



# st.bar_chart(
#    chart_data2, x= f"{category_dict[category_name]}, y=["Salary"], color=["#FF0000"])



    


# @st.cache_data
# def load_data():
#     df = pd.read_csv("Downloaded_db.csv")
#     return df


# data_load_state = st.text('Loading data...')
# df = load_data()
# data_load_state.text('Loading data...done!')


# st.write(df.head())


# #TOP INDUSTRIES:
# def top_category(category_name, top_n):
#     x_df = df.loc[df[category_name] != "Not given", :]
#     x_df = x_df[category_name].value_counts().nlargest(top_n).reset_index()
#     x_df.rename(columns = {"index": f"{category_name}",
#                            f"{category_name}": "Frequency"}, inplace = True)
    
#     return x_df


# category_name = st.selectbox(
#     'Select Category:',
#     ('Industry', 'Job Type', 'Education Requirements', "Experience Length",
#      "Experience Level"))

# category_dict = {
#     'Industry': 'Industry',
#     'Job Type': 'Job_Type',
#     'Education Requirements': 'Education_Requirements',
#     "Experience Length": "Experience_Length_Requirements",
#     "Experience Level": "Experience_Level_Requirements"
#     }

# top_n = st.slider("Top Value", 1, len(df[category_dict[category_name]].unique()), 1)

# st.write(f"### Top {top_n} most common {category_name}")




# chart_data1 = top_category(category_dict[category_name], top_n)

# #st.bar_chart(
#  #  chart_data1, x=f"{category_dict[category_name]}", y=["Frequency"]) #color=["#FF0000"]


# fig1=px.bar(chart_data1,x = ["Frequency"] , y= f"{category_dict[category_name]}", 
#            orientation='h')
# st.write(fig1)


# """
# salary_mask = (df["Salary"] != "Not given") & (df["Salary"] != "Commission Only")

# salary_df = df.loc[salary_mask, :]
# salary_df["Salary"] = salary_df["Salary"].astype(float)


# def top_salary_by_category(category_name, top_n):
#     x_df = salary_df.groupby(category_name).sum()["Salary"].nlargest(top_n).reset_index()
    
#     return x_df


# chart_data = top_salary_by_category("Industry", 7)

# st.bar_chart(
#    chart_data, x="Industry", y=["Salary"], color=["#FF0000"])
# """

    
