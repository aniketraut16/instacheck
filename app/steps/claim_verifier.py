from typing import List
import logging
import requests
logger = logging.getLogger(__name__)

def verify_claim(claim: str , evidence: List[str],model_name: str = "gpt-oss:20b", base_url: str = "http://localhost:11434") -> str:
    prompt = f"""You are a fact-checking assistant. Analyze the claim against the provided evidence and determine if it is correct, partially correct, or incorrect.

CLAIM: {claim}

EVIDENCE:
{chr(10).join([f"- {ev}" for ev in evidence])}

INSTRUCTIONS:
- Base your analysis ONLY on the evidence provided above
- Do not use external knowledge unless the evidence is insufficient
- Classify the claim as: CORRECT, PARTIALLY CORRECT, or INCORRECT
- Provide a brief explanation for your classification
- Keep your response under 700 characters including spaces

Respond now:"""
    
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
        logger.info(f"Verifying claim: {claim[:100]}...")
        api_url = f"{base_url}/api/generate"
        
        response = requests.post(
            api_url,
            json=payload,
            headers={"Content-Type": "application/json"},
            timeout=120
        )
        response.raise_for_status()
        
        result = response.json()
        raw_response = result.get("response", "").strip()

        return raw_response
    except Exception as e:
        logger.error(f"Error verifying claim: {e}")
        return None