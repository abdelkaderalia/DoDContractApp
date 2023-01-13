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


#### App starts here
if __name__ == "__main__":
    #st.markdown('<h2 align="left">How much money does the federal government spend?</h2>', unsafe_allow_html=True) # Add app title
    st.title('Department of Defense Service Contracting')
    st.header('Opportunities for Category Management')
    st.write('')

    tab1, tab2, tab3, tab4, tab5 = st.tabs(['Background', 'Comparing Other Agencies','Organizational Breakdown','Funding Breakdown','Mapping Contract Spending'])

    tab1.write('')

    usasplink = 'https://www.usaspending.gov/'
    gaolink = 'https://www.gao.gov/products/hr-93-8'

    tab1.subheader('DoD leads in spending on service contracts')
    tab1.write("""For at least the past decade, the Department of Defense (DoD) has spent more on contracts for services than any other federal agency every fiscal year.
    [DoD contracting has been on the General Accountability Office's (GAO) High-Risk List since 1992]({gaolink}), having been identified as an operation that
    is highly vulnerable to fraud, waste, abuse, and mismanagement.""")

    tab1.write('')

    tab1.subheader('Category management is a possible solution')
    tab1.write("""Category management is a strategy that helps organizations make smarter purchases of goods and services by identifying core spending categories
    and making those acquisitions as a combined enterprise, allowing for the consolidation and reduction of contracts (GSA, 2022). In doing so, organizations
    can also reduce the amount of time and resources spent on procuring services (such as reviewing bids and vetting contractors) and managing ongoing contracts.""")


    tab1.write("""Exploring trends in contract spending
    [USAspending]({usasplink}), a service run by the Department of the Treasury, publishes data on contracts as submitted by agencies to the Federal Procurement Data System.""")

    tab1.markdown("""There are a few different ways that we can consider the federal budget. The government uses the terms *obligations* and *outlays* to describe different
    views of the budget.""")

    df_agencies = get_data('compare_agencies')
    tab1.dataframe(df_agencies)
