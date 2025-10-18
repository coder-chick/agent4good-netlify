import json
import os
import pandas as pd
from google.cloud import bigquery
import google.generativeai as genai


def handler(event, context):
    """Netlify Function handler for AI analysis API"""
    
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
    
    if event['httpMethod'] != 'POST':
        return {
            'statusCode': 405,
            'headers': headers,
            'body': json.dumps({'error': 'Method not allowed'})
        }
    
    try:
        # Initialize clients
        bq_client = bigquery.Client(project=os.getenv('GOOGLE_CLOUD_PROJECT'))
        genai.configure(api_key=os.getenv('GEMINI_API_KEY'))
        model = genai.GenerativeModel('gemini-pro')
        
        # Parse request body
        request_data = json.loads(event['body'])
        question = request_data.get('question', '')
        state = request_data.get('state', None)
        days = int(request_data.get('days', 7))
        
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
        
        # Generate AI analysis
        if data:
            df = pd.DataFrame(data)
            data_summary = df.describe().to_string()
            
            prompt = f"""
            You are an air quality health advisor. Analyze this air quality data and answer the question.
            
            Data Summary:
            {data_summary}
            
            Recent Records:
            {df.head(10).to_string()}
            
            Question: {question}
            
            Provide a helpful, actionable response focused on community health and wellness.
            """
            
            response = model.generate_content(prompt)
            analysis = response.text
        else:
            analysis = "No recent air quality data available for analysis."
        
        return {
            'statusCode': 200,
            'headers': headers,
            'body': json.dumps({
                'success': True,
                'analysis': analysis,
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