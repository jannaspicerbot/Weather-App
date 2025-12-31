#!/usr/bin/env python3
"""
Ambient Weather Data Visualizer
Creates interactive charts from stored weather data
"""

import sqlite3
import pandas as pd
import plotly.graph_objects as go
from plotly.subplots import make_subplots
from datetime import datetime, timedelta
import sys


class WeatherVisualizer:
    def __init__(self, db_path='ambient_weather.db'):
        self.db_path = db_path
        try:
            self.conn = sqlite3.connect(db_path)
        except Exception as e:
            print(f"ERROR: Could not open database: {e}")
            sys.exit(1)
        self.df = None
    
    def load_data(self, start_date=None, end_date=None):
        """Load data from database into pandas DataFrame"""
        query = "SELECT * FROM weather_data"
        params = []
        
        if start_date or end_date:
            query += " WHERE"
            if start_date:
                query += " date >= ?"
                params.append(start_date.strftime('%Y-%m-%d'))
            if end_date:
                if start_date:
                    query += " AND"
                query += " date <= ?"
                params.append(end_date.strftime('%Y-%m-%d'))
        
        query += " ORDER BY dateutc ASC"
        
        self.df = pd.read_sql_query(query, self.conn, params=params)
        
        if len(self.df) == 0:
            return None
            
        self.df['datetime'] = pd.to_datetime(self.df['dateutc'], unit='ms')
        return self.df
    
    def create_temperature_plot(self):
        """Create temperature plot similar to AWN interface"""
        fig = go.Figure()
        
        # Add shaded area for feels like range
        fig.add_trace(go.Scatter(
            x=self.df['datetime'],
            y=self.df['feelsLike'],
            name='Feels Like',
            line=dict(color='rgba(173, 216, 230, 0.5)', width=1),
            fillcolor='rgba(173, 216, 230, 0.2)',
            fill='tonexty',
            mode='lines'
        ))
        
        # Outdoor temperature
        fig.add_trace(go.Scatter(
            x=self.df['datetime'],
            y=self.df['tempf'],
            name='Outdoor Temp',
            line=dict(color='rgb(0, 123, 255)', width=2),
            mode='lines'
        ))
        
        # Dew point
        fig.add_trace(go.Scatter(
            x=self.df['datetime'],
            y=self.df['dewPoint'],
            name='Dew Point',
            line=dict(color='rgb(0, 200, 150)', width=2),
            mode='lines'
        ))
        
        fig.update_layout(
            title='Temperature Over Time',
            xaxis_title='Date',
            yaxis_title='Temperature (°F)',
            hovermode='x unified',
            template='plotly_white',
            height=500,
            showlegend=True
        )
        
        return fig
    
    def create_wind_plot(self):
        """Create wind speed and direction plot"""
        fig = make_subplots(
            rows=2, cols=1,
            subplot_titles=('Wind Speed', 'Wind Direction'),
            vertical_spacing=0.15,
            row_heights=[0.6, 0.4]
        )
        
        # Wind gusts (background)
        fig.add_trace(go.Scatter(
            x=self.df['datetime'],
            y=self.df['windgustmph'],
            name='Wind Gust',
            line=dict(color='lightgray', width=0),
            fill='tozeroy',
            fillcolor='rgba(200, 200, 200, 0.3)',
            mode='lines'
        ), row=1, col=1)
        
        # Wind speed average
        fig.add_trace(go.Scatter(
            x=self.df['datetime'],
            y=self.df['windspeedmph'],
            name='Wind Speed',
            line=dict(color='rgb(0, 123, 255)', width=2),
            mode='lines'
        ), row=1, col=1)
        
        # Wind direction
        fig.add_trace(go.Scatter(
            x=self.df['datetime'],
            y=self.df['winddir'],
            name='Wind Direction',
            mode='markers',
            marker=dict(color='rgb(0, 123, 255)', size=3),
            showlegend=False
        ), row=2, col=1)
        
        fig.update_yaxes(title_text="Speed (mph)", row=1, col=1)
        fig.update_yaxes(
            title_text="Direction (°)", 
            row=2, col=1, 
            range=[0, 360],
            tickmode='array',
            tickvals=[0, 90, 180, 270, 360],
            ticktext=['N', 'E', 'S', 'W', 'N']
        )
        fig.update_xaxes(title_text="Date", row=2, col=1)
        
        fig.update_layout(
            height=700,
            hovermode='x unified',
            template='plotly_white'
        )
        
        return fig
    
    def create_rain_plot(self):
        """Create rainfall plot"""
        fig = make_subplots(
            rows=2, cols=1,
            subplot_titles=('Rain Rate', 'Daily Rainfall'),
            vertical_spacing=0.15
        )
        
        # Hourly rain rate
        fig.add_trace(go.Scatter(
            x=self.df['datetime'],
            y=self.df['hourlyrainin'],
            name='Rain Rate',
            line=dict(color='rgb(0, 150, 255)', width=0),
            fill='tozeroy',
            fillcolor='rgba(0, 150, 255, 0.4)',
            mode='lines',
            showlegend=False
        ), row=1, col=1)
        
        # Daily rain
        fig.add_trace(go.Scatter(
            x=self.df['datetime'],
            y=self.df['dailyrainin'],
            name='Daily Rain',
            line=dict(color='rgb(0, 100, 200)', width=2),
            mode='lines',
            showlegend=False
        ), row=2, col=1)
        
        fig.update_yaxes(title_text="Rate (in/hr)", row=1, col=1)
        fig.update_yaxes(title_text="Accumulation (in)", row=2, col=1)
        fig.update_xaxes(title_text="Date", row=2, col=1)
        
        fig.update_layout(
            height=600,
            hovermode='x unified',
            template='plotly_white'
        )
        
        return fig
    
    def create_pressure_plot(self):
        """Create barometric pressure plot"""
        fig = go.Figure()
        
        fig.add_trace(go.Scatter(
            x=self.df['datetime'],
            y=self.df['baromrelin'],
            name='Relative Pressure',
            line=dict(color='rgb(0, 123, 255)', width=2),
            mode='lines'
        ))
        
        fig.update_layout(
            title='Barometric Pressure',
            xaxis_title='Date',
            yaxis_title='Pressure (inHg)',
            hovermode='x unified',
            template='plotly_white',
            height=400
        )
        
        return fig
    
    def create_humidity_plot(self):
        """Create humidity plot"""
        fig = go.Figure()
        
        # Outdoor humidity with shaded area
        fig.add_trace(go.Scatter(
            x=self.df['datetime'],
            y=self.df['humidity'],
            name='Outdoor Humidity',
            line=dict(color='rgb(0, 123, 255)', width=2),
            fill='tozeroy',
            fillcolor='rgba(0, 123, 255, 0.1)',
            mode='lines'
        ))
        
        fig.update_layout(
            title='Outdoor Humidity',
            xaxis_title='Date',
            yaxis_title='Humidity (%)',
            hovermode='x unified',
            template='plotly_white',
            height=400
        )
        
        return fig
    
    def create_solar_plot(self):
        """Create solar radiation and UV index plot"""
        fig = make_subplots(
            rows=2, cols=1,
            subplot_titles=('Solar Radiation', 'UV Index'),
            vertical_spacing=0.15
        )
        
        # Solar radiation
        fig.add_trace(go.Scatter(
            x=self.df['datetime'],
            y=self.df['solarradiation'],
            name='Solar Radiation',
            line=dict(color='rgb(255, 165, 0)', width=0),
            fill='tozeroy',
            fillcolor='rgba(255, 165, 0, 0.3)',
            mode='lines',
            showlegend=False
        ), row=1, col=1)
        
        # UV Index
        fig.add_trace(go.Scatter(
            x=self.df['datetime'],
            y=self.df['uv'],
            name='UV Index',
            line=dict(color='rgb(138, 43, 226)', width=0),
            fill='tozeroy',
            fillcolor='rgba(138, 43, 226, 0.3)',
            mode='lines',
            showlegend=False
        ), row=2, col=1)
        
        fig.update_yaxes(title_text="W/m²", row=1, col=1)
        fig.update_yaxes(title_text="UV Index", row=2, col=1)
        fig.update_xaxes(title_text="Date", row=2, col=1)
        
        fig.update_layout(
            height=600,
            hovermode='x unified',
            template='plotly_white'
        )
        
        return fig
    
    def create_indoor_conditions_plot(self):
        """Create indoor temperature and humidity plot"""
        fig = make_subplots(
            rows=2, cols=1,
            subplot_titles=('Indoor Temperature', 'Indoor Humidity'),
            vertical_spacing=0.15
        )
        
        # Indoor temperature
        fig.add_trace(go.Scatter(
            x=self.df['datetime'],
            y=self.df['tempinf'],
            name='Indoor Temp',
            line=dict(color='rgb(0, 123, 255)', width=2),
            fill='tozeroy',
            fillcolor='rgba(0, 123, 255, 0.1)',
            mode='lines',
            showlegend=False
        ), row=1, col=1)
        
        # Indoor humidity
        fig.add_trace(go.Scatter(
            x=self.df['datetime'],
            y=self.df['humidityin'],
            name='Indoor Humidity',
            line=dict(color='rgb(0, 123, 255)', width=2),
            fill='tozeroy',
            fillcolor='rgba(0, 123, 255, 0.1)',
            mode='lines',
            showlegend=False
        ), row=2, col=1)
        
        fig.update_yaxes(title_text="Temperature (°F)", row=1, col=1)
        fig.update_yaxes(title_text="Humidity (%)", row=2, col=1)
        fig.update_xaxes(title_text="Date", row=2, col=1)
        
        fig.update_layout(
            height=600,
            hovermode='x unified',
            template='plotly_white'
        )
        
        return fig
    
    def create_dashboard(self, output_dir='output'):
        """Create a comprehensive dashboard with all plots"""
        import os
        
        if self.df is None or len(self.df) == 0:
            print("ERROR: No data loaded. Please load data first.")
            return False
        
        # Create output directory if it doesn't exist
        os.makedirs(output_dir, exist_ok=True)
        
        print("Creating visualizations...")
        
        # Create all plots
        plots = {
            'temperature.html': ('Temperature', self.create_temperature_plot),
            'wind.html': ('Wind', self.create_wind_plot),
            'rain.html': ('Rain', self.create_rain_plot),
            'pressure.html': ('Pressure', self.create_pressure_plot),
            'humidity.html': ('Humidity', self.create_humidity_plot),
            'solar.html': ('Solar/UV', self.create_solar_plot),
            'indoor.html': ('Indoor', self.create_indoor_conditions_plot),
        }
        
        for filename, (name, func) in plots.items():
            try:
                print(f"  Creating {name} plot...")
                fig = func()
                filepath = os.path.join(output_dir, filename)
                fig.write_html(filepath)
                print(f"    Saved: {filepath}")
            except Exception as e:
                print(f"    ERROR creating {name} plot: {e}")
        
        print(f"\nAll visualizations saved to '{output_dir}/' directory")
        print(f"Data range: {self.df['datetime'].min()} to {self.df['datetime'].max()}")
        print(f"Total data points: {len(self.df)}")
        
        return True
    
    def close(self):
        self.conn.close()


def main():
    import os
    
    # Check if database exists
    if not os.path.exists('ambient_weather.db'):
        print("ERROR: Database not found!")
        print("Please run 'python ambient_weather_fetch.py' first to fetch data.")
        sys.exit(1)
    
    # Create visualizer
    print("Loading data from database...")
    viz = WeatherVisualizer('ambient_weather.db')
    
    # Load all data (or specify date range)
    # Example: Load last 30 days
    # start_date = datetime.now() - timedelta(days=30)
    # viz.load_data(start_date=start_date)
    
    data = viz.load_data()
    
    if data is None or len(data) == 0:
        print("ERROR: No data found in database.")
        print("Please run 'python ambient_weather_fetch.py' first to fetch data.")
        viz.close()
        sys.exit(1)
    
    print(f"Loaded {len(data)} records")
    
    # Create all visualizations
    success = viz.create_dashboard()
    
    viz.close()
    
    if success:
        print("\n" + "="*50)
        print("Visualization complete!")
        print("="*50)
        print("Open the HTML files in the 'output' directory with your web browser")
    

if __name__ == "__main__":
    main()
