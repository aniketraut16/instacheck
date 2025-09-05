from groq import Groq
import requests
from core.config import llm_settings
import logging
import os

logger = logging.getLogger(__name__)

# Read Ollama base URL from environment, fallback to localhost
OLLAMA_BASE_URL = os.getenv("OLLAMA_API_BASE", "http://localhost:11434")


async def get_llm_client(prompt: str):
    if llm_settings.provider == "ollama":
        try:
            if not check_ollama_connection(OLLAMA_BASE_URL):
                logger.error("Ollama is not running")
                return None
            
            models = list_available_models(OLLAMA_BASE_URL)
            if "gpt-oss:20b" not in models:
                logger.error("gpt-oss:20b model is not available")
                return None
            
            api_url = f"{OLLAMA_BASE_URL}/api/generate"
            payload = {
                "model": "gpt-oss:20b",
                "prompt": prompt,
                "stream": False,
                "options": {
                    "temperature": 0.0,  # Lower temperature for more consistent JSON output
                    "top_p": 0.9
                }
            }
            
            response = requests.post(
                api_url,
                json=payload,
                headers={"Content-Type": "application/json"},
                timeout=180
            )
            response.raise_for_status()
            result = response.json().get("response", "").strip()
            return result
        except Exception as e:
            logger.error(f"Error getting llm client: {e}")
            return None
    
    elif llm_settings.provider == "groq":
        try:
            if not llm_settings.api_key:
                logger.error("Groq API key is not set")
                return None
            
            client = Groq(
                api_key=llm_settings.api_key,
            )

            chat_completion = client.chat.completions.create(
                messages=[
                    {
                        "role": "user",
                        "content": prompt,
                    }
                ],
                model="openai/gpt-oss-20b",
            )

            return chat_completion.choices[0].message.content
        except Exception as e:
            logger.error(f"Error getting llm client: {e}")
            return None


def check_ollama_connection(base_url: str = OLLAMA_BASE_URL) -> bool:
    """Check if Ollama is running and accessible."""
    try:
        response = requests.get(f"{base_url}/api/tags", timeout=5)
        response.raise_for_status()
        return True
    except:
        return False


def list_available_models(base_url: str = OLLAMA_BASE_URL) -> list:
    """Get list of available models in Ollama."""
    try:
        response = requests.get(f"{base_url}/api/tags", timeout=10)
        response.raise_for_status()
        models = response.json().get("models", [])
        return [model.get("name", "") for model in models]
    except Exception as e:
        logger.error(f"Could not fetch available models: {e}")
        return []
