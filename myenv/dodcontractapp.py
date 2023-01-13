import streamlit as st
st.set_page_config(page_icon="heavy_dollar_sign",page_title="DoD Service Contract Spending Explorer",layout="wide") # Increase page width for app
import pandas as pd
import numpy as np
import asyncio
import aiohttp
import sys
import requests
import openpyxl
import plotly as plt
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import time
import webbrowser
from PIL import Image


#### Functions

def human_format(num):
    """
    This function changes numbers to a human-interpretable SI format.
    Input: num (int)
    Output: Formatted number (string)
    """
    num = float('{:.3g}'.format(num))
    magnitude = 0
    while abs(num) >= 1000:
        magnitude += 1
        num /= 1000.0
    return '{}{}'.format('{:f}'.format(num).rstrip('0').rstrip('.'),
                         ['', 'K', 'M', 'B', 'T'][magnitude])

@st.cache(show_spinner=False)
def get_data(fname):
    """
    This function imports a file of longitudinal contract spending data from the Github repository for this project.
    Input: file name
    Output: Dataframe of agencies their total spending (pd.Dataframe)
    """
    url = f'https://github.com/abdelkaderalia/DoDContractApp/raw/main/Clean%20Data/Plot%20Data/{fname}.csv'
    df = pd.read_csv(url)
    return df


#### Other setup

# Create a list of colorblind-friendly colors for plotting
CB_color_cycle = ['#377eb8', '#ff7f00', '#4daf4a',
                  '#f781bf', '#a65628', '#984ea3',
                  '#999999', '#e41a1c', '#dede00']


