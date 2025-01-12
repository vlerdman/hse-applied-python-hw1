import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
import asyncio

from src.core.logger import CustomizeLogger
from src.services.weather_service import WeatherService
from src.services.historical_storage_service import HistoricalStorageService

async def main():
    st.title('Historical Weather Analyser')

    if 'historical_storage_service' not in st.session_state:
        st.session_state.historical_storage_service = HistoricalStorageService()
    
    if 'weather_service' not in st.session_state: 
        st.session_state.weather_service = WeatherService()

    if 'city' not in st.session_state: 
        st.session_state.city = None

    historical_weather = st.file_uploader('Historical Weather Data', type=['csv'])  
    if historical_weather is not None:
        historical_data = pd.read_csv(historical_weather)
        st.session_state.historical_storage_service.fetch_data(historical_data)
        await st.session_state.historical_storage_service.analyze_data()  
        
        city = st.selectbox('City for analysis', st.session_state.historical_storage_service.get_cities_list())
        api_key = st.text_input('Weather API key')
        
        if st.button('Get Weather Statistics'):
            st.session_state.city = city
        if st.session_state.city is not None:
            st.write(f'Data for {st.session_state.city}')
            
            fig = st.session_state.historical_storage_service.plot_data(st.session_state.city)
            st.pyplot(fig)
            seasonal_stats, all_cities_stats = st.session_state.historical_storage_service.get_seasonal_stats(st.session_state.city)
            st.dataframe(seasonal_stats, hide_index=True)

            st.write(f'Data for all cities')

            st.dataframe(all_cities_stats.style.
            highlight_max(subset = ['mean_temp', 'std_temp'], axis=0, color='red').
            highlight_min(subset = ['mean_temp', 'std_temp'], axis=0, color='blue'), hide_index=True)

        if st.button('Get Current Weather'):
           await st.session_state.weather_service.fetch_weather(city, api_key)
        
        status_code, current_weather, current_city = st.session_state.weather_service.get_weather()
        if status_code == 200:
            current_season = st.session_state.weather_service.get_season()
            is_anomaly = st.session_state.historical_storage_service.is_anomaly(current_city, current_season, current_weather)
            if is_anomaly:
                st.write(f'The current temperature in {current_city} is {current_weather}°C. It is anomal temperature')
            else:
                st.write(f'The current temperature in {current_city} is {current_weather}°C. It is not anomal temperature')
        elif not (current_weather is None):
            st.write(current_weather)

if __name__ == '__main__':
    logger = CustomizeLogger.make_logger("streamlit-app")
    asyncio.run(main())