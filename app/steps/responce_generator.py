from typing import List
import logging
import requests
logger = logging.getLogger(__name__)
def generate_responce(data: List[dict],model_name: str = "gpt-oss:20b", base_url: str = "http://localhost:11434") -> str:
    formatted_data = "\n".join([f"Claim: {item['claim']}\nVerfication Result: {item['verfication_result']}" for item in data])
    prompt = f"""You are a video authenticity analyst. After thoroughly examining a video's content and fact-checking its claims, provide your final assessment.

VIDEO FACT-CHECK RESULTS:
{formatted_data}

TASK:
Based on your comprehensive analysis of the video's content and the verification of its claims, determine the overall authenticity of this video.

INSTRUCTIONS:
- Write as if you have analyzed the entire video content, not just individual claims
- Conclude whether the video is AUTHENTIC, PARTIALLY AUTHENTIC, or INAUTHENTIC
- Focus on the video's overall credibility and trustworthiness
- Avoid mentioning claim counts or statistical breakdowns
- Write a cohesive assessment about the video's content quality and reliability
- Keep your entire response between 1000 and 1500 characters including spaces

Respond now:"""
    
    payload = {
        "model": model_name,
        "prompt": prompt,
        "stream": False,
        "options": {
            "temperature": 0.0, 
            "top_p": 0.9
        }
    }
    
    try:
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