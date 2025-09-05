from dotenv import load_dotenv
import os

load_dotenv()

class LLMSettings:
    provider: str = "ollama" # ollama or groq
    api_key: str = os.getenv("GROQ_API_KEY") if provider == "groq" else None

llm_settings = LLMSettings()
