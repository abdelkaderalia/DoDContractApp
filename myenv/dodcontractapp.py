import streamlit as st
st.set_page_config(page_icon="heavy_dollar_sign",page_title="DoD Service Contract Spending Explorer",layout="wide") # Increase page width for app
import pandas as pd
import numpy as np
import sys
import requests
import openpyxl
import plotly as plt
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import time
import geopandas as gpd
from mpl_toolkits.axes_grid1 import make_axes_locatable
import mapclassify

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

@st.cache
#define function to get geo data
def get_geo(df):
    """
    This function combines the contract data with a shape file to create a map visualization.
    Input: df of contract data, link to shapefile
    Output: merged df
    """
    geo = gpd.read_file('/vsicurl/https://github.com/abdelkaderalia/LIHEAPadminapp/raw/main/Data/tl_2021_us_state.shp')
    #save shapefile to dataframe
    geo = geo.to_crs("EPSG:4326")
    geo = geo.rename(columns = {'STUSPS':'State'})

    df_map = df.merge(geo,on='State',how='left')

    return df_map


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

    # Create tabs for the different visualizations
    tab1, tab2, tab3, tab4, tab5 = st.tabs(['Understanding the Context', 'Comparing Other Agencies','Breaking Down Contracts Awarded','Categorizing Contract Types','Mapping Contracts Awarded'])

    ############## Tab 1

    tab1.write('')

    # Store links to external information
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

    # Import data to compare service contract spending across agencies
    df_agencies = get_data('compare_agencies')
    # Create list of agencies to compare
    df_agencies = df_agencies.rename(columns={'agency':'Agency'})

    # Import data to compare total spending across agencies
    df_all = get_data('compare_all_spending')

    agencies = df_agencies['Agency'].unique().tolist() # Convert agency names to list for dropdown menus
    agencies.remove('Department of Defense')
    agencies = sorted(agencies)
    agencies.insert(0, ' ')

    agency_name = 'Department of Defense'
    tab2.subheader(f'How does the {agency_name} compare to other agencies?') # Add a subheader
    tab2.markdown('<h6 align="left">View data on service contract funds that were newly awarded in the fiscal year</h6>', unsafe_allow_html=True) # Add a subheader
    agency_name2 = tab2.selectbox("Compare with another one of the federal agencies that leads in service contracting:", agencies) # Store user selection for agency name 2

    agency_describe = """DoD far outranks all other federal agencies in its service contract spending, which has been extremely proportional to its total spending over time.
                    Not all other agencies see their contract spending trends mirrored in their total spending to the same degree."""

    if agency_name2 == ' ': # If agency name 2 has not been selected

        # Filter service contract data to just DoD
        h = df_agencies[df_agencies['Agency']==agency_name]

        # Create line chart
        fig1 = px.line(h, x='fiscal_year', y='spending', color='Agency',title=f'Compare Service Contract Spending - {agency_name}',  color_discrete_sequence=CB_color_cycle) # Create plot, set title and colors

        fig1.update_xaxes(title_text="Fiscal Year",tickmode='linear') # Name x axis, show all axis tixks
        fig1.update_yaxes(title_text="Contract Funds Obligated ($)",range=[0,180000000000]) # Name y axis
        fig1.update_layout(height=600,font=dict(size=16),legend=dict(yanchor="bottom",y=-0.4,xanchor="center",x=0.5,orientation="h"),title_x=0.5) # Set plot height, font size, move legent to bottom center, center title
        fig1.update_traces(line=dict(width=3)) # Increase line thickness
        fig1.update_traces(mode="markers+lines", hovertemplate=None)
        h['hoverdata'] = h['spending'].apply(human_format) # Set format of labels
        fig1.update_layout(hovermode="x")
        fig1.update_traces(hovertemplate = "%{y}")

        tab2.plotly_chart(fig1, use_container_width=True) # Show plot
        tab2.caption('Source: USAspending')

        # Filter total spending data to just DoD
        i = df_all[df_all['Agency']==agency_name]

        fig2 = px.line(i, x='Fiscal Year', y='Obligations', color='Agency',title=f'Compare Total Spending - {agency_name}',  color_discrete_sequence=CB_color_cycle) # Create plot, set title and colors

        fig2.update_xaxes(title_text="Fiscal Year",tickmode='linear') # Name x axis, show all axis ticks
        max_i = (i['Obligations'].max()*1.1)
        fig2.update_yaxes(title_text="Total Obligations ($)",range=[0,max_i]) # Name y axis
        fig2.update_layout(height=600,font=dict(size=16),legend=dict(yanchor="bottom",y=-0.4,xanchor="center",x=0.5,orientation="h"),title_x=0.5) # Set plot height, font size, move legent to bottom center, center title
        fig2.update_traces(line=dict(width=3)) # Increase line thickness
        fig2.update_traces(mode="markers+lines", hovertemplate=None)
        h['hoverdata'] = h['spending'].apply(human_format) # Set format of labels
        fig2.update_layout(hovermode="x")
        fig2.update_traces(hovertemplate = "%{y}")# Set format of labels

        tab2.plotly_chart(fig2, use_container_width=True) # Show plot
        tab2.caption('Source: USAspending')

    else: # If agency name has been selected

        a_list = [agency_name,agency_name2] # Filter data to DoD and agency 2
        h = df_agencies[df_agencies['Agency'].isin(a_list)]

         # Create double line chart
        fig1 = px.line(h, x='fiscal_year', y='spending', color='Agency',title=f'Compare Service Contract Spending - {agency_name} and {agency_name2}', color_discrete_sequence=CB_color_cycle) # Create plot, set title and colors

        fig1.update_xaxes(title_text="Fiscal Year",tickmode='linear') # Name x axis
        fig1.update_yaxes(title_text="Contract Funds Obligated ($)",range=[0,180000000000]) # Name y axis
        fig1.update_layout(height=600,font=dict(size=16),legend=dict(yanchor="bottom",y=-0.4,xanchor="center",x=0.5,orientation="h"),title_x=0.5) # Set plot height, font size, move legent to bottom center, center title
        fig1.update_traces(line=dict(width=3)) # Increase line thickness
        fig1.update_traces(mode="markers+lines", hovertemplate=None)
        h['hoverdata'] = h['spending'].apply(human_format)
        fig1.update_layout(hovermode="x")
        #fig.update_traces(customdata = h['hoverdata'],hovertemplate = "%{customdata}")
        fig1.update_traces(hovertemplate = "%{y}")

        tab2.plotly_chart(fig1, use_container_width=True) # Show plot
        tab2.caption('Source: USAspending')

        tab2.write(agency_describe)

        i = df_all[df_all['Agency'].isin(a_list)]

        fig2 = px.line(i, x='Fiscal Year', y='Obligations', color='Agency',title=f'Compare Total Spending - {agency_name} and {agency_name2}',  color_discrete_sequence=CB_color_cycle) # Create plot, set title and colors

        fig2.update_xaxes(title_text="Fiscal Year",tickmode='linear') # Name x axis
        max_i = (i['Obligations'].max()*1.1)
        fig2.update_yaxes(title_text="Total Obligations ($)",range=[0,max_i]) # Name y axis
        fig2.update_layout(height=600,font=dict(size=16),legend=dict(yanchor="bottom",y=-0.4,xanchor="center",x=0.5,orientation="h"),title_x=0.5) # Set plot height, font size, move legent to bottom center, center title
        fig2.update_traces(line=dict(width=3)) # Increase line thickness
        fig2.update_traces(mode="markers+lines", hovertemplate=None)
        h['hoverdata'] = h['spending'].apply(human_format)
        fig2.update_layout(hovermode="x")
        #fig.update_traces(customdata = h['hoverdata'],hovertemplate = "%{customdata}")
        fig2.update_traces(hovertemplate = "%{y}")

        tab2.plotly_chart(fig2, use_container_width=True) # Show plot
        tab2.caption('Source: USAspending')


    ############# Tab 3

    tab3.subheader('How can we breakdown DoD\'s service contracts?')
    tab3.markdown('<h6 align="left">View data on all service contracts with active transactions in the fiscal year</h6>', unsafe_allow_html=True) # Add a subheader

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
                that DoD has been awarding more higher-value contracts and fewer low-value contracts."""
    tab3.write(f'The top 10 {plural} are displayed and all others are grouped together. {sub_describe}')

    ############# Tab 4

    tab4.subheader('What kinds of service contracts is DoD awarding?')

    tab4.write('')

    tab4.write('There are a lot of ways we can categorize federal contracts. These are just a few:')

    tab4a,tab4b,tab4c = tab4.tabs(['NAICS Code','Product or Service Code (PSC)','Contract Bundling'])

    tab4a.markdown('<h4 align="left">What is a NAICS code?</h4>', unsafe_allow_html=True)
    naicslink = 'https://www.census.gov/programs-surveys/economic-census/year/2022/guidance/understanding-naics.html#:~:text=The%20North%20American%20Industry%20Classification,to%20the%20U.S.%20business%20economy.'
    tab4a.write(f'[The North American Industry Classification System (NAICS)]({naicslink}) is the standard used by Federal statistical agencies in classifying business establishments for the purpose of collecting, analyzing, and publishing statistical data related to the U.S. business economy. The NAICS code for each contract indicates what industry the contract\'s work falls into.')

    tab4b.markdown('<h4 align="left">What is a PSC code?</h4>', unsafe_allow_html=True)
    psclink = 'https://www.acquisition.gov/psc-manual.'
    tab4b.write('A product or service code (PSC)is a four-digit code that describes a product, service, or research and development (R&D) activity purchased by the federal government.')

    tab4b.write(f'The [Product and Service Codes Manual]({psclink}) is maintained by the General Services Administration (GSA) and lists all the existing PSCs, which indicate what the government bought for each contract action reported in the Federal Procurement Data System (FPDS).')

    tab4c.markdown('<h4 align="left">What is contract bundling?</h4>', unsafe_allow_html=True)
    tab4c.write("""Contract bundling refers to the practice of combining multiple contract requirements into a single procurement, typically for the purpose of achieving
    cost savings or other efficiencies. In the federal government, contract bundling is governed by the Federal Acquisition Regulation (FAR), which includes specific rules
    and guidelines for when and how contract bundling can be used.""")

    tab4c.write("""Federal agencies are encouraged to use contract bundling, especially driven by category management efforts, as a way to achieve economies
    of scale and reduce administrative costs.""")

    tab4.subheader(' ')

    tab4.markdown('<h6 align="left">View data on all service contracts with active transactions in the fiscal year</h6>', unsafe_allow_html=True) # Add a subheader

    # Create slider to select year and set default value
    default = 2022
    year = tab4.slider('Select a fiscal year to view data:',min_value = 2012, max_value = 2022, value = default)
    default = year

    # Create dictionary of category options
    categories = {'NAICS Code':'naics_description',
    'Product or Service Code (PSC)':'product_or_service_code_description',
                'Contract Bundling':'contract_bundling'}

    # Use radio buttons to select
    category = tab4.radio("Categorize funds by:",categories.keys())
    col_name = categories[category]

    # Get category data based on user selection
    df_category = get_data(col_name)

    # Filter data by year
    b = df_category[df_category['fiscal_year']==year]

    b['hoverdata'] = b['total_obligated_amount'].apply(human_format)

    # Create pie chart
    fig = go.Figure(data=[go.Pie(labels=b[col_name], values=b['total_obligated_amount'])]) # Create plot
    fig.update_traces(textfont_size=16,marker=dict(colors=px.colors.qualitative.Prism),rotation=60) # Set colors and font size, and rotate plot 140 degress so that slice labels don't overlap with plot title
    fig.update_layout(height=700,font=dict(size=16),showlegend=True,title=f'{agency_name} - Obligation Breakdown by {category}, FY{year}',title_x=0.5) # Set plot height, font size, title, and center title
    fig.update_traces(customdata=b['hoverdata'],hovertemplate = "%{label} <br> %{percent} </br> %{customdata}<extra></extra>")
    tab4.plotly_chart(fig, use_container_width=True) # Show plot
    tab4.caption('Source: USAspending')

    category_describe = """The bulk of service contracts are awards for Engineering and Technical Services, which includes
    services like information technology management and telecommunications. For these services, DoD seems to prefer to hire contractors over FTEs."""

    category_describe2 = 'Based on FAR, most DoD contracts do not require bundling. FAR places restrictions on bundling to promote competition and preserve award opportunities for small businesses.'

    if category == 'NAICS Code' or category == 'Product or Service Code (PSC)':
        tab4.write(f'The top 10 codes are displayed and all others are grouped together. {category_describe}')
        tab4.write(category_describe2)
    elif category == 'Contract Bundling':
        tab4.write(category_describe)
        tab4.write(category_describe2)

    ############# Tab 5

    tab5.subheader('How can we map DoD service contracts?')

    tab5.write('')

    tab5.markdown('<h6 align="left">View data on all service contracts with active transactions in the fiscal year</h6>', unsafe_allow_html=True) # Add a subheader

    # Create slider to select year and set default value
    default_map = 2022
    map_year = tab5.slider('Select a fiscal year to map data:',min_value = 2012, max_value = 2022, value = default_map)
    default_map = map_year

    # Get state level data
    df_state_data = get_data('primary_place_of_performance_state_code')
    df_state_data = df_state_data.rename(columns={'primary_place_of_performance_state_code':'State'})

    # Merge with shape file to prepare for mapping
    df_state_map = get_geo(df_state_data)
    m = df_state_map[df_state_map['fiscal_year']==map_year]

    metrics = {'Value of Contracts Awarded ($)':'total_obligated_amount'}
    metrics_reversed = dict()
    for item in metrics.items():
        key = item[1]
        val = item[0]
        metrics_reversed[key] = val

    # Create geopandas choropleth map
    fig = px.choropleth(m,locations='State', color='total_obligated_amount',
                       color_continuous_scale="Viridis",
                       hover_name='NAME',
                       hover_data=['total_obligated_amount'],
                       locationmode='USA-states',
                       scope="usa",
                       labels=metrics_reversed,
                       height=800)

    fig.update_layout(title_text=f'Value of Service Contracts Awarded by State, FY{year}', title_x=0.5,font=dict(size=16)) # Set title and font size

    tab5.plotly_chart(fig,use_container_width=True)
    tab5.caption('Source: USAspending')

    tab5.write('The bulk of funding for service contracts is awarded in a handful of states like California, Texas, and Virginia, where there are a large number of military installations and facilities.')
    tab5.write('Common, recurring, installation-level services, like those that fall into the PSC category Facility Related Services, are especially suited to the implementation of category management practices because the places of performance for these services are usually clustered near one another.')

    tab5.markdown('<h4 align="center">Locations of Contracts for PSC Category 4.4: Facility Related Services, FY2022</h4>', unsafe_allow_html=True) # Add a subheader

    # Get coordinate data
    coord_map = get_data('data_coordinates')

    # Group contracts by PSC and create list of top 10 to use in selectbox
    group_codes = pd.DataFrame({'count' : coord_map.groupby(['product_or_service_code_description']).size()}).reset_index()
    top_codes = group_codes.nlargest(10, 'count')
    top_codes_list = top_codes['product_or_service_code_description'].tolist()
    top_codes_list.insert(0, ' ')
    psc_code = tab5.selectbox('Select a PSC to filter the map:',top_codes_list)
    tab5.caption('(Click and drag the map to move to the United States)')

    # If PSC is not selected, show all contracts on map
    if psc_code == ' ':
        tab5.map(coord_map,3)

    # If PSC is selected, filter data and then map
    elif psc_code != ' ':
        filter_map = coord_map[coord_map['product_or_service_code_description']==psc_code]
        tab5.map(filter_map,3)

    tab5.caption('Source: USAspending')
