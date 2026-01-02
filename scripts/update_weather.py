#!/usr/bin/env python3
"""
update_weather.py - Daily Weather Data Updates
Fetches recent weather data in small batches to avoid rate limits
Run this daily/hourly to keep your data current
"""

import requests
import sqlite3
import json
from datetime import datetime, timedelta
import time
import sys
import os


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
                
                -- Additional fields
                battout INTEGER,
                battin INTEGER,
                
                -- Raw JSON for any additional fields
                raw_json TEXT
            )
        ''')
        
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
            return False
        except Exception as e:
            print(f"Error inserting data: {e}")
            return False
    
    def get_most_recent_date(self):
        """Get the most recent data timestamp in the database"""
        cursor = self.conn.cursor()
        cursor.execute("SELECT MAX(dateutc), MAX(date) FROM weather_data")
        result = cursor.fetchone()
        
        if result[0]:
            return {
                'timestamp': result[0],
                'date': result[1],
                'datetime': datetime.fromtimestamp(result[0] / 1000)
            }
        return None
    
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
        
        try:
            response = requests.get(url, params=params)
            response.raise_for_status()
            return response.json()
        except requests.exceptions.HTTPError as e:
            print(f"\nHTTP Error Details:")
            print(f"  Status Code: {response.status_code}")
            print(f"  Response: {response.text}")
            raise
    
    def get_recent_data(self, mac_address, limit=10):
        """
        Get recent device data
        limit: number of records to fetch (default: 10)
        """
        url = f"{self.base_url}/devices/{mac_address}"
        params = {
            'apiKey': self.api_key,
            'applicationKey': self.application_key,
            'limit': limit
        }
        
        try:
            response = requests.get(url, params=params)
            
            if response.status_code == 429:
                print("  ⚠️  Rate limit hit!")
                return None
            
            response.raise_for_status()
            return response.json()
        except Exception as e:
            print(f"  Error: {e}")
            return None


def update_recent_data(records_per_batch=10, delay_seconds=3, max_requests=20):
    """
    Fetch recent weather data and update the database
    
    Args:
        records_per_batch: How many records to fetch per API call (default: 10)
        delay_seconds: Seconds to wait between API calls (default: 3)
        max_requests: Maximum number of API requests to make (default: 20)
    """
    # Get API credentials
    API_KEY = os.getenv("AMBIENT_API_KEY")
    APPLICATION_KEY = os.getenv("AMBIENT_APP_KEY")
    
    if not API_KEY or not APPLICATION_KEY:
        print("=" * 60)
        print("ERROR: API credentials not found!")
        print("=" * 60)
        print("\nSet environment variables first:")
        print('  $env:AMBIENT_API_KEY="your_api_key"')
        print('  $env:AMBIENT_APP_KEY="your_application_key"')
        sys.exit(1)
    
    print("=" * 60)
    print("Weather Update - Recent Data Fetch")
    print("=" * 60)
    print(f"Configuration:")
    print(f"  Records per batch: {records_per_batch}")
    print(f"  Delay between requests: {delay_seconds}s")
    print(f"  Max requests: {max_requests}")
    print()
    
    # Initialize
    db = AmbientWeatherDB()
    api = AmbientWeatherAPI(API_KEY, APPLICATION_KEY)
    
    # Get device
    print("Fetching devices...")
    try:
        devices = api.get_devices()
    except Exception as e:
        print(f"Failed to fetch devices: {e}")
        db.close()
        sys.exit(1)
    
    if not devices:
        print("No devices found!")
        db.close()
        return
    
    device = devices[0]
    mac_address = device['macAddress']
    print(f"Using device: {device['info']['name']} ({mac_address})")
    
    # Check existing data
    most_recent = db.get_most_recent_date()
    
    if most_recent:
        print(f"\nMost recent data in database:")
        print(f"  Date: {most_recent['date']}")
        print(f"  ({most_recent['datetime'].strftime('%Y-%m-%d %I:%M %p')})")
    else:
        print("\nNo existing data in database")
        print("Fetching last 48 hours of data...")
    
    print(f"\nFetching recent data...")
    print("-" * 60)
    
    total_inserted = 0
    total_skipped = 0
    requests_made = 0
    
    # Fetch data in small batches
    for i in range(max_requests):
        requests_made += 1
        print(f"\nRequest {requests_made}/{max_requests}: Fetching {records_per_batch} records...")
        
        data = api.get_recent_data(mac_address, limit=records_per_batch)
        
        if data is None:
            print("  Rate limit hit or error occurred. Stopping.")
            break
        
        if not data:
            print("  No data returned")
            break
        
        print(f"  Received {len(data)} records")
        
        # Insert data
        inserted = 0
        skipped = 0
        
        for record in data:
            if db.insert_data(record):
                inserted += 1
            else:
                skipped += 1
        
        total_inserted += inserted
        total_skipped += skipped
        
        print(f"  Inserted: {inserted} new, Skipped: {skipped} duplicates")
        
        # If we got all duplicates, we're caught up
        if inserted == 0 and skipped > 0:
            print("\n✅ All caught up! No new data available.")
            break
        
        # If we got fewer records than requested, we've reached the end
        if len(data) < records_per_batch:
            print("\n✅ Reached end of available data")
            break
        
        # Wait before next request (except on last iteration)
        if i < max_requests - 1:
            print(f"  Waiting {delay_seconds}s before next request...")
            time.sleep(delay_seconds)
    
    # Final stats
    print("\n" + "=" * 60)
    print("Update Complete!")
    print("=" * 60)
    print(f"Requests made: {requests_made}")
    print(f"New records inserted: {total_inserted}")
    print(f"Duplicate records skipped: {total_skipped}")
    
    stats = db.get_stats()
    if stats['count'] > 0:
        print(f"\nDatabase totals:")
        print(f"  Total records: {stats['count']}")
        print(f"  Date range: {stats['min_date']} to {stats['max_date']}")
    
    db.close()


if __name__ == "__main__":
    import argparse
    
    parser = argparse.ArgumentParser(description='Update weather data with recent records')
    parser.add_argument('--records-per-batch', type=int, default=10,
                      help='Records to fetch per API call (default: 10)')
    parser.add_argument('--delay', type=int, default=3,
                      help='Seconds between requests (default: 3)')
    parser.add_argument('--max-requests', type=int, default=20,
                      help='Maximum API requests to make (default: 20)')
    
    args = parser.parse_args()
    
    update_recent_data(
        records_per_batch=args.records_per_batch,
        delay_seconds=args.delay,
        max_requests=args.max_requests
    )
