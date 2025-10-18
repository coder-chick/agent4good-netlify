import jsonimport json

import pandas as pdimport os

import numpy as npimport pandas as pd

from datetime import datetime, timedeltafrom datetime import datetime, timedelta

from google.cloud import bigquery

# GitHub raw file URLs for CSV dataimport google.generativeai as genai

GITHUB_RAW_BASE = "https://raw.githubusercontent.com/coder-chick/agent4good-netlify/main/data"

AIR_QUALITY_CSV_URL = f"{GITHUB_RAW_BASE}/daily_88101_2025/daily_88101_2025.csv"

import json

def load_air_quality_data():import pandas as pd

    """Load air quality data from GitHub CSV"""import numpy as np

    try:from datetime import datetime, timedelta

        df = pd.read_csv(AIR_QUALITY_CSV_URL)

        # GitHub raw file URLs for CSV data

        # Basic data cleaningGITHUB_RAW_BASE = "https://raw.githubusercontent.com/coder-chick/agent4good-netlify/main/data"

        if 'Date' in df.columns:AIR_QUALITY_CSV_URL = f"{GITHUB_RAW_BASE}/daily_88101_2025/daily_88101_2025.csv"

            df['Date'] = pd.to_datetime(df['Date'], errors='coerce')

        elif 'date' in df.columns:def load_air_quality_data():

            df['date'] = pd.to_datetime(df['date'], errors='coerce')    """Load air quality data from GitHub CSV"""

            df = df.rename(columns={'date': 'Date'})    try:

                df = pd.read_csv(AIR_QUALITY_CSV_URL)

        # Standardize column names        

        column_mapping = {        # Basic data cleaning

            'State Name': 'state_name',        if 'Date' in df.columns:

            'state': 'state_name',            df['Date'] = pd.to_datetime(df['Date'], errors='coerce')

            'County Name': 'county_name',         elif 'date' in df.columns:

            'county': 'county_name',            df['date'] = pd.to_datetime(df['date'], errors='coerce')

            'AQI': 'aqi',            df = df.rename(columns={'date': 'Date'})

            'Parameter Name': 'parameter_name',        

            'Site Name': 'site_name'        # Standardize column names

        }        column_mapping = {

                    'State Name': 'state_name',

        for old_col, new_col in column_mapping.items():            'state': 'state_name',

            if old_col in df.columns:            'County Name': 'county_name', 

                df = df.rename(columns={old_col: new_col})            'county': 'county_name',

                    'AQI': 'aqi',

        # Convert AQI to numeric            'Parameter Name': 'parameter_name',

        df['aqi'] = pd.to_numeric(df['aqi'], errors='coerce')            'Site Name': 'site_name'

        df = df.dropna(subset=['aqi'])        }

                

        return df        for old_col, new_col in column_mapping.items():

    except Exception as e:            if old_col in df.columns:

        print(f"Error loading data: {e}")                df = df.rename(columns={old_col: new_col})

        return None        

        # Convert AQI to numeric

