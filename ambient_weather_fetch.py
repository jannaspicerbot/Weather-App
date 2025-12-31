#!/usr/bin/env python3
"""
Ambient Weather Data Fetcher
Fetches data from Ambient Weather API and stores in SQLite database
"""

import requests
import sqlite3
import json
from datetime import datetime, timedelta
import time
import sys


class AmbientWeatherDB:
    def __init__(self, db_path='ambient_weather.db'):
        self.db_path = db_path
        self.conn = sqlite3.connect(db_path)
        self.create_tables()
    
    def create_tables(self):
        cursor = self.conn.cursor()
        
        # Main weather data table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS weather_data (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                dateutc INTEGER UNIQUE,
                date TEXT,
                
                -- Temperature
                tempf REAL,
                feelsLike REAL,
                dewPoint REAL,
                tempinf REAL,
                
                -- Humidity
                humidity INTEGER,
                humidityin INTEGER,
                
                -- Pressure
                baromrelin REAL,
                baromabsin REAL,
                
                -- Wind
                windspeedmph REAL,
                windgustmph REAL,
                winddir INTEGER,
                maxdailygust REAL,
                
                -- Rain
                hourlyrainin REAL,
                dailyrainin REAL,
                weeklyrainin REAL,
                monthlyrainin REAL,
                totalrainin REAL,
                
                -- Solar
                solarradiation REAL,
                uv INTEGER,
                
                -- Additional fields (vary by device)
                battout INTEGER,
                battin INTEGER,
                
                -- Raw JSON for any additional fields
                raw_json TEXT
            )
        ''')
        
        # Index on date for faster queries
        cursor.execute('''
            CREATE INDEX IF NOT EXISTS idx_dateutc ON weather_data(dateutc)
        ''')
        
        self.conn.commit()
    
    def insert_data(self, data_point):
        cursor = self.conn.cursor()
        
        try:
            cursor.execute('''
                INSERT OR REPLACE INTO weather_data (
                    dateutc, date, tempf, feelsLike, dewPoint, tempinf,
                    humidity, humidityin, baromrelin, baromabsin,
                    windspeedmph, windgustmph, winddir, maxdailygust,
                    hourlyrainin, dailyrainin, weeklyrainin, monthlyrainin, totalrainin,
                    solarradiation, uv, battout, battin, raw_json
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            ''', (
                data_point.get('dateutc'),
                data_point.get('date'),
                data_point.get('tempf'),
                data_point.get('feelsLike'),
                data_point.get('dewPoint'),
                data_point.get('tempinf'),
                data_point.get('humidity'),
                data_point.get('humidityin'),
                data_point.get('baromrelin'),
                data_point.get('baromabsin'),
                data_point.get('windspeedmph'),
                data_point.get('windgustmph'),
                data_point.get('winddir'),
                data_point.get('maxdailygust'),
                data_point.get('hourlyrainin'),
                data_point.get('dailyrainin'),
                data_point.get('weeklyrainin'),
                data_point.get('monthlyrainin'),
                data_point.get('totalrainin'),
                data_point.get('solarradiation'),
                data_point.get('uv'),
                data_point.get('battout'),
                data_point.get('battin'),
                json.dumps(data_point)
            ))
            self.conn.commit()
            return True
        except sqlite3.IntegrityError:
            # Data point already exists
            return False
        except Exception as e:
            print(f"Error inserting data: {e}")
            return False
    
    def get_data(self, start_date=None, end_date=None, limit=None):
        cursor = self.conn.cursor()
        
        query = "SELECT * FROM weather_data"
        params = []
        
        if start_date or end_date:
            query += " WHERE"
            if start_date:
                query += " dateutc >= ?"
                params.append(int(start_date.timestamp() * 1000))
            if end_date:
                if start_date:
                    query += " AND"
                query += " dateutc <= ?"
                params.append(int(end_date.timestamp() * 1000))
        
        query += " ORDER BY dateutc ASC"
        
        if limit:
            query += f" LIMIT {limit}"
        
        cursor.execute(query, params)
        columns = [description[0] for description in cursor.description]
        rows = cursor.fetchall()
        
        return [dict(zip(columns, row)) for row in rows]
    
    def get_stats(self):
        """Get database statistics"""
        cursor = self.conn.cursor()
        cursor.execute("SELECT COUNT(*) FROM weather_data")
        count = cursor.fetchone()[0]
        
        if count > 0:
            cursor.execute("SELECT MIN(date), MAX(date) FROM weather_data")
            min_date, max_date = cursor.fetchone()
            return {
                'count': count,
                'min_date': min_date,
                'max_date': max_date
            }
        return {'count': 0}
    
    def close(self):
        self.conn.close()


class AmbientWeatherAPI:
    def __init__(self, api_key, application_key):
        self.api_key = api_key
        self.application_key = application_key
        self.base_url = "https://api.ambientweather.net/v1"
    
    def get_devices(self):
        """Get list of user's devices"""
        url = f"{self.base_url}/devices"
        params = {
            'apiKey': self.api_key,
            'applicationKey': self.application_key
        }
        
        response = requests.get(url, params=params)
        response.raise_for_status()
        return response.json()
    
    def get_device_data(self, mac_address, end_date=None, limit=288):
        """
        Get device data
        limit: number of records to fetch (288 = 1 day at 5-minute intervals)
        end_date: datetime object for the end date
        """
        url = f"{self.base_url}/devices/{mac_address}"
        params = {
            'apiKey': self.api_key,
            'applicationKey': self.application_key,
            'limit': limit
        }
        
        if end_date:
            params['endDate'] = int(end_date.timestamp() * 1000)
        
        response = requests.get(url, params=params)
        response.raise_for_status()
        return response.json()
    
    def fetch_all_historical_data(self, mac_address, start_date, db):
        """
        Fetch all historical data from start_date to now
        API has rate limits, so we need to be careful
        """
        current_end = datetime.now()
        records_per_call = 288  # Max per API call
        total_inserted = 0
        
        print(f"Fetching data from {start_date} to {current_end}")
        
        while current_end > start_date:
            print(f"Fetching batch ending at {current_end.strftime('%Y-%m-%d %H:%M:%S')}")
            
            try:
                data = self.get_device_data(mac_address, current_end, records_per_call)
                
                if not data:
                    print("No more data available")
                    break
                
                # Insert data into database
                inserted = 0
                for record in data:
                    if db.insert_data(record):
                        inserted += 1
                
                total_inserted += inserted
                print(f"  Inserted {inserted} new records (total: {total_inserted})")
                
                # Get the oldest timestamp from this batch
                oldest_timestamp = min(record['dateutc'] for record in data)
                current_end = datetime.fromtimestamp(oldest_timestamp / 1000)
                
                # If we got fewer records than requested, we've reached the end
                if len(data) < records_per_call:
                    print("Reached the beginning of available data")
                    break
                
                # Respect API rate limits (1 call per second)
                time.sleep(1)
                
            except Exception as e:
                print(f"Error fetching data: {e}")
                break
        
        print(f"\nTotal records inserted: {total_inserted}")
        return total_inserted


def main():
    # Configuration
    API_KEY = "YOUR_API_KEY_HERE"
    APPLICATION_KEY = "YOUR_APPLICATION_KEY_HERE"
    
    if API_KEY == "YOUR_API_KEY_HERE" or APPLICATION_KEY == "YOUR_APPLICATION_KEY_HERE":
        print("ERROR: Please edit this file and add your API credentials")
        print("Get your keys from: https://ambientweather.net/account")
        sys.exit(1)
    
    # Initialize database
    print("Initializing database...")
    db = AmbientWeatherDB('ambient_weather.db')
    
    # Initialize API
    api = AmbientWeatherAPI(API_KEY, APPLICATION_KEY)
    
    # Get your devices
    print("\nFetching devices...")
    try:
        devices = api.get_devices()
    except Exception as e:
        print(f"ERROR: Failed to fetch devices: {e}")
        print("Please check your API credentials")
        sys.exit(1)
    
    if not devices:
        print("No devices found")
        return
    
    print(f"Found {len(devices)} device(s):")
    for i, device in enumerate(devices):
        print(f"  {i+1}. {device['info']['name']} (MAC: {device['macAddress']})")
    
    # Use the first device (or you can select which one)
    device = devices[0]
    mac_address = device['macAddress']
    
    print(f"\nUsing device: {device['info']['name']}")
    
    # Check existing data
    stats = db.get_stats()
    if stats['count'] > 0:
        print(f"\nExisting data in database:")
        print(f"  Records: {stats['count']}")
        print(f"  Date range: {stats['min_date']} to {stats['max_date']}")
        print("\nFetching new data since last update...")
        start_date = datetime.fromisoformat(stats['max_date'])
    else:
        # Fetch historical data starting from March 2024
        start_date = datetime(2024, 3, 1)
        print(f"\nNo existing data. Fetching all historical data since {start_date}")
    
    api.fetch_all_historical_data(mac_address, start_date, db)
    
    # Show final statistics
    stats = db.get_stats()
    print("\n" + "="*50)
    print("Data fetching complete!")
    print("="*50)
    print(f"Total records in database: {stats['count']}")
    if stats['count'] > 0:
        print(f"Date range: {stats['min_date']} to {stats['max_date']}")
    
    db.close()


if __name__ == "__main__":
    main()
