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
You are an expert fact-checker and information analyst. Your task is to extract ONLY the most important verifiable claims from this Instagram Reel transcription.

CRITICAL INSTRUCTIONS:
- Extract ONLY the MOST SIGNIFICANT claims that are worth fact-checking
- If video is not worth checking like its a meme or a random video, return an empty array
- For simple content with basic information: Extract 1-2 claims maximum
- For complex content with multiple important facts: Extract maximum 3 claims
- Each claim must be COMPLETELY INDEPENDENT and self-contained
- Include ALL specific details: exact names, precise dates, specific numbers, locations, companies
- NO vague references like "this product", "that company", "recent studies" - be EXPLICITLY specific
- NO subjective opinions, theories, or unverifiable statements
- NO personal experiences, lifestyle tips, or general advice
- Focus ONLY on factual statements that can be verified through reliable sources
- If the content is mainly opinion, entertainment, or personal stories, return an empty array

WHAT QUALIFIES AS A VERIFIABLE CLAIM:
- Specific medical/health facts with numbers or studies
- Political statements about policies or events
- Financial data, stock prices, economic statistics
- Scientific discoveries or research findings
- Historical facts with specific dates/events
- Product specifications or company announcements
- Legal or regulatory changes

WHAT DOES NOT QUALIFY:
- Personal opinions or experiences
- General advice or tips
- Entertainment content
- Lifestyle recommendations
- Subjective reviews
- Motivational content

RESPONSE FORMAT:
Return ONLY a valid JSON array. Each object must have exactly these fields:
- "claim": Complete, specific, independent statement with all details
- "category": One category from the list below

CATEGORIES: health_medical, political_news, celebrity_gossip, financial_market, scientific_fact, historical_event, product_review, social_issue, technology_tech, sports_entertainment, weather_natural, business_economy, education_academic, legal_regulatory, cultural_trend

TRANSCRIPTION:
{transcription.strip()}

RESPOND WITH JSON ONLY - NO OTHER TEXT. If no significant verifiable claims exist, return an empty array []:
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
            timeout=180
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
                
                if isinstance(claims_data, list):
                    # Filter out any claims that might be too generic or not worth verifying
                    filtered_claims = []
                    for claim in claims_data:
                        if isinstance(claim, dict) and claim.get('claim'):
                            claim_text = claim['claim'].lower()
                            # Skip claims that are too generic or opinion-based
                            if not any(skip_word in claim_text for skip_word in [
                                'i think', 'i believe', 'in my opinion', 'personally', 
                                'you should', 'try this', 'works for me', 'recommend'
                            ]):
                                filtered_claims.append(claim)
                    
                    logger.info(f"Successfully extracted {len(filtered_claims)} claims")
                    return filtered_claims
                else:
                    logger.warning("Invalid claims format")
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