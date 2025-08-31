import requests
import json
import logging

# Setup logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def extract_claims(transcription: str, model_name: str = "gpt-oss:20b", base_url: str = "http://localhost:11434"):   
    if not transcription or not transcription.strip():
        raise ValueError("Transcription cannot be empty")
    
    # Enhanced prompt for better claim extraction
    prompt = f"""
You are an expert fact-checker and information analyst. Your task is to extract the CORE verifiable claims from this Instagram Reel transcription.

CRITICAL INSTRUCTIONS:
- Extract ONLY 1-3 claims that capture the ESSENTIAL information of the entire text
- Each claim must be COMPLETELY INDEPENDENT and self-contained
- Include ALL specific details: exact names, precise dates, specific numbers, locations, companies
- NO vague references like "this product", "that company", "recent studies" - be EXPLICITLY specific
- NO subjective opinions, theories, or unverifiable statements
- Focus on the MAIN points that someone would fact-check
- Minimize the number of claims while maximizing information coverage

RESPONSE FORMAT:
Return ONLY a valid JSON array. Each object must have exactly these fields:
- "claim": Complete, specific, independent statement with all details
- "category": One category from the list below

CATEGORIES: health_medical, political_news, celebrity_gossip, financial_market, scientific_fact, historical_event, product_review, social_issue, technology_tech, sports_entertainment, weather_natural, business_economy, education_academic, legal_regulatory, cultural_trend

TRANSCRIPTION:
{transcription.strip()}

RESPOND WITH JSON ONLY - NO OTHER TEXT:
"""

    api_url = f"{base_url}/api/generate"
    payload = {
        "model": model_name,
        "prompt": prompt,
        "stream": False,
        "options": {
            "temperature": 0.0,  # Lower temperature for more consistent JSON output
            "top_p": 0.9
        }
    }
    
    try:
        logger.info(f"Extracting claims from transcription: {transcription[:100]}...")
        
        response = requests.post(
            api_url,
            json=payload,
            headers={"Content-Type": "application/json"},
            timeout=120
        )
        response.raise_for_status()
        
        result = response.json()
        raw_response = result.get("response", "").strip()
        
        # Clean and parse JSON response
        try:
            # Remove any potential markdown code blocks or extra text
            if "```json" in raw_response:
                raw_response = raw_response.split("```json")[1].split("```")[0].strip()
            elif "```" in raw_response:
                raw_response = raw_response.split("```")[1].strip()
            
            # Try to find JSON array in response
            start_idx = raw_response.find('[')
            end_idx = raw_response.rfind(']') + 1
            
            if start_idx != -1 and end_idx > start_idx:
                json_str = raw_response[start_idx:end_idx]
                claims_data = json.loads(json_str)
                
                if isinstance(claims_data, list) and len(claims_data) > 0:
                    logger.info(f"Successfully extracted {len(claims_data)} claims")
                    return claims_data
                else:
                    logger.warning("Empty or invalid claims list")
                    return []
            else:
                logger.error("No valid JSON array found in response")
                return []
                
        except json.JSONDecodeError as e:
            logger.error(f"JSON parsing failed: {e}")
            logger.error(f"Raw response: {raw_response}")
            return []
            
    except requests.exceptions.ConnectionError:
        logger.error(f"Could not connect to Ollama at {base_url}. Make sure Ollama is running.")
        return []
    except requests.exceptions.Timeout:
        logger.error("Ollama API request timed out")
        return []
    except Exception as e:
        logger.error(f"Claim extraction failed: {e}")
        return []

def check_ollama_connection(base_url: str = "http://localhost:11434") -> bool:
    """Check if Ollama is running and accessible."""
    try:
        response = requests.get(f"{base_url}/api/tags", timeout=5)
        response.raise_for_status()
        return True
    except:
        return False

def list_available_models(base_url: str = "http://localhost:11434") -> list:
    """Get list of available models in Ollama."""
    try:
        response = requests.get(f"{base_url}/api/tags", timeout=10)
        response.raise_for_status()
        models = response.json().get("models", [])
        return [model.get("name", "") for model in models]
    except Exception as e:
        logger.error(f"Could not fetch available models: {e}")
        return []