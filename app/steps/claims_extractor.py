import requests
import json
import logging

# Setup logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class InstagramReelClaimsExtractor:
    def __init__(self, model_name: str = "gpt-oss:20b", base_url: str = "http://localhost:11434"):
        """Initialize the extractor using Ollama API directly."""
        self.model_name = model_name
        self.base_url = base_url
        self.api_url = f"{base_url}/api/generate"
        self.prompt_template = self._create_extraction_prompt()
    
    def _create_extraction_prompt(self) -> str:
        """Prompt template for claim extraction."""
        return """
You are an expert fact-checker. Extract 2-5 SPECIFIC, EVIDENCE-BACKED, verifiable claims from this Instagram Reel transcription for authenticity verification.

- Claims must include SPECIFIC details (names, dates, numbers, locations, companies)
- NO subjective, theoretical, or vague claims
- Return claims as a JSON array with objects: 'claim' and 'category' fields

Categories: health_medical, political_news, celebrity_gossip, financial_market, scientific_fact, historical_event, product_review, social_issue, technology_tech, sports_entertainment, weather_natural, business_economy, education_academic, legal_regulatory, cultural_trend

Transcription: {transcription}

Respond ONLY with valid JSON array, no additional text.
"""
    
    def _call_ollama_api(self, prompt: str) -> str:
        """Make API call to Ollama."""
        payload = {
            "model": self.model_name,
            "prompt": prompt,
            "stream": False,
        }
        
        try:
            response = requests.post(
                self.api_url,
                json=payload,
                headers={"Content-Type": "application/json"},
                # timeout=120  
            )
            response.raise_for_status()
            
            result = response.json()
            return result.get("response", "")
            
        except requests.exceptions.ConnectionError:
            raise ConnectionError(f"Could not connect to Ollama at {self.base_url}. Make sure Ollama is running.")
        except requests.exceptions.Timeout:
            raise TimeoutError("Ollama API request timed out")
        except requests.exceptions.RequestException as e:
            raise RuntimeError(f"Ollama API request failed: {e}")
    
    def extract_claims(self, transcription: str):
        if not transcription or not transcription.strip():
            raise ValueError("Transcription cannot be empty")
        
        try:
            logger.info(f"Extracting claims from transcription: {transcription[:100]}...")
            
            # Format the prompt with transcription
            formatted_prompt = self.prompt_template.format(transcription=transcription.strip())
            
            # Call Ollama API
            response = self._call_ollama_api(formatted_prompt)
            
            # Parse the JSON response
            try:
                # Clean up the response string and parse as JSON
                cleaned_response = response.strip()
                claims_data = json.loads(cleaned_response)
                return claims_data
            except json.JSONDecodeError as e:
                logger.error(f"Failed to parse JSON response: {e}")
                logger.error(f"Raw response: {response}")
                return []
                
        except Exception as e:
            logger.error(f"Claim extraction failed: {e}")
            return []

    def check_model_availability(self) -> bool:
        try:
            list_url = f"{self.base_url}/api/tags"
            response = requests.get(list_url, timeout=10)
            response.raise_for_status()
            
            models = response.json().get("models", [])
            available_models = [model.get("name", "") for model in models]
            
            if self.model_name in available_models:
                logger.info(f"Model {self.model_name} is available")
                return True
            else:
                logger.warning(f"Model {self.model_name} not found. Available models: {available_models}")
                return False
                
        except Exception as e:
            logger.error(f"Could not check model availability: {e}")
            return False

def extract_claims(transcription: str, model_name: str = "gpt-oss:20b", base_url: str = "http://localhost:11434"):
    
    extractor = InstagramReelClaimsExtractor(model_name=model_name, base_url=base_url)
    
    # Check if model is available (optional)
    if not extractor.check_model_availability():
        logger.warning("Proceeding anyway - model might still work")
    
    return extractor.extract_claims(transcription)