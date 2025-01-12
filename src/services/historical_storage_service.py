import pandas as pd
import matplotlib.pyplot as plt
import asyncio

class HistoricalStorageService:
    def __init__(self):
        self.data = pd.DataFrame()
        self.seasonal_stats = pd.DataFrame()
        self.cities_list = []
    
    async def analyze_data(self):
        data = self.data.copy()
        data['timestamp'] = pd.to_datetime(data['timestamp'])

        data = data.sort_values(['city', 'timestamp'])
        data['rolling_avg_30'] = data.groupby('city')['temperature'].transform(lambda x: x.rolling(window=30, min_periods=1).mean())

        seasonal_stats = data.groupby(['city', 'season'])['temperature'].agg(['mean', 'std']).reset_index()
        seasonal_stats.rename(columns={'mean': 'mean_temp', 'std': 'std_temp'}, inplace=True)

        data = data.merge(seasonal_stats, on=['city', 'season'], how='left')

        data['is_anomaly'] = abs(data['temperature'] - data['mean_temp']) > 2 * data['std_temp']
        
        self.seasonal_stats = seasonal_stats
        self.data = data
        self.cities_list = list(data['city'].unique())
    
    def get_cities_list(self):
        return self.cities_list
        
    def fetch_data(self, data):
        self.data = data

    def plot_data(self, city):
        data = self.data[self.data['city'] == city]
        data['timestamp'] = pd.to_datetime(data['timestamp'])
        data = data.sort_values('timestamp')
        data.set_index('timestamp', inplace=True)
        
        fig, ax = plt.subplots(figsize=(10, 5))
        ax.plot(data['temperature'], label='Temperature')
        ax.plot(data['rolling_avg_30'], label='30-day Rolling Average')
        ax.scatter(data[data['is_anomaly']].index, data[data['is_anomaly']]['temperature'], color='red', label='Anomaly')
        
        ax.set_title(f'Historical temperature in {city}') 
        ax.set_xlabel('Date')
        ax.set_ylabel('Temperature')
        ax.legend()

        return fig
    
    def get_seasonal_stats(self, city):
        return self.seasonal_stats[self.seasonal_stats['city'] == city], self.seasonal_stats
    
    def is_anomaly(self, city, season, temp):
        stat = self.seasonal_stats[(self.seasonal_stats['city'] == city) & (self.seasonal_stats['season'] == season)]
        mean_temp = stat['mean_temp'].values[0]
        std_temp = stat['std_temp'].values[0]
        return abs(temp - mean_temp) > 2 * std_temp
