import pandas as pd
import numpy as np
import asyncio
import aiohttp
import sys
import requests

# Create dictionary of agencies and common government account Codes
codes = {'Department of Defense':'097',
        'Department of Energy':'089',
        'Department of Veterans Affairs':'036',
        'Department of Health and Human Services':'075',
        'Department of Homeland Security':'070',
        'General Services Administration (GSA)':'047',
        'Department of State':'019',
        'Department of Transportation':'069',
        'Department of Justice':'015',
        'Department of the Interior':'014',
        'Agency for International Development (USAID)':'072',
        'National Aeronautics and Space Administration (NASA)':'080'}

async def async_func(toptier_code,type):
    async with aiohttp.ClientSession() as session:
        arr = []

        for year in range(2012,2023):
            df = process_year(session,year,toptier_code,type)
            arr.append(df)

        results = await asyncio.gather(*arr)

        if type == 'historical':
            full = pd.DataFrame(columns=['fiscal_year','toptier_code','transaction_count','obligations','messages','latest_action_date'])
            for item in results:
                full = full.append(item)

            full['fiscal_year']=full['fiscal_year'].astype(str) # Redefine year as string
            full = full.rename(columns={"fiscal_year":"Fiscal Year","obligations":"Obligations"}) # Change column names
            full = full.reset_index(drop=True)

        elif type == 'category':
            full = pd.DataFrame(columns=['fiscal_year','name','abbreviation','total_obligations','transaction_count','new_award_count','children'])
            for item in results:
                full = full.append(item)

            full = full.rename(columns={"name": "Subagency","fiscal_year":"Fiscal Year","total_obligations":"Obligations"}) # Rename columns
            full['Fiscal Year']=full['Fiscal Year'].astype(str) # Redefine year as string
            full = full.reset_index(drop=True)

        return full

async def process_year(session,year,toptier_code,type):
    url = 'https://api.usaspending.gov'
    payload = {"fiscal_year":year}

    if type == 'historical':
        endpoint=f'/api/v2/agency/{toptier_code}/awards/'
        async with session.get(f'{url}{endpoint}',params=payload) as resp:
            data = await resp.json(content_type=None)
            df = pd.DataFrame(data.items()).transpose() # Convert to df and transpose
            df.columns = df.iloc[0] # Reset column names using first row
            df = df.tail(df.shape[0]-1) # Remove first row

    elif type == 'category':
        endpoint=f'/api/v2/agency/{toptier_code}/sub_agency/'
        async with session.get(f'{url}{endpoint}',params=payload) as resp:
            data = await resp.json(content_type=None)
            df = pd.DataFrame(data['results'])
            df.insert(loc = 0,column = 'fiscal_year',value = year)

    return df

df = pd.DataFrame()

for d in codes.keys(): # For agency 1 and agency 2
    code = codes[d]
    a = asyncio.run(async_func(code,'historical')) # Run function to pull award data
    a.insert(loc = 1,column = 'Agency',value = d)
    a = a[['Fiscal Year','Agency','Obligations']]
    df = df.append(a)

df.to_csv('/Users/alia/Documents/Github/DoDContractApp/Clean Data/Plot Data/compare_all_spending.csv',index=False)
