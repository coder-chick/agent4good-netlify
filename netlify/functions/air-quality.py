import json
import os
import pandas as pd
from datetime import datetime, timedelta
from google.cloud import bigquery
import google.generativeai as genai


def handler(event, context):
    """Netlify Function handler for air quality data API"""
    
    # Handle CORS
    headers = {
        'Access-Control-Allow-Origin': '*',
        'Access-Control-Allow-Headers': 'Content-Type',
        'Access-Control-Allow-Methods': 'GET, POST, OPTIONS'
    }
    
    if event['httpMethod'] == 'OPTIONS':
        return {
            'statusCode': 200,
            'headers': headers,
            'body': ''
        }
    
    try:
        # Initialize BigQuery client
        bq_client = bigquery.Client(project=os.getenv('GOOGLE_CLOUD_PROJECT'))
        
        # Get query parameters
        query_params = event.get('queryStringParameters', {}) or {}
        state = query_params.get('state', None)
        days = int(query_params.get('days', 7))
        
        # Query air quality data
        dataset = os.getenv('BIGQUERY_DATASET', 'air_quality_dataset')
        table = os.getenv('BIGQUERY_TABLE', 'air_quality_data')
        
        query = f"""
        SELECT 
            date,
            state_name,
            county_name,
            aqi,
            parameter_name,
            site_name
        FROM `{os.getenv('GOOGLE_CLOUD_PROJECT')}.{dataset}.{table}`
        WHERE date >= DATE_SUB(CURRENT_DATE(), INTERVAL {days} DAY)
        """
        
        if state:
            query += f" AND UPPER(state_name) = UPPER('{state}')"
        
        query += " ORDER BY date DESC LIMIT 1000"
        
        query_job = bq_client.query(query)
        results = query_job.result()
        
        data = []
        for row in results:
            data.append({
                'date': row.date.isoformat() if row.date else None,
                'state_name': row.state_name,
                'county_name': row.county_name,
                'aqi': row.aqi,
                'parameter_name': row.parameter_name,
                'site_name': row.site_name
            })
        
        # Calculate statistics
        df = pd.DataFrame(data)
        stats = {}
        if not df.empty:
            stats = {
                'total_records': len(df),
                'unique_locations': df['county_name'].nunique() if 'county_name' in df else 0,
                'avg_aqi': float(df['aqi'].mean()) if 'aqi' in df and not df['aqi'].empty else 0,
                'max_aqi': float(df['aqi'].max()) if 'aqi' in df and not df['aqi'].empty else 0,
                'min_aqi': float(df['aqi'].min()) if 'aqi' in df and not df['aqi'].empty else 0,
            }
        
        return {
            'statusCode': 200,
            'headers': headers,
            'body': json.dumps({
                'success': True,
                'data': data,
                'statistics': stats,
                'count': len(data)
            })
        }
        
    except Exception as e:
        return {
            'statusCode': 500,
            'headers': headers,
            'body': json.dumps({
                'success': False,
                'error': str(e)
            })
        }