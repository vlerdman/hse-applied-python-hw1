import pandas as pd
import multiprocessing
from multiprocessing.pool import ThreadPool
import time


def analysis(input_data):
    data = input_data.copy()
    data['timestamp'] = pd.to_datetime(data['timestamp'])

    data = data.sort_values(['city', 'timestamp'])
    data['rolling_avg_30'] = data.groupby('city')['temperature'].transform(lambda x: x.rolling(window=30, min_periods=1).mean())

    seasonal_stats = data.groupby(['city', 'season'])['temperature'].agg(['mean', 'std']).reset_index()
    seasonal_stats.rename(columns={'mean': 'mean_temp', 'std': 'std_temp'}, inplace=True)

    data = data.merge(seasonal_stats, on=['city', 'season'], how='left')

    data['is_anomaly'] = abs(data['temperature'] - data['mean_temp']) > 2 * data['std_temp']

    return data

def parallel_multithreading_analysis(data):
    data_split = [group for _, group in data.groupby('city')]
    with ThreadPool() as pool:
        result = pool.map(analysis, data_split)
    return pd.concat(result)

def parallel_multiprocessing_analysis(data):
    data_split = [group for _, group in data.groupby('city')]
    with multiprocessing.Pool() as pool:
        result = pool.map(analysis, data_split)
    return pd.concat(result)

if __name__ == '__main__':
    data = pd.read_csv('data/temperature_data.csv')

    start = time.time()
    result = analysis(data)
    end = time.time()
    print(f'Sequential Execution Time: {end - start}')

    start = time.time()
    result = parallel_multithreading_analysis(data)
    end = time.time()
    print(f'MultiThreading Parallel Execution Time: {end - start}')

    start = time.time()
    result = parallel_multiprocessing_analysis(data)
    end = time.time()
    print(f'MultiProcessing Parallel Execution Time: {end - start}')