def handler(event, context):        df['aqi'] = pd.to_numeric(df['aqi'], errors='coerce')

    """Netlify Function handler for air quality data API using CSV data"""        df = df.dropna(subset=['aqi'])

            

    # Handle CORS        return df

    headers = {    except Exception as e:

        'Access-Control-Allow-Origin': '*',        print(f"Error loading data: {e}")

        'Access-Control-Allow-Headers': 'Content-Type',        return None

        'Access-Control-Allow-Methods': 'GET, POST, OPTIONS'

    }def handler(event, context):

        """Netlify Function handler for air quality data API"""

    if event['httpMethod'] == 'OPTIONS':    

        return {    # Handle CORS

            'statusCode': 200,    headers = {

            'headers': headers,        'Access-Control-Allow-Origin': '*',

            'body': ''        'Access-Control-Allow-Headers': 'Content-Type',

        }        'Access-Control-Allow-Methods': 'GET, POST, OPTIONS'

        }

    try:    

        # Get query parameters    if event['httpMethod'] == 'OPTIONS':

        query_params = event.get('queryStringParameters', {}) or {}        return {

        state = query_params.get('state', None)            'statusCode': 200,

        days = int(query_params.get('days', 7))            'headers': headers,

                    'body': ''

        # Load data from CSV        }

        df = load_air_quality_data()    

            try:

        if df is None or len(df) == 0:        # Initialize BigQuery client

            return {        bq_client = bigquery.Client(project=os.getenv('GOOGLE_CLOUD_PROJECT'))

                'statusCode': 200,        

                'headers': headers,        # Get query parameters

                'body': json.dumps({        query_params = event.get('queryStringParameters', {}) or {}

                    'success': False,        state = query_params.get('state', None)

                    'error': 'No data available',        days = int(query_params.get('days', 7))

                    'data': [],        

                    'statistics': {        # Query air quality data

                        'total_records': 0,        dataset = os.getenv('BIGQUERY_DATASET', 'air_quality_dataset')

                        'unique_locations': 0,        table = os.getenv('BIGQUERY_TABLE', 'air_quality_data')

                        'avg_aqi': 0,        

                        'health_status': 'No Data'        query = f"""

                    }        SELECT 

                })            date,

            }            state_name,

                    county_name,

        # Filter by state if specified            aqi,

        if state and state != 'all':            parameter_name,

            df_filtered = df[df['state_name'].str.contains(state, case=False, na=False)]            site_name

        else:        FROM `{os.getenv('GOOGLE_CLOUD_PROJECT')}.{dataset}.{table}`

            df_filtered = df.copy()        WHERE date >= DATE_SUB(CURRENT_DATE(), INTERVAL {days} DAY)

                """

        # Filter by date range (last N days)        

        if 'Date' in df_filtered.columns:        if state:

            cutoff_date = datetime.now() - timedelta(days=days)            query += f" AND UPPER(state_name) = UPPER('{state}')"

            df_filtered = df_filtered[df_filtered['Date'] >= cutoff_date]        

                query += " ORDER BY date DESC LIMIT 1000"

        # Take a sample if dataset is too large        

        if len(df_filtered) > 1000:        query_job = bq_client.query(query)

            df_filtered = df_filtered.sample(n=1000)        results = query_job.result()

                

        # Convert to records        data = []

        records = df_filtered.to_dict('records')        for row in results:

                    data.append({

        # Convert timestamps to strings for JSON serialization                'date': row.date.isoformat() if row.date else None,

        for record in records:                'state_name': row.state_name,

            if 'Date' in record and pd.notna(record['Date']):                'county_name': row.county_name,

                record['Date'] = record['Date'].strftime('%Y-%m-%d')                'aqi': row.aqi,

            # Ensure all values are JSON serializable                'parameter_name': row.parameter_name,

            for key, value in record.items():                'site_name': row.site_name

                if pd.isna(value):            })

                    record[key] = None        

                elif isinstance(value, (np.integer, np.floating)):        # Calculate statistics

                    record[key] = float(value)        df = pd.DataFrame(data)

                stats = {}

        # Calculate statistics        if not df.empty:

        if len(df_filtered) > 0:            stats = {

            avg_aqi = df_filtered['aqi'].mean()                'total_records': len(df),

            unique_locations = df_filtered['county_name'].nunique()                'unique_locations': df['county_name'].nunique() if 'county_name' in df else 0,

                            'avg_aqi': float(df['aqi'].mean()) if 'aqi' in df and not df['aqi'].empty else 0,

            if avg_aqi <= 50:                'max_aqi': float(df['aqi'].max()) if 'aqi' in df and not df['aqi'].empty else 0,

                health_status = 'Good'                'min_aqi': float(df['aqi'].min()) if 'aqi' in df and not df['aqi'].empty else 0,

            elif avg_aqi <= 100:            }

                health_status = 'Moderate'        

            elif avg_aqi <= 150:        return {

                health_status = 'Unhealthy for Sensitive Groups'            'statusCode': 200,

            elif avg_aqi <= 200:            'headers': headers,

                health_status = 'Unhealthy'            'body': json.dumps({

            else:                'success': True,

                health_status = 'Very Unhealthy'                'data': data,

        else:                'statistics': stats,

            avg_aqi = 0                'count': len(data)

            unique_locations = 0            })

            health_status = 'No Data'        }

                

        statistics = {    except Exception as e:

            'total_records': len(records),        return {

            'unique_locations': unique_locations,            'statusCode': 500,

            'avg_aqi': round(avg_aqi, 1),            'headers': headers,

            'health_status': health_status            'body': json.dumps({

        }                'success': False,

                        'error': str(e)

        return {            })

            'statusCode': 200,        }
            'headers': headers,
            'body': json.dumps({
                'success': True,
                'data': records,
                'statistics': statistics,
                'count': len(records),
                'filtered_by': {
                    'state': state,
                    'days': days
                }
            })
        }
        
    except Exception as e:
        print(f"Error in air-quality function: {e}")
        
        return {
            'statusCode': 500,
            'headers': headers,
            'body': json.dumps({
                'success': False,
                'error': str(e),
                'data': [],
                'statistics': {
                    'total_records': 0,
                    'unique_locations': 0,
                    'avg_aqi': 0,
                    'health_status': 'Error'
                }
            })
        }