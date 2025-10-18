from flask import Flask, render_template, request, jsonify
import pandas as pd
import numpy as np
from datetime import datetime, timedelta
import json
import os
from flask_cors import CORS

app = Flask(__name__)
CORS(app)  # Enable CORS for all routes
app.config['SECRET_KEY'] = 'dev-secret-key'

# GitHub raw file URLs for CSV data
GITHUB_RAW_BASE = "https://raw.githubusercontent.com/coder-chick/agent4good-netlify/main/data"
AIR_QUALITY_CSV_URL = f"{GITHUB_RAW_BASE}/daily_88101_2025/daily_88101_2025.csv"

# Cache for loaded data
air_quality_data = None
data_last_loaded = None

def load_air_quality_data():
    """Load air quality data from GitHub CSV"""
    global air_quality_data, data_last_loaded
    
    # Check if we need to reload data (cache for 1 hour)
    if (air_quality_data is None or 
        data_last_loaded is None or 
        datetime.now() - data_last_loaded > timedelta(hours=1)):
        
        try:
            print(f"Loading air quality data from: {AIR_QUALITY_CSV_URL}")
            
            # Read CSV from GitHub
            df = pd.read_csv(AIR_QUALITY_CSV_URL)
            
            # Basic data cleaning and processing
            if 'Date' in df.columns:
                df['Date'] = pd.to_datetime(df['Date'], errors='coerce')
            elif 'date' in df.columns:
                df['date'] = pd.to_datetime(df['date'], errors='coerce')
                df = df.rename(columns={'date': 'Date'})
            
            # Standardize column names
            column_mapping = {
                'State Name': 'state_name',
                'state': 'state_name',
                'County Name': 'county_name', 
                'county': 'county_name',
                'AQI': 'aqi',
                'Parameter Name': 'parameter_name',
                'parameter': 'parameter_name',
                'Site Name': 'site_name',
                'site': 'site_name'
            }
            
            for old_col, new_col in column_mapping.items():
                if old_col in df.columns:
                    df = df.rename(columns={old_col: new_col})
            
            # Ensure required columns exist
            required_cols = ['state_name', 'county_name', 'aqi']
            for col in required_cols:
                if col not in df.columns:
                    df[col] = 'Unknown'
            
            # Convert AQI to numeric
            df['aqi'] = pd.to_numeric(df['aqi'], errors='coerce')
            
            # Remove rows with invalid AQI values
            df = df.dropna(subset=['aqi'])
            
            air_quality_data = df
            data_last_loaded = datetime.now()
            
            print(f"✅ Loaded {len(df)} air quality records")
            return df
            
        except Exception as e:
            print(f"❌ Error loading air quality data: {e}")
            # Return dummy data as fallback
            air_quality_data = pd.DataFrame({
                'Date': [datetime.now() - timedelta(days=i) for i in range(7)],
                'state_name': ['California'] * 7,
                'county_name': ['Los Angeles'] * 7,
                'aqi': [45, 52, 38, 61, 47, 55, 42],
                'parameter_name': ['PM2.5'] * 7,
                'site_name': ['Downtown LA'] * 7
            })
            data_last_loaded = datetime.now()
            print("🔄 Using dummy data as fallback")
            return air_quality_data
    
    return air_quality_data

def get_air_quality_stats(df):
    """Calculate statistics from air quality data"""
    if df is None or len(df) == 0:
        return {
            'total_records': 0,
            'unique_locations': 0,
            'avg_aqi': 0,
            'health_status': 'No Data'
        }
    
    total_records = len(df)
    unique_locations = df['county_name'].nunique() if 'county_name' in df.columns else 0
    avg_aqi = df['aqi'].mean() if 'aqi' in df.columns else 0
    
    # Determine health status based on average AQI
    if avg_aqi <= 50:
        health_status = 'Good'
    elif avg_aqi <= 100:
        health_status = 'Moderate'
    elif avg_aqi <= 150:
        health_status = 'Unhealthy for Sensitive Groups'
    elif avg_aqi <= 200:
        health_status = 'Unhealthy'
    else:
        health_status = 'Very Unhealthy'
    
    return {
        'total_records': total_records,
        'unique_locations': unique_locations,
        'avg_aqi': round(avg_aqi, 1),
        'health_status': health_status
    }

@app.route('/')
def index():
    """Main dashboard page"""
    return render_template('index.html')

@app.route('/health')
def health():
    """Health check endpoint"""
    return jsonify({
        'status': 'healthy',
        'service': 'Community Health & Wellness Platform',
        'version': '1.0.0',
        'data_source': 'CSV Files from GitHub'
    })

