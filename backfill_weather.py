#!/usr/bin/env python3
"""
backfill_weather.py - Historical Weather Data Backfill
Slowly fetches historical data to avoid rate limits
Designed to run overnight or during low-usage times
Can be paused and resumed
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
        
        # Backfill progress tracking table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS backfill_progress (
                id INTEGER PRIMARY KEY CHECK (id = 1),
                target_start_date TEXT,
                current_position_date TEXT,
                last_run_timestamp TEXT,
                total_records_fetched INTEGER DEFAULT 0,
                total_requests_made INTEGER DEFAULT 0,
                status TEXT DEFAULT 'not_started',
                last_error TEXT
            )
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
    
    def get_oldest_date(self):
        """Get the oldest data timestamp in the database"""
        cursor = self.conn.cursor()
        cursor.execute("SELECT MIN(dateutc), MIN(date) FROM weather_data")
        result = cursor.fetchone()
        
        if result[0]:
            return {
                'timestamp': result[0],
                'date': result[1],
                'datetime': datetime.fromtimestamp(result[0] / 1000)
            }
        return None
    
    def get_backfill_progress(self):
        """Get current backfill progress"""
        cursor = self.conn.cursor()
        cursor.execute("SELECT * FROM backfill_progress WHERE id = 1")
        row = cursor.fetchone()
        
        if row:
            return {
                'target_start_date': row[1],
                'current_position_date': row[2],
                'last_run_timestamp': row[3],
                'total_records_fetched': row[4],
                'total_requests_made': row[5],
                'status': row[6],
                'last_error': row[7]
            }
        return None
    
    def init_backfill_progress(self, target_start_date):
        """Initialize backfill progress"""
        cursor = self.conn.cursor()
        
        oldest = self.get_oldest_date()
        current_position = oldest['date'] if oldest else datetime.now().isoformat()
        
        cursor.execute('''
            INSERT OR REPLACE INTO backfill_progress 
            (id, target_start_date, current_position_date, last_run_timestamp, status)
            VALUES (1, ?, ?, ?, 'in_progress')
        ''', (target_start_date, current_position, datetime.now().isoformat()))
        
        self.conn.commit()
    
    def update_backfill_progress(self, current_position, records_fetched, requests_made, status='in_progress', error=None):
        """Update backfill progress"""
        cursor = self.conn.cursor()
        
        cursor.execute('''
            UPDATE backfill_progress 
            SET current_position_date = ?,
                last_run_timestamp = ?,
                total_records_fetched = total_records_fetched + ?,
                total_requests_made = total_requests_made + ?,
                status = ?,
                last_error = ?
            WHERE id = 1
        ''', (current_position, datetime.now().isoformat(), records_fetched, requests_made, status, error))
        
        self.conn.commit()
    
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
    
    def get_historical_data(self, mac_address, end_date, limit=5):
        """
        Get historical device data ending at a specific date
        limit: number of records to fetch (default: 5 for conservative backfill)
        end_date: datetime object for the end date
        """
        url = f"{self.base_url}/devices/{mac_address}"
        params = {
            'apiKey': self.api_key,
            'applicationKey': self.application_key,
            'limit': limit,
            'endDate': int(end_date.timestamp() * 1000)
        }
        
        try:
            response = requests.get(url, params=params)
            
            if response.status_code == 429:
                return {'error': 'rate_limit', 'data': None}
            
            response.raise_for_status()
            return {'error': None, 'data': response.json()}
        except Exception as e:
            return {'error': str(e), 'data': None}


def backfill_historical_data(
    start_date_str='2024-03-13',
    records_per_batch=5,
    delay_seconds=10,
    max_requests=500,
    resume=True
):
    """
    Backfill historical weather data
    
    Args:
        start_date_str: Target start date (YYYY-MM-DD format)
        records_per_batch: Records per API call (default: 5, conservative)
        delay_seconds: Seconds between requests (default: 10)
        max_requests: Max requests per run (default: 500)
        resume: Resume from last position if True (default: True)
    """
    # Get API credentials
    API_KEY = os.getenv("AMBIENT_API_KEY")
    APPLICATION_KEY = os.getenv("AMBIENT_APP_KEY")
    
    if not API_KEY or not APPLICATION_KEY:
        print("=" * 70)
        print("ERROR: API credentials not found!")
        print("=" * 70)
        print("\nSet environment variables first:")
        print('  $env:AMBIENT_API_KEY="your_api_key"')
        print('  $env:AMBIENT_APP_KEY="your_application_key"')
        sys.exit(1)
    
    print("=" * 70)
    print("Weather Backfill - Historical Data Collection")
    print("=" * 70)
    print(f"Configuration:")
    print(f"  Target start date: {start_date_str}")
    print(f"  Records per batch: {records_per_batch}")
    print(f"  Delay between requests: {delay_seconds}s")
    print(f"  Max requests this run: {max_requests}")
    print(f"  Resume from last position: {resume}")
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
    
    # Initialize or resume backfill
    target_start = datetime.strptime(start_date_str, '%Y-%m-%d')
    
    progress = db.get_backfill_progress()
    
    if not progress or not resume:
        print("\nInitializing new backfill...")
        db.init_backfill_progress(start_date_str)
        progress = db.get_backfill_progress()
    
    current_position = datetime.fromisoformat(progress['current_position_date'])
    
    print(f"\nBackfill Status:")
    print(f"  Target start: {start_date_str}")
    print(f"  Current position: {progress['current_position_date']}")
    print(f"  Records fetched so far: {progress['total_records_fetched']}")
    print(f"  Total requests made: {progress['total_requests_made']}")
    print(f"  Status: {progress['status']}")
    
    if current_position <= target_start:
        print(f"\n✅ Backfill already complete!")
        print(f"  Reached target date: {start_date_str}")
        db.update_backfill_progress(
            progress['current_position_date'],
            0, 0,
            status='complete'
        )
        db.close()
        return
    
    days_remaining = (current_position - target_start).days
    print(f"\n📊 Progress:")
    print(f"  Days remaining: {days_remaining}")
    print(f"  Estimated requests needed: ~{days_remaining * 288 // records_per_batch}")
    
    print(f"\nStarting backfill...")
    print("-" * 70)
    
    total_inserted = 0
    total_skipped = 0
    requests_made = 0
    
    # Fetch data working backwards
    current_end = current_position
    
    for i in range(max_requests):
        requests_made += 1
        
        print(f"\n[{requests_made}/{max_requests}] Fetching batch ending at {current_end.strftime('%Y-%m-%d %H:%M')}")
        
        result = api.get_historical_data(mac_address, current_end, limit=records_per_batch)
        
        if result['error'] == 'rate_limit':
            print("  ⚠️  RATE LIMIT HIT!")
            print("  Stopping and saving progress...")
            db.update_backfill_progress(
                current_end.isoformat(),
                total_inserted,
                requests_made,
                status='paused',
                error='Rate limit hit'
            )
            print("\n" + "=" * 70)
            print("❌ Backfill paused due to rate limit")
            print("=" * 70)
            print(f"  Inserted {total_inserted} records before stopping")
            print(f"  Current position saved: {current_end.isoformat()}")
            print(f"  Wait 1 hour and run again to resume")
            db.close()
            return
        
        if result['error']:
            print(f"  ❌ Error: {result['error']}")
            db.update_backfill_progress(
                current_end.isoformat(),
                total_inserted,
                requests_made,
                status='error',
                error=result['error']
            )
            db.close()
            return
        
        data = result['data']
        
        if not data:
            print("  No data returned (might have reached device start date)")
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
        
        # Update position to oldest record in this batch
        if data:
            oldest_in_batch = min(record['dateutc'] for record in data)
            current_end = datetime.fromtimestamp(oldest_in_batch / 1000)
            
            print(f"  New position: {current_end.strftime('%Y-%m-%d %H:%M')}")
            
            # Check if we've reached our target
            if current_end <= target_start:
                print(f"\n✅ Reached target start date: {start_date_str}")
                db.update_backfill_progress(
                    current_end.isoformat(),
                    total_inserted,
                    requests_made,
                    status='complete'
                )
                break
        
        # Save progress every 10 requests
        if requests_made % 10 == 0:
            db.update_backfill_progress(
                current_end.isoformat(),
                total_inserted,
                requests_made,
                status='in_progress'
            )
            print(f"  💾 Progress saved (checkpoint)")
        
        # If we got fewer records than requested, might be reaching the end
        if len(data) < records_per_batch:
            print("  ⚠️  Received fewer records than requested")
        
        # Wait before next request
        if i < max_requests - 1:
            print(f"  ⏳ Waiting {delay_seconds}s...")
            time.sleep(delay_seconds)
    
    # Final progress save
    db.update_backfill_progress(
        current_end.isoformat(),
        total_inserted,
        requests_made,
        status='in_progress' if current_end > target_start else 'complete'
    )
    
    # Final stats
    print("\n" + "=" * 70)
    print("Backfill Run Complete!")
    print("=" * 70)
    print(f"Requests made this run: {requests_made}")
    print(f"New records inserted: {total_inserted}")
    print(f"Duplicate records skipped: {total_skipped}")
    
    stats = db.get_stats()
    if stats['count'] > 0:
        print(f"\nDatabase totals:")
        print(f"  Total records: {stats['count']}")
        print(f"  Date range: {stats['min_date']} to {stats['max_date']}")
    
    progress = db.get_backfill_progress()
    if progress['status'] == 'complete':
        print(f"\n🎉 BACKFILL COMPLETE!")
        print(f"  Reached target: {start_date_str}")
    else:
        current_pos = datetime.fromisoformat(progress['current_position_date'])
        days_left = (current_pos - target_start).days
        print(f"\n📊 Backfill in progress:")
        print(f"  Current position: {progress['current_position_date']}")
        print(f"  Days remaining: {days_left}")
        print(f"  Run again to continue")
    
    db.close()


if __name__ == "__main__":
    import argparse
    
    parser = argparse.ArgumentParser(description='Backfill historical weather data')
    parser.add_argument('--start-date', type=str, default='2024-03-13',
                      help='Target start date (YYYY-MM-DD, default: 2024-03-13)')
    parser.add_argument('--records-per-batch', type=int, default=5,
                      help='Records per API call (default: 5)')
    parser.add_argument('--delay', type=int, default=10,
                      help='Seconds between requests (default: 10)')
    parser.add_argument('--max-requests', type=int, default=500,
                      help='Maximum requests per run (default: 500)')
    parser.add_argument('--no-resume', action='store_true',
                      help='Start fresh instead of resuming')
    
    args = parser.parse_args()
    
    backfill_historical_data(
        start_date_str=args.start_date,
        records_per_batch=args.records_per_batch,
        delay_seconds=args.delay,
        max_requests=args.max_requests,
        resume=not args.no_resume
    )
