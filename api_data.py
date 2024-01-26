"""Functions to retrieve data from an API"""

import os 
import json
import requests
import pandas as pd
from dotenv import load_dotenv


# Get env variables
load_dotenv()

headers={'User-agent': 'Mozilla/5.0'}

def fetch_execution_info() -> pd.DataFrame:
    # Retrieve API endpoint
    API_GEX_EX_INF = os.environ.get('API_GEX_EX_INF','Unable to retrieve API_GEX_EX_INF')
    
    # GET request
    response = requests.get(url=API_GEX_EX_INF, headers=headers, stream=True)
    content = response.content.decode("utf-8")
       
    # To pandas df
    df = pd.DataFrame(json.loads(content))
    
    return df

def fetch_zero_gamma() -> pd.DataFrame:
    # Retrieve API endpoint
    API_GEX_ZERO = os.environ.get('API_GEX_ZERO','Unable to retrieve API_GEX_ZERO')
    
    # GET request
    response = requests.get(url=API_GEX_ZERO, headers=headers, stream=True)
    content = response.content.decode("utf-8")
       
    # To pandas df
    df = pd.DataFrame.from_dict(json.loads(content), orient='index')
    df = df.reset_index().drop(columns={'level_0'})
    df['index'] = df['index'].transform(lambda x: x[0])
    df['Zero Gamma'] = df['Zero Gamma'].transform(lambda x: x[0])
    df['index'] = pd.to_datetime(df['index'])
    df.set_index(['index'], inplace=True)
    df.index.name='Date'
    
    return df

def fetch_gex_profile() -> dict:
    # Retrieve API endpoint
    API_GEX_PROFILE = os.environ.get('API_GEX_PROFILE','Unable to retrieve API_GEX_PROFILE')
    
    # GET request
    response = requests.get(url=API_GEX_PROFILE, headers=headers, stream=True)
    content = response.content.decode("utf-8")
    dict_content = json.loads(content)
    
    # pd.DataFrame(dict_content['65b27f58e6d8ca67493283ef'])
    
    return dict_content

def fetch_gex_levels() -> dict:
    # Retrieve API endpoint
    API_GEX_STRIKES = os.environ.get('API_GEX_STRIKES','Unable to retrieve API_GEX_STRIKES')
    
    # GET request
    response = requests.get(url=API_GEX_STRIKES, headers=headers, stream=True)
    content = response.content.decode("utf-8")
    dict_content = json.loads(content)
    
    # pd.DataFrame(dict_content['65b27f58e6d8ca67493283ef'])
    
    return dict_content

def fetch_ohlc_data() -> pd.DataFrame:
    # Retrieve API endpoint
    API_GEX_OHLC = os.environ.get('API_GEX_OHLC','Unable to retrieve API_GEX_OHLC')
    
    # GET request
    response = requests.get(url=API_GEX_OHLC, headers=headers, stream=True)
    content = response.content.decode("utf-8")
       
    # To pandas df
    df = pd.DataFrame(json.loads(content))
    df.set_index(['Date'], inplace=True)
    df.index = pd.to_datetime(df.index, format='%Y-%m-%dT%H:%M:%S%z', utc=True)
    df.index = pd.to_datetime(df.index.date)
    
    return df