@app.route('/api/air-quality', methods=['GET'])
def get_air_quality():
    """API endpoint to get air quality data"""
    try:
        # Get parameters
        state = request.args.get('state', None)
        days = int(request.args.get('days', 7))
        
        # Load data
        df = load_air_quality_data()
        
        if df is None or len(df) == 0:
            return jsonify({
                'success': False,
                'error': 'No data available',
                'data': [],
                'statistics': get_air_quality_stats(None)
            })
        
        # Filter by state if specified
        if state and state != 'all':
            df_filtered = df[df['state_name'].str.contains(state, case=False, na=False)]
        else:
            df_filtered = df.copy()
        
        # Filter by date range (last N days)
        if 'Date' in df_filtered.columns:
            cutoff_date = datetime.now() - timedelta(days=days)
            df_filtered = df_filtered[df_filtered['Date'] >= cutoff_date]
        
        # Take a sample if dataset is too large
        if len(df_filtered) > 1000:
            df_filtered = df_filtered.sample(n=1000)
        
        # Convert to records
        records = df_filtered.to_dict('records')
        
        # Convert timestamps to strings for JSON serialization
        for record in records:
            if 'Date' in record and pd.notna(record['Date']):
                record['Date'] = record['Date'].strftime('%Y-%m-%d')
        
        # Get statistics
        stats = get_air_quality_stats(df_filtered)
        
        return jsonify({
            'success': True,
            'data': records,
            'statistics': stats,
            'count': len(records),
            'filtered_by': {
                'state': state,
                'days': days
            }
        })
        
    except Exception as e:
        print(f"Error in get_air_quality: {e}")
        return jsonify({
            'success': False,
            'error': str(e),
            'data': [],
            'statistics': get_air_quality_stats(None)
        }), 500

@app.route('/api/health-recommendations', methods=['GET'])
def get_health_recommendations():
    """API endpoint to get health recommendations"""
    try:
        df = load_air_quality_data()
        stats = get_air_quality_stats(df)
        avg_aqi = stats['avg_aqi']
        
        # Generate recommendations based on AQI levels
        if avg_aqi <= 50:
            recommendations = [
                "Air quality is good. Great time for outdoor activities!",
                "Perfect conditions for exercise and outdoor recreation.",
                "Consider opening windows for natural ventilation."
            ]
        elif avg_aqi <= 100:
            recommendations = [
                "Air quality is moderate. Sensitive individuals should limit outdoor activities.",
                "Consider indoor exercise if you have respiratory conditions.",
                "Monitor air quality updates throughout the day."
            ]
        elif avg_aqi <= 150:
            recommendations = [
                "Air quality is unhealthy for sensitive groups.",
                "People with heart or lung disease should avoid outdoor activities.",
                "Keep windows closed and use air purifiers if available."
            ]
        else:
            recommendations = [
                "Air quality is unhealthy. Limit outdoor activities.",
                "Wear masks when going outside if necessary.",
                "Stay indoors and use air purifiers."
            ]
        
        return jsonify({
            'success': True,
            'recommendations': recommendations,
            'based_on_aqi': avg_aqi,
            'health_status': stats['health_status']
        })
        
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e),
            'recommendations': ["Unable to load recommendations at this time."]
        }), 500

@app.route('/api/analyze', methods=['POST'])
def analyze():
    """API endpoint for basic analysis (simplified without AI)"""
    try:
        request_data = request.get_json()
        question = request_data.get('question', '')
        
        df = load_air_quality_data()
        stats = get_air_quality_stats(df)
        
        # Simple rule-based responses
        question_lower = question.lower()
        
        if 'aqi' in question_lower or 'air quality' in question_lower:
            response = f"Based on current data, the average AQI is {stats['avg_aqi']}, which indicates {stats['health_status'].lower()} air quality conditions."
        elif 'health' in question_lower:
            response = f"Current health status is {stats['health_status']} based on air quality data from {stats['total_records']} monitoring locations."
        elif 'location' in question_lower:
            response = f"We are monitoring air quality across {stats['unique_locations']} different locations."
        else:
            response = f"Based on our monitoring data: Average AQI is {stats['avg_aqi']} ({stats['health_status']}), covering {stats['unique_locations']} locations with {stats['total_records']} data points."
        
        return jsonify({
            'success': True,
            'response': response,
            'statistics': stats
        })
        
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e),
            'response': "Sorry, I couldn't process your question at this time."
        }), 500

if __name__ == '__main__':
    # Load data on startup
    print("🚀 Starting Community Health & Wellness Platform (CSV Mode)")
    load_air_quality_data()
    
    port = int(os.environ.get('PORT', 8080))
    app.run(host='0.0.0.0', port=port, debug=True)