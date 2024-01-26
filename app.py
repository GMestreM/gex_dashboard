import os
import numpy as np 
import pandas as pd  
import streamlit as st 

from api_data import (
    fetch_execution_info,
    fetch_zero_gamma,
    fetch_gex_profile,
    fetch_gex_levels,
    fetch_ohlc_data,
)

from plots import (
    plotly_gex_strike_bars,
    plotly_gex_profile,
    plotly_candlestick_gex,
)


# Page configuration
# https://docs.streamlit.io/library/api-reference/utilities/st.set_page_config
st.set_page_config(
    page_title="SPX Gamma Exposure",
    page_icon="📖",
    layout="wide",
    initial_sidebar_state='expanded',
    menu_items={
        'About': f"""
            # Gamma Exposure for S&P 500
            
            [More info](https://www.meff.es/docs/newsletter/2022/Newsletter_MEFF-Marzo2022.pdf)
        """
    }
)

# Define data retrieval function
@st.cache_data
def get_data():
    execution_info = fetch_execution_info()
    zero_gamma = fetch_zero_gamma()
    dict_gex_profile = fetch_gex_profile()
    dict_gex_levels = fetch_gex_levels()
    ohlc = fetch_ohlc_data()
    
    return execution_info, zero_gamma, dict_gex_profile, dict_gex_levels, ohlc


# Retrieve data
with st.spinner(text='Loading data...'):
    execution_info, zero_gamma, dict_gex_profile, dict_gex_levels, ohlc = get_data()
    
    # FIXME
    # If market is open, drop it
    ohlc = ohlc.loc[ohlc['Open'] != 0,:]
    
# FIXME
# Include a calendar to select the displayed date
def get_mongoid_by_date(execution_info, selected_date):
    execution_info['delayed_timestamp'] = pd.to_datetime(pd.to_datetime(execution_info['delayed_timestamp']).dt.date)
    sel_execution_info = execution_info.loc[execution_info['delayed_timestamp'] == pd.to_datetime(selected_date),:]
    
    sel_mongodb_id = sel_execution_info['mongodb_id'].item()
    
    return sel_mongodb_id
    
selected_date = None
if selected_date is None:
    selected_date = execution_info['delayed_timestamp'].max()

last_date_delayed = selected_date #execution_info['delayed_timestamp'].max()
last_execution_info = execution_info.loc[execution_info['delayed_timestamp'] == last_date_delayed,:]
last_mongodb_id = last_execution_info['mongodb_id'].item()
last_close_date = pd.to_datetime(last_execution_info['delayed_timestamp'].item())
last_close_date = pd.to_datetime(last_close_date.date())

first_close_date = pd.to_datetime(pd.to_datetime(execution_info['delayed_timestamp']).dt.date).min()

# Display gamma exposure
col1, col2 = st.columns([1,1])
with col2:
    selected_date = st.date_input(
        label='GEX Date',
        min_value=first_close_date,
        max_value=last_close_date,
        value=last_close_date,
    )
    
with col1:
    st.markdown(f"""
                # SPX Gamma exposure ({pd.to_datetime(selected_date):%Y-%m-%d})
                """)

sel_mongodb_id = get_mongoid_by_date(execution_info, selected_date)


spot_price = ohlc.loc[pd.to_datetime(selected_date), 'Close']

gex_profile = pd.DataFrame(dict_gex_profile[sel_mongodb_id])
gex_profile.rename(columns={
    'strike':'Strikes',
    'index':'Strikes',
    'Gamma Profile All':'Gamma Exposure',
    'Gamma Profile (Ex Next)':'Gamma Exposure ExNext Expiry',
    'Gamma Profile (Ex Next Monthly)':'Gamma Exposure ExNext Friday',
}, inplace=True)
gex_levels = pd.DataFrame(dict_gex_levels[sel_mongodb_id])
gex_levels.rename(columns={
    'index':'Strikes',
    'strike':'Strikes',
    'Total Gamma Call':'Gamma Exposure Calls',
    'Total Gamma Put':'Gamma Exposure Puts',
}, inplace=True)

zero_gamma.index = pd.to_datetime(pd.to_datetime(zero_gamma.index).date)
zero_gamma_last = zero_gamma.loc[pd.to_datetime(selected_date), 'Zero Gamma']
    
# Figures
with st.spinner(text='In progress'):
    col1, col2 = st.columns([1,1])
    with col1:
        st.plotly_chart(
            figure_or_data=plotly_gex_strike_bars(
                gex_levels, 
                spot_price=spot_price),
            use_container_width=True)
    with col2:
        st.plotly_chart(
            figure_or_data=plotly_gex_profile(
                gex_profile, 
                spot_price=spot_price),
            use_container_width=True)
        
# Candlestick plot 
with st.spinner(text='In progress'):   
    st.plotly_chart(
        figure_or_data=plotly_candlestick_gex(
            ohlc.iloc[-252:,:], 
            historic_gex=zero_gamma),
        use_container_width=True)

# Display data tables
with st.expander(label='Show data', expanded=False):
    st.markdown('# Data retrieved')

    col1, col2, col3 = st.columns([1.5,1,1])
    with col1:
        st.dataframe(ohlc.iloc[::-1,:], use_container_width=False)
    with col2:
        st.dataframe(gex_levels.iloc[:,:4], use_container_width=False, hide_index=True)
    with col3:
        st.dataframe(gex_profile, use_container_width=False, hide_index=True)