import json
import os
import pandas as pd
from google.cloud import bigquery


def handler(event, context):
    """Netlify Function handler for health recommendations API"""
    
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
        
        # Query air quality data for the last day
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
        WHERE date >= DATE_SUB(CURRENT_DATE(), INTERVAL 1 DAY)
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
        
        if not data:
            return {
                'statusCode': 200,
                'headers': headers,
                'body': json.dumps({
                    'success': False,
                    'message': 'No recent data available'
                })
            }
        
        # Calculate average AQI
        df = pd.DataFrame(data)
        avg_aqi = df['aqi'].mean() if 'aqi' in df and not df.empty else 0
        
        # Health recommendations based on AQI levels
        if avg_aqi <= 50:
            level = "Good"
            color = "#00E400"
            recommendation = "Air quality is satisfactory. Enjoy outdoor activities!"
        elif avg_aqi <= 100:
            level = "Moderate"
            color = "#FFFF00"
            recommendation = "Air quality is acceptable. Sensitive individuals should consider limiting prolonged outdoor exertion."
        elif avg_aqi <= 150:
            level = "Unhealthy for Sensitive Groups"
            color = "#FF7E00"
            recommendation = "Sensitive groups should reduce prolonged outdoor exertion."
        elif avg_aqi <= 200:
            level = "Unhealthy"
            color = "#FF0000"
            recommendation = "Everyone should reduce prolonged outdoor exertion."
        elif avg_aqi <= 300:
            level = "Very Unhealthy"
            color = "#8F3F97"
            recommendation = "Everyone should avoid prolonged outdoor exertion."
        else:
            level = "Hazardous"
            color = "#7E0023"
            recommendation = "Everyone should avoid outdoor activities."
        
        return {
            'statusCode': 200,
            'headers': headers,
            'body': json.dumps({
                'success': True,
                'aqi': round(avg_aqi, 2),
                'level': level,
                'color': color,
                'recommendation': recommendation,
                'data_points': len(data)
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