#### App starts here
if __name__ == "__main__":
    #st.markdown('<h2 align="left">How much money does the federal government spend?</h2>', unsafe_allow_html=True) # Add app title
    st.title('Department of Defense Service Contracting')
    st.header('Opportunities for Category Management')
    st.write('')

    tab1, tab2, tab3, tab4, tab5 = st.tabs(['Understanding the Context', 'Comparing Other Agencies','Breaking Down Contracts Awarded','Categorizing Contract Types','Mapping Contracts and Spending'])

    ############## Tab 1

    tab1.write('')

    usasplink = 'https://www.usaspending.gov/search'
    gaolink = 'https://www.gao.gov/products/hr-93-8'
    gsalink = 'https://www.gsa.gov/buy-through-us/category-management#:~:text=Category%20Management%20is%20the%20practice,and%20effectiveness%20of%20acquisition%20activities'

    tab1.subheader('DoD leads in spending on service contracts, and some are concerned')
    tab1.write(f'For at least the past decade, the Department of Defense (DoD) has spent more on contracts for services than any other federal agency every fiscal year. [DoD contracting has been on the General Accountability Office\'s (GAO) High-Risk List since 1992]({gaolink}), having been identified as an operation that is highly vulnerable to fraud, waste, abuse, and mismanagement.')

    tab1.write('')

    tab1.subheader('Category management is a possible solution')
    tab1.write(f'[Category management]({gsalink}) is a strategy that helps organizations make smarter, more cost-effective purchases of goods and services by identifying core spending categories and making those acquisitions as a combined enterprise, allowing for the consolidation and reduction of contracts. In doing so, organizations can also reduce the amount of time and resources spent on procuring services and managing ongoing contracts.')

    #cm = Image.open('https://github.com/abdelkaderalia/DoDContractApp/blob/main/Images/cm.png?raw=true')
    #tab1.image(image,caption='Source: Acquisition.gov')

    tab1.write('')

    tab1.subheader("""Exploring trends in contract spending can demonstrate the potential for category management""")
    tab1.write('Visualizing contract data can illuminate not only the magnitude of DoD’s contractual service spending but also highlight the potential benefit of a wider implementation of category management.')

    tab1.write('')

    tab1.subheader("""Data source and limitations""")

    tab1.write(f'[USAspending]({usasplink}), a service run by the Department of the Treasury, publishes data on contracts as submitted by agencies to the Federal Procurement Data System.')

    tab1.markdown("""This interactive web app features USAspending data for *prime award contracts for services only.* This does not include contracts to purchase physical products,
    subaward contracts, or indefinite delivery vehicles (IDVs, a type of contract that allows the purchaser to buy an indefinite quantity of products or services over a fixed time period.)""")

    ############# Tab 2

    df_agencies = get_data('compare_agencies')
    df_agencies = df_agencies.rename(columns={'agency':'Agency'})

    agencies = df_agencies['Agency'].unique().tolist() # Convert agency names to list for dropdown menus
    agencies.remove('Department of Defense')
    agencies = sorted(agencies)
    agencies.insert(0, ' ')

    agency_name = 'Department of Defense'
    tab2.subheader(f'How does the {agency_name} compare to other agencies?') # Add a subheader
    tab2.markdown('<h6 align="left">View data on service contract funds that have been obligated (spent) to date</h6>', unsafe_allow_html=True) # Add a subheader
    agency_name2 = tab2.selectbox("Compare with another of the federal agencies that leads in service contracting:", agencies) # Store user selection for agency name 2

    if agency_name2 == ' ': # If agency name 2 has been selected

        h = df_agencies[df_agencies['Agency']==agency_name]
         # Create double line chart
        fig = px.line(h, x='fiscal_year', y='spending', color='Agency',title=f'Compare Contract Spending - {agency_name}',  color_discrete_sequence=CB_color_cycle) # Create plot, set title and colors

        fig.update_xaxes(title_text="Fiscal Year",tickmode='linear') # Name x axis
        fig.update_yaxes(title_text="Contract Funds Obligated ($)",range=[0,180000000000]) # Name y axis
        fig.update_layout(height=600,font=dict(size=16),legend=dict(yanchor="bottom",y=-0.4,xanchor="center",x=0.5,orientation="h"),title_x=0.5) # Set plot height, font size, move legent to bottom center, center title
        fig.update_traces(line=dict(width=3)) # Increase line thickness
        fig.update_traces(mode="markers+lines", hovertemplate=None)
        h['hoverdata'] = h['spending'].apply(human_format)
        fig.update_layout(hovermode="x")
        #fig.update_traces(customdata = h['hoverdata'],hovertemplate = "%{customdata}")
        fig.update_traces(hovertemplate = "%{y}")

        tab2.plotly_chart(fig, use_container_width=True) # Show plot
        tab2.caption('Source: USAspending')

    else:

        a_list = [agency_name,agency_name2]
        h = df_agencies[df_agencies['Agency'].isin(a_list)]

         # Create double line chart
        fig = px.line(h, x='fiscal_year', y='spending', color='Agency',title=f'Compare Contract Spending - {agency_name} and {agency_name2}',  color_discrete_sequence=CB_color_cycle) # Create plot, set title and colors

        fig.update_xaxes(title_text="Fiscal Year",tickmode='linear') # Name x axis
        fig.update_yaxes(title_text="Contract Funds Obligated ($)",range=[0,180000000000]) # Name y axis
        fig.update_layout(height=600,font=dict(size=16),legend=dict(yanchor="bottom",y=-0.4,xanchor="center",x=0.5,orientation="h"),title_x=0.5) # Set plot height, font size, move legent to bottom center, center title
        fig.update_traces(line=dict(width=3)) # Increase line thickness
        fig.update_traces(mode="markers+lines", hovertemplate=None)
        h['hoverdata'] = h['spending'].apply(human_format)
        fig.update_layout(hovermode="x")
        #fig.update_traces(customdata = h['hoverdata'],hovertemplate = "%{customdata}")
        fig.update_traces(hovertemplate = "%{y}")

        tab2.plotly_chart(fig, use_container_width=True) # Show plot
        tab2.caption('Source: USAspending')

    ############# Tab 3

    tab3.subheader('How can we breakdown DoD\'s service contracts?')
    tab3.markdown('<h6 align="left">View data on all service contracts that were awarded by DoD, but have not necessarily been obligated</h6>', unsafe_allow_html=True) # Add a subheader

    tab3.write(' ')

    col1, col2, col3, col4, col5, col6 = tab3.columns(6)
    view = col1.radio('Choose your view:',('Awarding Subagency','Awarding Office','Contract Recipient'))
    mode = col2.radio('Choose your subtotal method:',('Dollar Value','Number of Contracts'))
    sub_col_names = {'Awarding Subagency':['awarding_sub_agency_name','subagencies'],'Awarding Office':['awarding_office_name','offices'],'Contract Recipient':['recipient_name','recipients']}
    sub_list = sub_col_names.get(view)
    sub_col = sub_list[0]

    if mode == 'Dollar Value':
        sub_data = sub_col
        Y = 'total_obligated_amount'
        Y_label = 'Value of Contracts Awarded($)'
        Y_title = 'Value of Contracts Awarded'
    elif mode == 'Number of Contracts':
        sub_data = f'{sub_col}_count'
        Y = 'count'
        Y_label = 'Number of Contracts Awarded'
        Y_title = Y_label

    df_sub = get_data(sub_data)
    df_sub = df_sub.rename(columns={sub_col:view})
    df_sub = df_sub.sort_values(Y,ascending=False)
    col_title = view.split(' ')[1]

    fig = px.bar(df_sub, x='fiscal_year', y=Y, color=view,title=f'{agency_name} - {Y_title} by {col_title}',color_discrete_sequence=px.colors.qualitative.Prism) # Create plot and set title and colors

    fig.update_xaxes(title_text="Fiscal Year",tickmode='linear') # Name x axis
    fig.update_yaxes(title_text=Y_label) # Name y axis
    fig.update_layout(height=700,font=dict(size=16),showlegend=False,title_x=0.5) # Set plot height, font size, hide legend, and center plot title
    fig.update_traces(hovertemplate = "%{y}")

    tab3.plotly_chart(fig, use_container_width=True) # Show plot
    tab3.caption('Source: USAspending')
    #tab3.markdown('<p style="text-align: right;">Source: USAspending</p>', unsafe_allow_html=True)

    plural = sub_list[1]
    sub_describe = """Though the dollar value of contracts awarded peaked in FY2019, the number of contracts awarded has been
                decreasing steadily since FY2012. The proportion of funding awarded by larger subagencies and offices remains relatively consistent, indicating
                that DoD been more higher-value contracts and fewer low-value contracts."""
    tab3.write(f'The top 10 {plural} are displayed and all others are grouped together. {sub_describe}')
