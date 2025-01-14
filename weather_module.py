import requests
import pandas as pd
from bs4 import BeautifulSoup
import psycopg2
from psycopg2.extras import RealDictCursor
from dotenv import load_dotenv
import os

# Load variables from the .env file
load_dotenv()
# ================ WEB SCRAPING =====================

def fetch_weather_page(url):
    response = requests.get(url)
    if response.status_code == 200:
        return response.text
    else:
        raise Exception(f"Failed to fetch web page. Status code: {response.status_code}")

def parse_weather_data(html_content):
    soup = BeautifulSoup(html_content, 'html.parser')
    forecast_items = soup.find_all('div', class_='tombstone-container')
    weather_data = []
    for item in forecast_items:
        period = item.find('p', class_='period-name').get_text()
        short_desc = item.find('p', class_='short-desc').get_text()
        temp = item.find('p', class_='temp').get_text()
        weather_data.append({'period': period, 'short_desc': short_desc, 'temp': temp})
    return weather_data

# ================ DATABASE CONNECTION =====================
def get_db_connection():
    return psycopg2.connect(
        dbname=os.getenv("DB_NAME"),
        user=os.getenv("DB_USER"),
        password=os.getenv("DB_PASSWORD"),
        host=os.getenv("DB_HOST")
    )

def insert_weather_data(db_connection, weather_data):
    cursor = db_connection.cursor()
    truncate_query = "TRUNCATE TABLE weather_forecasts"
    cursor.execute(truncate_query)
    query = """
    INSERT INTO weather_forecasts (period, short_desc, temperature)
    VALUES (%s, %s, %s);
    """
    for data in weather_data:
        cursor.execute(query, (data['period'], data['short_desc'], data['temp']))
    db_connection.commit()
    cursor.close()

def fetch_data_to_dataframe(connection):
    query = "SELECT * FROM weather_forecasts;"
    return pd.read_sql_query(query, connection)

def save_processed_data(db_connection, dataframe):
    cursor = db_connection.cursor()
    truncate_query = "TRUNCATE TABLE processed_weather_forecasts"
    cursor.execute(truncate_query)
    query = """
    INSERT INTO processed_weather_forecasts (forecast_period, temperature)
    VALUES (%s, %s);
    """
    for _, row in dataframe.iterrows():
        cursor.execute(query, (row['forecast_period'], row['temperature']))
    db_connection.commit()
    cursor.close()

# ================ DATA PROCESSING =====================
def clean_and_transform(dataframe):
    dataframe['temperature'] = dataframe['temperature'].str.extract('(\d+)').astype(int)
    dataframe.rename(columns={'period': 'forecast_period', 'short_desc': 'description'}, inplace=True)
    dataframe.fillna(method='ffill', inplace=True)
    return dataframe

def aggregate_data(dataframe):
    aggregated_df = dataframe.groupby('forecast_period').agg({'temperature': 'mean'}).reset_index()
    aggregated_df['temperature'] = aggregated_df['temperature'].round(1)
    return aggregated_df
