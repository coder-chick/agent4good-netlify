import json
import os
import sys
import traceback
import asyncio
from typing import Optional, Dict, Any

# Add the agent directories to Python path
sys.path.append(os.path.join(os.path.dirname(__file__), '..', '..', 'multi_tool_agent'))
sys.path.append(os.path.join(os.path.dirname(__file__), '..', '..', 'multi_tool_agent_bquery_tools'))

def handler(event, context):
    """Netlify Function handler for multi-agent query system with Google ADK"""
    
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
        # Parse request body
        request_data = json.loads(event.get('body', '{}'))
        query = request_data.get('query', '')
        use_bigquery = request_data.get('use_bigquery', True)
        
        if not query:
            return {
                'statusCode': 400,
                'headers': headers,
                'body': json.dumps({
                    'success': False,
                    'error': 'Query parameter is required'
                })
            }
        
        # Try Google ADK agents first
        response = try_adk_agents(query, use_bigquery)
        if response:
            return {
                'statusCode': 200,
                'headers': headers,
                'body': json.dumps({
                    'success': True,
                    'response': response,
                    'agent': 'google-adk',
                    'source': 'agent_working.py'
                })
            }
        
        # Fallback to direct agent modules
        if use_bigquery:
            response = try_bigquery_agent(query)
            if response:
                return {
                    'statusCode': 200,
                    'headers': headers,
                    'body': json.dumps({
                        'success': True,
                        'response': response,
                        'agent': 'bigquery',
                        'source': 'multi_tool_agent_bquery_tools'
                    })
                }
        
        # Fallback to simple multi-tool agent
        response = try_simple_agent(query)
        if response:
            return {
                'statusCode': 200,
                'headers': headers,
                'body': json.dumps({
                    'success': True,
                    'response': response,
                    'agent': 'simple',
                    'source': 'multi_tool_agent'
                })
            }
        
        # If agents fail, provide a fallback response
        fallback_response = generate_fallback_response(query)
        return {
            'statusCode': 200,
            'headers': headers,
            'body': json.dumps({
                'success': True,
                'response': fallback_response,
                'agent': 'fallback',
                'source': 'builtin'
            })
        }
        
    except Exception as e:
        error_info = {
            'error': str(e),
            'type': type(e).__name__,
            'traceback': traceback.format_exc()
        }
        
        return {
            'statusCode': 500,
            'headers': headers,
            'body': json.dumps({
                'success': False,
                'error': 'Internal server error',
                'details': error_info
            })
        }


def try_adk_agents(query: str, use_bigquery: bool = True) -> Optional[str]:
    """Try to use the Google ADK agents from agent_working.py"""
    try:
        # Set up environment for ADK
        os.environ.setdefault('GOOGLE_APPLICATION_CREDENTIALS', 'service-account-key.json')
        
        # Import the working agent system
        import sys
        sys.path.append(os.path.join(os.path.dirname(__file__), '..', '..'))
        
        # Try to run the ADK agent system
        from agent_working import run_query_with_adk
        
        # Run the ADK agent
        result = run_query_with_adk(query)
        return result
        
    except Exception as e:
        print(f"ADK agent failed: {e}")
        return None

def try_bigquery_agent(query: str) -> Optional[str]:
    """Try to use the BigQuery agent"""
    try:
        # Import the BigQuery agent
        from multi_tool_agent_bquery_tools.agent import run_query
        
        # Run the query
        result = run_query(query)
        return result
        
    except Exception as e:
        print(f"BigQuery agent failed: {e}")
        return None


def try_simple_agent(query: str) -> Optional[str]:
    """Try to use the simple multi-tool agent"""
    try:
        # Import the simple agent
        from multi_tool_agent.agent import run_query
        
        # Run the query
        result = run_query(query)
        return result
        
    except Exception as e:
        print(f"Simple agent failed: {e}")
        return None


def generate_fallback_response(query: str) -> str:
    """Generate a fallback response when agents are unavailable"""
    
    # Analyze query for air quality keywords
    air_quality_keywords = ['aqi', 'air quality', 'pollution', 'particulate', 'ozone', 'smog']
    health_keywords = ['health', 'respiratory', 'asthma', 'lung', 'breathing', 'symptoms']
    location_keywords = ['california', 'texas', 'new york', 'florida', 'illinois', 'county', 'state']
    
    query_lower = query.lower()
    
    is_air_quality = any(keyword in query_lower for keyword in air_quality_keywords)
    is_health = any(keyword in query_lower for keyword in health_keywords)
    is_location = any(keyword in query_lower for keyword in location_keywords)
    
    if is_air_quality and is_health:
        return """Based on your air quality health question, here are some general guidelines:
        
**Air Quality Index (AQI) Health Guidelines:**
- 0-50 (Good): Air quality is satisfactory for most people
- 51-100 (Moderate): Unusually sensitive people may experience minor symptoms
- 101-150 (Unhealthy for Sensitive Groups): People with lung disease, heart disease, or asthma should limit outdoor activities
- 151-200 (Unhealthy): Everyone should reduce prolonged outdoor exertion
- 201-300 (Very Unhealthy): Everyone should avoid outdoor activities
- 301+ (Hazardous): Health alert - everyone should avoid outdoor activities

**Recommendations:**
- Check daily AQI forecasts before planning outdoor activities
- Use air purifiers indoors during high pollution days
- Consider wearing N95 masks outdoors when AQI > 150
- Consult your healthcare provider if you have respiratory conditions

*Note: This is general information. For real-time data and personalized advice, our AI agents provide more detailed analysis.*"""
        
    elif is_air_quality:
        return """Air quality information varies by location and time. Here's what I can share:
        
**Common Air Quality Factors:**
- Particulate Matter (PM2.5 and PM10)
- Ozone (O3)
- Nitrogen Dioxide (NO2)
- Sulfur Dioxide (SO2)
- Carbon Monoxide (CO)

**Factors Affecting Air Quality:**
- Weather conditions (wind, temperature, humidity)
- Traffic and industrial emissions
- Seasonal patterns (wildfire season, winter heating)
- Geographic features (valleys, mountains)

*For current conditions and detailed analysis in your area, our AI agents can access real-time BigQuery data.*"""
        
    elif is_health:
        return """Health considerations related to environmental factors:
        
**Air Quality Health Effects:**
- Short-term: Eye irritation, coughing, throat irritation
- Long-term: Respiratory disease, cardiovascular effects
- Vulnerable groups: Children, elderly, people with asthma/heart disease

**Protection Strategies:**
- Monitor daily air quality forecasts
- Limit outdoor exercise during high pollution days
- Use HEPA air purifiers indoors
- Keep windows closed during poor air quality events

*Our AI agents can provide personalized recommendations based on current conditions in your area.*"""
        
    else:
        return f"""I understand you're asking about: "{query}"
        
While our advanced AI agents are currently unavailable, I can provide some general information:

**Our AI Agent System Features:**
- Real-time air quality data analysis from BigQuery
- Location-specific health recommendations
- Multi-tool analysis capabilities
- Integration with Google Cloud services

**For the most accurate and current information:**
- Try refreshing the page to reconnect to our AI agents
- Check back in a few moments as the system may be initializing
- Visit our main dashboard for real-time air quality data

*Our intelligent agents provide much more detailed and personalized responses when available.*"""


# Helper function for async agent calls (if needed)
async def run_agent_async(agent_function, query: str):
    """Run agent function asynchronously"""
    try:
        import asyncio
        loop = asyncio.get_event_loop()
        return await loop.run_in_executor(None, agent_function, query)
    except Exception as e:
        print(f"Async agent execution failed: {e}")
        return None